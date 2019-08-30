from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from tweepy import Stream
import numpy as np
import pandas as pd

from textblob import TextBlob
import re
import matplotlib.pyplot as plt

import credentials


# twitter clients

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_user_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_friend_list(self, num_friends):
        friends = []
        for friend in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_friends):
            friends.append(friend)
        return friends

    def get_home_timeline_tweets(self, num_tweets):
        home_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_tweets.append(tweet)
        return home_tweets


# Authentcation class


class TwitterAuthenticator():
    def authenticate_app(self):
        auth = OAuthHandler(credentials.CONSUMER_KEY,
                            credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.ACCESS_TOKEN,
                              credentials.ACCESS_TOKEN_SECRET)
        return auth


class TwitterStreamer():
    """
    class that streams and processes live tweets

    """

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # this handels twitter auth and connection to twitter
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_app()
        stream = Stream(auth, listener)

        stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):
    # listener class that prints receiced tweets to stdout
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data : %s" % str(e))
        return True

    def on_error(self, status):
        # if limit reached
        if status == 420:
            return False
        print(status)


class TweetAnalyzer():

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(
            data=[tweet.text for tweet in tweets], columns=['tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df


if __name__ == "__main__":
    hash_tag_list = ["ucldraw", ]
    fetched_tweets_filename = "tweets.json"

    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name="realDonaldTrump", count=226)

    tweet_analyzer = TweetAnalyzer()

    df = tweet_analyzer.tweets_to_data_frame(tweets)

    # average length of tweets

    print(np.mean(df['len']))

    # most liked tweet

    print(np.max(df['likes']))

    # most retweeted

    print(np.max(df['retweets']))

    # time_likes = pd.Series(data=df['likes'].values, index=df['date'])

    # time_likes.plot(figsize=(10, 4), label="Likes", legend=True)

    # time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])

    # time_retweets.plot(figsize=(10, 4), label="Retweets", legend=True)

    # plt.show()

    # print(df.head(10))

    # print(dir(tweets[0]))
    # tweets = api.user_timeline(screen_name="realDonaldTrump", count=20)

    # print(tweets)

    # print(twitter_client.get_user_tweets(1))

    # twitter_streamer = TwitterStreamer()
    # twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)
