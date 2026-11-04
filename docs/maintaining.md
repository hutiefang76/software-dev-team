# 开发与维护

## 内容归属

- README：面向使用者，解释能解决什么、如何开始和实际限制。
- SKILL.md：面向执行 AI，规定需求澄清、选型、分工与交付方法，不夹带作者交接话术。
- references/roles：12 个职责岗位的专业判断、工作流程、工具选择、边界和交付。
- references/specialties：Java、Rust 等按语言/领域加载的工程能力，不新增常驻成员。
- references/technology：按软件类型与任务目标选方案，附官方资料和核验日期。
- 本文、AGENTS、测试与验证脚本：维护者入口，不塞进用户日常回复。

维护者、执行者和最终用户的表达要分开。对用户输出方案/结果，内部协议、JSON、测试编号和临时路径留在必要的工作记录。源项目、个人路径、环境地址、凭据和真实回执不得写入公开材料。

## 轻量边界

当前版本为纯指令和参考资料，技能包内没有程序、运行时或编排依赖。Maestro 完全独立，技能不安装、不包装、不更新它。旧版本的安装器是历史实现，不是当前能力。

角色按需加载；轻量来自没有运行时包装与重复上下文，不以削薄专业能力换文件数量。Java/Rust 正文为已授权专业角色材料整理，其他岗位采用同等专业标准，不机械复制同一 RACE 段落。

## 修改与验证

```text
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python -m unittest discover -s tests -p "test_*.py"
```

验证包内相对引用、岗位与能力索引、任务卡和示例边界。新增参考文件必须有实际调用入口。脚本检查不能证明 AI 的推荐正确，改专业行为后还应做独立的场景前向验证。

选型事实先查官方当前要求、支持/安全与兼容矩阵，更新 sources 的核验说明；条件推荐与官方事实分开。模型、框架或工具名称不能充当运行证据，不凭记忆拼版本。

发布时从确定的 Git 提交打包 skills/software-dev-team，检查无执行文件、外部私有路径和资料遗漏，附真实检查范围。Windows/Linux 的 Python 结构/合同检查不等于所有客户端和业务流程已验证。

## 交付管理扩展

治理规则以 references/governance.md 为真源，预算/容量口径以 references/delivery-planning.md 为真源；产品、技术和交付责任映射到既有 product、architect、planner，不注册新岗位或新状态系统。

任务卡可选 raci、itto、delivery；旧示例保持有效，新增示例明确未知费用和容量。结构检查验证单 A、非空 R、类别冲突、日期、估算顺序、非有限值和币种；不能证明实际授权、职责覆盖完整或已执行过程。

## 可选离线计划计算器（仅仓库工具）

skills/software-dev-team 内仍只有指令和参考资料。scripts/estimate_delivery.py 是仓库中的可选工具，不随单技能安装，也不是技能工作前提，不含安装/更新/编排程序。需要时在仓库根目录使用 Python 3.10+ 标准库运行：

```text
python -X utf8 scripts/estimate_delivery.py examples/web-plan.json --out web-report.json
python -X utf8 scripts/estimate_delivery.py examples/gui-network-plan.json --out gui-report.json
```

现有输出默认不覆盖；明确需要时使用 --overwrite。输入与输出不能相同。退出码 0 仅表示计算成功，必须阅读各情景的 budget_status/deadline_status；未知费用给出 cost_complete=false 和总额 null，不能当作免费。

示例全部是虚构工时/费率，PM/TL/DM 分别表示 product/architect/planner 职责，不是原生 Agent ID。脚本验证 RACI/ITTO 结构、角色/资源与无环依赖，并按真实资源 ID 共用日容量。O/M/P 产生乐观、PERT 与悲观情景，不是统计置信区间。

日期为周一至周五并排除显式 holidays；不自动推断法定节假日或调休。排程按输入优先的贪心顺序，依赖在上游完成后的下一个工作日开始，不保证最优。预备金只加金额，不自动延长日期；没有关键路径分析、实际账单跟踪或 agent 墙钟预测。AC+ETC 的持续预测仍由既有计划维护。

## 技能维护约定

描述负责发现，SKILL.md 负责判断和引用，岗位定义能力，任务卡定义本次范围与验收，避免跨文件复制规则。新增细节按需加载；只读/实施/外发/发布边界沿用用户与宿主授权。

每次发布分别记录结构测试、确定性计算、规划试用、真实安装和产品交付证据。更长提示词或更多文件不证明更好效果。参考 [OpenAI 技能编写](https://learn.chatgpt.com/docs/build-skills)；用户级用法留在 [安装说明](install.md)。

最近一次集成与真实安装检查见 [验证记录](verification.md)。
