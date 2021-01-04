# timestamp funcs
# https://stackoverflow.com/questions/3694487/in-python-how-do-you-convert-seconds-since-epoch-to-a-datetime-object

import datetime


def epoch_to_utc(epoch):
    """
    Return string version of epoch
    :param epoch:
    :return:
    """
    utc_str = datetime.datetime.utcfromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
    return utc_str


def epoch_to_local(epoch):
    """
    Return string as Localtime with epoch
    :param epoch:
    :return:
    """
    local_str = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
    return local_str
