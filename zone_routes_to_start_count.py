from io import StringIO
from pymongo import MongoClient
import pymongo
import glob
import datetime
import csv
import pandas as pd
import os.path
import decimal
import math

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

def day_name_to_day_of_week(x):
    if x == 'Monday':
        return 1
    elif x == 'Tuesday':
        return 2
    elif x == 'Wednesday':
        return 3
    elif x == 'Thursday':
        return 4
    elif x == 'Friday':
        return 5
    elif x == 'Saturday':
        return 6
    else:
        return 7

def hour_interval_formatter(x):
    start_hour_granularity = 2
    # if x % 3 == 2:
    #     return x - 2
    # elif x % 3 == 1:
    #     return x - 1
    # else:
    #     return x
    if x % 2 == 1:
        return x - 1
    else:
        return x

if __name__ == '__main__':
    size_in_meter = 100

    all_trips_df = pd.DataFrame(list(db['cleaned_trip_zones_' + str(size_in_meter)].find()))
    all_trips_df['start_hour'] = list(map(hour_interval_formatter, all_trips_df['start_hour']))

    grouped_df = all_trips_df.groupby(['start_zone', 'start_day', 'start_hour', 'start_date']).size()
    for index, row in grouped_df.iteritems():
        db['pickup_counts_' + str(size_in_meter) + '_3'].insert({
            'start_zone': index[0],
            'start_day': day_name_to_day_of_week(index[1].split('_')[0]),
            'zone_hour': index[0] + '_' + str(index[2]),
            'zone_hour_day': index[0] + '_' + str(index[2]) + '_' + str(day_name_to_day_of_week(index[1].split('_')[0])),
            'start_hour': index[2],
            'start_date': index[3],
            'pickup_count': int(row)
        })