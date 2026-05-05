#!/usr/bin/env python3
"""
PreToolUse Hook: 拦截危险 Bash 命令

规则：
1. rm -rf / rm -fr → deny（直接拦截）
2. rm（不带 -rf/-fr）→ ask（提示用户确认）
3. 查询类命令（ls, cat, grep, find, echo 等）→ allow（默认放行）
4. 浏览用户主目录 ~ → deny（禁止直接访问）
5. 其他命令 → 不干预（不输出 JSON，让正常权限流程处理）
"""

import json
import re
import sys


def read_input() -> dict:
    """从 stdin 读取 Claude Code 传入的 JSON"""
    return json.loads(sys.stdin.read())


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


def is_query_command(command: str) -> bool:
    """判断是否为只读/查询类命令"""
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
        "python3 -c", "python -c",  # 一行脚本（通常是查询）
        "jq", "yq",
        "curl", "wget",  # 网络请求（只读）
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
        r'~\s*$',                                                  # 单独的 ~
    ]
    for pattern in patterns:
        if re.search(pattern, command):
            return True

    # 匹配展开形式的家目录
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


def main():
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

    # --- 规则 4：禁止直接浏览用户主目录 ---
    if references_home_dir(command):
        output_decision(
            "deny",
            "🚫 安全策略：禁止直接浏览用户主目录（~）。"
            "请指定具体的子目录路径，如 ~/projects/xxx"
        )

    # --- 规则 1：rm -rf / rm -fr → 直接拦截 ---
    if is_rm_force(command):
        output_decision(
            "deny",
            "🚫 安全策略：rm -rf/rm -fr 已被拦截。"
            "这是破坏性操作，请手动在终端执行或改用更安全的删除方式。"
        )

    # --- 规则 2：rm（非强制）→ 提示用户确认 ---
    if is_rm_command(command):
        output_decision(
            "ask",
            f"⚠️ 检测到删除操作：{command}\n请确认是否允许执行。"
        )

    # --- 规则 3：查询类命令 → 放行 ---
    if is_query_command(command):
        output_decision("allow", "✅ 查询类命令，自动放行")

    # --- 其他命令：不干预，走正常权限流程 ---
    sys.exit(0)


if __name__ == "__main__":
    main()
