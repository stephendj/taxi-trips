from io import StringIO
from pymongo import MongoClient
import pymongo
import glob
import datetime
import csv
import pandas as pd
import os.path
import decimal

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

if __name__ == '__main__':
    size_in_meter = 100

    all_trips_df = pd.DataFrame(list(db['cleaned_trip_zones_' + str(size_in_meter)].find()))

    grouped_df = all_trips_df.groupby(['start_zone', 'start_day', 'start_hour', 'start_date']).size()
    for index, row in grouped_df.iteritems():
        db['pickup_counts_' + str(size_in_meter)].insert({
            'start_zone': index[0],
            'start_day': index[1],
            'start_hour': index[2],
            'start_date': index[3],
            'pickup_count': int(row)
        })