from io import StringIO
from pymongo import MongoClient
import pymongo
import glob
import datetime
import csv
import pandas as pd
import os.path
import decimal
from math import ceil

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

def week_of_month(dt):
    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))

def drange(x, y, jump):
  while x < y:
    yield float(x)
    x += decimal.Decimal(jump)

def getZoneNameFromLatLong(lat, long, size):
    upper_left_lat = decimal.Decimal(-6.839)
    upper_left_long = decimal.Decimal(107.547)
    bottom_right_lat = decimal.Decimal(-6.967)
    bottom_right_long = decimal.Decimal(107.738)
    step = decimal.Decimal(size / 100000)

    if (abs(lat) < abs(upper_left_lat) or abs(lat) > abs(bottom_right_lat) or long < upper_left_long or long > bottom_right_long):
        return '|'

    zone_x = 0
    for i in drange(abs(upper_left_lat), abs(bottom_right_lat), step):
        if (abs(lat) < i):
            break
        else:
            zone_x += 1

    zone_y = 0
    for j in drange(upper_left_long, bottom_right_long, step):
        if (abs(long) < j):
            break
        else:
            zone_y += 1

    return str(zone_x) + '|' + str(zone_y)


if __name__ == '__main__':
    size_in_meter = 100

    for trip in db.cleaned_trips.find():
        route_zones = []
        for route in trip['routes']:
            zone = getZoneNameFromLatLong(route['lat'], route['long'], size_in_meter)
            if (zone == '|'):
                continue
            else:
                if (not route_zones):
                    route_zones.append(zone)

                if (route_zones and route_zones[-1] != zone):
                    route_zones.append(zone)

        if (not route_zones or len(route_zones) < 2):
            continue

        db['cleaned_trip_zones_' + str(size_in_meter)].insert({
            'original_trip_id': str(trip['_id']),
            'start_date_time': trip['start_date_time'],
            'end_date_time': trip['end_date_time'],
            'start_date': str(trip['start_date_time'].date()),
            'start_day': trip['start_date_time'].strftime('%A') + '_week_' + str(week_of_month(trip['start_date_time'])),
            'start_hour': trip['start_date_time'].hour,
            'start_zone': route_zones[0],
            'end_zone': route_zones[-1],
            'route_zones': route_zones
        })
