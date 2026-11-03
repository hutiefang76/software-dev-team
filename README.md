# 软件开发虚拟团队 · Software Dev Team

[![Validate](https://github.com/hutiefang76/software-dev-team/actions/workflows/validate.yml/badge.svg)](https://github.com/hutiefang76/software-dev-team/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

一个可安装的 AI 软件开发团队 Skill：按任务选择专业岗位，用清楚的任务边界协作，以实际产物和验证结果交付。

推荐只安装 **`software-dev-team`** 这一个入口。12 个专业岗位按需加载，避免把整套团队塞进每次对话。适用于 Web、后端、桌面、数据处理、脚本和交付工作，不依赖特定业务项目或模型厂商。

## 快速开始

推荐通过 [Skills CLI](https://github.com/vercel-labs/skills) 安装，按提示选择客户端：

```text
npx skills add hutiefang76/software-dev-team --skill software-dev-team
```

也可以在支持 GitHub Skill 安装的 Codex 中发送：

```text
$skill-installer 从 https://github.com/hutiefang76/software-dev-team/tree/main/skills/software-dev-team 安装此技能。
```

其他支持 Agent Skills 的客户端，将整个 `skills/software-dev-team` 文件夹安装到该客户端的技能目录。正文、岗位和运行时脚本都在同一包中。原生子 Agent、模型和工具是否可用，以实际客户端能力为准。

安装后直接说：

```text
$software-dev-team 为当前项目实现用户资料编辑功能，沿用现有技术栈和 API，按需要分工并完成测试。
```

仅分析时：

```text
$software-dev-team 只读评审当前登录流程，交付带文件依据的问题与最小修改计划，本轮不修改产品。
```

## 用户无须单独安装 Maestro

当任务需要编排时，Skill 会自动调用自带的引导脚本：首次安装官方 `maestro-flow`，后续调用默认每 24 小时检查官方 npm 的稳定版本并自动更新。用户不需要全局安装 Maestro，也不需要记住 Maestro 命令。

安装 Skill 的动作通常只复制文件；自动准备发生在首次需要编排的调用。执行环境需要 **Node.js 22.19.0 或更高版本以及 npm**。没有 Shell 或网络权限的客户端可使用岗位与规划能力，不能声称已执行编排。

运行时安装在独立用户缓存中，不改全局 Maestro、模型账户或客户端配置。候选版本通过 CLI 与资源检查后才成为新任务默认版本；旧版本保留，进行中的任务固定原版本。更新失败时保留可用缓存并报告原因，项目状态迁移仍遵守官方流程和目标项目授权。

[自动安装与更新机制](skills/software-dev-team/references/runtime.md) · [Maestro 适配](skills/software-dev-team/references/maestro.md)

## 推荐分工

| 场景 | 建议岗位 |
|---|---|
| 清楚的小改或一次检查 | 当前成员直接完成 |
| 普通功能开发 | 协调者 + 对应工程岗位 + 测试验收 |
| 流程不清或界面改造 | 增加产品与体验岗位 |
| 跨模块接口或结构变化 | 增加架构岗位 |
| 认证、权限或敏感数据变化 | 增加安全岗位 |
| 大量明确的基础任务 | 基础执行成员 + 必要专业能力 |

12 个预设岗位：协调者、产品与体验、架构、前端、后端、桌面、数据工程、自动化脚本、部署交付、独立测试、安全、基础执行。

岗位使用 RACE（Role、Action、Context、Expectation）和完整示例。岗位提供专业能力；宿主负责工具执行和权限。角色数量不等于需要启动的 Agent 数量。

## 项目结构

```text
skills/software-dev-team/
  SKILL.md                     推荐安装入口
  agents/openai.yaml           Codex 展示元数据
  scripts/maestro-runtime.mjs  自动安装、更新及固定版本执行
  references/
    roles.json                 岗位索引
    roles/                     12 个 RACE 岗位与示例
    shared-rules.md            公共工程规范
    collaboration.md           分工、资源归属与回传
    task-card.schema.json      可选的机器可检查任务卡
    stacks.md                  按需技术能力
    hosts.md                   客户端与模型适配
    maestro.md                 官方工作流适配
    runtime.md                 自动安装与更新说明
tests/                         任务合同与运行时回归验证
scripts/validate.py             包结构、引用与示例检查
```

## 本地验证与贡献

```text
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python -m unittest discover -s tests -p "test_*.py"
node --test tests/runtime.test.mjs
```

验证修改后的指令是否在真实场景中保持范围。结构检查和自动测试不能替代跨客户端使用验证，行为评测场景见 [evals/scenarios.json](evals/scenarios.json)。

本项目维护团队岗位和 Maestro 自动接入层，上游 Maestro 使用官方 npm 发布包，不维护其源码分叉。当前测试过的上游版本及检查范围见 [运行时策略](skills/software-dev-team/references/runtime-policy.json)。

## 来源与许可

从作者原有的专用开发岗位库整理而来，保留按需加载、文件单写者和真实验收证据，移除业务专属规则、服务器信息、个人绝对路径和固定模型路线。

按照 [OpenAI 的 Skill 文档](https://learn.chatgpt.com/docs/build-skills)组织入口与渐进加载；本项目是社区项目。“推荐入口”指本项目推荐的安装方式，不代表官方收录或认证。

本项目使用 [MIT License](LICENSE)。通过 npm 下载的 Maestro 及其依赖保留各自的上游许可。
