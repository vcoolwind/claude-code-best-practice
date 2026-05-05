#!/usr/bin/env python3
"""
PreToolUse Hook: 拦截危险 Bash 命令

规则：
1. rm -rf / rm -fr → deny（直接拦截）
2. rm（不带 -rf/-fr）→ ask（提示用户确认）
3. 查询类命令（ls, cat, grep, find, echo 等）→ allow（默认放行）
4. 浏览用户主目录 ~ → deny（禁止直接访问）
5. curl/wget 管道到 shell → deny（远程代码执行风险）
6. 破坏性 git 操作（push --force、reset --hard、clean -f）→ ask
7. 其他命令 → 不干预（不输出 JSON，让正常权限流程处理）
"""

import json
import re
import sys


def read_input() -> dict:
    """从 stdin 读取 Claude Code 传入的 JSON"""
    return json.loads(sys.stdin.read())


def strip_quoted_strings(command: str) -> str:
    """
    移除命令中被引号包裹的字符串内容，避免对参数文本做误判。

    例如：
      git commit -m "删除 rm -rf 相关代码"  →  git commit -m ""
      echo 'rm -rf /' | cat                →  echo '' | cat
    """
    # 依次移除双引号、单引号内的内容（保留引号本身作为占位）
    result = re.sub(r'"[^"]*"', '""', command)
    result = re.sub(r"'[^']*'", "''", result)
    return result


def output_decision(decision: str, reason: str) -> None:
    """输出 hook 决定的 JSON 到 stdout"""
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(result))
    sys.exit(0)


def is_pipe_to_shell(command: str) -> bool:
    """
    检查是否将网络内容直接管道给 shell 执行（远程代码执行模式）。

    拦截模式（任意顺序均算）：
    - curl ... | bash
    - curl ... | sh
    - wget -O- ... | bash
    - bash <(curl ...)  / sh <(curl ...)

    不拦截：
    - curl url | jq     （管道给安全工具）
    - wget file.txt     （只下载，不执行）
    """
    # 模式 1：fetch 命令通过管道输出给 shell 解释器
    # 支持中间有其他管道段，例如 curl url | tr -d '\r' | bash
    pipe_to_shell = re.search(
        r'\b(curl|wget)\b.+\|\s*(bash|sh|zsh|fish|ksh|dash)\b',
        command
    )
    if pipe_to_shell:
        return True

    # 模式 2：bash <(curl ...) 进程替换形式
    process_sub = re.search(
        r'\b(bash|sh|zsh)\s+<\s*\(\s*(curl|wget)\b',
        command
    )
    if process_sub:
        return True

    return False


def is_destructive_git(command: str) -> bool:
    """
    检查是否为破坏性 git 操作。

    拦截的操作：
    - git push --force / git push -f（强制推送，可覆盖远程历史）
    - git reset --hard（丢弃本地提交或工作区修改）
    - git clean -f / -fd / -fx（删除未跟踪文件）
    - git checkout -- / git restore --source（覆盖工作区文件，不可逆）
    """
    destructive_patterns = [
        # push --force 或 push -f（位置不限）
        r'\bgit\s+push\b.*--force\b',
        r'\bgit\s+push\b.*\s-f\b',
        # reset --hard（后面可接 commit/HEAD 等）
        r'\bgit\s+reset\b.*--hard\b',
        # clean -f / -fd / -fx / -dfx 等含 f 标志的组合
        r'\bgit\s+clean\b.*-[a-z]*f',
        # checkout -- <file>（覆盖工作区）
        r'\bgit\s+checkout\s+--\s+',
        # restore（默认覆盖工作区，--staged 不算破坏性）
        r'\bgit\s+restore\b(?!.*--staged)',
    ]
    for pattern in destructive_patterns:
        if re.search(pattern, command):
            return True
    return False


def is_query_command(command: str) -> bool:
    """
    判断是否为只读/查询类命令。

    注意：curl/wget 单独使用视为只读网络请求，但若管道给 shell 则由
    is_pipe_to_shell() 优先拦截，本函数不需要重复考虑。
    同理，python3 -c / python -c 在引号内容已被 strip_quoted_strings()
    清空后，仅剩命令骨架，不会误判为危险内容，但也不再自动 allow，
    交给正常权限流程处理更安全——因此从列表中移除。
    """
    query_prefixes = [
        "ls", "ll", "la",
        "cat", "head", "tail", "less", "more",
        "grep", "rg", "ag", "ack",
        "find", "fd", "locate",
        "echo", "printf",
        "wc", "du", "df", "stat", "file",
        "which", "where", "type", "command -v",
        "pwd", "whoami", "hostname", "uname",
        "date", "cal",
        "git log", "git status", "git diff", "git show", "git branch",
        "ps", "top", "htop",
        "env", "printenv",
        "jq", "yq",
        "curl", "wget",  # 网络请求（只读；管道到 shell 已由规则5优先拦截）
        "tree",
    ]
    cmd_stripped = command.strip()
    for prefix in query_prefixes:
        if cmd_stripped.startswith(prefix):
            return True
    return False


def references_home_dir(command: str) -> bool:
    """
    检查命令是否直接浏览/访问用户主目录 ~

    拦截模式：
    - 直接 cd ~ 或 ls ~ 等操作
    - 使用 ~/.. 向上遍历
    - 不拦截 ~/project/specific-file 这种明确的子路径访问
    """
    # 匹配直接操作 ~ 本身（cd ~, ls ~, cat ~）
    # 但不匹配 ~/some/specific/path（有明确子路径的不拦截）
    patterns = [
        r'\b(cd|ls|ll|la|cat|find|tree|open|du)\s+~\s*$',        # cmd ~ (末尾)
        r'\b(cd|ls|ll|la|cat|find|tree|open|du)\s+~\s*[|;&]',    # cmd ~ | ...
        r'\b(cd|ls|ll|la|cat|find|tree|open|du)\s+~/\s*$',       # cmd ~/ (末尾)
        r'\b(cd|ls|ll|la|cat|find|tree|open|du)\s+~/\s*[|;&]',   # cmd ~/ | ...
        r'\b(cd|ls|ll|la|cat|find|tree|open|du)\s+~/\.\.',       # cmd ~/.. (向上遍历)
        # 注意：原来的 r'~\s*$' 已移除——过于宽泛，会误匹配 "git checkout branch~" 等
    ]
    for pattern in patterns:
        if re.search(pattern, command):
            return True

    # 匹配展开形式的家目录（/Users/xxx 或 /home/xxx 或 /root）
    home_patterns = [
        r'\b(cd|ls|ll|la|cat|find|tree|open|du)\s+(/Users/\w+|/home/\w+|/root)\s*$',
        r'\b(cd|ls|ll|la|cat|find|tree|open|du)\s+(/Users/\w+|/home/\w+|/root)\s*[|;&]',
        r'\b(cd|ls|ll|la|cat|find|tree|open|du)\s+(/Users/\w+|/home/\w+|/root)/?\s*$',
    ]
    for pattern in home_patterns:
        if re.search(pattern, command):
            return True

    return False


def is_rm_force(command: str) -> bool:
    """检查是否为 rm -rf 或 rm -fr（强制递归删除）"""
    # 匹配 rm 带有 -rf, -fr, -r -f, -f -r 等组合
    rm_force_patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',   # rm ... -rf, -arf, etc.
        r'\brm\s+.*-[a-z]*f[a-z]*r',   # rm ... -fr, -afr, etc.
        r'\brm\s+-r\s+-f',              # rm -r -f
        r'\brm\s+-f\s+-r',              # rm -f -r
    ]
    for pattern in rm_force_patterns:
        if re.search(pattern, command):
            return True
    return False


def is_rm_command(command: str) -> bool:
    """检查是否为 rm 命令（不含 -rf/-fr）"""
    return bool(re.search(r'\brm\s+', command))


def main() -> None:
    """Hook 入口：读取 stdin JSON，按规则决定 allow/ask/deny 或不干预"""
    try:
        data = read_input()
    except (json.JSONDecodeError, KeyError):
        # 无法解析输入，不干预
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # 只处理 Bash 工具
    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    # 去除引号内的文本，避免 commit message 等参数内容触发误报
    cmd_stripped = strip_quoted_strings(command)

    # --- 规则 5：curl/wget 管道到 shell → 直接拦截（优先级高于查询放行） ---
    if is_pipe_to_shell(cmd_stripped):
        output_decision(
            "deny",
            "🚫 安全策略：禁止将网络内容直接管道给 shell 执行（RCE 风险）。"
            "请先下载到本地文件，审查后再手动执行。"
        )

    # --- 规则 4：禁止直接浏览用户主目录 ---
    if references_home_dir(cmd_stripped):
        output_decision(
            "deny",
            "🚫 安全策略：禁止直接浏览用户主目录（~）。"
            "请指定具体的子目录路径，如 ~/projects/xxx"
        )

    # --- 规则 1：rm -rf / rm -fr → 直接拦截 ---
    if is_rm_force(cmd_stripped):
        output_decision(
            "deny",
            "🚫 安全策略：rm -rf/rm -fr 已被拦截。"
            "这是不可逆操作，请手动在终端确认后执行。"
        )

    # --- 规则 2：rm（非强制）→ 提示用户确认 ---
    if is_rm_command(cmd_stripped):
        output_decision(
            "ask",
            f"⚠️ 检测到删除操作：{command}\n请确认是否允许执行。"
        )

    # --- 规则 6：破坏性 git 操作 → 提示用户确认 ---
    if is_destructive_git(cmd_stripped):
        output_decision(
            "ask",
            f"⚠️ 检测到破坏性 git 操作：{command}\n"
            "此操作可能丢失提交或覆盖远程历史，请确认是否允许执行。"
        )

    # --- 规则 3：查询类命令 → 放行 ---
    if is_query_command(cmd_stripped):
        output_decision("allow", "✅ 查询类命令，自动放行")

    # --- 其他命令：不干预，走正常权限流程 ---
    sys.exit(0)


if __name__ == "__main__":
    main()
