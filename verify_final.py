# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    db.create_all()
    
    # 获取所有成果记录
    achievements = Achievement.query.order_by(Achievement.date.desc()).all()
    
    print("=" * 80)
    print("最终验证 - 数据库中的成果记录")
    print("=" * 80)
    print(f"数据库中共有 {len(achievements)} 条成果记录\n")
    
    # 检查是否还存在要删除的记录
    titles_to_check = [
        "全国大学生程序设计竞赛金奖",  # 中国计算机学会
        "技术博客达人"  # 掘金社区
    ]
    
    found_any = False
    for achievement in achievements:
        if achievement.title in titles_to_check:
            found_any = True
            print(f"⚠️  发现应删除的记录:")
            print(f"   ID: {achievement.id}")
            print(f"   标题: {achievement.title}")
            print(f"   机构: {achievement.organization}")
    
    if not found_any:
        print("✓ 未发现应删除的记录（中国计算机学会、掘金社区已成功删除）")
    
    print("\n" + "=" * 80)
    print("当前数据库中的所有成果记录：")
    print("=" * 80)
    
    for i, achievement in enumerate(achievements, 1):
        print(f"\n【记录 {i}】")
        print(f"ID: {achievement.id}")
        print(f"标题: {achievement.title}")
        print(f"日期: {achievement.date}")
        if achievement.organization:
            print(f"机构: {achievement.organization}")
        
    print("\n" + "=" * 80)
    print("验证完成！")
    print("=" * 80)
