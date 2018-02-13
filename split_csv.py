from io import StringIO
from pymongo import MongoClient
import pymongo
import glob
import datetime
import csv
import pandas as pd

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']
collection = db.trips

taxi_csv_path = './Data/GPS/GPS_2015_12.csv'
taxi_id_map_path = './Data/Argometer/DATA GPS.csv'
taxi_id_mapper = {}
with open(taxi_id_map_path, 'r') as mapper_file:
    lines = csv.reader(mapper_file)
    for line in lines:
        taxi_id_mapper[line[0]] = line[1].lower()

existing_taxi_trips = {}
for trip in collection.find().sort('taxi_id', pymongo.ASCENDING):
    if (trip['taxi_id'] in taxi_id_mapper.keys()):
        if (taxi_id_mapper[trip['taxi_id']] not in existing_taxi_trips.keys()):
            existing_taxi_trips[taxi_id_mapper[trip['taxi_id']]] = []

        existing_taxi_trips[taxi_id_mapper[trip['taxi_id']]].append({
            'id': str(trip['_id']),
            'trip_start_datetime': trip['start_date_time'].strftime("%Y-%m-%d %H:%M"),
            'trip_end_datetime': trip['end_date_time'].strftime("%Y-%m-%d %H:%M")
        })

start_index = 0
i = start_index
for chunk in pd.read_csv(taxi_csv_path, dtype = object, header = None, chunksize = 100000):
    for i in range(start_index, len(chunk) + start_index):
        if (chunk[1][i].strip() in existing_taxi_trips.keys()):
            with open('./Split CSV/' + chunk[1][i].strip() + '.csv', 'a', newline = '') as f:
                writer = csv.writer(f)
                writer.writerow([chunk[1][i].strip(), chunk[3][i].strip(), chunk[5][i].strip(), chunk[4][i].strip()])
    start_index = start_index + 100000
    i = start_index