# 按软件类型和目标选方案

## 获取决定性信息

询问给谁用、在哪些设备使用、何时交付、规模与数据量、是否离线、已有系统、预算与维护者。把“快”区分为开发快、响应快、吞吐高、启动快。缺失条件会影响方向时先问，不虚构负载或替用户选择商业约束。

已有项目先读代码、构建配置与部署约定。技术事实不确定时查官方当前文档，无法核实则说明缺口。每次新增或升级依赖重新检查稳定版本、支持周期、安全公告和兼容性；不能把本文当永久版本清单。

## 工作类型与候选工具

| 工作 | 适合的方案起点 | 改选条件 | 技术细节 |
|---|---|---|---|
| 业务 Web / 管理系统 | Java 17+、Spring Boot + Spring MVC + MyBatis，关系数据库；Vue 或 React 界面按需求评估 | 既有容器与配置标准、团队经验、SEO 与界面复杂度 | [Web](web.md) |
| 传统 SSM 新项目 | Spring Framework + Spring MVC + MyBatis，Maven，JDK 17+；显式管理容器、事务与配置 | 比较独立部署、WAR/JAR、维护与配置成本，不自动替换为 Boot | [Web](web.md) |
| 内容网站 / 搜索引擎收录 | Next.js、Nuxt 等 SSR/静态生成路线 | 仅内部表单无需为 SEO 增加第二个服务端 | [Web](web.md) |
| 跨平台桌面 GUI | Web 团队比较 Electron / Tauri；原生复杂界面或设备工具比较 Qt | 安装包、系统 WebView、原生 SDK、离线、资源预算 | [桌面](desktop.md) |
| Windows 专用 GUI | C# + WPF / WinUI，或现有桌面栈 | 需要跨平台时比较 Avalonia、Qt、Tauri 等，不把 WPF 说成跨平台 | [桌面](desktop.md) |
| Android + iOS App | Flutter；React 团队可比较 React Native + Expo | 深度平台能力、原生 SDK、团队能力及上架条件 | [手机](mobile.md) |
| 单平台 App | Android：Kotlin + Jetpack Compose；iOS：Swift + SwiftUI | 目标系统版本、硬件 SDK 与分发渠道决定可用能力 | [手机](mobile.md) |
| 文件/API/数据脚本 | Python 标准库起步，必要时加 Typer、pytest | Windows 管理优先 PowerShell；短 Linux 管道优先 Bash | [脚本](scripting.md) |
| 高性能核心 / CLI / 服务 | Rust stable；网络服务可比较 Axum + Tokio | 先确认瓶颈，未测量不承诺更快；必要时仅替换热点模块 | [性能](data-performance.md) |
| Python 数据/模型 API | Python + FastAPI；长任务与请求分离 | CPU 负载、并发、失败恢复、离线及模型调用成本 | [性能](data-performance.md) |
| 部署与运维 | 现有 CI/CD；单机服务或 Compose 起步 | 有多节点调度/隔离需求才比较 Kubernetes | [运维](operations.md) |

这些是带条件的工程建议，不是所有项目统一使用的固定栈。版本事实与官方入口见 [技术依据](sources.md)。

## 目标如何改变选择

| 目标 | 优先策略 | 必须说明 |
|---|---|---|
| 尽快交付 | 熟悉的受支持框架、成熟组件、模块化单体、较少部署单元 | 真正必需功能、首批验收与后续边界 |
| 运行性能高 | 测量算法、SQL、网络、渲染和内存，再比较并发或 Rust 热点实现 | 负载、延迟/吞吐/内存基线及优化实测 |
| 安装包和内存小 | 比较系统 WebView、原生 UI、Rust CLI 与运行库 | 含依赖的真实分发体积、冷启动和目标机测量 |
| 易维护 | 现有生态、清楚模块、稳定接口、统一工程工具 | 新语言/新服务的维护人、升级与排错成本 |
| 低成本 | 减少服务与云资源，比较本地和必要的托管能力 | 实际费用、许可、账户和运营成本，不能猜预算 |
| 离线 / 数据敏感 | 本地处理、受控依赖与分发 | 首装和运行期联网点、数据外发与恢复方式 |

## 给用户的建议

用普通话给出主方案、选择理由、主要代价和有意义的备选，再列必要技术名。不要让不懂技术的用户先选框架。重要约束未清楚前只给条件方案并提问；选定后纳入当前项目技术基线。

说明界面、服务、存储和部署怎样组成系统，参考 [架构](architecture.md)。超出目录或证据不足时使用 [方案调研](research.md)，不能硬套 Java、Rust 或现有岗位示例。
