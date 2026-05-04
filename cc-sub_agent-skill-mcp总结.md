# Claude Code 运行机制详解：主 Agent → Sub-Agent → Skill → MCP

---

## 整体架构：分层委托系统

```
┌──────────────────────────────────────────────────────────────────┐
│                        用户输入                                    │
│            "查上海天气"  /  "/weather"  /  "重构代码"              │
└───────────────────────────────┬──────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     主 Agent（Main Agent）                         │
│  • 就是你对话的 Claude Code 本体                                   │
│  • 读取 CLAUDE.md + Rules + 所有 Agent 的 description              │
│  • 决定自己做还是委托给 sub-agent                                  │
└───────────────┬──────────────────┬───────────────────────────────┘
                │                  │
     自己处理    │                  │ 委托
                ▼                  ▼
┌──────────────────┐    ┌──────────────────────────────────────────┐
│  直接执行         │    │            Sub-Agent（子代理）              │
│  Read/Write/Bash │    │  • 隔离的 context fork                    │
│  ...             │    │  • 有自己的 allowedTools 白名单             │
│                  │    │  • 可预加载 Skills                         │
│                  │    │  • 可绑定 MCP 服务器                       │
│                  │    │  • 有 maxTurns 限制                       │
└──────────────────┘    └───────────────┬──────────────────────────┘
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                   ┌──────────┐  ┌──────────┐  ┌──────────────┐
                   │  Skill   │  │  Skill   │  │  MCP Tool    │
                   │(知识注入) │  │(工具调用) │  │ (外部连接)    │
                   └──────────┘  └──────────┘  └──────────────┘
```

---

## 一、主 Agent（Main Agent）

**本质**：就是你正在对话的 Claude Code 本体。

**职责**：
1. 接收用户输入
2. 读取所有 `.claude/agents/*.md` 的 `description` 字段，建立路由表
3. **决策**：自己做 or 委托给某个 sub-agent
4. 拥有完整的工具集（Read、Write、Bash、Agent、Skill、MCP...）

**路由规则**（优先级从高到低）：

| 优先级 | 条件 | 动作 |
|--------|------|------|
| 1 | description 含 `PROACTIVELY` 且匹配 | **必须**委托，不能自己做 |
| 2 | 有匹配的普通 agent | 优先委托 |
| 3 | 没有匹配 agent | 自己执行或调用 Skill |

**实际例子**：

`universal-weather-agent.md` 的 description 写了：
> "PROACTIVELY use this agent whenever the user asks about the weather"

所以主 Agent 看到"查上海天气"时，**不应该自己处理**，而是调用：
```
Agent(subagent_type="universal-weather-agent", prompt="查上海天气")
```

---

## 二、Agent（Sub-Agent / 子代理）

**本质**：在隔离的 context fork 中运行的专用 Claude 实例。

**关键特征**：

| 特征 | 说明 |
|------|------|
| **隔离上下文** | 子代理有独立的对话历史，不污染主 Agent 的 context window |
| **工具白名单** | `allowedTools` 限制子代理能用什么工具 |
| **轮数限制** | `maxTurns` 防止无限循环 |
| **模型选择** | 可以用更便宜的模型（如 `haiku`）做简单任务 |
| **权限模式** | `permissionMode: acceptEdits` 可免确认写文件 |

**Frontmatter 字段（共16个）**：

| 字段 | 作用 |
|------|------|
| `name` | 唯一标识符（小写字母+连字符） |
| `description` | 何时调用。含 `"PROACTIVELY"` 表示自动触发 |
| `allowedTools` | 允许使用的工具白名单 |
| `disallowedTools` | 禁止使用的工具 |
| `model` | 使用的模型：`haiku`/`sonnet`/`opus`/`inherit` |
| `permissionMode` | 权限模式：`default`/`acceptEdits`/`auto`/`bypassPermissions`/`plan` |
| `maxTurns` | 最大执行轮数 |
| `skills` | 预加载的 Skill 列表（注入上下文） |
| `mcpServers` | 作用域限定的 MCP 服务器 |
| `hooks` | 生命周期钩子（PreToolUse/PostToolUse/Stop 等） |
| `memory` | 持久记忆范围：`user`/`project`/`local` |
| `background` | 是否作为后台任务运行 |
| `effort` | 努力级别：`low`/`medium`/`high`/`xhigh`/`max` |
| `isolation` | 设为 `"worktree"` 可在临时 git worktree 中运行 |
| `initialPrompt` | 作为主会话代理时的初始提示 |
| `color` | CLI 输出颜色 |

**生命周期**：

```
主 Agent 调用 Agent(...)
  → Claude Code 创建新的 context fork
  → 注入 agent.md 的正文作为 system prompt
  → 预加载 skills: 中列出的 Skill 内容
  → 子代理开始执行（受 allowedTools + maxTurns 约束）
  → 执行完毕，结果返回给主 Agent
  → context fork 销毁
```

**调用语法**：
```
Agent(subagent_type="agent-name", description="...", prompt="...", model="haiku")
```

> 注意：`Agent` 工具在 v2.1.63 从 `Task` 重命名而来，`Task(...)` 仍可作为别名使用。

**关键规则**：
- Subagent **不能**通过 bash 命令调用其他 subagent
- 必须使用 `Agent` 工具进行委托
- 每个 subagent 运行在隔离的 context fork 中

**官方内置 Agent（5个）**：

| Agent | 模型 | 用途 |
|-------|------|------|
| `general-purpose` | inherit | 复杂多步骤任务（默认） |
| `Explore` | haiku | 快速代码搜索（只读） |
| `Plan` | inherit | 规划模式研究（只读） |
| `statusline-setup` | sonnet | 配置状态栏 |
| `claude-code-guide` | haiku | 回答 Claude Code 功能问题 |

---

## 三、Skill（技能）

**本质**：一段**结构化的指令文本**，告诉 Agent "怎么做某件事"。

**两种使用模式**：

| 模式 | 机制 | 触发方式 | 类比 |
|------|------|----------|------|
| **预加载** | 启动时注入 Agent 上下文 | agent 的 `skills:` 字段 | 相当于"背景知识" |
| **工具调用** | 运行时通过 `Skill(...)` 调用 | Agent 主动调用 | 相当于"查手册执行" |

**关键区别**：

```
预加载（注入上下文）：
┌─────────────────────────────┐
│  Agent 启动时                │
│  system prompt = agent.md   │
│  + city-coordinates/SKILL.md │  ← 直接拼进去
│  + weather-query/SKILL.md    │  ← 直接拼进去
└─────────────────────────────┘

工具调用：
Agent 运行中 → 决定需要某个 Skill
→ 调用 Skill(skill: "weather-query")
→ Skill 的 allowed-tools 临时生效
→ 按 Skill 指令执行
→ 返回结果
```

**Skill 的 `allowed-tools` 字段（权限升级）**：

```yaml
# weather-query/SKILL.md
allowed-tools:
  - "WebFetch(*)"    # ← 只有通过这个 Skill 才能用 WebFetch
```

这实现了**权限升级**：子代理本身没有 `WebFetch`，但通过 Skill 调用时可以临时获得。类似于 Linux 的 `sudo` 概念。

**Skill 不是代码，是指令**：Skill 本身不执行任何东西，它只是告诉 Agent "第一步做什么、第二步做什么、用什么 URL、怎么解析响应"。执行者仍然是 Agent 自己。

**Frontmatter 字段（共15个）**：

| 字段 | 作用 |
|------|------|
| `name` | 显示名和 `/slash-command` 标识符 |
| `description` | 技能功能描述（用于自动发现） |
| `when_to_use` | 触发短语和示例请求 |
| `argument-hint` | 自动补全提示 |
| `arguments` | 命名位置参数 |
| `disable-model-invocation` | 设为 `true` 防止自动调用 |
| `user-invocable` | 设为 `false` 隐藏于 `/` 菜单 |
| `allowed-tools` | 技能活跃时允许的工具 |
| `model` | 运行时使用的模型 |
| `effort` | 努力级别覆盖 |
| `context` | 设为 `fork` 在隔离子代理中运行 |
| `agent` | `context: fork` 时的子代理类型 |
| `hooks` | 作用域限定的生命周期钩子 |
| `paths` | Glob 模式限制自动激活范围 |
| `shell` | Shell 类型（bash/powershell） |

**官方内置 Skill（6个）**：

| Skill | 用途 |
|-------|------|
| `simplify` | 审查代码质量并重构 |
| `batch` | 批量运行命令 |
| `debug` | 调试失败的命令 |
| `loop` | 循环执行提示 |
| `claude-api` | 构建 Claude API 应用 |
| `fewer-permission-prompts` | 减少权限提示 |

---

## 四、MCP（Model Context Protocol）

**本质**：标准化的外部工具连接协议，让 Claude Code 能调用任意外部服务。

**与其他概念的关系**：

```
MCP 提供"能力"（工具）
Agent/Skill 决定"用不用"和"怎么用"

类比：
- MCP = USB 接口（标准化连接）
- MCP Server = U 盘/打印机/摄像头（各种外设）
- MCP Tool = 读文件/打印/拍照（具体操作）
```

**运行机制**：

```
Claude Code 启动
  → 读取 .mcp.json / ~/.claude.json
  → 启动配置的 MCP Server 进程（或连接远程 URL）
  → 注册所有 MCP Tools 到可用工具列表
  → Agent 可以像用内置工具一样用 MCP 工具
```

**工具命名约定**：`mcp__<server-name>__<tool-name>`

```json
// .mcp.json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp"]
    }
  }
}
```
→ 注册为 `mcp__context7__query-docs` 等工具

**服务器类型**：

| 类型 | 传输 | 示例 |
|------|------|------|
| **stdio** | 启动本地进程 | `npx`, `python`, binary |
| **http** | 连接远程 URL | HTTP/SSE endpoint |

**作用域控制**：

| 层级 | 配置位置 | 可见范围 |
|------|----------|---------|
| User | `~/.claude.json` | 所有项目 |
| Project | `.mcp.json` | 当前项目所有 Agent |
| Agent | frontmatter 的 `mcpServers` 字段 | 仅该子代理 |

**优先级**：Agent > Project > User

**权限规则**：

MCP 工具遵循 `mcp__<server>__<tool>` 命名约定：
```json
{
  "permissions": {
    "allow": ["mcp__context7__*"],
    "deny": ["mcp__dangerous-server__*"]
  }
}
```

**推荐的 MCP 服务器**：

| 服务器 | 功能 |
|--------|------|
| **Context7** | 获取最新库文档，防止 API 幻觉 |
| **Playwright** | 浏览器自动化测试 |
| **Claude in Chrome** | 连接真实 Chrome 进行调试 |
| **DeepWiki** | 获取 GitHub 仓库结构化文档 |
| **Excalidraw** | 生成架构图 |

---

## 五、Hooks（生命周期钩子）

**本质**：在特定事件发生时自动执行的外部脚本。

**作用点**：

```
Agent 决定调用某个工具
  ↓
┌─────────────┐
│ PreToolUse  │ ← 工具调用前触发（可以做：语音提示、参数校验、日志）
└─────────────┘
  ↓
  工具实际执行
  ↓
┌─────────────┐
│ PostToolUse │ ← 工具调用后触发（可以做：结果播报、审计、通知）
└─────────────┘
  ↓
Agent 准备结束
  ↓
┌─────────────┐
│ Stop        │ ← Agent 停止时触发（可以做：总结、清理）
└─────────────┘
```

**示例（天气 agent 语音播报）**：
```yaml
hooks:
  PreToolUse:
    - matcher: "Skill|Read|Write"
      hooks:
        - type: command
          command: python3 weather-voice.py --event=pre
          timeout: 3000
          async: true
```

---

## 六、完整调用链（以"查上海天气"为例）

```
用户: "查上海天气"
  │
  ▼
主 Agent: 扫描所有 agent description
  │       → 发现 universal-weather-agent 含 "PROACTIVELY" + "weather"
  │       → 必须委托
  ▼
Agent(subagent_type="universal-weather-agent", prompt="查上海天气")
  │
  ▼
Sub-Agent 启动:
  │  context = agent.md正文 + city-coordinates/SKILL.md + weather-query/SKILL.md
  │  allowedTools = [Read, Write, Skill]
  │  model = haiku
  │
  │  Step 1: 解析 "上海"
  │  Step 2: 调用 Skill(skill:"city-coordinates")
  │           │
  │           ├─ [PreToolUse hook] → weather-voice.py --event=pre → 🔊播报
  │           │
  │           ├─ Skill 临时获得 Read + Write + WebFetch 权限
  │           ├─ Read coord-cache.json → 缓存命中？
  │           │   ├─ 是 → 返回坐标
  │           │   └─ 否 → WebFetch geocoding API → Write 缓存 → 返回坐标
  │           │
  │           └─ [PostToolUse hook] → weather-voice.py --event=post → 🔊播报
  │
  │  Step 3: 调用 Skill(skill:"weather-query")
  │           │
  │           ├─ [PreToolUse hook] → 🔊播报
  │           ├─ Skill 临时获得 WebFetch 权限
  │           ├─ WebFetch open-meteo API → 解析温度+天气码 → 返回结果
  │           └─ [PostToolUse hook] → 🔊播报
  │
  │  Step 4: Write → history.md 追加记录
  │  Step 5: 返回格式化结果
  │
  ▼
主 Agent: 收到结果，展示给用户
```

---

## 七、Agent Teams（多代理团队）

与 subagent 不同，Agent Teams 启动**多个独立的 Claude Code 会话**，通过共享任务列表协调。

**对比**：

| 维度 | Sub-Agent | Agent Teams |
|------|-----------|-------------|
| 运行方式 | 一个会话内的 context fork | 多个独立会话 |
| 上下文 | 共享主 Agent 的部分上下文 | 各有完整独立的上下文 |
| 通信 | 通过返回值 | 通过共享任务列表/文件 |
| 适用场景 | 单一任务委托 | 复杂多角色协作 |

---

## Sub-Agent 与 Skill 的关系与区别

### 核心区别：一个是"人"，一个是"手册"

| 维度 | Sub-Agent | Skill |
|------|-----------|-------|
| **本质** | 一个独立运行的 Claude 实例 | 一段结构化的指令文本 |
| **类比** | 雇了一个专人去做事 | 给人一本操作手册 |
| **有无上下文** | ✅ 有独立的对话历史和推理能力 | ❌ 没有，只是被注入或被读取的文本 |
| **谁在执行** | Sub-Agent 自己 | 调用 Skill 的那个 Agent |
| **隔离性** | 完全隔离（context fork） | 不隔离，在调用者的上下文中执行 |
| **成本** | 高（独立模型推理） | 低（只是额外 prompt 文本） |
| **适合做什么** | 多步骤、需要判断和决策的任务 | 明确的、步骤固定的操作流程 |

### 组合关系

```
Sub-Agent 可以"持有" Skill（通过 skills: 字段预加载）
Sub-Agent 可以"调用" Skill（通过 Skill(...) 工具）
Skill 不能调用 Sub-Agent
Skill 不能调用其他 Skill
```

**为什么 Skill 不能调用其他 Skill？**

因为 Skill 不是执行体，它只是一段 markdown 指令。真正执行的是 Agent。
Skill 的 `allowed-tools` 只能声明基础工具（Read/Write/WebFetch/Bash 等），
`Skill` 工具本身不在 Skill 可声明的 allowed-tools 范围内。

多 Skill 的编排顺序（先查坐标 → 再查天气）由 Agent 的 system prompt 决定，
Skill 可以在文本中"建议"下一步，但无法强制触发另一个 Skill。

### 选择策略：什么时候用 Agent，什么时候用 Skill？

| 场景 | 选择 | 理由 |
|------|------|------|
| 查询天气（固定 API + 固定解析） | Skill | 步骤固定，不需要决策 |
| 代码审查（需要理解上下文、给建议） | Agent | 需要推理和判断 |
| 格式化输出（固定模板） | Skill | 纯模板填充 |
| 多轮对话收集需求 | Agent | 需要交互和状态维护 |
| 调用外部 API 并缓存结果 | Skill | 流程固定，Agent 执行 Skill 指令即可 |
| 协调多个 Skill 的执行顺序 | Agent | 需要编排和错误处理 |

### 实际案例对照

```
universal-weather-agent（Agent）
├── 职责：解析城市名、决定调用顺序、处理错误、记录历史
├── 预加载 city-coordinates（Skill）→ "如何获取坐标"的手册
└── 预加载 weather-query（Skill）→ "如何查天气"的手册

Agent 读了两本手册，然后自己判断：
  先查坐标 → 再查天气 → 缓存没命中怎么办 → API 挂了怎么办
这些决策是 Agent 做的，不是 Skill 做的。
```

### 一句话总结

> **Agent 是有脑子的执行者，Skill 是没脑子的说明书。Agent 决定"做不做"和"怎么组合"，Skill 告诉 Agent "具体怎么做某一步"。**

---

## 八、关键设计原则总结

| 原则 | 说明 | 实现手段 |
|------|------|---------|
| **最小权限** | 子代理只拥有完成任务所需的工具 | `allowedTools` 白名单 |
| **隔离性** | 子代理的上下文不影响主 Agent | context fork |
| **成本控制** | 简单任务用便宜模型 | `model: haiku` |
| **可组合** | Skill 可被任意 Agent 复用 | 独立文件 + 标准接口 |
| **可观测** | Hooks 提供生命周期可见性 | PreToolUse/PostToolUse/Stop |
| **权限升级** | Skill 可临时授予 Agent 没有的工具 | Skill 的 `allowed-tools` |
| **强制委托** | PROACTIVELY 确保不被跳过 | description 关键词 |

---

## 九、核心思想

这套体系的核心思想：**用声明式配置（YAML frontmatter）替代命令式编排**，让 Claude Code 自己根据 description 路由请求、根据 allowedTools 限制能力边界、根据 Skill 获取领域知识。

这实现了"从 Vibe Coding 到 Agentic Engineering"的渐进式工程化转变。
