import time

import call_rest_api
import definitions


def calc_forecast_sequence(locations_list):
    location = locations_list[0]    # FIXME - just use first one - OK if all in same part of world ?

    query = {}
    query['location'] = location['location']
    query['lat'] = location['lat'].__str__()
    query['lon'] = location['lon'].__str__()

    # call the external API
    status_code, response_dict = call_rest_api.call_rest_api(
        definitions.metminimisc_service_endpoint_base + '/get_solar_times', query)



    # sort based on values
    phases = {}
    phases['morning'] = '09:00:00'      # pass through in func parameters
    phases['afternoon'] = '14:00:00'
    phases['evening'] = '20:00:00'
    phases['sunrise'] = response_dict['sunrise']
    phases['sunset'] = response_dict['sunset']
    phases['solar_noon'] = response_dict['solar_noon']

    #now = time.ctime()
    #now = now.split(' ')[3]
    #phases['now'] = now

    sorted_phases_dict = dict(sorted(phases.items(), key=lambda item: item[1]))
    sorted_phases = [tuple(reversed(x)) for x in sorted_phases_dict.items()]

    print('sorted_phases==' + sorted_phases.__str__())

    return sorted_phases
