# -*- coding: utf-8 -*-
from sqlalchemy import text
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    print("=" * 80)
    print("最终验证 - 成果展示页面GitHub链接更新")
    print("=" * 80)
    
    # 检查数据库结构
    print("\n【1. 检查数据库结构】")
    with db.engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(achievement)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"   achievement 表列: {columns}")
        
        if 'github_url' in columns:
            print("   ✓ github_url 列已存在")
        else:
            print("   ✗ github_url 列不存在")
    
    # 检查所有成果记录
    print("\n【2. 检查所有成果记录】")
    achievements = Achievement.query.order_by(Achievement.date.desc()).all()
    
    print(f"   数据库中共有 {len(achievements)} 条成果记录\n")
    
    for i, achievement in enumerate(achievements, 1):
        print(f"   【记录 {i}】")
        print(f"   ID: {achievement.id}")
        print(f"   标题: {achievement.title}")
        print(f"   日期: {achievement.date}")
        print(f"   机构: {achievement.organization or '无'}")
        print(f"   GitHub链接: {achievement.github_url or '无'}")
        
        if achievement.github_url:
            print("   ✓ 有GitHub链接")
        print()
    
    # 检查特定记录
    print("【3. 验证指定记录的GitHub链接】")
    
    # 定义预期的链接
    expected_links = {
        "Flask用户注册系统节省6.25人日/月": "https://github.com/xiaoyu-li-china/userRegister",
        "MyBaby项目获上海电视台报道": "https://github.com/xiaoyu-li-china/ocean_mybaby"
    }
    
    all_correct = True
    for title, expected_url in expected_links.items():
        achievement = Achievement.query.filter_by(title=title).first()
        
        if achievement:
            if achievement.github_url == expected_url:
                print(f"   ✓ {title}")
                print(f"     GitHub链接: {achievement.github_url}")
            else:
                all_correct = False
                print(f"   ✗ {title}")
                print(f"     预期: {expected_url}")
                print(f"     实际: {achievement.github_url}")
        else:
            all_correct = False
            print(f"   ✗ 未找到记录: {title}")
    
    print("\n" + "=" * 80)
    if all_correct:
        print("✓ 所有验证通过！")
    else:
        print("✗ 存在验证失败！")
    print("=" * 80)
    
    # 检查模板文件
    print("\n【4. 检查模板文件】")
    import os
    template_path = os.path.join(os.path.dirname(__file__), 'app', 'templates', 'achievements.html')
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'github_url' in content:
            print("   ✓ 模板中包含 github_url 逻辑")
        else:
            print("   ✗ 模板中未找到 github_url 逻辑")
        
        if '查看Git详情' in content:
            print("   ✓ 模板中包含 '查看Git详情' 按钮")
        else:
            print("   ✗ 模板中未找到 '查看Git详情' 按钮")
    else:
        print(f"   ✗ 模板文件不存在: {template_path}")
    
    print("\n" + "=" * 80)
    print("验证完成！")
    print("=" * 80)
