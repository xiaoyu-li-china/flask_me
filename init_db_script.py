import os
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///site.db')

from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print('Database initialized successfully')
