# https://realpython.com/twitter-bot-python-tweepy/
import time
import tweepy

# blackraintweets
# ---------------
# Twitter username = blackraintweets
CONSUMER_KEY    = 'N41qzhrygLrmxVMUXQhg'
CONSUMER_SECRET = 'Ad13vdyy5HIjBY3nsipddCrSGVeXUacIjCeyz4hjABo'
ACCESS_TOKEN      = '293023517-Aab9pQEGzECrGGj8lLjGsIqnB6CSOQGXmnlx476W'
ACCESS_TOKEN_SECRET   = 'ZmtLBKNHVlnzImahZbMUgegz0PBM9st1fx7FIngDA'


# FIXME : add lat and lon to the tweet in the future
def send_tweet(tweet, lat, lon):
    """

    :param tweet:
    :return:
    """
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # Create API object
    api = tweepy.API(auth)

    # Create a tweet
    ts = time.ctime()

    tweet_full = ts + " : " + tweet
    status = api.update_status(tweet_full)
    return status


def main():
    tweet = "The weather is lovely"
    lat = 0.0
    lon = 1.0
    status = send_tweet(tweet, lat, lon)
    print(status)


if __name__ == '__main__':
    main()

