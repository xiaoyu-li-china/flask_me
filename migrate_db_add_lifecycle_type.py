# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加lifecycle_type列和contract_type表

此脚本用于修复以下错误：
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: transaction_lifecycle_stage.lifecycle_type
"""

import os
from app import create_app, db
from app.models import TransactionLifecycleStage

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///site.db')
os.environ.setdefault('SECRET_KEY', 'flask-me-secret-key-2024')

app = create_app()

with app.app_context():
    print('=== 开始数据库迁移 ===')
    
    try:
        # 方法1: 使用ALTER TABLE添加列 (SQLite 3.35.0+ 支持)
        print('尝试添加 lifecycle_type 列到 transaction_lifecycle_stage 表...')
        from sqlalchemy import text
        
        # 检查表是否已有该列
        try:
            # 先尝试查询，如果列不存在会抛出异常
            existing = TransactionLifecycleStage.query.first()
            if existing:
                # 尝试访问 lifecycle_type 属性
                _ = existing.lifecycle_type
                print('lifecycle_type 列已存在')
        except Exception as e:
            if 'no such column' in str(e) or 'has no attribute' in str(e):
                print(f'检测到列不存在，尝试添加列: {e}')
                # 使用原始SQL添加列
                try:
                    # 对于SQLite，需要使用ALTER TABLE
                    db.session.execute(text("ALTER TABLE transaction_lifecycle_stage ADD COLUMN lifecycle_type VARCHAR(50) DEFAULT 'web3_chain'"))
                    db.session.commit()
                    print('成功添加 lifecycle_type 列')
                    
                    # 更新现有数据的默认值
                    db.session.execute(text("UPDATE transaction_lifecycle_stage SET lifecycle_type = 'web3_chain' WHERE lifecycle_type IS NULL"))
                    db.session.commit()
                    print('成功更新现有数据的 lifecycle_type 值')
                except Exception as alter_error:
                    print(f'ALTER TABLE 失败: {alter_error}')
                    print('尝试其他方法...')
            else:
                raise
    
    except Exception as e:
        print(f'迁移过程中出现错误: {e}')
        print('建议: 如果数据库包含重要数据，请先备份。')
        print('或者: 删除 site.db 文件并重新运行 init_db.py')
    
    # 尝试创建 ContractType 表
    try:
        print('尝试创建 contract_type 表...')
        # 检查模型是否可以访问
        from app.models import ContractType
        # 尝试创建表
        db.create_all()
        print('成功创建所有新表 (如果不存在)')
    except Exception as e:
        print(f'创建表时出错: {e}')
    
    print('=== 迁移完成 ===')
    print('')
    print('如果迁移失败，您可以尝试以下方法:')
    print('1. 备份重要数据后删除 site.db 文件')
    print('2. 运行 python init_db.py 重新初始化数据库')
