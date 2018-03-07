from pymongo import MongoClient
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
import matplotlib.pyplot as plt
import pymongo
import pandas as pd
import os.path
import decimal
import pickle
import math

def float_to_int(x): return int(x)

def load_obj(name ):
    with open('models/nb_mappers/' + name.replace('|', '_') + '.pkl', 'rb') as f:
        return pickle.load(f)

def save_obj(obj, name):
    with open('models/nb_models/'+ name.replace('|', '_') + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

if __name__ == '__main__':
    size_in_meter = 100

    # start_zones = db['dropoffs_' + str(size_in_meter) + '_2'].find().distinct('start_zone')
    start_zones = ['74|56']
    for start_zone in start_zones:
        mapper = load_obj(start_zone)

        features = list(db['dropoffs_' + str(size_in_meter) + '_2'].find({ 'start_zone': start_zone }))
        array_features = []
        labels = []
        for item in features:
            array_features.append([
                item['start_day'],
                item['start_hour'],
                # mapper[item['start_zone']]
            ])
            labels.append(mapper[item['end_zone']])
        print(array_features, labels)

        clf = GaussianNB()
        clf.fit(array_features, labels)
        # result = clf.predict([[3, 8, mapper['56|51']]])
        # print(list(mapper.keys())[list(mapper.values()).index(result[0])])
        print(clf.score(array_features, labels))

        # save_obj(clf, start_zone)