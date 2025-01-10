import sqlite3
import json
import dateparser
from datetime import datetime

from setup import DB_FILE

def init_db():
    """
    Initialize the SQLite database. Create a table to store scheduled_tweets.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post TEXT NOT NULL,
            scheduled_time TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.commit()
    conn.close()

def get_scheduled_tweets(status=None):
    """
    Retrieve scheduled tweets from the database.

    Args:
        status (str): Filter by status (e.g., 'pending', 'posted').

    Returns:
        list[dict]: A list of dictionaries containing the scheduled tweets.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = "SELECT * FROM scheduled_tweets"
    if status:
        query += f" WHERE status = '{status}'"

    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    tweets = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return tweets

def list_scheduled_tweets(status: str = None, verbose: bool = False) -> None:
    """
    List scheduled tweets from the database.
    
    Args:
        status (str): Filter by status (e.g., 'pending', 'posted').
        verbose (bool): Show full tweet content.
    """
    print("\n=== Scheduled Tweets ===\n")
    # Get the scheduled tweets
    scheduled_tweets = get_scheduled_tweets(status)
    
    if not scheduled_tweets:
        print("No scheduled tweets found.")
        return
    
    for tweet in scheduled_tweets:
        print(f"ID: {tweet['id']}")
        print(f"Post: {tweet['post']}")
        print(f"Scheduled Time: {tweet['scheduled_time']}")
        print(f"Status: {tweet['status']}")
        print(f"Created At: {tweet['created_at']}")
        if verbose:
            try:
                tweets_list = json.loads(tweet['post'])
                if isinstance(tweets_list, list):
                    print("Tweets in thread:")
                    for i, t in enumerate(tweets_list, 1):
                        print(f"Tweet {i}: {t}")
                else:
                    print(f"Tweet: {tweets_list}")
            except json.JSONDecodeError:
                print(f"Tweet: {tweet['post']}")

        print("-" * 40)

def add_tweet(post, scheduled_time):
    """
    Add a tweet to the database.

    Args:
        tweets (str): The content of the tweet.
        scheduled_time (str): When the tweet should be posted (in natural language).
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Parse the natural language date/time into a standard format
    parsed_time = dateparser.parse(scheduled_time)
    if not parsed_time:
        print("Error: Unable to parse the scheduled time.")
        return

    try:
        tweets_json = json.dumps(post)

        cursor.execute("""
            INSERT INTO scheduled_tweets (post, scheduled_time, created_at) 
            VALUES (?, ?, ?)
        """, (
            tweets_json,
            parsed_time.strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        print("Tweet scheduled successfully!")
    except Exception as e:
        print("Error adding tweet to database:", e)
    finally:
        conn.close()

