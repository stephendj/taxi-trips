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

for trip in db.trips.find():
    if ('routes' in trip and len(trip['routes']) > 2 and trip['distance'] > 1):
        db.cleaned_trips.insert({
            'start_date_time': trip['start_date_time'],
            'end_date_time': trip['end_date_time'],
            'distance': trip['distance'],
            'routes': trip['routes']
        })