from pay import app, db


class UserDB(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    last_claimed = db.Column(db.Date, nullable=False, default=None)
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


class ParkingDB(db.Model):
    __tablename__ = 'parking'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)
    num_spots = db.Column(db.Integer, nullable=False)
    street = db.Column(db.String(128), nullable=False)
    rate = db.Column(db.Float(precision=2), nullable=False)
