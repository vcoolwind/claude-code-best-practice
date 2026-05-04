---
name: coordinate-validator
description: Validate city coordinates by reverse geocoding. Checks if the coordinates actually correspond to the expected city.
user-invocable: false
allowed-tools:
  - "WebFetch(*)"
---

# Coordinate Validator Skill

通过反向地理编码校验坐标是否与预期城市匹配。

## Task

输入城市名、纬度、经度，校验坐标是否合理，返回校验结果。

## Instructions

### Step 1: 范围校验

检查坐标基本合法性：
- 纬度必须在 -90 ~ 90 之间
- 经度必须在 -180 ~ 180 之间

如果不合法，直接返回校验失败，不调用 API。

### Step 2: 反向地理编码（Nominatim）

使用 WebFetch 调用 **OpenStreetMap Nominatim** 反向地理编码 API，用坐标反查地名：

- URL: `https://nominatim.openstreetmap.org/reverse?lat={纬度}&lon={经度}&format=json&accept-language=zh&zoom=10`
- 必须设置 User-Agent header（Nominatim 要求）：`User-Agent: claude-weather-agent/1.0`

从响应中提取：
- `address.city` 或 `address.state`（有些城市在 city 字段，有些在 state 字段）
- 作为 `反查城市名`

**错误处理**：如果 Nominatim API 调用失败或返回空结果，返回 WARN 并说明"校验服务不可用"，不阻断主流程。

### Step 3: 城市名匹配判定

将 `反查城市名` 与 `输入城市名` 进行模糊匹配：

**匹配规则**：
- 完全包含即通过：如输入"上海"，反查"上海市" → 包含关系 → PASS
- 反向包含也通过：如输入"上海市"，反查"上海" → 包含关系 → PASS
- 常见后缀忽略：去掉"市"、"省"、"区"、"县"后再比较

| 匹配情况 | 判定 | 说明 |
|----------|------|------|
| 城市名匹配 | ✅ PASS | 坐标与城市一致 |
| 城市名不匹配但同省/同国 | ⚠️ WARN | 坐标可能偏移，附近城市 |
| 城市名完全不相关 | ❌ FAIL | 坐标与城市严重不匹配 |

### Step 4: 返回结果

## Expected Output

```
校验结果: PASS / WARN / FAIL
输入城市: {城市名}
输入坐标: {lat}, {lon}
反查城市: {Nominatim 返回的城市名}
数据源: OpenStreetMap Nominatim（独立于坐标获取的 Open-Meteo）
说明: {判定说明}
```

## Notes

- **独立数据源**：坐标获取用 Open-Meteo（GeoNames 数据），校验用 Nominatim（OpenStreetMap 数据），两者独立，避免共因失效
- Nominatim 免费，无需 API Key，但要求设置 User-Agent header
- Nominatim 使用政策：请求频率不超过 1 次/秒（单次校验无需担心）
- 本 Skill 只做校验，不修改坐标或缓存
- 如果 Nominatim API 调用失败，返回 WARN 并说明原因，不阻断主流程
