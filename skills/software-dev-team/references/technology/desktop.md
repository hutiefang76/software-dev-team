# 桌面 GUI 与本地核心

先确认 Windows/macOS/Linux、最低系统、离线、设备访问、安装权限、更新渠道、包体/内存目标与团队能力。桌面 GUI 不能直接套用浏览器验证。

| 工作和目标 | 候选 | 工具与注意事项 |
|---|---|---|
| Web 团队快速交付跨平台 UI | Electron + 现有 React/Vue | Chromium/Node 生态；应用隔离、IPC、打包签名、真实资源测量 |
| 复用 Web UI，重视本地核心与分发 | Tauri + Rust + Web 前端 | 系统 WebView、权限与命令范围；核对各系统运行库及原生插件 |
| Windows 专用深度集成 | C# + WPF / WinUI | .NET、Windows SDK、安装与 UI Automation；WPF 非跨平台 |
| 跨平台复杂原生/设备界面 | Qt / C++ 或 PySide | SDK、线程、事件循环、目标机打包及选定模块许可 |
| .NET 团队需要多系统 | Avalonia 等现有成熟路线 | 核实所需控件、平台支持和发布方式，不仅看截图 |

“更小”“更快”必须在相同目标机与实际负载下测量安装体积、冷启动、内存与关键操作。选择 Rust 核心不保证 UI、SQL 或网络性能随之改善。

架构明确 UI → 应用服务/IPC → 文件/数据库/设备边界。渲染线程不做长时间阻塞工作，定义任务取消、进度、错误与窗口关闭时的资源清理。最小化文件、Shell、网络和设备权限。

交付包括真实安装包、架构/运行库要求、签名情况、离线可用性、卸载与用户数据保留规则。Tauri/Electron 的组件预览与 Mock 不替代完整应用启动、系统对话框、IPC 和设备验证。

官方依据：[Tauri](https://v2.tauri.app/start/)、[Electron](https://www.electronjs.org/docs/latest/tutorial/tutorial-quick-start)、[WPF](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/overview/)、[Qt for Python](https://doc.qt.io/qtforpython-6/)。
