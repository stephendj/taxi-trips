from pymongo import MongoClient
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt
import pymongo
import pandas as pd
import os.path
import decimal
import pickle
import math

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

def save_obj(obj, name):
    with open('models/mlp_models/'+ name.replace('|', '_') + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

if __name__ == '__main__':
    size_in_meter = 100

    start_zones = db['pickup_counts_' + str(size_in_meter) + '_2'].find().distinct('start_zone')

    with open('models/mlp_keys_new.txt') as f:
        default_keys = f.read().splitlines()

    for start_zone in start_zones:
        pickup_counts = pd.DataFrame(list(db['pickup_counts_' + str(size_in_meter) + '_2'].find({'start_zone': start_zone})))

        if (len(pickup_counts) < 6):
            continue

        features = pickup_counts.drop('_id', axis = 1).drop('pickup_count', axis = 1).drop('start_date', axis = 1).drop('start_zone', axis = 1)
        features['start_week'] = features['start_day'].apply(lambda x: x.split('_week_')[1])
        features['start_day'] = features['start_day'].apply(lambda x: day_name_to_day_of_week(x.split('_week_')[0]))

        # features = pd.get_dummies(features)
        labels = pickup_counts['pickup_count']

        # existing_columns = features.keys()
        # for key in default_keys:
        #     if key not in existing_columns:
        #         features[key] = 0

        # scaler = StandardScaler()
        # scaler.fit(features)
        # features = scaler.transform(features)

        mlp = MLPRegressor(
            solver='lbfgs',
            alpha=0.001, tol=0.00001, hidden_layer_sizes = (30, 20, 10),
            max_iter = 1500, activation = 'relu', random_state = 10,
            learning_rate = 'adaptive', shuffle = True
        )

        mlp.fit(features, labels)
        score = mlp.score(features, labels)
        if score > 0:
            save_obj(mlp, start_zone)