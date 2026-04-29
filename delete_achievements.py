# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import Achievement

app = create_app()

with app.app_context():
    db.create_all()
    
    # 要删除的记录ID
    ids_to_delete = [1, 4]
    
    print("=" * 80)
    print("准备删除以下成果记录：")
    print("=" * 80)
    
    for achievement_id in ids_to_delete:
        achievement = Achievement.query.get(achievement_id)
        if achievement:
            print(f"\nID: {achievement.id}")
            print(f"标题: {achievement.title}")
            print(f"机构: {achievement.organization}")
            print(f"日期: {achievement.date}")
            
            # 删除记录
            db.session.delete(achievement)
            print(f"✓ 已删除")
        else:
            print(f"\nID: {achievement_id} - 未找到该记录")
    
    # 提交更改
    db.session.commit()
    
    print("\n" + "=" * 80)
    print("删除完成！")
    
    # 验证删除结果
    remaining = Achievement.query.count()
    print(f"数据库中剩余 {remaining} 条成果记录")
    print("=" * 80)
