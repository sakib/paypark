#!venv/bin/python
from flask import request, jsonify, url_for, render_template
from pay import app, db, auth
from models import *
from datetime import datetime


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


@app.route('/users/<user_id>', methods=['GET'])
def user(user_id):
    if request.method == 'GET':
        user = UserDB.query.filter_by(id=user_id).first()
        json_user = get_user_json(user)
        return jsonify(user=json_user)
    return "Fuck you"


@app.route('/cards', methods=['GET','POST'])
def cards():
    if request.method == 'GET':
        cards = CardDB.query.all()
        json_cards = map(get_card_json, cards)
        return jsonify(cards=json_cards)
    if request.method == 'POST':
        number = request.json.get('number')
        user_id = request.json.get('user_id')
        expiration_date = request.json.get('expiration_date')
        name = request.json.get('name')
        cvv = request.json.get('cvv')
        card = CardDB(number=number, user_id=user_id, name=name,
                cvv=cvv, expiration_date=expiration_date)
        db.session.add(card)
        db.session.commit()
        return "Success"
    return "Fuck you"


@app.route('/vehicles', methods=['GET','POST'])
def vehicles():
    if request.method == 'GET':
        vehicles = VehicleDB.query.all()
        json_vehicles = map(get_vehicle_json, vehicles)
        return jsonify(vehicles=json_vehicles)
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

        db.session.commit()
        entry = UserToVehicleDB(user_id=user_id,
                                vehicle_id=vehicle.id)
        db.session.add(entry)
        db.session.commit()
        return "Success"
    return "Fuck you"


@app.route('/claim', methods=['POST'])
def claim():
    if request.method == 'POST':
        user_id = request.json.get('user_id')
        user = UserDB.query.filter_by(id=user_id).first()
        parking_id = request.json.get('parking_id')
        parking = ParkingDB.query.filter_by(id=parking_id).first()
        if parking is not None and user is not None:
            user.last_claimed = datetime.now()
            parking.num_spots -= 1
            db.session.commit()
            return "Success"
        else:
            return "Fuck you"
    return "Fuck you"


@app.route('/relinquish', methods=['POST'])
def relinquish():
    if request.method == 'POST':
        user_id = request.json.get('user_id')
        user = UserDB.query.filter_by(id=user_id).first()
        parking_id = request.json.get('parking_id')
        parking = ParkingDB.query.filter_by(id=parking_id).first()
        if parking is not None and user is not None:
            end_time = datetime.now()
            start_time = user.last_claimed
            delta = end_time - start_time
            charge = delta * parking.rate
            user.balance += charge
            parking.num_spots += 1
            db.session.commit()
            return "Success"
        else:
            return "Fuck you"
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
        vehicles.append(VehicleDB.query.filter_by(id=entry.vehicle_id).first())
    vehicle_json = map(get_vehicle_json, vehicles)

    cards = CardDB.query.filter_by(user_id=user.id).all()
    cards_json = map(get_card_json, cards)

    return {'id': user.id,
            'last_claimed': user.last_claimed,
            'balance': user.balance,
            'vehicles': vehicle_json,
            'cards': cards_json }


def get_vehicle_json(vehicle):
    return {'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'license': vehicle.license }

