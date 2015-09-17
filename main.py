"""
Rating of people popularity on Twitter according mentioning frequency
"""

import csv
from collections import Counter, deque

import tweepy

# Secret data from Twitter app
from secret_data import (
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET
)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

counter = Counter()
users_to_process = deque()
USERS_TO_PROCESS = 100
STARTING_USER = "gvanrossum"  # User to start


def extract_tweet(tweet):
    """
    Extract basic information from tweet
    """
    user_mentions = ",".join(
        [user["screen_name"] for user in tweet.entities["user_mentions"]]
    )
    urls = ",".join([url["expanded_url"] for url in tweet.entities["urls"]])
    return [
        tweet.user.screen_name,
        tweet.id,
        tweet.text,
        user_mentions,
        urls
    ]


def process_users(writer, tweets):
    """
    Processing all mentions users
    """
    users_processed = {STARTING_USER}
    while True:
        if len(users_processed) >= USERS_TO_PROCESS:
            break
        else:
            if (len(users_processed)) > 0:
                next_user = users_to_process.popleft()
                if next_user in users_to_process:
                    print("-- %s already processed" % next_user)
                else:
                    print("-- processing %s" % next_user)
                    users_processed.add(next_user)
                    for tweet in tweepy.Cursor(
                            api.user_timeline,
                            id=next_user
                    ).items(10):
                        writer.writerow(extract_tweet(tweet))
                        tweets.flush()
                        for user_mentioned in tweet.entities["user_mentions"]:
                            if not len(users_processed) > 50:
                                users_to_process.append(
                                    user_mentioned["screen_name"])
                                counter[user_mentioned["screen_name"]] += 1
                            else:
                                break
            else:
                break


def process_user():
    """
    Process starting user, launch all user processing, ratings printing
    """
    with open("tweet.csv", "a") as tweets:
        writer = csv.writer(
            tweets, delimiter=",", escapechar="\\", doublequote=False
        )
        print("%s user processing started" % STARTING_USER)
        for tweet in tweepy.Cursor(
                api.user_timeline,
                id=STARTING_USER
        ).items(50):
            writer.writerow(extract_tweet(tweet))
            tweets.flush()
            for user in tweet.entities["user_mentions"]:
                if not len(users_to_process) > USERS_TO_PROCESS:
                    users_to_process.append(user["screen_name"])
                    counter[user["screen_name"]] += 1
                else:
                    break
        print("%s user processing ended" % STARTING_USER)
        print("Mentioned users processing started")
        process_users(writer, tweets)
        print("Mentioned users processing ended")
        print()
    print("User popularity:")
    for user_name, count in counter.most_common(20):
        print(user_name, count)


def main():
    process_user()

main()
