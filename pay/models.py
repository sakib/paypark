from pay import app, db


class UserDB(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    last_claimed = db.Column(db.DateTime, nullable=True, default=0)
    current_parking = db.Column(db.Integer, nullable=True, default=0) # ForeignKey: parking.id
    balance = db.Column(db.Float(precision=2), nullable=False, default=0)


class UserToVehicleDB(db.Model):
    __tablename__ = 'users_to_vehicles'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)


class VehicleDB(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    license = db.Column(db.String(20), nullable=False)


class CardDB(db.Model):
    __tablename__ = 'cards'
    number = db.Column(db.BigInteger, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cvv = db.Column(db.Integer, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(30), nullable=False)


class ParkingDB(db.Model):
    __tablename__ = 'parking'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)
    num_spots = db.Column(db.Integer, nullable=False)
    street = db.Column(db.String(128), nullable=False)
    rate = db.Column(db.Float(precision=2), nullable=False)
    current_vehicle = db.Column(db.Integer, nullable=True, default=0) # ForeignKey: vehicle.id


class PaymentDB(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    card_number = db.Column(db.Integer, db.ForeignKey('cards.number'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
