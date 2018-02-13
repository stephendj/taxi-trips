from io import StringIO
from pymongo import MongoClient
import pymongo
import glob
import datetime
import csv
import pandas as pd
import os.path

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']
collection = db.trips

taxi_csv_path = './Data/GPS/GPS_2015_12.csv'
taxi_id_map_path = './Data/Argometer/DATA GPS.csv'
taxi_route_path = './Split CSV/'
taxi_id_mapper = {}
with open(taxi_id_map_path, 'r') as mapper_file:
    lines = csv.reader(mapper_file)
    for line in lines:
        taxi_id_mapper[line[0]] = line[1].lower()

existing_taxi_trips = {}
for trip in collection.find({ 'routes': { '$exists': False } }).sort('taxi_id', pymongo.ASCENDING):
    if (trip['taxi_id'] in taxi_id_mapper.keys()):
        if (taxi_id_mapper[trip['taxi_id']] not in existing_taxi_trips.keys()):
            existing_taxi_trips[taxi_id_mapper[trip['taxi_id']]] = []

        existing_taxi_trips[taxi_id_mapper[trip['taxi_id']]].append({
            'id': trip['_id'],
            'trip_start_datetime': trip['start_date_time'].strftime("%Y-%m-%d %H:%M"),
            'trip_end_datetime': trip['end_date_time'].strftime("%Y-%m-%d %H:%M")
        })

for taxi_id, trips in existing_taxi_trips.items():
    file_path = taxi_route_path + taxi_id + '.csv'
    if (not os.path.isfile(file_path)):
        continue

    for trip in trips:
        print(taxi_id)
        print(trip)
        is_trip_found = False
        is_trip_finished = False
        trip_routes = []

        start_index = 0
        i = start_index
        for chunk in pd.read_csv(file_path, dtype = object, header = None, chunksize = 10000):
            for i in range(start_index, len(chunk) + start_index):
                csv_datetime = chunk[1][i][0:16]
                
                if (is_trip_finished):
                    break

                if (is_trip_found):
                    if (float(chunk[2][i]) != trip_routes[-1]['lat'] and float(chunk[3][i]) != trip_routes[-1]['long']):
                        trip_routes.append({
                            'lat': float(chunk[2][i]),
                            'long': float(chunk[3][i])
                        })

                if (trip['trip_start_datetime'] == csv_datetime):
                    is_trip_found = True
                    trip_routes.append({
                        'lat': float(chunk[2][i]),
                        'long': float(chunk[3][i])
                    })

                if (trip['trip_end_datetime'] == csv_datetime and is_trip_found):
                    is_trip_finished = True
                    if (float(chunk[2][i]) != trip_routes[-1]['lat'] and float(chunk[3][i]) != trip_routes[-1]['long']):
                        trip_routes.append({
                            'lat': float(chunk[2][i]),
                            'long': float(chunk[3][i])
                        })
            if (is_trip_finished):
                break

            start_index = start_index + 10000
            i = start_index

        collection.find_one_and_update(
            {'_id': trip['id']},
            {'$set': { 'routes': trip_routes }}
        )