# -*- coding: utf-8 -*-
from sqlalchemy import text
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    print("=" * 80)
    print("检查并更新数据库结构")
    print("=" * 80)
    
    # 首先获取原始连接，直接执行SQL添加列
    # 这需要在db.create_all()之前执行，或者使用原始连接
    with db.engine.connect() as conn:
        # 检查表是否存在
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='achievement'"))
        table_exists = result.fetchone() is not None
        
        if table_exists:
            print("✓ achievement 表已存在")
            
            # 检查列是否存在
            result = conn.execute(text("PRAGMA table_info(achievement)"))
            columns = [row[1] for row in result.fetchall()]
            print(f"  现有列: {columns}")
            
            if 'github_url' not in columns:
                print("\n正在添加 github_url 列...")
                try:
                    conn.execute(text("ALTER TABLE achievement ADD COLUMN github_url VARCHAR(200)"))
                    conn.commit()
                    print("✓ 已成功添加 github_url 列")
                except Exception as e:
                    print(f"✗ 添加列失败: {e}")
            else:
                print("✓ github_url 列已存在")
        else:
            print("⚠️ achievement 表不存在，将通过 db.create_all() 创建")
            conn.commit()
    
    # 现在创建所有表（如果不存在）
    db.create_all()
    
    print("\n" + "=" * 80)
    print("更新指定成果的GitHub链接")
    print("=" * 80)
    
    # 定义要更新的记录
    updates = [
        {
            "title": "Flask用户注册系统节省6.25人日/月",
            "github_url": "https://github.com/xiaoyu-li-china/userRegister"
        },
        {
            "title": "MyBaby项目获上海电视台报道",
            "github_url": "https://github.com/xiaoyu-li-china/ocean_mybaby"
        }
    ]
    
    for update_data in updates:
        # 查找记录
        achievement = Achievement.query.filter_by(title=update_data["title"]).first()
        
        if achievement:
            print(f"\n找到记录: {achievement.title}")
            print(f"  原GitHub链接: {achievement.github_url or '空'}")
            
            # 更新GitHub链接
            achievement.github_url = update_data["github_url"]
            print(f"  新GitHub链接: {achievement.github_url}")
            print("✓ 已更新")
        else:
            print(f"\n⚠️  未找到记录: {update_data['title']}")
    
    # 提交更改
    db.session.commit()
    
    print("\n" + "=" * 80)
    print("验证更新结果")
    print("=" * 80)
    
    # 验证更新
    achievements = Achievement.query.order_by(Achievement.date.desc()).all()
    
    for achievement in achievements:
        if achievement.github_url:
            print(f"\n✓ {achievement.title}")
            print(f"  GitHub链接: {achievement.github_url}")
    
    print("\n" + "=" * 80)
    print("更新完成！")
    print("=" * 80)
