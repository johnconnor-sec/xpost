import sys
import tweepy
import time
import schedule

from input import parse_args
from db import init_db, add_tweet, list_scheduled_tweets
from setup import setup_wizard, load_credentials, ensure_home_dir
from api import create_api, post_pending_tweets, post_tweet

def main():
    """
    Main function to initialize the tool and start the scheduler.
    """
    ensure_home_dir()
    init_db()

    # Create the Tweepy API client
    client = create_api()

    # Parse command line arguments
    args, tweets = parse_args()
    
    if args.command == 'post':

        if len(tweets) == 1:
            # Post a single tweet
            success, _ = post_tweet(client, tweets[0])
            if success:
                print(f"Tweet posted: {tweets[0]}")
            else:
                print(f"Error posting tweet")

        else:
            # Post a thread of tweets
            print("Posting a thread of tweets")
            previous_id = None
            all_succeeded = True

            for i, tweet in enumerate(tweets, 1):
                print(f"Posting tweet {i}/{len(tweets)}...")
                success, tweet_id = post_tweet(client, tweet, in_reply_to_id=previous_id)
                if not success:
                    all_succeeded = False
                    break
                if all_succeeded:
                    print("Thread posted successfully!")
                else:
                    print("Error posting thread")

    elif args.command == 'schedule':
        # Add a tweet to the database
        add_tweet(tweets, args.time)
        print(f"Tweet scheduled for {args.time}")

    elif args.command == 'list':
        # List scheduled tweets
        list_scheduled_tweets(
            status=args.status if hasattr(args, 'status') else None,
            verbose=args.verbose if hasattr(args, 'verbose') else False
        )

    elif args.command == 'run':
        # Run the scheduler
        print("Tweet scheduler is running. Press Ctrl+C to exit.")
        # Schedule the job to check for pending tweets every minute
        schedule.every(1).minutes.do(post_pending_tweets, client)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting Tweet Scheduler.")

if __name__ == "__main__":
    main()
