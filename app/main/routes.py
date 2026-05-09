import os
import json
from datetime import datetime
from flask import render_template, url_for, redirect, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.main import main
from app import db
from app.models import (
    Project, Certificate, Achievement, 
    BlockChainTestCases, TestModule,
    TransactionLifecycleStage, TableRelationship,
    PerformanceTestCase, TestType, TestProcess,
    APIAutomationFramework, TestTheory,
    TestCaseDesign, QAQCAnalysis,
    ContractType, TestUpload,
    ChecklistCategory, ChecklistItem
)
from app.utils.file_parser import parse_file

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
    module = (request.args.get('module') or '').strip()
    category = (request.args.get('category') or '').strip()

    # 普通用户（非管理员）功能测试仅开放 CEX 模块
    functional_cex_only = not getattr(current_user, 'is_admin', False)
    if functional_cex_only:
        if not module:
            return redirect(url_for('main.blockchain_functional_tests', module='cex'))
        if module != 'cex':
            flash('当前账号仅能访问 CEX 中心化交易所功能测试。', 'warning')
            return redirect(url_for('main.blockchain_functional_tests', module='cex'))
    
    query = BlockChainTestCases.query.filter(BlockChainTestCases.module != 'performance')
    
    if module and module != 'performance':
        query = query.filter_by(module=module)
    if category:
        query = query.filter_by(category=category)
    
    test_cases = query.order_by(
        BlockChainTestCases.module,
        BlockChainTestCases.category,
        BlockChainTestCases.priority,
        BlockChainTestCases.created_at.desc()
    ).all()

    # CEX 仅展示已上传 Excel；库内 BlockChainTestCases 卡片不再展示。
    if module == 'cex':
        test_cases = []

    modules = TestModule.query.filter(TestModule.name != 'performance').order_by(TestModule.sort_order).all()
    if functional_cex_only:
        modules = [m for m in modules if m.name == 'cex']
    
    block_chain_categories_q = db.session.query(
        BlockChainTestCases.module,
        BlockChainTestCases.category
    ).filter(BlockChainTestCases.module != 'performance')
    if functional_cex_only:
        block_chain_categories_q = block_chain_categories_q.filter_by(module='cex')
    block_chain_categories = block_chain_categories_q.distinct().all()
    
    upload_categories_q = db.session.query(
        TestUpload.module,
        TestUpload.category
    ).filter(
        TestUpload.status == 'success',
        TestUpload.module != 'performance',
        TestUpload.module != None,
        TestUpload.category != None,
        TestUpload.category != ''
    )
    if functional_cex_only:
        upload_categories_q = upload_categories_q.filter_by(module='cex')
    upload_categories = upload_categories_q.distinct().all()
    
    categories_set = set()
    for cat in block_chain_categories:
        if cat[1]:
            categories_set.add(cat)
    for cat in upload_categories:
        if cat[1]:
            categories_set.add(cat)
    
    categories = list(categories_set)
    if functional_cex_only:
        categories = [(m, c) for m, c in categories if m == 'cex']
    
    indexed_uploads_query = TestUpload.query.filter_by(status='success')
    if module and module != 'performance':
        indexed_uploads_query = indexed_uploads_query.filter_by(module=module)
    if category:
        indexed_uploads_query = indexed_uploads_query.filter_by(category=category)
    indexed_uploads = indexed_uploads_query.order_by(TestUpload.upload_time.desc()).all()

    # 上传 Excel 预览：非 CEX 需存在成功上传记录；CEX 在选定分类后始终走 Excel 区（无上传则空表提示）。
    show_uploaded_excel_only = False
    preview_upload = None
    preview_table_columns = [
        'TestCaseId', 'Module', 'SubModule', 'Title',
        'Preconditions', 'TestSteps', 'ExpectedResult', 'Priority'
    ]
    preview_table_rows = []

    if module and category:
        preview_upload = TestUpload.query.filter_by(
            status='success',
            module=module,
            category=category
        ).order_by(TestUpload.upload_time.desc()).first()

        # CEX：只要选了分类就进入 Excel 视图（无上传则提示上传），永不回退到库内卡片。
        show_uploaded_excel_only = True if module == 'cex' else bool(preview_upload)

        if preview_upload and preview_upload.parsed_data:
            try:
                parsed_data = json.loads(preview_upload.parsed_data)
                for case in parsed_data.get('test_cases', []):
                    raw_data = case.get('raw_data', {}) or {}
                    priority = case.get('priority', '') or raw_data.get('Priority', '') or raw_data.get('优先级', '')
                    preview_table_rows.append({
                        'TestCaseId': case.get('test_case_id', '') or raw_data.get('TestCaseId', '') or raw_data.get('用例ID', ''),
                        'Module': preview_upload.module or case.get('module', '') or raw_data.get('Module', '') or raw_data.get('模块', ''),
                        'SubModule': case.get('sub_module', '') or raw_data.get('SubModule', '') or raw_data.get('子模块', ''),
                        'Title': case.get('title', '') or raw_data.get('Title', '') or raw_data.get('用例标题', ''),
                        'Preconditions': case.get('preconditions', '') or raw_data.get('Preconditions', '') or raw_data.get('前置条件', ''),
                        'TestSteps': case.get('test_steps', '') or raw_data.get('TestSteps', '') or raw_data.get('测试步骤', ''),
                        'ExpectedResult': case.get('expected_result', '') or raw_data.get('ExpectedResult', '') or raw_data.get('预期结果', ''),
                        'Priority': priority
                    })

                if not preview_table_rows:
                    for sheet in parsed_data.get('sheets', []):
                        for row in sheet.get('rows', []):
                            priority = row.get('Priority', '') or row.get('优先级', '')
                            preview_table_rows.append({
                                'TestCaseId': row.get('TestCaseId', '') or row.get('用例ID', '') or row.get('用例编号', ''),
                                'Module': preview_upload.module or row.get('Module', '') or row.get('模块', ''),
                                'SubModule': row.get('SubModule', '') or row.get('Sub Module', '') or row.get('子模块', ''),
                                'Title': row.get('Title', '') or row.get('用例标题', '') or row.get('测试用例', ''),
                                'Preconditions': row.get('Preconditions', '') or row.get('前置条件', '') or row.get('前提条件', ''),
                                'TestSteps': row.get('TestSteps', '') or row.get('Test Steps', '') or row.get('测试步骤', '') or row.get('步骤', ''),
                                'ExpectedResult': row.get('ExpectedResult', '') or row.get('Expected Result', '') or row.get('预期结果', ''),
                                'Priority': priority
                            })
            except Exception:
                preview_table_rows = []

    return render_template('blockchain_functional.html',
                           title='功能测试用例',
                           test_cases=test_cases,
                           indexed_uploads=indexed_uploads,
                           show_uploaded_excel_only=show_uploaded_excel_only,
                           preview_upload=preview_upload,
                           preview_table_columns=preview_table_columns,
                           preview_table_rows=preview_table_rows,
                           modules=modules,
                           categories=categories,
                           current_module=module,
                           current_category=category)

@main.route('/blockchain-tests/<int:test_id>')
@login_required
def blockchain_test_detail(test_id):
    test_case = BlockChainTestCases.query.get_or_404(test_id)
    if not getattr(current_user, 'is_admin', False) and test_case.module != 'cex':
        flash('当前账号无权查看该测试案例。', 'danger')
        return redirect(url_for('main.blockchain_functional_tests', module='cex'))
    return render_template('blockchain_test_detail.html',
                           title=test_case.title,
                           test_case=test_case)

@main.route('/blockchain-tests/transaction-lifecycle')
@login_required
def transaction_lifecycle():
    stages = TransactionLifecycleStage.query.filter_by(
        lifecycle_type='web3_chain'
    ).order_by(
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


@main.route('/blockchain-tests/wallet-cex-dex')
@login_required
def wallet_cex_dex_relationships():
    return render_template('wallet_cex_dex_relationships.html',
                           title='钱包、CEX、DEX与公链的关系')

@main.route('/blockchain-tests/cex-contract-lifecycle')
@login_required
def cex_contract_lifecycle():
    stages = TransactionLifecycleStage.query.filter_by(
        lifecycle_type='cex_contract'
    ).order_by(
        TransactionLifecycleStage.stage_order
    ).all()
    
    contract_types = ContractType.query.order_by(
        ContractType.sort_order
    ).all()
    
    return render_template('cex_contract_lifecycle.html',
                           title='CEX合约生命周期&合约种类',
                           stages=stages,
                           contract_types=contract_types)

@main.route('/blockchain-tests/spot-trading-lifecycle')
@login_required
def spot_trading_lifecycle():
    stages = TransactionLifecycleStage.query.filter_by(
        lifecycle_type='spot_trading'
    ).order_by(
        TransactionLifecycleStage.stage_order
    ).all()
    
    return render_template('spot_trading_lifecycle.html',
                           title='币币交易生命周期',
                           stages=stages)

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


@main.route('/test-case-uploads')
@login_required
def test_case_upload_module():
    if not current_user.is_admin:
        flash('您没有权限访问上传测试用例模块', 'danger')
        return redirect(url_for('main.permission_center'))

    stats = {
        'total': TestUpload.query.count(),
        'success': TestUpload.query.filter_by(status='success').count(),
        'error': TestUpload.query.filter_by(status='error').count(),
        'processing': TestUpload.query.filter_by(status='processing').count()
    }
    return render_template('test_case_upload_module.html',
                           title='上传测试用例模块',
                           stats=stats)


@main.route('/permissions')
@login_required
def permission_center():
    return render_template('permissions.html', title='权限页面')


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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@main.route('/blockchain-tests/upload')
@login_required
def upload_test_case():
    if not current_user.is_admin:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('main.test_case_upload_module'))
    
    modules = TestModule.query.filter(TestModule.name != 'performance').order_by(TestModule.sort_order).all()

    module_categories = {m.name: [] for m in modules}

    existing_case_categories = db.session.query(
        BlockChainTestCases.module,
        BlockChainTestCases.category
    ).filter(
        BlockChainTestCases.module.isnot(None),
        BlockChainTestCases.category.isnot(None),
        BlockChainTestCases.category != ''
    ).distinct().all()

    existing_upload_categories = db.session.query(
        TestUpload.module,
        TestUpload.category
    ).filter(
        TestUpload.module.isnot(None),
        TestUpload.category.isnot(None),
        TestUpload.category != ''
    ).distinct().all()

    for module_name, category_name in list(existing_case_categories) + list(existing_upload_categories):
        if module_name in module_categories and category_name not in module_categories[module_name]:
            module_categories[module_name].append(category_name)

    for module_name in module_categories:
        module_categories[module_name].sort()

    return render_template('upload_test_case.html',
                           title='上传测试用例',
                           modules=modules,
                           module_categories=module_categories)


@main.route('/blockchain-tests/upload', methods=['POST'])
@login_required
def upload_test_case_post():
    if not current_user.is_admin:
        flash('您没有权限上传测试用例', 'danger')
        return redirect(url_for('main.test_case_upload_module'))
    
    if 'file' not in request.files:
        flash('没有选择文件', 'danger')
        return redirect(url_for('main.upload_test_case'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('没有选择文件', 'danger')
        return redirect(url_for('main.upload_test_case'))
    
    if not allowed_file(file.filename):
        flash('不支持的文件格式，支持的格式：xlsx、xls、xmind', 'danger')
        return redirect(url_for('main.upload_test_case'))
    
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        original_filename = file.filename
        original_ext = os.path.splitext(original_filename)[1].lower()
        
        safe_base = secure_filename(os.path.splitext(original_filename)[0])
        if not safe_base or safe_base.strip() == '':
            safe_base = 'test_case'
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_with_timestamp = f"{timestamp}_{safe_base}{original_ext}"
        file_path = os.path.join(upload_folder, filename_with_timestamp)
        file.save(file_path)
        
        display_filename = original_filename
        file_type = original_ext.lstrip('.')
        
        title = request.form.get('title', '') or display_filename
        description = request.form.get('description', '')
        module = request.form.get('module', '')
        category = request.form.get('category', '')
        
        test_upload = TestUpload(
            file_name=display_filename,
            file_type=file_type,
            file_path=file_path,
            uploader_id=current_user.id,
            title=title,
            description=description,
            module=module,
            category=category,
            status='processing'
        )
        db.session.add(test_upload)
        db.session.commit()
        
        try:
            parsed_result = parse_file(file_path, original_ext)
            
            test_upload.parsed_data = json.dumps(parsed_result, ensure_ascii=False)
            test_upload.status = 'success'
            
            for case in parsed_result.get('test_cases', []):
                existing = BlockChainTestCases.query.filter_by(
                    title=case.get('title', ''),
                    module=module or case.get('module', ''),
                    category=category or case.get('category', ''),
                    sub_category=case.get('sub_module', '')
                ).first()
                
                if not existing:
                    test_case = BlockChainTestCases(
                        module=module or case.get('module', ''),
                        category=category or case.get('category', ''),
                        sub_category=case.get('sub_module', ''),
                        title=case.get('title', ''),
                        description=case.get('description', ''),
                        test_steps=case.get('test_steps', ''),
                        expected_result=case.get('expected_result', ''),
                        preconditions=case.get('preconditions', ''),
                        priority=case.get('priority', ''),
                        test_type='功能测试',
                        notes=json.dumps(case.get('raw_data', {}), ensure_ascii=False)
                    )
                    db.session.add(test_case)
            
            db.session.commit()
            flash(f'文件上传成功！共解析了 {parsed_result.get("total_cases", 0)} 个测试用例', 'success')
            
        except Exception as parse_error:
            test_upload.status = 'error'
            test_upload.error_message = str(parse_error)
            db.session.commit()
            flash(f'文件上传成功，但解析时出错：{str(parse_error)}', 'warning')
        
        return redirect(url_for('main.uploaded_test_cases_list'))
    
    except Exception as e:
        flash(f'上传失败：{str(e)}', 'danger')
        return redirect(url_for('main.upload_test_case'))


@main.route('/blockchain-tests/uploaded')
@login_required
def uploaded_test_cases_list():
    module = request.args.get('module', '')
    status = request.args.get('status', '')
    
    query = TestUpload.query
    
    if module:
        query = query.filter_by(module=module)
    if status:
        query = query.filter_by(status=status)
    
    uploads = query.order_by(TestUpload.upload_time.desc()).all()
    
    modules = TestModule.query.filter(TestModule.name != 'performance').order_by(TestModule.sort_order).all()
    
    statuses = db.session.query(TestUpload.status).distinct().all()
    
    stats = {
        'total': TestUpload.query.count(),
        'success': TestUpload.query.filter_by(status='success').count(),
        'error': TestUpload.query.filter_by(status='error').count(),
        'processing': TestUpload.query.filter_by(status='processing').count()
    }
    
    return render_template('uploaded_test_cases.html',
                           title='已上传测试用例',
                           uploads=uploads,
                           modules=modules,
                           statuses=statuses,
                           current_module=module,
                           current_status=status,
                           stats=stats)


@main.route('/blockchain-tests/uploaded/<int:upload_id>')
@login_required
def uploaded_test_case_detail(upload_id):
    test_upload = TestUpload.query.get_or_404(upload_id)
    
    parsed_data = None
    if test_upload.parsed_data:
        try:
            parsed_data = json.loads(test_upload.parsed_data)
        except:
            parsed_data = None
    
    return render_template('uploaded_test_case_detail.html',
                           title=test_upload.title,
                           test_upload=test_upload,
                           parsed_data=parsed_data)


@main.route('/blockchain-tests/uploaded/<int:upload_id>/delete', methods=['POST'])
@login_required
def delete_uploaded_test_case(upload_id):
    if not current_user.is_admin:
        flash('您没有权限删除上传记录', 'danger')
        return redirect(url_for('main.uploaded_test_cases_list'))

    test_upload = TestUpload.query.get_or_404(upload_id)

    try:
        file_path = test_upload.file_path
        db.session.delete(test_upload)
        db.session.commit()

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        flash('上传记录已删除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败：{str(e)}', 'danger')

    return redirect(url_for('main.uploaded_test_cases_list'))


@main.route('/blockchain-tests/uploaded/<int:upload_id>/indexed')
@login_required
def uploaded_test_case_indexed(upload_id):
    test_upload = TestUpload.query.get_or_404(upload_id)

    if test_upload.status != 'success' or not test_upload.parsed_data:
        flash('该上传记录尚未解析成功，暂无法索引展示', 'warning')
        return redirect(url_for('main.uploaded_test_case_detail', upload_id=upload_id))

    try:
        parsed_data = json.loads(test_upload.parsed_data)
    except Exception:
        flash('解析数据格式异常，无法展示索引页面', 'danger')
        return redirect(url_for('main.uploaded_test_case_detail', upload_id=upload_id))

    table_columns = [
        'TestCaseId', 'Module', 'SubModule', 'Title',
        'Preconditions', 'TestSteps', 'ExpectedResult', 'Priority'
    ]
    table_rows = []
    for case in parsed_data.get('test_cases', []):
        raw_data = case.get('raw_data', {}) or {}
        priority = case.get('priority', '') or raw_data.get('Priority', '') or raw_data.get('优先级', '')
        table_rows.append({
            'TestCaseId': case.get('test_case_id', '') or raw_data.get('TestCaseId', '') or raw_data.get('用例ID', ''),
            'Module': test_upload.module or case.get('module', '') or raw_data.get('Module', '') or raw_data.get('模块', ''),
            'SubModule': case.get('sub_module', '') or raw_data.get('SubModule', '') or raw_data.get('子模块', ''),
            'Title': case.get('title', '') or raw_data.get('Title', '') or raw_data.get('用例标题', ''),
            'Preconditions': case.get('preconditions', '') or raw_data.get('Preconditions', '') or raw_data.get('前置条件', ''),
            'TestSteps': case.get('test_steps', '') or raw_data.get('TestSteps', '') or raw_data.get('测试步骤', ''),
            'ExpectedResult': case.get('expected_result', '') or raw_data.get('ExpectedResult', '') or raw_data.get('预期结果', ''),
            'Priority': priority
        })

    # Fallback: if structured cases are empty, render directly from original Excel rows.
    if not table_rows:
        for sheet in parsed_data.get('sheets', []):
            for row in sheet.get('rows', []):
                priority = row.get('Priority', '') or row.get('优先级', '')
                table_rows.append({
                    'TestCaseId': row.get('TestCaseId', '') or row.get('用例ID', '') or row.get('用例编号', ''),
                    'Module': test_upload.module or row.get('Module', '') or row.get('模块', ''),
                    'SubModule': row.get('SubModule', '') or row.get('Sub Module', '') or row.get('子模块', ''),
                    'Title': row.get('Title', '') or row.get('用例标题', '') or row.get('测试用例', ''),
                    'Preconditions': row.get('Preconditions', '') or row.get('前置条件', '') or row.get('前提条件', ''),
                    'TestSteps': row.get('TestSteps', '') or row.get('Test Steps', '') or row.get('测试步骤', '') or row.get('步骤', ''),
                    'ExpectedResult': row.get('ExpectedResult', '') or row.get('Expected Result', '') or row.get('预期结果', ''),
                    'Priority': priority
                })

    return render_template('uploaded_test_case_indexed.html',
                           title=f'案例库索引 - {test_upload.title}',
                           test_upload=test_upload,
                           table_columns=table_columns,
                           table_rows=table_rows)


@main.route('/checklist')
@login_required
def checklist_home():
    if not current_user.is_admin:
        flash('当前账号无权访问 Checklist 模块。', 'warning')
        return redirect(url_for('main.permission_center'))
    
    categories = ChecklistCategory.query.order_by(ChecklistCategory.sort_order).all()
    
    stats = {
        'categories': ChecklistCategory.query.count(),
        'items': ChecklistItem.query.count()
    }
    
    return render_template('checklist_home.html',
                           title='项目内容完整性 Checklist',
                           categories=categories,
                           stats=stats)


@main.route('/checklist/<int:item_id>')
@login_required
def checklist_detail(item_id):
    if not current_user.is_admin:
        flash('当前账号无权访问 Checklist 模块。', 'warning')
        return redirect(url_for('main.permission_center'))
    
    item = ChecklistItem.query.get_or_404(item_id)
    
    return render_template('checklist_detail.html',
                           title=item.title,
                           item=item)


@main.route('/checklist/create', methods=['GET', 'POST'])
@login_required
def checklist_create():
    if not current_user.is_admin:
        flash('当前账号无权访问 Checklist 模块。', 'warning')
        return redirect(url_for('main.permission_center'))
    
    categories = ChecklistCategory.query.order_by(ChecklistCategory.sort_order).all()
    
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        title = (request.form.get('title') or '').strip()
        description = (request.form.get('description') or '').strip()
        content = (request.form.get('content') or '').strip()
        
        if not category_id:
            flash('请选择分类', 'danger')
            return redirect(url_for('main.checklist_create'))
        if not title:
            flash('请输入内容', 'danger')
            return redirect(url_for('main.checklist_create'))
        
        max_order = db.session.query(db.func.max(ChecklistItem.sort_order)).filter_by(
            category_id=int(category_id)
        ).scalar() or 0
        
        item = ChecklistItem(
            category_id=int(category_id),
            title=title,
            description=description,
            content=content,
            sort_order=max_order + 1,
            status=ChecklistItem.STATUS_NOT_STARTED
        )
        db.session.add(item)
        db.session.commit()
        
        flash('Checklist 条目创建成功', 'success')
        return redirect(url_for('main.checklist_home'))
    
    return render_template('checklist_form.html',
                           title='添加检查点',
                           categories=categories,
                           item=None)


@main.route('/checklist/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def checklist_edit(item_id):
    if not current_user.is_admin:
        flash('当前账号无权访问 Checklist 模块。', 'warning')
        return redirect(url_for('main.permission_center'))
    
    item = ChecklistItem.query.get_or_404(item_id)
    categories = ChecklistCategory.query.order_by(ChecklistCategory.sort_order).all()
    
    if request.method == 'POST':
        category_id = request.form.get('category_id')
        title = (request.form.get('title') or '').strip()
        description = (request.form.get('description') or '').strip()
        content = (request.form.get('content') or '').strip()
        
        if not category_id:
            flash('请选择分类', 'danger')
            return redirect(url_for('main.checklist_edit', item_id=item.id))
        if not title:
            flash('请输入内容', 'danger')
            return redirect(url_for('main.checklist_edit', item_id=item.id))
        
        item.category_id = int(category_id)
        item.title = title
        item.description = description
        item.content = content
        db.session.commit()
        
        flash('Checklist 条目更新成功', 'success')
        return redirect(url_for('main.checklist_home'))
    
    return render_template('checklist_form.html',
                           title='修改检查点',
                           categories=categories,
                           item=item)


@main.route('/checklist/<int:item_id>/delete', methods=['POST'])
@login_required
def checklist_delete(item_id):
    if not current_user.is_admin:
        flash('当前账号无权访问 Checklist 模块。', 'warning')
        return redirect(url_for('main.permission_center'))
    
    item = ChecklistItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    
    flash('Checklist 条目删除成功', 'success')
    return redirect(url_for('main.checklist_home'))


@main.route('/checklist/<int:item_id>/status', methods=['POST'])
@login_required
def checklist_toggle_status(item_id):
    if not current_user.is_admin:
        return jsonify({'error': '无权访问'}), 403
    
    item = ChecklistItem.query.get_or_404(item_id)
    status = request.form.get('status')
    
    valid_statuses = [
        ChecklistItem.STATUS_NOT_STARTED,
        ChecklistItem.STATUS_IN_PROGRESS,
        ChecklistItem.STATUS_COMPLETED,
        ChecklistItem.STATUS_INCOMPLETE
    ]
    
    if status in valid_statuses:
        item.status = status
        db.session.commit()
        return jsonify({'success': True, 'status': status})
    
    return jsonify({'error': '无效状态'}), 400


@main.route('/checklist/<int:item_id>/move', methods=['POST'])
@login_required
def checklist_move(item_id):
    if not current_user.is_admin:
        return jsonify({'error': '无权访问'}), 403
    
    item = ChecklistItem.query.get_or_404(item_id)
    direction = request.form.get('direction')
    
    items_in_category = ChecklistItem.query.filter_by(
        category_id=item.category_id
    ).order_by(ChecklistItem.sort_order).all()
    
    current_index = None
    for i, it in enumerate(items_in_category):
        if it.id == item.id:
            current_index = i
            break
    
    if current_index is None:
        return jsonify({'error': '条目不存在'}), 404
    
    target_index = None
    if direction == 'up' and current_index > 0:
        target_index = current_index - 1
    elif direction == 'down' and current_index < len(items_in_category) - 1:
        target_index = current_index + 1
    
    if target_index is not None:
        other_item = items_in_category[target_index]
        temp_order = item.sort_order
        item.sort_order = other_item.sort_order
        other_item.sort_order = temp_order
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': '已在边界'})


@main.route('/checklist/reorder', methods=['POST'])
@login_required
def checklist_reorder():
    if not current_user.is_admin:
        return jsonify({'error': '无权访问'}), 403
    
    data = request.get_json()
    category_id = data.get('category_id')
    item_ids = data.get('item_ids', [])
    
    if not category_id or not item_ids:
        return jsonify({'error': '参数无效'}), 400
    
    for index, item_id in enumerate(item_ids):
        item = ChecklistItem.query.filter_by(id=item_id, category_id=category_id).first()
        if item:
            item.sort_order = index + 1
    
    db.session.commit()
    
    return jsonify({'success': True})
