import os

HOME_DIR = os.path.expanduser("~/.tweet")
CREDENTIALS_FILE = os.path.join(HOME_DIR, "credentials.txt")
DB_FILE = os.path.join(HOME_DIR, "scheduled_tweets.db")

def ensure_home_dir():
    """
    Ensure the $HOME/.tweet directory exists.
    """
    if not os.path.exists(HOME_DIR):
        os.makedirs(HOME_DIR)
        print(f"Created directory: {HOME_DIR}")

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"No credentials file not found at: {CREDENTIALS_FILE}")
        setup_wizard()

def setup_wizard():
    """
    Guide the user through setting up their Twitter API credentials.
    """
    print("Twitter API credentials setup wizard")
    consumer_key = input("Enter your Consumer Key: ").strip()
    consumer_secret = input("Enter your Consumer Secret Key: ").strip()
    access_token = input("Enter your Access Token: ").strip()
    access_token_secret = input("Enter your Access Token Secret: ").strip()
    
    # Ensure the home directory exists
    os.makedirs(HOME_DIR, exist_ok=True)

    with open(CREDENTIALS_FILE, "w") as f:
        f.write(f"consumer_key={consumer_key}\n")
        f.write(f"consumer_secret={consumer_secret}\n")
        f.write(f"access_token={access_token}\n")
        f.write(f"access_token_secret={access_token_secret}\n")

    print("Credentials saved successfully!")


def load_credentials():
    """
    Load Twitter API credentials from the credentials file.

    Returns:
        dict: A dictionary containing the API credentials.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        print("Credentials not found. Starting setup wizard.")
        setup_wizard()

    credentials = {}
    try:
        with open(CREDENTIALS_FILE, "r") as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split("=", 1)
                    credentials[key] = value.strip()

        required_keys = ["consumer_key", "consumer_secret", "access_token", "access_token_secret"]

        missing_keys = [key for key in required_keys if key not in credentials]

        if missing_keys:
            print("Error: Missing required credentials: {', '.join(missing_keys)}")
            setup_wizard()
            return load_credentials()

        return credentials
    except Exception as e:
        print("Error loading credentials:", e)
        setup_wizard()
        return load_credentials() # Try loading credentials again after setup_wizard

