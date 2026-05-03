---
name: weather-query
description: Fetch current temperature and weather condition for a given latitude/longitude using Open-Meteo API.
user-invocable: false
allowed-tools:
  - "WebFetch(*)"
---

# Weather Query Skill

根据经纬度获取当前温度和天气状况。

## Task

输入经纬度坐标和城市名，返回该位置的当前温度（摄氏度）和天气状况（中文描述）。

## Instructions

### Step 1: 调用 Open-Meteo Weather API

使用 WebFetch 请求当前天气数据：

- URL: `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code`

将 `{lat}` 和 `{lon}` 替换为实际坐标值。

### Step 2: 解析响应

从 JSON 响应中提取：
- `current.temperature_2m` → 当前温度
- `current.weather_code` → 天气代码（WMO 标准）

### Step 3: 将 weather_code 转为中文描述

使用以下 WMO Weather Code 映射表：

| Code | 描述 |
|------|------|
| 0 | 晴 |
| 1 | 大部晴朗 |
| 2 | 局部多云 |
| 3 | 多云 |
| 45 | 雾 |
| 48 | 雾凇 |
| 51 | 小毛毛雨 |
| 53 | 中毛毛雨 |
| 55 | 大毛毛雨 |
| 56 | 冻毛毛雨（小） |
| 57 | 冻毛毛雨（大） |
| 61 | 小雨 |
| 63 | 中雨 |
| 65 | 大雨 |
| 66 | 冻雨（小） |
| 67 | 冻雨（大） |
| 71 | 小雪 |
| 73 | 中雪 |
| 75 | 大雪 |
| 77 | 雪粒 |
| 80 | 阵雨（小） |
| 81 | 阵雨（中） |
| 82 | 阵雨（大） |
| 85 | 阵雪（小） |
| 86 | 阵雪（大） |
| 95 | 雷暴 |
| 96 | 雷暴伴小冰雹 |
| 99 | 雷暴伴大冰雹 |

如果 weather_code 不在上表中，返回"未知天气（code: {数字}）"。

### Step 4: 返回结果

## Expected Output

```
城市: {城市名}
温度: {温度}°C
天气: {中文天气描述}
```

## Notes

- Open-Meteo API 免费，无需 API Key
- 温度单位默认为摄氏度（API 默认值）
- weather_code 遵循 WMO 4677 标准
- 如果 API 调用失败，返回错误信息："天气查询失败，请稍后重试"
- 城市名由调用者传入（仅用于展示），本 Skill 不负责城市→坐标的转换
