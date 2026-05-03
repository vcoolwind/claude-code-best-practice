"""weather-voice.py 核心逻辑测试"""

import importlib.util
import sys
from pathlib import Path

# 导入带连字符的模块
spec = importlib.util.spec_from_file_location(
    "weather_voice", Path(__file__).parent / "weather-voice.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

identify_stage = mod.identify_stage
get_voice_text = mod.get_voice_text


# ===== identify_stage 测试 =====

class TestIdentifyStage:
    def test_skill_city_coordinates(self):
        data = {"tool_name": "Skill", "tool_input": {"skill": "city-coordinates"}}
        assert identify_stage(data) == "city-coordinates"

    def test_skill_weather_query(self):
        data = {"tool_name": "Skill", "tool_input": {"skill": "weather-query"}}
        assert identify_stage(data) == "weather-query"

    def test_write_history(self):
        data = {"tool_name": "Write", "tool_input": {"file_path": ".claude/agent-memory/universal-weather-agent/history.md"}}
        assert identify_stage(data) == "Write:history"

    def test_read_coord_cache(self):
        data = {"tool_name": "Read", "tool_input": {"file_path": ".claude/agent-memory/universal-weather-agent/coord-cache.json"}}
        assert identify_stage(data) == "city-coordinates"

    def test_unknown_skill(self):
        data = {"tool_name": "Skill", "tool_input": {"skill": "unknown-skill"}}
        assert identify_stage(data) is None

    def test_unrelated_write(self):
        data = {"tool_name": "Write", "tool_input": {"file_path": "/tmp/other.txt"}}
        assert identify_stage(data) is None

    def test_empty_data(self):
        assert identify_stage({}) is None


# ===== get_voice_text 测试 =====

class TestGetVoiceText:
    def test_pre_city_coordinates(self):
        assert get_voice_text("pre", "city-coordinates") == "正在获取城市坐标"

    def test_post_weather_query(self):
        assert get_voice_text("post", "weather-query") == "天气查询完成"

    def test_error_with_default(self):
        assert get_voice_text("error", "Write:history") == "操作失败"

    def test_error_specific(self):
        assert get_voice_text("error", "city-coordinates") == "坐标查询失败"

    def test_none_stage(self):
        assert get_voice_text("pre", None) is None

    def test_post_write_history(self):
        assert get_voice_text("post", "Write:history") == "历史记录已保存"
