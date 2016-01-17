from pay import app, db


class UserDB(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)


class UserToVehicleDB(db.Model):



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
    rate = db.Column(db.Float, nullable=False)
