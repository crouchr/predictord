# do not send forecasts during the night
# this calculation get as complex as needed
def calc_wait_time(now_utc_hour):
    """

    :param now_utc_hour:
    :return:
    """
    wait_time = 2 * 3600    # 2 hours to start

    return wait_time
