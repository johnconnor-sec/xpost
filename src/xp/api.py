import tweepy
import sqlite3
import dateparser
import json

from db import DB_FILE
from datetime import datetime
from setup import setup_wizard, load_credentials

def create_api():
    """
    Create a Tweepy API object using the stored credentials.

    Returns:
        tweepy.API: The Tweepy API object.
    """
    # Check for credentials
    credentials = load_credentials()
    print("Debug: loaded credentials:",{k: '***' for k in credentials.keys()} if credentials else None)
    
    # If credentials are not found, run the setup wizard
    if not credentials:
        print("No credentials found. Running setup wizard...")
        setup_wizard()
        credentials = load_credentials()

    client = tweepy.Client(
        consumer_key=credentials["consumer_key"],
        consumer_secret=credentials["consumer_secret"],
        access_token=credentials["access_token"],
        access_token_secret=credentials["access_token_secret"]
    )

    return client 

def post_tweet(client, post, in_reply_to_id=None):
    """
    Post a single tweet using Tweepy.

    Args:
        client (tweepy.Client): The Tweepy Client object.
        tweet (str): The content of the tweet.
        in_reply_to_id (str, optional): The ID of the tweet to reply to.

    Returns:
        tuple: (success boolean, tweet_id if successful or None if failed)
    """
    try:
        # client.create_tweet(text=tweets)
        if in_reply_to_id:
            response = client.create_tweet(
                text=post, 
                in_reply_to_tweet_id=in_reply_to_id
            )
        else:
            response = client.create_tweet(text=post)

        tweet_id = response.data['id']
        tweet_url = f"https://x.com/user/status/{tweet_id}"
        print(f"Tweet posted successfully: {tweet_url}")
        return True, tweet_id
    except Exception as e:
        print("Error posting tweet:", e)
        return False, None

def post_thread(client, tweets):
    """
    Post a thread of tweets using Tweepy.

    Args:
        client (tweepy.Client): The Tweepy Client object.
        tweets (list[str]): The list of tweets in the thread.
    """
    try:
        tweet_ids = []
        for tweet in tweets:
            response = client.create_tweet(text=tweet, in_reply_to_tweet_id=tweet_ids[-1] if tweet_ids else None)
            tweet_id = response.data['id']
            tweet_ids.append(tweet_id)
            print(f"Tweet posted successfully: https://x.com/user/status/{tweet_id}")
        return True
    except Exception as e:
        print("Error posting thread:", e)
        return False

def post_pending_tweets(client):
    """
    Check the database for pending tweets and post them if their scheduled time has passed.

    Args:
        client (tweepy.Client): The Tweepy Client object.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            SELECT id, post 
            FROM scheduled_tweets
            WHERE status = 'pending' 
            AND scheduled_time <= ?
            ORDER BY scheduled_time ASC
        """, (now,))

        pending_tweets = cursor.fetchall()

        for tweet_id, tweets in pending_tweets:
            tweets = json.loads(tweets)

            if isinstance(tweets, list):
                # Handle a thread of tweets
                previous_id = None
                success = True

                for tweet in tweets:
                    success, new_id = post_tweet(client, tweet, previous_id)
                    if not success:
                        break
                    previous_id = new_id

                if success:
                    cursor.execute(
                        "UPDATE scheduled_tweets SET status = 'posted' WHERE id = ?", 
                        (tweet_id,)
                    )
                    conn.commit()

                else:
                    # Handle single tweet
                    success, _ = post_tweet(client, tweets)
                    if success:
                        cursor.execute(
                            "UPDATE scheduled_tweets SET status = 'posted' WHERE id = ?", 
                            (tweet_id,)
                        )
                        conn.commit()

    except Exception as e:
        print("Error posting pending tweets:", e)
    finally:
        conn.close()

