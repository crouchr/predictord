# https://gist.github.com/michaelosthege/cd3e0c3c556b70a79deba6855deb2cc8
# yum install gifsicle
import imageio
import mytwython
import os


def resize_gif(input_gif, resize_width):
    compressed_gif = 'compressed_gif.gif'

    cmd_str = 'gifsicle --verbose --colors 256 ' + input_gif + ' -o ' + compressed_gif + ' --resize-width ' + resize_width.__str__()
    print(cmd_str)
    os.system(cmd_str)

    file_stats = os.stat(input_gif)
    input_file_size = file_stats.st_size / (1024 * 1024)
    print('input gif size (MB) : ' + input_file_size.__str__())

    file_stats = os.stat(compressed_gif)
    output_file_size = file_stats.st_size / (1024 * 1024)
    print('compressed gif size (MB) : ' + output_file_size.__str__())

    return(compressed_gif)


# class TargetFormat(object):
#     GIF = ".gif"
#     MP4 = ".mp4"
#     AVI = ".avi"

def convert_to_gif(inputpath, outputpath):
    """Reference: http://imageio.readthedocs.io/en/latest/examples.html#convert-a-movie"""
    #outputpath = os.path.splitext(inputpath)[0] + targetFormat
    #print("converting\r\n\t{0}\r\nto\r\n\t{1}".format(inputpath, outputpath))
    print('converting ' + inputpath + ' to ' + outputpath + ' ...')

    file_stats = os.stat(inputpath)
    input_file_size = file_stats.st_size / (1024 * 1024)
    print('input avi size (MB) : ' + input_file_size.__str__())

    reader = imageio.get_reader(inputpath)
    fps = reader.get_meta_data()['fps']

    writer = imageio.get_writer(outputpath, fps=fps)
    for i, im in enumerate(reader):
        #sys.stdout.write("\rframe {0}".format(i))
        #sys.stdout.flush()
        writer.append_data(im)
    print("\r\nfinalizing...")
    writer.close()

    print('compressing...')
    compressed_gif = 'compressed_gif.gif'
    compressed_gif = resize_gif(outputpath, resize_width=160)

    return compressed_gif

if __name__ == '__main__':

    compressed_gif = convert_to_gif("sky.avi", "sky.gif", TargetFormat.GIF)

    tweet_text = 'testing from convert_video_to_gif'
    mytwython.send_tweet(tweet_text, hashtags=None, media_type='video', media_pathname=compressed_gif)
