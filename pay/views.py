#!venv/bin/python
from flask import request, jsonify, url_for, render_template
from pay import app, db, auth
from models import *


@app.route('/')
def index():
    return "Fuck you!"


@app.route('/users', methods=['GET','POST'])
def users():
    if request.method == 'GET':
        users = UserDB.query.all()
        json_users = map(get_user_json, users)
        return jsonify(users=json_users)
    if request.method == 'POST':
        user = UserDB()
        db.session.add(user)
        db.session.commit()
        return "Success"
    return "Fuck you"


@app.route('/vehicles', methods=['POST'])
def vehicles():
    if request.method == 'POST':
        user_id = request.json.get('user_id')

        user = UserDB.query.filter_by(id=user_id).first()
        if user is None:
            return "Fuck you"

        make = request.json.get('make')
        model = request.json.get('model')
        year = request.json.get('year')
        license = request.json.get('license')

        vehicle = VehicleDB(make=make, model=model,
                            year=year, license=license)
        db.session.add(vehicle)

        entry = UserToVehicleDB(user_id=user_id,
                                vehicle_id=vehicle.id)
        db.session.add(entry)
        db.session.commit()
        return "Success"
    return "Fuck you"


@app.route('/claim', methods=['POST'])
def claim():
    if request.method == 'POST':
        parking_id = request.json.get('parking_id')
        parking = ParkingDB.query.filter_by(id=parking_id).first()
        if parking is not None:
            parking.num_spots -= 1
            db.session.commit()
            return "Success"
        else:
            return "Failure"
    return "Fuck you"


@app.route('/relinquish', methods=['POST'])
def relinquish():
    if request.method == 'POST':
        parking_id = request.json.get('parking_id')
        parking = ParkingDB.query.filter_by(id=parking_id).first()
        if parking is not None:
            parking.num_spots += 1
            db.session.commit()
            return "Success"
        else:
            return "Failure"
    return "Fuck you"


@app.route('/parking', methods=['GET'])
def parking():
    if request.method == 'GET':
        parking = ParkingDB.query.all()
        json_parking = map(get_parking_json, parking)
        return jsonify(parking=json_parking)


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("park.html")
    if request.method == 'POST':
        lat = request.form['latitude']
        long = request.form['longitude']
        num_spots = request.form['num_spots']
        street = request.form['street']
        rate = request.form['rate']

        parking = ParkingDB(lat=lat, long=long,
            num_spots=num_spots, street=street, rate=rate)

        db.session.add(parking)
        db.session.commit()

        return render_template("park.html",
                    lat = lat, long = long,
                    num_spots = num_spots,
                    street = street, rate = rate)
    return "Fuck you"


def get_parking_json(parking):
    return {'id': parking.id,
            'latitude': parking.lat,
            'longitude': parking.long,
            'num_spots': parking.num_spots,
            'street': parking.street,
            'rate': parking.rate }


def get_user_json(user):

    vehicle_entries = UserToVehicleDB.query.filter_by(user_id=user.id).all()

    vehicles = []

    for entry in vehicle_entries:
        vehicles.add(VehicleDB.query.filter_by(id=entry.vehicle_id).all())

    vehicle_json = map(get_vehicle_json, vehicles)

    return {'id': user.id,
            'last_claimed': user.last_claimed,
            'balance': user.balance,
            'vehicles': jsonify(vehicles=vehicle_json) }


def get_vehicle_json(vehicle):
    return {'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'license': vehicle.license }

