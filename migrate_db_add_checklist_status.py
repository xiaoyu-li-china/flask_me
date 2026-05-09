# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import ChecklistItem
from sqlalchemy import text

app = create_app()

with app.app_context():
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('checklist_item')]
    
    print(f"migrate_db_add_checklist_status: 当前 checklist_item 表字段: {columns}", flush=True)
    
    with db.engine.begin() as conn:
        if 'status' not in columns:
            try:
                conn.execute(text("ALTER TABLE checklist_item ADD COLUMN status VARCHAR(20) DEFAULT 'not_started'"))
                print("migrate_db_add_checklist_status: 已添加 status 字段", flush=True)
            except Exception as e:
                print(f"migrate_db_add_checklist_status: 添加 status 字段失败: {e}", flush=True)
        else:
            print("migrate_db_add_checklist_status: status 字段已存在", flush=True)
        
        if 'code' in columns:
            try:
                conn.execute(text("ALTER TABLE checklist_item DROP COLUMN code"))
                print("migrate_db_add_checklist_status: 已删除 code 字段", flush=True)
            except Exception as e:
                print(f"migrate_db_add_checklist_status: 删除 code 字段失败: {e}", flush=True)
        
        if 'keywords' in columns:
            try:
                conn.execute(text("ALTER TABLE checklist_item DROP COLUMN keywords"))
                print("migrate_db_add_checklist_status: 已删除 keywords 字段", flush=True)
            except Exception as e:
                print(f"migrate_db_add_checklist_status: 删除 keywords 字段失败: {e}", flush=True)
        
        if 'url' in columns:
            try:
                conn.execute(text("ALTER TABLE checklist_item DROP COLUMN url"))
                print("migrate_db_add_checklist_status: 已删除 url 字段", flush=True)
            except Exception as e:
                print(f"migrate_db_add_checklist_status: 删除 url 字段失败: {e}", flush=True)
    
    db.session.commit()
    print("migrate_db_add_checklist_status: 完成", flush=True)
