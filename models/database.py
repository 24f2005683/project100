from flask_sqlalchemy import SQLAlchemy
import base64
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = base64.b64encode(password.encode()).decode()
    
    def check_password(self, password):
        return self.password_hash == base64.b64encode(password.encode()).decode()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = base64.b64encode(password.encode()).decode()
    
    def check_password(self, password):
        return self.password_hash == base64.b64encode(password.encode()).decode()

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)  # A=Available, O=Occupied
    
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True, cascade='all, delete-orphan')

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Active')  # Active, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)