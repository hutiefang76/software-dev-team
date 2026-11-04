# 安装与首次使用

## 把地址交给 AI

安装地址：[software-dev-team](https://github.com/hutiefang76/software-dev-team/tree/main/skills/software-dev-team)。它对应一个完整的技能目录，包含岗位与参考资料；不要只复制 SKILL.md 而漏掉 references。

在有本地文件/终端权限的 Codex 中发送：

```text
$skill-installer 请从 https://github.com/hutiefang76/software-dev-team/tree/main/skills/software-dev-team 安装这个技能。
先检查同名技能；如已存在，说明来源和差异，不重复创建。
```

安装后下一轮可用。Codex 可通过 `/skills` 或 `$software-dev-team` 调用；没有出现时重开会话或重启客户端。普通网页聊天是否可以安装取决于它有没有连接到目标机器的安装工具，单纯打开 GitHub 链接不代表已安装。[Codex 官方技能说明](https://learn.chatgpt.com/docs/build-skills)

## 使用 Skills CLI

需要 Node.js 22.20+。在要开发的软件项目目录执行；以下命令安装到当前项目：

```text
npx skills add hutiefang76/software-dev-team --skill software-dev-team -a codex -y
```

多个项目共用时，明确选择用户级安装：

```text
npx skills add hutiefang76/software-dev-team --skill software-dev-team -a codex -g -y
```

Claude Code 使用 `-a claude-code`，Cursor 使用 `-a cursor`。安装到多个客户端时可以传 `-a codex claude-code`。Windows 上若需要真实文件而不是符号链接，可加 `--copy`。这些参数以 [Skills CLI 文档](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) 为准。

Codex 的常见项目级目录是 `.agents/skills/software-dev-team`，Claude Code 是 `.claude/skills/software-dev-team`；具体路径及全局范围由当前安装器报告为准。旧安装器与自定义 CODEX_HOME 的路径可能不同，不要硬编码个人绝对路径。[客户端目录表](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)

CLI 安装结果能证明文件落盘；客户端加载、实际工具权限及产品开发效果要分别核实。安装会添加指令，不会注册固定数量的 Agent、开通模型账户或更改模型配置。

## 验证与开始

1. 检查安装器显示的目录含 SKILL.md、references/roles.json、references/governance.md。
2. 在客户端选择或提及软件开发团队技能。
3. 先试一个有限请求：

```text
$software-dev-team 我想做一个内部预约网站，本轮只给方案。
请明确产品经理、技术经理、模块与验收；预算和人数未知的部分列为待确认。
```

再给实际仓库和允许修改的范围，团队才进入开发。技能本体不依赖 Python；仓库里的预算计算器仅供需要计算的维护者选用。

## 更新或移除

使用 Skills CLI 安装的版本可用 `npx skills list` 查看、`npx skills check` 检查更新，再按工具提示更新指定技能。先检查本地修改和同名来源，保留需要的修改后再更新。

官方 skill-installer 安装的版本按其流程管理；同名存在时通常拒绝覆盖，不要通过重复安装掩盖冲突。卸载前核对当前安装范围与目录，只移除目标技能，不删除整个 skills 目录。
