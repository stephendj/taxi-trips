from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask_pymongo import PyMongo
from flask_pymongo import ObjectId
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MONGO_DBNAME'] = 'taxi-trips'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/taxi-trips'

mongo = PyMongo(app)

def toJSON(document):
    document['id'] = str(document['_id'])
    document.pop('_id')
    return document

@app.route('/<size>')
def show_map(size):
    return render_template('map.html', size = size)

@@app.route('/start-finish-prediction/<size>')
def show_map(size):
    return render_template('map2.html', size = size)

@app.route('/trips', methods=['GET'])
@cross_origin()
def get_all_trips():
    trips = mongo.db['cleaned_trip_zones_' + str(request.args.get('size'))]
    output = []
    for trip in trips.find({ 'original_trip_id': '5999b6bf347aa80c7452265e' }):
        output.append(toJSON(trip))
        break
    return jsonify(output)

@app.route('/predict-start-finish', methods=['GET'])
@cross_origin()
def get_all_trips():
    trips = mongo.db['cleaned_trip_zones_' + str(request.args.get('size'))]
    output = []
    for trip in trips.find({ 'start_zone': {
            '$in': [
                '78|55',
                '78|54',
                '51|50',
                '74|56',
                '54|39',
                '50|50',
                '64|58',
                '28|60',
                '68|69',
                '27|80'
            ]
        }}):
        output.append(toJSON(trip))
        break
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug = True)