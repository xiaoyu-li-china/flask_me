# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    db.create_all()
    
    # 获取所有成果记录
    achievements = Achievement.query.order_by(Achievement.date.desc()).all()
    
    print("=" * 80)
    print(f"数据库中共有 {len(achievements)} 条成果记录")
    print("=" * 80)
    
    for i, achievement in enumerate(achievements, 1):
        print(f"\n【记录 {i}】")
        print(f"ID: {achievement.id}")
        print(f"标题: {achievement.title}")
        print(f"日期: {achievement.date}")
        if achievement.organization:
            print(f"机构: {achievement.organization}")
        print(f"描述: {achievement.description[:100]}...")
        
    print("\n" + "=" * 80)
    print("检查完成！")
    print("=" * 80)
