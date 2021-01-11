import ts_funcs
import time
import datetime
# do not send forecasts during the night
# this calculation get as complex as needed
# def calc_wait_time(now_utc_hour):
#     """
#
#     :param now_utc_hour:
#     :return:
#     """
#     wait_time = 4 * 3600    # 4 hours to start
#
#     return wait_time


# make forecasts and tweet image 6 times a day
# 'sunrise'
# 'morning' 0900
# 'noon' # solar noon
# ' afternoon' 1500
# 'evening' :1900
# 'sunset'
# all based on UTC
# ['sunset', 'morning', 'noon', 'afternoon', 'evening', 'sunset']
# FIXME - make it workout what is next phase and then sync to that ?
def calc_wait_time(event_name):
    """

    :param event_name:
    :return:
    """
    try:
        forecast_mins = 0

        now_utc = time.time()
        utc_time_str = ts_funcs.epoch_to_utc(now_utc)
        if event_name == 'Now':
            return 0, 0, 0
        if event_name == 'Sunrise':
            forecast_hour = 8
            forecast_mins = 6
        elif event_name == 'Morning':
            forecast_hour = 9
        elif event_name == 'Noon':
            forecast_hour = 12
        elif event_name == 'Afternoon':
            forecast_hour = 15
        elif event_name == 'Evening':
            forecast_hour = 19
        elif event_name == 'Sunset':
            forecast_hour = 16
            forecast_mins = 19

        utc_now = datetime.datetime.now()        # FIXME : should this be datetime.utcnow() ?
        utc_now_epoch = int(utc_now.timestamp())

        forecast_ts = utc_now.replace(hour=forecast_hour, minute=forecast_mins, second=0, microsecond=0)
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


