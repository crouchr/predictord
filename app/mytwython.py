# https://realpython.com/twitter-bot-python-tweepy/
# Twitter API returned a 400 (Bad Request), Image file size must be <= 5242880 bytes
import time
import traceback

from twython import Twython, TwythonError   # 3.7.0

# blackraintweets
# ---------------
# Twitter username = blackraintweets
APP_KEY    = 'N41qzhrygLrmxVMUXQhg'
APP_SECRET = 'Ad13vdyy5HIjBY3nsipddCrSGVeXUacIjCeyz4hjABo'
OAUTH_TOKEN      = '293023517-Aab9pQEGzECrGGj8lLjGsIqnB6CSOQGXmnlx476W'
OAUTH_TOKEN_SECRET   = 'ZmtLBKNHVlnzImahZbMUgegz0PBM9st1fx7FIngDA'


# FIXME : add lat and lon to the tweet in the future
def send_tweet(tweet_text, hashtags=None, media_type=None, media_pathname=None):
    """

    :param tweet:
    :return:
    """
    try:
        hashtag_str = ''

        # Authenticate to Twitter
        twitter = Twython(APP_KEY, APP_SECRET,
                      OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

        # Create a tweet
        ts = time.ctime()
        tweet_full = ts + " : " + tweet_text
        if hashtags:
            for hashtag in hashtags:
                hashtag_str += '#' + hashtag + ' '
            #print(hashtag_str)
            tweet_full = tweet_full + ' ' + hashtag_str

        # Send tweet
        print('send_tweet() : ' + tweet_full)
        # status = api.update_status(tweet_full, lat=lat, long=lon)

        # send Tweet
        if media_type == "tweet":
            result=twitter.update_status(status=tweet_full)
            truncated = result['truncated']
            print('tweet sent successfully, truncated=' + truncated.__str__())    # TODO : log to tweets dbas
        elif media_type == "photo":
            my_image = open(media_pathname, 'rb')
            response = twitter.upload_video(media=my_image, media_type='photo')
            twitter.update_status(status=tweet_full, media_ids=[response['media_id']])
        elif media_type == "video":
            my_video = open(media_pathname, 'rb')
            response = twitter.upload_video(media=my_video, media_type='video/mp4')
            twitter.update_status(status=tweet_full, media_ids=[response['media_id']])
    except Exception as e:
        traceback.print_exc()

    return


# basic test script - not used otherwise
def main():

    lat = 0.0
    lon = 1.0

    #print(twython.__version__)  # 3.7.0
    tweet_text = 'testing from mytwython.py'

    # Tweet an image
    image_pathname = 'test_image.png'
    media_type = 'photo'
    send_tweet(tweet_text + ' - a photo', hashtags=None, media_type=media_type, media_pathname=image_pathname)

    # Tweet a video
    # media_pathname = 'sky.mp4'
    # media_type = 'video'
    # send_tweet(tweet_text + ' - a video', hashtags=None, media_type=media_type, media_pathname=media_pathname)


if __name__ == '__main__':
    main()

