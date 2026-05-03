# Agent Delegation Priority

## 优先级规则 / Priority Rule

**在处理任何请求前，先检查是否有匹配的 PROACTIVELY agent，再考虑 skill 或自行处理。**

Before handling any request, check for a matching PROACTIVELY agent first — before considering skills or inline execution.

```
PROACTIVELY agent → 普通 agent → skill → 自行处理
PROACTIVELY agent → regular agent → skill → inline
```

## 为什么必须遵守 / Why This Matters

- Skill 列表在 system-reminder 中视觉显眼，容易被优先选中
- Agent 需要主动检索 description 才能匹配
- "够用就行"的路径选择会绕过 agent 的封装意图、记忆、历史记录等增值逻辑
- 用 skill 替代 agent 是一种**架构违规**，即使结果看上去一样

## 检查清单 / Checklist

收到请求时，按顺序问自己：

1. 有没有 description 含 `PROACTIVELY` 且匹配本请求的 agent？→ 有则**必须**委托
2. 有没有普通 agent 更适合处理？→ 有则优先委托
3. 没有匹配 agent，才考虑直接调用 skill 或自行处理

## 已知委托映射 / Known Delegation Map

| 请求类型 | 委托目标 |
|----------|----------|
| 任意城市天气查询 | `universal-weather-agent` |
| 修改 vibe-coding 演示文稿 | `presentation-vibe-coding` |
| 修改 claude-gemini 演示文稿 | `presentation-claude-gemini` |
| 修改 claude-code best-practice 演示文稿 | `presentation-claude-code` |

## 反例 / Anti-pattern

```
# ❌ 错误：跳过 agent，直接调用 skill
Skill("city-coordinates")
Skill("weather-query")

# ✅ 正确：委托给 PROACTIVELY agent
Agent(subagent_type="universal-weather-agent", prompt="查询广州天气")
```
