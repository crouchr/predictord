# Infinite loop for grabbing sky images and videos

import time
import mytwython
import webcam_capture
import gif_funcs
import call_rest_api

def main():

    query = {}
    query['app_name'] = 'take_sky_webcamd'
    listen_port = 9503
    endpoint_base = 'http://192.168.1.180:' + listen_port.__str__()  # mrdell

    while True:
        print('started')

        status_code, response_dict = call_rest_api.call_rest_api(endpoint_base + '/get_lux', query)
        lux = response_dict['lux']
        sky_condition = response_dict['sky_condition']
        watts = response_dict['watts']

        # still image of sky
        # img_name = "../images/metminiwx_sky_image_" + time.ctime() + '.png'
        # img_name = img_name.replace('  ', ' ')
        # img_name = img_name.replace(' ', '_')
        # img_name = img_name.replace(':', '_')
        # webcam_capture.take_picture(img_name)

        # Tweet the picture
        #tweet = 'TESTING take_sky_webcam.py : Image of sky'
        #status = twitter.send_tweet(tweet, hashtags=None, image_pathname=img_name)

        # video of sky
        #video_filename = "../videos/metminiwx_sky_video_" + time.ctime() + '.avi'
        video_filename = "../videos/metminiwx_sky_video_" + time.ctime() + '.avi'
        video_filename = video_filename.replace('  ', ' ')
        video_filename = video_filename.replace(' ', '_')
        video_filename = video_filename.replace(':', '_')
        webcam_capture.take_video(video_filename, video_length_secs=10)

        compressed_gif = gif_funcs.convert_to_gif(video_filename, "sky.gif")

        # Tweet the video
        tweet_text = 'take_sky_webcam, lux=' + lux.__str__() + \
            ', watts=' + watts.__str__() + ', condition=' + sky_condition

        mytwython.send_tweet(tweet_text, hashtags=None, media_type='video', media_pathname=compressed_gif)

        mins = 10   # 1 hour between images
        sleep_secs = mins * 60
        print('----------------------------------------------')
        print(time.ctime() + ' sleeping...')
        time.sleep(sleep_secs)


if __name__ == '__main__' :
    main()
