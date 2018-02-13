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

    pickup_counts = pd.DataFrame(list(db['pickup_counts_' + str(size_in_meter)].find()))

    features = pickup_counts.drop('_id', axis = 1).drop('pickup_count', axis = 1).drop('start_date', axis = 1)
    features = pd.get_dummies(features)
    # features = pickup_counts.drop('_id', axis = 1).drop('pickup_count', axis = 1).drop('start_date', axis = 1)
    labels = pickup_counts['pickup_count']

    print(features.dtypes)

    # unique_zones = pickup_counts['start_zone'].unique()
    # for zone in unique_zones:
    #     current_feature = features.loc[features['start_zone'] == zone].drop('start_zone', axis = 1)
    #     print(list(raw_features.keys()))
    #     current_feature = current_feature.astype('category', categories = list(raw_features.keys()))
    #     # print(zone, current_feature)
    #     break
        

    scaler = StandardScaler()
    scaler.fit(features)
    features = scaler.transform(features)



    mlp = MLPRegressor(
        solver='lbfgs',
        alpha=0.001, tol=0.00001, hidden_layer_sizes = (10, 20, 30),
        max_iter = 1500, activation = 'relu', random_state = 9,
        learning_rate = 'adaptive', shuffle = True
    )

    mlp.fit(features, labels)
    print(mlp.score(features, labels))

    # # save the model to disk
    # filename = 'models/mlpregression_model.sav'
    # pickle.dump(mlp, open(filename, 'wb'))