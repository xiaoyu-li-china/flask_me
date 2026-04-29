#!/bin/bash
set -e

echo "Initializing database..."
python -c "
from run import app
from app import db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"

echo "Starting application..."
exec gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 --threads 4 wsgi:app
