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

    for index, row in all_trips_df.iterrows():
        db['dropoffs_' + str(size_in_meter) + '_2'].insert({
            'start_zone': row['start_zone'],
            'start_day': day_name_to_day_of_week(row['start_day'].split('_')[0]),
            'zone_hour': row['start_zone'] + '_' + str(row['start_hour']),
            'zone_hour_day': row['start_zone'] + '_' + str(row['start_hour']) + '_' + str(day_name_to_day_of_week(row['start_day'].split('_')[0])),
            'start_hour': row['start_hour'],
            'start_date': row['start_date'],
            'end_zone': row['end_zone']
        })