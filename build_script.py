import os
import platform
import shutil
import subprocess
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BuildError(Exception):
    """Custom exception for build process errors"""
    pass

def clean_build_directories():
    """Clean up previous build artifacts"""
    directories = ['build', 'dist']
    for directory in directories:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                logger.info(f"Cleaned {directory} directory")
            except Exception as e:
                logger.error(f"Error cleaning {directory}: {e}")
                raise BuildError(f"Failed to clean {directory}")

def build_executable():
    """Build the executable from src/xp"""
    try:
        # Clean previous builds
        clean_build_directories()

        # Ensure source directory exists
        src_path = Path("src/xp")
        if not src_path.exists():
            raise BuildError(f"Source directory {src_path} not found")

        # Find main entry point
        main_file = src_path / "__main__.py"
        if not main_file.exists():
            main_file = src_path / "main.py"
            if not main_file.exists():
                raise BuildError("No main entry point found in src/xp")

        logger.info(f"Building from entry point: {main_file}")

        # Create build command with optimizations and metadata
        build_command = [
            "poetry", "run", "pyinstaller",
            "--onefile",
            "--clean",
            "--name", "xp",
            "--add-data", f"src/xp:xp",  # Include package data
            str(main_file)
        ]

        # Add platform-specific options
        if platform.system() == "Linux":
            build_command.extend([
                "--strip",  # Strip symbols to reduce size
                "--noupx"  # Avoid UPX compression which can trigger false AV positives
            ])

        # Run build process
        logger.info("Starting build process...")
        result = subprocess.run(
            build_command,
            check=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Build failed: {result.stderr}")
            raise BuildError("Build process failed")

        # Verify build output
        executable_path = Path("dist/xp")
        if not executable_path.exists():
            raise BuildError("Build completed but executable not found")

        # Set permissions on Linux
        if platform.system() == "Linux":
            executable_path.chmod(0o755)
            logger.info("Set executable permissions")

        logger.info(f"Build successful! Executable created at: {executable_path}")
        return executable_path

    except subprocess.CalledProcessError as e:
        logger.error(f"Build command failed: {e.stderr}")
        raise BuildError("Build process failed") from e
    except Exception as e:
        logger.error(f"Unexpected error during build: {e}")
        raise BuildError("Build process failed") from e

def install_executable(executable_path: Path):
    """Install the executable to appropriate system location"""
    try:
        if platform.system() != "Linux":
            logger.warning("Installation only supported on Linux")
            return

        # Determine install location
        install_dir = Path("/usr/local/bin")
        user_install_dir = Path.home() / ".local" / "bin"

        # Prefer user installation unless we have root
        if os.geteuid() == 0:
            target_dir = user_install_dir
            # target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = install_dir

        target_path = target_dir / "xp"
        
        # Copy executable
        shutil.copy2(executable_path, target_path)
        target_path.chmod(0o755)
        
        logger.info(f"Installed executable to: {target_path}")
        logger.info(f"Make sure {target_dir} is in your PATH")

    except Exception as e:
        logger.error(f"Installation failed: {e}")
        raise BuildError("Installation failed") from e

def main():
    """Main build and install process"""
    try:
        executable_path = build_executable()
        install_executable(executable_path)
        logger.info("Build and installation complete!")
    except BuildError as e:
        logger.error(f"Build failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
