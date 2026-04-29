import os
import sys

print('=== Starting database initialization ===')
print(f'Current directory: {os.getcwd()}')
print(f'Python version: {sys.version}')

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///site.db')
os.environ.setdefault('SECRET_KEY', 'flask-me-secret-key-2024')

from app import create_app, db
from app.models import User

print('Creating Flask app...')
app = create_app()

print('Initializing database...')
with app.app_context():
    try:
        db.create_all()
        print('Database tables created successfully')
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print('Creating default admin user...')
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Default admin user created successfully')
        else:
            print('Admin user already exists')
        
        # Verify user creation
        user = User.query.filter_by(username='admin').first()
        if user:
            print(f'User verification: username={user.username}, id={user.id}')
            print(f'Password check: {user.check_password("admin123")}')
        
        print('=== Database initialization completed ===')
        
    except Exception as e:
        print(f'Error during database initialization: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
