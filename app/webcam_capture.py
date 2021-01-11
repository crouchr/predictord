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

import cv2
import time


def create_media_filename(media_type):
    """
    Generate a filename from the current time
    :return:
    """
    filename = "metminiwx_sky_image_" + time.ctime()
    filename = filename.replace('  ', ' ')
    filename = filename.replace(' ', '_')
    filename = filename.replace(':', '_')

    if media_type == 'image':
        filename = filename + '.png'
    elif media_type == 'video':
        filename = filename + '.avi'


    return filename


def take_picture(image_filename):
    cam = cv2.VideoCapture(0)       # /dev/video0

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


def take_video(video_filename, video_length_secs):
    print('Grabbing video from webcam...')
    cam = cv2.VideoCapture(0)       # /dev/video0
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # fourcc = cv2.VideoWriter_fourcc(*'X264')

    # 20 fps
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))
    frames_captured = 0
    frames_to_capture = video_length_secs * 20   # 20 fps

    while(cam.isOpened() and frames_captured < frames_to_capture):
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

    return True


if __name__ == '__main__' :
    media_filename = create_media_filename('image')
    flag = take_picture(media_filename)

    media_filename = create_media_filename('video')
    flag = take_video(media_filename, video_length_secs=3)