#!/usr/bin/env python3
"""
Weather Voice Hook
==================
Universal Weather Agent 的语音播报脚本。
根据 stdin 传入的 hook JSON 数据，识别当前调用的工具/Skill，
播报对应阶段的中文提示。

用法（由 Agent hooks 自动调用）：
  python3 weather-voice.py --event=pre
  python3 weather-voice.py --event=post
  python3 weather-voice.py --event=error

stdin 传入 JSON 示例：
  {"hook_event_name": "PreToolUse", "tool_name": "Skill", "tool_input": {"skill": "city-coordinates", ...}}
  {"hook_event_name": "PostToolUse", "tool_name": "Write", "tool_input": {"file_path": "...history.md", ...}}
"""

import sys
import json
import subprocess
import platform
import argparse


# ===== 分阶段播报规则 =====
# 根据 (event, tool_name, skill/context) 决定播报内容
# 格式：(event, tool_name_pattern, context_pattern) → 播报文本

# PreToolUse 播报（开始做某事）
PRE_VOICE_MAP = {
    "city-coordinates": "正在获取城市坐标",
    "weather-query": "正在查询天气",
    "Write:history": "正在记录查询历史",
}

# PostToolUse 播报（某事完成）
POST_VOICE_MAP = {
    "city-coordinates": "坐标获取完成",
    "weather-query": "天气查询完成",
    "Write:history": "历史记录已保存",
}

# 错误播报
ERROR_VOICE_MAP = {
    "city-coordinates": "坐标查询失败",
    "weather-query": "天气查询失败",
    "_default": "操作失败",
}


def speak(text: str) -> bool:
    """
    调用系统 TTS 播报文本。

    Args:
        text: 要播报的中文文本

    Returns:
        True if successful, False otherwise
    """
    system = platform.system()

    try:
        if system == "Darwin":
            # macOS: 使用 say 命令，Ting-Ting 是中文语音
            subprocess.Popen(
                ["say", "-v", "Ting-Ting", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        elif system == "Linux":
            # Linux: 尝试 espeak
            subprocess.Popen(
                ["espeak", "-v", "zh", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True
        else:
            return False
    except (FileNotFoundError, OSError):
        return False


def identify_stage(hook_data: dict) -> str | None:
    """
    从 hook JSON 数据中识别当前处于哪个业务阶段。

    Returns:
        阶段标识符（如 "city-coordinates"、"weather-query"、"Write:history"），
        无法识别时返回 None
    """
    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})

    # Skill 调用：从 tool_input 中提取 skill 名
    if tool_name == "Skill":
        skill_name = tool_input.get("skill", "")
        if skill_name in ("city-coordinates", "weather-query"):
            return skill_name

    # Write 调用：检查是否写入 history.md
    if tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        if "history" in file_path:
            return "Write:history"

    # Read 调用：检查是否读取 coord-cache（坐标缓存阶段的一部分）
    if tool_name == "Read":
        file_path = tool_input.get("file_path", "")
        if "coord-cache" in file_path:
            return "city-coordinates"

    return None


def get_voice_text(event: str, stage: str | None) -> str | None:
    """
    根据事件类型和阶段，返回要播报的文本。

    Args:
        event: "pre" / "post" / "error"
        stage: 阶段标识符

    Returns:
        播报文本，或 None（表示不播报）
    """
    if not stage:
        return None

    if event == "pre":
        return PRE_VOICE_MAP.get(stage)
    elif event == "post":
        return POST_VOICE_MAP.get(stage)
    elif event == "error":
        return ERROR_VOICE_MAP.get(stage, ERROR_VOICE_MAP["_default"])

    return None


def main():
    parser = argparse.ArgumentParser(description="Weather voice hook")
    parser.add_argument(
        "--event",
        type=str,
        choices=["pre", "post", "error"],
        required=True,
        help="Hook event type: pre(开始), post(完成), error(失败)",
    )
    args = parser.parse_args()

    # 读取 stdin 的 hook JSON 数据
    hook_data = {}
    try:
        stdin_content = sys.stdin.read().strip()
        if stdin_content:
            hook_data = json.loads(stdin_content)
    except (json.JSONDecodeError, Exception):
        pass

    # 识别当前阶段
    stage = identify_stage(hook_data)

    # 获取播报文本
    text = get_voice_text(args.event, stage)

    if text:
        speak(text)

    sys.exit(0)


if __name__ == "__main__":
    main()
