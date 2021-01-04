# https://stackoverflow.com/questions/13943062/extract-day-of-year-and-julian-day-from-a-string-date
import datetime


def get_julian_date(datetime_str):
    """

    :param date_str: e.g. 2012-11-7 18:00:00
    :return:
    """
    date_part = datetime_str.split(' ')[0]
    date_parts = date_part.split('-')
    year = int(date_parts[0])
    month = int(date_parts[1])
    day = int(date_parts[2])
    my_date = datetime.date(year, month, day)   # time = 00:00:00
    jd = my_date.toordinal() + 1721424
    return jd
