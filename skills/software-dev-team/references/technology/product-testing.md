# 产品与测试工具随工作选择

## 产品工作

| 工作 | 候选工具/方法 | 应交付什么 |
|---|---|---|
| 用户与范围澄清 | 访谈、用户故事、任务流程、现有工单/文档 | 用户、痛点、入口、前置条件、范围、验收及未决问题 |
| 流程/状态建模 | Mermaid、现有白板或图形工具 | 成功/失败/取消/恢复的真实状态与数据来源 |
| 界面与可用性 | 现有组件体系；需要时 Figma/Penpot 或可点击 HTML 原型 | 信息层级、操作路径、文案、键盘/焦点、尺寸适配 |
| 需求跟踪 | 现有任务系统/当前计划 | 需求 → 模块 → 任务 → 验收关系，不另建第二总账 |
| 价值与发布取舍 | 目标、使用证据、成本/风险与用户反馈 | 可决策的主方案/备选，不编造指标或优先级数字 |

原型是设计材料，不等于生产能力。工具可用性、账户和材料外发需要核实；简单需求可用文字/现有组件，不强制外部设计服务。

## 测试工作

| 被测工作 | 候选工具 | 重点 |
|---|---|---|
| Java 业务/API | JUnit、Mockito、Spring MVC Test、Testcontainers | 业务断言、事务/数据库、权限、并发与错误合同 |
| Web 组件/流程 | Vitest/Testing Library；Playwright | 可见行为、键盘、失败恢复、真实 API/浏览器差异 |
| Rust 核心/并发 | cargo test、Clippy、必要时属性测试/基准 | 生命周期、边界、关闭/取消与正确性，性能单独测量 |
| Python/脚本 | pytest；PowerShell 用 Pester/PSScriptAnalyzer | 参数、路径、编码、退出码、幂等和清理 |
| 桌面 GUI | 宿主支持的 WebDriver/UI Automation 和真实应用 | IPC、文件对话框、安装包、系统权限；网页预览不够 |
| 手机 App | Flutter integration_test、原生平台测试或 Appium | 真机/模拟器、弱网、设备权限、前后台与签名包 |
| 性能/可靠性 | k6/JFR/对应 profiler 或故障探针 | 明确工作负载、环境、指标、恢复和正确性 |

从需求和真实差异设计最小充分测试，不为覆盖率堆实现镜像用例。独立验收先读需求与产物；不能只重复实现者总结。无法运行列明原因，失败不通过删用例、改标准或无限重试掩盖。

依据：[Penpot](https://docs.penpot.app/)、[Playwright](https://playwright.dev/docs/intro)、[Flutter 测试](https://docs.flutter.dev/testing/overview)、[Appium](https://appium.io/docs/en/latest/)、[Pester](https://pester.dev/docs/quick-start)。
