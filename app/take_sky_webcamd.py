# Infinite loop for grabbing sky videos and posting to Twitter if there is sufficient light
# TODO : only tweet if other weather conditions are true e.g. wind ? minimum

import time
import mytwython
import webcam_capture
import call_rest_api


def main():

    query = {}
    query['app_name'] = 'take_sky_webcamd'
    light_service_listen_port = 9503
    light_service_endpoint_base = 'http://192.168.1.180:' + light_service_listen_port.__str__()  # mrdell

    while True:
        print('take_sky_webcamd : started')

        # determine current light conditions
        status_code, response_dict = call_rest_api.call_rest_api(light_service_endpoint_base + '/get_lux', query)
        lux = response_dict['lux']
        sky_condition = response_dict['sky_condition']
        watts = response_dict['watts']
        if lux <= 1000:    # do not bother taking video if it is too dark
            print('light levels are too low, so sleeping, lux=' + lux.__str__())
            time.sleep(60)
            continue

        # video of sky
        # video_filename = "../videos/metminiwx_sky_video_" + time.ctime() + '.avi'
        # video_filename = video_filename.replace('  ', ' ')
        # video_filename = video_filename.replace(' ', '_')
        # video_filename = video_filename.replace(':', '_')
        video_filename = 'sky.avi'
        crf = 19        # H264 encoding quality parameter
        flag, video_filename= webcam_capture.take_video(video_filename, crf=crf, video_length_secs=20)     # 10

        # Tweet the video
        tweet_text = 'take_sky_webcam, lux=' + lux.__str__() + \
            ', watts=' + watts.__str__() + \
            ', condition=' + sky_condition + \
            ', crf=' + crf.__str__()

        mytwython.send_tweet(tweet_text, hashtags=None, media_type='video', media_pathname=video_filename)

        mins_between_videos = 15
        sleep_secs = mins_between_videos * 60
        print('----------------------------------------------')
        print(time.ctime() + ' sleeping...')
        time.sleep(sleep_secs)


if __name__ == '__main__':
    main()
