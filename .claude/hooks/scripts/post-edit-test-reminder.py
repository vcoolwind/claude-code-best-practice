#!/usr/bin/env python3
"""
PostToolUse Hook: 编码完成后提醒测试用例

当 Write/Edit 操作的目标文件是代码文件（py/java/go/ts/js 等）时：
- 检查是否存在对应的测试文件
- 如果没有，通过 additionalContext 提醒 Claude 补充单元测试并执行
"""

import json
import os
import sys


# 需要关注的代码文件扩展名
CODE_EXTENSIONS = {
    ".py", ".java", ".go", ".ts", ".js",
    ".tsx", ".jsx", ".kt", ".rs", ".rb",
    ".cs", ".scala", ".swift",
}

# 测试文件名前缀/后缀模式（匹配 basename）
TEST_NAME_PATTERNS = [
    "test_",       # test_utils.py
    "_test.",      # utils_test.py / utils_test.go
    ".test.",      # utils.test.ts
    ".spec.",      # utils.spec.ts
]

# 测试目录名（精确匹配路径组件）
TEST_DIR_NAMES = {"tests", "test", "__tests__"}

# 测试文件后缀模式（匹配 basename 结尾）
TEST_SUFFIX_PATTERNS = [
    "Test.java", "Tests.java",
    "Test.kt", "Tests.kt",
    "Test.scala", "Spec.scala",
    "Tests.cs", "Test.cs",
    "Tests.swift",
]

# 各语言的测试文件命名约定
TEST_FILE_CONVENTIONS = {
    ".py": ["test_{name}.py", "{name}_test.py", "tests/test_{name}.py"],
    ".java": ["{Name}Test.java", "{Name}Tests.java", "test/{Name}Test.java"],
    ".go": ["{name}_test.go"],
    ".ts": ["{name}.test.ts", "{name}.spec.ts", "__tests__/{name}.test.ts"],
    ".js": ["{name}.test.js", "{name}.spec.js", "__tests__/{name}.test.js"],
    ".tsx": ["{name}.test.tsx", "{name}.spec.tsx", "__tests__/{name}.test.tsx"],
    ".jsx": ["{name}.test.jsx", "{name}.spec.jsx", "__tests__/{name}.test.jsx"],
    ".kt": ["{Name}Test.kt"],
    ".rs": ["{name}_test.rs", "tests/{name}.rs"],
    ".rb": ["{name}_test.rb", "test_{name}.rb", "spec/{name}_spec.rb"],
    ".cs": ["{Name}Tests.cs", "{Name}Test.cs"],
    ".scala": ["{Name}Test.scala", "{Name}Spec.scala"],
    ".swift": ["{Name}Tests.swift"],
}

# 各语言的测试运行命令
TEST_RUN_COMMANDS = {
    ".py": "pytest {test_file} -v",
    ".java": "mvn test -Dtest={TestClass}",
    ".go": "go test -v -run {TestFunc} ./{package}/",
    ".ts": "npx jest {test_file} 或 npx vitest {test_file}",
    ".js": "npx jest {test_file} 或 npx vitest {test_file}",
    ".tsx": "npx jest {test_file}",
    ".jsx": "npx jest {test_file}",
    ".kt": "gradle test --tests {TestClass}",
    ".rs": "cargo test {test_name}",
    ".rb": "bundle exec rspec {test_file}",
}


def is_code_file(file_path: str) -> bool:
    """判断是否为需要关注的代码文件"""
    _, ext = os.path.splitext(file_path)
    return ext.lower() in CODE_EXTENSIONS


def is_test_file(file_path: str) -> bool:
    """判断文件本身是否就是测试文件"""
    basename = os.path.basename(file_path).lower()

    # 1. 文件名前缀/包含模式
    for pattern in TEST_NAME_PATTERNS:
        if pattern in basename:
            return True

    # 2. 文件名后缀模式（如 UserServiceTest.java）
    for pattern in TEST_SUFFIX_PATTERNS:
        if basename.endswith(pattern.lower()):
            return True

    # 3. 目录名精确匹配（路径中包含 tests/ 或 test/ 或 __tests__/ 作为独立组件）
    parts = file_path.replace("\\", "/").split("/")
    for part in parts[:-1]:  # 排除文件名本身
        if part.lower() in TEST_DIR_NAMES:
            return True

    return False


def find_test_file(file_path: str) -> str | None:
    """
    根据源文件路径，查找对应的测试文件。
    返回找到的测试文件路径，或 None。
    """
    dir_path = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    name, ext = os.path.splitext(basename)

    conventions = TEST_FILE_CONVENTIONS.get(ext.lower(), [])

    for pattern in conventions:
        # 替换占位符
        test_name = pattern.replace("{name}", name).replace("{Name}", name[0].upper() + name[1:] if name else "")

        # 在同目录查找
        candidate = os.path.join(dir_path, test_name)
        if os.path.exists(candidate):
            return candidate

        # 在父目录的 tests/test/ 子目录查找
        parent = os.path.dirname(dir_path)
        for test_dir in ["tests", "test", "__tests__"]:
            candidate = os.path.join(parent, test_dir, test_name)
            if os.path.exists(candidate):
                return candidate
            # 同级 tests 目录
            candidate = os.path.join(dir_path, test_dir, test_name)
            if os.path.exists(candidate):
                return candidate

    return None


def get_test_command(ext: str) -> str:
    """获取对应语言的测试运行命令示例"""
    return TEST_RUN_COMMANDS.get(ext.lower(), "运行对应的单元测试")


def build_reminder(file_path: str, has_test: bool, test_file: str | None) -> str:
    """构建提醒信息"""
    _, ext = os.path.splitext(file_path)
    basename = os.path.basename(file_path)

    if has_test and test_file:
        return (
            f"📋 测试提醒：`{basename}` 已有对应测试文件 `{os.path.basename(test_file)}`。"
            f"\n请确认本次修改是否需要更新测试用例，并执行测试确保通过。"
            f"\n参考命令：{get_test_command(ext)}"
        )
    else:
        conventions = TEST_FILE_CONVENTIONS.get(ext.lower(), [])
        suggested_name = conventions[0].replace(
            "{name}", os.path.splitext(basename)[0]
        ).replace(
            "{Name}", basename[0].upper() + os.path.splitext(basename)[0][1:]
        ) if conventions else f"test_{basename}"

        return (
            f"⚠️ 测试提醒：`{basename}` 没有找到对应的测试文件。"
            f"\n请为本次编码补充单元测试用例（建议文件名：`{suggested_name}`），"
            f"并执行测试确保通过。"
            f"\n参考命令：{get_test_command(ext)}"
        )


def output_context(context: str) -> None:
    """输出 additionalContext 注入到 Claude 上下文"""
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, KeyError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # 只处理 Write 和 Edit 工具
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # 不是代码文件 → 不干预
    if not is_code_file(file_path):
        sys.exit(0)

    # 文件本身就是测试文件 → 不干预（避免死循环）
    if is_test_file(file_path):
        sys.exit(0)

    # 查找对应测试文件
    test_file = find_test_file(file_path)
    has_test = test_file is not None

    # 构建提醒并注入上下文
    reminder = build_reminder(file_path, has_test, test_file)
    output_context(reminder)


if __name__ == "__main__":
    main()
