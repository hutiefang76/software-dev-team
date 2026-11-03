# 软件开发虚拟团队

[![Validate](https://github.com/hutiefang76/software-dev-team/actions/workflows/validate.yml/badge.svg)](https://github.com/hutiefang76/software-dev-team/actions/workflows/validate.yml)

告诉 AI 你想做什么软件、给谁使用、准备在哪些设备运行，以及最看重什么。团队会帮助你比较技术方案、划分功能、组织开发、测试并交付。

不懂编程也可以使用。你不必先选框架，也不必自己编写团队提示词。

## 你可以这样开始

```text
$software-dev-team 我想做一个给 20 人使用的预约网站，先尽快做出可用版本，请推荐方案并列出功能。
```

```text
$software-dev-team 我需要 Windows 桌面软件，能离线处理大文件。运行速度比开发速度更重要，请比较合适的技术。
```

```text
$software-dev-team 做一个 Android 和 iPhone 都能用的 App。预算有限，请先告诉我还需要确认什么。
```

```text
$software-dev-team 帮我分析现有软件的问题，本轮只给方案，不修改程序。
```

团队会先确认会影响方案的事情，再给出推荐、理由、代价和备选。没有把握的内容会继续查证或向你询问。

## 根据工作选择方案

| 你要做什么 | 团队会考虑什么 |
|---|---|
| Web 网站、管理系统 | Java / Spring Boot、传统 SSM、前后端分离或服务端页面；是否需要搜索引擎收录 |
| 桌面 GUI 软件 | Windows 专用或跨系统，Tauri、Electron、WPF、Qt 等方案；离线、安装包、设备访问 |
| 手机 App | Flutter、React Native / Expo，或 Android / iOS 原生开发；设备能力和上架要求 |
| 脚本与自动化 | Python、PowerShell、Bash；操作系统、参数、编码、重试与数据保护 |
| 高性能组件 | 先定位瓶颈，再评估 Rust、并发、数据库与算法；用实际负载验证 |
| 部署与运行 | 单机还是多节点，打包、配置、监控、备份和恢复；复用已有工具 |

“尽快开发完成”和“软件运行得快”是不同目标。已有软件会先考虑兼容和改动成本，新项目再比较适合的架构与工具。

## 团队怎样工作

1. 理解用户、功能、设备、预算与优先目标，查证需要的技术资料。
2. 给出适合你的方案，解释选择理由，确认尚不明确的重要条件。
3. 按功能模块划分工作，再安排产品、架构、前端、后端、测试和运维职责。
4. 开发后验证实际功能，说明哪些已完成、哪些仍未验证。

保留 12 个专业岗位，按工作需要参与。小任务由必要成员直接处理，不要求每次组成完整团队。

## 安装

使用下面的安装工具需要 Node.js 22.20 或更高版本。安装时选择你使用的 AI 编程客户端：

```text
npx skills add hutiefang76/software-dev-team --skill software-dev-team
```

在 Codex 中也可以让 `$skill-installer` 安装 [software-dev-team](https://github.com/hutiefang76/software-dev-team/tree/main/skills/software-dev-team)。

也可从 [Release](https://github.com/hutiefang76/software-dev-team/releases) 下载技能文件夹，安装到客户端的技能目录。

技能本身没有程序运行时依赖，不需要安装 Maestro，也不会自动下载或更新它。已有 Maestro 或其他编排工具可以继续独立使用。

## 进一步了解

[技术选型与适用场景](skills/software-dev-team/references/technology/selection.md) · [岗位目录](skills/software-dev-team/references/roles.json) · [开发与维护](docs/maintaining.md) · [MIT License](LICENSE)
