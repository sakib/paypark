#!venv/bin/python
from flask import request, jsonify, url_for, render_template
from pay import app, db, auth
from models import *
from datetime import datetime


@app.route('/')
def index():
    return "Fuck you!"


# Get all users or create new user
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


# Get information for one user, his cards, vehicles and parking status
@app.route('/users/<user_id>', methods=['GET'])
def user(user_id):
    if request.method == 'GET':
        user = UserDB.query.filter_by(id=user_id).first()
        json_user = get_user_json(user)
        return jsonify(user=json_user)
    return "Fuck you"


# Get all cards or submit new card
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

        card = CardDB.query.filter_by(number=number).first()

        if card is None:
            card = CardDB(number=number, user_id=user_id, name=name,
                    cvv=cvv, expiration_date=expiration_date)
            db.session.add(card)
        else:
            if user_id is not None:
                card.user_id = user_id
            if expiration_date is not None:
                card.expiration_date = expiration_date
            if name is not None:
                card.name = name
            if cvv is not None:
                card.cvv = cvv

        db.session.commit()
        return "Success"
    return "Fuck you"


# Get all payments or submit new payment
@app.route('/payments', methods=['GET','POST'])
def payments():
    if request.method == 'GET':
        payments = PaymentDB.query.all()
        payments_json = map(get_payment_json, payments)
        return jsonify(payments=payments_json)
    if request.method == 'POST':
        amount = request.json.get('amount')
        card_number = request.json.get('card_number')
        user_id = request.json.get('user_id')
        time = datetime.now()

        card = CardDB.query.filter_by(number=card_number).first()
        user = UserDB.query.filter_by(id=user_id).first()

        if user is None or card is None:
            return "Fuck you"

        user.balance += float(amount)

        payment = PaymentDB(amount=amount, time=time,
                card_number=card_number, user_id=user_id)
        db.session.add(payment)
        db.session.commit()
        return "Success"
    return "Fuck you"


# Get payment history for a user
@app.route('/payments/<user_id>', methods=['GET'])
def payment(user_id):
    if request.method == 'GET':
        payments = PaymentDB.query.filter_by(user_id=user_id).all()
        payments_json = map(get_payment_json, payments)
        return jsonify(payments=payments_json)
    return "Fuck you"


# Get all vehicles or add new vehicles under existing users or edit existing vehicles
@app.route('/vehicles', methods=['GET','POST'])
def vehicles():
    if request.method == 'GET':
        vehicles = VehicleDB.query.all()
        json_vehicles = map(get_vehicle_json, vehicles)
        return jsonify(vehicles=json_vehicles)
    if request.method == 'POST':
        user_id = request.json.get('user_id')
        vehicle_id = request.json.get('vehicle_id')

        user = UserDB.query.filter_by(id=user_id).first()
        if user is None:
            return "Fuck you"

        make = request.json.get('make')
        model = request.json.get('model')
        year = request.json.get('year')
        license = request.json.get('license')

        if vehicle_id == -1: # Create new
            vehicle = VehicleDB(make=make, model=model,
                            year=year, license=license)
            db.session.add(vehicle)
            db.session.commit()
            entry = UserToVehicleDB(user_id=user_id,
                                vehicle_id=vehicle.id)
            db.session.add(entry)
        else: # Find old
            vehicle = VehicleDB.query.filter_by(id=vehicle_id).first()
            if vehicle is None:
                return "Fuck you"
            if make is not None:
                vehicle.make = make
            if model is not None:
                vehicle.model = model
            if year is not None:
                vehicle.year = year
            if license is not None:
                vehicle.license = license

        db.session.commit()
        return "Success"
    return "Fuck you"


# Claim a parking spot.
@app.route('/claim', methods=['POST'])
def claim():
    if request.method == 'POST':
        user_id = request.json.get('user_id')
        user = UserDB.query.filter_by(id=user_id).first()
        parking_id = request.json.get('parking_id')
        parking = ParkingDB.query.filter_by(id=parking_id).first()
        vehicle_id = request.json.get('vehicle_id')
        vehicle = VehicleDB.query.filter_by(id=vehicle_id).first()
        if parking is not None and user is not None and vehicle is not None:
            user.last_claimed = datetime.now()
            user.current_parking = parking.id
            parking.current_vehicle = vehicle.id
            parking.num_spots -= 1
            parking_history_entry = ParkingHistoryDB(parking_id=parking_id,
                user_id=user_id, start_time=datetime.now(), active=1)
            db.session.add(parking_history_entry)
            db.session.commit()
            return "Success"
        else:
            return "Fuck you"
    return "Fuck you"


# Give up a parking spot.
@app.route('/relinquish', methods=['POST'])
def relinquish():
    if request.method == 'POST':
        user_id = request.json.get('user_id')
        user = UserDB.query.filter_by(id=user_id).first()
        parking_id = request.json.get('parking_id')
        parking = ParkingDB.query.filter_by(id=parking_id).first()
        vehicle_id = request.json.get('vehicle_id')
        vehicle = VehicleDB.query.filter_by(id=vehicle_id).first()
        parking_history_entry = ParkingHistoryDB.query.filter_by(user_id=user_id,
                parking_id=parking_id, active=1).first()
        if parking is not None and user is not None and parking_history_entry is not None:
            end_time = datetime.now()
            start_time = user.last_claimed
            delta = end_time - start_time
            charge = delta.total_seconds()/3600 * parking.rate
            user.balance -= charge
            user.current_parking = 0
            parking.current_vehicle = 0
            parking.num_spots += 1
            parking_history_entry.active = 0
            parking_history_entry.end_time = datetime.now()
            db.session.commit()
            card = CardDB.query.filter_by(user_id=user_id).first()
            payment = PaymentDB(amount=-1*charge, time=parking_history_entry.end_time,
                card_number=card.number, user_id=user_id, parking_history_id=parking_history_entry.id)
            db.session.add(payment)
            db.session.commit()
            return "Success"
        else:
            return "Fuck you"
    return "Fuck you"


# Get all parking information
@app.route('/parking', methods=['GET'])
def parking():
    if request.method == 'GET':
        parking = ParkingDB.query.all()
        json_parking = map(get_parking_json, parking)
        return jsonify(parking=json_parking)


# Add new or edit existing parking spaces.
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

        parking_exists = ParkingDB.query.filter_by(lat=lat,
                            long=long, street=street).first()
        if parking_exists is not None:
            parking_exists.num_spots = num_spots
            parking_exists.rate = rate
        else:
            db.session.add(parking)

        db.session.commit()

        return render_template("park.html",
                    lat = lat, long = long,
                    num_spots = num_spots,
                    street = street, rate = rate)
    return "Fuck you"


def get_parking_json(parking):
    vehicle = VehicleDB.query.filter_by(id=parking.current_vehicle).first()
    if vehicle is None:
        return {'id': parking.id,
            'latitude': parking.lat,
            'longitude': parking.long,
            'num_spots': parking.num_spots,
            'street': parking.street,
            'rate': str('{:20,.2f}'.format(parking.rate)) }
    else:
        return {'id': parking.id,
            'latitude': parking.lat,
            'longitude': parking.long,
            'num_spots': parking.num_spots,
            'street': parking.street,
            'rate': str('{:20,.2f}'.format(parking.rate)),
            'current_vehicle': get_vehicle_json(vehicle) }


def get_user_json(user):
    vehicle_entries = UserToVehicleDB.query.filter_by(user_id=user.id).all()
    vehicles = []
    for entry in vehicle_entries:
        vehicles.append(VehicleDB.query.filter_by(id=entry.vehicle_id).first())
    vehicle_json = map(get_vehicle_json, vehicles)

    cards = CardDB.query.filter_by(user_id=user.id).all()
    cards_json = map(get_card_json, cards)

    parking = ParkingDB.query.filter_by(id=user.current_parking).first()
    if parking is None:
        return {'id': user.id,
                'last_claimed': str(user.last_claimed),
                'balance': str('{:20,.2f}'.format(user.balance)),
                'vehicles': vehicle_json,
                'cards': cards_json }
    else:
        parking_json = get_parking_json(parking)
        return {'id': user.id,
                'last_claimed': str(user.last_claimed),
                'current_parking': parking_json,
                'balance': str('{:20,.2f}'.format(user.balance)),
                'vehicles': vehicle_json,
                'cards': cards_json }


def get_vehicle_json(vehicle):
    return {'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'license': vehicle.license }


def get_card_json(card):
    return {'number': card.number,
            'user_id': card.user_id,
            'cvv': card.cvv,
            'name': card.name,
            'expiration_date': str(card.expiration_date) }


def get_payment_json(payment):
    card = CardDB.query.filter_by(number=payment.card_number).first()
    card_json = get_card_json(card)

    ph = ParkingHistoryDB.query.filter_by(id=payment.parking_history_id).first()

    if ph is None:
        return {'id': payment.id,
            'amount': str('{:20,.2f}'.format(payment.amount)),
            'time': str(payment.time),
            'user_id': payment.user_id,
            'card': card_json }
    else:
        return {'id': payment.id,
            'amount': str('{:20,.2f}'.format(payment.amount)),
            'time': str(payment.time),
            'user_id': payment.user_id,
            'card': card_json,
            'parking_history': get_parking_history_json(ph) }


def get_parking_history_json(ph):
    parking = ParkingDB.query.filter_by(id=ph.parking_id).first()
    parking_json = get_parking_json(parking)
    return {'id': ph.id,
            'active': ph.active,
            'start_time': ph.start_time,
            'end_time': ph.end_time,
            'user_id': ph.user_id,
            'parking': parking_json }
