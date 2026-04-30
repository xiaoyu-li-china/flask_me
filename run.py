from app import create_app, db
from app.models import User, Project, Certificate, Achievement

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Project': Project,
        'Certificate': Certificate,
        'Achievement': Achievement
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)

        normal_user = User.query.filter_by(username='user').first()
        if not normal_user:
            normal_user = User(username='user', is_admin=False)
            normal_user.set_password('user123')
            db.session.add(normal_user)

        db.session.commit()
    app.run(debug=True, host='0.0.0.0', port=5002)
