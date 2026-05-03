---
name: city-coordinates
description: Get latitude and longitude coordinates for any city name. Automatically caches results to avoid repeated API calls.
user-invocable: false
allowed-tools:
  - "Read"
  - "Write"
  - "WebFetch(*)"
---

# City Coordinates Skill

根据城市名获取经纬度坐标，内部自动管理缓存。

## Task

输入一个城市名（支持中文/英文），返回该城市的经纬度坐标。优先从缓存读取，缓存未命中时调用 API 并写入缓存。

## Instructions

### Step 1: 读取坐标缓存

使用 Read 工具读取缓存文件：

- 文件路径：`.claude/agent-memory/universal-weather-agent/coord-cache.json`
- 如果文件不存在或为空，视为空缓存 `{}`
- 在 JSON 中查找是否存在目标城市的 key

### Step 2: 缓存命中 → 直接返回

如果缓存中存在该城市，直接使用缓存的 `lat` 和 `lon` 值，跳到 Step 5。

### Step 3: 缓存未命中 → 调用 Geocoding API

使用 WebFetch 调用 Open-Meteo Geocoding API：

- URL: `https://geocoding-api.open-meteo.com/v1/search?name={城市名}&count=1&language=zh`
- 从 JSON 响应中提取：
  - `results[0].latitude` → lat
  - `results[0].longitude` → lon
  - `results[0].name` → 标准化城市名（用于缓存 key）

**错误处理**：
- 如果 `results` 为空或不存在 → 返回错误："无法识别城市名：{输入}"，终止流程

### Step 4: 写入缓存

将新获取的坐标追加到缓存文件：

1. 读取当前缓存文件内容（已在 Step 1 获取）
2. 添加新条目：
   ```json
   "{城市名}": {"lat": 纬度, "lon": 经度, "cached_at": "YYYY-MM-DD"}
   ```
3. 使用 Write 工具将完整 JSON 写回文件路径：`.claude/agent-memory/universal-weather-agent/coord-cache.json`

### Step 5: 返回结果

## Expected Output

```
城市: {城市名}
纬度: {lat}
经度: {lon}
来源: 缓存 / API
```

## Notes

- Open-Meteo Geocoding API 免费，无需 API Key
- 缓存文件使用 JSON 格式，key 为城市名
- `cached_at` 记录缓存写入日期，便于未来做过期策略
- 支持中文和英文城市名查询
- 如果城市名无法识别，必须明确报错，不要猜测坐标
