# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    print("=" * 80)
    print("检查 Flask用户注册系统 记录的GitHub链接")
    print("=" * 80)
    
    # 查找Flask用户注册系统记录
    achievement = Achievement.query.filter_by(title="Flask用户注册系统节省6.25人日/月").first()
    
    if achievement:
        print(f"\n找到记录:")
        print(f"  ID: {achievement.id}")
        print(f"  标题: {achievement.title}")
        print(f"  GitHub链接: '{achievement.github_url}'")
        print(f"  GitHub链接类型: {type(achievement.github_url)}")
        print(f"  是否为None: {achievement.github_url is None}")
        print(f"  是否为空字符串: {achievement.github_url == ''}")
        print(f"  布尔值: {bool(achievement.github_url)}")
        
        # 检查MyBaby记录作为对比
        mybaby = Achievement.query.filter_by(title="MyBaby项目获上海电视台报道").first()
        if mybaby:
            print(f"\n\n对比记录 (MyBaby):")
            print(f"  ID: {mybaby.id}")
            print(f"  标题: {mybaby.title}")
            print(f"  GitHub链接: '{mybaby.github_url}'")
            print(f"  布尔值: {bool(mybaby.github_url)}")
    else:
        print("\n未找到记录!")
        
        # 列出所有记录
        print("\n所有成果记录:")
        achievements = Achievement.query.all()
        for a in achievements:
            print(f"  - {a.title}: '{a.github_url}'")
    
    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)
