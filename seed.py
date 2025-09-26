from app import db
from models import Airport, Flight
from datetime import datetime, timedelta

def seed():
    db.create_all()
    if Airport.query.count() == 0:
        a1 = Airport(code='DEL', name='Indira Gandhi International', city='Delhi')
        a2 = Airport(code='BOM', name='Chhatrapati Shivaji Maharaj', city='Mumbai')
        a3 = Airport(code='BLR', name='Kempegowda', city='Bengaluru')
        db.session.add_all([a1,a2,a3])
        db.session.commit()
        f1 = Flight(flight_number='AI101', departure_airport_id=a1.id, arrival_airport_id=a2.id,
                    departure_time=datetime.utcnow()+timedelta(days=1),
                    arrival_time=datetime.utcnow()+timedelta(days=1,hours=2),
                    price=5000.0, seats_available=100)
        f2 = Flight(flight_number='AI202', departure_airport_id=a2.id, arrival_airport_id=a3.id,
                    departure_time=datetime.utcnow()+timedelta(days=2),
                    arrival_time=datetime.utcnow()+timedelta(days=2,hours=2),
                    price=4500.0, seats_available=80)
        db.session.add_all([f1,f2])
        db.session.commit()
        print('Seeded airports and flights')

