from datetime import date
from app import create_app, db
from app.models import User, Project, Certificate, Achievement

app = create_app()

with app.app_context():
    db.create_all()
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
    
    sample_projects = [
        Project(
            title='电商平台系统',
            description='一个完整的电商平台，支持商品浏览、购物车、订单管理、支付等功能。采用前后端分离架构，前端使用Vue.js，后端使用Flask。',
            tech_stack='Vue.js, Flask, MySQL, Redis, Docker',
            project_url='https://example.com/ecommerce',
            github_url='https://github.com/example/ecommerce',
            image_filename='project1.jpg'
        ),
        Project(
            title='任务管理系统',
            description='团队协作任务管理工具，支持任务分配、进度跟踪、团队协作等功能。',
            tech_stack='React, Node.js, MongoDB',
            project_url='https://example.com/taskmanager',
            github_url='https://github.com/example/taskmanager',
            image_filename='project2.jpg'
        ),
        Project(
            title='数据分析仪表板',
            description='实时数据分析和可视化平台，支持多种图表类型和数据导入导出。',
            tech_stack='Python, Flask, ECharts, PostgreSQL',
            project_url='https://example.com/dashboard',
            github_url='https://github.com/example/dashboard',
            image_filename='project3.jpg'
        )
    ]
    
    for p in sample_projects:
        existing = Project.query.filter_by(title=p.title).first()
        if not existing:
            db.session.add(p)
    
    sample_certificates = [
        Certificate(
            title='AWS Solutions Architect Associate',
            issuer='Amazon Web Services',
            issue_date=date(2023, 6, 15),
            expiry_date=date(2026, 6, 15),
            credential_id='AWS-SAA-2023-12345',
            credential_url='https://example.com/cert/aws',
            image_filename='cert_aws.jpg',
            description='AWS解决方案架构师专业认证，掌握AWS云服务架构设计与最佳实践。'
        ),
        Certificate(
            title='Google Cloud Professional Data Engineer',
            issuer='Google Cloud',
            issue_date=date(2023, 8, 20),
            expiry_date=date(2025, 8, 20),
            credential_id='GCP-PDE-2023-67890',
            credential_url='https://example.com/cert/gcp',
            image_filename='cert_gcp.jpg',
            description='Google Cloud专业数据工程师认证，精通大数据处理和机器学习。'
        ),
        Certificate(
            title='PMP项目管理专业人士',
            issuer='Project Management Institute',
            issue_date=date(2022, 12, 1),
            expiry_date=date(2025, 12, 1),
            credential_id='PMP-2022-11111',
            credential_url='https://example.com/cert/pmp',
            image_filename='cert_pmp.jpg',
            description='项目管理专业人士认证，掌握敏捷和传统项目管理方法论。'
        )
    ]
    
    for c in sample_certificates:
        existing = Certificate.query.filter_by(title=c.title).first()
        if not existing:
            db.session.add(c)
    
    sample_achievements = [
        Achievement(
            title='全国大学生程序设计竞赛金奖',
            description='在第15届全国大学生程序设计竞赛中，带领团队获得金奖。比赛涵盖算法设计、数据结构、系统设计等多个领域。',
            date=date(2020, 11, 15),
            organization='中国计算机学会',
            image_filename='achievement1.jpg'
        ),
        Achievement(
            title='开源项目贡献者',
            description='在GitHub上有多个开源项目，累计获得超过500个Star。主要贡献领域包括Web开发、工具库开发等。',
            date=date(2022, 6, 1),
            organization='GitHub',
            image_filename='achievement2.jpg'
        ),
        Achievement(
            title='技术博客达人',
            description='在掘金、CSDN等平台发表技术文章超过100篇，累计阅读量超过50万。分享内容涵盖Python、Web开发、云原生等技术领域。',
            date=date(2023, 3, 10),
            organization='掘金社区',
            image_filename='achievement3.jpg'
        )
    ]
    
    for a in sample_achievements:
        existing = Achievement.query.filter_by(title=a.title).first()
        if not existing:
            db.session.add(a)
    
    db.session.commit()
    print('数据库初始化完成！')
    print('默认管理员账号: admin')
    print('默认管理员密码: admin123')
