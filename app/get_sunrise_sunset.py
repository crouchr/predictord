# https://sunrise-sunset.org/api
import requests
import json


def get_sunrise_info(lat, lon):
    """

    :param lat:
    :param lon:
    :return:
    """
    url = "https://api.sunrise-sunset.org/json?" +\
        "lat=" + lat.__str__() + \
        "&lng=" + lon.__str__() + \
        "&date=today"

    response = requests.get(url)
    if response.status_code != 200:
        return response.status_code, None

    response_dict = json.loads(response.content.decode('utf-8'))

    return response.status_code, response_dict['results']


# testing
if __name__ == '__main__':
    my_lat = 1.0
    my_lon = 1.0

    status_code, response  = get_sunrise_info(my_lat, my_lon)

    if status_code != 200:
        print('status_code=' + status_code.__str__())

    sunrise = response['sunrise']
    sunset = response['sunset']
    noon = response['solar_noon']




