#!/usr/bin/env python3
"""
Stop Hook: 任务结束时验证测试通过

触发时机：Claude 认为任务完成、准备停止时
行为逻辑：
  1. 通过 git diff 获取本次改动的代码文件
  2. 排除非代码文件（.md/.json/.yaml 等）
  3. 如果没有代码文件变更 → 放行
  4. 检测项目测试框架（pytest/jest/go test）
  5. 查找受影响文件的对应测试
  6. 执行测试，失败则 block（最多 3 轮）
  7. 超时保护（30s）

决策方式：
  - exit 0 → 允许 Claude 停止
  - exit 2 + stderr → 阻止停止，Claude 继续修复
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# ============================================================
# 配置
# ============================================================

# 需要测试验证的代码文件扩展名
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".go", ".java", ".kt", ".rs", ".rb",
    ".cs", ".scala", ".swift",
}

# 排除的路径模式（不需要测试的代码）
EXCLUDE_PATTERNS = [
    "test_", "_test.", ".test.", ".spec.",
    "conftest.py", "setup.py", "setup.cfg",
    "__init__.py", "migrations/",
]

# 测试执行超时（秒）
TEST_TIMEOUT = 30

# 最大阻止轮次（通过文件追踪）
MAX_BLOCK_ROUNDS = 3

# ============================================================
# 核心逻辑
# ============================================================


def read_input() -> dict:
    """从 stdin 读取 Stop hook 传入的 JSON"""
    return json.loads(sys.stdin.read())


def get_changed_code_files(cwd: str) -> list[str]:
    """
    通过 git diff 获取本次改动的代码文件。
    优先用 staged + unstaged 的 diff，覆盖已提交和未提交的情况。
    """
    files = set()

    # 未暂存的改动
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True, cwd=cwd, timeout=5
        )
        if result.returncode == 0:
            files.update(result.stdout.strip().splitlines())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 已暂存的改动
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=cwd, timeout=5
        )
        if result.returncode == 0:
            files.update(result.stdout.strip().splitlines())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 如果都没有，看最近一次 commit 的改动（可能刚 commit 完）
    if not files:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True, text=True, cwd=cwd, timeout=5
            )
            if result.returncode == 0:
                files.update(result.stdout.strip().splitlines())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # 过滤：只保留代码文件，排除测试文件本身
    code_files = []
    for f in files:
        if not f:
            continue
        ext = Path(f).suffix.lower()
        if ext not in CODE_EXTENSIONS:
            continue
        # 排除测试文件和配置文件
        basename = os.path.basename(f).lower()
        if any(pattern in basename or pattern in f.lower() for pattern in EXCLUDE_PATTERNS):
            continue
        code_files.append(f)

    return code_files


def detect_test_framework(cwd: str) -> str | None:
    """检测项目使用的测试框架"""
    # Python: pytest
    if any(
        os.path.exists(os.path.join(cwd, f))
        for f in ["pytest.ini", "pyproject.toml", "setup.cfg", "conftest.py"]
    ):
        # 确认 pytest 可用
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "--version"],
                capture_output=True, cwd=cwd, timeout=5
            )
            if result.returncode == 0:
                return "pytest"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # JavaScript/TypeScript: jest or vitest
    pkg_json = os.path.join(cwd, "package.json")
    if os.path.exists(pkg_json):
        try:
            with open(pkg_json) as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts", {})
            deps = {
                **pkg.get("devDependencies", {}),
                **pkg.get("dependencies", {}),
            }
            if "vitest" in deps:
                return "vitest"
            if "jest" in deps or "test" in scripts:
                return "jest"
        except (json.JSONDecodeError, IOError):
            pass

    # Go
    if any(
        os.path.exists(os.path.join(cwd, f))
        for f in ["go.mod", "go.sum"]
    ):
        return "go_test"

    return None


def find_test_files_for(code_files: list[str], cwd: str, framework: str) -> list[str]:
    """找到受影响代码文件对应的测试文件"""
    test_files = []

    for code_file in code_files:
        name = Path(code_file).stem
        ext = Path(code_file).suffix
        dir_path = os.path.dirname(code_file)

        candidates = []

        if framework == "pytest":
            candidates = [
                os.path.join(dir_path, f"test_{name}.py"),
                os.path.join(dir_path, f"{name}_test.py"),
                os.path.join(dir_path, "tests", f"test_{name}.py"),
                os.path.join("tests", f"test_{name}.py"),
            ]
        elif framework in ("jest", "vitest"):
            base_ext = ext  # .ts / .tsx / .js / .jsx
            candidates = [
                os.path.join(dir_path, f"{name}.test{base_ext}"),
                os.path.join(dir_path, f"{name}.spec{base_ext}"),
                os.path.join(dir_path, "__tests__", f"{name}.test{base_ext}"),
                os.path.join(dir_path, "__tests__", f"{name}{base_ext}"),
            ]
        elif framework == "go_test":
            candidates = [
                os.path.join(dir_path, f"{name}_test.go"),
            ]

        for candidate in candidates:
            full_path = os.path.join(cwd, candidate)
            if os.path.exists(full_path):
                test_files.append(candidate)
                break

    return test_files


def run_tests(test_files: list[str], cwd: str, framework: str) -> tuple[bool, str]:
    """
    执行测试，返回 (是否通过, 输出信息)
    """
    try:
        if framework == "pytest":
            cmd = ["python3", "-m", "pytest", "-x", "--tb=short", "-q"] + test_files
        elif framework == "jest":
            cmd = ["npx", "jest", "--bail", "--no-coverage"] + test_files
        elif framework == "vitest":
            cmd = ["npx", "vitest", "run", "--reporter=verbose"] + test_files
        elif framework == "go_test":
            # go test 需要包路径
            packages = set()
            for f in test_files:
                packages.add("./" + os.path.dirname(f))
            cmd = ["go", "test", "-v", "-count=1"] + list(packages)
        else:
            return True, ""

        result = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=cwd, timeout=TEST_TIMEOUT
        )

        output = result.stdout + result.stderr
        # 截断过长输出
        if len(output) > 2000:
            output = output[:1000] + "\n...(truncated)...\n" + output[-800:]

        return result.returncode == 0, output

    except subprocess.TimeoutExpired:
        return False, f"⏱️ 测试执行超时（>{TEST_TIMEOUT}s），建议手动验证"
    except FileNotFoundError as e:
        return True, f"测试工具未找到: {e}"


def get_block_count(session_id: str, cwd: str) -> int:
    """获取当前 session 被 block 的次数（通过临时文件追踪）"""
    track_file = os.path.join(cwd, ".claude", ".stop-hook-count-" + session_id[:8])
    if os.path.exists(track_file):
        try:
            with open(track_file) as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return 0
    return 0


def increment_block_count(session_id: str, cwd: str) -> int:
    """递增 block 计数并返回新值"""
    track_file = os.path.join(cwd, ".claude", ".stop-hook-count-" + session_id[:8])
    count = get_block_count(session_id, cwd) + 1
    try:
        os.makedirs(os.path.dirname(track_file), exist_ok=True)
        with open(track_file, "w") as f:
            f.write(str(count))
    except IOError:
        pass
    return count


def cleanup_block_count(session_id: str, cwd: str) -> None:
    """清理计数文件（测试通过时）"""
    track_file = os.path.join(cwd, ".claude", ".stop-hook-count-" + session_id[:8])
    try:
        if os.path.exists(track_file):
            os.remove(track_file)
    except IOError:
        pass


def block_stop(reason: str) -> None:
    """阻止 Claude 停止，输出原因到 stderr"""
    print(reason, file=sys.stderr)
    sys.exit(2)


def allow_stop() -> None:
    """允许 Claude 停止"""
    sys.exit(0)


# ============================================================
# 入口
# ============================================================


def main():
    data = read_input()
    session_id = data.get("session_id", "unknown")
    cwd = data.get("cwd", os.getcwd())

    # 1. 获取改动的代码文件
    code_files = get_changed_code_files(cwd)
    if not code_files:
        allow_stop()

    # 2. 检测测试框架
    framework = detect_test_framework(cwd)
    if not framework:
        # 没有测试框架，不强制验证
        allow_stop()

    # 3. 查找对应的测试文件
    test_files = find_test_files_for(code_files, cwd, framework)
    if not test_files:
        # 没找到测试文件，放行（PostToolUse hook 已经提醒过了）
        allow_stop()

    # 4. 检查 block 轮次
    block_count = get_block_count(session_id, cwd)
    if block_count >= MAX_BLOCK_ROUNDS:
        # 超过最大修复轮次，不再阻止，改为提醒
        cleanup_block_count(session_id, cwd)
        print(
            f"⚠️ 已尝试 {MAX_BLOCK_ROUNDS} 轮自动修复仍未通过，"
            "建议手动检查测试失败原因。",
            file=sys.stderr
        )
        # exit 0 允许停止，但 stderr 信息仍会展示
        allow_stop()

    # 5. 执行测试
    passed, output = run_tests(test_files, cwd, framework)

    if passed:
        # 测试通过，清理计数，放行
        cleanup_block_count(session_id, cwd)
        allow_stop()
    else:
        # 测试失败，阻止停止
        round_num = increment_block_count(session_id, cwd)
        remaining = MAX_BLOCK_ROUNDS - round_num

        block_stop(
            f"🚫 测试未通过（第 {round_num}/{MAX_BLOCK_ROUNDS} 轮修复）\n"
            f"剩余 {remaining} 轮自动修复机会\n\n"
            f"失败的测试文件: {', '.join(test_files)}\n"
            f"测试框架: {framework}\n\n"
            f"--- 测试输出 ---\n{output}\n"
            f"--- 结束 ---\n\n"
            f"请修复上述测试失败，然后再次尝试完成任务。"
        )


if __name__ == "__main__":
    main()
