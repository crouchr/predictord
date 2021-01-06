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
#import twitter


def get_forecast_prereqs(location, julian_day_yesterday, forecast_hour_utc, source):
    """
    Retrieve the required values needed to make a forecast from the database
    :return:
    """
    pressure_values = []
    wind_deg_values = []
    wind_strength_values = []

    recs_to_retrieve = 3    # number of readings to use to determine pressure trend and wind_deg
    index = [1, 2, 3]       # FIXME : calc from recs_to_retrieve

    my_dbase="172.26.0.2"   # FIXME : debugging only
    mydb, mycursor = connect_db.connect_database(my_dbase, "metminidb")
    # mydb, mycursor = connect_db.connect_database("metmini-mysql", "metminidb")

    # Retrieve the FIRST set of records that are AFTER the 0900 UTC optimaum forecasting time
    sql_query = """SELECT * FROM actual WHERE location = %s and julian = %s and hour_utc >= %s and source = "OpenWeatherMap" limit %s"""
    mycursor.execute(sql_query, (location, julian_day_yesterday, forecast_hour_utc, recs_to_retrieve,))
    records = mycursor.fetchall()

    if len(records) != recs_to_retrieve:
        print("Unable to retrieve enough records from Actuald table")
        return None, None, None, None, None

    # fixme : fragile = need named columns not numbers
    for row in records:
        pressure_values.append(row[8])
        wind_deg_values.append(row[10])
        wind_strength_values.append(row[12])

    last_record_id = row[0]     # id of the last record to be used

    trend_str, slope = trend.trendline(index, pressure_values)
    wind_deg_avg = int(sum(wind_deg_values)) / len(wind_deg_values)
    wind_deg_avg = int(wind_deg_avg)

    wind_strength_avg = int(sum(wind_strength_values)) / len(wind_strength_values)
    wind_strength     = int(wind_strength_avg)

    pressure = pressure_values[0]   # use the first one
    ptrend = trend_str
    wind_quadrant = metfuncs.wind_deg_to_quadrant(wind_deg_avg)

    log_msg = 'Forecasting data retrieved from Actual table : pressure=' + pressure.__str__() + ', ptrend=' + ptrend +\
    ', wind_deg_avg=' + wind_deg_avg.__str__() + \
    ', wind_quadrant=' + wind_quadrant +\
    ', wind_strength=' + wind_strength.__str__() +\
    ', slope=' + slope.__str__() +\
    ', last_record_id=' + last_record_id.__str__()
    print(log_msg)

    return pressure, ptrend, wind_deg_avg, wind_quadrant, wind_strength, slope, last_record_id


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


def add_forecast_to_db(julian_day, location, pressure, ptrend, wind_deg, wind_quadrant, wind_strength, slope, met_source, last_record_id, hughes38_forecast_text, hughes38_forecast_id, zambretti_forecast_text, zambretti_forecast_id, container_version):
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
    my_dbase = "172.26.0.2"
    mydb, mycursor = connect_db.connect_database(my_dbase, "metminidb")
    #mydb, mycursor = connect_db.connect_database("metmini-mysql", "metminidb")

    ts_local = ts_funcs.epoch_to_local(utc_epoch)
    ts_utc   = ts_funcs.epoch_to_utc(utc_epoch)

    sql = "INSERT INTO forecasts (" \
          "ts_local, " \
          "ts_utc, " \
          "julian, " \
          "location, " \
          "pressure, " \
          "ptrend, " \
          "wind_deg, " \
          "wind_quadrant, " \
          "wind_strength, " \
          "slope, " \
          "met_source, " \
          "last_record_id, " \
          "hughes38_forecast_text, " \
          "hughes38_forecast_id, " \
          "zambretti_forecast_text, " \
          "zambretti_forecast_id, " \
          "container_version" \
          ") " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    val = (ts_local,
           ts_utc,
           julian_day,
           location,
           pressure,
           ptrend,
           wind_deg,
           wind_quadrant,
           wind_strength,
           slope,
           met_source,
           last_record_id,
           hughes38_forecast_text,
           hughes38_forecast_id,
           zambretti_forecast_text,
           zambretti_forecast_id,
           container_version
           )

    print(sql)

    mycursor.execute(sql, val)
    mydb.commit()
    message = "record inserted into Forecasts table OK for location=" + location.__str__()
    print(mycursor.rowcount, message)

# ---------------------------------------------------


# Manually run this at 10 UTC - then do via Cron
def main():
    met_source = "OpenWeatherMap"       # the only source of weather info at the moment
    forecast_hour_utc = 9               # FIXME : Test purposes
    query = {}
    container_version = predictord_funcs.get_version()

    try:
        print('predictord started, container_version=' + container_version)
        now_utc = time.time()
        utc_time_str = ts_funcs.epoch_to_utc(now_utc)

        julian_day = julian.get_julian_date(utc_time_str)
        #julian_day_yesterday = julian_day - 1
        julian_day_yesterday = julian_day

        for place in locations.locations:
            #print("===========================================================")
            print("Location : " + place['location'])

            pressure, ptrend, wind_deg, wind_quadrant, wind_strength, slope , last_record_id = \
                get_forecast_prereqs(place['location'], julian_day_yesterday, forecast_hour_utc, met_source)

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

            full_forecast_txt = "MetMini Forecast\n"
            full_forecast_txt += "---------------\n"
            full_forecast_txt += time.ctime() + "\n"
            full_forecast_txt += "Location : " + place['location'] + "\n"
            full_forecast_txt += "Meteorological data source : " + met_source + "\n"
            full_forecast_txt += "Hughes38  forecast for next 12 hours : " + hughes38_forecast_text + "\n"
            full_forecast_txt += "Hughes38  forecast id : " + hughes38_forecast_id.__str__() + "\n"
            full_forecast_txt += "Zambretti forecast for next 12 hours : " + zambretti_forecast_text + "\n"
            full_forecast_txt += "Zambretti forecast id : " + zambretti_forecast_id.__str__() + "\n"
            full_forecast_txt += "{"
            full_forecast_txt += "pressure=" + pressure.__str__() + " mbar (trend=" + ptrend + ")"
            full_forecast_txt += ", wind_deg=" + wind_deg.__str__()
            full_forecast_txt += ", wind_quadrant=" + wind_quadrant.__str__()
            full_forecast_txt += ", wind_strength=F" + wind_strength.__str__()
            full_forecast_txt += ", pressure_slope=" + slope.__str__()
            full_forecast_txt += ", last_record_id=" + last_record_id.__str__()
            full_forecast_txt += "}"
            #print("------------------------------------------------")
            print(full_forecast_txt)
            #print("------------------------------------------------")

            add_forecast_to_db(julian_day, place['location'], pressure, ptrend, wind_deg, wind_quadrant, wind_strength, slope, met_source, last_record_id, hughes38_forecast_text, hughes38_forecast_id, zambretti_forecast_text, zambretti_forecast_id, container_version)

            # only Tweet out my local forecast
            # if place['location'] == "Stockcross, UK":
            #     twitter.send_tweet(full_forecast_txt)

            #print()

    except Exception as e:
        print("main() : " + e.__str__())


if __name__ == '__main__':
    os.environ['PYTHONUNBUFFERED'] = "1"  # does this help with log buffering ?
    #print('Waiting...')
    #time.sleep(30)  # FIXME : hack to wait until other services are up
    main()
