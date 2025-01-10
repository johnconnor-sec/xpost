import argparse
import sys
import schedule
import time
from pathlib import Path

from api import post_pending_tweets
from db import add_tweet, get_scheduled_tweets

def create_parser() -> argparse.ArgumentParser:
    """
    Parse command-line arguments for the Tweet Scheduler tool.
    """
    parser = argparse.ArgumentParser(
        description="Tweet Scheduler CLI: Schedule and manage your tweets effortlessly."
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Post command for immediate posting
    post_parser = subparsers.add_parser('post', help='Post a thread immediately')
    post_parser.add_argument(
        'tweets',
        nargs='*',
        help='Tweet messages (optional if piping or using --file)'
    )
    post_parser.add_argument(
        '--file', '-f',
        help='Read tweets from file (one tweet per line)'
    )
    post_parser.add_argument(
        '--preview', '-p',
        action='store_true',
        help='Preview thread before posting'
    )
    post_parser.add_argument(
        'post',
        nargs='*',
        help='Tweet messages (optional if piping or using --file)'
    )

    # Schedule command
    schedule_parser = subparsers.add_parser(
        'schedule',
        help='Schedule a tweet thread for future posting'
    )
    schedule_parser.add_argument(
        'tweets',
        nargs='+',
        help='Tweet messages (optional if piping or using --file)'
    )
    schedule_parser.add_argument(
        '--time', '-t',
        required=True,
        help=(
            'When to post the thread. Supports:\n'
            '- Standard format: "YYYY-MM-DD HH:MM:SS"\n'
            '- Natural language: "next friday at 3pm", "tomorrow at noon",\n'
            '  "in 2 hours", "November 1st at 3:30pm", etc.'
        )
    )
    schedule_parser.add_argument(
        '--file', '-f',
        help='Read tweets from file (one tweet per line)'
    )
    schedule_parser.add_argument(
        '--preview', '-p',
        action='store_true',
        help='Preview thread before scheduling'
    )
    
    # List command
    list_parser = subparsers.add_parser('list', help='List scheduled threads')
    list_parser.add_argument(
        '--status', '-s',
        choices=['pending', 'posted', 'cancelled'],
        help='Filter by status'
    )
    list_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show full tweet content'
    )
    
    run_parser = subparsers.add_parser('run', help='Run the Tweet Scheduler to post pending tweets.')
    run_parser.add_argument(
        dest="run",
        action="store_true",
        help="Run the Tweet Scheduler to post pending tweets.",
    )

    return parser

def get_tweets_input(args) -> list[str]:
    """Get tweets from either pipe, file, or command line arguments."""
    tweets = []

    # First check if input is being piped
    if not sys.stdin.isatty():
        tweets = [line.strip() for line in sys.stdin.readlines() if line.strip()]

    # Then check if a file is specified
    elif hasattr(args, 'file') and args.file:
        try:
            file_path = Path(args.file)
            with open(file_path, 'r') as f:
                tweets = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            raise ValueError(f"Error reading file {args.file}: {str(e)}")

    # Finally use command line arguments
    elif hasattr(args, 'tweets') and args.tweets:
        tweets = args.tweets

    return tweets

def preview_thread(tweets: list[str]) -> None:
    """Display a formatted preview of the thread."""
    print("\n=== Thread Preview ===\n")
    for i, tweet in enumerate(tweets, 1):
        print(f"Tweet {i}/{len(tweets)}:")
        print(f"{tweet}\n")
        print(f"Length: {len(tweet)}/280 characters\n")
        if i < len(tweets):
            print("-" * 40 + "\n")

def parse_args():
    """Parse command line arguments and handle input."""
    parser = create_parser()
    args = parser.parse_args()

    print(f"Debug: Got args: {args}")
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    # Get tweets for commands that need them
    tweets = []
    if args.command in ('post', 'schedule'):
        tweets = get_tweets_input(args)
        print(f"Debug: Got tweets: {tweets}")

        if not tweets:
            print("Error: No tweets provided")
            sys.exit(1)
            
        # Handle preview if requested
        if args.preview:
            preview_thread(tweets)
            if not input("\nContinue? [y/N] ").lower().startswith('y'):
                print("Cancelled.")
                sys.exit(0)

    return args, tweets

