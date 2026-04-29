# -*- coding: utf-8 -*-
from datetime import date
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    db.create_all()
    
    print("=" * 80)
    print("恢复 MyBaby项目获上海电视台报道 记录")
    print("=" * 80)
    
    # 恢复 ID: 4 的记录
    mybaby_achievement = Achievement(
        id=4,
        title='MyBaby项目获上海电视台报道',
        description='主导试管婴儿医疗区块链项目测试，涉及高度敏感的健康数据管理，对数据安全与隐私保护有极致要求，项目成功上线并获"上海电视台"报道。',
        date=date(2022, 6, 1),
        organization='OceanEx交易所',
        image_filename='achievement_mybaby.jpg'
    )
    
    db.session.add(mybaby_achievement)
    print("✓ 已恢复 MyBaby项目获上海电视台报道 记录")
    
    print("\n" + "=" * 80)
    print("删除 掘金社区 - 技术博客达人 记录")
    print("=" * 80)
    
    # 删除 ID: 3 的记录（掘金社区 - 技术博客达人）
    juejin_achievement = db.session.get(Achievement, 3)
    if juejin_achievement:
        print(f"ID: {juejin_achievement.id}")
        print(f"标题: {juejin_achievement.title}")
        print(f"机构: {juejin_achievement.organization}")
        print(f"日期: {juejin_achievement.date}")
        
        db.session.delete(juejin_achievement)
        print("✓ 已删除 掘金社区 - 技术博客达人 记录")
    else:
        print("未找到 掘金社区 - 技术博客达人 记录")
    
    # 提交更改
    db.session.commit()
    
    print("\n" + "=" * 80)
    print("操作完成！")
    
    # 验证结果
    remaining = Achievement.query.count()
    print(f"数据库中剩余 {remaining} 条成果记录")
    print("=" * 80)
