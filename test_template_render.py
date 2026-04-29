# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    print("=" * 80)
    print("测试模板渲染逻辑")
    print("=" * 80)
    
    # 获取所有记录
    achievements = Achievement.query.order_by(Achievement.date.desc()).all()
    
    print(f"\n共有 {len(achievements)} 条成果记录\n")
    
    # 模拟模板中的判断逻辑
    for i, achievement in enumerate(achievements, 1):
        print("=" * 60)
        print(f"【记录 {i}】{achievement.title}")
        print("=" * 60)
        
        # 打印原始值
        print(f"  github_url: '{achievement.github_url}'")
        print(f"  类型: {type(achievement.github_url)}")
        
        # 模拟模板中的判断逻辑
        # 原逻辑: if achievement.github_url
        original_condition = bool(achievement.github_url)
        print(f"\n  原判断逻辑 (if achievement.github_url): {original_condition}")
        
        # 新逻辑
        new_condition = (
            achievement.github_url is not None and 
            achievement.github_url != 'None' and 
            achievement.github_url != '' and 
            achievement.github_url.startswith('http')
        )
        print(f"  新判断逻辑: {new_condition}")
        
        # 检查是否应该显示按钮
        if new_condition:
            print(f"\n  应该显示GitHub按钮")
            print(f"     按钮链接: {achievement.github_url}")
        else:
            print(f"\n  不应该显示GitHub按钮")
        
        print()
    
    print("=" * 80)
    print("测试完成")
    print("=" * 80)
