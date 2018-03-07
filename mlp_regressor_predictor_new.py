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

def round_float(x):
    return int(round(x))

def format_date(x, pos=None):
    return dates.num2date(x).strftime('%Y-%m-%d %H:00, %A')

def string_to_date(x):
    return datetime.strptime(x, '%Y-%m-%d')

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

def load_mlp_model(name):
    my_path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(my_path, 'models/mlp_models/' + name.replace('|', '_') + '.pkl'), 'rb') as f:
        return pickle.load(f)

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

if __name__ == '__main__':
    size_in_meter = 100
    selected_zone = '78|55'

    mlp = load_mlp_model(selected_zone)

    pickup_counts = pd.DataFrame(list(db['pickup_counts_' + str(size_in_meter) + '_2'].find({
        'start_zone': selected_zone,
    }).sort([('start_date', pymongo.ASCENDING)])))

    fig = plt.figure()
    plt.style.use('fivethirtyeight')
    # ax = fig.add_subplot(211)
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
    plt.plot(sorted_xyz_keys, sorted_z, label = 'Actual', linestyle = '-', color = 'b')

    # predict using model
    features = pickup_counts.drop('_id', axis = 1).drop('pickup_count', axis = 1).drop('start_date', axis = 1).drop('start_zone', axis = 1)
    features['start_week'] = features['start_day'].apply(lambda x: x.split('_week_')[1])
    features['start_day'] = features['start_day'].apply(lambda x: day_name_to_day_of_week(x.split('_week_')[0]))
    prediction_result = list(map(round_float, mlp.predict(features)))
    plt.plot(sorted_xyz_keys, prediction_result, label = 'predicted', linestyle = '-', color = 'r')
    plt.xticks(rotation = 30)
    # ax.set_ylim([0, 10])
    # ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    # for tl in ax.xaxis.get_ticklabels():
    #    tl.set_ha('right')
    #    tl.set_rotation(15)

    plt.legend(loc=0)

    plt.show()