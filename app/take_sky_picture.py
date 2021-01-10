# POC
# take a picture of the sky so that the picture can be:
# a) send in Forecast Tweet
# b) analysed to determine approximate light level
# c) analysed for cloud coverage

# ideas
# grab a 3 second video and send in tweet as an animated gif ?

import cv2
import time


def create_sky_picture_filename():
    """
    Generate a filename from the current time
    :return:
    """
    img_name = "metminiwx_sky_image_" + time.ctime()  + '.png'
    img_name = img_name.replace('  ', ' ')
    img_name = img_name.replace(' ', '_')
    img_name = img_name.replace(':', '_')

    return img_name


def take_picture(image_filename):
    cam = cv2.VideoCapture(0)       # /dev/video0

    print('Grabbing sky image from webcam...')
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab sky image from webcam")
        return None

    #img_name = "../images/metminiwx_sky_image_" + time.ctime()  + '.png'
    #img_name = "metminiwx_sky_image_" + time.ctime()  + '.png'
    #img_name = img_name.replace('  ', ' ')
    #img_name = img_name.replace(' ', '_')
    #img_name = img_name.replace(':', '_')

    cv2.imwrite(image_filename, frame)
    print("Image {} written to disk".format(image_filename))

    cam.release()

    return True


if __name__ == '__main__' :
    image_filename = 'sky_test_image.png'
    flag = take_picture(image_filename)
