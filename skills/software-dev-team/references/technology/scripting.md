# 脚本、自动化与 CLI

| 工作 | 优先比较 | 工具与边界 |
|---|---|---|
| 跨平台文件/API/批处理 | Python 标准库，必要时 Typer/Click | argparse/pathlib/subprocess、pytest、Ruff；参数数组，不经 Shell 拼接 |
| Windows 系统管理 | PowerShell | 类型化参数、对象管道、Pester/PSScriptAnalyzer；先读 [Windows 规范](windows-shell.md) |
| Linux 短管道与服务胶水 | POSIX shell/Bash | 以目标解释器语法为准，适用时 bash -n / ShellCheck；退出码和管道失败 |
| 可分发、高负载或资源受限工具 | Rust CLI | clap 等必要依赖、cargo test / fmt / Clippy，明确版本与目标架构 |

先列输入输出、路径和编码、工作目录、进程、权限、副作用、超时/取消、重试与恢复。文件转换和复杂状态逐渐增多时，比较可测试的 Python/Rust 模块，不无限扩展 Shell 字符串。

复用现有正式入口，脚本保持业务边界清楚。验证无害参数探针后再进行真实下载、远程执行或大文件操作；长任务需要稳定 ID、终态、日志与重新查询，不以启动成功当完成。

安全处理临时文件、锁、finally 清理、输入校验与范围检查。重复执行要有明确语义，不盲目重试非幂等操作。外部程序失败必须传播，不吞异常或把空输出当成功。
