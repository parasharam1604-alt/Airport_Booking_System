from app import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='user', nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Airport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(200), nullable=False)
    departures = db.relationship('Flight', backref='departure_airport', foreign_keys='Flight.departure_airport_id', lazy=True)
    arrivals = db.relationship('Flight', backref='arrival_airport', foreign_keys='Flight.arrival_airport_id', lazy=True)

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(50), nullable=False)
    departure_airport_id = db.Column(db.Integer, db.ForeignKey('airport.id'), nullable=False)
    arrival_airport_id = db.Column(db.Integer, db.ForeignKey('airport.id'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats_available = db.Column(db.Integer, default=100, nullable=False)
    bookings = db.relationship('Booking', backref='flight', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_name = db.Column(db.String(200), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
