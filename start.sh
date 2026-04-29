#!/bin/bash
set -e

echo "=== STARTING APPLICATION ==="
echo "Current directory: $(pwd)"
echo "PORT environment variable: ${PORT}"
echo "FLASK_ENV environment variable: ${FLASK_ENV}"

echo "Initializing database..."
python -c "
import os
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('SECRET_KEY', 'flask-me-secret-key-2024')
os.environ.setdefault('DATABASE_URL', 'sqlite:///site.db')
from run import app
from app import db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
echo "Database initialization completed"

echo "Starting application on port ${PORT:-10000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-10000} --timeout 120 --workers 1 --threads 4 wsgi:app
