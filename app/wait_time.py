import ts_funcs
import time
import datetime


def calc_wait_time(event_time):
    """

    :param event_time: '08:12:00'
    :return:
    """



    try:
        forecast_mins = 0
        forecast_hour = int(event_time.split(':')[0])
        forecast_mins = int(event_time.split(':')[1])
        forecast_secs = int(event_time.split(':')[2])

        now_utc = time.time()
        utc_time_str = ts_funcs.epoch_to_utc(now_utc)

        # if event_name == 'Now':
        #     return 0, 0, 0
        # if event_name == 'Sunrise':
        #     forecast_hour = 8
        #     forecast_mins = 6
        # elif event_name == 'Morning':
        #     forecast_hour = 9
        # elif event_name == 'Noon':
        #     forecast_hour = 12
        # elif event_name == 'Afternoon':
        #     forecast_hour = 15
        # elif event_name == 'Evening':
        #     forecast_hour = 19
        # elif event_name == 'Sunset':
        #     forecast_hour = 16
        #     forecast_mins = 19

        utc_now = datetime.datetime.now()        # FIXME : should this be datetime.utcnow() ?
        utc_now_epoch = int(utc_now.timestamp())

        forecast_ts = utc_now.replace(hour=forecast_hour, minute=forecast_mins, second=forecast_secs, microsecond=0)
        forecast_ts_utc_epoch = int(forecast_ts.timestamp())

        secs_to_wait = int(forecast_ts_utc_epoch - utc_now_epoch)

        if secs_to_wait < 0:
            secs_to_wait = (24 * 60 * 60) + secs_to_wait
        mins_to_wait = int(secs_to_wait/60)
        hours_to_wait = round(secs_to_wait / 3600, 1)

        return secs_to_wait, mins_to_wait, hours_to_wait

    except Exception as e:
        print('calc_wait_time() : error : ' + e.__str__())
        return None


# def calc_wait_time(event_name):
#     """
#
#     :param event_name:
#     :return:
#     """
#     try:
#         forecast_mins = 0
#
#         now_utc = time.time()
#         utc_time_str = ts_funcs.epoch_to_utc(now_utc)
#         if event_name == 'Now':
#             return 0, 0, 0
#         if event_name == 'Sunrise':
#             forecast_hour = 8
#             forecast_mins = 6
#         elif event_name == 'Morning':
#             forecast_hour = 9
#         elif event_name == 'Noon':
#             forecast_hour = 12
#         elif event_name == 'Afternoon':
#             forecast_hour = 15
#         elif event_name == 'Evening':
#             forecast_hour = 19
#         elif event_name == 'Sunset':
#             forecast_hour = 16
#             forecast_mins = 19
#
#         utc_now = datetime.datetime.now()        # FIXME : should this be datetime.utcnow() ?
#         utc_now_epoch = int(utc_now.timestamp())
#
#         forecast_ts = utc_now.replace(hour=forecast_hour, minute=forecast_mins, second=0, microsecond=0)
#         forecast_ts_utc_epoch = int(forecast_ts.timestamp())
#
#         secs_to_wait = int(forecast_ts_utc_epoch - utc_now_epoch)
#
#         if secs_to_wait < 0:
#             secs_to_wait = (24 * 60 * 60) + secs_to_wait
#         mins_to_wait = int(secs_to_wait/60)
#         hours_to_wait = round(secs_to_wait / 3600, 1)
#
#         return secs_to_wait, mins_to_wait, hours_to_wait
#
#     except Exception as e:
#         print('calc_wait_time() : error : ' + e.__str__())
#         return None

