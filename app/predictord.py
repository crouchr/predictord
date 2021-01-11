# https://realpython.com/python-time-module/
# https://www.epochconverter.com/   - use this online tool to convert to/from epoch in a web service
# timedatectl - run on CentOS7 to see UTC and local time and TZ settings
# triggered by cron to run once a day

from datetime import datetime
import time
import os

# my modules from web.ermin
import metfuncs

import definitions
import call_rest_api
import connect_db
import trend
import ts_funcs
import locations
import julian
import predictord_funcs
import twitter
import wait_time
import webcam_capture

# This is heavily modified from the master
def get_forecast_prereqs(location, julian_day, forecast_hour_utc, met_source):
    """
    Retrieve the required values needed to make a forecast from the database
    :return:
    """
    pressure_values = []
    wind_deg_values = []
    wind_strength_values = []
    wind_speed_values = []
    temp_values = []
    dew_point_values = []
    humidity_values = []
    rain_values = []
    snow_values = []

    # reasoning - look at last hour for trends = 6 samples

    recs_to_retrieve = 4                # number of readings to use to determine pressure trend and wind_deg
    index = [1, 2, 3, 4]           # FIXME : calc from recs_to_retrieve
    #recs_to_retrieve = 2
    #index = [1, 2]

    my_dbase="172.27.0.2"   # FIXME : 1 debugging only
    my_dbase = "192.168.1.180"
    mydb, mycursor = connect_db.connect_database(my_dbase, "metminidb")
    #mydb, mycursor = connect_db.connect_database("metmini-mysql", "metminidb")

    # Retrieve the FIRST set of records that are AFTER the 0900 UTC optimum forecasting time
    sql_query = """SELECT * FROM actual WHERE location = %s and julian = %s and hour_utc = %s and source = %s limit %s"""
    #sql_query = """SELECT * FROM actual WHERE location = %s and julian = %s and source = %s limit %s"""
    print('Retrieve Actual Table records for julian_day=' + julian_day.__str__() + ', forecast_hour_utc=' + forecast_hour_utc.__str__() + ', met_source=' + met_source)
    mycursor.execute(sql_query, (location, julian_day, forecast_hour_utc, met_source, recs_to_retrieve))
    records = mycursor.fetchall()

    if len(records) != recs_to_retrieve:
        print("Unable to retrieve sufficient historical records (recs_to_retrieve=" + recs_to_retrieve.__str__() + ") from MetMini Actual table")
        return None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None

    # fixme : fragile = need named columns not numbers - first row is 0
    for row in records:
        pressure_values.append(row[8])
        wind_speed_values.append(row[9])
        wind_deg_values.append(row[10])
        wind_strength_values.append(row[12])
        temp_values.append(row[14])
        dew_point_values.append(row[16])
        humidity_values.append(row[18])
        rain_values.append(row[20])
        snow_values.append(row[21])

    last_record_id = row[0]     # id of the last record to be used
    last_main = row[6]
    last_description = row[7]
    last_weather_description = last_main + " (" + last_description + ")"
    last_record_timestamp = row[2]          # ts_utc

    lat = row[24]
    lon = row[25]

    trend_str, slope = trend.trendline(index, pressure_values)
    wind_deg_avg = int(sum(wind_deg_values)) / len(wind_deg_values)
    wind_deg_avg = int(wind_deg_avg)

    wind_strength_avg = int(sum(wind_strength_values)) / len(wind_strength_values)
    wind_strength_avg = int(wind_strength_avg)

    pressure = pressure_values[0]   # use the first one
    ptrend = trend_str
    wind_quadrant = metfuncs.wind_deg_to_quadrant(wind_deg_avg)

    temp_avg = sum(temp_values) / len(temp_values)
    temp_avg = round(temp_avg, 1)

    rain_avg = sum(rain_values) / len(rain_values)
    rain_avg = round(rain_avg, 2)

    snow_avg = sum(snow_values) / len(snow_values)
    snow_avg = round(snow_avg, 2)

    humidity_avg = sum(humidity_values) / len(humidity_values)
    humidity_avg = round(humidity_avg, 1)

    dew_point_avg = sum(dew_point_values) / len(dew_point_values)
    dew_point_avg = round(dew_point_avg, 1)

    log_msg = 'Forecasting data retrieved from MetMini Actual table : pressure=' + pressure.__str__() + ', ptrend=' + ptrend + \
    ', lat=' + lat.__str__() + \
    ', lon=' + lon.__str__() + \
    ', wind_deg_avg=' + wind_deg_avg.__str__() +\
    ', wind_quadrant=' + wind_quadrant +\
    ', wind_strength_avg=' + wind_strength_avg.__str__() +\
    ', temp_avg=' + temp_avg.__str__() +\
    ', rain_avg=' + rain_avg.__str__() +\
    ', snow_avg=' + snow_avg.__str__() +\
    ', humidity_avg=' + humidity_avg.__str__() +\
    ', dew_point_avg=' + dew_point_avg.__str__() +\
    ', slope=' + slope.__str__() + \
    ', last_weather_description=' + last_weather_description.__str__() + \
    ', last_record_timestamp=' + last_record_timestamp.__str__() + \
    ', last_record_id=' + last_record_id.__str__()
    print(log_msg)

    return lat, lon, pressure, ptrend, wind_deg_avg, wind_quadrant, wind_strength_avg, temp_avg, rain_avg, snow_avg, humidity_avg, dew_point_avg, slope, last_weather_description, last_record_id, last_record_timestamp


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


# def sleep_till_forecast_time(utc_hour_required, utc_minute_required):
#     """
#     Sleep until 0900 UTC
#     """
#     sleep_period = 60
#
#     while True:
#         print('-----')
#         now = time.time()
#         utc_now = datetime.utcnow()
#         print("Local time : " + time.ctime())
#         #print(datetime.timestamp(utc_now))
#         utc_hour   = utc_now.hour
#         utc_minute = utc_now.minute
#         utc_second = utc_now.second
#         print("UTC hour   : " + utc_hour.__str__())
#         print("UTC minute : " + utc_minute.__str__())
#         print("UTC second : " + utc_second.__str__())
#
#         if utc_hour >= utc_hour_required and utc_minute >= utc_minute_required:
#             return
#
#         msg = "Waiting for hour>=" + utc_hour_required.__str__() + ", minute>=" + utc_minute_required.__str__() + " ..."
#         print(msg)
#         time.sleep(sleep_period)
#
#     return


def add_forecast_to_db(julian_day, location, lat, lon, pressure, ptrend, wind_deg, wind_quadrant, wind_strength, temp_avg, rain_avg, snow_avg, humidity_avg, dew_point_avg, slope, met_source, last_weather_description, last_record_id, hughes38_forecast_text, hughes38_forecast_id, zambretti_forecast_text, zambretti_forecast_id, metmini_forecast_text, metmini_forecast_id, api_forecast_text, last_record_timestamp, sky_picture_filename, container_version):
    """
    :param julian_day: When the forecast was made for
    :param pressure:
    :param ptrend:
    :param wind_deg:
    :param wind_strength:
    :param slope: pressure trend slope value
    :param forecast_text:
    :return:
    """

    utc_epoch = time.time()
    #print(utc_epoch)

    # FIXME : remove hardcoding
    my_dbase = "172.27.0.2"         # FIXME 2
    my_dbase = "192.168.1.180"      # FIXME 2
    my_dbase = "192.168.1.15"      # FIXME 2
    mydb, mycursor = connect_db.connect_database(my_dbase, "metminidbflux")
    #mydb, mycursor = connect_db.connect_database("metmini-mysql", "metminidb")

    # Not implemented yet
    hughes38_condition_code = -1
    zambretti_condition_code = -1
    metmini_condition_code = -1
    api_condition_code = -1
    location_code = 'UNKNOWN'
    last_weather_condition_code = -1

    ts_local = ts_funcs.epoch_to_local(utc_epoch)
    ts_utc   = ts_funcs.epoch_to_utc(utc_epoch)

    sql = "INSERT INTO forecasts (" \
          "ts_local, " \
          "ts_utc, " \
          "julian, " \
          "location, " \
          "location_code, " \
          "lat, " \
          "lon, " \
          "pressure, " \
          "ptrend, " \
          "wind_deg, " \
          "wind_quadrant, " \
          "wind_strength, " \
          "temp_avg, " \
          "rain_avg, " \
          "snow_avg, " \
          "humidity_avg, "\
          "dew_point_avg, "\
          "slope, " \
          "met_source, " \
          "last_weather_description, " \
          "last_weather_condition_code, " \
          "last_record_id, " \
          "last_record_timestamp, " \
          "sky_picture_filename, " \
          "hughes38_forecast_text, " \
          "hughes38_forecast_id, " \
          "hughes38_condition_code, " \
          "zambretti_forecast_text, " \
          "zambretti_forecast_id, " \
          "zambretti_condition_code, " \
          "metmini_forecast_text, " \
          "metmini_condition_code, " \
          "api_forecast_text, " \
          "api_condition_code, " \
          "container_version" \
          ") " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    val = (ts_local,
           ts_utc,
           julian_day,
           location,
           location_code,
           lat,
           lon,
           pressure,
           ptrend,
           wind_deg,
           wind_quadrant,
           wind_strength,
           temp_avg,
           rain_avg,
           snow_avg,
           humidity_avg,
           dew_point_avg,
           slope,
           met_source,
           last_weather_description,
           last_weather_condition_code,
           last_record_id,
           last_record_timestamp,
           sky_picture_filename,
           hughes38_forecast_text,
           hughes38_forecast_id,
           hughes38_condition_code,
           zambretti_forecast_text,
           zambretti_forecast_id,
           zambretti_condition_code,
           metmini_forecast_text,
           metmini_condition_code,
           api_forecast_text,
           api_condition_code,
           container_version
           )

    #print(sql)

    mycursor.execute(sql, val)
    mydb.commit()
    message = "record inserted into MetMini Forecasts table OK for location=" + location.__str__()
    print(mycursor.rowcount, message)

# ---------------------------------------------------

def update_forecasts(julian_day, forecast_hour_utc, met_source, forecast_phase):
    query = {}
    container_version = predictord_funcs.get_version()

    try:
        for place in locations.locations:
            #print("===========================================================")
            print("\nLocation : " + place['location'])

            lat, lon, pressure, ptrend, wind_deg, wind_quadrant, wind_strength, temp_avg, rain_avg, snow_avg, humidity_avg, dew_point_avg, slope , last_weather_description, last_record_id , last_record_timestamp = \
                get_forecast_prereqs(place['location'], julian_day, forecast_hour_utc, met_source)

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

            #print("------------------------------------------------")
            #print(full_forecast_txt)
            #print("------------------------------------------------")

            # take picture of sky using webcam
            if place['location'] == 'Stockcross, UK':
                sky_picture_filename = webcam_capture.create_media_filename('image')
                flag = webcam_capture.take_picture(sky_picture_filename)
                print('sky_picture_filename=' + sky_picture_filename)
            else:
                sky_picture_filename="None"

            add_forecast_to_db(julian_day, place['location'], lat, lon, pressure, ptrend, wind_deg, wind_quadrant, wind_strength, temp_avg, rain_avg, snow_avg, humidity_avg, dew_point_avg, slope, met_source, last_weather_description, last_record_id, hughes38_forecast_text, hughes38_forecast_id, zambretti_forecast_text, zambretti_forecast_id, metmini_forecast_text, metmini_forecast_id, api_forecast_text, last_record_timestamp, sky_picture_filename, container_version)

            # only Tweet out my local forecast "Stockcross, UK",
            # ["Stockcross, UK", "Lymington Harbour, UK", "Yarmouth Harbour, UK", "Cowes, UK", "Portsmouth, UK"]:
            if place['location'] in ["Stockcross, UK"]:
                tweet = forecast_phase + ' forecast for ' + place['location'] + ' is *** ' + hughes38_forecast_text.lower() + ' ***' + \
                    ', current=' + last_weather_description.__str__() + \
                    ', temp=' + temp_avg.__str__() + 'C'\
                    ', wind=F' + wind_strength.__str__() + \
                    ', rain=' + rain_avg.__str__() + 'mm/hr'
                    #', last_record_id=' + last_record_id.__str__()
                    #', condition_code=' + hughes38_forecast_id.__str__() + ', sender=mrdell'
                tweet_location = place['location'].split(',')[0].lower()    # bug for lymington harbour and yarmouth harbour
                tweet_truncated = tweet[0:250]
                print('tweet length=' + len(tweet_truncated).__str__())
                twitter.send_tweet(tweet_truncated , hashtags=['metminiwx', tweet_location], image_pathname=sky_picture_filename)
                print('update_forecasts() : sleeping for 120 seconds')
                time.sleep(120)       # rate-limit code': 326, 'message': 'To protect our users from spam and other malicious activity, this account is temporarily locked.

    except Exception as e:
        print("update_forecasts() : error : " + e.__str__())


def main():
    try:
        source = "OpenWeatherMap"   # the only source of weather info at the moment
        container_version = predictord_funcs.get_version()

        print('predictord started, container_version=' + container_version)
        print("\n")         # force buffer flush ?
        forecast_sequence = ['Now', 'Sunrise', 'Morning', 'Noon', 'Afternoon', 'Evening', 'Sunset']

        while True:
            for forecast_phase in forecast_sequence:
                print("\n----------")
                print(time.ctime() + ' forecast_phase=' + forecast_phase)
                secs_to_wait, mins_to_wait, hours_to_wait = wait_time.calc_wait_time(forecast_phase)
                print('sleeping for ' + secs_to_wait.__str__() + ' secs...')
                print('sleeping for ' + mins_to_wait.__str__() + ' mins...')
                print('sleeping for ' + hours_to_wait.__str__() + ' hours...')
                time.sleep(secs_to_wait)
                #time.sleep(3)

                print('woke up at : ' + time.ctime())
                now_utc = time.time()
                utc_time_str = ts_funcs.epoch_to_utc(now_utc)
                julian_day = julian.get_julian_date(utc_time_str)
                now_utc_hour = utc_time_str.split(" ")[1]
                forecast_utc_hour = int(now_utc_hour.split(':')[0]) - 1
                print('forecast_utc_hour = ' + forecast_utc_hour.__str__())
                update_forecasts(julian_day, forecast_utc_hour, source, forecast_phase)

                # sleep_secs = wait_time.calc_wait_time(now_utc_hour)
                # print('sleeping for ' + sleep_secs.__str__() + ' secs...')
                # time.sleep(sleep_secs)

    except Exception as e:
        print("main() : error : " + e.__str__())


if __name__ == '__main__':
    os.environ['PYTHONUNBUFFERED'] = "1"  # does this help with log buffering ?
    #print('Waiting...')
    #time.sleep(60)  # FIXME : hack to wait until other services are up
    main()
