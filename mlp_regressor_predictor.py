from pymongo import MongoClient
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
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

def format_date(x, pos=None):
    return dates.num2date(x).strftime('%Y-%m-%d %H:00, %A') #use FuncFormatter to format dates

def string_to_date(x):
    return datetime.strptime(x, '%Y-%m-%d')

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

if __name__ == '__main__':
    size_in_meter = 100
    selected_zone = '51|50'

    all_pickup_counts = pd.DataFrame(list(db['pickup_counts_' + str(size_in_meter)].find()))
    all_features = all_pickup_counts.drop('_id', axis = 1).drop('pickup_count', axis = 1).drop('start_date', axis = 1)
    all_features_keys = pd.get_dummies(all_features).keys()

    pickup_counts = pd.DataFrame(list(db['pickup_counts_' + str(size_in_meter)].find({
        'start_zone': selected_zone,
        'start_day': { '$regex' : '.*week_3.*'}
    })))

    # load model
    filename = 'models/mlpregression_model.sav'
    mlp = pickle.load(open(filename, 'rb'))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    x = list(map(dates.date2num, map(string_to_date, pickup_counts['start_date'])))
    x = list(map(string_to_date, pickup_counts['start_date']))
    y = pickup_counts['start_hour']
    xy = []
    for i in range(0, len(x)):
        xy.append(datetime(x[i].year, x[i].month, x[i].day, y[i], 0, 0))

    z = pickup_counts['pickup_count']
    xyz = dict(zip(xy, z))
    sorted_xyz_keys = sorted(xyz)
    sorted_z = []
    for key in sorted_xyz_keys:
        sorted_z.append(xyz[key])

    # plot the actual one
    ax.plot_date(sorted_xyz_keys, sorted_z, label = 'Actual', linestyle = '-', color = 'b')

    # predict using model
    features = pickup_counts.drop('_id', axis = 1).drop('pickup_count', axis = 1).drop('start_date', axis = 1)
    print(features)
    features = features.astype('category', categories = all_features_keys)
    features = pd.get_dummies(features)
    print(features)

    # scaler = StandardScaler()
    # scaler.fit(features)
    # features = scaler.transform(features)
    # print(features)
    # print(mlp.predict(features))


    # ax.set_ylim([0, 6])
    # ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    # for tl in ax.xaxis.get_ticklabels():
    #    tl.set_ha('right')
    #    tl.set_rotation(15)

    # ax.legend()

    # plt.show()