# 技术依据与版本核验

本次核验日期：2026-11-03。以下是技术材料入口与核验快照，不是永久锁定版本。具体项目开始和升级时再次读取当前官方发布、支持周期、兼容与安全说明；技术推荐中的权衡是工程判断，不冒充厂商的唯一推荐。

| 领域 | 已核验事实 / 使用重点 | 官方来源 |
|---|---|---|
| Java Web | Spring Boot 当前要求页为 4.1.2，最低 Java 17；容器与框架另有配套要求 | [系统要求](https://docs.spring.io/spring-boot/system-requirements.html) |
| MyBatis / Boot | Starter 4.0 配 Boot 4.0+；Starter 3.0 配 Boot 3.2–3.5；均需 Java 17+ | [兼容表](https://mybatis.org/spring-boot-starter/mybatis-spring-boot-autoconfigure/) |
| 独立 SSM | MyBatis-Spring 提供事务与 Mapper 集成；开发文档示例可能是 SNAPSHOT，须另查稳定发布 | [项目](https://mybatis.org/spring/)、[配置](https://mybatis.org/spring/getting-started.html) |
| Spring Cloud | 发布列车与 Boot 配套，不能按名称中的年份或大小版本猜兼容 | [Cloud](https://spring.io/projects/spring-cloud/) |
| Alibaba / AI | 具体项目使用当前版本说明与参考文档；不能直接复制历史最佳实践中的旧 BOM | [Alibaba](https://sca.aliyun.com/docs/2025.x/overview/faq/)、[Spring AI](https://docs.spring.io/spring-ai/reference/) |
| Web UI | Vue、React、Vite 各自的构建/框架与部署边界不同 | [Vue](https://vuejs.org/guide/introduction.html)、[React](https://react.dev/learn/creating-a-react-app)、[Vite](https://vite.dev/guide/) |
| Rust | 无 GC 的系统语言；Axum 为模块化 HTTP 框架，仍须按工作负载测性能 | [Rust](https://rust-lang.org/)、[Axum](https://docs.rs/axum/latest/axum/) |
| 桌面 | 系统 WebView、Chromium/Node、Windows 原生与 Qt 路线的运行/分发要求不同 | [Tauri](https://v2.tauri.app/start/)、[Electron](https://www.electronjs.org/docs/latest/tutorial/tutorial-quick-start)、[WPF](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/overview/)、[Qt](https://doc.qt.io/qtforpython-6/) |
| 手机 | Flutter、Expo、Android Compose、SwiftUI 分别有 SDK/原生能力与构建边界 | [Flutter](https://docs.flutter.dev/)、[Expo](https://docs.expo.dev/get-started/create-a-project/)、[Compose](https://developer.android.com/compose)、[SwiftUI](https://developer.apple.com/swiftui/) |
| 运维 | 依据交付与观测需求选工具，不预设全套基础设施 | [Compose](https://docs.docker.com/compose/)、[Ansible](https://docs.ansible.com/)、[OTel](https://opentelemetry.io/docs/) |
| 产品/测试 | 工具按原型、浏览器、桌面或原生移动工作选择 | [Penpot](https://docs.penpot.app/)、[Playwright](https://playwright.dev/docs/intro)、[Appium](https://appium.io/docs/en/latest/) |
| Windows | 原生命令参数、退出码和编码因 Shell/版本而异 | [解析](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_parsing)、[编码](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_character_encoding) |

记录所选方案的资料链接、核验日期、实际版本、兼容依据与未验证项。找不到权威依据时明确说明，并进入 [调研流程](research.md)；不要编造链接、测试或基准。
