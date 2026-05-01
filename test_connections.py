#!/usr/bin/env python3
"""
测试连接情况：
1. 数据库连接
2. 飞书API连接（如果配置）
3. Web应用连接
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_database_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("测试数据库连接...")
    print("=" * 60)
    
    try:
        from app import create_app, db
        from app.models import User, Project, Certificate, Achievement
        
        app = create_app()
        
        with app.app_context():
            # 测试数据库连接
            print(f"数据库URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # 创建所有表
            db.create_all()
            print("✓ 数据库表创建成功")
            
            # 测试查询
            user_count = User.query.count()
            print(f"✓ 数据库查询成功，当前用户数: {user_count}")
            
            # 测试写入和读取
            # 检查是否已有admin用户
            admin = User.query.filter_by(username='test_admin').first()
            if not admin:
                admin = User(username='test_admin', is_admin=True)
                admin.set_password('test123')
                db.session.add(admin)
                db.session.commit()
                print("✓ 数据库写入成功")
            
            # 再次查询确认
            test_admin = User.query.filter_by(username='test_admin').first()
            if test_admin:
                print(f"✓ 数据库读取成功，找到测试用户: {test_admin.username}")
                
                # 清理测试数据
                db.session.delete(test_admin)
                db.session.commit()
                print("✓ 测试数据清理成功")
            
            print("\n✅ 数据库连接测试通过！")
            return True
            
    except Exception as e:
        print(f"\n❌ 数据库连接测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_feishu_api():
    """测试飞书API连接"""
    print("\n" + "=" * 60)
    print("测试飞书API连接...")
    print("=" * 60)
    
    try:
        from app.utils.feishu_api import FeishuAPI
        
        # 检查是否有实际的配置（不是默认的占位符）
        # 默认配置是:
        # app_id = "cli_a1a1a1a1a1a1a1a1"
        # app_secret = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        
        # 尝试创建API实例
        feishu = FeishuAPI()
        
        # 检查是否使用的是默认占位符配置
        if feishu.app_id == "cli_a1a1a1a1a1a1a1a1" or \
           feishu.app_secret == "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
            print("⚠️  飞书API使用的是默认占位符配置")
            print("ℹ️  如果需要测试实际的飞书API连接，请配置正确的 app_id 和 app_secret")
            print("ℹ️  配置位置: app/utils/feishu_api.py 或环境变量")
            print("\n⚠️  飞书API连接测试跳过（使用默认配置）")
            return None
        
        # 尝试获取access_token
        print("尝试获取飞书API access_token...")
        token = feishu.get_access_token()
        print(f"✓ 成功获取access_token: {token[:20]}...")
        
        print("\n✅ 飞书API连接测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 飞书API连接测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_web_application():
    """测试Web应用基本功能"""
    print("\n" + "=" * 60)
    print("测试Web应用基本功能...")
    print("=" * 60)
    
    try:
        from app import create_app
        
        app = create_app()
        
        # 测试应用配置
        print(f"应用名称: {app.name}")
        print(f"调试模式: {app.debug}")
        print(f"静态文件夹: {app.static_folder}")
        print(f"模板文件夹: {app.template_folder}")
        
        # 测试路由
        print("\n已注册的路由:")
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
            print(f"  {rule.endpoint}: {rule} [{methods}]")
        
        # 测试请求上下文
        with app.test_request_context():
            from flask import url_for
            print("\n✓ 请求上下文测试成功")
        
        # 测试客户端
        client = app.test_client()
        response = client.get('/')
        print(f"\n✓ 测试客户端请求成功，状态码: {response.status_code}")
        
        print("\n✅ Web应用基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ Web应用测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("连接情况测试开始")
    print("=" * 60)
    print(f"测试时间: {__import__('datetime').datetime.now()}")
    print(f"Python版本: {sys.version}")
    print(f"项目路径: {os.path.abspath(os.path.dirname(__file__))}")
    
    # 运行所有测试
    results = {}
    
    # 测试数据库连接
    results['database'] = test_database_connection()
    
    # 测试飞书API连接
    results['feishu'] = test_feishu_api()
    
    # 测试Web应用
    results['web'] = test_web_application()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results.items():
        if result is True:
            status = "✅ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⚠️  跳过"
        print(f"{name.capitalize()}: {status}")
    
    # 统计
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\n总计: {passed} 通过, {failed} 失败, {skipped} 跳过")
    
    if failed == 0:
        print("\n🎉 所有关键测试通过！")
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查配置")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)