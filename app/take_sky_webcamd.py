# Infinite loop for grabbing sky images and videos

import time
import twitter
import webcam_capture


def main():
    while True:
        print('started')

        # still image of sky
        img_name = "../images/metminiwx_sky_image_" + time.ctime() + '.png'
        img_name = img_name.replace('  ', ' ')
        img_name = img_name.replace(' ', '_')
        img_name = img_name.replace(':', '_')
        webcam_capture.take_picture(img_name)

        # Tweet the picture
        tweet = 'TESTING take_sky_webcam.py : Image of sky'
        status = twitter.send_tweet(tweet, hashtags=None, image_pathname=img_name)

        # video of sky
        video_filename = "../videos/metminiwx_sky_video_" + time.ctime() + '.avi'
        video_filename = video_filename.replace('  ', ' ')
        video_filename = video_filename.replace(' ', '_')
        video_filename = video_filename.replace(':', '_')
        webcam_capture.take_video(video_filename, video_length_secs=5)

        # Tweet the video
        #tweet = 'TESTING take_sky_webcam.py : Video of sky'
        #status = twitter.send_tweet(tweet, hashtags=None, image_pathname=video_filename)

        mins = 20  # 1 hour between images
        sleep_secs = mins * 60
        print('----------------------------------------------')
        print(time.ctime() + ' sleeping...')
        time.sleep(sleep_secs)


if __name__ == '__main__' :
    main()
