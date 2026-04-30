import os
os.environ.setdefault('FLASK_ENV', 'production')
# 数据库连接以环境变量 DATABASE_URL 与 config.Config 为准；勿在此写死 sqlite，以免与 init_db 使用的库不一致
os.environ.setdefault('SECRET_KEY', 'flask-me-secret-key-2024')

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin123')
        admin.is_admin = True
        db.session.add(admin)
        print('Default admin user created')

    user = User.query.filter_by(username='user').first()
    if not user:
        user = User(username='user')
        user.set_password('user123')
        user.is_admin = False
        db.session.add(user)
        print('Default user created')

    db.session.commit()

if __name__ == "__main__":
    app.run()
