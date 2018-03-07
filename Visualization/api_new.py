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
from operator import itemgetter
import itertools

### Initialization
app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGO_DBNAME'] = 'taxi-trips'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/taxi-trips'

mongo = PyMongo(app)

# load models and stuffs
my_path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(my_path, '../models/mlp_keys_new.txt')) as f:
    default_mlp_model_keys = f.read().splitlines()

available_pickup_zones = list(map(lambda x: x.replace('.pkl', '').replace('_', '|'), os.listdir(os.path.join(my_path, '../models/mlp_models'))))

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

def load_mlp_model(name):
    my_path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(my_path, '../models/mlp_models/' + name.replace('|', '_') + '.pkl'), 'rb') as f:
        return pickle.load(f)

### APIs
@app.route('/<size>')
def show_map(size):
    return render_template('map.html', size = size)

@app.route('/start-finish-prediction/<size>')
def show_map_2(size):
    return render_template('map2.html', size = size)

@app.route('/predict-pickups', methods=['GET'])
@cross_origin()
def predict_pickups():
    ## Predict top 10 pick up zones
    top = int(request.args.get('numTrip'))
    pickup_prediction_results = []
    start_date = string_to_date(str(request.args.get('date')))
    start_day = day_name_to_day_of_week(start_date.strftime('%A'))
    start_week = week_of_month(start_date)
    start_hour = int(request.args.get('hour'))

    pickup_test_features = pd.DataFrame([{
        'start_day': start_day,
        'start_hour': start_hour,
        'start_week': start_week
    }])

    for zone in available_pickup_zones:
        mlp = load_mlp_model(zone)

        # dummy_pickup_test_features = pd.get_dummies(pd.DataFrame(pickup_test_features))    
        # existing_columns = dummy_pickup_test_features.keys()

        # for key in default_mlp_model_keys:
        #     if key not in existing_columns:
        #         dummy_pickup_test_features[key] = 0

        # print(dummy_pickup_test_features)

        # scaler = StandardScaler()
        # scaler.fit(dummy_pickup_test_features)
        # dummy_pickup_test_features = scaler.transform(dummy_pickup_test_features)

        # print(dummy_pickup_test_features)

        prediction_result = list(map(round_float, mlp.predict(pickup_test_features)))
        pickup_prediction_results.append({
            'start_zone': zone,
            'pickup_count': prediction_result[0]
        })

    sorted_result = sorted(pickup_prediction_results, key= itemgetter('pickup_count'), reverse=True) 
    return jsonify(sorted_result[:top])

@app.route('/predict-dropoffs', methods=['GET'])
@cross_origin()
def predict_dropoffs():
    pickup_zones = request.args.get('pickup_zones').split(',')
    start_date = string_to_date(str(request.args.get('date')))
    start_day = day_name_to_day_of_week(start_date.strftime('%A'))
    start_hour = int(request.args.get('hour'))
    results = []

    for pickup_zone in pickup_zones:
        mapper = load_nb_mapper(pickup_zone)
        model = load_nb_model(pickup_zone)

        result = model.predict([[start_day, start_hour]])
        results.append(list(mapper.keys())[list(mapper.values()).index(result[0])])

    return jsonify(results)

@app.route('/predict-routes', methods=['GET'])
@cross_origin()
def predict_routes():
    pickup_zones = request.args.get('pickup_zones').split(',')
    dropoff_zones = request.args.get('dropoff_zones').split(',')

    pickup_zones = request.args.get('pickup_zones').split(',')
    dropoff_zones = request.args.get('dropoff_zones').split(',')
    all_routes = []

    for index, pickup_zone in enumerate(pickup_zones):
        routes = list(mongo.db['cleaned_trip_zones_' + str(request.args.get('size'))].find({'start_zone': pickup_zone, 'end_zone': dropoff_zones[index]}).limit(1))
        all_routes.append(routes[0]['route_zones'])

    return jsonify(all_routes)
    # date = string_to_date(str(request.args.get('date')))
    # day = day_name_to_day_of_week(date.strftime('%A'))
    # hour = int(request.args.get('hour'))
    # all_routes = []

    # for index, pickup_zone in enumerate(pickup_zones):
    #     current_zone = pickup_zone
    #     possible_routes = [current_zone]
    #     print(pickup_zone)
    #     print(dropoff_zones[index])

    #     while (current_zone != dropoff_zones[index]):
    #         transfer_probabilities = mongo.db['transfer_probabilities_' + str(request.args.get('size'))].find_one({'start_zone': current_zone, 'destination_zone': dropoff_zones[index]})
    #         if (transfer_probabilities == None):
    #             print('none')
    #             break
    #         neighbor_transfers = transfer_probabilities['neighbor_transfers']
    #         possible_transfers = list(filter(lambda transfer: transfer['hour'] == hour and transfer['day'] == day, neighbor_transfers))
    #         if (len(possible_transfers) == 0):
    #             grouped_possible_transfers = [{
    #                 'neighbor_zone': key,
    #                 'count': sum(int(item['count']) for item in group)
    #             } for key, group in itertools.groupby(neighbor_transfers, key = lambda x: x['neighbor_zone'])]
    #             sorted_possible_transfer = sorted(grouped_possible_transfers, key = itemgetter('count'), reverse = True)

    #             if (len(possible_routes) > 2 and sorted_possible_transfer[0] == possible_routes[-2]):
    #                 possible_routes.append(sorted_possible_transfer[1]['neighbor_zone'])
    #                 current_zone = sorted_possible_transfer[1]['neighbor_zone']
    #             else:
    #                 possible_routes.append(sorted_possible_transfer[0]['neighbor_zone'])
    #                 current_zone = sorted_possible_transfer[0]['neighbor_zone']
    #         elif (len(possible_transfers) == 1):
    #             possible_routes.append(possible_transfers[0]['neighbor_zone'])
    #             current_zone = possible_transfers[0]['neighbor_zone']
    #         else:
    #             grouped_possible_transfers = [{
    #                 'neighbor_zone': key,
    #                 'count': sum(int(item['count']) for item in group)
    #             } for key, group in itertools.groupby(possible_transfers, key = lambda x: x['neighbor_zone'])]
    #             sorted_possible_transfer = sorted(grouped_possible_transfers, key = itemgetter('count'), reverse = True)

    #             i = 0
    #             while(i < len(sorted_possible_transfer) and sorted_possible_transfer[i] in possible_routes):
    #                 i += 1

    #             possible_routes.append(sorted_possible_transfer[i]['neighbor_zone'])
    #             current_zone = sorted_possible_transfer[i]['neighbor_zone']
    #             print(current_zone)

    #     print(possible_routes)
    #     print()
    #     print()
    #     all_routes.append(possible_routes)


    # return jsonify(all_routes)

if __name__ == '__main__':
    app.run(debug = True)