
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_this_secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:rootpassword@localhost/airportdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# import models AFTER db created
from models import User, Airport, Flight, Booking

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def ensure_default_admin():
    db.create_all()
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(email='admin@example.com', password_hash=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()
        print('Created default admin: admin@example.com / admin123')

@app.route('/')
def index():
    airports = Airport.query.all()
    return render_template('index.html', airports=airports)

# ---------- Auth ----------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        if not email or not password:
            flash('Missing fields', 'danger'); return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email exists', 'danger'); return redirect(url_for('register'))
        u = User(email=email, password_hash=generate_password_hash(password), role='user')
        db.session.add(u); db.session.commit()
        flash('Registered. Login now.', 'success'); return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        u = User.query.filter_by(email=email).first()
        if u and check_password_hash(u.password_hash, password):
            login_user(u)
            flash('Logged in', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index'))

# ---------- Airports (CRUD - admin) ----------
@app.route('/airports')
def airports():
    airports = Airport.query.all()
    return render_template('airports.html', airports=airports)

@app.route('/airports/new', methods=['GET','POST'])
@login_required
def new_airport():
    if current_user.role != 'admin':
        flash('Admins only', 'danger'); return redirect(url_for('airports'))
    if request.method == 'POST':
        code = request.form['code'].strip().upper()
        name = request.form['name'].strip()
        city = request.form['city'].strip()
        if not code or not name or not city:
            flash('Missing fields', 'danger'); return redirect(url_for('new_airport'))
        a = Airport(code=code, name=name, city=city)
        db.session.add(a); db.session.commit()
        flash('Airport created', 'success'); return redirect(url_for('airports'))
    return render_template('new_airport.html')

@app.route('/airports/<int:aid>/delete', methods=['POST'])
@login_required
def delete_airport(aid):
    if current_user.role != 'admin':
        flash('Admins only', 'danger'); return redirect(url_for('airports'))
    a = Airport.query.get_or_404(aid)
    db.session.delete(a); db.session.commit()
    flash('Deleted', 'success'); return redirect(url_for('airports'))

# ---------- Flights ----------
@app.route('/flights')
def flights():
    from_id = request.args.get('from')
    to_id = request.args.get('to')
    date = request.args.get('date')  # YYYY-MM-DD
    q = Flight.query
    if from_id: q = q.filter_by(departure_airport_id=from_id)
    if to_id: q = q.filter_by(arrival_airport_id=to_id)
    if date:
        try:
            d = datetime.strptime(date, '%Y-%m-%d')
            next_d = d.replace(day=d.day+1)
            q = q.filter(Flight.departure_time >= d, Flight.departure_time < next_d)
        except Exception:
            pass
    flights = q.all()
    airports = Airport.query.all()
    return render_template('flights.html', flights=flights, airports=airports)

@app.route('/flights/new', methods=['GET','POST'])
@login_required
def new_flight():
    if current_user.role != 'admin':
        flash('Admins only', 'danger'); return redirect(url_for('flights'))
    airports = Airport.query.all()
    if request.method == 'POST':
        fn = request.form['flight_number'].strip()
        dep = int(request.form['departure_airport'])
        arr = int(request.form['arrival_airport'])
        dep_time = request.form['departure_time']
        arr_time = request.form['arrival_time']
        price = float(request.form['price'])
        seats = int(request.form['seats'])
        f = Flight(
            flight_number=fn,
            departure_airport_id=dep,
            arrival_airport_id=arr,
            departure_time=datetime.fromisoformat(dep_time),
            arrival_time=datetime.fromisoformat(arr_time),
            price=price,
            seats_available=seats
        )
        db.session.add(f); db.session.commit()
        flash('Flight created', 'success'); return redirect(url_for('flights'))
    return render_template('new_flight.html', airports=airports)

@app.route('/flights/<int:fid>')
def flight_detail(fid):
    f = Flight.query.get_or_404(fid)
    return render_template('flight_detail.html', f=f)

@app.route('/flights/<int:fid>/delete', methods=['POST'])
@login_required
def delete_flight(fid):
    if current_user.role != 'admin':
        flash('Admins only', 'danger'); return redirect(url_for('flights'))
    f = Flight.query.get_or_404(fid)
    db.session.delete(f); db.session.commit()
    flash('Deleted flight', 'success'); return redirect(url_for('flights'))

# ---------- Bookings ----------
@app.route('/book/<int:flight_id>', methods=['GET','POST'])
@login_required
def book(flight_id):
    f = Flight.query.get_or_404(flight_id)
    if request.method == 'POST':
        name = request.form['passenger_name'].strip()
        seats = int(request.form['seats'])
        if seats <= 0:
            flash('Invalid seats', 'danger'); return redirect(url_for('book', flight_id=flight_id))
        if f.seats_available < seats:
            flash('Not enough seats', 'danger'); return redirect(url_for('book', flight_id=flight_id))
        b = Booking(passenger_name=name, seats=seats, user_id=current_user.id, flight_id=f.id)
        f.seats_available -= seats
        db.session.add(b); db.session.commit()
        flash('Booked', 'success'); return redirect(url_for('my_bookings'))
    return render_template('book.html', f=f)

@app.route('/my-bookings')
@login_required
def my_bookings():
    bs = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('bookings.html', bookings=bs)

