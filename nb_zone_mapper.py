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
import pickle

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

def save_obj(obj, name):
    with open('models/nb_mappers/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

size_in_meter = 100
start_zones = db['dropoffs_' + str(size_in_meter) + '_2'].find().distinct('start_zone')
for zone in start_zones:
    end_zones = db['dropoffs_' + str(size_in_meter) + '_2'].find({ 'start_zone': zone }).distinct('end_zone')
    sorted_end_zones = sorted(end_zones)

    zones_with_index = {}
    for index, item in enumerate(sorted_end_zones):
        zones_with_index[item] = index

    save_obj(zones_with_index, zone.replace('|', '_'))