import os
from dotenv import load_dotenv

load_dotenv()

def _normalize_database_url(url):
    """Render/Heroku 等常提供 postgres://，SQLAlchemy 需要 postgresql://。"""
    if not url:
        return url
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'flask-me-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.environ.get('DATABASE_URL')) or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    DEBUG = False
    
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'xmind'}
