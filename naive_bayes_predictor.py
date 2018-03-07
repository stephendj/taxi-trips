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

def load_mapper(name ):
    with open('models/nb_mappers/' + name.replace('|', '_') + '.pkl', 'rb') as f:
        return pickle.load(f)

def load_model(name ):
    with open('models/nb_models/' + name.replace('|', '_') + '.pkl', 'rb') as f:
        return pickle.load(f)

def save_obj(obj, name):
    with open('models/nb_models/'+ name.replace('|', '_') + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

if __name__ == '__main__':
    size_in_meter = 100
    chosen_zone = '51|50'
    mapper = load_mapper(chosen_zone)
    print(mapper)
    model = load_model(chosen_zone)

    result = model.predict([[5, 18]])
    print(result[0])
    print(list(mapper.keys())[list(mapper.values()).index(result[0])])