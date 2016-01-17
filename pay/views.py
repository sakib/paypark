#!venv/bin/python
from flask import request, jsonify, url_for, abort, g
from pay import app, db, auth
from models import ParkingDB


@app.route('/')
@app.route('/index')
def index():
    return "Hello World!"


@app.route('/lel', methods=['GET','POST'])
def events():
    if request.method == 'GET':
        parking = ParkingDB.query.all()
        json_parking = map(get_parking_json, parking)
        return jsonify(parking=json_parking)
        #return render_template("park.html")


def get_parking_json(parking):
    return {'id': parking.id,
            'latitude': parking.lat,
            'longitude': parking.long,
            'num_spots': parking.num_spots,
            'street': parking.street,
            'rate': parking.rate }

