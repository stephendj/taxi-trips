from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask_pymongo import PyMongo
from flask_pymongo import ObjectId
from flask_cors import CORS, cross_origin
from datetime import datetime
from math import ceil
import itertools
from sklearn.preprocessing import StandardScaler
import matplotlib.dates as dates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import pymongo
import os.path
import decimal
import pickle
import math

### Initialization
app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGO_DBNAME'] = 'taxi-trips'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/taxi-trips'

mongo = PyMongo(app)

# load models and stuffs
my_path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(my_path, '../models/mlp_keys.txt')) as f:
    default_mlp_model_keys = f.read().splitlines()

with open(os.path.join(my_path, '../models/mlpregression_model_2.sav'), 'rb') as f:
    mlp = pickle.load(f)

### Utility Functions
def round_float(x):
    return int(round(x))

def toJSON(document):
    document['id'] = str(document['_id'])
    document.pop('_id')
    return document

def string_to_date(x):
    return datetime.strptime(x, '%m/%d/%Y')

def week_of_month(dt):
    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))

def take(n, iterable):
    return list(islice(iterable, n))

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

def load_nb_mapper(name):
    my_path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(my_path, '../models/nb_mappers/' + name.replace('|', '_') + '.pkl'), 'rb') as f:
        return pickle.load(f)

def load_nb_model(name):
    my_path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(my_path, '../models/nb_models/' + name.replace('|', '_') + '.pkl'), 'rb') as f:
        return pickle.load(f)

### APIs
@app.route('/<size>')
def show_map(size):
    return render_template('map.html', size = size)

@app.route('/start-finish-prediction/<size>')
def show_map_2(size):
    return render_template('map2.html', size = size)

@app.route('/trips', methods=['GET'])
@cross_origin()
def get_all_trips():
    trips = mongo.db['cleaned_trip_zones_' + str(request.args.get('size'))]
    output = []
    for trip in trips.find({ 'original_trip_id': '5999b6bf347aa80c7452265e' }):
        output.append(toJSON(trip))
        break
    return jsonify(output)

@app.route('/predict-pickups', methods=['GET'])
@cross_origin()
def predict_pickups():
    ## Predict top 10 pick up zones
    top = int(request.args.get('numTrip'))
    pickup_zones = mongo.db['pickup_counts_' + str(request.args.get('size')) + '_2'].find({'pickup_count': {'$gt': 1}}).distinct('start_zone')
    pickup_test_features = []
    start_date = string_to_date(str(request.args.get('date')))
    start_day = start_date.strftime('%A') + '_week_' + str(week_of_month(start_date))
    start_hour = int(request.args.get('hour'))

    for zone in pickup_zones:
        pickup_test_features.append({
            'start_zone': zone,
            'start_day': start_day,
            'start_hour': start_hour
        })

    dummy_pickup_test_features = pd.get_dummies(pd.DataFrame(pickup_test_features))    
    existing_columns = dummy_pickup_test_features.keys()

    for key in default_mlp_model_keys:
        if key not in existing_columns:
            dummy_pickup_test_features[key] = 0

    scaler = StandardScaler()
    scaler.fit(dummy_pickup_test_features)
    dummy_pickup_test_features = scaler.transform(dummy_pickup_test_features)

    prediction_result = list(map(round_float, mlp.predict(dummy_pickup_test_features)))

    combined_prediction_result = dict(zip(list(map((lambda x: x['start_zone']), pickup_test_features)), prediction_result))
    sorted_pickup_prediction = [(k, combined_prediction_result[k]) for k in sorted(combined_prediction_result, key=combined_prediction_result.get, reverse=True)]
    return jsonify(sorted_pickup_prediction[:top])

@app.route('/predict-dropoffs', methods=['GET'])
@cross_origin()
def predict_dropoffs():
    pickup_zones = request.args.get('pickup_zones').split(',')
    results = []
    for pickup_zone in pickup_zones:
        mapper = load_nb_mapper(pickup_zone)
        model = load_nb_model(pickup_zone)
        start_date = string_to_date(str(request.args.get('date')))
        start_day = day_name_to_day_of_week(start_date.strftime('%A'))
        start_hour = int(request.args.get('hour'))

        result = model.predict([[start_day, start_hour]])
        results.append(list(mapper.keys())[list(mapper.values()).index(result[0])])

    return jsonify(results)

@app.route('/predict-routes', methods=['GET'])
@cross_origin()
def predict_routes():
    pickup_zones = request.args.get('pickup_zones').split(',')
    dropoff_zones = request.args.get('dropoff_zones').split(',')
    all_routes = []

    for index, pickup_zone in enumerate(pickup_zones):
        routes = list(mongo.db['cleaned_trip_zones_' + str(request.args.get('size'))].find({'start_zone': pickup_zone, 'end_zone': dropoff_zones[index]}).limit(1))
        all_routes.append(routes[0]['route_zones'])

    return jsonify(all_routes)

if __name__ == '__main__':
    app.run(debug = True)