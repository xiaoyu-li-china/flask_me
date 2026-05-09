# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import ChecklistCategory, ChecklistItem

app = create_app()

with app.app_context():
    db.create_all()
    print(f"migrate_db_add_checklist: 数据库驱动={db.engine.url.drivername}", flush=True)

    def sync_existing_record(existing_record, new_record):
        for column in new_record.__table__.columns:
            column_name = column.name
            if column_name in ('id',):
                continue
            setattr(existing_record, column_name, getattr(new_record, column_name))

    categories = [
        ChecklistCategory(
            name='区块链内部各子模块',
            code='blockchain_modules',
            description='涵盖区块链各子模块的基础原理、功能测试、非功能测试，以及子模块内部模块的完整性检查。',
            icon='fa-link',
            sort_order=1
        ),
        ChecklistCategory(
            name='测试知识体系',
            code='testing_knowledge',
            description='涵盖测试类型、测试流程、自动化框架、测试理论、用例设计等完整测试知识体系。',
            icon='fa-vial',
            sort_order=2
        ),
        ChecklistCategory(
            name='QA修炼手册',
            code='qa_handbook',
            description='涵盖QA职业发展、技能提升、质量保障、团队协作等方面的修炼指南。',
            icon='fa-book',
            sort_order=3
        )
    ]

    for c in categories:
        existing = ChecklistCategory.query.filter_by(code=c.code).first()
        if not existing:
            db.session.add(c)
        else:
            sync_existing_record(existing, c)

    db.session.flush()

    blockchain_cat = ChecklistCategory.query.filter_by(code='blockchain_modules').first()
    testing_cat = ChecklistCategory.query.filter_by(code='testing_knowledge').first()
    qa_cat = ChecklistCategory.query.filter_by(code='qa_handbook').first()

    blockchain_items = [
        ChecklistItem(
            category_id=blockchain_cat.id,
            title='Web3公链 - 基础原理',
            code='web3_fundamentals',
            description='检查Web3公链的核心概念、共识机制、交易生命周期等基础原理是否完整。',
            keywords='区块链, 公链, 基础原理, 共识机制, PoW, PoS',
            content='1. 区块链核心概念\n   - 区块结构（区块头、区块体）\n   - 哈希链（默克尔树）\n   - 去中心化与分布式账本\n\n2. 共识机制\n   - PoW（工作量证明）\n   - PoS（权益证明）\n   - DPoS、PBFT等其他共识\n\n3. 交易生命周期\n   - 交易构造与签名\n   - 交易广播与内存池\n   - 区块打包与确认\n   - 最终性保证',
            sort_order=1
        ),
        ChecklistItem(
            category_id=blockchain_cat.id,
            title='Web3公链 - 功能测试',
            code='web3_functional',
            description='检查Web3公链相关的功能测试用例是否完整。',
            keywords='功能测试, 智能合约, ERC-20, RPC接口, 交易测试',
            content='1. 智能合约测试\n   - ERC-20标准代币测试\n   - ERC-721/1155 NFT测试\n   - 合约升级与代理模式\n   - 安全漏洞测试（重入、溢出等）\n\n2. RPC接口测试\n   - eth_call vs eth_sendTransaction\n   - eth_getLogs 事件查询\n   - WebSocket 订阅（newHeads/logs）\n   - 批量JSON-RPC\n\n3. 交易测试\n   - 转账测试（普通、合约调用）\n   - Gas消耗分析\n   - Nonce管理\n   - 签名验证',
            sort_order=2
        ),
        ChecklistItem(
            category_id=blockchain_cat.id,
            title='Web3公链 - 非功能测试',
            code='web3_non_functional',
            description='检查Web3公链相关的非功能测试（性能、安全、可靠性等）是否完整。',
            keywords='性能测试, 安全测试, 51%攻击, 节点部署, 同步验证',
            content='1. 性能测试\n   - 节点同步性能\n   - RPC接口压测\n   - 交易吞吐量（TPS）\n   - Gas优化分析\n\n2. 安全测试\n   - 51%算力攻击模拟\n   - 智能合约安全审计\n   - 私钥管理安全\n   - 重放攻击防护\n\n3. 可靠性测试\n   - 节点部署与同步验证\n   - 故障恢复测试\n   - 版本升级与回滚\n   - 网络分区测试',
            sort_order=3
        ),
        ChecklistItem(
            category_id=blockchain_cat.id,
            title='CEX中心化交易所 - 基础原理',
            code='cex_fundamentals',
            description='检查CEX中心化交易所的核心业务流程、数据模型等基础原理是否完整。',
            keywords='CEX, 中心化交易所, 交易生命周期, 撮合引擎, 资金管理',
            content='1. 核心业务模块\n   - 用户注册与KYC\n   - 资产充提（充值、提现）\n   - 交易撮合（订单簿、撮合引擎）\n   - 资金清算与结算\n\n2. 币币交易生命周期\n   - 订单创建与余额冻结\n   - 订单簿入队\n   - 交易撮合\n   - 成交结算\n   - 订单完成/取消\n\n3. 合约交易生命周期\n   - 开仓准备（杠杆、保证金模式）\n   - 订单创建与保证金冻结\n   - 撮合与开仓\n   - 持仓管理（未实现盈亏、标记价格）\n   - 资金费用结算\n   - 平仓与强制平仓',
            sort_order=4
        ),
        ChecklistItem(
            category_id=blockchain_cat.id,
            title='CEX中心化交易所 - 功能测试',
            code='cex_functional',
            description='检查CEX中心化交易所的功能测试用例是否完整。',
            keywords='CEX功能测试, 币币交易, 合约交易, 充提测试, 风控测试',
            content='1. 币币交易测试\n   - 订单类型（限价、市价、止损）\n   - 撮合算法验证\n   - 成交价格计算\n   - 账户余额更新\n   - 订单簿深度管理\n\n2. 合约交易测试\n   - 开仓/平仓测试\n   - 保证金计算\n   - 未实现盈亏计算\n   - 资金费率结算\n   - 强制平仓触发\n\n3. 充提测试\n   - 充值流程（链上确认、账户入账）\n   - 提现流程（审核、链上广播）\n   - 地址校验\n   - 风控规则\n\n4. 风控系统测试\n   - 交易限额\n   - 异常交易监控\n   - 风险预警机制',
            sort_order=5
        ),
        ChecklistItem(
            category_id=blockchain_cat.id,
            title='CEX中心化交易所 - 非功能测试',
            code='cex_non_functional',
            description='检查CEX中心化交易所的非功能测试是否完整。',
            keywords='CEX性能, 撮合引擎性能, 安全测试, 高可用',
            content='1. 性能测试\n   - 撮合引擎TPS\n   - 订单处理延迟\n   - 数据库性能优化\n   - 并发用户测试\n\n2. 安全测试\n   - 资金安全（冷热钱包）\n   - API接口安全\n   - 用户数据保护\n   - 防DDoS攻击\n\n3. 高可用测试\n   - 故障转移\n   - 数据备份与恢复\n   - 容灾演练\n   - 服务降级策略',
            sort_order=6
        ),
        ChecklistItem(
            category_id=blockchain_cat.id,
            title='DEX去中心化交易所',
            code='dex_modules',
            description='检查DEX去中心化交易所的测试模块是否完整。',
            keywords='DEX, 去中心化交易所, AMM, 流动性池, 跨链桥',
            content='1. 核心功能\n   - 钱包连接协议（WalletConnect等）\n   - 流动性池管理\n   - AMM自动做市商模型\n   - 交易撮合机制\n\n2. 治理功能\n   - 治理代币\n   - 提案与投票\n   - 参数调整\n\n3. 跨链功能\n   - 跨链桥测试\n   - 多链资产映射\n   - 跨链交易确认',
            sort_order=7
        )
    ]

    for item in blockchain_items:
        existing = ChecklistItem.query.filter_by(category_id=blockchain_cat.id, code=item.code).first()
        if not existing:
            db.session.add(item)
        else:
            sync_existing_record(existing, item)

    testing_items = [
        ChecklistItem(
            category_id=testing_cat.id,
            title='测试类型',
            code='test_types',
            description='检查各类测试类型的知识是否完整。',
            keywords='测试类型, 功能测试, 性能测试, 安全测试, 兼容性测试',
            content='1. 功能测试\n   - 单元测试\n   - 集成测试\n   - 系统测试\n   - 验收测试（UAT）\n   - 回归测试\n   - 冒烟测试\n\n2. 非功能测试\n   - 性能测试（负载、压力、并发）\n   - 安全测试（渗透、漏洞扫描）\n   - 兼容性测试（浏览器、设备、系统）\n   - 可用性测试（UI/UX）\n   - 可靠性测试（稳定性、容错）\n\n3. 专项测试\n   - 接口测试（API）\n   - UI自动化测试\n   - 数据库测试\n   - 移动端测试\n   - 国际化测试',
            sort_order=1
        ),
        ChecklistItem(
            category_id=testing_cat.id,
            title='测试流程及优化',
            code='test_process',
            description='检查测试流程阶段和优化方法是否完整。',
            keywords='测试流程, 测试计划, 测试设计, 测试执行, 测试报告',
            content='1. 测试流程阶段\n   - 需求分析与评审\n   - 测试计划制定\n   - 测试用例设计\n   - 测试环境搭建\n   - 测试执行\n   - 缺陷管理\n   - 测试报告\n   - 复盘总结\n\n2. 流程优化\n   - 测试左移\n   - 精准测试\n   - 风险驱动测试\n   - 持续集成/持续测试\n   - 测试效率度量',
            sort_order=2
        ),
        ChecklistItem(
            category_id=testing_cat.id,
            title='API自动化测试框架',
            code='api_automation',
            description='检查API自动化测试框架的知识是否完整。',
            keywords='API自动化, Requests, RestAssured, Postman, JMeter',
            content='1. 主流框架\n   - Python: Requests + Pytest\n   - Java: RestAssured + TestNG\n   - 工具: Postman, JMeter\n\n2. 框架设计\n   - 分层架构（数据层、逻辑层、断言层）\n   - 配置管理\n   - 日志与报告\n   - 持续集成集成\n\n3. 最佳实践\n   - 用例独立性\n   - 数据驱动\n   - 响应断言策略\n   - 环境隔离',
            sort_order=3
        ),
        ChecklistItem(
            category_id=testing_cat.id,
            title='测试理论',
            code='test_theory',
            description='检查测试基础理论知识是否完整。',
            keywords='测试理论, 测试原则, 缺陷管理, 风险评估',
            content='1. 测试基础\n   - 测试定义与目的\n   - 测试原则（7大原则）\n   - 测试与调试的区别\n\n2. 测试层次\n   - 单元测试\n   - 集成测试\n   - 系统测试\n   - 验收测试\n\n3. 缺陷管理\n   - 缺陷生命周期\n   - 缺陷优先级与严重程度\n   - 缺陷报告规范\n\n4. 风险评估\n   - 风险识别\n   - 风险分析\n   - 风险应对策略',
            sort_order=4
        ),
        ChecklistItem(
            category_id=testing_cat.id,
            title='测试用例设计思想',
            code='case_design',
            description='检查测试用例设计技术是否完整。',
            keywords='用例设计, 等价类, 边界值, 判定表, 状态转换',
            content='1. 黑盒测试技术\n   - 等价类划分\n   - 边界值分析\n   - 判定表法\n   - 因果图法\n   - 正交试验法\n   - 场景法\n   - 错误推测法\n\n2. 白盒测试技术\n   - 语句覆盖\n   - 判定覆盖\n   - 条件覆盖\n   - 路径覆盖\n\n3. 测试用例规范\n   - 用例结构\n   - 优先级划分\n   - 可维护性',
            sort_order=5
        ),
        ChecklistItem(
            category_id=testing_cat.id,
            title='QA与QC分析',
            code='qa_qc',
            description='检查QA与QC的区别和知识体系是否完整。',
            keywords='QA, QC, 质量保证, 质量控制, 度量指标',
            content='1. QA质量保证\n   - 定义与目标\n   - 流程建立与改进\n   - 培训与指导\n   - 审计与评审\n\n2. QC质量控制\n   - 定义与目标\n   - 测试执行\n   - 缺陷发现与跟踪\n   - 产品验证\n\n3. 关键区别\n   - 预防性 vs 检测性\n   - 过程导向 vs 产品导向\n   - 全员参与 vs 特定团队\n\n4. 度量指标\n   - 测试覆盖率\n   - 缺陷密度\n   - 测试效率\n   - 逃逸缺陷率',
            sort_order=6
        )
    ]

    for item in testing_items:
        existing = ChecklistItem.query.filter_by(category_id=testing_cat.id, code=item.code).first()
        if not existing:
            db.session.add(item)
        else:
            sync_existing_record(existing, item)

    qa_items = [
        ChecklistItem(
            category_id=qa_cat.id,
            title='QA职业发展路径',
            code='career_path',
            description='QA职业发展的不同阶段和方向。',
            keywords='职业发展, 技术路线, 管理路线, 专家路线',
            content='1. 初级QA\n   - 功能测试执行\n   - 用例编写\n   - 缺陷报告\n   - 工具使用\n\n2. 中级QA\n   - 测试设计能力\n   - 自动化测试\n   - 接口测试\n   - 性能测试基础\n\n3. 高级QA/技术专家\n   - 测试架构设计\n   - 性能调优\n   - 安全测试\n   - 测试框架开发\n\n4. 管理路线\n   - 测试主管\n   - 测试经理\n   - QA总监\n   - 质量负责人',
            sort_order=1
        ),
        ChecklistItem(
            category_id=qa_cat.id,
            title='核心技能提升',
            code='skills',
            description='QA必备的核心技术和软技能。',
            keywords='技能提升, 编程能力, 数据库, Linux, 沟通协作',
            content='1. 技术技能\n   - 编程语言（Python/Java/JavaScript）\n   - 数据库（SQL、事务、索引）\n   - Linux系统操作\n   - 网络协议（HTTP/HTTPS、TCP/IP）\n   - 版本控制（Git）\n\n2. 测试技能\n   - 测试方法论\n   - 自动化框架\n   - 性能测试工具\n   - 安全测试基础\n\n3. 软技能\n   - 沟通协作\n   - 问题分析\n   - 文档写作\n   - 时间管理\n   - 持续学习',
            sort_order=2
        ),
        ChecklistItem(
            category_id=qa_cat.id,
            title='质量保障体系建设',
            code='quality_system',
            description='如何建立和完善团队的质量保障体系。',
            keywords='质量体系, 流程建设, 度量体系, 文化建设',
            content='1. 流程体系\n   - 需求评审流程\n   - 测试流程规范\n   - 发布流程\n   - 缺陷管理流程\n\n2. 度量体系\n   - 质量指标定义\n   - 数据采集\n   - 报表分析\n   - 趋势追踪\n\n3. 工具体系\n   - 用例管理\n   - 缺陷管理\n   - CI/CD集成\n   - 监控告警\n\n4. 文化建设\n   - 质量意识培养\n   - 跨团队协作\n   - 持续改进机制',
            sort_order=3
        ),
        ChecklistItem(
            category_id=qa_cat.id,
            title='团队协作与沟通',
            code='teamwork',
            description='QA如何与产品、开发、运维等角色高效协作。',
            keywords='团队协作, 跨部门沟通, 敏捷开发, 缺陷管理',
            content='1. 与产品经理协作\n   - 需求评审\n   - 验收标准对齐\n   - 变更管理\n\n2. 与开发协作\n   - 缺陷沟通\n   - 测试左移\n   - 代码评审参与\n   - 自动化共建\n\n3. 敏捷开发中的QA\n   - Sprint规划参与\n   - 每日站会\n   - 迭代回顾\n   - 持续测试\n\n4. 高效沟通技巧\n   - 问题描述清晰\n   - 数据支撑观点\n   - 建设性反馈\n   - 冲突处理',
            sort_order=4
        ),
        ChecklistItem(
            category_id=qa_cat.id,
            title='认证与学习资源',
            code='certifications',
            description='QA相关的认证考试和持续学习资源。',
            keywords='认证, ISTQB, 学习资源, 技术社区',
            content='1. 专业认证\n   - ISTQB（基础级/高级/专家级）\n   - CSTE（软件测试认证）\n   - CSQA（质量分析师认证）\n   - AWS/GCP云服务认证\n\n2. 学习平台\n   - 官方文档\n   - 技术博客\n   - 在线课程\n   - 开源项目贡献\n\n3. 技术社区\n   - 技术大会\n   - 本地Meetup\n   - 技术公众号\n   - GitHub开源社区',
            sort_order=5
        )
    ]

    for item in qa_items:
        existing = ChecklistItem.query.filter_by(category_id=qa_cat.id, code=item.code).first()
        if not existing:
            db.session.add(item)
        else:
            sync_existing_record(existing, item)

    db.session.commit()
    print(f"migrate_db_add_checklist: Checklist 模块数据初始化完成", flush=True)
