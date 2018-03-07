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

def float_to_int(x): return int(x)

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

if __name__ == '__main__':
    size_in_meter = 100

    pickup_counts = pd.DataFrame(list(db['pickup_counts_' + str(size_in_meter) + '_3'].find()))

    features = pickup_counts.drop('_id', axis = 1).drop('pickup_count', axis = 1).drop('start_date', axis = 1).drop('zone_hour_day', axis = 1)
    features = pd.get_dummies(features)
    labels = pickup_counts['pickup_count']

    # print('\n'.join(features.keys()), file=open("models/mlp_keys_2.txt", "w"))
    with open('models/mlp_keys_2.txt') as f:
        default_keys = f.read().splitlines()

    existing_columns = features.keys()

    for key in default_keys:
        if key not in existing_columns:
            features[key] = 0
    print(len(features))
    scaler = StandardScaler()
    scaler.fit(features)
    features = scaler.transform(features)

    mlp = MLPRegressor(
        solver='lbfgs',
        alpha=0.001, tol=0.00001, hidden_layer_sizes = (30, 20, 10),
        max_iter = 1500, activation = 'relu', random_state = 10,
        learning_rate = 'adaptive', shuffle = True
    )

    mlp.fit(features, labels)
    print(mlp.score(features, labels))

    filename = 'models/mlpregression_model_4.sav'
    pickle.dump(mlp, open(filename, 'wb'))