# Windows / PowerShell 执行规范

在 Windows 执行命令、编写脚本及调用原生程序前读取。目标是用最少的真实探针发现参数、路径、编码和进程边界问题。

## 解释器与语法

- 核对实际 PowerShell 版本、原生 CLI 位置和工作目录。PowerShell 7 与 Windows PowerShell 5.1 的语法、编码和原生参数行为不同。
- 不照搬 Bash 的 heredoc、环境变量、反斜杠续行与管道规则。只有项目要求兼容 5.1 时才维持相应语法；不能无故重写既有入口。
- 调用含空格的可执行路径使用调用运算符和参数数组；避免多层字符串嵌套、Invoke-Expression 和不必要的 cmd /c。
- JSON 序列化不是 Shell 转义。含美元符号、反引号、引号或分号的文本不要拼进可执行命令。

## 路径、编码与结果

- 文件路径优先 -LiteralPath，使用 Join-Path；不复用 HOME、CODEX_HOME 等系统变量作任务变量。
- 区分文件编码、控制台显示及原生 stdin/stdout。PS 7 默认 UTF-8 无 BOM；兼容 5.1 的非 ASCII 脚本须核对其 BOM/编码合同。Unix 接收脚本不能批量加入 BOM 或 CRLF。
- 原生程序后立即保存 $LASTEXITCODE；$ErrorActionPreference 不能替代所有原生退出状态检查。命令返回非零时按语义判断，不把搜索无匹配等同工具崩溃。
- stdout 的 JSON 与 stderr 日志分开；stdin 只有一个明确消费者，不能同时无协议地传密码、代码与业务 payload。

## 先探针，再真实调用

1. PowerShell 脚本使用其 AST parser 做语法检查。
2. 用无害 argv 接收程序核对空格、中文、空值、引号、美元符号等实际参数，不能仅看命令字符串。
3. 对 PowerShell → SSH/WSL → Shell/sudo 分层确认解释器、路径、stdin、编码与权限；优先上传脚本/传文件，减少远程字符串解析。
4. 用与真人相同的入口做最小验证，保留首个错误和退出码，再运行被授权操作。

递归删除/移动前核对解析后的绝对路径仍在指定范围。不要在 PowerShell 枚举后交给 cmd、批处理或另一 Shell 拼接删除。清理只处理本次创建并已验证归属的路径。

验证可选择 Pester、PSScriptAnalyzer；远端脚本按对应解释器进行 bash -n / ShellCheck 等检查。静态、参数探针、本机执行、目标安装与业务回读分别报告。

官方依据：[命令解析](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_parsing)、[引号](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_quoting_rules)、[编码](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_character_encoding)、[Pester](https://pester.dev/docs/quick-start)。
