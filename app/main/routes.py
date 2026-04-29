from flask import render_template, url_for, redirect, flash, request
from flask_login import login_required, current_user
from app.main import main
from app import db
from app.models import (
    Project, Certificate, Achievement, 
    BlockChainTestCases, TestModule,
    TransactionLifecycleStage, TableRelationship,
    PerformanceTestCase, TestType, TestProcess,
    APIAutomationFramework, TestTheory,
    TestCaseDesign, QAQCAnalysis
)

@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html', title='首页')

@main.route('/resume')
@login_required
def resume():
    return render_template('resume.html', title='个人简历')

@main.route('/projects')
@login_required
def projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', title='项目展示', projects=projects)

@main.route('/certificates')
@login_required
def certificates():
    certificates = Certificate.query.filter(
        Certificate.title.contains('ISTQB')
    ).order_by(Certificate.issue_date.desc()).all()
    return render_template('certificates.html', title='证书展示', certificates=certificates)

@main.route('/achievements')
@login_required
def achievements():
    achievements = Achievement.query.order_by(Achievement.date.desc()).all()
    return render_template('achievements.html', title='成果展示', achievements=achievements)

@main.route('/blockchain-tests')
@login_required
def blockchain_tests():
    from sqlalchemy import func
    
    total = BlockChainTestCases.query.count()
    p0 = BlockChainTestCases.query.filter_by(priority='P0').count()
    p1 = BlockChainTestCases.query.filter_by(priority='P1').count()
    modules = db.session.query(BlockChainTestCases.module).distinct().count()
    
    stats = {
        'total': total,
        'p0': p0,
        'p1': p1,
        'modules': modules
    }
    
    return render_template('blockchain_home.html', 
                           title='区块链测试案例库',
                           stats=stats)

@main.route('/blockchain-tests/functional')
@login_required
def blockchain_functional_tests():
    module = request.args.get('module', '')
    category = request.args.get('category', '')
    
    query = BlockChainTestCases.query
    
    if module:
        query = query.filter_by(module=module)
    if category:
        query = query.filter_by(category=category)
    
    test_cases = query.order_by(
        BlockChainTestCases.module,
        BlockChainTestCases.category,
        BlockChainTestCases.priority,
        BlockChainTestCases.created_at.desc()
    ).all()
    
    modules = TestModule.query.order_by(TestModule.sort_order).all()
    
    categories = db.session.query(
        BlockChainTestCases.module,
        BlockChainTestCases.category
    ).distinct().all()
    
    return render_template('blockchain_functional.html', 
                           title='功能测试用例',
                           test_cases=test_cases,
                           modules=modules,
                           categories=categories,
                           current_module=module,
                           current_category=category)

@main.route('/blockchain-tests/<int:test_id>')
@login_required
def blockchain_test_detail(test_id):
    test_case = BlockChainTestCases.query.get_or_404(test_id)
    return render_template('blockchain_test_detail.html',
                           title=test_case.title,
                           test_case=test_case)

@main.route('/blockchain-tests/transaction-lifecycle')
@login_required
def transaction_lifecycle():
    stages = TransactionLifecycleStage.query.order_by(
        TransactionLifecycleStage.stage_order
    ).all()
    return render_template('transaction_lifecycle.html',
                           title='Web3公链交易生命周期',
                           stages=stages)

@main.route('/blockchain-tests/table-relationships')
@login_required
def table_relationships():
    relationships = TableRelationship.query.order_by(
        TableRelationship.module,
        TableRelationship.id
    ).all()
    return render_template('table_relationships.html',
                           title='表格关系与数据流程',
                           relationships=relationships)

@main.route('/blockchain-tests/performance')
@login_required
def blockchain_performance_tests():
    test_cases = PerformanceTestCase.query.order_by(
        PerformanceTestCase.category,
        PerformanceTestCase.id
    ).all()
    return render_template('blockchain_performance.html',
                           title='性能测试与优化',
                           test_cases=test_cases)

@main.route('/blockchain-tests/performance/<int:test_id>')
@login_required
def performance_test_detail(test_id):
    test_case = PerformanceTestCase.query.get_or_404(test_id)
    return render_template('blockchain_performance_detail.html',
                           title=test_case.title,
                           test_case=test_case)


@main.route('/testing')
@login_required
def testing_home():
    from sqlalchemy import func
    
    test_types_count = TestType.query.count()
    test_processes_count = TestProcess.query.count()
    api_frameworks_count = APIAutomationFramework.query.count()
    test_theories_count = TestTheory.query.count()
    case_designs_count = TestCaseDesign.query.count()
    qa_qc_analyses_count = QAQCAnalysis.query.count()
    
    stats = {
        'test_types': test_types_count,
        'test_processes': test_processes_count,
        'api_frameworks': api_frameworks_count,
        'test_theories': test_theories_count,
        'case_designs': case_designs_count,
        'qa_qc_analyses': qa_qc_analyses_count
    }
    
    return render_template('testing_home.html',
                           title='测试知识体系',
                           stats=stats)


@main.route('/testing/test-types')
@login_required
def test_types():
    category = request.args.get('category', '')
    
    query = TestType.query
    
    if category:
        query = query.filter_by(category=category)
    
    test_types = query.order_by(
        TestType.sort_order,
        TestType.id
    ).all()
    
    categories = db.session.query(TestType.category).distinct().all()
    
    return render_template('test_types.html',
                           title='测试类型',
                           test_types=test_types,
                           categories=categories,
                           current_category=category)


@main.route('/testing/test-types/<int:type_id>')
@login_required
def test_type_detail(type_id):
    test_type = TestType.query.get_or_404(type_id)
    return render_template('test_type_detail.html',
                           title=test_type.name,
                           test_type=test_type)


@main.route('/testing/process')
@login_required
def test_processes():
    stages = TestProcess.query.order_by(
        TestProcess.stage_order
    ).all()
    return render_template('test_processes.html',
                           title='测试流程及流程优化',
                           stages=stages)


@main.route('/testing/api-automation')
@login_required
def api_automation_frameworks():
    category = request.args.get('category', '')
    
    query = APIAutomationFramework.query
    
    if category:
        query = query.filter_by(category=category)
    
    frameworks = query.order_by(
        APIAutomationFramework.sort_order,
        APIAutomationFramework.id
    ).all()
    
    categories = db.session.query(APIAutomationFramework.category).distinct().all()
    
    return render_template('api_automation_frameworks.html',
                           title='API自动化测试框架',
                           frameworks=frameworks,
                           categories=categories,
                           current_category=category)


@main.route('/testing/api-automation/<int:framework_id>')
@login_required
def api_automation_framework_detail(framework_id):
    framework = APIAutomationFramework.query.get_or_404(framework_id)
    return render_template('api_automation_framework_detail.html',
                           title=framework.framework_name,
                           framework=framework)


@main.route('/testing/theory')
@login_required
def test_theories():
    category = request.args.get('category', '')
    
    query = TestTheory.query
    
    if category:
        query = query.filter_by(category=category)
    
    theories = query.order_by(
        TestTheory.sort_order,
        TestTheory.id
    ).all()
    
    categories = db.session.query(TestTheory.category).distinct().all()
    
    return render_template('test_theories.html',
                           title='测试理论',
                           theories=theories,
                           categories=categories,
                           current_category=category)


@main.route('/testing/theory/<int:theory_id>')
@login_required
def test_theory_detail(theory_id):
    theory = TestTheory.query.get_or_404(theory_id)
    return render_template('test_theory_detail.html',
                           title=theory.topic,
                           theory=theory)


@main.route('/testing/case-design')
@login_required
def test_case_designs():
    category = request.args.get('category', '')
    
    query = TestCaseDesign.query
    
    if category:
        query = query.filter_by(category=category)
    
    designs = query.order_by(
        TestCaseDesign.sort_order,
        TestCaseDesign.id
    ).all()
    
    categories = db.session.query(TestCaseDesign.category).distinct().all()
    
    return render_template('test_case_designs.html',
                           title='测试用例设计思想',
                           designs=designs,
                           categories=categories,
                           current_category=category)


@main.route('/testing/case-design/<int:design_id>')
@login_required
def test_case_design_detail(design_id):
    design = TestCaseDesign.query.get_or_404(design_id)
    return render_template('test_case_design_detail.html',
                           title=design.technique_name,
                           design=design)


@main.route('/testing/qa-qc-analysis')
@login_required
def qa_qc_analyses():
    category = request.args.get('category', '')
    
    query = QAQCAnalysis.query
    
    if category:
        query = query.filter_by(category=category)
    
    analyses = query.order_by(QAQCAnalysis.id).all()
    
    categories = db.session.query(QAQCAnalysis.category).distinct().all()
    
    return render_template('qa_qc_analyses.html',
                           title='QA与QC的分析',
                           analyses=analyses,
                           categories=categories,
                           current_category=category)


@main.route('/testing/qa-qc-analysis/<int:analysis_id>')
@login_required
def qa_qc_analysis_detail(analysis_id):
    analysis = QAQCAnalysis.query.get_or_404(analysis_id)
    return render_template('qa_qc_analysis_detail.html',
                           title=analysis.title,
                           analysis=analysis)
