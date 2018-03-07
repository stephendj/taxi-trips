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

size_in_meter = 100
zones = db['cleaned_trip_zones_' + str(size_in_meter)].find().distinct('start_zone')
keys = []
keys.append('start_hour')
keys.append('start_day')
for zone in zones:
    keys.append('start_zone_' + zone)
    for i in range(0, 23):
        keys.append('zone_hour_' + zone + '_' + str(i))

print('\n'.join(keys), file=open("models/mlp_keys_2.txt", "w"))