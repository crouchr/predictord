# https://realpython.com/twitter-bot-python-tweepy/
# Twitter API returned a 400 (Bad Request), Image file size must be <= 5242880 bytes
import time
from twython import Twython, TwythonError

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
        pass
    elif media_type == "video":
        my_video = open(media_pathname, 'rb')
        #response = twitter.upload_video(media=video, media_type='video/mp4')
        #response = twitter.upload_video(media=video, media_type='video/mp4')
        #mf = open(media_pathname, "rb")
        response = twitter.upload_media(media=my_video)
        mfid = []
        mfid.append(response["media_id"])

        try:
            result=twitter.update_status(status=tweet_full, media_ids=mfid)
            truncated = result['truncated']
            print('tweet sent successfully, truncated=' + truncated.__str__())    # TODO : log to tweets dbase
        except TwythonError as e:
            print(e)
    elif media_type == "image":
        pass

    return


# basic test script - not used otherwise
def main():
    lat = 0.0
    lon = 1.0

    #image_pathname = 'test_image.png'
    #status = send_tweet(tweet, hashtags = None, image_pathname=image_pathname)
    #print(status)
    tweet_text = 'testing from mytwython.py'
    media_type = 'video'
    #media_pathname = 'beatles.gif'  # known good animated gif

    media_pathname = 'sky-optimised.gif'
    send_tweet(tweet_text, hashtags=None, media_type=media_type, media_pathname=media_pathname)


if __name__ == '__main__':
    main()

