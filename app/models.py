from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    # Werkzeug 3.x 默认 scrypt 等算法哈希长度可超过 128，Postgres 会按 VARCHAR 严格截断报错
    password_hash = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.String(200))
    project_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    image_filename = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Project {self.title}>'

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    issuer = db.Column(db.String(100), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    credential_id = db.Column(db.String(100))
    credential_url = db.Column(db.String(200))
    image_filename = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Certificate {self.title}>'

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    organization = db.Column(db.String(100))
    github_url = db.Column(db.String(200))
    image_filename = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Achievement {self.title}>'

class BlockChainTestCases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(50))
    category = db.Column(db.String(50))
    sub_category = db.Column(db.String(50))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    test_steps = db.Column(db.Text)
    expected_result = db.Column(db.Text)
    actual_tool = db.Column(db.String(100))
    preconditions = db.Column(db.Text)
    test_data = db.Column(db.Text)
    priority = db.Column(db.String(20))
    test_type = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BlockChainTestCases {self.title}>'

class TestModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(50))
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<TestModule {self.name}>'

class TransactionLifecycleStage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lifecycle_type = db.Column(db.String(50), default='web3_chain')
    stage_name = db.Column(db.String(100), nullable=False)
    stage_order = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    key_concepts = db.Column(db.Text)
    involved_tables = db.Column(db.Text)
    data_flow = db.Column(db.Text)
    test_focus = db.Column(db.Text)
    common_issues = db.Column(db.Text)
    
    def __repr__(self):
        return f'<TransactionLifecycleStage {self.stage_name}>'

class ContractType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    key_features = db.Column(db.Text)
    settlement_type = db.Column(db.String(50))
    margin_mode = db.Column(db.String(50))
    risk_characteristics = db.Column(db.Text)
    test_scenarios = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<ContractType {self.name}>'

class TableRelationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(50))
    relationship_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    source_table = db.Column(db.String(100))
    target_table = db.Column(db.String(100))
    relationship_type = db.Column(db.String(50))
    key_fields = db.Column(db.Text)
    data_flow_diagram = db.Column(db.Text)
    test_scenarios = db.Column(db.Text)
    
    def __repr__(self):
        return f'<TableRelationship {self.relationship_name}>'

class PerformanceTestCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    test_objective = db.Column(db.Text)
    test_environment = db.Column(db.Text)
    test_steps = db.Column(db.Text)
    metrics_to_collect = db.Column(db.Text)
    acceptance_criteria = db.Column(db.Text)
    test_data_requirements = db.Column(db.Text)
    tools_used = db.Column(db.String(200))
    common_pitfalls = db.Column(db.Text)
    optimization_strategies = db.Column(db.Text)
    monitoring_points = db.Column(db.Text)
    
    def __repr__(self):
        return f'<PerformanceTestCase {self.title}>'


class TestType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    purpose = db.Column(db.Text)
    when_to_use = db.Column(db.Text)
    key_concepts = db.Column(db.Text)
    tools = db.Column(db.Text)
    examples = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<TestType {self.name}>'


class TestProcess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stage_name = db.Column(db.String(100), nullable=False)
    stage_order = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    key_activities = db.Column(db.Text)
    deliverables = db.Column(db.Text)
    best_practices = db.Column(db.Text)
    common_pitfalls = db.Column(db.Text)
    optimization_techniques = db.Column(db.Text)
    metrics = db.Column(db.Text)
    
    def __repr__(self):
        return f'<TestProcess {self.stage_name}>'


class APIAutomationFramework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    framework_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    core_features = db.Column(db.Text)
    architecture = db.Column(db.Text)
    setup_guide = db.Column(db.Text)
    key_components = db.Column(db.Text)
    best_practices = db.Column(db.Text)
    code_examples = db.Column(db.Text)
    pros_cons = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<APIAutomationFramework {self.framework_name}>'


class TestTheory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    key_principles = db.Column(db.Text)
    historical_context = db.Column(db.Text)
    practical_applications = db.Column(db.Text)
    related_concepts = db.Column(db.Text)
    examples = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<TestTheory {self.topic}>'


class TestCaseDesign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    technique_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    purpose = db.Column(db.Text)
    when_to_apply = db.Column(db.Text)
    step_by_step_guide = db.Column(db.Text)
    examples = db.Column(db.Text)
    advantages = db.Column(db.Text)
    limitations = db.Column(db.Text)
    real_world_scenarios = db.Column(db.Text)
    sort_order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<TestCaseDesign {self.technique_name}>'


class QAQCAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    definition = db.Column(db.Text)
    key_differences = db.Column(db.Text)
    roles_responsibilities = db.Column(db.Text)
    processes = db.Column(db.Text)
    tools_techniques = db.Column(db.Text)
    metrics_kpis = db.Column(db.Text)
    best_practices = db.Column(db.Text)
    real_world_examples = db.Column(db.Text)
    
    def __repr__(self):
        return f'<QAQCAnalysis {self.title}>'


class TestUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(20))
    file_path = db.Column(db.String(500))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    module = db.Column(db.String(50))
    category = db.Column(db.String(50))
    parsed_data = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    error_message = db.Column(db.Text)
    
    uploader = db.relationship('User', backref=db.backref('test_uploads', lazy=True))
    
    def __repr__(self):
        return f'<TestUpload {self.file_name}>'
