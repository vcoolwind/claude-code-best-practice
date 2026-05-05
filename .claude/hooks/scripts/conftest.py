"""
conftest.py — pytest 启动时将 check-dangerous-command.py（含连字符，
无法直接 import）以 check_dangerous_command 别名注册到 sys.modules，
供测试文件用标准 import 语句引用。
"""
import importlib.util
import sys
from pathlib import Path

def _register_module_with_hyphen(filename: str, alias: str) -> None:
    """将含连字符的 .py 文件注册为可 import 的模块别名"""
    path = Path(__file__).parent / filename
    spec = importlib.util.spec_from_file_location(alias, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules[alias] = mod

_register_module_with_hyphen("check-dangerous-command.py", "check_dangerous_command")
