# functions that use SQL to interact with the database schemea

import time

import mysql.connector
import trend
import ts_funcs
import metfuncs

def connect_database(mysql_host, db_name):
    """

    :return:
    """
    print('Accessing MySQL host ' + mysql_host + ' ...')

    mydb = mysql.connector.connect(
        host=mysql_host,
        database=db_name,
        user="metmini",
        password="metmini"
    )

    mycursor = mydb.cursor()

    return (mydb, mycursor)



def add_forecast_to_db(julian_day, location, lat, lon, pressure, ptrend, wind_deg, wind_quadrant, wind_strength, temp_avg, rain_avg, snow_avg, humidity_avg, dew_point_avg, slope, met_source, last_weather_description, last_record_id, hughes38_forecast_text, hughes38_forecast_id, zambretti_forecast_text, zambretti_forecast_id, metmini_forecast_text, metmini_forecast_id, api_forecast_text, last_record_timestamp, sky_picture_filename, window_hours, container_version):
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
    mydb, mycursor = connect_database(my_dbase, "metminidbflux")
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
          "window_hours, " \
          "container_version" \
          ") " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

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
           window_hours,
           container_version
           )

    #print(sql)

    mycursor.execute(sql, val)
    mydb.commit()
    message = "record inserted into MetMini Forecasts table OK for location=" + location.__str__()
    print(mycursor.rowcount, message)


# This is heavily modified from the master branch
def get_forecast_prereqs(location, julian_day, forecast_hour_utc, met_source, window_hours):
    """
    Retrieve the required values needed to make a forecast from the 'actual' database
    :return:
    """
    try:
        min_recs_to_process = 6

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

        recs_to_retrieve = window_hours * 6   # was 4 : number of readings to use to determine pressure trend and wind_deg

        #pass
        #index = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]  # FIXME : calc from recs_to_retrieve
        # recs_to_retrieve = 2
        # index = [1, 2]

        my_dbase = "192.168.1.180"
        mydb, mycursor = connect_database(my_dbase, "metminidb")
        # mydb, mycursor = connect_db.connect_database("metmini-mysql", "metminidb")

        # Retrieve the FIRST set of records that are AFTER the 0900 UTC optimum forecasting time
        sql_query = """SELECT * FROM actual WHERE location = %s and julian = %s and hour_utc >= %s and met_source = %s limit %s"""
        # sql_query = """SELECT * FROM actual WHERE location = %s and julian = %s and source = %s limit %s"""
        print(
        'Retrieve Actual Table records for julian_day=' + julian_day.__str__() + ', forecast_hour_utc=' + forecast_hour_utc.__str__() + ', met_source=' + met_source + ', window_hours=' + window_hours.__str__())
        mycursor.execute(sql_query, (location, julian_day, forecast_hour_utc, met_source, recs_to_retrieve))
        records = mycursor.fetchall()
        records_retrieved = len(records)
        print(records_retrieved.__str__() + ' records retrieved from historical data')

        if records_retrieved <= min_recs_to_process :
            print(
            "Unable to retrieve sufficient historical records (min_recs_to_process=" + min_recs_to_process.__str__() + ") from MetMini Actual table")
            return None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
        else:
            index = list(range(1, records_retrieved + 1))
            print('index=' + index.__str__())

        # fixme : fragile = need named columns not numbers - first row is 0
        for row in records:
            pressure_values.append(row[8])
            wind_speed_values.append(row[9])
            wind_deg_values.append(row[10])
            wind_strength_values.append(row[13])
            temp_values.append(row[15])
            dew_point_values.append(row[17])
            humidity_values.append(row[19])
            rain_values.append(row[21])
            snow_values.append(row[22])

        last_record_id = row[0]  # id of the last record to be used
        last_main = row[6]
        last_description = row[7]
        last_weather_description = last_main + " (" + last_description + ")"
        last_record_timestamp = row[2]  # ts_utc

        lat = row[25]
        lon = row[26]

        trend_str, slope = trend.trendline(index, pressure_values)
        wind_deg_avg = int(sum(wind_deg_values)) / len(wind_deg_values)
        wind_deg_avg = int(wind_deg_avg)

        wind_strength_avg = int(sum(wind_strength_values)) / len(wind_strength_values)
        wind_strength_avg = int(wind_strength_avg)

        pressure = pressure_values[0]  # use the first one
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
              ', wind_deg_avg=' + wind_deg_avg.__str__() + \
              ', wind_quadrant=' + wind_quadrant + \
              ', wind_strength_avg=' + wind_strength_avg.__str__() + \
              ', temp_avg=' + temp_avg.__str__() + \
              ', rain_avg=' + rain_avg.__str__() + \
              ', snow_avg=' + snow_avg.__str__() + \
              ', humidity_avg=' + humidity_avg.__str__() + \
              ', dew_point_avg=' + dew_point_avg.__str__() + \
              ', slope=' + slope.__str__() + \
              ', last_weather_description=' + last_weather_description.__str__() + \
              ', last_record_timestamp=' + last_record_timestamp.__str__() + \
              ', last_record_id=' + last_record_id.__str__()
        print(log_msg)

        return lat, lon, pressure, ptrend, wind_deg_avg, wind_quadrant, wind_strength_avg, temp_avg, rain_avg, snow_avg, humidity_avg, dew_point_avg, slope, last_weather_description, last_record_id, last_record_timestamp

    except Exception as e:
        print('get_forecast_prereqs() : error : ' + e.__str__())
        return None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
