# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    print("=" * 80)
    print("检查所有成果记录的详细信息")
    print("=" * 80)
    
    # 按日期排序获取所有记录
    achievements = Achievement.query.order_by(Achievement.date.desc()).all()
    
    print(f"\n数据库中共有 {len(achievements)} 条成果记录\n")
    
    for i, achievement in enumerate(achievements, 1):
        print(f"{'='*60}")
        print(f"【记录 {i}】")
        print(f"{'='*60}")
        print(f"  ID: {achievement.id}")
        print(f"  标题: {achievement.title}")
        print(f"  日期: {achievement.date}")
        print(f"  机构: {achievement.organization or '无'}")
        print(f"  图片: {achievement.image_filename or '无'}")
        print(f"  GitHub链接: '{achievement.github_url}'")
        print(f"  GitHub链接布尔值: {bool(achievement.github_url)}")
        print(f"  描述长度: {len(achievement.description)} 字符")
        
        # 检查是否应该显示按钮
        if achievement.github_url:
            print(f"  ✅ 应该显示GitHub按钮")
        else:
            print(f"  ❌ 不应该显示GitHub按钮")
        
        print()
    
    print("=" * 80)
    print("检查完成")
    print("=" * 80)
