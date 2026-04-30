# -*- coding: utf-8 -*-
import os
from app import create_app, db
from app.models import User

app = create_app()

def get_db_path():
    with app.app_context():
        uri = app.config['SQLALCHEMY_DATABASE_URI']
        if uri.startswith('sqlite:///'):
            return uri[10:]
    return None

def migrate_database():
    db_path = get_db_path()
    print(f"数据库路径: {db_path}")
    
    if db_path and os.path.exists(db_path):
        print(f"数据库文件存在，大小: {os.path.getsize(db_path)} bytes")
    else:
        print("数据库文件不存在，将创建新数据库")
    
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"数据库中的表: {tables}")
        
        if 'user' in tables:
            columns = [c['name'] for c in inspector.get_columns('user')]
            print(f"user表的列: {columns}")
            
            if 'is_admin' not in columns:
                print("正在添加 is_admin 列到 user 表...")
                try:
                    with db.engine.connect() as conn:
                        conn.execute(db.text("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                        conn.commit()
                    print("成功添加 is_admin 列")
                except Exception as e:
                    print(f"添加列时出错: {e}")
        
        if 'test_upload' not in tables:
            print("正在创建 test_upload 表...")
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("""
                        CREATE TABLE test_upload (
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
                    """))
                    conn.commit()
                print("成功创建 test_upload 表")
            except Exception as e:
                print(f"创建表时出错: {e}")
        
        admin = User.query.filter_by(username='admin').first()
        if admin:
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                print("已将 admin 用户设置为管理员")
            else:
                print("admin 用户已经是管理员")
        else:
            print("创建 admin 用户...")
            admin = User(username='admin')
            admin.set_password('admin123')
            admin.is_admin = True
            db.session.add(admin)
            db.session.commit()
            print("admin 用户创建成功")
        
        print("数据库迁移完成！")

if __name__ == '__main__':
    migrate_database()
