# 集成与安装验证记录

日期：2026-11-04。环境：Windows、PowerShell 7.6.9、Python 3.14.5、Node.js 24.21.0、Skills CLI 1.7.6。

## 已执行

- scripts/validate.py：单一技能、12 个岗位、相对引用、纯指令边界和两份任务卡示例检查通过。
- unittest：49 项通过，覆盖原有权限/外发边界、可选 RACI/ITTO/交付字段，以及三点估算、共享容量、日历、未知费用、超限和文件覆盖保护。
- 在隔离项目中使用真实安装入口：
  `npx --yes skills@latest add ../.. --skill software-dev-team -a codex claude-code --copy -y`
- Codex 的 .agents/skills/software-dev-team 和 Claude Code 的 .claude/skills/software-dev-team 各 42 个文件；逐文件 SHA-256 与安装源一致，两份安装目录再次通过包结构检查。安装未改用户全局客户端配置。
- GUI 示例实际计算的 PERT 为 39,472 CNY、2026-12-09，按样例截止 12-04 标记 late。
- Web 示例仅把预算/截止收紧为 10,000 CNY、2026-11-13，实际计算 PERT 为 20,746 CNY、2026-11-27，明确 over_limit 与 late。所有数字都是样例估算，不是报价或已发生费用。

## 场景决策复核

下列是本次实现者按技能执行的有界规划复核，不声称独立或盲测；回归请求保留在 evals/scenarios.json。

| 请求 | 得到的决定与可执行下一步 | 证据限制 |
|---|---|---|
| 完整 Web 范围但预算 10,000、截止 11-13 | 计算显示两项冲突；product 明确可删验收项，architect 核对影响，planner 重算，由有权限的 OWNER 决定；不承诺原范围交付 | 运行了计划工具，未开发业务 |
| 前后端争用 api-schema.json，错误/幂等未定 | architect 负责合同并指定一个写入者；先确认业务语义、兼容向量，再开放不重叠模块的实现；qa 做跨端验收 | 产出任务安排，未创建真实成员或改业务仓库 |
| 一人兼 product/architect/planner，每日 4h，费率未知 | 三个责任席位映射同一 executor；合计每日 4h；费用保持 null，不能宣称独立复核或免费 | 字段和规则复核，非真实排期承诺 |

## 未证明的事项

客户端目录安装成功不等于客户端 UI 已加载、自动触发稳定或完整产品开发成功。本次未启动 Codex/Claude Code GUI 观察技能列表，也未统计多轮产品开发的质量、返工或真实成本。

本地安装测试使用当前源码；公开 GitHub 地址的下载结果以实际发布后的安装记录为准。CI 的平台运行结果与这些本地验证分别报告，不因提交触发就写成已通过。

预算计算器保留在仓库 scripts/，不随技能安装。其日粒度贪心排程不保证最优，不推断法定假期、真实 agent 时长或账单。新字段结构检查不能证明组织授权和实际管理过程完整。
