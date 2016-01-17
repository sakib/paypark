from pay import app, db


class ParkingDB(db.Model):
    __tablename__ = 'parking'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)
    num_spots = db.Column(db.Integer, nullable=False)
    street = db.Column(db.String(128), nullable=False)
    rate = db.Column(db.Float, nullable=False)
