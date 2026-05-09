# -*- coding: utf-8 -*-
from datetime import date
from sqlalchemy import text
from app import create_app, db
from app.models import (
    User, Project, Certificate, Achievement, 
    BlockChainTestCases, TestModule, 
    TransactionLifecycleStage, TableRelationship,
    PerformanceTestCase, TestType, TestProcess,
    APIAutomationFramework, TestTheory,
    TestCaseDesign, QAQCAnalysis,
    ContractType, TestUpload,
    ChecklistCategory, ChecklistItem
)

app = create_app()

with app.app_context():
    db.create_all()
    # 便于在 Render 日志中确认实际连的是 Postgres 还是 SQLite（避免 init 与 Web 连不同库）
    print(f"init_db: 数据库驱动={db.engine.url.drivername}", flush=True)
    # Postgres 上若 user 表仍是旧版 VARCHAR(128)，Werkzeug3 scrypt 密码哈希会超长导致插入失败
    if db.engine.url.drivername == 'postgresql':
        try:
            with db.engine.begin() as conn:
                conn.execute(
                    text('ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(512)')
                )
        except Exception as exc:
            print(f'init_db: 调整 user.password_hash 列宽跳过（可能已是新宽度）: {exc}', flush=True)
    
    def sync_existing_record(existing_record, new_record):
        for column in new_record.__table__.columns:
            column_name = column.name
            if column_name in ('id', 'created_at', 'upload_time'):
                continue
            setattr(existing_record, column_name, getattr(new_record, column_name))
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin123')
        admin.is_admin = True
        db.session.add(admin)
    else:
        if not admin.is_admin:
            admin.is_admin = True

    normal_user = User.query.filter_by(username='user').first()
    if not normal_user:
        normal_user = User(username='user')
        normal_user.set_password('user123')
        normal_user.is_admin = False
        db.session.add(normal_user)
    else:
        if normal_user.is_admin:
            normal_user.is_admin = False
    
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
        ),
        Project(
            title='公链节点部署与同步验证',
            description='在测试网或私有化环境中完成全节点/归档节点部署与版本升级回滚演练；验证初始同步、断点续传、对等节点数与出块延迟；建立高度/哈希对账与磁盘、带宽、句柄等资源基线巡检，覆盖进程崩溃与机器重启后的自愈与追块。',
            tech_stack='Docker, systemd, Geth/Reth/Besu, Prometheus, 区块浏览器',
            image_filename='project_flask_reg.jpg'
        ),
        Project(
            title='JSON-RPC 链上查询与网关服务测试',
            description='对上游节点与自建 RPC 网关构建自动化回归：HTTP/HTTPS 与 WebSocket 的订阅稳定性、批量 JSON-RPC、超时重试与限流熔断；重点覆盖 eth_getLogs 起止块过大、地址/Topic 过滤组合、chainId 与 EIP-1559 字段一致性，以及重组(reorg)后查询结果与最终性策略对齐。',
            tech_stack='Python, Postman, Pytest, Nginx, Redis 限流, Web3.py / ethers.js',
            image_filename='project_api_auto.jpg'
        )
    ]
    
    for p in sample_projects:
        existing = Project.query.filter_by(title=p.title).first()
        if not existing:
            db.session.add(p)
        else:
            sync_existing_record(existing, p)
    
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
            sync_existing_record(existing, c)
    
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
        else:
            sync_existing_record(existing, a)
    
    sample_blockchain_tests = [
        BlockChainTestCases(
            module='web3_chain',
            category='智能合约',
            sub_category='ERC-20标准',
            title='ERC-20代币转账边界测试',
            description='测试ERC-20标准代币合约的转账功能边界情况，包括零地址转账、超额转账、approve/transferFrom流程等。',
            preconditions='1. 已部署ERC-20代币合约\n2. 测试账户有代币余额\n3. 测试网络正常连接',
            test_data='ERC-20合约地址、测试账户地址和私钥、测试代币数量',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 部署ERC-20代币合约，初始供应量1000000枚\n2. 测试账户A向零地址(0x000...000)转账100枚\n3. 测试账户A向账户B转账超过余额的金额\n4. 测试账户A approve账户C 500枚额度\n5. 测试账户C通过transferFrom从A转账给B 300枚\n6. 测试账户C再次transferFrom超过剩余额度',
            expected_result='步骤2: 交易失败或抛出异常\n步骤3: 交易失败，余额不足\n步骤4: approve成功，allowance为500\n步骤5: transferFrom成功，A余额减少300，B增加300\n步骤6: 交易失败，额度不足',
            actual_tool='Hardhat',
            notes='在实际项目中发现的注意点：\n\n1. **零地址转账风险**：部分ERC-20实现未禁止向零地址转账，这会导致代币永久锁定。建议在合约中显式添加零地址检查。\n\n2. **approve frontrunning攻击**：当用户先approve 1000，后修改为500时，恶意观察者可以在两笔交易之间先转走1000，再转走500。建议使用increaseAllowance/decreaseAllowance模式。\n\n3. **decimal精度问题**：测试时务必注意代币的decimals，1枚代币实际是10^decimals单位。使用ethers.js的parseEther/formatEther工具避免手动计算错误。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='智能合约',
            sub_category='安全漏洞',
            title='重入攻击(Reentrancy)漏洞测试',
            description='测试智能合约是否存在重入攻击漏洞，这是DAO攻击事件的根本原因。验证合约在调用外部合约前是否正确更新状态。',
            preconditions='1. 已部署Vault合约\n2. 已部署Attacker攻击合约\n3. 测试账户有ETH余额',
            test_data='Vault合约地址、Attacker合约地址、测试ETH数量',
            priority='P0',
            test_type='安全测试',
            test_steps='1. 部署一个简单的Vault合约，用户可存款和取款\n2. 部署恶意攻击合约Attacker\n3. Attacker合约向Vault存入1 ETH\n4. Attacker调用Vault.withdraw(1 ETH)\n5. 观察Attacker的fallback/receive函数是否再次调用withdraw\n6. 检查Vault合约最终余额和Attacker余额',
            expected_result='如果存在漏洞：Attacker可以多次取款，耗尽Vault资金\n如果已修复：Attacker只能取款一次，第二次取款失败',
            actual_tool='Truffle + Ganache',
            notes='在实际项目中发现的注意点：\n\n1. **Checks-Effects-Interactions模式**：必须严格遵循：先检查条件，再更新状态，最后与外部合约交互。这是防止重入的最有效方法。\n\n2. **ReentrancyGuard**：使用OpenZeppelin的ReentrancyGuard修饰符作为额外保护层，但不应替代Checks-Effects-Interactions模式。\n\n3. **transfer/send vs call**：.transfer()和.send()有2300 gas限制，原本设计用来防止重入。但EIP-2929后gas成本变化，建议使用.call并配合重入保护。\n\n4. **跨合约调用分析**：不仅要检查直接的外部调用，还要分析间接调用链。一个看似安全的调用可能触发另一个合约的恶意逻辑。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='共识机制',
            sub_category='PoW共识',
            title='PoW网络51%算力攻击模拟',
            description='在私有测试网中模拟51%算力攻击场景，验证双花(Double Spending)攻击的可能性和防护措施。',
            preconditions='1. 已启动PoW私有测试网\n2. 控制两个节点的算力\n3. 测试账户有BTC余额',
            test_data='测试网节点配置、测试账户地址、测试BTC数量',
            priority='P1',
            test_type='安全测试',
            test_steps='1. 启动一个PoW私有测试网，初始难度较低\n2. 控制节点A拥有51%算力，节点B拥有49%\n3. 节点A在链A上向商家发送1 BTC购买商品\n4. 商家确认6个区块后发货\n5. 节点A开始在私有链B上挖矿，不包含步骤3的交易\n6. 节点A持续挖矿直到链B长度超过链A\n7. 节点A向全网广播链B\n8. 观察网络是否接受更长的链',
            expected_result='1. 初始链A被网络接受\n2. 节点A成功分叉出链B\n3. 当链B长度超过链A时，网络切换到链B\n4. 步骤3中的交易被回滚，节点A实现双花',
            actual_tool='Bitcoin Core RegTest',
            notes='在实际项目中发现的注意点：\n\n1. **确认数的重要性**：比特币建议6个确认，但对于高价值交易，建议等待更多确认。交易所通常要求10-100个确认。\n\n2. **算力分布监控**：实时监控网络算力分布。如果某一矿池接近50%，应警惕中心化风险。\n\n3. **最长链原则**：理解PoW的"最长链"实际是"累计工作量最大"的链。这是攻击成功的理论基础。\n\n4. **PoS的不同**：PoS共识机制(如以太坊)的攻击成本更高，攻击者需要质押大量代币，且有Slashing机制惩罚恶意行为。\n\n5. **Finality(最终性)**：追求即时最终性的共识算法(如PBFT)可以避免这类攻击，但牺牲了部分去中心化。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='RPC接口',
            sub_category='交易接口',
            title='eth_call vs eth_sendTransaction差异测试',
            description='深入理解以太坊RPC接口中eth_call和eth_sendTransaction的区别，测试两者在状态修改、gas消耗、返回值等方面的不同行为。',
            preconditions='1. 已部署Counter合约\n2. 测试账户有ETH余额\n3. 连接到以太坊节点',
            test_data='Counter合约地址、测试账户地址和私钥',
            priority='P1',
            test_type='功能测试',
            test_steps='1. 部署一个简单的计数器合约Counter，包含：\n   - count() view函数返回当前值\n   - increment() 函数增加计数并返回新值\n2. 使用eth_call调用increment()\n3. 检查count值是否变化\n4. 使用eth_sendTransaction调用increment()\n5. 等待交易确认后检查count值\n6. 比较两者的返回值和gas消耗\n7. 测试在合约中发送ETH时的行为差异',
            expected_result='eth_call:\n- 状态不改变，count保持原值\n- 不消耗gas\n- 立即返回函数执行结果\n\neth_sendTransaction:\n- 状态被修改，count增加\n- 消耗gas\n- 返回交易哈希，需等待确认\n- 无法直接获取返回值(需通过事件或二次call)',
            actual_tool='Postman + Ganache',
            notes='在实际项目中发现的注意点：\n\n1. **返回值获取**：eth_sendTransaction不返回函数返回值，只能返回txHash。如需获取返回值，有三种方案：\n   - 使用事件(Event)\n   - 交易确认后再eth_call一次\n   - 使用eth_estimateGas模拟执行获取返回值\n\n2. **gas估计**：eth_call可以用来估计gas，但实际发送时仍可能失败(如状态变化导致的条件变化)。\n\n3. **节点同步状态**：eth_call使用的是节点当前状态。如果节点不同步，返回结果可能不准确。\n\n4. **安全性**：永远不要信任eth_call的结果作为最终状态验证，特别是在处理金融交易时。\n\n5. **Raw Transaction**：生产环境中通常使用eth_sendRawTransaction而非eth_sendTransaction，因为前者允许离线签名，更安全。\n\n6. **批量与网关**：经网关路由时注意 id 映射、超时与 HTTP 413/429；同一批次内切勿混用不同 chainId 的 endpoint。\n\n**关联实践项目**：JSON-RPC 链上查询与网关服务测试（项目展示页）。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='Gas消耗',
            sub_category='存储优化',
            title='存储优化与Gas成本分析',
            description='测试不同Solidity数据结构和存储模式的Gas消耗差异，包括storage vs memory、packing变量、映射vs数组等场景。',
            preconditions='1. 已部署不同版本的存储合约\n2. 测试账户有ETH余额\n3. 配置了gas-reporter',
            test_data='存储合约地址、测试账户地址和私钥',
            priority='P2',
            test_type='性能测试',
            test_steps='1. 编写多个版本的存储合约：\n   Version A: 单独的uint256变量\n   Version B: 使用Struct打包多个小变量\n   Version C: 使用mapping存储\n   Version D: 使用array存储\n\n2. 测试写入操作的Gas消耗：\n   - 写入一个新slot\n   - 更新已有slot\n   - 删除(清零)slot\n\n3. 测试读取操作的Gas消耗\n\n4. 测试数组push/pop的Gas\n\n5. 测试mapping的key不存在时的行为',
            expected_result='1. 256位对齐：同一slot内的变量共享存储，节省Gas\n2. SSTORE成本：新slot 20000 gas，更新 5000 gas，清零返还15000 gas\n3. SLOAD成本：固定2100 gas(EIP-2929后)\n4. mapping读取比数组随机访问更贵\n5. 数组push有额外的长度更新成本',
            actual_tool='Hardhat + gas-reporter',
            notes='在实际项目中发现的注意点：\n\n1. **Storage Packing**：合理排列变量顺序可以大幅节省Gas。例如，两个uint128可以打包进一个slot，但如果中间夹着一个uint256就不行。\n\n2. **内存vs存储**：memory操作比storage便宜得多。复杂计算应在memory中完成后一次性写入storage。\n\n3. **删除存储的Gas返还**：删除storage变量会返还Gas，但有上限(最多交易Gas的一半)。这意味着不能靠删除存储来赚钱。\n\n4. **Gas Token**：在Gas价格低时存储数据，价格高时删除获取返还。这是一种Gas套利策略，但EIP-3298后被移除。\n\n5. **冷读vs热读**：EIP-2929引入了访问列表，首次访问(冷)2100 gas，后续访问(热)100 gas。合理安排访问顺序可以优化。\n\n6. **代理模式的Gas**：委托调用(delegatecall)有额外的Gas开销，但存储在主合约中。需要权衡升级灵活性和Gas成本。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='智能合约',
            sub_category='安全漏洞',
            title='整数溢出与下溢测试',
            description='测试Solidity 0.8.0前后版本对整数溢出的不同处理行为，验证SafeMath库的必要性和使用方法。',
            preconditions='1. 已编译Solidity 0.7.0和0.8.0版本的合约\n2. 测试账户有ETH余额\n3. 连接到测试网络',
            test_data='测试合约地址、测试账户地址和私钥',
            priority='P1',
            test_type='安全测试',
            test_steps='1. 编译Solidity 0.7.0版本的合约，包含：\n   function add(uint256 a, uint256 b) pure returns(uint256) { return a + b; }\n   function sub(uint256 a, uint256 b) pure returns(uint256) { return a - b; }\n\n2. 测试边界情况：\n   - add(type(uint256).max, 1)\n   - sub(0, 1)\n\n3. 编译Solidity 0.8.0版本的相同合约，重复测试\n\n4. 使用SafeMath库(0.7版本)测试相同场景\n\n5. 观察不同版本的行为差异',
            expected_result='Solidity 0.7.0 (无SafeMath):\n- 溢出/下溢静默发生，返回错误结果\n- add(MAX, 1) = 0\n- sub(0, 1) = MAX\n\nSolidity 0.8.0+:\n- 溢出/下溢自动revert\n- 交易失败\n\n使用SafeMath:\n- 显式检查，溢出时revert',
            actual_tool='Remix IDE + Hardhat',
            notes='在实际项目中发现的注意点：\n\n1. **Solidity 0.8.0的内置检查**：0.8.0版本后，编译器默认插入溢出检查，但这会增加约5-10%的Gas成本。如果需要极致优化且有自信，可以用unchecked块。\n\n2. **unchecked块的风险**：unchecked块内不检查溢出，必须确保数学逻辑的安全性。常用于已验证边界的循环计数器。\n\n3. **不同整数类型**：uint8/uint16/uint32等小类型更容易溢出，尤其在累加操作中。建议使用uint256进行中间计算，最后再转换。\n\n4. **有符号整数的特殊性**：int类型的溢出行为与uint不同，且二补码表示容易出错。除非必要，优先使用uint。\n\n5. **升级合约的兼容性**：如果从0.7版本升级到0.8+，注意某些依赖溢出的"特性"会变成bug。例如，某些代币合约利用溢出实现特殊逻辑。\n\n6. **formatted audit**：审计时特别注意unchecked块和复杂的数学公式，建议使用形式化验证工具(如CertiK)验证关键数学逻辑。\n\n**关联实践项目**：测试用例模版化系统 / Hardhat 合约流水线（可结合项目展示中的自动化与模版化实践）。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='节点与网络',
            sub_category='部署与同步',
            title='全节点部署、同步进度与健康检查',
            description='验证自建或托管全节点/验证者从创世或快照恢复后的同步行为，以及对等连接、链尖高度与本地状态是否一致，避免业务读到落后或损坏的链状态。',
            preconditions='1. 已部署至少一个共识客户端+可选执行客户端（或单客户端架构）\n2. 具备访问 net_peerCount、eth_blockNumber、eth_syncing 等 RPC 的权限\n3. 有可对照的区块浏览器或第二独立节点',
            test_data='节点配置文件、JWT/引擎 API 密钥、测试网 chainId、对照用 explorer 或备用 RPC',
            priority='P0',
            test_type='功能/可靠性测试',
            test_steps='1. 记录启动后 eth_syncing：应经历从 false→同步中→false 的状态迁移（取决于初始数据量）\n2. 对比本地 eth_blockNumber 与权威浏览器/备用节点，误差应在可接受出块间隔内\n3. 模拟磁盘满、进程 kill -9、整机重启，验证恢复后能否继续追块且无 DB 损坏告警\n4. 检查日志中对等连接数过低、INVALID 区块、forkchoice 不合等错误\n5. 变更一小版本号做滚动升级与回滚演练，观察同步不受影响\n6. 对归档节点：验证历史 state 查询与全节点一致（若有该需求）',
            expected_result='1. 同步完成后 eth_syncing 为 false（或客户端文档定义的完成态）\n2. 高度与对照源持续对齐，无长期落后\n3. 故障恢复后自动追块，无需人工数据目录清理（除非文档要求）\n4. 升级回滚路径在测试环境可重复执行',
            actual_tool='Docker Compose / systemd + Geth、Reth、Besu 等官方发行版',
            notes='测试注意点：\n\n1. **快照与检查点**：从快照启动可节省时间，但要校验快照来源与哈希，防止污染。\n2. **磁盘与 IO**：历史链数据量级极大，SSD、文件系统与 inode 需提前容量评估。\n3. **网络策略**：P2P 端口、出站限制会导致 peer 数长期为 0，需与运维协同排查。\n4. **时钟与 NTP**：验证者/共识节点对时钟敏感，漂移过大可能缺席出块。\n5. **多客户端生态**：执行层与共识层版本矩阵要在发布说明中逐项对齐，避免「能启动但不同步」。\n\n**关联实践项目**：公链节点部署与同步验证（项目展示页）。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='RPC接口',
            sub_category='事件与日志',
            title='eth_getLogs 范围、过滤与重组一致性',
            description='围绕事件索引与查询接口验证：地址与 Topic 组合、起止块跨度、429/超时与节点返回上限，以及链重组后已读日志与业务落库的最终性策略是否一致。',
            preconditions='1. 已连接可写读的全节点或支持日志索引的 RPC\n2. 测试合约能产生多条带索引事件\n3. 可在测试网制造或观察短重组（或使用私链）',
            test_data='合约地址、事件 ABI、fromBlock/toBlock 用例、地址列表与 Topic0/Topic1 组合',
            priority='P0',
            test_type='功能/接口测试',
            test_steps='1. 单次查询极大块跨度，观察是否超时、截断或返回错误码\n2. 拆分多个小区间查询与单次大区间的结果 diff\n3. 仅填 address、仅填 topics、多地址 OR（若客户端支持）边界\n4. 区块边界上的日志：fromBlock=toBlock=最新块是否包含该块内交易日志\n5. 在可重组环境：记录某一 tx 的 logIndex，在浅重组后比对是否需业务侧回滚或重扫\n6. 与 eth_getTransactionReceipt 中 logs 字段逐字段对齐抽查',
            expected_result='1. 文档化单次查询的块跨度与 QPS 限制，超出时有明确降级策略\n2. 拆分查询与单次查询在相同高度下日志集合一致\n3. 重组场景下业务侧「确认数」策略可解释、可回归\n4. receipt 与 getLogs 字段一致',
            actual_tool='curl / Postman + Web3.py 脚本 + 自建索引对比（可选 The Graph）',
            notes='测试注意点：\n\n1. **块范围**：过大范围易导致节点 OOM 或网关中断，生产应分页或流式消费。\n2. **removed 字段**：部分客户端在重组标记 removed log，消费方必须处理。\n3. **虚假安全**：仅靠「拿到日志」不够，需结合区块确认数或 finalized 标签（视链而定）。\n4. **匿名事件与未索引参数**：Topic 过滤行为与预期不符时优先核对 ABI。\n5. **Alchemy/Infura 等供应商**：免费层与公司层的返回限制不同，需在 CI 用接近生产的档位测。\n\n**关联实践项目**：JSON-RPC 链上查询与网关服务测试（项目展示页）。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='RPC接口',
            sub_category='WebSocket',
            title='WebSocket 订阅（newHeads/logs）与断线恢复',
            description='验证应用长连接订阅的稳定性：订阅 payload 格式、二进制帧、心跳与代理超时，以及断线重连后的 gap 补偿（补拉区块或重放 getLogs）。',
            preconditions='1. 节点或网关开启 WebSocket\n2. 测试环境可持续出块\n3. 可模拟网络中断（防火墙、kill 连接）',
            test_data='wss URL、订阅过滤器、重连退避策略配置',
            priority='P1',
            test_type='功能/稳定性测试',
            test_steps='1. 建立 wss 连接，分别订阅 newHeads 与 logs（带 address/topics 过滤）\n2. 持续运行 ≥30 分钟，统计消息间隔与乱序/重复块哈希\n3. 中间主动断开 TCP，验证客户端指数退避重连是否生效\n4. 断连期间记录最后安全高度，重连后用 eth_getLogs 或 JSON-RPC batch 补齐缺口\n5. 经反向代理（Nginx）时调大 read_timeout，验证长连接不被误杀\n6. 多 Tab 或多进程重复订阅下的服务端资源占用',
            expected_result='1. 订阅推送字段与 HTTP 轮询一致\n2. 可容忍短暂断连且不漏块（或在可控策略下可检测并告警漏块）\n3. 代理超时与客户端 keepalive 配置匹配\n4. 无内存泄漏或 goroutine/线程泄漏（服务端视角）',
            actual_tool='wscat / Python websockets + Nginx + Pytest',
            notes='测试注意点：\n\n1. **与 HTTP 混用**：同一后端 key 的 WS 与 REST 限流策略可能不同，要分别压测。\n2. **链 ID**：切换网络时必须重建订阅，防止张冠李戴。\n3. **处理 backlog**：高块速链上若处理慢于出块，需有队列与丢弃策略。\n4. **EIP-4844 等升级**：升级前后区块头字段变化要纳入契约测试。\n\n**关联实践项目**：JSON-RPC 链上查询与网关服务测试（项目展示页）。'
        )
    ]
    
    for t in sample_blockchain_tests:
        existing = BlockChainTestCases.query.filter_by(title=t.title).first()
        if not existing:
            db.session.add(t)
        else:
            sync_existing_record(existing, t)
    
    test_modules = [
        TestModule(
            name='web3_chain',
            display_name='Web3公链',
            description='涵盖公链全流程测试：交易生命周期与最终性、共识与重组风险、智能合约与 Gas、钱包与签名；节点侧含全节点/归档/验证者部署、同步与健康检查、版本升级与快照恢复；RPC 与应用侧含 JSON-RPC/WebSocket、批量与限流、eth_call 与发送交易差异、事件日志(eth_getLogs)与 trace/debug 类接口的正确性与边界。可与项目展示中的「公链节点部署与同步验证」「JSON-RPC 链上查询与网关服务测试」等实践结合回归。',
            icon='fa-link',
            sort_order=1
        ),
        TestModule(
            name='cex',
            display_name='CEX中心化交易所',
            description='涵盖中心化交易所全流程测试：注册登录、KYC身份认证、用户资产管理、充提币流程、交易撮合引擎、订单管理、风控系统等核心功能模块测试。',
            icon='fa-building',
            sort_order=2
        ),
        TestModule(
            name='dex',
            display_name='DEX去中心化交易所',
            description='涵盖去中心化交易所核心测试：钱包连接协议、流动性池管理、AMM自动做市商模型、交易撮合机制、用户资产管理、治理投票、跨链桥等功能测试。',
            icon='fa-exchange-alt',
            sort_order=3
        ),
        TestModule(
            name='spot_trading',
            display_name='币币交易补充测试点',
            description='涵盖币币交易核心原理测试：订单类型与管理、撮合引擎算法、成交价格计算、账户余额管理、交易风控规则、订单簿深度管理等功能测试。',
            icon='fa-chart-line',
            sort_order=4
        ),
        TestModule(
            name='contract_trading',
            display_name='合约交易补充测试点',
            description='涵盖合约交易全流程测试：合约生命周期、开仓平仓机制、保证金管理、资金费率计算、强制平仓触发、风险控制规则、合约类型差异等功能测试。',
            icon='fa-file-contract',
            sort_order=5
        ),
        TestModule(
            name='performance',
            display_name='性能测试',
            description='涵盖系统性能测试：并发用户测试、接口压力测试、数据库性能优化、系统监控指标、性能瓶颈分析、容量规划评估等性能相关测试。',
            icon='fa-tachometer-alt',
            sort_order=6
        )
    ]
    
    for m in test_modules:
        existing = TestModule.query.filter_by(name=m.name).first()
        if not existing:
            db.session.add(m)
        else:
            sync_existing_record(existing, m)
    
    web3_transaction_lifecycle_stages = [
        TransactionLifecycleStage(
            lifecycle_type='web3_chain',
            stage_name='交易构造',
            stage_order=1,
            description='用户或应用程序构造一笔区块链交易，包含所有必要字段',
            key_concepts='nonce, gasPrice, gasLimit, to, value, data, chainId',
            involved_tables='transactions, wallets, user_accounts',
            data_flow='用户输入 → 前端校验 → 构造交易对象 → 签名',
            test_focus='交易字段完整性、nonce管理、gas参数设置、chainId校验',
            common_issues='nonce重复/跳过、gasPrice过低、gasLimit不足、chainId不匹配'
        ),
        TransactionLifecycleStage(
            lifecycle_type='web3_chain',
            stage_name='交易签名',
            stage_order=2,
            description='使用私钥对交易进行签名，确保交易的完整性和身份验证',
            key_concepts='ECDSA签名、v/r/s、keccak256哈希、私钥管理',
            involved_tables='wallets, key_pairs (离线)',
            data_flow='交易哈希 → 私钥签名 → 生成签名交易',
            test_focus='签名算法正确性、私钥安全性、签名格式兼容性',
            common_issues='签名失败、签名格式错误、私钥泄露风险'
        ),
        TransactionLifecycleStage(
            lifecycle_type='web3_chain',
            stage_name='交易广播',
            stage_order=3,
            description='将签名后的交易广播到区块链网络中的节点',
            key_concepts='P2P网络、交易池、节点传播、eth_sendRawTransaction',
            involved_tables='transactions, network_nodes, mempool',
            data_flow='签名交易 → RPC/WS → 节点接收 → 网络广播',
            test_focus='网络连接稳定性、广播成功率、节点同步状态；经 RPC 网关时的重试退避、429/超时与 eth_sendRawTransaction 幂等',
            common_issues='网络超时、节点不接收、广播后消失；多节点负载下 mempool 视图不一致'
        ),
        TransactionLifecycleStage(
            lifecycle_type='web3_chain',
            stage_name='内存池等待',
            stage_order=4,
            description='交易进入节点的内存池，等待被矿工打包',
            key_concepts='mempool、gasPrice排序、交易替换、pending状态',
            involved_tables='mempool, transactions, gas_oracle',
            data_flow='节点验证 → 加入mempool → 等待打包',
            test_focus='mempool大小限制、gasPrice竞争、交易替换机制',
            common_issues='mempool满被踢出、长时间pending、被替换风险'
        ),
        TransactionLifecycleStage(
            lifecycle_type='web3_chain',
            stage_name='交易打包',
            stage_order=5,
            description='矿工选择内存池中的交易，打包进新的区块',
            key_concepts='矿工、区块gas limit、交易选择策略、区块构建',
            involved_tables='blocks, transactions, miner_rewards',
            data_flow='矿工选择交易 → 构建区块 → 工作量证明/权益证明',
            test_focus='交易优先级、区块容量、矿工激励机制',
            common_issues='交易未被选中、区块gas耗尽、共识延迟'
        ),
        TransactionLifecycleStage(
            lifecycle_type='web3_chain',
            stage_name='区块传播与验证',
            stage_order=6,
            description='新区块在网络中传播，其他节点验证区块有效性',
            key_concepts='区块传播、状态验证、共识确认、叔块/孤块',
            involved_tables='blocks, network_nodes, consensus_state',
            data_flow='新区块 → 网络传播 → 节点验证 → 状态更新',
            test_focus='传播延迟、验证正确性、分叉处理',
            common_issues='分叉、双花、重组风险'
        ),
        TransactionLifecycleStage(
            lifecycle_type='web3_chain',
            stage_name='交易确认',
            stage_order=7,
            description='随着后续区块的生成，交易获得确认数增加',
            key_concepts='确认数、区块确认、最终性、概率最终性',
            involved_tables='transactions, blocks, confirmation_tracker',
            data_flow='每增加一个区块 → 确认数+1 → 达到安全阈值',
            test_focus='确认数阈值、重组概率、最终性保证',
            common_issues='确认数不足、重组回滚、最终性延迟'
        )
    ]
    
    for s in web3_transaction_lifecycle_stages:
        existing = TransactionLifecycleStage.query.filter_by(
            lifecycle_type=s.lifecycle_type,
            stage_name=s.stage_name
        ).first()
        if not existing:
            db.session.add(s)
        else:
            sync_existing_record(existing, s)
    
    cex_contract_lifecycle_stages = [
        TransactionLifecycleStage(
            lifecycle_type='cex_contract',
            stage_name='开仓准备',
            stage_order=1,
            description='用户在CEX开立合约仓位前的准备阶段，包括选择交易对、设置杠杆倍数、选择保证金模式等',
            key_concepts='交易对选择、杠杆倍数、保证金模式、逐仓/全仓、合约类型',
            involved_tables='user_accounts, contract_settings, trading_pairs',
            data_flow='用户选择交易对 → 设置杠杆倍数 → 选择保证金模式 → 确认开仓参数',
            test_focus='杠杆倍数限制、保证金模式切换、交易对状态检查、风险提示显示',
            common_issues='杠杆倍数超出限制、保证金模式切换失败、交易对已停牌'
        ),
        TransactionLifecycleStage(
            lifecycle_type='cex_contract',
            stage_name='订单创建与保证金冻结',
            stage_order=2,
            description='用户创建合约订单，系统计算所需保证金并冻结用户账户余额',
            key_concepts='初始保证金、维持保证金、开仓价格、订单类型、数量',
            involved_tables='user_accounts, orders, margin_records, frozen_balances',
            data_flow='用户输入订单参数 → 系统计算所需保证金 → 检查账户余额 → 冻结保证金 → 创建订单',
            test_focus='保证金计算准确性、余额不足处理、部分成交保证金计算、保证金冻结/解冻时机',
            common_issues='保证金计算错误、余额不足但订单创建成功、冻结金额不正确'
        ),
        TransactionLifecycleStage(
            lifecycle_type='cex_contract',
            stage_name='撮合与开仓',
            stage_order=3,
            description='合约订单进入撮合引擎，与对手方订单匹配成交，成功后开立合约仓位',
            key_concepts='价格时间优先、撮合成交、开仓均价、持仓数量、未实现盈亏',
            involved_tables='order_book, trades, contract_positions, user_accounts',
            data_flow='订单进入撮合引擎 → 价格时间优先匹配 → 撮合成交 → 创建/更新持仓 → 更新订单状态',
            test_focus='撮合算法正确性、部分成交处理、开仓均价计算、持仓数量更新、成交记录创建',
            common_issues='撮合顺序错误、部分成交逻辑错误、开仓均价计算错误'
        ),
        TransactionLifecycleStage(
            lifecycle_type='cex_contract',
            stage_name='持仓管理',
            stage_order=4,
            description='用户持有合约仓位期间的管理，包括未实现盈亏计算、标记价格更新、保证金率监控等',
            key_concepts='标记价格、未实现盈亏、保证金率、维持保证金、风险预警',
            involved_tables='contract_positions, mark_prices, user_accounts, risk_alerts',
            data_flow='标记价格更新 → 计算未实现盈亏 → 更新账户权益 → 计算保证金率 → 风险预警检查',
            test_focus='标记价格获取、未实现盈亏计算、保证金率计算、风险预警触发、全仓/逐仓模式差异',
            common_issues='未实现盈亏计算错误、保证金率计算错误、风险预警未触发'
        ),
        TransactionLifecycleStage(
            lifecycle_type='cex_contract',
            stage_name='资金费用结算',
            stage_order=5,
            description='永续合约每8小时进行一次资金费用结算，多空双方根据资金费率互相支付费用',
            key_concepts='资金费率、溢价指数、资金费用时间点、多空支付方向',
            involved_tables='funding_fees, contract_positions, user_accounts, funding_rate_history',
            data_flow='计算资金费率 → 检查持仓越过资金费用时间点 → 计算应付/应收资金费用 → 更新账户余额 → 记录资金费用',
            test_focus='资金费率计算、资金费用收取/支付、时间点判断、历史记录、资金费率为负的情况',
            common_issues='资金费率计算错误、资金费用收取方向错误、未持有仓位却被收取费用'
        ),
        TransactionLifecycleStage(
            lifecycle_type='cex_contract',
            stage_name='平仓与结算',
            stage_order=6,
            description='用户手动平仓或被强制平仓，系统计算实现盈亏并结算，更新账户余额',
            key_concepts='平仓价格、实现盈亏、结算、平仓手续费、强制平仓',
            involved_tables='contract_positions, orders, trades, user_accounts, settlement_records',
            data_flow='用户创建平仓订单 → 撮合成交 → 计算实现盈亏 → 扣除手续费 → 更新账户余额 → 关闭/更新持仓',
            test_focus='平仓撮合逻辑、实现盈亏计算、手续费扣除、强制平仓触发、部分平仓处理',
            common_issues='实现盈亏计算错误、强制平仓触发条件错误、平仓后持仓未正确关闭'
        ),
        TransactionLifecycleStage(
            lifecycle_type='cex_contract',
            stage_name='强制平仓',
            stage_order=7,
            description='当用户保证金率低于维持保证金率时，系统触发强制平仓，接管用户仓位并在市场上平仓',
            key_concepts='强制平仓价格、维持保证金率、保险基金、自动减仓、穿仓分摊',
            involved_tables='contract_positions, liquidation_records, insurance_fund, user_accounts',
            data_flow='监控保证金率 → 低于维持保证金率 → 触发强平 → 接管仓位 → 市场平仓 → 使用保险基金弥补亏损 → 如有剩余返还用户',
            test_focus='强平触发条件、强平价格计算、保险基金使用、自动减仓逻辑、穿仓分摊',
            common_issues='强平触发过早/过晚、强平价格计算错误、保险基金使用不当'
        )
    ]
    
    for s in cex_contract_lifecycle_stages:
        existing = TransactionLifecycleStage.query.filter_by(
            lifecycle_type=s.lifecycle_type,
            stage_name=s.stage_name
        ).first()
        if not existing:
            db.session.add(s)
        else:
            sync_existing_record(existing, s)
    
    spot_trading_lifecycle_stages = [
        TransactionLifecycleStage(
            lifecycle_type='spot_trading',
            stage_name='订单创建',
            stage_order=1,
            description='用户在CEX创建币币交易订单，选择交易对、订单类型、价格、数量等参数',
            key_concepts='交易对、订单类型、限价单、市价单、止损单、订单有效期',
            involved_tables='user_accounts, orders, trading_pairs',
            data_flow='用户选择交易对 → 选择订单类型 → 输入价格/数量 → 确认订单 → 系统校验参数',
            test_focus='交易对状态检查、订单类型支持、价格精度校验、数量精度校验、订单有效期设置',
            common_issues='交易对已停牌但仍可下单、价格精度处理错误、数量精度处理错误'
        ),
        TransactionLifecycleStage(
            lifecycle_type='spot_trading',
            stage_name='余额冻结',
            stage_order=2,
            description='系统根据订单类型冻结用户账户中相应的资产，确保订单有足够的资金可以成交',
            key_concepts='可用余额、冻结余额、冻结金额计算、部分成交冻结',
            involved_tables='user_accounts, frozen_balances, account_journals',
            data_flow='检查可用余额 → 计算所需冻结金额 → 冻结余额 → 记录账户流水 → 更新订单状态',
            test_focus='余额不足处理、冻结金额计算、部分成交后冻结金额调整、冻结/解冻时机',
            common_issues='余额不足但订单创建成功、冻结金额计算错误、解冻不及时'
        ),
        TransactionLifecycleStage(
            lifecycle_type='spot_trading',
            stage_name='订单簿入队',
            stage_order=3,
            description='订单进入订单簿等待撮合，限价单如果不能立即成交则进入订单簿，市价单立即撮合',
            key_concepts='订单簿、买一价、卖一价、深度、价格档位',
            involved_tables='order_book, orders',
            data_flow='判断是否可立即成交 → 限价单：价格不优则进入订单簿 → 市价单：立即撮合 → 更新订单状态',
            test_focus='订单簿数据结构、价格档位维护、订单排序、订单簿快照、深度计算',
            common_issues='订单排序错误、订单簿深度计算错误、订单状态更新不及时'
        ),
        TransactionLifecycleStage(
            lifecycle_type='spot_trading',
            stage_name='交易撮合',
            stage_order=4,
            description='撮合引擎按照价格优先、时间优先的原则，匹配买单和卖单，生成成交记录',
            key_concepts='价格优先、时间优先、撮合算法、成交价格、部分成交',
            involved_tables='order_book, orders, trades',
            data_flow='新订单进入 → 价格时间优先匹配对手方 → 计算成交价格和数量 → 生成成交记录 → 更新订单状态 → 处理剩余数量',
            test_focus='撮合顺序、成交价格确定、部分成交处理、多笔成交记录、成交推送',
            common_issues='撮合顺序错误、成交价格计算错误、部分成交逻辑错误'
        ),
        TransactionLifecycleStage(
            lifecycle_type='spot_trading',
            stage_name='成交结算',
            stage_order=5,
            description='订单成交后，系统进行资金结算，更新买卖双方的账户余额，扣除手续费',
            key_concepts='成交金额、手续费、Maker/Taker、账户流水、结算确认',
            involved_tables='trades, user_accounts, account_journals, fee_records',
            data_flow='获取成交信息 → 计算成交金额 → 计算手续费 → 更新买方账户 → 更新卖方账户 → 记录账户流水 → 记录手续费',
            test_focus='成交金额计算、手续费计算、账户余额更新、Maker/Taker区分、流水记录完整性',
            common_issues='成交金额计算错误、手续费扣除错误、余额更新不一致'
        ),
        TransactionLifecycleStage(
            lifecycle_type='spot_trading',
            stage_name='订单完成',
            stage_order=6,
            description='订单全部成交、部分成交后撤单、或用户主动撤单，订单生命周期结束',
            key_concepts='全部成交、部分成交、撤单、订单状态、冻结金额解冻',
            involved_tables='orders, user_accounts, frozen_balances',
            data_flow='检查订单状态 → 全部成交：标记为已完成 → 部分成交：用户可撤单 → 用户撤单：解冻剩余冻结金额 → 标记订单状态',
            test_focus='撤单权限检查、部分成交后撤单、冻结金额解冻、订单状态流转、撤单后撮合停止',
            common_issues='撤单后订单仍被撮合、冻结金额未完全解冻、订单状态流转错误'
        ),
        TransactionLifecycleStage(
            lifecycle_type='spot_trading',
            stage_name='订单取消',
            stage_order=7,
            description='用户主动取消未成交或部分成交的订单，系统解冻冻结的余额并更新订单状态',
            key_concepts='主动撤单、撤单权限、部分成交撤单、冻结解冻',
            involved_tables='orders, user_accounts, frozen_balances, cancel_records',
            data_flow='用户请求撤单 → 检查订单状态 → 检查撤单权限 → 从订单簿移除订单 → 解冻冻结金额 → 更新订单状态 → 记录撤单日志',
            test_focus='撤单权限、部分成交撤单处理、冻结金额解冻、订单簿更新、撤单后成交处理',
            common_issues='撤单后仍有成交、冻结金额未正确解冻、订单簿未正确更新'
        )
    ]
    
    for s in spot_trading_lifecycle_stages:
        existing = TransactionLifecycleStage.query.filter_by(
            lifecycle_type=s.lifecycle_type,
            stage_name=s.stage_name
        ).first()
        if not existing:
            db.session.add(s)
        else:
            sync_existing_record(existing, s)
    
    contract_types = [
        ContractType(
            name='perpetual',
            display_name='永续合约',
            description='永续合约是一种没有到期日的期货合约，用户可以长期持有。通过资金费率机制使合约价格锚定现货价格，是目前最主流的合约类型。',
            key_features='无到期日、资金费率机制、锚定现货价格、可长期持有、支持多空双向',
            settlement_type='现金结算',
            margin_mode='逐仓/全仓',
            risk_characteristics='资金费率风险、高杠杆风险、强平风险、价格波动风险',
            test_scenarios='1. 开仓/平仓测试\n2. 资金费率收取测试\n3. 强制平仓测试\n4. 标记价格更新测试\n5. 保证金率计算测试',
            sort_order=1
        ),
        ContractType(
            name='delivery_future',
            display_name='交割合约',
            description='交割合约有固定的到期日，到期时会按照约定价格进行实物交割或现金交割。分为当周、次周、当季、次季等不同周期。',
            key_features='固定到期日、交割结算、基差交易、周期选择、到期强制平仓',
            settlement_type='实物交割/现金交割',
            margin_mode='逐仓/全仓',
            risk_characteristics='到期风险、基差风险、交割风险、流动性风险',
            test_scenarios='1. 交割流程测试\n2. 到期结算测试\n3. 交割价格计算测试\n4. 展期操作测试\n5. 不同周期合约切换',
            sort_order=2
        ),
        ContractType(
            name='inverse',
            display_name='反向合约',
            description='反向合约使用加密货币作为保证金和结算货币，盈亏以标的货币计算。例如BTC反向合约，用户用BTC作为保证金，盈亏也以BTC计算。',
            key_features='标的货币保证金、盈亏反向计算、非线性盈亏、适合套期保值',
            settlement_type='标的货币结算',
            margin_mode='逐仓/全仓',
            risk_characteristics='非线性盈亏风险、保证金价值波动、复杂计算风险',
            test_scenarios='1. 保证金计算测试\n2. 盈亏计算测试\n3. 强平价格计算测试\n4. 与正向合约对比测试\n5. 套期保值场景测试',
            sort_order=3
        ),
        ContractType(
            name='linear',
            display_name='正向合约',
            description='正向合约使用稳定币（如USDT）作为保证金和结算货币，盈亏以稳定币计算。是目前最主流的合约类型，用户更容易理解。',
            key_features='稳定币保证金、线性盈亏、USDT本位、易于理解、适合新手',
            settlement_type='稳定币结算',
            margin_mode='逐仓/全仓',
            risk_characteristics='线性盈亏、稳定币汇率风险、强平风险',
            test_scenarios='1. 开仓保证金计算测试\n2. 实现盈亏计算测试\n3. 未实现盈亏计算测试\n4. 强平触发测试\n5. 与反向合约对比测试',
            sort_order=4
        ),
        ContractType(
            name='option',
            display_name='期权合约',
            description='期权合约赋予买方在未来某个时间以约定价格买入或卖出标的资产的权利，但不是义务。分为看涨期权和看跌期权。',
            key_features='权利金、行权价格、到期日、看涨/看跌、买方/卖方',
            settlement_type='现金结算/实物交割',
            margin_mode='卖方需要保证金',
            risk_characteristics='时间价值衰减、波动率风险、无限损失风险（卖方）、有限损失（买方）',
            test_scenarios='1. 期权定价测试\n2. 权利金计算测试\n3. 行权流程测试\n4. 到期结算测试\n5. 波动率影响测试',
            sort_order=5
        ),
        ContractType(
            name='leveraged_token',
            display_name='杠杆代币',
            description='杠杆代币是一种带杠杆的代币产品，通过自动再平衡机制维持目标杠杆倍数。用户无需管理保证金和强平，操作简单。',
            key_features='自动再平衡、目标杠杆、无保证金管理、无强平风险、每日复利',
            settlement_type='代币净值',
            margin_mode='无保证金',
            risk_characteristics='杠杆衰减、复利风险、长期持有风险、净值偏离风险',
            test_scenarios='1. 净值计算测试\n2. 再平衡机制测试\n3. 杠杆倍数维护测试\n4. 申购赎回测试\n5. 与传统合约对比测试',
            sort_order=6
        )
    ]
    
    for ct in contract_types:
        existing = ContractType.query.filter_by(name=ct.name).first()
        if not existing:
            db.session.add(ct)
        else:
            sync_existing_record(existing, ct)
    
    table_relationships = [
        TableRelationship(
            module='spot_trading',
            relationship_name='订单创建流程',
            description='用户创建币币交易订单时的数据流转过程',
            source_table='user_accounts',
            target_table='orders',
            relationship_type='1:N',
            key_fields='user_id → orders.user_id, balance → frozen_balance',
            data_flow_diagram='用户账户 → 余额冻结 → 创建订单 → 订单簿',
            test_scenarios='1. 余额充足下单\n2. 余额不足下单\n3. 部分成交\n4. 订单取消\n5. 并发下单'
        ),
        TableRelationship(
            module='spot_trading',
            relationship_name='交易撮合流程',
            description='订单簿中买单和卖单的撮合匹配过程',
            source_table='order_book',
            target_table='trades',
            relationship_type='N:M',
            key_fields='buy_order_id, sell_order_id → trades.*',
            data_flow_diagram='订单簿 → 撮合引擎 → 成交记录 → 账户更新',
            test_scenarios='1. 价格优先撮合\n2. 时间优先撮合\n3. 部分成交\n4. 全部成交\n5. 订单过期'
        ),
        TableRelationship(
            module='spot_trading',
            relationship_name='成交后账户更新',
            description='交易成交后用户账户余额的更新流程',
            source_table='trades',
            target_table='user_accounts',
            relationship_type='N:1',
            key_fields='trade_id → account_journals → balance',
            data_flow_diagram='成交记录 → 账户流水 → 可用余额/冻结余额更新',
            test_scenarios='1. 买入成交\n2. 卖出成交\n3. 手续费扣除\n4. 回滚场景\n5. 并发更新'
        ),
        TableRelationship(
            module='contract_trading',
            relationship_name='合约开仓流程',
            description='用户开立合约仓位的完整数据流程',
            source_table='user_accounts',
            target_table='contract_positions',
            relationship_type='1:N',
            key_fields='user_id, margin → position.*',
            data_flow_diagram='可用保证金 → 冻结保证金 → 创建订单 → 撮合成交 → 开仓',
            test_scenarios='1. 逐仓开仓\n2. 全仓开仓\n3. 杠杆倍数设置\n4. 保证金不足\n5. 市价/限价开仓'
        ),
        TableRelationship(
            module='contract_trading',
            relationship_name='持仓管理流程',
            description='合约持仓期间的资金费用、标记价格更新等',
            source_table='contract_positions',
            target_table='funding_fees',
            relationship_type='1:N',
            key_fields='position_id → funding_fee.*',
            data_flow_diagram='标记价格更新 → 未实现盈亏计算 → 资金费用结算 → 保证金检查',
            test_scenarios='1. 未实现盈亏计算\n2. 资金费用收取\n3. 标记价格更新\n4. 保证金预警\n5. 强制平仓触发'
        ),
        TableRelationship(
            module='contract_trading',
            relationship_name='合约平仓流程',
            description='用户平仓或强制平仓的数据流程',
            source_table='contract_positions',
            target_table='contract_trades',
            relationship_type='1:1',
            key_fields='position_id → realized_pnl, close_price',
            data_flow_diagram='平仓订单 → 撮合成交 → 实现盈亏计算 → 保证金返还 → 持仓关闭',
            test_scenarios='1. 手动平仓\n2. 强制平仓\n3. 部分平仓\n4. 盈亏结算\n5. 手续费计算'
        ),
        TableRelationship(
            module='cex',
            relationship_name='充币流程',
            description='用户从外部地址向CEX充值加密货币的流程',
            source_table='blockchain_transactions',
            target_table='user_accounts',
            relationship_type='N:1',
            key_fields='tx_hash, address → deposit_record → balance',
            data_flow_diagram='用户地址 → 区块确认 → 入账审核 → 余额增加',
            test_scenarios='1. 正常充币\n2. 小额充币\n3. 异常地址\n4. 区块重组\n5. 审核拒绝'
        ),
        TableRelationship(
            module='cex',
            relationship_name='提币流程',
            description='用户从CEX提取加密货币到外部地址的流程',
            source_table='user_accounts',
            target_table='withdraw_records',
            relationship_type='1:N',
            key_fields='user_id, balance → withdraw_request → blockchain_tx',
            data_flow_diagram='余额冻结 → 风控审核 → 人工审核 → 链上广播 → 到账确认',
            test_scenarios='1. 正常提币\n2. 提币限额\n3. 风控拦截\n4. 审核拒绝\n5. 链上失败'
        )
    ]
    
    for r in table_relationships:
        existing = TableRelationship.query.filter_by(
            module=r.module, 
            relationship_name=r.relationship_name
        ).first()
        if not existing:
            db.session.add(r)
        else:
            sync_existing_record(existing, r)
    
    performance_test_cases = [
        PerformanceTestCase(
            category='并发测试',
            title='高并发下单性能测试',
            description='测试系统在高并发场景下的订单处理能力',
            test_objective='验证系统在10000 TPS下的稳定性和响应时间',
            test_environment='生产级配置：4核8G，Redis集群，MySQL主从，消息队列',
            test_steps='1. 准备测试数据：1000个用户账户，充足余额\n2. 设置并发数：从100逐步增加到10000\n3. 监控指标：TPS、响应时间、错误率\n4. 持续压测30分钟\n5. 分析性能瓶颈',
            metrics_to_collect='TPS (每秒事务数)\n平均响应时间\nP95/P99响应时间\n错误率\nCPU/内存使用率\n数据库连接数\n队列积压',
            acceptance_criteria='TPS >= 目标值的90%\n平均响应时间 < 200ms\nP99响应时间 < 1s\n错误率 < 0.1%\n无内存泄漏',
            test_data_requirements='用户数据：1000个活跃用户\n账户余额：每个用户充足\n交易对：BTC/USDT, ETH/USDT\n价格波动：模拟真实市场波动',
            tools_used='JMeter / Locust\nPrometheus + Grafana\nNew Relic / Datadog\n数据库慢查询日志\n应用性能监控(APM)',
            common_pitfalls='1. 测试数据不足导致缓存命中失真\n2. 并发数设置不合理\n3. 忽略网络延迟影响\n4. 不清理测试数据影响后续测试\n5. 只关注TPS忽略错误率',
            optimization_strategies='1. 数据库优化：索引优化、读写分离、分库分表\n2. 缓存优化：Redis热点数据、本地缓存\n3. 异步处理：消息队列解耦\n4. 连接池优化：合理设置连接数\n5. 水平扩展：多节点部署\n6. 代码优化：减少数据库交互、批量操作',
            monitoring_points='应用层：QPS、响应时间、错误率\n数据库层：连接数、慢查询、锁等待\n缓存层：命中率、内存使用、过期key\n消息队列：积压数、消费速度\n基础设施：CPU、内存、网络、磁盘IO'
        ),
        PerformanceTestCase(
            category='压力测试',
            title='撮合引擎极限压力测试',
            description='测试交易撮合引擎在极限压力下的表现',
            test_objective='找到撮合引擎的性能瓶颈和极限处理能力',
            test_environment='撮合引擎独立部署，专用服务器，低延迟网络',
            test_steps='1. 预热阶段：逐步增加负载\n2. 压力阶段：持续极限压测\n3. 稳定性阶段：长时间运行观察\n4. 恢复阶段：停止压测观察恢复能力',
            metrics_to_collect='撮合吞吐量\n订单延迟\n内存使用趋势\nGC停顿时间\nCPU使用率\n订单队列积压',
            acceptance_criteria='无OOM错误\n无数据丢失\n系统可自动恢复\n延迟在可接受范围内',
            test_data_requirements='大量订单数据：不同价格、不同数量\n模拟真实订单分布\n包含市价单、限价单、条件单',
            tools_used='Golang基准测试\npprof性能分析\n火焰图分析\n内存dump分析',
            common_pitfalls='1. 忽略GC影响\n2. 不考虑内存泄漏\n3. 只测短时间不测长时间稳定性\n4. 忽略冷启动影响',
            optimization_strategies='1. 算法优化：价格时间优先算法优化\n2. 数据结构：使用更高效的数据结构\n3. 内存管理：对象池、避免频繁GC\n4. 并发优化：读写锁、无锁数据结构\n5. 批量处理：减少锁竞争',
            monitoring_points='堆内存使用\nGC次数和时长\n协程数量\n锁竞争情况\nCPU使用率分布'
        ),
        PerformanceTestCase(
            category='稳定性测试',
            title='7*24小时稳定性测试',
            description='长时间运行测试，验证系统稳定性',
            test_objective='验证系统在持续运行下无内存泄漏、无性能退化',
            test_environment='与生产环境一致的配置',
            test_steps='1. 系统启动，预热30分钟\n2. 持续施加70%目标负载\n3. 每天执行一次峰值负载测试\n4. 监控所有关键指标\n5. 7天后分析结果',
            metrics_to_collect='内存使用趋势\nCPU使用趋势\n句柄/文件描述符\n连接数趋势\n错误日志\n重启次数',
            acceptance_criteria='内存无持续增长\nCPU使用率稳定\n无服务重启\n错误率在阈值内',
            test_data_requirements='持续生成新数据\n定期清理过期数据\n模拟真实业务场景',
            tools_used='监控告警系统\n日志收集分析\n自动化巡检脚本',
            common_pitfalls='1. 测试期间不做任何干预\n2. 忽略资源耗尽问题\n3. 不分析慢查询累积效应',
            optimization_strategies='1. 定时任务优化\n2. 数据归档策略\n3. 连接池管理\n4. 缓存过期策略\n5. 错误重试机制',
            monitoring_points='所有基础设施指标\n应用健康检查\n业务健康指标\n错误日志监控'
        )
    ]
    
    for p in performance_test_cases:
        existing = PerformanceTestCase.query.filter_by(title=p.title).first()
        if not existing:
            db.session.add(p)
        else:
            sync_existing_record(existing, p)
    
    advanced_blockchain_tests = [
        BlockChainTestCases(
            module='web3_chain',
            category='交易生命周期',
            sub_category='交易构造',
            title='Nonce管理正确性测试',
            description='测试交易nonce字段的生成和管理逻辑，确保交易顺序性',
            preconditions='1. 用户账户有ETH余额\n2. 账户nonce从0开始\n3. 网络正常连接',
            test_data='测试账户地址、私钥、充足的ETH余额',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 查询账户当前nonce值\n2. 构造第一笔交易，使用查询到的nonce\n3. 构造第二笔交易，使用nonce+1\n4. 构造第三笔交易，使用nonce+3（跳过一个nonce）\n5. 广播所有交易\n6. 观察交易状态和nonce变化',
            expected_result='1. 第一笔交易成功确认\n2. 第二笔交易成功确认\n3. 第三笔交易长时间pending，直到nonce+2的交易被处理\n4. 账户nonce正确递增',
            actual_tool='Web3.py + Goerli测试网',
            notes='实际项目经验：\n\n1. **Nonce必须严格递增**：如果跳过某个nonce，后续所有交易都会卡住。这是最常见的问题之一。\n\n2. **并发交易处理**：同一账户同时发送多笔交易时，必须正确管理nonce。建议使用队列或锁机制。\n\n3. **Pending交易替换**：可以使用相同nonce但更高gasPrice的交易替换pending中的交易（RBF - Replace-By-Fee）。\n\n4. **交易取消**：实际上无法"取消"已广播的交易，只能用更高gasPrice发送一笔0值交易到自己地址来"覆盖"。\n\n5. **Nonce查询时机**：应该使用pending状态的nonce，而不是latest状态。在web3.py中使用get_transaction_count(address, "pending")。\n\n6. **RPC 与多服务发送**：经负载均衡时可能打到不同节点、mempool 视图不一致，需在集成环境对「发交易 + 查 pending」做联合压测。\n\n**关联实践项目**：JSON-RPC 链上查询与网关服务测试。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='交易生命周期',
            sub_category='Gas管理',
            title='Gas参数设置合理性测试',
            description='测试gasPrice和gasLimit的设置对交易的影响',
            preconditions='1. 测试账户有ETH余额\n2. 连接到测试网或主网\n3. 了解当前网络gas情况',
            test_data='测试账户、目标合约地址、测试函数',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 使用eth_estimateGas估算gasLimit\n2. 设置gasPrice为网络平均值\n3. 发送交易观察结果\n4. 设置gasPrice过低（远低于网络平均）\n5. 发送交易观察结果\n6. 设置gasLimit过低（低于估算值）\n7. 发送交易观察结果',
            expected_result='1. 合理gas设置：交易成功确认\n2. gasPrice过低：长时间pending或失败\n3. gasLimit过低：交易失败（out of gas），已消耗的gas不返还',
            actual_tool='Ethers.js + Hardhat Network',
            notes='实际项目经验：\n\n1. **Gas估算不是100%准确**：estimateGas可能因为状态变化而不准确，建议设置10-20%的缓冲。\n\n2. **Gas Price动态调整**：使用gas oracle或EIP-1559的maxPriorityFee/maxFee来动态设置。\n\n3. **EIP-1559 vs Legacy**：EIP-1559交易更高效，但需要确保节点支持。建议提供两种模式。\n\n4. **Out of Gas的危害**：不仅交易失败，已消耗的gas也不会返还。这会导致用户损失资金。\n\n5. **Gas refunds**：删除存储会有gas返还，但有上限（最多交易gas的一半）。不能以此作为盈利手段。\n\n6. **费用类接口 SLA**：eth_feeHistory、eth_maxPriorityFeePerGas 等与钱包联动，需在节点升级后做回归。\n\n**关联实践项目**：JSON-RPC 链上查询与网关服务测试；Hardhat/本地分叉回归可结合「测试用例模版化系统」。'
        ),
        BlockChainTestCases(
            module='web3_chain',
            category='交易生命周期',
            sub_category='交易确认',
            title='区块确认数与最终性测试',
            description='测试交易确认数的意义和双花风险',
            preconditions='1. 私有测试网环境\n2. 控制多个节点的算力\n3. 能够分叉网络',
            test_data='测试账户、测试代币、足够算力',
            priority='P1',
            test_type='安全测试',
            test_steps='1. 在链A上发送交易TX1\n2. 等待1个确认\n3. 在分叉链B上不包含TX1继续挖矿\n4. 链B超过链A长度\n5. 观察TX1的状态\n6. 测试不同确认数下的安全性',
            expected_result='1. 1个确认后交易可能被回滚\n2. 6个确认后安全性大幅提高\n3. 更长的确认数意味着更低的重组风险',
            actual_tool='Bitcoin RegTest + Ethereum Testnet',
            notes='实际项目经验：\n\n1. **确认数不是绝对安全**：即使100个确认，理论上仍有重组可能，只是概率极低。\n\n2. **不同链的确认要求**：比特币建议6个确认，以太坊建议12-20个确认（PoS后最终性更快）。\n\n3. **交易所的确认策略**：不同交易所对不同币种有不同确认要求，高价值币种要求更多确认。\n\n4. **Finality（最终性）**：PoS链（如以太坊）有更强的最终性保证，Casper FFG确保区块最终确定后无法回滚。\n\n5. **重组监控**：生产环境应该监控区块重组，一旦发生深度重组（如3个以上区块）应立即告警。\n\n6. **与节点高度对齐**：内部入账、索引与对账应以「可配置确认数 + finalized/safe 标签（若节点暴露）」为准，避免与落后节点 RPC 判重不一致。\n\n**关联实践项目**：公链节点部署与同步验证；JSON-RPC 链上查询与网关服务测试。'
        ),
        BlockChainTestCases(
            module='cex',
            category='注册登录',
            sub_category='用户注册',
            title='CEX用户注册流程测试',
            description='测试中心化交易所的用户注册完整流程',
            preconditions='1. 注册页面可访问\n2. 邮件/SMS服务正常\n3. 数据库可连接',
            test_data='有效邮箱、手机号、密码（符合复杂度要求）',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 访问注册页面\n2. 输入邮箱/手机号\n3. 输入密码和确认密码\n4. 获取并输入验证码\n5. 勾选用户协议\n6. 点击注册\n7. 验证邮件/短信\n8. 登录验证',
            expected_result='1. 验证码正确发送\n2. 密码验证通过\n3. 注册成功\n4. 验证成功后可正常登录\n5. 重复注册同一邮箱被拒绝',
            actual_tool='Selenium + Postman',
            notes='实际项目经验：\n\n1. **密码安全存储**：必须使用bcrypt/argon2等慢哈希算法，禁止明文或简单MD5存储。\n\n2. **验证码防暴力破解**：限制发送频率（如60秒一次），限制每日次数，使用图形验证码前置。\n\n3. **用户协议合规**：必须记录用户同意的协议版本号和时间，用于法律合规。\n\n4. **注册即风控**：注册阶段就要开始风控，检测异常IP、设备指纹、批量注册行为。\n\n5. **数据隔离**：用户敏感数据（密码哈希、密钥）应该加密存储，最小权限访问。'
        ),
        BlockChainTestCases(
            module='cex',
            category='用户资产',
            sub_category='账户余额',
            title='用户余额准确性测试',
            description='测试用户账户余额的计算和更新逻辑',
            preconditions='1. 用户已登录\n2. 账户有初始余额\n3. 无进行中的交易',
            test_data='测试账户、测试币种、初始余额',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 查询当前可用余额和冻结余额\n2. 发起一笔买入订单，冻结部分余额\n3. 查询余额变化\n4. 订单部分成交\n5. 查询余额变化\n6. 订单完全成交\n7. 查询最终余额',
            expected_result='1. 可用余额 = 总余额 - 冻结余额\n2. 下单时：可用余额减少，冻结余额增加\n3. 成交时：冻结余额减少，对应资产增加\n4. 所有计算精确到最小单位（如聪、wei）',
            actual_tool='JMeter + 数据库查询',
            notes='实际项目经验：\n\n1. **余额计算必须在数据库层面**：不能依赖应用层计算，必须使用数据库事务和锁（如SELECT FOR UPDATE）。\n\n2. **精度问题**：加密货币通常有很多小数位（比特币8位，以太坊18位），必须使用精确数值类型（Decimal或BigInteger），禁止浮点运算。\n\n3. **余额更新必须有流水**：每一次余额变动都要有对应的账户流水，用于对账和审计。\n\n4. **并发更新处理**：同一用户并发操作时，必须使用数据库锁或分布式锁，防止超卖。\n\n5. **对账机制**：每日进行账户余额对账，确保余额=初始+入账-出账，发现差异立即告警。'
        ),
        BlockChainTestCases(
            module='cex',
            category='充提币',
            sub_category='充币',
            title='CEX充币流程端到端测试',
            description='测试用户从外部地址向CEX充值的完整流程',
            preconditions='1. 用户已完成KYC\n2. 已生成充币地址\n3. 外部钱包有余额',
            test_data='测试币种、充币数量、外部钱包',
            priority='P0',
            test_type='端到端测试',
            test_steps='1. 在CEX获取充币地址\n2. 从外部钱包向该地址转账\n3. 等待区块链确认\n4. 观察CEX充币记录状态\n5. 检查账户余额变化\n6. 验证入账通知',
            expected_result='1. 区块确认后充币记录显示\n2. 达到确认数后自动入账\n3. 账户余额正确增加\n4. 用户收到通知',
            actual_tool='Hardhat + Web3.py + 后台管理系统',
            notes='实际项目经验：\n\n1. **确认数策略**：不同币种设置不同确认数。比特币通常6个确认，以太坊通常12-20个确认。\n\n2. **小额充币处理**：设置最小充币金额，低于该金额的充币可能不自动入账（或累积到一定金额）。\n\n3. **异常地址检测**：检测合约地址充币、黑名单地址、异常小额等风险情况。\n\n4. **区块重组处理**：必须监控区块链重组，如果已入账的交易被回滚，需要冻结用户资产并人工介入。\n\n5. **热钱包归集**：用户充币地址通常是观察钱包或热钱包，需要定期归集到冷钱包。'
        ),
        BlockChainTestCases(
            module='cex',
            category='充提币',
            sub_category='提币',
            title='CEX提币流程风控测试',
            description='测试提币流程中的各种风控拦截场景',
            preconditions='1. 用户已完成高级KYC\n2. 账户有充足余额\n3. 已绑定提币地址',
            test_data='提币金额、目标地址、风控触发条件',
            priority='P1',
            test_type='风控测试',
            test_steps='1. 正常提币测试\n2. 大额提币测试（超过阈值）\n3. 新地址首次提币\n4. 异常IP地址提币\n5. 异常设备提币\n6. 短时间多次提币',
            expected_result='1. 正常提币：通过审核或自动处理\n2. 大额提币：触发人工审核\n3. 新地址：需要邮件/短信确认\n4. 异常情况：风控拦截，需要验证或人工审核',
            actual_tool='Selenium + 风控后台',
            notes='实际项目经验：\n\n1. **提币风控分级**：\n   - 小额+白名单地址+常用设备：自动通过\n   - 中额+新地址：邮件确认\n   - 大额：人工审核\n   - 异常行为：直接拦截并告警\n\n2. **地址白名单**：建议用户添加提币地址白名单，白名单地址提币风险更低。\n\n3. **延迟到账策略**：对于高风险提币，可以设置延迟到账（如24小时），期间用户可以取消。\n\n4. **提币限制**：设置单日提币限额、单笔限额，超过限额需要更高级别的验证。\n\n5. **冷钱包管理**：大部分资金应该存储在冷钱包，热钱包只保留日常运营所需的小额资金。'
        ),
        BlockChainTestCases(
            module='cex',
            category='KYC',
            sub_category='身份认证',
            title='KYC等级与权限测试',
            description='测试不同KYC等级对应的功能权限',
            preconditions='1. 新注册用户\n2. KYC系统正常工作\n3. 测试用的身份材料',
            test_data='KYC等级1/2/3所需材料',
            priority='P1',
            test_type='功能测试',
            test_steps='1. 未认证用户：测试提币、交易等功能\n2. 完成KYC Level 1（基础认证）：测试权限变化\n3. 完成KYC Level 2（高级认证）：测试权限变化\n4. 完成KYC Level 3（企业认证）：测试权限变化\n5. 验证各等级的提币限额',
            expected_result='1. 未认证：可能无法提币或限额极低\n2. Level 1：基本功能，小额提币\n3. Level 2：完整功能，较高限额\n4. Level 3：企业级功能，最高限额',
            actual_tool='Selenium + 后台管理系统',
            notes='实际项目经验：\n\n1. **KYC合规要求**：不同司法管辖区有不同的KYC要求，必须合规运营。FATF旅行规则要求在某些情况下传输交易双方信息。\n\n2. **KYC等级设计**：\n   - Level 0：注册即拥有，可浏览、充值\n   - Level 1：邮箱验证+基础信息，可小额交易\n   - Level 2：身份验证+面部识别+地址证明，完整功能\n   - Level 3：企业认证，更高限额\n\n3. **活体检测**：高级KYC需要活体检测，防止使用照片/视频攻击。\n\n4. **数据保护**：KYC数据属于高度敏感数据，必须加密存储，严格控制访问权限，定期审计。\n\n5. **KYC重试机制**：用户KYC失败应该有合理的重试次数，超过次数需要人工审核。'
        ),
        BlockChainTestCases(
            module='cex',
            category='交易撮合',
            sub_category='订单簿',
            title='订单簿价格时间优先撮合测试',
            description='测试撮合引擎的价格优先、时间优先原则',
            preconditions='1. 交易对已开启\n2. 订单簿为空\n3. 测试账户有充足余额',
            test_data='多个限价单，不同价格不同时间',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 卖单A：价格100，数量1，时间最早\n2. 卖单B：价格99，数量1，时间次之\n3. 卖单C：价格100，数量1，时间最晚\n4. 买单：价格100，数量2\n5. 观察撮合结果',
            expected_result='1. 撮合顺序：首先是价格最低的卖单B（99）\n2. 然后是相同价格中时间最早的卖单A（100）\n3. 卖单C未被撮合（买单只剩1个数量，但价格时间都不优先）\n4. 成交价格：先99，后100',
            actual_tool='JMeter + 撮合引擎日志',
            notes='实际项目经验：\n\n1. **价格优先原则**：买入时价格高的优先，卖出时价格低的优先。\n\n2. **时间优先原则**：相同价格下，先挂单的优先成交。\n\n3. **撮合算法实现**：使用红黑树或跳表等数据结构维护订单簿，确保O(log n)的插入删除和O(1)的最优价格查询。\n\n4. **成交价格确定**：\n   - 市价单吃单：以对手方最优价格成交\n   - 限价单吃单：如果是买入，以卖一或更优价格成交；如果是卖出，以买一或更优价格成交\n\n5. **部分成交**：一个订单可能与多个对手方订单成交，形成多笔成交记录。'
        ),
        BlockChainTestCases(
            module='dex',
            category='钱包连接',
            sub_category='WalletConnect',
            title='DEX钱包连接兼容性测试',
            description='测试DEX支持的各种钱包连接方式',
            preconditions='1. DEX网页可访问\n2. 安装了MetaMask等钱包\n3. 测试网络配置正确',
            test_data='MetaMask、WalletConnect、Coinbase Wallet等',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 测试MetaMask浏览器扩展连接\n2. 测试WalletConnect二维码连接\n3. 测试Coinbase Wallet连接\n4. 测试移动端钱包App内浏览器\n5. 测试断开重连\n6. 测试切换网络',
            expected_result='1. 所有支持的钱包都能正常连接\n2. 连接后正确获取账户地址\n3. 网络切换正确识别\n4. 断开后状态正确更新',
            actual_tool='Selenium + MetaMask + 真机测试',
            notes='实际项目经验：\n\n1. **钱包连接库**：使用wagmi、web3-react或ethers.js等库，不要自己从零实现。\n\n2. **网络检测**：连接后必须检测用户当前网络，提示切换到正确的链（如以太坊主网、Polygon等）。\n\n3. **签名验证**：某些操作需要用户签名验证身份，注意签名消息的格式和安全性（EIP-4361 Sign-In with Ethereum）。\n\n4. **移动端适配**：移动端浏览器对钱包扩展支持有限，主要依赖WalletConnect协议。\n\n5. **链ID混淆**：不同链有不同的chainId，必须确保交易在正确的链上签名，防止重放攻击。'
        ),
        BlockChainTestCases(
            module='dex',
            category='交易撮合',
            sub_category='AMM模型',
            title='Uniswap V2 AMM定价模型测试',
            description='测试自动做市商模型的定价公式和滑点计算',
            preconditions='1. 部署Uniswap V2风格的合约\n2. 添加初始流动性\n3. 测试代币有足够余额',
            test_data='流动性池：10 ETH + 20000 USDT，测试交易数量',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 查询当前储备量：x=10 ETH, y=20000 USDT\n2. 计算恒定乘积k = x * y = 200000\n3. 测试用1 ETH买入USDT\n4. 验证新的储备量：x=11, y=200000/11≈18181.82\n5. 用户获得：20000 - 18181.82 = 1818.18 USDT\n6. 验证滑点计算',
            expected_result='1. 恒定乘积k保持不变（扣除手续费后）\n2. 交易后价格：1 ETH ≈ 1818 USDT（滑点导致价格变差）\n3. 初始价格：1 ETH = 2000 USDT\n4. 交易滑点：约9%',
            actual_tool='Hardhat + Ethers.js + Uniswap V2合约',
            notes='实际项目经验：\n\n1. **AMM核心公式**：x * y = k（恒定乘积），其中x和y是两种代币的储备量。\n\n2. **滑点**：交易越大，滑点越大。大额交易可能导致严重滑点，用户需要设置滑点容忍度。\n\n3. **无常损失**：为流动性提供者提供流动性时，如果代币价格相对发生变化，可能产生无常损失。\n\n4. **手续费**：通常收取0.3%的交易手续费，部分分配给流动性提供者，部分归协议所有。\n\n5. **价格预言机**：AMM的价格可以被操纵（闪电贷攻击），不能直接作为价格预言机使用，需要使用时间加权平均价格(TWAP)。'
        ),
        BlockChainTestCases(
            module='dex',
            category='用户资产',
            sub_category='流动性挖矿',
            title='DEX流动性添加/移除测试',
            description='测试用户向DEX添加和移除流动性的完整流程',
            preconditions='1. 用户持有两种代币\n2. 流动性池已创建\n3. 钱包已连接',
            test_data='测试代币数量、流动性池地址',
            priority='P1',
            test_type='功能测试',
            test_steps='1. 批准合约使用代币\n2. 添加流动性（两种代币按当前比例）\n3. 验证LP代币余额\n4. 验证流动性池储备量增加\n5. 移除部分流动性\n6. 验证代币返还\n7. 验证LP代币销毁',
            expected_result='1. 添加流动性成功，获得LP代币\n2. 流动性池储备量正确增加\n3. 移除流动性成功，获得对应比例的两种代币\n4. LP代币正确销毁',
            actual_tool='Hardhat + MetaMask',
            notes='实际项目经验：\n\n1. **代币批准**：ERC-20代币需要先approve合约才能使用，这是用户经常困惑的步骤。\n\n2. **价格比例**：添加流动性时，两种代币的价值必须按当前池内比例，否则交易可能被机器人抢跑（sandwich攻击）。\n\n3. **LP代币**：流动性提供者获得的LP代币代表其在池中的份额，可以在其他协议中进一步使用（如质押挖矿）。\n\n4. **滑点保护**：添加流动性时也需要设置滑点容忍度，防止交易被抢跑。\n\n5. **无常损失风险**：必须向用户充分提示无常损失风险，特别是在价格波动大的代币对。'
        ),
        BlockChainTestCases(
            module='spot_trading',
            category='交易原理',
            sub_category='订单类型',
            title='币币交易订单类型测试',
            description='测试限价单、市价单、条件单等订单类型的行为',
            preconditions='1. 交易对正常运行\n2. 订单簿有深度\n3. 测试账户有余额',
            test_data='各种订单类型的测试参数',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 限价买单测试：价格低于当前卖一\n2. 限价卖单测试：价格高于当前买一\n3. 市价买单测试：立即成交\n4. 市价卖单测试：立即成交\n5. 止损单测试：价格触发后转为市价单\n6. 冰山单测试：大额订单拆分显示',
            expected_result='1. 限价单：进入订单簿等待成交\n2. 市价单：立即以最优价格成交\n3. 止损单：未触发时不进入订单簿，触发后转为市价单\n4. 冰山单：只显示部分数量，成交后自动补充',
            actual_tool='JMeter + 撮合引擎验证',
            notes='实际项目经验：\n\n1. **限价单**：最常用的订单类型，用户指定价格，需要等待对手方。\n\n2. **市价单**：立即以当前最优价格成交，但在行情波动大时可能滑点严重。\n\n3. **止损单(Stop Loss)**：当价格达到触发价时，自动转为市价单。用于限制损失或锁定利润。\n\n4. **止盈单(Take Profit)**：价格达到目标价时自动卖出。\n\n5. **冰山单(Iceberg)**：大额订单只显示一部分，防止影响市场价格。\n\n6. **条件单复杂度**：条件单的触发条件、有效时间、执行价格等参数组合很多，测试时要覆盖所有组合。'
        ),
        BlockChainTestCases(
            module='spot_trading',
            category='交易原理',
            sub_category='成交计算',
            title='币币交易成交价格与数量计算测试',
            description='测试撮合时成交价格和数量的精确计算',
            preconditions='1. 撮合引擎正常工作\n2. 订单簿有测试数据\n3. 支持小数精度',
            test_data='卖单：价格100数量5，价格101数量10；买单：价格102数量12',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 订单簿状态：\n   卖一：100 USDT，数量5 BTC\n   卖二：101 USDT，数量10 BTC\n   买一：99 USDT，数量3 BTC\n\n2. 下买单：价格102，数量12 BTC\n\n3. 计算撮合结果：\n   - 先吃卖一5个，价格100\n   - 再吃卖二7个，价格101\n   - 卖二剩余3个\n\n4. 验证成交记录',
            expected_result='1. 总成交数量：12 BTC\n2. 成交价格：5个100，7个101\n3. 成交额：5*100 + 7*101 = 500 + 707 = 1207 USDT\n4. 平均成交价：1207 / 12 ≈ 100.5833 USDT\n5. 手续费：按成交额比例扣除',
            actual_tool='单元测试 + 数据库验证',
            notes='实际项目经验：\n\n1. **成交价确定**：\n   - 吃单时，以挂单方的价格成交\n   - 买入时，先吃价格最低的卖单\n   - 卖出时，先吃价格最高的买单\n\n2. **部分成交**：一个订单可能与多个对手方订单成交，每笔成交有独立的成交记录。\n\n3. **精度处理**：\n   - 不同交易对有不同的价格精度和数量精度\n   - 必须使用精确数值计算，四舍五入规则要明确\n   - 记录原始委托数量、成交数量、剩余数量\n\n4. **手续费计算**：\n   - 通常按成交额的一定比例收取\n   - 区分maker和taker手续费\n   - 支持平台币抵扣手续费\n\n5. **成交推送**：\n   - 成交后要实时推送给用户\n   - 更新订单状态\n   - 记录账户流水'
        ),
        BlockChainTestCases(
            module='contract_trading',
            category='合约原理',
            sub_category='开仓流程',
            title='合约开仓与保证金测试',
            description='测试合约开仓时的保证金计算和冻结',
            preconditions='1. 用户账户有USDT余额\n2. 合约交易对已开启\n3. 用户了解杠杆风险',
            test_data='BTC/USDT永续合约，价格50000 USDT，杠杆10x',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 用户账户有10000 USDT\n2. 开多仓：BTC价格50000，数量0.2 BTC，杠杆10x\n3. 计算所需保证金：(0.2 * 50000) / 10 = 1000 USDT\n4. 验证保证金冻结\n5. 验证持仓信息\n6. 测试不同杠杆倍数',
            expected_result='1. 开仓成功\n2. 冻结保证金：1000 USDT（可能还有额外的开仓手续费）\n3. 可用余额：10000 - 1000 - 手续费\n4. 持仓信息：多仓，数量0.2，开仓价50000，杠杆10x\n5. 强制平仓价格：需要计算',
            actual_tool='合约交易模拟器 + 后台验证',
            notes='实际项目经验：\n\n1. **保证金模式**：\n   - 逐仓模式(Isolated)：每个仓位独立保证金，风险隔离\n   - 全仓模式(Cross)：所有仓位共享账户余额，风险共享\n\n2. **杠杆倍数**：\n   - 杠杆越高，所需保证金越少，但风险越大\n   - 不同币种有不同的最大杠杆限制\n   - 高杠杆仓位的维持保证金要求也更高\n\n3. **保证金计算**：\n   - 初始保证金 = 合约价值 / 杠杆倍数\n   - 维持保证金 = 合约价值 * 维持保证金率\n   - 当保证金余额低于维持保证金时，触发强制平仓\n\n4. **标记价格**：\n   - 合约盈亏通常使用标记价格计算，而非最新成交价\n   - 标记价格通常是多个交易所价格的加权平均\n   - 防止恶意操纵价格触发强制平仓\n\n5. **资金费用**：\n   - 永续合约每8小时收取/支付资金费用\n   - 资金费率由多空双方力量对比决定\n   - 持有仓位越过资金费用时间点需要支付/收取'
        ),
        BlockChainTestCases(
            module='contract_trading',
            category='合约原理',
            sub_category='持仓管理',
            title='合约未实现盈亏与强制平仓测试',
            description='测试持仓期间的盈亏计算和强制平仓触发机制',
            preconditions='1. 用户已有持仓\n2. 标记价格正常更新\n3. 保证金监控正常',
            test_data='持仓信息、价格波动场景',
            priority='P0',
            test_type='功能测试',
            test_steps='1. 初始状态：多仓0.2 BTC，开仓价50000，杠杆10x\n2. 标记价格上涨到55000\n3. 计算未实现盈亏：(55000-50000)*0.2 = 1000 USDT\n4. 验证账户权益增加\n5. 标记价格下跌到46000\n6. 计算未实现盈亏：(46000-50000)*0.2 = -800 USDT\n7. 验证保证金率\n8. 价格继续下跌，测试强制平仓触发',
            expected_result='1. 价格上涨时：未实现盈利，保证金率上升\n2. 价格下跌时：未实现亏损，保证金率下降\n3. 当保证金率低于维持保证金率时：触发强制平仓\n4. 强平后：仓位被接管，保证金用于弥补亏损',
            actual_tool='合约模拟交易 + 价格波动模拟',
            notes='实际项目经验：\n\n1. **未实现盈亏计算**：\n   - 多仓：(标记价格 - 开仓价格) * 持仓数量\n   - 空仓：(开仓价格 - 标记价格) * 持仓数量\n   - 未实现盈亏随标记价格实时变化\n\n2. **保证金率**：\n   - 保证金率 = (保证金余额 + 未实现盈亏) / 持仓价值\n   - 全仓模式：保证金率 = (账户权益 - 其他仓位占用) / 当前仓位价值\n   - 当保证金率低于维持保证金率时，触发强制平仓\n\n3. **强制平仓流程**：\n   - 系统接管用户仓位\n   - 在市场上进行强平交易\n   - 使用强平保证金弥补亏损\n   - 如有剩余，返还用户\n   - 如有不足，可能产生穿仓（用户需要分摊）\n\n4. **保险基金**：\n   - 交易所设立保险基金，用于弥补穿仓损失\n   - 强平产生的额外盈利注入保险基金\n   - 保险基金不足时，可能需要自动减仓(ADL)\n\n5. **自动减仓(ADL)**：\n   - 当保险基金不足以弥补穿仓损失时\n   - 系统自动减仓盈利最多的对手方仓位\n   - 按照盈利比例和杠杆倍数排序'
        ),
        BlockChainTestCases(
            module='contract_trading',
            category='合约原理',
            sub_category='资金费用',
            title='永续合约资金费用机制测试',
            description='测试永续合约的资金费率计算和资金费用收取',
            preconditions='1. 永续合约正常运行\n2. 资金费率正常计算\n3. 接近资金费用时间点',
            test_data='多空持仓、资金费率场景',
            priority='P1',
            test_type='功能测试',
            test_steps='1. 记录资金费用时间点（如UTC 0:00, 8:00, 16:00）\n2. 在时间点前建立多仓和空仓\n3. 观察资金费率计算\n4. 越过时间点后验证资金费用收取/支付\n5. 测试正资金费率和负资金费率场景',
            expected_result='1. 资金费率为正时：多仓支付，空仓收取\n2. 资金费率为负时：多仓收取，空仓支付\n3. 资金费用 = 持仓价值 * 资金费率\n4. 只在资金费用时间点持有仓位才需要支付/收取',
            actual_tool='合约交易系统 + 时间模拟',
            notes='实际项目经验：\n\n1. **资金费率目的**：\n   - 使永续合约价格锚定现货价格\n   - 当合约价格高于现货时，多头支付空头\n   - 当合约价格低于现货时，空头支付多头\n\n2. **资金费率计算**：\n   - 资金费率 = 溢价指数 + clamp(利率 - 溢价指数, 0.0005, -0.0005)\n   - 溢价指数 = (合约价格 - 现货价格) / 现货价格\n   - 利率通常是固定的（如0.01%每天）\n\n3. **资金费用收取**：\n   - 每8小时收取一次（UTC 0:00, 8:00, 16:00）\n   - 只在时间点持有仓位才需要支付/收取\n   - 资金费用直接在账户余额中增减\n\n4. **用户策略**：\n   - 可以通过在资金费用时间点前平仓来避免支付\n   - 某些用户专门进行资金费率套利\n   - 高资金费率时期，持仓成本显著增加\n\n5. **极端情况**：\n   - 市场极度看涨时，资金费率可能非常高（如1%以上每天）\n   - 这会导致多头持仓成本极高\n   - 交易所可能设置资金费率上限'
        )
    ]
    
    for t in advanced_blockchain_tests:
        existing = BlockChainTestCases.query.filter_by(title=t.title).first()
        if not existing:
            db.session.add(t)
        else:
            sync_existing_record(existing, t)
    
    test_types = [
        TestType(
            name='功能测试',
            category='功能测试类',
            description='功能测试是软件测试的基础类型，主要验证软件的各个功能是否符合需求规格说明书的要求。通过模拟用户实际使用场景，检查系统是否能够正确完成预期的功能操作。',
            purpose='验证软件功能的正确性，确保系统能够按照需求规格说明书正确工作。发现功能缺陷，确保用户能够正常使用系统的各项功能。',
            when_to_use='<ul><li>新功能开发完成后</li><li>系统集成测试阶段</li><li>回归测试阶段</li><li>用户验收测试前</li><li>每次代码变更后</li></ul>',
            key_concepts='<ul><li><strong>测试覆盖</strong>：确保所有功能点都被测试覆盖</li><li><strong>正向测试</strong>：验证正常输入下的正确行为</li><li><strong>反向测试</strong>：验证异常输入下的错误处理</li><li><strong>边界测试</strong>：验证边界条件下的系统行为</li><li><strong>需求追溯</strong>：确保测试用例与需求一一对应</li></ul>',
            tools='<ul><li><strong>手工测试工具</strong>：Jira、TestRail、禅道、Excel</li><li><strong>自动化测试工具</strong>：Selenium、Appium、Cypress、Playwright</li><li><strong>接口测试工具</strong>：Postman、JMeter、RestAssured、Requests</li><li><strong>用例管理工具</strong>：TestLink、Polarion、Xray</li></ul>',
            examples='<strong>登录功能测试场景：</strong><br><ol><li><strong>正向测试</strong>：输入正确的用户名和密码，验证登录成功</li><li><strong>反向测试</strong>：输入错误的密码，验证登录失败并提示正确的错误信息</li><li><strong>边界测试</strong>：输入空的用户名或密码，验证系统的提示信息</li><li><strong>特殊字符测试</strong>：输入包含SQL注入、XSS攻击字符的用户名，验证系统的安全性</li><li><strong>并发测试</strong>：同一账号同时在多个地方登录，验证系统的会话管理</li></ol>',
            sort_order=1
        ),
        TestType(
            name='界面测试 (UI测试)',
            category='功能测试类',
            description='界面测试关注用户与系统交互的界面元素，验证界面布局、样式、交互行为是否符合设计规范和用户预期。包括视觉测试、交互测试、兼容性测试等方面。',
            purpose='确保用户界面的视觉效果和交互体验符合设计要求，提升用户体验。发现界面布局问题、交互异常、视觉不一致等缺陷。',
            when_to_use='<ul><li>UI设计稿完成后</li><li>前端开发完成后</li><li>跨浏览器/跨设备测试</li><li>响应式设计验证</li><li>主题切换测试</li></ul>',
            key_concepts='<ul><li><strong>像素级对齐</strong>：验证界面元素与设计稿的像素级一致性</li><li><strong>响应式布局</strong>：验证在不同屏幕尺寸下的布局适配</li><li><strong>交互反馈</strong>：验证按钮、输入框等元素的交互反馈</li><li><strong>视觉一致性</strong>：验证字体、颜色、间距等视觉元素的一致性</li><li><strong>可访问性</strong>：验证界面是否符合无障碍设计标准</li></ul>',
            tools='<ul><li><strong>视觉对比工具</strong>：Applitools、Percy、BackstopJS</li><li><strong>浏览器开发者工具</strong>：Chrome DevTools、Firefox Developer Tools</li><li><strong>响应式测试工具</strong>：BrowserStack、Sauce Labs、LambdaTest</li><li><strong>可访问性测试</strong>：axe、WAVE、NVDA屏幕阅读器</li><li><strong>截图对比</strong>：Selenium + Pillow、Playwright截图</li></ul>',
            examples='<strong>电商商品详情页UI测试场景：</strong><br><ol><li><strong>布局验证</strong>：验证商品图片、价格、规格选择、加入购物车按钮的位置和间距是否与设计稿一致</li><li><strong>响应式测试</strong>：在手机、平板、桌面端分别测试，验证布局是否正确适配</li><li><strong>交互测试</strong>：点击规格选择（颜色、尺寸），验证价格是否实时更新，按钮状态是否变化</li><li><strong>图片轮播测试</strong>：测试商品图片轮播的自动播放、手动切换、指示器功能</li><li><strong>表单验证</strong>：测试数量输入框的边界值（最小1、最大库存）、增减按钮的交互</li><li><strong>视觉回归</strong>：对比当前版本与上一版本的界面截图，发现意外的视觉变化</li></ol>',
            sort_order=2
        ),
        TestType(
            name='接口测试 (API测试)',
            category='功能测试类',
            description='接口测试是测试系统组件间接口的一种测试方式，主要验证数据交换的正确性、接口协议的合规性、异常处理的健壮性。是持续集成和自动化测试的核心领域。',
            purpose='验证API接口的功能正确性、性能稳定性和安全性。在UI开发完成前即可进行测试，更早发现问题。',
            when_to_use='<ul><li>后端API开发完成后</li><li>前后端联调前</li><li>回归测试（最适合自动化）</li><li>微服务架构测试</li><li>第三方接口集成测试</li></ul>',
            key_concepts='<ul><li><strong>请求方法</strong>：GET、POST、PUT、DELETE、PATCH等HTTP方法的正确使用</li><li><strong>状态码</strong>：2xx成功、3xx重定向、4xx客户端错误、5xx服务端错误</li><li><strong>请求/响应格式</strong>：JSON、XML、表单数据等格式的正确性</li><li><strong>认证授权</strong>：Token、JWT、OAuth、Session等认证机制</li><li><strong>参数校验</strong>：必填项、数据类型、格式、长度、范围等校验</li></ul>',
            tools='<ul><li><strong>接口测试工具</strong>：Postman、Insomnia、Apifox、JMeter</li><li><strong>代码框架</strong>：Python Requests + Pytest、Java RestAssured + TestNG</li><li><strong>契约测试</strong>：Pact、Spring Cloud Contract</li><li><strong>性能测试</strong>：JMeter、Gatling、k6、Locust</li><li><strong>API文档</strong>：Swagger/OpenAPI、Postman Collection</li></ul>',
            examples='<strong>用户注册接口测试场景：</strong><br><ol><li><strong>正向测试</strong>：发送POST请求到/api/register，包含有效的用户名、密码、邮箱，验证返回200状态码和成功消息</li><li><strong>参数缺失测试</strong>：不发送密码字段，验证返回400状态码和"密码不能为空"的错误信息</li><li><strong>格式校验测试</strong>：发送格式错误的邮箱（如"test"），验证返回400状态码和邮箱格式错误提示</li><li><strong>重复注册测试</strong>：使用已注册的用户名再次注册，验证返回409状态码和"用户名已存在"提示</li><li><strong>SQL注入测试</strong>：在用户名字段发送"admin\' OR \'1\'=\'1"，验证系统能够正确处理，不返回敏感信息</li><li><strong>认证测试</strong>：访问需要登录的接口（如修改用户信息），不带Token验证返回401，带正确Token验证返回200</li></ol>',
            sort_order=3
        ),
        TestType(
            name='数据库测试',
            category='功能测试类',
            description='数据库测试验证数据的存储、检索、更新和删除操作的正确性，包括数据完整性、一致性、安全性和性能。是保障数据质量的关键测试类型。',
            purpose='确保数据在数据库层面的正确性、完整性和安全性。验证业务逻辑在数据层的实现是否正确。',
            when_to_use='<ul><li>数据库设计完成后</li><li>数据迁移前后</li><li>批量数据处理后</li><li>报表功能测试</li><li>数据备份恢复测试</li></ul>',
            key_concepts='<ul><li><strong>ACID特性</strong>：原子性、一致性、隔离性、持久性</li><li><strong>数据完整性</strong>：实体完整性、参照完整性、域完整性、用户定义完整性</li><li><strong>数据一致性</strong>：同一数据在不同表中的值保持一致</li><li><strong>索引有效性</strong>：验证索引是否正确创建和使用</li><li><strong>存储过程/触发器</strong>：验证数据库逻辑的正确性</li></ul>',
            tools='<ul><li><strong>数据库客户端</strong>：MySQL Workbench、Navicat、DBeaver、pgAdmin</li><li><strong>数据对比工具</strong>：Redgate SQL Compare、ApexSQL Diff、Navicat Data Modeler</li><li><strong>测试框架</strong>：Python SQLAlchemy + Pytest、Java JDBC + TestNG</li><li><strong>数据生成</strong>：Mockaroo、GenerateData、Faker库</li><li><strong>性能监控</strong>：MySQL Enterprise Monitor、pg_stat_statements</li></ul>',
            examples='<strong>电商订单系统数据库测试场景：</strong><br><ol><li><strong>数据插入测试</strong>：创建一个新订单，验证orders表、order_items表、order_logs表都正确插入了对应记录，且外键关联正确</li><li><strong>数据一致性测试</strong>：用户支付订单后，验证user_balance表的余额减少、orders表的status更新为"已支付"、transaction_logs表有支付记录，三者金额一致</li><li><strong>事务回滚测试</strong>：在订单创建过程中人为制造错误（如库存不足），验证整个事务是否正确回滚，没有产生脏数据</li><li><strong>存储过程测试</strong>：调用计算用户等级的存储过程，验证根据用户消费金额正确更新user_level字段</li><li><strong>触发器测试</strong>：更新订单状态为"已完成"，验证触发器是否自动创建用户积分记录</li><li><strong>数据删除测试</strong>：删除一个订单，验证级联删除是否正确处理相关表的数据，或软删除标记是否正确设置</li></ol>',
            sort_order=4
        ),
        TestType(
            name='性能测试',
            category='非功能测试类',
            description='性能测试评估系统在各种负载下的表现，包括响应时间、吞吐量、资源利用率、稳定性等指标。是保障系统能够承受预期用户访问量的关键测试类型。',
            purpose='评估系统的性能表现，发现性能瓶颈，确保系统能够满足预期的性能需求。在高并发场景下保障系统的稳定性。',
            when_to_use='<ul><li>系统架构设计验证</li><li>新版本上线前</li><li>大促活动前</li><li>系统扩容后</li><li>性能优化前后对比</li></ul>',
            key_concepts='<ul><li><strong>响应时间</strong>：从请求发送到响应接收的时间</li><li><strong>吞吐量</strong>：单位时间内系统处理的请求数</li><li><strong>并发用户数</strong>：同时访问系统的用户数量</li><li><strong>资源利用率</strong>：CPU、内存、磁盘IO、网络带宽的使用情况</li><li><strong>性能瓶颈</strong>：限制系统性能提升的关键因素</li></ul>',
            tools='<ul><li><strong>负载测试工具</strong>：JMeter、Gatling、k6、Locust、LoadRunner</li><li><strong>APM工具</strong>：New Relic、Datadog、SkyWalking、Pinpoint</li><li><strong>监控工具</strong>：Prometheus + Grafana、Zabbix、Nagios</li><li><strong>数据库性能</strong>：MySQL Slow Query Log、EXPLAIN分析、pg_stat_statements</li><li><strong>前端性能</strong>：WebPageTest、Lighthouse、Chrome DevTools Performance</li></ul>',
            examples='<strong>电商秒杀系统性能测试场景：</strong><br><ol><li><strong>基准测试</strong>：在单用户情况下测试秒杀接口的响应时间，建立性能基线</li><li><strong>负载测试</strong>：逐步增加并发用户数（从100到10000），观察系统的响应时间和吞吐量变化</li><li><strong>压力测试</strong>：持续增加负载直到系统崩溃，找到系统的极限处理能力</li><li><strong>稳定性测试</strong>：以80%极限负载持续运行24小时，观察系统是否有内存泄漏、性能下降</li><li><strong>并发控制测试</strong>：模拟10000个用户同时抢购100件商品，验证是否出现超卖、少卖、数据不一致</li><li><strong>性能瓶颈分析</strong>：在高负载下观察数据库连接池、Redis缓存、消息队列等组件的状态，定位性能瓶颈</li></ol>',
            sort_order=5
        ),
        TestType(
            name='负载测试',
            category='非功能测试类',
            description='负载测试是性能测试的一种，通过模拟真实用户的负载情况，评估系统在预期负载下的性能表现。关注系统在正常和峰值负载下的响应时间、吞吐量和资源利用率。',
            purpose='验证系统在预期负载下是否能够满足性能需求。确定系统的最佳负载范围，为容量规划提供依据。',
            when_to_use='<ul><li>系统开发完成后</li><li>性能调优过程中</li><li>每次重大变更后</li><li>容量规划决策前</li><li>与上一版本性能对比</li></ul>',
            key_concepts='<ul><li><strong>预期负载</strong>：根据业务分析得出的正常使用情况下的负载</li><li><strong>峰值负载</strong>：业务高峰期的最大负载</li><li><strong>负载模型</strong>：模拟用户行为的脚本和场景</li><li><strong>渐增式负载</strong>：逐步增加负载观察系统变化</li><li><strong>拐点分析</strong>：找到性能开始急剧下降的负载点</li></ul>',
            tools='<ul><li><strong>主流工具</strong>：JMeter、Gatling、k6、Locust</li><li><strong>企业级工具</strong>：LoadRunner、NeoLoad、Silk Performer</li><li><strong>云原生工具</strong>：k6、JMeter Distributed、Gatling FrontLine</li><li><strong>实时监控</strong>：Grafana、InfluxDB、Telegraf</li></ul>',
            examples='<strong>内容平台负载测试场景：</strong><br><ol><li><strong>负载模型设计</strong>：根据实际业务数据，设计用户行为模型：30%浏览首页、40%阅读文章、20%搜索、10%发布评论</li><li><strong>基准测试</strong>：以100并发用户运行30分钟，记录响应时间、TPS、错误率作为基准</li><li><strong>渐增负载测试</strong>：每10分钟增加100并发用户，直到达到1000并发，观察各指标的变化趋势</li><li><strong>峰值负载测试</strong>：以预期峰值负载（如500并发）持续运行1小时，验证系统稳定性</li><li><strong>负载卸载测试</strong>：从高负载逐步降低负载，观察系统恢复能力</li><li><strong>对比测试</strong>：比较新版本与上一版本在相同负载下的性能表现，确认没有性能回退</li></ol>',
            sort_order=6
        ),
        TestType(
            name='压力测试',
            category='非功能测试类',
            description='压力测试是通过给系统施加超过预期的负载，评估系统在极限情况下的表现。目的是找到系统的瓶颈点和崩溃点，了解系统的极限处理能力。',
            purpose='发现系统的极限承载能力，识别潜在的性能瓶颈。验证系统在极端压力下的容错能力和恢复能力。',
            when_to_use='<ul><li>新系统上线前的极限验证</li><li>架构重构后的能力验证</li><li>重大促销活动前</li><li>容量规划的参考依据</li><li>发现隐蔽的性能问题</li></ul>',
            key_concepts='<ul><li><strong>极限负载</strong>：系统能够承受的最大负载</li><li><strong>瓶颈点</strong>：限制系统性能提升的关键组件</li><li><strong>熔断机制</strong>：系统在压力过大时的自我保护</li><li><strong>优雅降级</strong>：在压力下关闭非核心功能</li><li><strong>快速恢复</strong>：压力解除后系统能否快速恢复正常</li></ul>',
            tools='<ul><li><strong>高并发工具</strong>：Gatling、k6、JMeter分布式测试</li><li><strong>混沌工程</strong>：Chaos Monkey、ChaosBlade、Gremlin</li><li><strong>故障注入</strong>：Toxiproxy、Pumba</li><li><strong>全链路监控</strong>：Jaeger、Zipkin、SkyWalking</li></ul>',
            examples='<strong>支付系统压力测试场景：</strong><br><ol><li><strong>阶梯式加压</strong>：从1000并发开始，每5分钟增加1000并发，直到系统响应时间超过阈值或错误率上升</li><li><strong>极限突破测试</strong>：发现系统极限后，继续增加20%负载，观察系统是否崩溃、数据是否损坏</li><li><strong>资源耗尽测试</strong>：模拟数据库连接池耗尽、Redis内存满、磁盘空间不足等场景，验证系统的容错机制</li><li><strong>网络延迟测试</strong>：使用Toxiproxy模拟网络延迟、丢包、断连，验证系统在网络异常下的表现</li><li><strong>熔断机制测试</strong>：在高压力下验证熔断器是否正确触发，下游故障是否影响上游</li><li><strong>恢复能力测试</strong>：压力测试后停止加压，观察系统的CPU、内存、连接数等指标是否能快速恢复到正常水平</li></ol>',
            sort_order=7
        ),
        TestType(
            name='安全性测试',
            category='专项测试类',
            description='安全性测试验证系统是否存在安全漏洞，保护系统免受未经授权的访问、数据泄露、恶意攻击等威胁。是保障系统和用户数据安全的重要测试类型。',
            purpose='发现系统中的安全漏洞和弱点，评估系统的安全防护能力。确保系统符合安全法规和标准要求。',
            when_to_use='<ul><li>新系统上线前</li><li>重大功能变更后</li><li>定期安全审计</li><li>合规性认证前</li><li>安全事件响应后</li></ul>',
            key_concepts='<ul><li><strong>OWASP Top 10</strong>：注入、失效认证、敏感数据泄露、XML外部实体、失效访问控制、安全配置错误、跨站脚本、不安全的反序列化、使用含有已知漏洞的组件、不足的日志和监控</li><li><strong>渗透测试</strong>：模拟黑客攻击发现漏洞</li><li><strong>漏洞扫描</strong>：自动化工具发现已知漏洞</li><li><strong>代码审计</strong>：审查源代码中的安全问题</li><li><strong>合规性</strong>：满足等保2.0、PCI-DSS、GDPR等法规要求</li></ul>',
            tools='<ul><li><strong>Web扫描器</strong>：OWASP ZAP、Burp Suite、Nessus、AppScan</li><li><strong>代码审计</strong>：SonarQube、Checkmarx、Fortify、Coverity</li><li><strong>渗透测试</strong>：Metasploit、Nmap、sqlmap、XSSer</li><li><strong>移动安全</strong>：MobSF、Frida、Objection</li><li><strong>API安全</strong>：Postman安全测试、Burp Suite API扫描</li></ul>',
            examples='<strong>金融系统安全性测试场景：</strong><br><ol><li><strong>SQL注入测试</strong>：在登录表单、搜索框、URL参数中注入SQL语句（如"\' OR 1=1 --"），验证系统是否存在注入漏洞</li><li><strong>XSS跨站脚本测试</strong>：在评论、个人资料等用户输入区域输入恶意脚本（如"<script>alert(document.cookie)</script>"），验证系统是否正确过滤</li><li><strong>越权访问测试</strong>：登录普通用户账户，尝试访问管理员功能、修改其他用户数据、查看他人敏感信息，验证权限控制是否有效</li><li><strong>敏感数据泄露测试</strong>：检查网络传输是否使用HTTPS、敏感数据（密码、身份证、银行卡）是否加密存储、日志中是否泄露敏感信息</li><li><strong>认证机制测试</strong>：测试密码复杂度要求、登录失败锁定、会话超时、Token过期、单点登录安全性</li><li><strong>业务逻辑漏洞测试</strong>：测试支付流程中能否修改金额、转账时能否转出负数、积分兑换时能否重复兑换等业务逻辑层面的安全问题</li></ol>',
            sort_order=8
        ),
        TestType(
            name='兼容性测试',
            category='专项测试类',
            description='兼容性测试验证软件在不同环境下的正确运行能力，包括不同浏览器、操作系统、设备、网络环境、软件版本等。确保目标用户群体都能正常使用软件。',
            purpose='确保软件在目标用户的各种环境中都能正常工作。减少因环境差异导致的用户体验问题和功能缺陷。',
            when_to_use='<ul><li>新功能开发完成后</li><li>浏览器/系统新版本发布后</li><li>移动端应用发布前</li><li>企业级软件多环境部署</li><li>国际化版本发布</li></ul>',
            key_concepts='<ul><li><strong>浏览器兼容性</strong>：Chrome、Firefox、Safari、Edge、IE等不同浏览器和版本</li><li><strong>操作系统兼容性</strong>：Windows、macOS、Linux、iOS、Android等</li><li><strong>设备兼容性</strong>：不同品牌、型号、屏幕尺寸、分辨率的设备</li><li><strong>版本兼容性</strong>：新旧版本数据兼容、API兼容、数据库兼容</li><li><strong>网络兼容性</strong>：WiFi、4G、5G、弱网、断网等网络环境</li></ul>',
            tools='<ul><li><strong>跨浏览器测试</strong>：BrowserStack、Sauce Labs、LambdaTest、CrossBrowserTesting</li><li><strong>真机云测试</strong>：Testin云测、阿里云测、腾讯WeTest、Sauce Labs Real Device Cloud</li><li><strong>兼容性自动化</strong>：Selenium Grid、Appium Grid、Playwright跨浏览器</li><li><strong>网络模拟</strong>：Charles、Fiddler、Network Link Conditioner</li><li><strong>版本对比</strong>：Applitools视觉AI对比</li></ul>',
            examples='<strong>社交应用兼容性测试场景：</strong><br><ol><li><strong>浏览器兼容性测试</strong>：在Chrome（最新版、上一版本）、Firefox、Safari、Edge中测试登录、发帖、评论、上传图片等核心功能，验证功能正常和界面一致</li><li><strong>移动端兼容性测试</strong>：在iPhone 14（iOS 16）、iPhone SE（iOS 15）、华为Mate 60（HarmonyOS）、小米13（Android 13）、OPPO低端机型（Android 10）等设备上测试应用安装、启动、核心功能、UI适配</li><li><strong>屏幕适配测试</strong>：在不同分辨率（1080p、2K、4K）、不同屏幕比例（16:9、18:9、20:9）、不同DPI（低密度、高密度）下测试UI布局是否正确</li><li><strong>弱网兼容性测试</strong>：使用Charles模拟3G网络（1Mbps带宽、300ms延迟）、丢包（10%丢包率）、网络抖动，验证应用的加载状态、错误提示、重试机制</li><li><strong>系统版本兼容性测试</strong>：在iOS 14-17、Android 8-14等不同系统版本上测试，验证没有使用新版本API导致的崩溃</li><li><strong>第三方软件兼容性</strong>：测试与微信、支付宝、地图、相机、相册等系统应用和常见第三方应用的交互兼容性</li></ol>',
            sort_order=9
        ),
        TestType(
            name='易用性测试',
            category='专项测试类',
            description='易用性测试评估用户使用软件的难易程度，关注用户体验、学习成本、操作效率、错误恢复等方面。是提升用户满意度和产品竞争力的重要测试类型。',
            purpose='评估产品的用户友好程度，发现用户体验问题。提升产品的易用性，降低用户学习成本和操作失误。',
            when_to_use='<ul><li>产品原型阶段</li><li>UI设计完成后</li><li>功能开发完成后</li><li>用户验收测试</li><li>产品迭代优化</li></ul>',
            key_concepts='<ul><li><strong>可学习性</strong>：用户首次使用时学习操作的难易程度</li><li><strong>效率</strong>：熟练用户完成任务的效率</li><li><strong>可记忆性</strong>：用户间隔一段时间后再次使用的记忆成本</li><li><strong>错误处理</strong>：用户犯错后的恢复能力和系统提示</li><li><strong>满意度</strong>：用户对产品的主观满意程度</li></ul>',
            tools='<ul><li><strong>用户研究</strong>：UserTesting、Maze、Lookback</li><li><strong>热力图分析</strong>：Hotjar、Crazy Egg、Mouseflow</li><li><strong>A/B测试</strong>：Optimizely、Google Optimize、AB Tasty</li><li><strong>可用性度量</strong>：System Usability Scale (SUS)问卷、Net Promoter Score (NPS)</li><li><strong>原型测试</strong>：Figma、Sketch、Axure、InVision</li></ul>',
            examples='<strong>电商APP易用性测试场景：</strong><br><ol><li><strong>任务完成测试</strong>：让用户完成"找到心仪商品并下单购买"的任务，记录完成时间、点击次数、错误次数、求助次数</li><li><strong>首次使用测试</strong>：让从未使用过该APP的用户尝试注册登录，观察是否遇到困难，哪些步骤需要思考很久</li><li><strong>导航测试</strong>：让用户从首页出发，找到"我的订单"、"购物车"、"客服中心"、"设置"等功能，观察导航是否清晰</li><li><strong>错误恢复测试</strong>：让用户在填写收货地址时故意填错（如手机号位数不足、邮编格式错误），观察系统提示是否清晰，修改是否方便</li><li><strong>可访问性测试</strong>：测试色盲用户能否分辨按钮状态、视力障碍用户使用屏幕阅读器能否正常操作、键盘用户能否不使用鼠标完成所有操作</li><li><strong>满意度调查</strong>：让用户完成典型任务后填写SUS问卷，评估整体可用性，并收集主观反馈和改进建议</li></ol>',
            sort_order=10
        ),
        TestType(
            name='安装/卸载测试',
            category='专项测试类',
            description='安装/卸载测试验证软件安装、升级、卸载过程的正确性和完整性。确保用户能够顺利完成整个软件生命周期的管理操作。',
            purpose='确保安装过程顺畅、卸载干净彻底、升级数据兼容。避免因安装问题导致的用户流失和数据丢失。',
            when_to_use='<ul><li>软件首次发布前</li><li>每次版本更新前</li><li>安装包格式变更</li><li>签名/证书更新</li><li>企业级部署验证</li></ul>',
            key_concepts='<ul><li><strong>安装过程</strong>：下载、解压、复制文件、注册表写入、服务注册、权限设置</li><li><strong>升级过程</strong>：覆盖安装、数据迁移、配置保留、回滚机制</li><li><strong>卸载过程</strong>：文件删除、注册表清理、服务停止、数据保留/删除选项</li><li><strong>磁盘空间</strong>：安装所需空间、临时空间、卸载后空间释放</li><li><strong>权限要求</strong>：管理员权限、用户权限、沙盒环境</li></ul>',
            tools='<ul><li><strong>安装包制作</strong>：InstallShield、WiX、Advanced Installer、NSIS</li><li><strong>虚拟机环境</strong>：VMware、VirtualBox、Docker、Windows Sandbox</li><li><strong>注册表监控</strong>：Process Monitor、RegShot、InstallWatch</li><li><strong>文件系统监控</strong>：FileMon、Process Explorer、Everything</li><li><strong>移动端安装</strong>：ADB、iTunes、各种应用商店</li></ul>',
            examples='<strong>桌面应用安装/卸载测试场景：</strong><br><ol><li><strong>全新安装测试</strong>：在干净的系统中运行安装程序，验证安装向导步骤、许可协议、安装路径选择、组件选择、快捷方式创建、启动菜单条目</li><li><strong>磁盘空间测试</strong>：在磁盘空间不足时尝试安装，验证系统提示是否清晰、是否在空间释放后能继续安装</li><li><strong>权限测试</strong>：在普通用户权限（非管理员）下尝试安装，验证是否正确提示需要管理员权限</li><li><strong>升级安装测试</strong>：安装上一版本，使用一段时间产生数据，然后安装新版本，验证数据是否正确迁移、配置是否保留、功能是否正常</li><li><strong>卸载测试</strong>：使用控制面板或自带卸载程序卸载，验证：程序文件是否删除、注册表是否清理、服务是否停止并删除、用户数据是否按选择保留/删除</li><li><strong>强制终止测试</strong>：在安装过程中强制终止安装程序，验证系统状态是否干净、是否可以重新安装</li></ol>',
            sort_order=11
        ),
        TestType(
            name='网络测试',
            category='专项测试类',
            description='网络测试验证软件在各种网络环境下的表现，包括不同网络类型、网络质量、网络切换、断网恢复等场景。确保用户在各种网络条件下都能获得良好体验。',
            purpose='评估软件在不同网络环境下的适应性和稳定性。发现网络相关的缺陷，优化弱网下的用户体验。',
            when_to_use='<ul><li>网络相关功能开发</li><li>移动端应用测试</li><li>弱网环境优化</li><li>离线功能验证</li><li>网络切换场景</li></ul>',
            key_concepts='<ul><li><strong>网络类型</strong>：WiFi、4G、5G、3G、2G、有线网络</li><li><strong>网络质量</strong>：带宽、延迟、丢包、抖动、乱序</li><li><strong>网络状态</strong>：在线、离线、弱连接、网络切换</li><li><strong>请求处理</strong>：超时、重试、熔断、降级、缓存</li><li><strong>数据同步</strong>：在线/离线数据同步、冲突解决</li></ul>',
            tools='<ul><li><strong>网络模拟</strong>：Charles、Fiddler、mitmproxy、Network Link Conditioner</li><li><strong>流量分析</strong>：Wireshark、Tcpdump、Burp Suite</li><li><strong>弱网测试</strong>：Clumsy、WAN Emulation、tc (Linux)</li><li><strong>移动网络</strong>：Android ADB网络限速、iOS Developer Network Link Conditioner</li><li><strong>API监控</strong>：Postman Monitors、New Relic Synthetics</li></ul>',
            examples='<strong>社交应用网络测试场景：</strong><br><ol><li><strong>弱网加载测试</strong>：使用Charles模拟3G网络（1Mbps带宽、500ms延迟），测试首页信息流加载，验证是否有加载动画、是否显示进度、是否在超时后给出友好提示</li><li><strong>断网测试</strong>：在使用过程中断开网络，验证：已缓存的内容是否可访问、离线操作是否正确队列、网络恢复后是否自动同步、是否有网络状态提示</li><li><strong>网络切换测试</strong>：在WiFi环境下开始下载文件，切换到4G网络，验证下载是否继续或提示用户；在4G下播放视频，切换到WiFi，验证是否自动切换到高清画质</li><li><strong>丢包测试</strong>：模拟20%的网络丢包率，测试消息发送、图片上传等操作，验证是否有重试机制、是否最终成功、是否在失败时给出提示</li><li><strong>超时测试</strong>：模拟服务器无响应（使用Charles设置无限延迟），验证客户端的超时时间设置是否合理、超时后的提示是否友好、是否提供重试选项</li><li><strong>并发网络请求测试</strong>：同时发起多个网络请求（如同时加载多张图片、多个API请求），验证请求管理是否合理、是否有请求优先级、是否会导致界面卡顿</li></ol>',
            sort_order=12
        ),
        TestType(
            name='文档测试',
            category='其他测试类型',
            description='文档测试验证软件相关文档的正确性、完整性、一致性和易用性。包括用户手册、安装指南、API文档、帮助文档、Release Notes等。',
            purpose='确保文档与实际产品一致，用户能够通过文档正确使用软件。减少因文档问题导致的用户困惑和客服咨询。',
            when_to_use='<ul><li>产品发布前</li><li>每次版本更新</li><li>文档重大修订</li><li>用户反馈文档问题后</li><li>国际化版本发布</li></ul>',
            key_concepts='<ul><li><strong>正确性</strong>：文档描述与实际产品行为一致</li><li><strong>完整性</strong>：所有功能都有文档说明</li><li><strong>一致性</strong>：术语、格式、风格在各文档间保持一致</li><li><strong>可读性</strong>：语言通俗易懂，步骤清晰</li><li><strong>时效性</strong>：文档版本与产品版本对应</li></ul>',
            tools='<ul><li><strong>文档工具</strong>：Confluence、Notion、GitBook、ReadMe</li><li><strong>API文档</strong>：Swagger UI、Postman Documenter、Apiary</li><li><strong>拼写检查</strong>：Grammarly、Hunspell、Microsoft Word</li><li><strong>版本控制</strong>：Git + Markdown、SVN</li><li><strong>测试管理</strong>：TestRail、Jira Xray</li></ul>',
            examples='<strong>企业级软件文档测试场景：</strong><br><ol><li><strong>安装指南测试</strong>：按照安装指南的步骤一步步操作，验证每个步骤的描述是否准确、是否有遗漏步骤、截图是否与实际界面一致</li><li><strong>用户手册测试</strong>：随机抽取几个用户任务，按照手册描述操作，验证能否成功完成任务、术语是否与界面一致、快捷键描述是否正确</li><li><strong>API文档测试</strong>：使用Swagger文档中的示例请求，复制到Postman中执行，验证参数描述是否正确、响应示例与实际响应是否一致、必填项标记是否准确</li><li><strong>Release Notes测试</strong>：对照Release Notes中列出的"新功能"和"修复问题"，验证功能是否确实存在、问题是否确实修复、已知问题描述是否准确</li><li><strong>一致性测试</strong>：检查用户手册、安装指南、界面、错误提示中使用的术语是否一致（如"登录"vs"登入"、"确定"vs"确认"）</li><li><strong>国际化文档测试</strong>：检查翻译版本的文档，验证：专业术语翻译准确、文化习惯适配、日期/时间/货币格式与目标地区一致</li></ol>',
            sort_order=13
        ),
        TestType(
            name='回归测试',
            category='其他测试类型',
            description='回归测试是在软件变更后重新测试已有功能，确保变更没有引入新的缺陷或破坏现有功能。是软件维护和持续集成过程中最重要的测试类型之一。',
            purpose='确保代码变更不会意外破坏现有功能。保证系统在迭代过程中的稳定性和可靠性。',
            when_to_use='<ul><li>每次代码提交后</li><li>Bug修复后</li><li>新功能开发完成</li><li>版本发布前</li><li>重构/优化后</li></ul>',
            key_concepts='<ul><li><strong>测试范围</strong>：完整回归、部分回归、选择性回归</li><li><strong>自动化优先</strong>：回归测试是最适合自动化的测试类型</li><li><strong>风险驱动</strong>：根据变更的影响范围确定回归测试范围</li><li><strong>测试套件</strong>：维护稳定的回归测试用例集</li><li><strong>持续集成</strong>：回归测试是CI/CD流水线的核心环节</li></ul>',
            tools='<ul><li><strong>自动化框架</strong>：Selenium、Appium、Cypress、Playwright、Pytest</li><li><strong>CI/CD</strong>：Jenkins、GitLab CI、GitHub Actions、Azure DevOps</li><li><strong>测试管理</strong>：TestRail、Jira Xray、PractiTest</li><li><strong>用例选择</strong>：基于代码覆盖率、风险分析、变更影响分析</li><li><strong>结果分析</strong>：Allure Report、ExtentReports</li></ul>',
            examples='<strong>支付系统回归测试场景：</strong><br><ol><li><strong>Bug修复回归</strong>：修复了"支付超时后状态未更新"的Bug，需要回归测试：正常支付流程、支付超时场景、取消支付、重复支付、与该Bug相关的所有测试用例</li><li><strong>新功能回归</strong>：新增了"优惠券抵扣"功能，需要回归测试：不使用优惠券的正常支付流程、多种支付方式组合、订单计算逻辑、发票开具、与支付相关的所有历史功能</li><li><strong>重构回归</strong>：重构了订单创建的底层代码，需要回归测试：所有涉及订单的功能（创建、修改、取消、查询）、与订单相关的支付、库存、积分等联动功能、性能测试确保没有性能下降</li><li><strong>冒烟测试</strong>：每次代码提交后执行核心功能的快速回归测试：用户登录、商品浏览、加入购物车、下单支付，确保最核心的功能没有被破坏</li><li><strong>完整回归</strong>：版本发布前执行完整的回归测试，包括：所有功能测试用例、各种边界场景、异常处理、性能测试、兼容性测试</li><li><strong>自动化回归</strong>：CI/CD流水线中自动执行的回归测试：API自动化测试（Pytest + Requests）、UI自动化测试（Selenium或Cypress）、数据库数据一致性校验</li></ol>',
            sort_order=14
        ),
        TestType(
            name='探索性测试',
            category='其他测试类型',
            description='探索性测试是一种无预设脚本的测试方法，测试人员在测试过程中同时学习产品、设计测试、执行测试。依靠测试人员的经验、直觉和创造力发现隐蔽的缺陷。',
            purpose='发现脚本化测试难以发现的缺陷。深入探索产品的边界场景和异常情况。弥补结构化测试的不足。',
            when_to_use='<ul><li>需求不明确时</li><li>新产品早期测试</li><li>时间紧迫的项目</li><li>补充结构化测试</li><li>复杂业务场景测试</li></ul>',
            key_concepts='<ul><li><strong>同步学习</strong>：在测试过程中理解产品</li><li><strong>基于会话</strong>：Session-based Testing，限定时间的探索会话</li><li><strong>测试章程</strong>：Test Charter，指导探索的方向和目标</li><li><strong>自由发挥</strong>：不依赖预设脚本，根据实际情况调整测试</li><li><strong>经验依赖</strong>：高度依赖测试人员的技能和经验</li></ul>',
            tools='<ul><li><strong>会话测试管理</strong>：Session Tester、TestRail Session-Based</li><li><strong>笔记工具</strong>：OneNote、Evernote、Notion</li><li><strong>截图录屏</strong>：Snagit、LICEcap、OBS Studio</li><li><strong>思维导图</strong>：XMind、MindManager、FreeMind</li><li><strong>缺陷跟踪</strong>：Jira、Bugzilla、禅道</li></ul>',
            examples='<strong>社交平台探索性测试场景：</strong><br><ol><li><strong>并发操作探索</strong>：同时在网页端和手机端登录同一账号，两边同时进行：发送消息、修改个人资料、发布动态、删除动态，观察是否出现数据冲突、状态不一致</li><li><strong>边界数据探索</strong>：测试各种边界数据：用户名最大长度、简介最大长度、头像图片最大尺寸、一次最多选择多少张图片发布、消息最多输入多少字符</li><li><strong>异常流程探索</strong>：不走正常流程，尝试各种异常操作：注册到一半关闭页面、上传图片到一半取消、支付过程中网络断开、编辑到一半切换页面、快速连续点击按钮</li><li><strong>权限边界探索</strong>：测试权限的边界：普通用户能否通过修改URL访问管理员页面、已拉黑的用户能否通过某种方式查看动态、已退出的群组能否通过历史记录访问、不同隐私设置的内容在各种场景下的可见性</li><li><strong>性能极端探索</strong>：在数据量很大的情况下探索：有1000个好友时的列表滚动性能、有1000条未读消息时的应用启动速度、聊天记录很多时的搜索性能</li><li><strong>多任务并行探索</strong>：同时进行多个任务：上传视频时发送消息、下载文件时浏览动态、语音通话时切换到其他功能、拍照时收到来电</li></ol>',
            sort_order=15
        ),
        TestType(
            name='灰度测试',
            category='其他测试类型',
            description='灰度测试是在生产环境中对部分用户或部分功能进行的测试，介于测试环境和正式发布之间。通过小范围真实用户验证，降低全面发布的风险。',
            purpose='在真实生产环境中验证功能的稳定性和用户体验。收集真实用户反馈，发现测试环境难以模拟的问题。降低大规模发布的风险。',
            when_to_use='<ul><li>重大功能发布前</li><li>架构重构验证</li><li>性能优化效果验证</li><li>A/B测试</li><li>高风险变更验证</li></ul>',
            key_concepts='<ul><li><strong>灰度策略</strong>：按用户ID、地区、设备类型、比例等灰度</li><li><strong>流量控制</strong>：逐步扩大灰度范围，观察指标</li><li><strong>监控告警</strong>：灰度期间密切监控各项指标</li><li><strong>快速回滚</strong>：发现问题时能够快速回滚</li><li><strong>数据隔离</strong>：灰度数据与正式数据的隔离或兼容</li></ul>',
            tools='<ul><li><strong>灰度发布</strong>：Kubernetes滚动更新、Nginx灰度、API网关灰度</li><li><strong>流量染色</strong>：基于Header、Cookie的流量标识</li><li><strong>功能开关</strong>：Feature Flags、LaunchDarkly、ConfigCat</li><li><strong>全链路监控</strong>：SkyWalking、Jaeger、Pinpoint</li><li><strong>用户反馈</strong>：App内反馈、Hotjar用户行为分析</li></ul>',
            examples='<strong>电商新功能灰度测试场景：</strong><br><ol><li><strong>灰度策略设计</strong>：新的"直播购物"功能，设计灰度策略：第一阶段（1%）内部员工、第二阶段（5%）忠诚用户（过去一年消费10单以上）、第三阶段（20%）随机用户、第四阶段（100%）全量发布</li><li><strong>功能开关控制</strong>：使用Feature Flags控制功能可见性，未灰度用户看不到直播入口，灰度用户可以看到</li><li><strong>灰度期间监控</strong>：密切关注：直播功能的错误率、API响应时间、服务器资源使用率、数据库慢查询、用户投诉量</li><li><strong>数据兼容测试</strong>：验证：灰度用户产生的直播订单与现有订单系统的兼容性、直播相关数据与数据仓库的同步、报表统计是否正确包含灰度数据</li><li><strong>用户反馈收集</strong>：收集灰度用户的反馈：通过App内反馈入口、客服记录、用户行为分析（Hotjar录屏）、NPS评分</li><li><strong>灰度回滚演练</strong>：演练发现问题时的回滚流程：关闭功能开关、验证功能入口消失、已产生的数据处理、通知相关用户</li></ol>',
            sort_order=16
        ),
        TestType(
            name='Alpha/Beta测试',
            category='其他测试类型',
            description='Alpha测试是在开发环境由内部用户进行的测试，Beta测试是在生产环境由真实用户进行的测试。是产品正式发布前的最后验证阶段。',
            purpose='在真实用户场景中发现问题。收集用户体验反馈。验证产品的市场接受度。',
            when_to_use='<ul><li>产品功能基本完成后</li><li>正式发布前1-2周</li><li>需要用户真实反馈</li><li>验证产品市场 fit</li><li>重大版本更新</li></ul>',
            key_concepts='<ul><li><strong>Alpha测试</strong>：内部人员在开发环境测试，可随时调试</li><li><strong>Beta测试</strong>：真实用户在生产环境测试，获取真实反馈</li><li><strong>封闭Beta</strong>：邀请少量特定用户参与</li><li><strong>开放Beta</strong>：对所有感兴趣的用户开放</li><li><strong>反馈收集</strong>：系统化收集和分析用户反馈</li></ul>',
            tools='<ul><li><strong>Beta分发</strong>：TestFlight（iOS）、Google Play Beta、Firebase App Distribution</li><li><strong>反馈收集</strong>：Instabug、Bugsee、TestFairy</li><li><strong>用户调研</strong>：SurveyMonkey、Typeform、问卷星</li><li><strong>数据分析</strong>：Firebase Analytics、Mixpanel、友盟</li><li><strong>崩溃报告</strong>：Crashlytics、Sentry、Bugly</li></ul>',
            examples='<strong>移动应用Beta测试场景：</strong><br><ol><li><strong>TestFlight分发</strong>：使用TestFlight向1000名测试用户分发Beta版本，包括：内部测试员（25名内部员工）、外部测试员（1000名真实用户，通过邀请链接注册）</li><li><strong>测试任务设计</strong>：为Beta测试用户设计明确的测试任务：完成新手引导、体验核心功能（如发布内容、互动交流）、尝试边缘场景（如断网、弱网）、体验新功能并给出反馈</li><li><strong>崩溃监控</strong>：集成Firebase Crashlytics，实时监控：崩溃次数、崩溃率、崩溃堆栈、影响用户数、崩溃设备分布</li><li><strong>用户行为分析</strong>：使用Mixpanel分析：用户留存率（次日、7日、30日）、功能使用率（哪些功能最常用/最不常用）、用户旅程（用户从哪里流失）、关键漏斗转化率</li><li><strong>反馈收集</strong>：通过多种渠道收集反馈：App内反馈入口（截图+标注+描述）、Beta用户微信群、用户调研问卷（NPS评分、满意度评分、开放问题）、客服记录</li><li><strong>版本迭代</strong>：根据Beta测试反馈进行迭代：修复高优先级崩溃、优化用户体验问题、调整不符合用户习惯的设计、补充缺失的引导提示</li></ol>',
            sort_order=17
        ),
        TestType(
            name='Monkey测试',
            category='其他测试类型',
            description='Monkey测试是一种随机、自动化的测试方法，通过模拟用户的随机操作（点击、滑动、按键等）来发现应用的崩溃、无响应等稳定性问题。特别适合发现内存泄漏、异常处理等隐蔽问题。',
            purpose='发现应用在长时间、高强度使用下的稳定性问题。验证应用的异常处理和容错能力。发现内存泄漏等缓慢积累的问题。',
            when_to_use='<ul><li>功能开发完成后</li><li>性能优化前后</li><li>版本发布前</li><li>内存泄漏 suspect</li><li>长时间运行测试</li></ul>',
            key_concepts='<ul><li><strong>随机操作</strong>：随机生成点击、滑动、按键等事件</li><li><strong>事件流</strong>：连续发送大量随机事件</li><li><strong>崩溃捕获</strong>：捕获ANR、Crash等异常</li><li><strong>压力测试</strong>：高强度、长时间运行</li><li><strong>无预设</strong>：不依赖业务逻辑，纯随机操作</li></ul>',
            tools='<ul><li><strong>Android Monkey</strong>：Android SDK自带Monkey工具</li><li><strong>iOS Monkey</strong>：XCTest UI Monkeys、第三方框架</li><li><strong>增强版</strong>：Appetizer、Maxim、Smart Monkey</li><li><strong>崩溃分析</strong>：Bugly、Sentry、Firebase Crashlytics</li><li><strong>性能监控</strong>：PerfDog、GT、Android Studio Profiler</li></ul>',
            examples='<strong>移动应用Monkey测试场景：</strong><br><ol><li><strong>基础Monkey测试</strong>：使用Android原生Monkey命令：`adb shell monkey -p com.example.app -v --throttle 300 --pct-touch 45 --pct-motion 10 --pct-nav 10 --pct-majornav 5 --pct-syskeys 5 --pct-appswitch 10 --pct-anyevent 15 10000`，执行10000次随机操作</li><li><strong>ANR测试</strong>：执行Monkey测试，观察是否产生ANR（Application Not Responding），如果有，分析traces.txt文件定位问题</li><li><strong>崩溃测试</strong>：执行Monkey测试，捕获所有崩溃，包括：NullPointerException、IndexOutOfBoundsException、OutOfMemoryError、SecurityException等</li><li><strong>内存泄漏测试</strong>：在Monkey测试过程中监控内存使用：使用Android Studio Profiler观察内存趋势、使用LeakCanary自动检测内存泄漏、多次执行Monkey后观察内存是否持续增长</li><li><strong>长时间稳定性测试</strong>：执行超长Monkey测试：设置--throttle 500（500ms间隔）、执行50000次操作、持续数小时，观察应用是否能稳定运行</li><li><strong>自定义Monkey测试</strong>：使用更智能的Monkey工具（如Maxim）：支持黑白名单（只测试特定Activity）、支持自定义事件序列、支持截图记录、支持深度优先遍历而非纯随机</li></ol>',
            sort_order=18
        ),
        TestType(
            name='埋点测试',
            category='专项测试类',
            description='埋点测试验证数据采集埋点的正确性，包括事件触发、属性上报、数据格式等。是数据分析、用户行为分析、A/B测试的数据基础，直接影响业务决策的准确性。',
            purpose='确保埋点数据的准确性、完整性和及时性。为数据分析、用户研究、业务决策提供可靠的数据基础。',
            when_to_use='<ul><li>新埋点开发完成</li><li>埋点逻辑变更</li><li>版本发布前</li><li>数据异常报警后</li><li>数据报表核对时</li></ul>',
            key_concepts='<ul><li><strong>事件埋点</strong>：用户行为事件的采集（点击、浏览、购买等）</li><li><strong>属性埋点</strong>：事件附带的属性信息（商品ID、价格、用户ID等）</li><li><strong>用户属性</strong>：用户画像信息（年龄、性别、地域、设备等）</li><li><strong>上报策略</strong>：实时上报、批量上报、WiFi下上报、失败重试</li><li><strong>数据校验</strong>：采集数据与预期数据的一致性校验</li></ul>',
            tools='<ul><li><strong>埋点验证</strong>：Charles、Fiddler、mitmproxy抓包分析</li><li><strong>SDK调试</strong>：各分析平台Debug模式（友盟、TalkingData、GrowingIO）</li><li><strong>埋点管理</strong>：神策埋点管理、GrowingIO埋点方案</li><li><strong>数据核对</strong>：Excel对比、SQL查询、数据平台报表</li><li><strong>自动化测试</strong>：Appium + 抓包、Selenium + 代理</li></ul>',
            examples='<strong>电商App埋点测试场景：</strong><br><ol><li><strong>点击事件埋点测试</strong>：点击"加入购物车"按钮，使用Charles抓包验证：是否触发了add_to_cart事件、事件属性是否包含（product_id、product_name、price、quantity、user_id等）、属性值是否正确、事件是否成功上报到服务器</li><li><strong>页面浏览埋点测试</strong>：进入商品详情页，验证：是否触发了page_view事件、page_name是否为"商品详情页"、page参数是否包含（product_id、category_id、from_page等）、是否有重复上报或漏报</li><li><strong>购买转化漏斗埋点测试</strong>：完成一次完整的购买流程，验证漏斗各环节的埋点：浏览商品(page_view) → 加入购物车(add_to_cart) → 提交订单(submit_order) → 支付成功(payment_success)，每个事件都要验证触发时机和属性正确性</li><li><strong>属性完整性测试</strong>：测试各种场景下的属性完整性：不同用户类型（新用户/老用户/VIP用户）、不同商品类型（实物/虚拟/服务）、不同支付方式（微信/支付宝/银行卡）、不同设备（iOS/Android/小程序）</li><li><strong>数据一致性核对</strong>：测试结束后进行数据核对：App端触发的事件数 vs 后端接收的事件数 vs 数据平台显示的事件数，三方数据是否一致；抽样核对具体事件的属性值</li><li><strong>异常场景测试</strong>：测试各种异常场景下的埋点行为：弱网下是否缓存并重试、断网后恢复网络是否补发、App崩溃前的事件是否丢失、用户退出登录后是否停止上报用户信息</li></ol>',
            sort_order=19
        ),
        TestType(
            name='流程测试',
            category='功能测试类',
            description='流程测试验证端到端的业务流程完整性，模拟真实用户完成一个完整业务目标的全过程。关注流程中各环节的衔接、数据流转、状态变化和最终结果。',
            purpose='确保完整的业务流程能够顺利完成。发现流程中各环节衔接的问题。验证数据在流程中的一致性和正确性。',
            when_to_use='<ul><li>系统集成测试阶段</li><li>端到端测试</li><li>用户验收测试</li><li>业务流程变更后</li><li>新系统上线前</li></ul>',
            key_concepts='<ul><li><strong>端到端</strong>：从用户视角的完整业务流程</li><li><strong>数据流转</strong>：数据在各系统/模块间的传递</li><li><strong>状态机</strong>：业务对象的状态变化</li><li><strong>异常分支</strong>：流程中的异常处理和回退</li><li><strong>角色协作</strong>：多角色参与的流程（如审批流）</li></ul>',
            tools='<ul><li><strong>E2E自动化</strong>：Selenium、Cypress、Playwright、Robot Framework</li><li><strong>流程建模</strong>：BPMN、Visio、Draw.io</li><li><strong>数据验证</strong>：数据库查询、API校验、报表核对</li><li><strong>测试管理</strong>：TestRail、Jira Xray（维护流程测试用例）</li><li><strong>API测试</strong>：Postman、RestAssured（流程中的API调用）</li></ul>',
            examples='<strong>电商订单完整流程测试场景：</strong><br><ol><li><strong>正常购买流程</strong>：模拟用户完成一次完整购买：用户登录 → 浏览商品 → 搜索商品 → 查看商品详情 → 选择规格（颜色、尺寸）→ 加入购物车 → 查看购物车 → 去结算 → 选择收货地址 → 选择支付方式 → 提交订单 → 完成支付 → 查看订单状态 → 商家发货 → 用户确认收货 → 评价商品，验证每个环节的正确性和数据一致性</li><li><strong>订单取消流程</strong>：测试各种取消场景：未支付取消（用户主动取消、超时自动取消）、已支付未发货取消（申请退款 → 商家同意 → 退款到账）、已发货取消（拒收 → 退回商家 → 退款），验证订单状态变化、库存变化、金额变化</li><li><strong>退换货流程</strong>：测试完整的退换货流程：用户申请退换货 → 商家审核（同意/拒绝）→ 审核通过后用户寄回商品 → 商家确认收货 → 商家处理（退款/换货）→ 用户收到退款/新商品，验证各环节的状态流转和数据一致性</li><li><strong>异常流程测试</strong>：测试流程中的异常处理：支付过程中网络中断（恢复后能否继续支付或订单关闭）、库存不足时下单（是否正确提示）、优惠券过期时使用（是否正确处理）、收货地址不存在时提交订单（是否正确校验）</li><li><strong>数据一致性校验</strong>：在流程各节点进行数据校验：订单创建后验证orders表、order_items表、order_logs表的数据一致性；支付成功后验证user_balance表、transaction_logs表、order_status的一致性；库存变化验证inventory表、inventory_logs表的一致性</li><li><strong>多角色协作流程</strong>：测试需要多角色参与的流程：用户申请退款 → 客服审核 → 财务退款 → 用户确认，每个角色登录系统执行自己的操作，验证流程在角色间的正确流转</li></ol>',
            sort_order=20
        )
    ]
    
    for t in test_types:
        existing = TestType.query.filter_by(name=t.name).first()
        if not existing:
            db.session.add(t)
        else:
            sync_existing_record(existing, t)
    
    test_processes = [
        TestProcess(
            stage_name='软件开发生命周期概述',
            stage_order=1,
            description='软件开发生命周期(SDLC)是软件从概念到退役的完整过程，涵盖需求分析、设计、编码、测试、部署和维护等阶段。理解SDLC是掌握测试流程的基础。',
            key_activities='<ul><li><strong>需求阶段</strong>：需求收集、分析、评审、确认</li><li><strong>设计阶段</strong>：架构设计、详细设计、技术选型</li><li><strong>编码阶段</strong>：代码实现、单元测试、代码审查</li><li><strong>测试阶段</strong>：测试计划、测试设计、测试执行、测试报告</li><li><strong>部署阶段</strong>：发布计划、环境准备、部署执行、产品验收</li><li><strong>维护阶段</strong>：线上监控、问题处理、项目复盘、流程优化</li></ul>',
            deliverables='<ul><li><strong>需求阶段</strong>：需求规格说明书、需求追溯矩阵</li><li><strong>设计阶段</strong>：架构设计文档、详细设计文档、数据库设计</li><li><strong>编码阶段</strong>：源代码、单元测试报告、代码审查记录</li><li><strong>测试阶段</strong>：测试计划、测试用例、测试报告、缺陷报告</li><li><strong>部署阶段</strong>：部署计划、发布说明、验收报告</li><li><strong>维护阶段</strong>：运维报告、问题分析报告、复盘总结</li></ul>',
            best_practices='<ul><li><strong>迭代开发</strong>：采用敏捷/DevOps等迭代开发模式，缩短反馈周期</li><li><strong>左移测试</strong>：将测试活动提前到需求和设计阶段，更早发现问题</li><li><strong>持续集成</strong>：建立CI/CD流水线，实现自动化构建、测试、部署</li><li><strong>质量门禁</strong>：在各阶段设置质量门禁，未达标不进入下一阶段</li><li><strong>度量驱动</strong>：建立度量体系，用数据驱动过程改进</li></ul>',
            common_pitfalls='<ul><li><strong>瀑布思维</strong>：严格按阶段划分，前一阶段不完成后一阶段不开始，缺乏灵活性</li><li><strong>测试后置</strong>：将测试全部放在编码完成后，问题发现太晚，修复成本高</li><li><strong>文档泛滥</strong>：过度追求文档完整性，忽视实际沟通和协作</li><li><strong>缺乏反馈</strong>：各阶段之间缺乏有效反馈，问题不能及时暴露</li><li><strong>忽视维护</strong>：认为上线即完成，忽视线上问题和持续改进</li></ul>',
            optimization_techniques='<ul><li><strong>敏捷开发</strong>：Scrum、Kanban等敏捷方法论，拥抱变化</li><li><strong>DevOps</strong>：开发与运维一体化，实现持续交付</li><li><strong>测试左移</strong>：在需求阶段就开始测试活动</li><li><strong>自动化测试</strong>：单元测试、接口测试、UI测试自动化</li><li><strong>持续反馈</strong>：每日站会、迭代评审、回顾会议</li></ul>',
            metrics='<ul><li><strong>进度指标</strong>：各阶段完成率、计划vs实际进度</li><li><strong>质量指标</strong>：缺陷密度、逃逸缺陷数、测试覆盖率</li><li><strong>效率指标</strong>：需求变更率、返工率、交付周期</li><li><strong>流程指标</strong>：各阶段流转时间、阻塞点数量、评审通过率</li></ul>'
        ),
        TestProcess(
            stage_name='需求阶段 - 质量预防',
            stage_order=2,
            description='需求阶段是软件开发生命周期的起点，也是质量预防的关键环节。在这个阶段明确"做什么"，对后续开发和测试效率影响巨大。通过需求分析反馈机制，可以在早期发现和解决问题。',
            key_activities='<ul><li><strong>需求收集</strong>：与利益相关者沟通，收集原始需求</li><li><strong>需求分析</strong>：分析需求的完整性、一致性、可测试性</li><li><strong>需求评审</strong>：组织产研测三方评审，确认需求理解一致</li><li><strong>需求分析反馈</strong>：测试团队提前介入，提供测试视角的反馈</li><li><strong>需求确认</strong>：各方确认需求规格，形成基线</li><li><strong>需求变更管理</strong>：建立变更控制流程，管理需求变更</li></ul>',
            deliverables='<ul><li><strong>业务需求文档(BRD)</strong>：业务目标、用户故事、业务规则</li><li><strong>需求规格说明书(SRS)</strong>：功能需求、非功能需求、接口需求</li><li><strong>需求追溯矩阵(RTM)</strong>：需求与测试用例的追溯关系</li><li><strong>需求评审报告</strong>：评审记录、问题清单、决议</li><li><strong>需求分析反馈报告</strong>：测试团队的需求分析反馈</li></ul>',
            best_practices='<ul><li><strong>测试左移</strong>：测试团队在需求阶段就介入，提供测试视角</li><li><strong>需求分析反馈</strong>：测试团队输出需求分析反馈文档，识别模糊点、风险点、可测试性问题</li><li><strong>三方评审</strong>：产品、开发、测试三方共同评审需求，确保理解一致</li><li><strong>实例化需求</strong>：通过具体例子澄清需求，避免歧义</li><li><strong>验收标准先行</strong>：在需求阶段就定义好验收标准</li></ul>',
            common_pitfalls='<ul><li><strong>需求模糊</strong>：需求描述不清晰，存在歧义，导致各方理解不一致</li><li><strong>需求遗漏</strong>：重要功能或场景被遗漏，后期才发现</li><li><strong>需求镀金</strong>：添加不必要的功能，增加开发和测试成本</li><li><strong>变更失控</strong>：需求变更频繁且无控制，导致范围蔓延</li><li><strong>测试后置</strong>：测试团队在需求阶段不参与，后期才理解需求</li></ul>',
            optimization_techniques='<ul><li><strong>需求分析反馈机制</strong>：<br>- 测试团队收到需求后进行系统性分析<br>- 识别：模糊点、矛盾点、遗漏点、风险点、可测试性问题<br>- 输出需求分析反馈文档，与产品团队沟通确认<br>- 闭环：确认所有问题都得到解决</li><li><strong>风险识别</strong>：在需求阶段识别业务风险和技术风险</li><li><strong>测试驱动开发(TDD)</strong>：先写测试用例，再写代码</li><li><strong>行为驱动开发(BDD)</strong>：用自然语言描述需求，作为验收标准</li></ul>',
            metrics='<ul><li><strong>需求质量指标</strong>：需求评审缺陷数、需求澄清次数、需求歧义率</li><li><strong>需求稳定性指标</strong>：需求变更率、需求冻结期长度</li><li><strong>需求覆盖率指标</strong>：测试用例需求覆盖率、需求追溯完整性</li><li><strong>效率指标</strong>：需求分析周期、需求评审周期</li></ul>'
        ),
        TestProcess(
            stage_name='设计阶段 - 技术方案制定',
            stage_order=3,
            description='设计阶段是将需求转化为技术方案的关键环节。在这个阶段确定"怎么做"，包括系统架构、模块划分、接口设计、数据库设计等。测试团队也应参与设计评审，确保方案的可测试性。',
            key_activities='<ul><li><strong>架构设计</strong>：系统整体架构、技术选型、模块划分</li><li><strong>详细设计</strong>：模块内部设计、算法设计、数据结构设计</li><li><strong>接口设计</strong>：API接口定义、数据格式、协议规范</li><li><strong>数据库设计</strong>：表结构设计、索引设计、关系设计</li><li><strong>设计评审</strong>：技术方案评审，包括可测试性评审</li><li><strong>测试设计准备</strong>：测试团队根据设计文档准备测试策略</li></ul>',
            deliverables='<ul><li><strong>架构设计文档</strong>：系统架构图、技术选型说明、模块划分</li><li><strong>详细设计文档</strong>：模块设计、类图、时序图、算法说明</li><li><strong>接口设计文档</strong>：API清单、请求/响应格式、错误码定义</li><li><strong>数据库设计文档</strong>：ER图、表结构、索引设计、数据字典</li><li><strong>设计评审报告</strong>：评审记录、问题清单、改进建议</li><li><strong>测试策略文档</strong>：测试范围、测试重点、测试方法</li></ul>',
            best_practices='<ul><li><strong>测试参与设计评审</strong>：测试团队参与设计评审，关注可测试性、可监控性</li><li><strong>接口先行</strong>：先定义好接口规范，前后端可以并行开发</li><li><strong>设计模式</strong>：合理使用设计模式，提高代码可维护性和可测试性</li><li><strong>关注点分离</strong>：分层架构，业务逻辑与数据访问分离</li><li><strong>容错设计</strong>：在设计阶段考虑异常处理和容错机制</li></ul>',
            common_pitfalls='<ul><li><strong>过度设计</strong>：设计过于复杂，超出实际需求，增加实现和测试难度</li><li><strong>设计不足</strong>：设计过于简单，无法应对需求变化和扩展</li><li><strong>接口不清晰</strong>：接口定义模糊，前后端联调时问题频发</li><li><strong>忽视可测试性</strong>：设计时不考虑测试需求，导致测试困难</li><li><strong>缺乏设计评审</strong>：设计方案没有经过充分评审，问题在编码阶段才暴露</li></ul>',
            optimization_techniques='<ul><li><strong>测试件设计引导软件设计</strong>：在设计阶段就考虑测试件的设计，使软件更易于测试</li><li><strong>契约驱动开发(Contract-First)</strong>：先定义接口契约，再进行实现</li><li><strong>API优先设计</strong>：以API为中心进行设计，便于集成和测试</li><li><strong>设计模式应用</strong>：工厂模式、单例模式、策略模式等提高可测试性</li><li><strong>依赖注入</strong>：通过依赖注入降低耦合，提高可测试性</li></ul>',
            metrics='<ul><li><strong>设计质量指标</strong>：设计评审缺陷数、设计变更次数</li><li><strong>可测试性指标</strong>：测试点识别率、可自动化测试比例</li><li><strong>接口质量指标</strong>：接口变更率、联调问题数</li><li><strong>进度指标</strong>：设计周期、设计评审周期</li></ul>'
        ),
        TestProcess(
            stage_name='编码阶段 - 功能实现',
            stage_order=4,
            description='编码阶段是将设计转化为可执行代码的阶段。在这个阶段，开发人员编写代码、进行单元测试、代码审查。测试团队可以开始编写测试用例，并与开发保持密切沟通。',
            key_activities='<ul><li><strong>代码实现</strong>：按照设计文档编写功能代码</li><li><strong>单元测试</strong>：开发人员编写单元测试，验证代码逻辑</li><li><strong>代码审查</strong>：团队成员互相审查代码，发现潜在问题</li><li><strong>静态代码分析</strong>：使用工具进行代码质量检查</li><li><strong>持续集成</strong>：代码提交后自动构建和测试</li><li><strong>测试用例编写</strong>：测试团队根据需求和设计编写测试用例</li></ul>',
            deliverables='<ul><li><strong>源代码</strong>：功能代码、配置文件、构建脚本</li><li><strong>单元测试代码</strong>：JUnit/Pytest等单元测试代码</li><li><strong>代码审查记录</strong>：审查问题、改进建议、确认记录</li><li><strong>静态分析报告</strong>：代码质量、安全漏洞、重复代码等</li><li><strong>测试用例</strong>：功能测试用例、接口测试用例</li><li><strong>构建产物</strong>：可部署的应用包、容器镜像</li></ul>',
            best_practices='<ul><li><strong>测试驱动开发(TDD)</strong>：先写单元测试，再写功能代码</li><li><strong>代码规范</strong>：遵循团队编码规范，使用代码检查工具</li><li><strong>小步提交</strong>：频繁小粒度提交代码，便于问题定位</li><li><strong>持续集成</strong>：每次代码提交都触发自动化构建和测试</li><li><strong>测试人员与开发人员紧密合作</strong>：及时沟通需求理解、实现细节</li></ul>',
            common_pitfalls='<ul><li><strong>忽视单元测试</strong>：开发人员不写或写不好单元测试，依赖后续测试阶段</li><li><strong>代码质量差</strong>：代码可读性差、重复代码多、缺乏注释</li><li><strong>缺乏代码审查</strong>：代码没有经过审查，问题在测试阶段才发现</li><li><strong>自测不充分</strong>：开发人员自测不够，提测质量低</li><li><strong>测试与开发不同步</strong>：测试用例编写与开发实现脱节</li></ul>',
            optimization_techniques='<ul><li><strong>测试驱动开发(TDD)</strong>：<br>- 红：先写一个失败的单元测试<br>- 绿：编写最少的代码使测试通过<br>- 重构：优化代码，保持测试通过</li><li><strong>结对编程</strong>：两个开发人员一起编码，实时审查</li><li><strong>代码审查检查清单</strong>：建立代码审查检查清单，确保审查全面</li><li><strong>SonarQube等代码质量平台</strong>：持续监控代码质量</li><li><strong>自动化代码格式化</strong>：使用Prettier、Black等工具统一代码风格</li></ul>',
            metrics='<ul><li><strong>代码质量指标</strong>：圈复杂度、代码重复率、静态分析告警数</li><li><strong>单元测试指标</strong>：单元测试覆盖率、测试通过率、测试执行时间</li><li><strong>代码审查指标</strong>：审查发现问题数、审查周期</li><li><strong>构建指标</strong>：构建成功率、构建时间</li></ul>'
        ),
        TestProcess(
            stage_name='测试阶段 - 质量评估',
            stage_order=5,
            description='测试阶段是对软件质量进行系统性评估的关键阶段。包括测试计划、测试设计、测试执行、测试报告四个核心环节。通过系统性的测试，发现缺陷、评估质量、为发布决策提供依据。',
            key_activities='<ul><li><strong>测试计划</strong>：确定测试范围、测试策略、资源安排、进度计划</li><li><strong>测试设计</strong>：根据需求和设计，设计测试用例和测试数据</li><li><strong>测试环境准备</strong>：搭建测试环境、准备测试数据、配置测试工具</li><li><strong>测试执行</strong>：执行测试用例、记录结果、跟踪缺陷</li><li><strong>缺陷管理</strong>：缺陷报告、缺陷跟踪、缺陷验证、缺陷分析</li><li><strong>测试报告</strong>：汇总测试结果、评估质量、给出建议</li></ul>',
            deliverables='<ul><li><strong>测试计划</strong>：测试范围、测试策略、资源计划、风险评估</li><li><strong>测试用例</strong>：功能测试用例、接口测试用例、性能测试用例</li><li><strong>测试数据</strong>：测试准备的数据、数据生成脚本</li><li><strong>测试执行记录</strong>：用例执行结果、测试日志</li><li><strong>缺陷报告</strong>：详细的缺陷描述、重现步骤、影响分析</li><li><strong>测试报告</strong>：测试总结、质量评估、发布建议</li></ul>',
            best_practices='<ul><li><strong>分层测试</strong>：单元测试、接口测试、UI测试按金字塔模型分配</li><li><strong>风险驱动测试</strong>：根据风险优先级确定测试重点和深度</li><li><strong>测试用例评审</strong>：测试用例经过评审，确保覆盖全面</li><li><strong>冒烟测试</strong>：版本提测后先进行冒烟测试，确认版本可测</li><li><strong>回归测试</strong>：缺陷修复后进行回归测试，确保没有引入新问题</li></ul>',
            common_pitfalls='<ul><li><strong>测试计划不完善</strong>：测试范围不清晰、资源安排不合理、风险考虑不足</li><li><strong>测试用例质量低</strong>：用例覆盖不全、步骤不清晰、预期结果不明确</li><li><strong>测试环境不稳定</strong>：测试环境与生产差异大、环境频繁变动</li><li><strong>缺陷管理混乱</strong>：缺陷描述不清、状态流转不规范、沟通效率低</li><li><strong>测试报告流于形式</strong>：只罗列数据，缺乏深入分析和建议</li></ul>',
            optimization_techniques='<ul><li><strong>测试计划优化</strong>：<br>- 明确测试范围和边界<br>- 基于风险确定测试优先级<br>- 合理安排资源和进度<br>- 识别风险并制定应对措施</li><li><strong>测试设计优化</strong>：<br>- 使用等价类划分、边界值分析、判定表等设计技术<br>- 保证需求覆盖率和代码覆盖率<br>- 测试数据准备自动化</li><li><strong>测试执行监控</strong>：<br>- 运用测试执行策略和监控方式<br>- 对风险点、阻塞点、问题集中点沟通疏导<br>- 风险识别、缓解、版本控制</li><li><strong>测试阻塞处理</strong>：<br>- 测试阻塞：增加经验丰富人员、增加校验手段（稳定性、性能优化、自动化回归等）、回退不测等<br>- 产品问题阻塞：确认、延期、修复<br>- 开发问题阻塞：增加开发解决、集中精力攻关</li></ul>',
            metrics='<ul><li><strong>测试覆盖率指标</strong>：需求覆盖率、用例通过率、代码覆盖率</li><li><strong>缺陷相关指标</strong>：缺陷密度、缺陷严重程度分布、缺陷修复率、逃逸缺陷数</li><li><strong>进度指标</strong>：测试执行进度、用例执行效率</li><li><strong>质量指标</strong>：P0/P1缺陷数、回归测试通过率、版本质量评估</li></ul>'
        ),
        TestProcess(
            stage_name='部署阶段 - 发布与验收',
            stage_order=6,
            description='部署阶段是将软件发布到生产环境的阶段。优化后的流程在发布前增加了产品验收环节，确保产品符合预期后再上线。包括发布计划、环境准备、部署执行、产品验收等活动。',
            key_activities='<ul><li><strong>发布计划</strong>：制定发布策略、时间窗口、回滚计划</li><li><strong>环境准备</strong>：生产环境配置、数据准备、依赖检查</li><li><strong>预发布验证</strong>：在预发布环境进行最终验证</li><li><strong>部署执行</strong>：执行部署脚本、监控部署过程</li><li><strong>产品验收</strong>：产品团队进行验收，确认功能符合需求</li><li><strong>发布监控</strong>：发布后密切监控系统状态和业务指标</li></ul>',
            deliverables='<ul><li><strong>发布计划</strong>：发布内容、时间安排、回滚策略、通知范围</li><li><strong>部署文档</strong>：部署步骤、配置清单、验证清单</li><li><strong>验收报告</strong>：产品验收结果、遗留问题清单</li><li><strong>发布说明</strong>：新功能介绍、变更内容、已知问题</li><li><strong>监控报告</strong>：发布后监控指标、异常告警</li><li><strong>回滚记录</strong>：如果需要回滚，记录回滚原因和过程</li></ul>',
            best_practices='<ul><li><strong>产品验收</strong>：发布前由产品团队进行验收，确认功能符合需求</li><li><strong>灰度发布</strong>：先发布给部分用户，观察稳定后再全量</li><li><strong>蓝绿部署</strong>：两套环境，切换时流量割接，便于快速回滚</li><li><strong>自动化部署</strong>：使用CI/CD工具实现自动化部署</li><li><strong>发布监控</strong>：发布后密切监控关键指标，发现问题及时处理</li></ul>',
            common_pitfalls='<ul><li><strong>缺乏产品验收</strong>：发布前没有经过产品验收，上线后发现不符合需求</li><li><strong>发布计划不周</strong>：时间选择不合理、回滚计划缺失</li><li><strong>环境差异</strong>：测试环境与生产环境差异大，导致发布问题</li><li><strong>缺乏监控</strong>：发布后没有有效监控，问题不能及时发现</li><li><strong>回滚困难</strong>：没有准备回滚方案，出现问题无法快速回滚</li></ul>',
            optimization_techniques='<ul><li><strong>产品验收机制</strong>：<br>- 测试通过后，产品团队进行验收<br>- 验收重点：核心功能、用户体验、需求符合度<br>- 验收通过才能上线，不通过返回修改</li><li><strong>灰度发布策略</strong>：<br>- 按用户ID、地区、比例等进行灰度<br>- 逐步扩大灰度范围<br>- 密切监控灰度用户的指标</li><li><strong>自动化部署流水线</strong>：<br>- 构建 → 测试 → 预发布 → 生产<br>- 每个阶段设置质量门禁<br>- 一键部署、一键回滚</li><li><strong>发布验证清单</strong>：<br>- 部署前检查项<br>- 部署后验证项<br>- 功能验证、性能验证、安全验证</li></ul>',
            metrics='<ul><li><strong>发布频率指标</strong>：发布周期、发布次数</li><li><strong>发布质量指标</strong>：发布成功率、回滚次数、发布后缺陷数</li><li><strong>效率指标</strong>：部署时间、回滚时间</li><li><strong>验收指标</strong>：验收通过率、验收发现问题数</li></ul>'
        ),
        TestProcess(
            stage_name='维护阶段 - 持续改进',
            stage_order=7,
            description='维护阶段是软件上线后的持续运营阶段。优化后的流程增加了项目复盘环节，通过项目复盘进行质量改进，反哺下一个周期的需求分析。包括线上监控、问题处理、项目复盘、流程优化等活动。',
            key_activities='<ul><li><strong>线上监控</strong>：监控系统状态、业务指标、用户行为</li><li><strong>问题响应</strong>：线上问题发现、响应、处理</li><li><strong>线上问题根因分析</strong>：深入分析问题根因，制定纠正预防措施</li><li><strong>项目复盘</strong>：版本/项目结束后进行复盘，总结经验教训</li><li><strong>流程优化</strong>：根据复盘结果优化流程和规范</li><li><strong>知识沉淀</strong>：将经验教训沉淀到组织知识库</li></ul>',
            deliverables='<ul><li><strong>运维报告</strong>：系统运行状态、告警记录、处理记录</li><li><strong>问题分析报告</strong>：问题描述、根因分析、改进措施</li><li><strong>复盘总结报告</strong>：项目亮点、问题不足、改进建议</li><li><strong>流程更新文档</strong>：优化后的流程、规范、检查清单</li><li><strong>知识库更新</strong>：案例分析、最佳实践、经验分享</li></ul>',
            best_practices='<ul><li><strong>测试右移</strong>：将质量保障活动延伸到线上，关注线上问题和用户反馈</li><li><strong>项目复盘</strong>：每个版本/项目结束后进行复盘，不指责、聚焦改进</li><li><strong>根因分析</strong>：使用5 Whys、鱼骨图等方法深入分析问题根因</li><li><strong>持续优化</strong>：将复盘发现的问题转化为流程改进措施</li><li><strong>知识沉淀</strong>：将经验教训沉淀下来，避免重复踩坑</li></ul>',
            common_pitfalls='<ul><li><strong>上线即结束</strong>：认为上线就是项目完成，忽视后续监控和改进</li><li><strong>问题处理治标不治本</strong>：只处理问题现象，不分析根因，问题重复发生</li><li><strong>缺乏复盘</strong>：项目结束后不总结，经验教训流失</li><li><strong>复盘流于形式</strong>：复盘变成批评会，不聚焦改进</li><li><strong>改进不落地</strong>：复盘发现了问题，但没有转化为实际行动</li></ul>',
            optimization_techniques='<ul><li><strong>测试右移策略</strong>：<br>- 上线验收：确保发布质量<br>- 线上问题根因分析：深入分析，防止重复发生<br>- 项目复盘：总结经验，持续改进<br>- 流程优化：将改进措施落地</li><li><strong>项目版本右移</strong>：<br>- 不仅跟进线上问题<br>- 优化整体结构，使后续项目更顺畅</li><li><strong>项目复盘方法</strong>：<br>- 收集数据：项目关键指标、问题记录、反馈<br>- 分析原因：什么做得好、什么可以改进、为什么<br>- 制定行动：具体的改进措施、责任人、时间点<br>- 跟踪落地：在下个周期验证改进效果</li><li><strong>根因分析技术</strong>：<br>- 5 Whys：连续问5个为什么<br>- 鱼骨图：人、机、料、法、环各维度分析<br>- 故障树分析：从结果倒推原因</li></ul>',
            metrics='<ul><li><strong>线上稳定性指标</strong>：可用性、故障率、MTTR(平均恢复时间)</li><li><strong>问题分析指标</strong>：线上问题数、根因分析完成率、重复问题率</li><li><strong>复盘指标</strong>：复盘参与率、改进措施落地率</li><li><strong>流程优化指标</strong>：流程变更数、改进效果验证</li></ul>'
        ),
        TestProcess(
            stage_name='原软件测试流程 vs ISTQB测试流程',
            stage_order=8,
            description='理解传统测试流程与ISTQB标准测试流程的区别，是进行流程优化的基础。本阶段对比分析原软件测试流程与ISTQB测试流程的特点和差异。',
            key_activities='<ul><li><strong>原软件测试流程特点分析</strong>：理解传统测试流程的活动和顺序</li><li><strong>ISTQB测试流程学习</strong>：掌握ISTQB定义的标准测试流程</li><li><strong>流程对比分析</strong>：对比两种流程的差异和优缺点</li><li><strong>差距识别</strong>：识别现有流程与标准的差距</li><li><strong>优化方向确定</strong>：基于对比确定流程优化方向</li></ul>',
            deliverables='<ul><li><strong>流程分析报告</strong>：现有流程分析、问题识别</li><li><strong>流程对比矩阵</strong>：两种流程的详细对比</li><li><strong>差距分析报告</strong>：与标准流程的差距</li><li><strong>优化建议</strong>：流程优化的具体建议</li></ul>',
            best_practices='<ul><li><strong>对标行业标准</strong>：参考ISTQB等行业标准，结合实际情况优化</li><li><strong>问题导向</strong>：从实际问题出发，不是为了流程而流程</li><li><strong>渐进式改进</strong>：不要试图一次性改变所有，小步快跑持续优化</li><li><strong>全员参与</strong>：流程优化需要产研测各方共同参与</li></ul>',
            common_pitfalls='<ul><li><strong>生搬硬套</strong>：直接照搬标准流程，不考虑实际情况</li><li><strong>过度工程化</strong>：流程过于复杂，执行成本高</li><li><strong>忽视实际问题</strong>：为了符合标准而忽视实际痛点</li><li><strong>缺乏验证</strong>：流程变更后不验证效果</li></ul>',
            optimization_techniques='<ul><li><strong>原软件测试流程的典型问题</strong>：<br>- 测试后置：编码完成后才开始测试<br>- 测试与开发脱节：双方沟通不充分<br>- 缺乏早期质量控制：问题发现太晚<br>- 流程不闭环：上线后没有复盘改进</li><li><strong>ISTQB测试流程的核心活动</strong>：<br>- 测试计划：确定测试范围、策略、资源<br>- 测试监控与控制：跟踪进度、调整计划<br>- 测试分析：分析测试依据、识别测试条件<br>- 测试设计：设计测试用例和测试数据<br>- 测试执行：执行测试用例、报告缺陷<br>- 测试完成：评估测试完成度、输出报告</li><li><strong>结合实际的优化思路</strong>：<br>- 保留ISTQB流程的系统性和完整性<br>- 增加适合敏捷环境的灵活性<br>- 加入测试左移、右移等现代实践<br>- 增加项目复盘等持续改进环节</li></ul>',
            metrics='<ul><li><strong>流程成熟度</strong>：当前流程的成熟度级别</li><li><strong>流程符合度</strong>：与标准流程的符合程度</li><li><strong>问题解决率</strong>：流程问题的解决比例</li><li><strong>改进效果</strong>：流程优化带来的质量和效率提升</li></ul>'
        ),
        TestProcess(
            stage_name='优化后流程 - 完整质量闭环',
            stage_order=9,
            description='优化后的流程在原有测试流程基础上进行了多处改进：需求分析阶段增加需求分析反馈，提测环节增加提测演示，测试结束增加产品验收，上线完成增加项目复盘。形成了一个完整的质量闭环。',
            key_activities='<ul><li><strong>需求阶段</strong>：需求分析反馈，进行质量预防</li><li><strong>提测阶段</strong>：提测演示，进行质量过滤</li><li><strong>测试阶段</strong>：系统性测试，进行质量评估</li><li><strong>发布前</strong>：产品验收，进行质量确认</li><li><strong>发布后</strong>：项目复盘，进行质量改进</li><li><strong>持续改进</strong>：复盘结果反哺下一个周期的需求分析</li></ul>',
            deliverables='<ul><li><strong>需求分析反馈报告</strong>：需求分析中的问题和建议</li><li><strong>提测演示记录</strong>：提测演示的内容和结果</li><li><strong>测试报告</strong>：测试执行结果和质量评估</li><li><strong>产品验收报告</strong>：验收结果和遗留问题</li><li><strong>项目复盘报告</strong>：经验教训和改进建议</li><li><strong>流程优化方案</strong>：基于复盘的流程改进措施</li></ul>',
            best_practices='<ul><li><strong>测试左移</strong>：需求分析反馈、风险识别、测试驱动开发、提测流程规范、引入提测演示等</li><li><strong>测试执行监控</strong>：运用测试执行策略，测试执行监控等方式</li><li><strong>测试右移</strong>：上线验收、线上问题根因分析、项目复盘、流程优化等</li><li><strong>全流程闭环</strong>：从需求到复盘形成完整闭环，质量意识贯穿始终</li></ul>',
            common_pitfalls='<ul><li><strong>环节流于形式</strong>：增加了环节但没有实际效果，成为负担</li><li><strong>过度流程化</strong>：为了流程而流程，降低了效率</li><li><strong>改进不落地</strong>：复盘发现了问题但没有后续改进</li><li><strong>缺乏数据支撑</strong>：凭感觉优化，没有数据验证效果</li></ul>',
            optimization_techniques='<ul><li><strong>完整流程闭环总结</strong>：<br><strong>需求阶段</strong>：通过【需求分析反馈】进行质量预防<br><strong>提测阶段</strong>：通过【提测演示】进行质量过滤<br><strong>测试阶段</strong>：通过系统性的测试进行质量评估<br><strong>发布前</strong>：通过【产品验收】进行质量确认<br><strong>发布后</strong>：通过【项目复盘】进行质量改进，从而反哺下一个周期的【需求分析】</li><li><strong>这个流程不再仅仅是测试团队的工作指南，而是整个产品研发团队共同遵循的高质量交付准则。</strong></li><li><strong>流程落地推动思想</strong>：<br>1. 发现问题，细化拆解为可落地步骤<br>2. 内部制定落地策略执行<br>3. 外部沟通同步<br>4. 落地监测并持续优化</li></ul>',
            metrics='<ul><li><strong>需求质量指标</strong>：需求分析反馈问题数、需求澄清次数</li><li><strong>提测质量指标</strong>：提测演示通过率、提测后阻塞问题数</li><li><strong>验收质量指标</strong>：产品验收通过率、验收发现问题数</li><li><strong>复盘改进指标</strong>：复盘问题数、改进措施落地率</li><li><strong>整体质量指标</strong>：线上缺陷数、项目延期率、客户满意度</li></ul>'
        ),
        TestProcess(
            stage_name='测试左移 - 早期质量预防',
            stage_order=10,
            description='测试左移是指将测试活动提前到软件开发生命周期的早期阶段，在需求分析、设计阶段就开始进行质量保障活动。通过测试左移，可以更早发现问题，降低修复成本，提高整体质量。',
            key_activities='<ul><li><strong>需求分析反馈</strong>：测试团队分析需求，识别模糊点、风险点、可测试性问题</li><li><strong>风险识别</strong>：在项目早期识别业务风险和技术风险</li><li><strong>测试驱动开发(TDD)</strong>：先写测试用例，再写功能代码</li><li><strong>提测流程规范</strong>：建立提测标准和检查清单</li><li><strong>提测演示</strong>：开发团队在提测前进行演示，确保基本功能可用</li></ul>',
            deliverables='<ul><li><strong>需求分析反馈报告</strong>：需求分析中的问题、建议、确认记录</li><li><strong>风险登记册</strong>：识别的风险、影响分析、应对措施</li><li><strong>提测检查清单</strong>：提测前需要满足的条件</li><li><strong>提测演示记录</strong>：演示内容、参与人员、结果记录</li><li><strong>早期测试报告</strong>：需求阶段和设计阶段发现的问题</li></ul>',
            best_practices='<ul><li><strong>测试参与需求评审</strong>：测试团队在需求阶段就参与，提供测试视角</li><li><strong>需求可测试性分析</strong>：确保每个需求都可以被测试验证</li><li><strong>验收标准先行</strong>：在需求阶段就定义好验收标准</li><li><strong>提测质量门禁</strong>：设置提测门槛，质量不达标不进入测试阶段</li><li><strong>开发自测文化</strong>：培养开发人员的质量意识，做好自测</li></ul>',
            common_pitfalls='<ul><li><strong>测试左移变成测试前移</strong>：只是把测试用例编写提前，没有真正参与需求和设计</li><li><strong>需求分析反馈不受重视</strong>：测试团队的反馈不被产品团队重视</li><li><strong>提测演示流于形式</strong>：演示变成走过场，没有真正验证质量</li><li><strong>过度依赖左移</strong>：认为左移了就不需要后期测试了</li></ul>',
            optimization_techniques='<ul><li><strong>需求分析反馈机制</strong>：<br>- 测试团队收到需求文档后进行系统性分析<br>- 检查：完整性、一致性、可测试性、无歧义性<br>- 识别：遗漏的场景、隐含的需求、风险点<br>- 输出：需求分析反馈文档，与产品团队沟通确认<br>- 闭环：确保所有问题都得到解决后才进入下一阶段</li><li><strong>提测演示机制</strong>：<br>- 开发完成后，向测试团队进行功能演示<br>- 演示内容：核心功能、主要流程、边界情况<br>- 目的：确保基本功能可用，避免提测后阻塞<br>- 不通过则返回修改，通过才进入正式测试<br>- 效果：提高提测质量，减少测试阻塞</li><li><strong>风险识别与管理</strong>：<br>- 在需求阶段识别业务风险和技术风险<br>- 分析风险的影响概率和严重程度<br>- 制定风险应对措施：规避、转移、缓解、接受<br>- 在测试过程中重点关注高风险功能</li></ul>',
            metrics='<ul><li><strong>需求质量指标</strong>：需求分析反馈问题数、需求变更率、需求澄清次数</li><li><strong>提测质量指标</strong>：提测演示通过率、提测后P0缺陷数、测试阻塞时间</li><li><strong>风险指标</strong>：风险识别数量、高风险数量、风险缓解率</li><li><strong>效率指标</strong>：需求理解时间、测试准备时间</li></ul>'
        ),
        TestProcess(
            stage_name='测试执行监控 - 过程质量保证',
            stage_order=11,
            description='测试执行监控是指在测试执行过程中，通过各种方式监控测试进度、识别风险点和阻塞点、及时沟通疏导问题，保证测试执行质量和进度。这是测试过程中非常重要的管理活动。',
            key_activities='<ul><li><strong>测试进度跟踪</strong>：跟踪测试用例执行进度、与计划对比</li><li><strong>风险点识别</strong>：识别测试过程中的风险和问题</li><li><strong>阻塞点沟通</strong>：对阻塞测试的问题进行沟通协调</li><li><strong>问题集中点分析</strong>：分析缺陷集中的模块和功能</li><li><strong>测试策略调整</strong>：根据实际情况调整测试策略和重点</li><li><strong>风险缓解</strong>：采取措施缓解已识别的风险</li></ul>',
            deliverables='<ul><li><strong>测试进度报告</strong>：每日/每周进度、与计划对比</li><li><strong>风险登记册</strong>：测试过程中识别的风险</li><li><strong>阻塞问题清单</strong>：阻塞测试的问题及处理状态</li><li><strong>缺陷分析报告</strong>：缺陷分布、趋势分析</li><li><strong>测试调整记录</strong>：测试策略和范围的调整</li></ul>',
            best_practices='<ul><li><strong>每日站会</strong>：同步进度、识别阻塞、协调资源</li><li><strong>测试看板</strong>：可视化测试进度和状态</li><li><strong>缺陷趋势分析</strong>：通过缺陷趋势判断版本质量</li><li><strong>及时沟通</strong>：发现问题及时沟通，不要等待</li><li><strong>分级处理</strong>：根据问题的严重程度和影响范围分级处理</li></ul>',
            common_pitfalls='<ul><li><strong>只管执行不管监控</strong>：只关注执行测试用例，不关注整体进度和风险</li><li><strong>问题发现太晚</strong>：阻塞问题没有及时识别和沟通</li><li><strong>缺乏数据分析</strong>：不分析缺陷趋势，无法判断质量走势</li><li><strong>策略僵化</strong>：测试计划制定后不根据实际情况调整</li></ul>',
            optimization_techniques='<ul><li><strong>测试执行监控方式</strong>：<br>- 运用测试执行策略，测试执行监控等方式<br>- 对风险点、阻塞点、问题集中点沟通疏导<br>- 风险识别、缓解、版本控制等保证测试执行质量</li><li><strong>测试阻塞处理</strong>：<br><strong>测试阻塞</strong>：增加经验丰富人员、增加校验手段（稳定性、性能优化、自动化回归等）、回退不测等<br><strong>产品问题阻塞</strong>：确认、延期、修复<br><strong>开发问题阻塞</strong>：增加开发解决、集中精力攻关</li><li><strong>版本控制策略</strong>：<br>- 建立清晰的版本管理机制<br>- 了解每个版本的变更内容<br>- 控制测试范围，避免范围蔓延<br>- 版本冻结策略，防止最后时刻变更</li><li><strong>风险缓解措施</strong>：<br>- 对于高风险功能，增加测试深度<br>- 准备备用测试方案<br>- 预留缓冲时间<br>- 关键问题升级机制</li></ul>',
            metrics='<ul><li><strong>进度指标</strong>：测试执行进度、用例执行率、计划达成率</li><li><strong>阻塞指标</strong>：阻塞问题数、平均阻塞时间、阻塞解决率</li><li><strong>风险指标</strong>：识别风险数、高风险数、风险缓解率</li><li><strong>缺陷指标</strong>：每日新增缺陷数、缺陷修复率、缺陷密度</li><li><strong>效率指标</strong>：人均每日执行用例数、缺陷发现效率</li></ul>'
        ),
        TestProcess(
            stage_name='测试右移 - 线上质量改进',
            stage_order=12,
            description='测试右移是指将质量保障活动延伸到软件上线之后，关注线上问题、用户反馈、持续改进。通过测试右移，可以发现测试环境难以模拟的问题，持续优化产品质量和流程。一般测试右移指线上问题跟进和优化，优化后还增加了项目版本右移，使后续项目更顺畅。',
            key_activities='<ul><li><strong>上线验收</strong>：发布后进行线上验证，确保发布成功</li><li><strong>线上监控</strong>：监控系统状态、业务指标、用户行为</li><li><strong>线上问题响应</strong>：及时响应和处理线上问题</li><li><strong>线上问题根因分析</strong>：深入分析问题根因，防止重复发生</li><li><strong>项目复盘</strong>：项目结束后进行复盘，总结经验教训</li><li><strong>流程优化</strong>：根据线上问题和复盘结果优化流程</li><li><strong>项目版本右移</strong>：优化整体结构，使后续项目更顺畅</li></ul>',
            deliverables='<ul><li><strong>上线验收报告</strong>：线上验证结果</li><li><strong>运维监控报告</strong>：系统运行状态、告警记录</li><li><strong>线上问题记录</strong>：问题描述、处理过程、根因分析</li><li><strong>根因分析报告</strong>：5 Whys分析、改进措施</li><li><strong>项目复盘报告</strong>：亮点、不足、改进建议</li><li><strong>流程更新文档</strong>：优化后的流程和规范</li></ul>',
            best_practices='<ul><li><strong>线上验收</strong>：发布后立即进行线上验证，确保功能正常</li><li><strong>全链路监控</strong>：建立从前端到后端的全链路监控</li><li><strong>快速响应</strong>：建立线上问题快速响应机制</li><li><strong>根因分析</strong>：不仅解决问题，更要分析根因防止重复发生</li><li><strong>项目复盘</strong>：每个项目结束后都进行复盘，持续改进</li><li><strong>项目版本右移</strong>：优化整体结构，使后续项目更顺畅</li></ul>',
            common_pitfalls='<ul><li><strong>发布即结束</strong>：认为上线就完成任务，不关注线上情况</li><li><strong>被动响应</strong>：只有用户投诉了才处理问题</li><li><strong>治标不治本</strong>：只解决问题现象，不分析根因</li><li><strong>复盘流于形式</strong>：复盘变成走过场，没有实际改进</li><li><strong>改进不落地</strong>：发现了问题但没有后续行动</li></ul>',
            optimization_techniques='<ul><li><strong>测试右移策略</strong>：<br><strong>一般测试右移指</strong>：线上问题跟进、优化<br><strong>增加</strong>：项目版本右移，这样优化结构，才可使后续项目跟进更方便</li><li><strong>上线验收机制</strong>：<br>- 发布后立即进行线上验证<br>- 验证核心功能、关键流程<br>- 对比测试环境与线上环境的差异<br>- 发现问题及时回滚</li><li><strong>线上问题根因分析</strong>：<br>- 使用5 Whys方法深入分析<br>- 区分：人的问题、流程的问题、技术的问题<br>- 制定纠正措施和预防措施<br>- 跟踪措施的落地效果</li><li><strong>项目复盘方法</strong>：<br>- 收集数据：项目指标、问题记录、反馈<br>- 分析原因：什么做得好、什么可以改进<br>- 制定行动：具体改进措施、责任人、时间点<br>- 跟踪落地：在下个周期验证改进效果</li><li><strong>流程优化闭环</strong>：<br>- 线上问题 → 根因分析 → 流程改进 → 验证效果<br>- 形成持续改进的闭环</li></ul>',
            metrics='<ul><li><strong>线上稳定性指标</strong>：系统可用性、MTTR(平均恢复时间)、线上P0/P1缺陷数</li><li><strong>问题处理指标</strong>：问题响应时间、问题解决率、重复问题率</li><li><strong>根因分析指标</strong>：根因分析完成率、改进措施落地率</li><li><strong>复盘指标</strong>：复盘参与率、复盘问题数、改进措施数</li><li><strong>流程优化指标</strong>：流程变更数、优化效果验证</li></ul>'
        ),
        TestProcess(
            stage_name='TMMI测试成熟度模型',
            stage_order=13,
            description='测试成熟度模型集成(Test Maturity Model Integration, TMMI)是一个用于评估和改进测试过程的框架。TMMI由5个成熟度级别组成，每个级别定义不同的过程域。通过TMMI可以系统性地评估和提升测试组织的成熟度。',
            key_activities='<ul><li><strong>TMMI模型学习</strong>：理解TMMI的5个成熟度级别和过程域</li><li><strong>组织现状评估</strong>：评估当前测试组织的TMMI级别</li><li><strong>差距分析</strong>：识别当前状态与目标级别的差距</li><li><strong>改进路线图</strong>：制定提升到更高级别的路线图</li><li><strong>过程改进实施</strong>：实施过程改进措施</li><li><strong>效果评估</strong>：评估改进效果，持续优化</li></ul>',
            deliverables='<ul><li><strong>成熟度评估报告</strong>：当前级别的评估结果</li><li><strong>差距分析报告</strong>：与目标级别的差距</li><li><strong>改进路线图</strong>：提升成熟度的实施计划</li><li><strong>过程改进记录</strong>：改进措施和效果</li><li><strong>再评估报告</strong>：改进后的成熟度评估</li></ul>',
            best_practices='<ul><li><strong>循序渐进</strong>：不要试图越级提升，按级别逐步改进</li><li><strong>聚焦核心</strong>：每个级别聚焦于该级别应该解决的核心问题</li><li><strong>全员参与</strong>：过程改进需要测试团队全员参与</li><li><strong>持续优化</strong>：达到高级别后仍需持续优化</li><li><strong>结合实际</strong>：不要生搬硬套，结合组织实际情况</li></ul>',
            common_pitfalls='<ul><li><strong>为了评估而评估</strong>：只关注级别认证，不关注实际改进</li><li><strong>越级提升</strong>：试图跳过基础级别直接追求高级别</li><li><strong>文档化泛滥</strong>：过度追求文档，忽视实际执行</li><li><strong>缺乏管理层支持</strong>：过程改进缺乏资源和授权</li><li><strong>改进不持续</strong>：评估通过后就停止改进</li></ul>',
            optimization_techniques='<ul><li><strong>TMMI总结</strong>：<br>1. 作为TMMI模型的补充<br>2. 由5个成熟度级别组成<br>3. 每个级别定义不同的过程域<br>4. 至少完成85%的过程域的特殊目标和通用目标</li><li><strong>TMMI成熟度级别</strong>：<br><strong>Level 1: Initial (初始级)</strong><br>- 没有文档化的测试过程<br>- 测试是编码之后的随意活动<br>- 没有明确测试与调试之间的区别<br>- 测试目的主要是证明软件可以正常工作<br><br><strong>Level 2: Managed (管理级)</strong><br>- 测试与调试完全分开<br>- 定义了基本的测试过程<br>- 采用了基本的测试技术与方法<br>- 过程域：测试政策和测试策略、测试计划、测试监控与控制、测试设计与执行、测试环境<br><br><strong>Level 3: Defined (定义级)</strong><br>- 测试过程与开发过程的集成，并进行正式的文档化<br>- 开展评审活动<br>- 专门的测试职能，并可对其进行监控<br>- 过程域：测试组织、测试培训计划、测试生命周期和集成、非功能性测试、同行评审<br><br><strong>Level 4: Measured (测试度量级)</strong><br>- 在组织层面进行有效度量和管理<br>- 过程域：测试测量/评估、产品质量评价、高级同行评审<br><br><strong>Level 5: Optimization (优化级)</strong><br>- 测试过程收集的数据帮助预防缺陷<br>- 关注测试过程优化<br>- 过程域：缺陷预防、质量控制、测试流程组织</li><li><strong>TMMi结构</strong>：<br>5 Maturity Levels (成熟度级别)<br>└── indicate (表明) → Testing Capability (测试能力)<br>└── Contain (包含) → Maturity Goals (KPA) 成熟的目标<br>    └── Maturity Sub-Goals (Goals) 成熟的子目标<br>        └── Activities / Tasks / Responsible (KPs) 活动/任务/负责<br>            └── Organised by (组织的) → Critical Views (SPs) 批评/评价<br>                └── Manager (经理)、Developer/Tester (开发/测试)、User/Client (用户/客户端)<br>            └── Implementation and Organisation Adoption (实施及组织采用)</li></ul>',
            metrics='<ul><li><strong>成熟度级别</strong>：当前所处的TMMI级别</li><li><strong>过程域完成度</strong>：各过程域的实现程度</li><li><strong>改进进度</strong>：从低级到高级的提升进度</li><li><strong>质量指标</strong>：成熟度提升带来的质量改善</li><li><strong>效率指标</strong>：成熟度提升带来的效率提升</li></ul>'
        ),
        TestProcess(
            stage_name='STEP系统化测试和评估过程',
            stage_order=14,
            description='STEP(Systematic Test and Evaluation Process)是一个系统化的测试和评估过程模型。STEP强调测试的缺陷预防功能，将缺陷检测和软件能力验证作为第二个目标。STEP属于内容参考模型，贯穿于整个生命周期的活动。',
            key_activities='<ul><li><strong>STEP模型学习</strong>：理解STEP的核心思想和方法</li><li><strong>测试再编码</strong>：将测试活动提前到编码之前</li><li><strong>基于需求的测试策略</strong>：以需求为基础进行测试</li><li><strong>尽早创建测试用例</strong>：在需求阶段就开始创建测试用例</li><li><strong>测试件设计引导软件设计</strong>：测试件设计影响和引导软件设计</li><li><strong>尽早检测缺陷或预防</strong>：通过早期测试活动发现或预防缺陷</li></ul>',
            deliverables='<ul><li><strong>STEP过程定义</strong>：适配组织的STEP过程文档</li><li><strong>需求规格验证报告</strong>：测试用例对需求规格的验证</li><li><strong>测试件设计文档</strong>：测试件设计，用于引导软件设计</li><li><strong>缺陷预防报告</strong>：早期发现和预防的缺陷</li><li><strong>系统化缺陷分析报告</strong>：缺陷的系统化分析</li></ul>',
            best_practices='<ul><li><strong>测试再编码</strong>：强调"测试在编码之前"的理念</li><li><strong>基于需求的测试策略</strong>：所有测试活动都基于需求</li><li><strong>尽早创建测试用例</strong>：验证需求规格说明的正确性和完整性</li><li><strong>测试与开发紧密合作</strong>：测试人员与开发人员紧密合作</li><li><strong>系统化缺陷分析</strong>：不仅发现缺陷，更要系统化分析</li></ul>',
            common_pitfalls='<ul><li><strong>理解偏差</strong>：只理解了字面意思，没有理解核心思想</li><li><strong>执行不到位</strong>：知道要尽早测试，但实际还是延后</li><li><strong>协作不足</strong>：测试与开发仍然是两个独立的团队</li><li><strong>缺乏系统化分析</strong>：只关注缺陷修复，不关注系统化分析</li></ul>',
            optimization_techniques='<ul><li><strong>STEP总结</strong>：<br>1. 定义了软件评估的主要活动，主要包括分析、评审和测试<br>2. STEP首先强调测试的缺陷预防功能，将缺陷检测软件能力验证作为第二个目标<br>3. 属于内容参考模型，贯穿于整个生命周期的活动，从需求开始直到被测对象退役</li><li><strong>STEP特点</strong>：<br>1. 强调"测试再编码"<br>2. 采用基于需求的测试策略<br>3. 尽早创建测试用例验证需求规格说明</li><li><strong>STEP基本理念</strong>：<br>1. 基于需求的测试策略<br>2. 测试在生命周期的早期启动<br>3. 测试作为需求和使用模型<br>4. 测试件设计引导软件设计<br>5. 尽早检测缺陷或预防<br>6. 系统化分析缺陷<br>7. 测试人员与开发人员紧密合作</li><li><strong>STEP核心实践</strong>：<br><strong>测试再编码(Test Before Code)</strong>：<br>- 测试用例在代码之前编写<br>- 测试用例用于验证需求规格说明<br>- 测试用例帮助发现需求中的问题<br>- 测试用例作为开发的验收标准<br><br><strong>测试件设计引导软件设计</strong>：<br>- 测试件设计考虑可测试性<br>- 可测试性设计影响软件架构<br>- 模块化设计便于测试<br>- 接口设计便于模拟和验证<br><br><strong>系统化缺陷分析</strong>：<br>- 收集缺陷数据<br>- 分析缺陷模式<br>- 识别根本原因<br>- 制定预防措施<br>- 持续改进</li></ul>',
            metrics='<ul><li><strong>需求阶段测试活动</strong>：需求阶段创建的测试用例数、发现的需求问题数</li><li><strong>缺陷预防效果</strong>：早期发现的缺陷数、避免的后期修复成本</li><li><strong>测试与开发协作</strong>：协作活动次数、问题沟通效率</li><li><strong>缺陷分析深度</strong>：根因分析完成率、预防措施落地率</li><li><strong>质量趋势</strong>：版本质量改善趋势</li></ul>'
        ),
        TestProcess(
            stage_name='实践案例 - 金融界与红上金融',
            stage_order=15,
            description='本阶段通过实际案例展示测试流程优化的实践应用。包括红上金融的TMMI级别评估、STEP流程改进的实际应用，以及Ocean、人品科技等公司的产研测协同发展实践。',
            key_activities='<ul><li><strong>案例分析</strong>：分析不同公司的测试流程实践</li><li><strong>经验萃取</strong>：从案例中萃取可复用的经验</li><li><strong>对比学习</strong>：对比不同案例的异同点</li><li><strong>实践落地</strong>：将案例经验应用到实际工作</li><li><strong>效果验证</strong>：验证实践应用的效果</li></ul>',
            deliverables='<ul><li><strong>案例分析报告</strong>：各公司案例的详细分析</li><li><strong>经验萃取文档</strong>：从案例中提取的最佳实践</li><li><strong>对标分析</strong>：与自身情况的对标分析</li><li><strong>改进建议</strong>：基于案例的改进建议</li><li><strong>实践记录</strong>：应用案例经验的实践记录</li></ul>',
            best_practices='<ul><li><strong>案例学习</strong>：学习行业内的最佳实践</li><li><strong>因地制宜</strong>：结合自身实际情况，不要生搬硬套</li><li><strong>小步验证</strong>：先在小范围验证效果，再推广</li><li><strong>持续优化</strong>：在实践中持续调整和优化</li><li><strong>知识沉淀</strong>：将实践经验沉淀为组织资产</li></ul>',
            common_pitfalls='<ul><li><strong>生搬硬套</strong>：直接照搬其他公司的做法，不考虑自身情况</li><li><strong>只学皮毛</strong>：只看到表面做法，不理解背后的原理</li><li><strong>缺乏验证</strong>：不验证效果就全面推广</li><li><strong>急于求成</strong>：期望短时间内看到显著效果</li></ul>',
            optimization_techniques='<ul><li><strong>案例分析：评估组织的TMMI级别</strong>：<br>根据TMMI成熟度级别特点，评估你的测试团队属于哪个级别？<br><br><strong>红上金融案例</strong>：<br>- 评估结果：管理级+优化级（定义级和测度级进行了简化）<br>- 根据现状做了简单评估<br>- 未有文档化留存和输出<br>- 实际优化改善了测试效果、上线效果<br><br>分析：红上金融在实际操作中达到了较高的实践水平，但缺乏正式的文档化和度量体系。这是很多中小企业的典型情况——实际做得不错，但体系化不足。</li><li><strong>产、研、测协同发展规划</strong>：<br>详细讲解测试流程的各个阶段、关键活动、交付物，以及流程优化的技术和最佳实践，提升测试效率和质量。<br><br><strong>核心要点</strong>：<br>1. <strong>协同而非分离</strong>：测试不是测试团队独立的工作，而是产研测三方协同的过程<br>2. <strong>全流程参与</strong>：测试团队在需求、设计、编码、测试、部署、维护全流程参与<br>3. <strong>质量共建</strong>：质量是整个团队的责任，不是测试团队 alone<br>4. <strong>持续改进</strong>：通过复盘不断优化协同效率和质量</li><li><strong>实践经验总结</strong>：<br>从金融界、红上金融、Ocean、人品科技等案例中可以看到：<br><br>1. <strong>流程优化的价值</strong>：<br>   - 测试流程优化，项目延期风险降低20%以上<br>   - 整体测试效率提升显著<br>   - 提升测试效率和质量<br><br>2. <strong>关键成功因素</strong>：<br>   - 管理层支持和资源投入<br>   - 产研测三方的协作意识<br>   - 持续改进的文化<br>   - 数据驱动的决策<br><br>3. <strong>可复用的实践</strong>：<br>   - 需求分析反馈机制<br>   - 提测演示和提测标准<br>   - 产品验收环节<br>   - 项目复盘机制<br>   - 缺陷根因分析</li></ul>',
            metrics='<ul><li><strong>实践应用率</strong>：案例经验在实际工作中的应用比例</li><li><strong>改进效果</strong>：应用案例经验后的质量和效率改善</li><li><strong>团队成熟度</strong>：基于案例评估的团队成熟度</li><li><strong>协同效率</strong>：产研测协同效率的提升</li><li><strong>质量指标</strong>：线上缺陷率、项目延期率等质量指标的改善</li></ul>'
        )
    ]
    
    for p in test_processes:
        existing = TestProcess.query.filter_by(stage_name=p.stage_name).first()
        if not existing:
            db.session.add(p)
        else:
            sync_existing_record(existing, p)
    
    checklist_categories = [
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

    for c in checklist_categories:
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
    print('数据库初始化完成！')
    print('默认管理员账号: admin')
    print('默认管理员密码: admin123')
    print(
        'init_db: 行数统计 — '
        f'BlockChainTestCases={BlockChainTestCases.query.count()}, '
        f'TransactionLifecycleStage={TransactionLifecycleStage.query.count()}, '
        f'TestType={TestType.query.count()}, '
        f'TestModule={TestModule.query.count()}, '
        f'ChecklistCategory={ChecklistCategory.query.count()}, '
        f'ChecklistItem={ChecklistItem.query.count()}',
        flush=True,
    )
