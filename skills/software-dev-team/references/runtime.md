# 自动安装与官方更新

## 使用者体验

用户安装整个 Skill 即可，无须全局安装 Maestro。首次需要编排时，AI 运行包内脚本；脚本从官方 npm 解析稳定版本、安装到独立缓存并检查后返回机器可读回执。

需要 Node.js 22.19.0+ 与 npm。Skill 文件复制通常没有跨客户端通用的安装钩子，因此自动安装在首次调用时发生。纯聊天、无网络或禁止执行程序的宿主不能自动安装；此时岗位与分析能力仍可用。

## 自动更新

每次 `ensure` 检查缓存，默认每 24 小时从固定官方渠道检查一次。新版本安装到自己的目录，校验包版本、npm 完整性记录、必要命令、生命周期能力协议及上游路由/资源文件。全部通过后原子切换默认指针。

旧版本保留，运行中任务始终传入回执里的版本。更新失败或离线时使用现有可用版本并返回具体状态；首次安装没有缓存而失败时返回非零退出码，不伪称安装完成。

仅安装官方 npm 软件不发送项目源码或模型请求；后续调用外部成员仍遵守当前项目外发范围。安装使用 `--ignore-scripts`，不自动执行依赖的安装生命周期脚本。CLI 冒烟检查不证明每个可选原生扩展或所有官方工作流均可用，所需额外能力在实际使用时另验。

脚本不自动安装全局 Hooks、MCP、模型账户或客户端原生成员。官方运行时资源复制到版本自己的托管目录，`MAESTRO_HOME` 只在该版本子进程中指定；某些上游功能仍可能读取现有用户配置，应按任务范围调用。

更新的是官方软件包，**不自动迁移目标仓的 `.workflow` 状态**。涉及迁移时先使用当前官方预览与备份流程，遵守用户授权。上游协议出现不兼容时保留已用版本并报告，不修改上游完成协议来绕过检查。

## 命令

以下命令均从已安装的 Skill 目录执行；在目标项目使用时把脚本换成它的绝对路径，并保留目标项目为当前工作目录。

```text
node scripts/maestro-runtime.mjs ensure
node scripts/maestro-runtime.mjs status
node scripts/maestro-runtime.mjs ensure --refresh
node scripts/maestro-runtime.mjs ensure --offline
node scripts/maestro-runtime.mjs run --version 0.5.93 -- --version
```

`--refresh` 提前检查并自动更新，`--offline` 只使用已有版本。`run` 必须明确版本，不会在调用中隐式切换。这里的版本仅为命令示例，以实际 `ensure` 回执为准。

可用 `--cache-root <目录>` 或 `SOFTWARE_DEV_TEAM_CACHE` 改变缓存位置。默认优先当前 `CODEX_HOME/cache/software-dev-team`，其次 XDG/系统用户缓存位置。不修改这些系统变量。

自定义 npm 安装位置且无法自动发现 `npm-cli.js` 时，可设 `SOFTWARE_DEV_TEAM_NPM_CLI` 为其真实路径；这只是本地可执行文件入口，不改变下载渠道。所有 npm 调用使用参数数组，不经过 Shell 拼接。

## 版本与检查范围

官方包名、最低 Node 版本、测试过的版本和完整性记录在 [runtime-policy.json](runtime-policy.json)。`tested_version` 是维护者核验基线，不把之后自动发现的新版本冒充已做完整行为验证。

缓存包含版本目录、托管资源、npm 缓存和状态；不会写入 Skill 安装目录。安装锁避免并发更新；其他任务可继续运行已固定的旧版本。没有后台服务、定时任务或自动清理旧版本。

上游渠道：[npm maestro-flow](https://www.npmjs.com/package/maestro-flow)。这里指软件开发编排工具 `maestro-flow`，与同名移动 UI 测试产品不同。
