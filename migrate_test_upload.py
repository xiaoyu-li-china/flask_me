# -*- coding: utf-8 -*-
import sqlite3
import os
from app import create_app, db
from app.models import User

app = create_app()

def migrate_database():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'site.db')
    
    if not os.path.exists(db_path):
        print("数据库不存在，将创建新数据库")
        with app.app_context():
            db.create_all()
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin')
                admin.set_password('admin123')
                admin.is_admin = True
                db.session.add(admin)
                db.session.commit()
                print("管理员用户已创建")
        return
    
    print("正在迁移现有数据库...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        print("已添加 is_admin 列到 user 表")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("is_admin 列已存在")
        else:
            raise e
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_upload (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name VARCHAR(200) NOT NULL,
                file_type VARCHAR(20),
                file_path VARCHAR(500),
                upload_time DATETIME,
                uploader_id INTEGER NOT NULL,
                title VARCHAR(200),
                description TEXT,
                module VARCHAR(50),
                category VARCHAR(50),
                parsed_data TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT,
                FOREIGN KEY (uploader_id) REFERENCES user (id)
            )
        """)
        print("已创建 test_upload 表")
    except sqlite3.OperationalError as e:
        print(f"创建 test_upload 表时出错: {e}")
    
    cursor.execute("UPDATE user SET is_admin = 1 WHERE username = 'admin'")
    print("已将 admin 用户设置为管理员")
    
    conn.commit()
    conn.close()
    
    print("数据库迁移完成！")

if __name__ == '__main__':
    migrate_database()
