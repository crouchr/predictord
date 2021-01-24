# POC
# take a picture of the sky so that the picture can be:
# a) send in Forecast Tweet
# b) analysed to determine approximate light level
# c) analysed for cloud coverage

# ideas
# grab a 5 second video and send in tweet as an animated gif ?

# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
# https://linuxconfig.org/how-to-install-mpeg-4-aac-decoder-for-centos-7-linux
# use smplayer for viewing


import time
import os

import cv2

import video_compress_funcs


def create_media_filename(media_type):
    """
    Generate a filename from the current time
    :return:
    """
    filename = "metminiwx_" + time.ctime()
    filename = filename.replace('  ', ' ')
    filename = filename.replace(' ', '_')
    filename = filename.replace(':', '_')

    if media_type == 'image':
        filename = filename + '.png'
    elif media_type == 'video':
        filename = filename + '.avi'

    full_pathname = '/home/crouchr/metminiwx_media/' + filename
    full_pathname = full_pathname.lower()

    return full_pathname


# can't get it to do anything except 640 x 480
def take_picture(image_filename):
    cam = cv2.VideoCapture(0)        # /dev/video0

    print('Grabbing still image from webcam...')
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab still image from webcam")
        return None

    cv2.imwrite(image_filename, frame)
    print("Image {} written to disk".format(image_filename))

    cam.release()

    time.sleep(1)

    return True


def take_video(video_length_secs, crf=19):
    print('Grabbing ' + video_length_secs.__str__() + ' seconds of video from webcam...')
    video_filename = create_media_filename('video')     # name of the intermediate avi file

    cam = cv2.VideoCapture(0)       # /dev/video0
    fourcc = cv2.VideoWriter_fourcc(*'XVID')        # .avi

    out = cv2.VideoWriter(video_filename, fourcc, 30.0, (640, 480))

    frames_captured = 0
    frames_to_capture = video_length_secs * 30   # 20 fps

    while cam.isOpened() and frames_captured < frames_to_capture:
        ret, frame = cam.read()
        if ret:
            out.write(frame)
            frames_captured += 1
        else:
            print('Failed to grab video')
            break

    print("Video {} written to disk".format(video_filename))

    cam.release()
    time.sleep(1)

    # convert avi to mp4/h264
    mp4_filename = video_compress_funcs.encode_to_mp4(video_filename, crf=crf)

    # remove the avi file
    # os.remove(video_filename)

    return True, mp4_filename


if __name__ == '__main__':
    #print(cv2.__version__)
    #print(cv2.getBuildInformation())

    # media_filename = create_media_filename('image')
    # flag = take_picture('test_image.png')

    flag, mp4_filename = take_video(crf=10, video_length_secs=15)
