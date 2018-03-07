from pymongo import MongoClient
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from datetime import datetime
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

my_path = os.path.abspath(os.path.dirname(__file__))
available_pickup_zones = list(map(lambda x: x.replace('.pkl', '').replace('_', '|'), os.listdir(os.path.join(my_path, 'models/mlp_models'))))

client = MongoClient('mongodb://localhost:27017/')
db = client['taxi-trips']

if __name__ == '__main__':
    size_in_meter = 100

    trips = db['cleaned_trip_zones_' + str(size_in_meter)].find({ 'start_zone': { '$in': available_pickup_zones } })

    for trip in trips:
        route_zones = trip['route_zones']

        day = day_name_to_day_of_week(trip['start_date_time'].strftime('%A'))
        if (trip['start_hour'] % 2 == 0):
            hour = trip['start_hour']
        else:
            hour = trip['start_hour'] - 1

        for i in range(0, len(route_zones) - 1):
            current_zone = route_zones[i]
            next_zone = route_zones[i + 1]
            
            existing_zone = db['transfer_probabilities_' + str(size_in_meter)].find_one({'start_zone': current_zone, 'destination_zone': trip['end_zone']})
            if (existing_zone == None):
                db['transfer_probabilities_' + str(size_in_meter)].insert({
                    'start_zone': current_zone,
                    'destination_zone': trip['end_zone'],
                    'neighbor_transfers': [{
                        'neighbor_zone': next_zone,
                        'hour': hour,
                        'day': day,
                        'count': 1
                    }]
                })
            else:
                neighbor_transfers = existing_zone['neighbor_transfers']

                # existing_neighbor_transfers = list(filter(lambda transfer: transfer['neighbor_zone'] == next_zone and transfer['hour'] == hour and transfer['day'] == day, neighbor_transfers))
                existing_neighbor_transfers_indexes = [i for i, transfer in enumerate(neighbor_transfers) if (transfer['neighbor_zone'] == next_zone and transfer['hour'] == hour and transfer['day'] == day)]
                if len(existing_neighbor_transfers_indexes) == 0:
                    new_neighbor_transfer = {
                        'neighbor_zone': next_zone,
                        'hour': hour,
                        'day': day,
                        'count': 1
                    }

                    db['transfer_probabilities_' + str(size_in_meter)].find_one_and_update(
                        {'start_zone': current_zone, 'destination_zone': trip['end_zone']},
                        {'$push': { 'neighbor_transfers': new_neighbor_transfer }}
                    )
                else:
                    db['transfer_probabilities_' + str(size_in_meter)].find_one_and_update(
                        {'start_zone': current_zone, 'destination_zone': trip['end_zone']},
                        {'$inc': { 'neighbor_transfers.' + str(existing_neighbor_transfers_indexes[0]) + '.count': 1 }}
                    )
            