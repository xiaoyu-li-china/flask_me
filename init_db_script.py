import os
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///site.db')

from run import app
from app import db

with app.app_context():
    db.create_all()
    print('Database initialized successfully')
