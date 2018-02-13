from io import StringIO
from pymongo import MongoClient
import glob
import datetime

pdf_year = 2015
pdf_month = 12
special_file_names = ['./Parsed PDF\\12-1.txt', './Parsed PDF\\12-2.txt']
special_excluded_dates = [27, 28, 29, 30]
parsed_pdf_path = './Parsed PDF/*.txt'
files = glob.glob(parsed_pdf_path)

if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client['taxi-trips']
    collection = db.trips
    trips = []

    for file in files:
        with open(file, 'r') as file:
            lines = file.read().split('\n')

            for i in range(0, len(lines) - 1):
                if lines[i].strip() == 'Page.1':
                    # Find the trip date
                    is_trip_date_found  = False
                    while (i < len(lines) and not is_trip_date_found):
                        line = lines[i].strip()
                        if (line.startswith('Start:')):
                            is_trip_date_found = True
                        else:
                            i = i + 1
                    trip_date = line[6:16]
                    trip_year = int(trip_date.split('-')[0])
                    trip_month = int(trip_date.split('-')[1])
                    trip_day = int(trip_date.split('-')[2])
                    if (trip_year != 2015):
                        continue
                    if (trip_month != 11 and trip_month != 12):
                        continue

                    # Find the taxi id
                    is_taxi_id_found = False
                    while (i < len(lines) and not is_taxi_id_found):
                        line = lines[i].strip()
                        if (line.startswith('Taxi:00-')):
                            is_taxi_id_found = True
                        else:
                            i = i + 1

                    taxi_id =  line[8:12]

                    # Find the taxi trips header
                    is_taxi_trips_found = False
                    while (i < len(lines) and not is_taxi_trips_found):
                        line = lines[i].strip()
                        if (line.startswith('ANALYSIS OF HIRED DETAILS')):
                            while (i < len(lines) and not is_taxi_trips_found):
                                line = lines[i].strip()
                                if (line.startswith('1')):
                                    is_taxi_trips_found = True
                                else:
                                    i = i + 1
                        else:
                            i = i + 1  

                    if (is_taxi_trips_found):
                        trip_number = 1
                        split_line = lines[i].strip().split()

                        trip_index = 0
                        while (split_line[trip_index] != '--'):
                            if ('.' in split_line[trip_index + 2]):
                                date_time = split_line[trip_index + 2].split('.')
                                day = int(date_time[0])
                                time_range = date_time[1].split('-')
                            else:
                                time_range = split_line[trip_index + 2].split('-')

                            if (file.name in special_file_names and day in special_excluded_dates):
                                break

                            distance = float(split_line[trip_index + 3])
                            if (distance == 0):
                                break

                            start_hour = int(time_range[0].split(':')[0])
                            start_minute = int(time_range[0].split(':')[1])
                            end_hour = int(time_range[1].split(':')[0])
                            end_minute = int(time_range[1].split(':')[1])

                            trip = {
                                'taxi_id': taxi_id,
                                'distance': distance,
                                'start_date_time': datetime.datetime(pdf_year, pdf_month, day, start_hour, start_minute),
                                'end_date_time': datetime.datetime(pdf_year, pdf_month, day, end_hour, end_minute)
                            }

                            trips.append(trip)
                            if (trip_number % 2 == 0):
                                i = i + 1
                                split_line = lines[i].strip().split()
                                trip_index = 0
                            else:
                                trip_index = 6

                            trip_number = trip_number + 1

    collection.insert_many(trips)