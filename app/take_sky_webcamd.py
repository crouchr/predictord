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
        if lux <= 100:    # do not bother taking video if it is too dark
            print(time.ctime() + ' : light levels are too low, so sleeping, lux=' + lux.__str__())
            time.sleep(60)
            continue

        crf = 19        # H264 encoding quality parameter
        # flag, video_filename_encoded = webcam_capture.take_video(crf=crf, video_length_secs=20)     # 10
        flag, mp4_filename = webcam_capture.take_video(crf=10, video_length_secs=20)
        print('wrote webcam video to : ' + mp4_filename)

        filename = mp4_filename.split('/')[-1]      # ignore the filepath
        # Tweet the video
        tweet_text = 'take_sky_webcamd, lux=' + lux.__str__() + \
            ', watts=' + watts.__str__() + \
            ', condition=' + sky_condition + \
            ', crf=' + crf.__str__() + \
            ', file=' + filename

        mytwython.send_tweet(tweet_text, hashtags=None, media_type='video', media_pathname=mp4_filename)

        mins_between_videos = 15
        sleep_secs = mins_between_videos * 60
        print('----------------------------------------------')
        print(time.ctime() + ' sleeping...')
        time.sleep(sleep_secs)


if __name__ == '__main__':
    main()
