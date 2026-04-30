# -*- coding: utf-8 -*-
import os
import sys

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('DATABASE_URL', 'sqlite:///site.db')
os.environ.setdefault('SECRET_KEY', 'flask-me-secret-key-2024')

from app import create_app, db
from app.models import TestType

app = create_app()

with app.app_context():
    print('=== 开始添加平台测试对比数据 ===')
    
    platform_test_comparison = TestType(
        name='不同平台测试对比（小程序、APP、WEB、WEB3、H5）',
        category='专项测试类',
        description='全面对比小程序、原生APP、WEB、WEB3、H5五种平台在测试方面的核心区别，包括技术架构、测试环境、测试工具、测试重点、注意事项等方面的差异。帮助测试人员根据不同平台特点制定合适的测试策略。',
        purpose='理解不同平台的技术特点和测试差异，为各平台制定针对性的测试策略。提高测试效率和覆盖率，避免因平台特性理解不足导致的测试遗漏。',
        when_to_use='<ul><li>新项目启动，确定技术栈时</li><li>跨平台项目测试时</li><li>测试人员切换平台时</li><li>制定测试计划和测试策略时</li><li>评估测试工作量和资源需求时</li></ul>',
        key_concepts='<h5>一、各平台定义与核心特点</h5><p><strong>1. 小程序</strong>：运行在微信、支付宝、抖音等超级App内的轻量级应用，依赖宿主App环境，具有"用完即走"的特点。</p><p><strong>2. 原生APP</strong>：使用平台原生语言开发的应用（iOS用Swift/Objective-C，Android用Kotlin/Java），直接运行在操作系统上，性能最佳。</p><p><strong>3. WEB</strong>：运行在浏览器中的网页应用，通过URL访问，无需安装，跨平台性好。</p><p><strong>4. WEB3</strong>：基于区块链技术的去中心化应用，涉及钱包、智能合约、链上交易等特殊场景。</p><p><strong>5. H5</strong>：HTML5移动网页，通常内嵌在APP或小程序中，或作为独立的移动端网页使用。</p><h5>二、技术架构对比</h5><table class="table table-bordered table-sm"><thead><tr><th>维度</th><th>小程序</th><th>原生APP</th><th>WEB</th><th>WEB3</th><th>H5</th></tr></thead><tbody><tr><td><strong>运行环境</strong></td><td>宿主App（微信等）</td><td>操作系统</td><td>浏览器</td><td>浏览器+钱包</td><td>浏览器/WebView</td></tr><tr><td><strong>开发语言</strong></td><td>小程序框架（WXML/WXSS）</td><td>Swift/Java/Kotlin</td><td>HTML/CSS/JS</td><td>Solidity + Web3.js</td><td>HTML/CSS/JS</td></tr><tr><td><strong>安装方式</strong></td><td>无需安装，扫码即用</td><td>应用商店下载安装</td><td>无需安装</td><td>无需安装</td><td>无需安装</td></tr><tr><td><strong>更新方式</strong></td><td>平台审核后自动更新</td><td>应用商店审核更新</td><td>服务器部署即更新</td><td>智能合约部署</td><td>服务器部署即更新</td></tr><tr><td><strong>系统权限</strong></td><td>受限（依赖宿主授权）</td><td>完整权限</td><td>受限（浏览器沙箱）</td><td>受限（需钱包签名）</td><td>受限（浏览器沙箱）</td></tr></tbody></table>',
        tools='<h5>各平台常用测试工具</h5><p><strong>小程序测试工具：</strong></p><ul><li><strong>开发者工具</strong>：微信开发者工具、支付宝开发者工具</li><li><strong>真机调试</strong>：真机预览、远程调试</li><li><strong>自动化测试</strong>：Minium（微信小程序自动化框架）</li><li><strong>性能分析</strong>：开发者工具性能面板</li></ul><p><strong>原生APP测试工具：</strong></p><ul><li><strong>UI自动化</strong>：Appium、XCUI Test（iOS）、Espresso（Android）、UI Automator</li><li><strong>性能测试</strong>：PerfDog、GT、LeakCanary（Android）、Instruments（iOS）</li><li><strong>崩溃分析</strong>：Bugly、Firebase Crashlytics、Sentry</li><li><strong>弱网测试</strong>：Charles、Fiddler、Network Link Conditioner</li><li><strong>云测试平台</strong>：Testin、阿里云测、腾讯WeTest、BrowserStack</li></ul><p><strong>WEB测试工具：</strong></p><ul><li><strong>UI自动化</strong>：Selenium、Cypress、Playwright、Puppeteer</li><li><strong>接口测试</strong>：Postman、JMeter、RestAssured、Requests</li><li><strong>性能测试</strong>：JMeter、Gatling、k6、Locust</li><li><strong>安全测试</strong>：OWASP ZAP、Burp Suite、Nessus</li><li><strong>兼容性测试</strong>：BrowserStack、Sauce Labs、LambdaTest</li><li><strong>开发者工具</strong>：Chrome DevTools、Firefox Developer Tools</li></ul><p><strong>WEB3测试工具：</strong></p><ul><li><strong>智能合约测试</strong>：Hardhat、Truffle、Foundry、Brownie</li><li><strong>测试网络</strong>：Ganache、Hardhat Network、Goerli、Sepolia</li><li><strong>钱包测试</strong>：MetaMask、WalletConnect模拟器</li><li><strong>RPC测试</strong>：Postman、Web3.py、Ethers.js</li><li><strong>安全审计</strong>：Slither、MythX、Oyente</li><li><strong>区块浏览器</strong>：Etherscan、BscScan、Polygon Scan</li></ul><p><strong>H5测试工具：</strong></p><ul><li><strong>真机调试</strong>：Chrome Inspect、Safari Web Inspector</li><li><strong>模拟器</strong>：Chrome DevTools Device Mode</li><li><strong>抓包工具</strong>：Charles、Fiddler、mitmproxy</li><li><strong>性能分析</strong>：Chrome DevTools Performance、Lighthouse</li><li><strong>自动化测试</strong>：Appium（WebView）、Selenium</li></ul>',
        examples='<h5>一、功能测试区别对比</h5><table class="table table-bordered table-sm"><thead><tr><th>测试项</th><th>小程序</th><th>原生APP</th><th>WEB</th><th>WEB3</th><th>H5</th></tr></thead><tbody><tr><td><strong>授权登录</strong></td><td>微信授权、手机号授权</td><td>手机号、第三方登录</td><td>账号密码、SSO</td><td>钱包签名登录</td><td>手机号、授权登录</td></tr><tr><td><strong>支付方式</strong></td><td>微信支付、支付宝</td><td>内购、第三方支付</td><td>扫码支付、网银</td><td>链上转账、USDT</td><td>微信支付、支付宝H5</td></tr><tr><td><strong>推送通知</strong></td><td>订阅消息、模板消息</td><td>APNs、厂商推送</td><td>Web Push（有限支持）</td><td>无（链上事件）</td><td>无</td></tr><tr><td><strong>分享功能</strong></td><td>分享到聊天、朋友圈</td><td>系统分享面板</td><td>URL复制、社交分享</td><td>无</td><td>URL复制、社交分享</td></tr><tr><td><strong>离线功能</strong></td><td>有限支持（缓存）</td><td>完整支持</td><td>Service Worker</td><td>无</td><td>有限支持</td></tr></tbody></table><h5>二、实际测试案例</h5><p><strong>案例1：小程序授权登录测试</strong></p><ol><li>测试微信授权登录流程：点击登录 → 拉起授权弹窗 → 用户同意 → 获取用户信息 → 登录成功</li><li>测试拒绝授权场景：用户拒绝授权 → 系统应有友好提示，允许重新授权</li><li>测试手机号授权：验证手机号格式、验证码发送与校验</li><li>测试登录态保持：小程序退出后再次进入，是否保持登录状态</li><li><strong>注意</strong>：小程序登录依赖微信服务，需在真机上测试，开发者工具可能有差异</li></ol><p><strong>案例2：原生APP安装/升级测试</strong></p><ol><li>全新安装测试：在干净设备上安装，验证首次启动引导、权限申请</li><li>覆盖安装测试：从低版本升级到高版本，验证数据迁移、配置保留</li><li>跨版本升级测试：从非常老的版本直接升级到最新版</li><li>降级测试：高版本覆盖安装低版本（如果允许）</li><li>应用商店更新测试：通过应用商店进行更新</li><li><strong>注意</strong>：不同品牌Android设备（华为、小米、OPPO等）安装行为可能有差异</li></ol><p><strong>案例3：WEB浏览器兼容性测试</strong></p><ol><li>多浏览器测试：Chrome、Firefox、Safari、Edge、IE（如需要）</li><li>多版本测试：同一浏览器的不同主版本</li><li>渲染差异测试：CSS样式、布局、字体渲染</li><li>JS兼容性测试：ES6+特性、API支持差异</li><li>插件兼容性：Flash、PDF阅读器等（如需要）</li><li><strong>注意</strong>：使用BrowserStack等云平台进行真实环境测试，不要只依赖模拟器</li></ol><p><strong>案例4：WEB3钱包连接测试</strong></p><ol><li>MetaMask连接测试：安装MetaMask → 点击连接按钮 → 钱包弹窗 → 选择账户 → 确认连接</li><li>多钱包支持测试：MetaMask、WalletConnect、Coinbase Wallet等</li><li>网络切换测试：主网、测试网（Goerli、Sepolia）、本地网络</li><li>签名测试：消息签名、交易签名、EIP-712结构化签名</li><li>断开连接测试：断开后状态清理、重新连接</li><li><strong>注意</strong>：钱包交互是异步的，需要测试各种网络状态下的表现</li></ol><p><strong>案例5：H5内嵌测试</strong></p><ol><li>APP内嵌测试：在iOS WKWebView、Android WebView中测试</li><li>小程序内嵌测试：在web-view组件中测试</li><li>JSBridge测试：H5与原生的交互（调用相机、定位、支付等）</li><li>通信测试：postMessage、url scheme等通信方式</li><li>性能测试：WebView的渲染性能、内存占用</li><li><strong>注意</strong>：不同APP的WebView配置可能不同，需要在实际宿主APP中测试</li></ol><h5>三、性能测试关注点</h5><p><strong>小程序性能关注点：</strong></p><ul><li>首屏加载时间（建议 < 2s）</li><li>包体积（主包建议 < 2MB，总包 < 20MB）</li><li>页面渲染性能（setData频率、大小）</li><li>内存占用（避免内存泄漏导致小程序被回收）</li><li>网络请求优化（并发数、缓存策略）</li></ul><p><strong>原生APP性能关注点：</strong></p><ul><li>启动时间（冷启动、热启动）</li><li>页面渲染帧率（目标 60fps）</li><li>内存占用（避免OOM崩溃）</li><li>CPU使用率（后台耗电优化）</li><li>包体积（下载安装体验）</li><li>网络请求优化（弱网体验）</li></ul><p><strong>WEB性能关注点：</strong></p><ul><li>首屏加载时间（FP、FCP、LCP）</li><li>可交互时间（TTI）</li><li>资源加载优化（压缩、缓存、CDN）</li><li>渲染性能（重排重绘、合成层）</li><li>SEO友好度</li></ul><p><strong>WEB3性能关注点：</strong></p><ul><li>Gas消耗优化（存储、计算成本）</li><li>交易确认时间（区块确认数）</li><li>网络响应时间（RPC节点性能）</li><li>钱包连接响应速度</li><li>事件监听实时性</li></ul><p><strong>H5性能关注点：</strong></p><ul><li>首屏加载速度（移动端网络差）</li><li>页面渲染性能（DOM操作优化）</li><li>内存占用（移动端内存有限）</li><li>触摸响应延迟（300ms点击延迟）</li><li>离线缓存策略</li></ul>',
        sort_order=21
    )
    
    existing = TestType.query.filter_by(name=platform_test_comparison.name).first()
    if not existing:
        db.session.add(platform_test_comparison)
        db.session.commit()
        print('✅ 成功添加平台测试对比数据')
    else:
        print('⚠️  平台测试对比数据已存在，跳过')
        existing.description = platform_test_comparison.description
        existing.purpose = platform_test_comparison.purpose
        existing.when_to_use = platform_test_comparison.when_to_use
        existing.key_concepts = platform_test_comparison.key_concepts
        existing.tools = platform_test_comparison.tools
        existing.examples = platform_test_comparison.examples
        existing.sort_order = platform_test_comparison.sort_order
        db.session.commit()
        print('✅ 已更新平台测试对比数据')
    
    print('=== 平台测试对比数据添加完成 ===')
    print(f'测试类型总数: {TestType.query.count()}')
