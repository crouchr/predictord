# https://stackoverflow.com/questions/55649356/how-can-i-detect-if-trend-is-increasing-or-decreasing-in-time-series

import numpy as np


def trendline(t_index, data, order=1):
    """
    Determine trend of a series of time values
    :param t_index:
    :param data:
    :param order:
    :return:
    """
    thresh = 0.001  # specific to a problem - take a guess and refine
    coeffs = np.polyfit(t_index, list(data), order)
    slope = round(float(coeffs[-2]), 3)
    if slope * slope <= thresh:
        trend_str = "Steady"
    elif slope > thresh:
        trend_str = "Rising"
    else:
        trend_str = "Falling"

    return trend_str, slope

if __name__ == '__main__':
    index = [1, 2, 3, 4, 5]
    values=[1043,6582,5452,7571,8000]
    # = [1022, 1022, 1022, 1022, 1022]
    values = [1023, 1022, 1022, 1022, 1023]
    values = [1023, 1022, 1022, 1022, 1019]
    trend_str, slope = trendline(index, values)
    print(trend_str)
    print(slope)
