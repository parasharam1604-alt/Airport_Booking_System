# Airport Management System (Flask + MySQL)

## Quick local (without Docker)
1. Create virtualenv and install:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Create a MySQL database & user or use the docker-compose below.
3. Copy .env.example to .env and update DATABASE_URL etc.
4. Initialize DB:
   export FLASK_APP=app.py
   flask db init
   flask db migrate -m "init"
   flask db upgrade
5. Run:
   flask run --host=0.0.0.0 --port=5000

## Quick using Docker (recommended)
1. Copy .env.example to .env and edit if you want.
2. docker-compose up --build
3. Visit http://localhost:5000

Default admin: admin@example.com / admin123

Notes:
- For production, use managed MySQL (RDS/Cloud SQL) and set DATABASE_URL to your DB.
- Consider moving from SQLite/ephemeral storage to persistent managed DB for production.