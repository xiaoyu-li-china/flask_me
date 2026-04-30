import os
import sys
from datetime import date

print('=== Starting database initialization ===')
print(f'Current directory: {os.getcwd()}')
print(f'Python version: {sys.version}')

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///site.db')
os.environ.setdefault('SECRET_KEY', 'flask-me-secret-key-2024')

from app import create_app, db
from app.models import User, Project, Certificate, Achievement

print('Creating Flask app...')
app = create_app()

print('Initializing database...')
with app.app_context():
    try:
        db.create_all()
        print('Database tables created successfully')

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print('Creating default admin user...')
            admin = User(username='admin')
            admin.set_password('admin123')
            admin.is_admin = True
            db.session.add(admin)
            db.session.commit()
            print('Default admin user created successfully')
        else:
            print('Admin user already exists')

        normal_user = User.query.filter_by(username='user').first()
        if not normal_user:
            print('Creating default normal user...')
            normal_user = User(username='user')
            normal_user.set_password('user123')
            normal_user.is_admin = False
            db.session.add(normal_user)
            db.session.commit()
            print('Default normal user created successfully')
        else:
            print('Normal user already exists')

        print('Adding sample projects...')
        sample_projects = [
            Project(
                title='Flask用户注册系统',
                description='基于Flask研发用户注册系统，自动化处理繁琐的账号生成与权限配置流程。平均为每次注册节省5分钟（身份证制作，OCR识别，4要素填写，人脸有缘无缘，月度100+/人 账号制作），团队月度累计节省约6.25人日。',
                tech_stack='Python, Flask, MySQL, OCR识别, 人脸识别',
                image_filename='project_flask_reg.jpg'
            ),
            Project(
                title='Python接口自动化测试框架',
                description='基于Python维护接口自动化测试框架，使用Postman、JMeter进行接口测试与性能压测，构建持续集成流水线，将核心接口回归时间从人日缩短至小时级，极大提升回归效率。',
                tech_stack='Python, Unittest, Pytest, Postman, JMeter, Jenkins',
                image_filename='project_api_auto.jpg'
            ),
            Project(
                title='Java-Appium UI自动化测试框架',
                description='搭建Java-Appium UI自动化测试框架，实现部分核心业务的自动化回归，为团队自动化转型奠定基础。',
                tech_stack='Java, Appium, UiAutomator, TestNG',
                image_filename='project_ui_auto.jpg'
            ),
            Project(
                title='Monkey测试优化脚本',
                description='优化Monkey测试执行命令，封装为一键式执行的Shell脚本，大幅提升测试执行效率。独立编写日志分析脚本，实现对Monkey测试数据的深度校验与自动化结果分析，缩短问题定位时间。',
                tech_stack='Shell脚本, Python, ADB, Monkey测试',
                image_filename='project_monkey.jpg'
            ),
            Project(
                title='数据库批量删除工具',
                description='解决测试数据清理痛点，将原需手动小时级操作优化至分钟级完成。',
                tech_stack='Python, MySQL, SQLAlchemy',
                image_filename='project_db_tool.jpg'
            ),
            Project(
                title='测试用例模版化系统',
                description='基于Xmind2testcase开源框架，实现测试用例模版化，帮助同事增加测试用例覆盖度。实现上下游测试用例模版化，提升测试用例覆盖率15%。',
                tech_stack='Python, Xmind2testcase, 测试用例管理',
                image_filename='project_testcase_template.jpg'
            )
        ]

        for p in sample_projects:
            existing = Project.query.filter_by(title=p.title).first()
            if not existing:
                db.session.add(p)
        db.session.commit()
        print(f'Projects added: {Project.query.count()}')

        print('Adding sample certificates...')
        sample_certificates = [
            Certificate(
                title='ISTQB 认证',
                issuer='国际软件测试资格认证委员会 (ISTQB)',
                issue_date=date(2025, 7, 11),
                credential_id='CN-FL25071148.pdf',
                image_filename='CN-FL25071148.pdf',
                description='系统学习了测试理论知识，掌握完整的测试理论体系，包括测试基础、测试管理、测试技术、测试工具等核心内容。'
            )
        ]

        for c in sample_certificates:
            existing = Certificate.query.filter_by(title=c.title).first()
            if not existing:
                db.session.add(c)
            else:
                existing.issuer = c.issuer
                existing.issue_date = c.issue_date
                existing.credential_id = c.credential_id
                existing.image_filename = c.image_filename
                existing.description = c.description
        db.session.commit()
        print(f'Certificates added: {Certificate.query.count()}')

        print('Adding sample achievements...')
        sample_achievements = [
            Achievement(
                title='MyBaby项目获上海电视台报道',
                description='主导试管婴儿医疗区块链项目测试，涉及高度敏感的健康数据管理，对数据安全与隐私保护有极致要求，项目成功上线并获"上海电视台"报道。',
                date=date(2022, 6, 1),
                organization='OceanEx交易所',
                image_filename='achievement_mybaby.jpg'
            ),
            Achievement(
                title='NFT项目获10w VET奖励',
                description='独立负责NFT项目，项目取得积极反响，同年获得10w VET奖励。',
                date=date(2021, 12, 1),
                organization='OceanEx交易所',
                image_filename='achievement_nft.jpg'
            ),
            Achievement(
                title='小程序日活从0到2万+',
                description='独立负责核心小程序业务测试，支撑其用户规模在半年内从零增长至日活2万+，关键指标反超已有9年历史的APP，成为公司新的增长引擎。',
                date=date(2025, 6, 1),
                organization='人品科技有限公司',
                image_filename='achievement_miniprogram.jpg'
            ),
            Achievement(
                title='Flask用户注册系统节省6.25人日/月',
                description='基于Flask研发用户注册系统，自动化处理繁琐的账号生成与权限配置流程，平均为每次注册节省5分钟（身份证制作，OCR识别，4要素填写，人脸有缘无缘，月度100+/人 账号制作），团队月度累计节省约6.25人日。',
                date=date(2024, 12, 1),
                organization='人品科技有限公司',
                image_filename='achievement_flask.jpg'
            ),
            Achievement(
                title='推行Jira BUG管理工具，减少40%以上沟通成本',
                description='成功推行Jira BUG管理工具，设计统一工作流与字段规范，减少团队40%以上沟通成本，实现问题流程透明化与可量化，极大促进产研测协同效能。',
                date=date(2024, 9, 1),
                organization='人品科技有限公司',
                image_filename='achievement_jira.jpg'
            ),
            Achievement(
                title='测试流程优化，项目延期风险降低20%以上',
                description='从零开始优化并完善公司级测试流程，引入测试左移、精准测试等理念，建立需求评审、测试计划、用例评审、缺陷管理、复盘闭环的标准流程，将项目延期风险降低20%以上，整体测试效率提升显著。',
                date=date(2021, 3, 1),
                organization='OceanEx交易所',
                image_filename='achievement_process.jpg'
            )
        ]

        for a in sample_achievements:
            existing = Achievement.query.filter_by(title=a.title).first()
            if not existing:
                db.session.add(a)
        db.session.commit()
        print(f'Achievements added: {Achievement.query.count()}')

        print('=== Database initialization completed ===')
        print(f'Total Users: {User.query.count()}')
        print(f'Total Projects: {Project.query.count()}')
        print(f'Total Certificates: {Certificate.query.count()}')
        print(f'Total Achievements: {Achievement.query.count()}')

    except Exception as e:
        print(f'Error during database initialization: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
