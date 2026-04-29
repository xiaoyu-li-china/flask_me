# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    print("=" * 80)
    print("修复数据库中的 github_url 数据")
    print("=" * 80)
    
    # 获取所有记录
    achievements = Achievement.query.all()
    
    fixed_count = 0
    for achievement in achievements:
        # 检查是否是字符串 'None' 或空字符串
        if achievement.github_url == 'None' or achievement.github_url == '':
            print(f"\n修复记录: {achievement.title}")
            print(f"  原值: '{achievement.github_url}'")
            achievement.github_url = None
            print(f"  新值: {achievement.github_url}")
            fixed_count += 1
        elif achievement.github_url is not None:
            # 验证是否是有效的URL
            print(f"\n验证记录: {achievement.title}")
            print(f"  github_url: '{achievement.github_url}'")
            
            # 检查是否以 http 开头
            if not achievement.github_url.startswith('http'):
                print(f"  ⚠️  URL格式不正确，不以 http 开头")
    
    if fixed_count > 0:
        # 提交更改
        db.session.commit()
        print(f"\n✓ 已修复 {fixed_count} 条记录")
    else:
        print(f"\n✓ 没有需要修复的记录")
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
