# https://realpython.com/python-time-module/
# https://www.epochconverter.com/   - use this online tool to convert to/from epoch in a web service
# timedatectl - run on CentOS7 to see UTC and local time and TZ settings

from datetime import datetime
import time
import os

# my modules from web.ermin
import metfuncs

import definitions
import call_rest_api

import ts_funcs
import locations
import julian
import get_env
import mytwython
import wait_time
import webcam_capture
import dbase_funcs
import gif_funcs
import predictord_funcs

#
# FIXME : something is wrong here but go with it
# use forecast_hour_utc = 10 to get it to work for now
def calc_forecast_time_epoch(forecast_hour_utc):
    """
    Calculate UNIX epoch (UTC/GMT) for when forecast should be made - this is 09:00 UTC
    :return:
    """
    utc_now = datetime.now()    # FIXME : should this be datetime.utcnow() ?
    utc_now_epoch = int(utc_now.timestamp())

    forecast_ts = utc_now.replace(hour=forecast_hour_utc, minute=0, second=0, microsecond=0)
    forecast_ts_utc = int(forecast_ts.timestamp())

    return forecast_ts_utc



# ---------------------------------------------------

def update_forecasts(julian_day, forecast_hour_utc, met_source, forecast_phase):
    query = {}
    container_version = get_env.get_version()
    window_hours = 3    # look at previous data for last window_hours hours

    try:
        for place in locations.locations:
            print("\nLocation : " + place['location'])

            lat, lon, pressure, ptrend, wind_deg, wind_quadrant, wind_strength, temp_avg, rain_avg, snow_avg, humidity_avg, dew_point_avg, slope , last_weather_description, last_record_id , last_record_timestamp = \
                dbase_funcs.get_forecast_prereqs(place['location'], julian_day, forecast_hour_utc, met_source, window_hours)

            if lat is None:
                print('Unable to retrieve data for ' + place['location'])
                continue

            query['pressure'] = pressure
            query['trend_str'] = ptrend
            query['wind_deg'] = wind_deg

            status_code, response_dict = call_rest_api.call_rest_api(
                definitions.endpoint_base + '/get_forecast_hughes38',
                query)

            if status_code != 200:
                raise

            hughes38_forecast_text = response_dict['forecast_text']
            hughes38_forecast_id = response_dict['forecast_id']
            print('hughes38_forecast_text = *** ' + hughes38_forecast_text + ' ***')
            print('hughes38_forecast_id = ' + hughes38_forecast_id.__str__())

            zambretti_forecast_text = 'NOT_IMPLEMENTED'
            zambretti_forecast_id = '0'         # 0 is not a valid Zambretti id

            metmini_forecast_text = 'NOT_IMPLEMENTED'
            metmini_forecast_id = -1

            api_forecast_text = 'NOT_IMPLEMENTED'   # e.g. forecast from a Weather API

            full_forecast_txt =  "MetMini Forecast\n"
            full_forecast_txt += "----------------\n"
            full_forecast_txt += time.ctime() + "\n"
            full_forecast_txt += "Location  : " + place['location'] + "\n"
            full_forecast_txt += "Latitude  : " + lat.__str__() + "\n"
            full_forecast_txt += "Longitude : " + lon.__str__() + "\n"
            full_forecast_txt += "Meteorological data source : " + met_source + "\n"
            full_forecast_txt += "Hughes38  forecast for next 12 hours : " + hughes38_forecast_text + "\n"
            full_forecast_txt += "Hughes38  forecast id : " + hughes38_forecast_id.__str__() + "\n"
            full_forecast_txt += "Zambretti forecast for next 12 hours : " + zambretti_forecast_text + "\n"
            full_forecast_txt += "Zambretti forecast id : " + zambretti_forecast_id.__str__() + "\n"
            full_forecast_txt += "MetMini forecast for next 12 hours : " + metmini_forecast_text + "\n"
            full_forecast_txt += "MetMini forecast id : " + metmini_forecast_id.__str__() + "\n"
            full_forecast_txt += "API forecast for next 12 hours : " + api_forecast_text + "\n"
            full_forecast_txt += "{"
            full_forecast_txt += "pressure=" + pressure.__str__() + " mbar (ptrend=" + ptrend + ")"
            full_forecast_txt += ", wind_deg=" + wind_deg.__str__()
            full_forecast_txt += ", wind_quadrant=" + wind_quadrant.__str__()
            full_forecast_txt += ", wind_strength=F" + wind_strength.__str__()
            full_forecast_txt += ", pressure_slope=" + slope.__str__()
            full_forecast_txt += ", last_record_id=" + last_record_id.__str__()
            full_forecast_txt += "}"
            full_forecast_txt += "\n"
            full_forecast_txt += "["
            full_forecast_txt += "temp_avg=" + temp_avg.__str__()
            full_forecast_txt += ", dew_point_avg=" + dew_point_avg.__str__()
            full_forecast_txt += ", humidity_avg=" + humidity_avg.__str__()
            full_forecast_txt += ", rain_avg=" + rain_avg.__str__()
            full_forecast_txt += ", snow_avg=" + snow_avg.__str__()
            full_forecast_txt += ", last_weather_description=" + last_weather_description.__str__()
            full_forecast_txt += "]"

            # take picture of sky using webcam
            if place['location'] == 'Stockcross, UK':
                # sky_picture_filename = webcam_capture.create_media_filename('image')
                # flag = webcam_capture.take_picture(sky_picture_filename)
                # print('sky_picture_filename=' + sky_picture_filename)

                sky_video_filename = webcam_capture.create_media_filename('video')
                flag = webcam_capture.take_video(sky_video_filename, video_length_secs=8)
                print('sky_video_filename=' + sky_video_filename)

                sky_video_filename = gif_funcs.convert_to_gif(sky_video_filename, "sky.gif")

                # # Tweet the video
                # tweet_text = 'testing from convert_video_to_gif'
                # mytwython.send_tweet(tweet_text, hashtags=None, media_type='video', media_pathname=compressed_gif)

            else:
                sky_video_filename="None"

            dbase_funcs.add_forecast_to_db(julian_day, place['location'], lat, lon, pressure, ptrend, wind_deg, wind_quadrant, wind_strength, temp_avg, rain_avg, snow_avg, humidity_avg, dew_point_avg, slope, met_source, last_weather_description, last_record_id, hughes38_forecast_text, hughes38_forecast_id, zambretti_forecast_text, zambretti_forecast_id, metmini_forecast_text, metmini_forecast_id, api_forecast_text, last_record_timestamp, sky_video_filename, container_version)

            # only Tweet out my local forecast "Stockcross, UK",
            # ["Stockcross, UK", "Lymington Harbour, UK", "Yarmouth Harbour, UK", "Cowes, UK", "Portsmouth, UK"]:
            if place['location'] in ["Stockcross, UK"]:
                tweet = forecast_phase + ' forecast for ' + place['location'] + ' is *** ' + hughes38_forecast_text.lower() + ' ***' + \
                    ', current=' + last_weather_description.__str__() +\
                    ', temp=' + temp_avg.__str__() + 'C' +\
                    ', wind=F' + wind_strength.__str__() +\
                    ', rain=' + rain_avg.__str__() + 'mm/hr' +\
                    ', rec_id=' + last_record_id.__str__() + \
                    ', slp=' + slope.__str__()
                    #', last_record_id=' + last_record_id.__str__()
                    #', condition_code=' + hughes38_forecast_id.__str__() + ', sender=mrdell'
                tweet_location = place['location'].split(',')[0].lower()    # bug for lymington harbour and yarmouth harbour
                tweet_truncated = tweet[0:250]
                print('tweet length=' + len(tweet_truncated).__str__())
                mytwython.send_tweet(tweet_truncated , hashtags=['metminiwx'], media_type='video', media_pathname=sky_video_filename)
                print('update_forecasts() : sleeping for 120 seconds...')
                time.sleep(120)       # rate-limit code': 326, 'message': 'To protect our users from spam and other malicious activity, this account is temporarily locked.

    except Exception as e:
        print("update_forecasts() : error : " + e.__str__())


def main():
    try:
        source = "OpenWeatherMap"   # the only source of weather info at the moment
        container_version = get_env.get_version()

        print('predictord started, container_version=' + container_version)

        forecast_tuples = predictord_funcs.calc_forecast_sequence(locations.locations)
        #forecast_sequence = ['Now', 'Sunrise', 'Morning', 'Noon', 'Afternoon', 'Evening', 'Sunset']

        while True:
            for forecast_phase in forecast_tuples:
                print("\n----------")
                print(time.ctime() + ' forecast_phase=' + forecast_phase[1])
                secs_to_wait, mins_to_wait, hours_to_wait = wait_time.calc_wait_time(forecast_phase[0])
                print('sleeping for ' + secs_to_wait.__str__() + ' secs...')
                print('sleeping for ' + mins_to_wait.__str__() + ' mins...')
                print('sleeping for ' + hours_to_wait.__str__() + ' hours...')
                time.sleep(secs_to_wait)

                print('=> woke up at : ' + time.ctime())
                now_utc = time.time()
                utc_time_str = ts_funcs.epoch_to_utc(now_utc)
                julian_day = julian.get_julian_date(utc_time_str)
                now_utc_hour = utc_time_str.split(" ")[1]
                #forecast_utc_hour = int(now_utc_hour.split(':')[0]) - 1
                forecast_utc_hour = int(now_utc_hour.split(':')[0]) - 3
                print('forecast_utc_hour = ' + forecast_utc_hour.__str__())
                update_forecasts(julian_day, forecast_utc_hour, source, forecast_phase)

    except Exception as e:
        print("main() : error : " + e.__str__())


if __name__ == '__main__':
    os.environ['PYTHONUNBUFFERED'] = "1"  # does this help with log buffering ?
    #print('Waiting...')
    #time.sleep(60)  # FIXME : hack to wait until other services are up
    main()
