# Claude Code 最佳实践 — 学习方案

> 基于 [claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) 仓库内容整理。
> 学习目标：从"会用 Claude Code"到"像 Claude Code 团队一样用 Claude Code"。

---

## 学习路线总览

```
Phase 1: 基础认知（Day 1-2）
    ↓
Phase 2: 核心三件套 — Memory / Commands / Skills（Day 3-5）
    ↓
Phase 3: 子代理与编排模式（Day 6-7）
    ↓
Phase 4: 工程化配置 — Settings / Hooks / MCP（Day 8-10）
    ↓
Phase 5: 高级工作流与日常实践（Day 11-14）
    ↓
Phase 6: 构建自己的工作流（持续迭代）
```

---

## Phase 1: 基础认知（Day 1-2）

> 目标：建立 Claude Code 的核心心智模型，理解 Prompt → Agent → Skill 的三层抽象。

### Day 1：安装与第一次对话

- [ ] **阅读** `tutorial/day0/README.md` — 安装与认证
- [ ] **阅读** `tutorial/day1/README.md` — 三层使用模型（Prompting → Agents → Skills）
- [ ] **实操** 在终端启动 `claude`，用自然语言做 2-3 个简单任务（问问题、读文件、改代码）
- [ ] **实操** 执行 `/powerup`，浏览全部 10 个交互教程，快速建立功能全景
  - 参考：`best-practice/claude-power-ups.md`

### Day 2：理解 Harness 思维

- [ ] **阅读** `reports/why-harness-is-important.md`（核心哲学文档）
  - 关键理解：Claude Code 不是 ChatGPT 套壳，harness 在模型之外做了大量系统级工作
  - "Prompt 控制模型被要求做什么。Harness 控制系统在模型无法触及的层面做什么。"
- [ ] **阅读** `reports/claude-agent-command-skill.md`（三种扩展机制对比）
  - 关键理解：Command（用户触发入口）、Agent（自主执行上下文隔离）、Skill（自动调用可复用模块）
- [ ] **阅读** Boris 的 13 条技巧：`tips/claude-boris-13-tips-03-jan-26.md`
  - 重点关注：#6 Plan 模式开始、#13 给 Claude 验证方式

**✅ Phase 1 检查点：** 能回答 "Command、Agent、Skill 各自在什么场景用？" 并能说出 harness 的 3 个不可替代能力。

---

## Phase 2: 核心三件套 — Memory / Commands / Skills（Day 3-5）

> 目标：掌握 Claude Code 最重要的三个配置维度——让 Claude 记住规则、执行工作流、获得能力。

### Day 3：Memory 系统（CLAUDE.md + Rules）

- [ ] **阅读** `best-practice/claude-memory.md`
  - 重点：祖先加载（向上）vs 后代懒加载（向下）机制
  - 重点：`CLAUDE.md`、`.claude/rules/*.md`、`~/.claude/CLAUDE.md` 的分工
- [ ] **阅读** `reports/claude-agent-memory.md`（代理持久记忆）
  - 三种作用域：`user`（跨项目个人）、`project`（团队共享）、`local`（个人项目）
- [ ] **实操** 在自己的项目中创建/优化 `CLAUDE.md`
  - 目标：< 200 行，包含项目概述、构建/测试命令、编码规范、常见错误
  - 创建 `.claude/rules/` 目录，用 `paths:` frontmatter 做条件加载
- [ ] **阅读** README 中 CLAUDE.md + .claude/rules 的 8 条 Tips

**💡 经验法则：** 任何开发者启动 Claude，说"run the tests"，如果第一次就能跑通——你的 CLAUDE.md 就到位了。

### Day 4：Commands（斜杠命令）

- [ ] **阅读** `best-practice/claude-commands.md`
  - 重点：frontmatter 字段（`name`、`description`、`context: fork`、`agent`）
  - 浏览 75 个官方内置命令，标记 10 个最常用的
- [ ] **实操** 查看本仓库的示例命令 `.claude/commands/weather-orchestrator.md`
- [ ] **实操** 为自己的高频工作流创建 1-2 个命令
  - 建议起步：`/commit`（规范化提交）或 `/review`（代码审查）
  - 放在 `.claude/commands/` 下，提交到 git

**💡 Boris 原则：** 如果你每天做某件事超过一次，就把它变成命令。

### Day 5：Skills（技能）

- [ ] **阅读** `best-practice/claude-skills.md`
  - 重点：Skill 是**文件夹**不是文件，可包含 `references/`、`scripts/`、`examples/`
  - 6 个官方捆绑技能：`simplify`、`batch`、`debug`、`loop`、`claude-api`、`fewer-permission-prompts`
- [ ] **阅读** Thariq 的 Skills 深度指南：`tips/claude-thariq-tips-17-mar-26.md`
  - 重点：9 种 Skill 类型分类、9 条编写最佳实践
  - 核心思维：description 是"触发条件"不是"摘要"，不要写 Claude 已经知道的东西
- [ ] **实操** 尝试使用 `/simplify` 和 `/batch` 官方技能
- [ ] **实操** 为自己的项目创建一个简单 Skill（如代码模板生成、特定 API 调用模式）

**✅ Phase 2 检查点：** 自己的项目已有：一个精心编写的 CLAUDE.md + 至少一条自定义 Command + 了解 Skill 的触发机制。

---

## Phase 3: 子代理与编排模式（Day 6-7）

> 目标：理解上下文隔离的核心价值，掌握 Command → Agent → Skill 编排模式。

### Day 6：子代理（Subagents）

- [ ] **阅读** `best-practice/claude-subagents.md`
  - 重点：16 个 frontmatter 字段，尤其是 `tools`、`model`、`skills`（预加载）、`isolation`（worktree）
  - 5 个官方内置代理：`general-purpose`、`Explore`（只读搜索用 Haiku）、`Plan` 等
- [ ] **阅读** README Tips 中 Agents 部分（4 条）
  - 核心：用子代理做上下文管理——"我需要这个工具输出本身，还是只需要结论？"
  - 子代理的 20 次文件读取 + 12 次 grep 只有最终报告返回主上下文
- [ ] **实操** 在 Claude 对话中说 "use subagents" 来处理一个多步骤任务
  - 观察主上下文的 token 消耗变化

### Day 7：编排工作流

- [ ] **阅读** `orchestration-workflow/orchestration-workflow.md`
  - 完整走通 Command → Agent (with preloaded Skill) → Skill 的三层编排
  - 理解两种技能模式：预加载（Agent Skill）vs 直接调用（Skill Tool）
- [ ] **实操** 运行 `/weather-orchestrator` 命令，亲身体验编排流程
- [ ] **思考** 自己的项目中有没有可以用这个模式的场景
  - 典型模式：一个入口命令编排用户交互 → 一个代理做数据获取/分析 → 一个技能做输出生成

**✅ Phase 3 检查点：** 能画出 Command → Agent → Skill 的数据流图，能解释预加载 Skill 和直接调用 Skill 的区别。

---

## Phase 4: 工程化配置 — Settings / Hooks / MCP（Day 8-10）

> 目标：将 Claude Code 从"能用"提升到"好用"——权限管理、自动化钩子、外部工具集成。

### Day 8：Settings 系统

- [ ] **阅读** `best-practice/claude-settings.md`
  - 重点章节：
    - 设置优先级层次（Managed > CLI > local > project > global）
    - 权限系统：`allow`/`ask`/`deny` + `auto` 模式
    - 工具权限语法：`Bash(npm run *)`、`Edit(src/**)`
    - 沙箱系统（Sandbox）
    - 模型配置（effort level、modelOverrides）
- [ ] **阅读** `best-practice/claude-cli-startup-flags.md`
  - 标记常用标志：`--continue`、`--resume`、`--model`、`--permission-mode`、`--print`
- [ ] **实操** 优化自己项目的 `.claude/settings.json`
  - 配置合理的权限白名单（减少反复确认的烦扰）
  - 设置 `statusLine` 显示上下文使用情况
  - 考虑启用 `auto` 模式：`Shift+Tab` 切换

### Day 9：Hooks 系统

- [ ] **阅读** README Tips 中 Hooks 部分（5 条）
  - PostToolUse Hook 自动格式化代码
  - Stop Hook 在每轮结束时验证工作
  - 按需 Hook（on-demand hooks）：`/careful` 阻止危险命令
- [ ] **浏览** [claude-code-hooks](https://github.com/shanraisshan/claude-code-hooks) 仓库了解实现模式
- [ ] **实操** 为自己的项目配置 1 个 Hook
  - 推荐起步：PostToolUse Hook 在每次文件编辑后自动运行 linter/formatter

### Day 10：MCP 服务器

- [ ] **阅读** `best-practice/claude-mcp.md`
  - 5 个推荐日常 MCP：Context7、Playwright、Chrome、DeepWiki、Excalidraw
  - 三种作用域：Project(`.mcp.json`) > User(`~/.claude.json`) > Subagent(frontmatter)
- [ ] **实操** 配置 1-2 个对自己最有用的 MCP
  - 建议优先级：**Context7**（获取最新库文档）> **Playwright**（浏览器调试）
- [ ] **实操** 在 Claude 对话中实际使用 MCP 工具，体验差异

**💡 MCP 黄金法则：** 不要贪多。装了 15 个最终只用 4 个——先从 1-2 个开始。

**✅ Phase 4 检查点：** 项目有合理的 `settings.json` 权限配置，至少配置了 1 个 Hook 和 1 个 MCP。

---

## Phase 5: 高级工作流与日常实践（Day 11-14）

> 目标：学习社区验证过的高级模式，形成自己的日常工作节奏。

### Day 11：会话管理与上下文控制

- [ ] **精读** Thariq 的会话管理指南：`tips/claude-thariq-tips-16-apr-26.md`
  - 核心决策表：Continue / Rewind / Compact / Clear / Subagent 五选一
  - 上下文腐蚀：新手保持 < 40%，老手 < 30%，只有简单任务才推到 60%
  - **Rewind > 纠正**：双击 Esc 回退比在上下文中留下失败尝试更好
  - `/compact` 带提示（如 `/compact focus on the auth refactor`）效果远好于让自动压缩触发
- [ ] **实操** 在一个实际开发任务中刻意练习：
  - 用 `/context` 观察上下文使用率
  - 在 30-40% 时主动 `/compact`
  - 走错路时用 `Esc-Esc` rewind 而不是在同一会话中纠正

### Day 12：Plan 模式与开发流程

- [ ] **阅读** Boris 10 条技巧：`tips/claude-boris-10-tips-01-feb-26.md`
  - 重点：#1 git worktrees 并行、#2 Plan 模式、#3 投资 CLAUDE.md、#5 直接说 fix
- [ ] **阅读** RPI 工作流：`development-workflows/rpi/rpi-workflow.md`
  - Research → Plan → Implement 每阶段有验证门控
- [ ] **阅读** 跨模型工作流：`development-workflows/cross-model-workflow/cross-model-workflow.md`
  - Claude 规划实施 + Codex 审查验证的互补模式
- [ ] **实操** 用 Plan 模式处理一个中等复杂度的任务
  - 流程：Plan 模式制定计划 → 审查计划 → 切换到执行模式实施

### Day 13：并行开发与 Agent Teams

- [ ] **阅读** `implementation/claude-agent-teams-implementation.md`
- [ ] **阅读** README Tips 中 Workflows Advanced 部分（9 条）
  - `/loop` 本地循环监控、`/schedule` 云端定时任务
  - `/permissions` 通配符语法替代 `dangerously-skip-permissions`
  - `/sandbox` 减少 84% 的权限弹窗
- [ ] **阅读** Boris 15 条隐藏功能：`tips/claude-boris-15-tips-30-mar-26.md`
- [ ] **了解** 以下高级模式（先了解概念，需要时再深入）：
  - Git Worktrees 并行开发
  - Ralph Wiggum 自进化循环
  - Scheduled Tasks / Routines
  - Ultrareview / Ultraplan

### Day 14：Git 工作流与代码审查

- [ ] **阅读** README Tips 中 Git/PR 部分（5 条）
  - Boris 每天 141 个 PR，中位数 118 行——保持 PR 小而聚焦
  - 始终 squash merge，保持线性历史
  - 至少每小时提交一次
- [ ] **阅读** Boris 6 条 Opus 4.7 技巧：`tips/claude-boris-6-tips-16-apr-26.md`
  - Auto 模式、/focus 模式、effort level 调节
- [ ] **实操** 用 Claude 完成一个完整的 Plan → Implement → Review → Commit 循环

**✅ Phase 5 检查点：** 能在真实项目中流畅使用 Plan 模式 → 执行 → 会话管理 → 提交的完整工作流。

---

## Phase 6: 构建自己的工作流（持续迭代）

> 目标：把学到的模式组合成适合自己项目的工作流，持续演进。

### 持续任务

- [ ] **浏览** README 中 Development Workflows 表格，研究 2-3 个感兴趣的社区工作流
  - 推荐优先看：[Superpowers](https://github.com/obra/superpowers)（175k ★）、[Matt Pocock Skills](https://github.com/mattpocock/skills)（51k ★）
- [ ] **浏览** Skill Collections 表格，从社区 Skill 库中挑选适合自己的
  - [anthropics/skills](https://github.com/anthropics/skills)（官方 127k ★）
- [ ] **订阅** 信息源保持更新：
  - Reddit: r/ClaudeCode
  - X: @bcherny（Boris）、@trq212（Thariq）
  - 每天更新 Claude Code：`npm update -g @anthropic-ai/claude-code`
  - 每天读 [CHANGELOG](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- [ ] **为自己的项目逐步构建：**
  - 一套 Commands 覆盖日常高频操作
  - 一组 Skills 封装项目特定的能力
  - 合理的 Agent 体系（如 research-agent、review-agent）
  - 投资"产品验证"类 Skill（如 signup-flow-driver、checkout-verifier）

---

## 快速参考：关键文件索引

| 主题 | 文件路径 | 优先级 |
|------|---------|--------|
| 项目总览 | `README.md` | ⭐⭐⭐ |
| 三种机制对比 | `reports/claude-agent-command-skill.md` | ⭐⭐⭐ |
| Harness 哲学 | `reports/why-harness-is-important.md` | ⭐⭐⭐ |
| Memory 系统 | `best-practice/claude-memory.md` | ⭐⭐⭐ |
| Commands | `best-practice/claude-commands.md` | ⭐⭐⭐ |
| Skills | `best-practice/claude-skills.md` | ⭐⭐⭐ |
| Subagents | `best-practice/claude-subagents.md` | ⭐⭐⭐ |
| Settings | `best-practice/claude-settings.md` | ⭐⭐ |
| MCP | `best-practice/claude-mcp.md` | ⭐⭐ |
| CLI 启动标志 | `best-practice/claude-cli-startup-flags.md` | ⭐⭐ |
| 编排工作流 | `orchestration-workflow/orchestration-workflow.md` | ⭐⭐⭐ |
| Agent Memory | `reports/claude-agent-memory.md` | ⭐⭐ |
| Boris 13 Tips | `tips/claude-boris-13-tips-03-jan-26.md` | ⭐⭐⭐ |
| Boris 10 Tips | `tips/claude-boris-10-tips-01-feb-26.md` | ⭐⭐⭐ |
| Thariq Skills | `tips/claude-thariq-tips-17-mar-26.md` | ⭐⭐⭐ |
| Thariq 会话管理 | `tips/claude-thariq-tips-16-apr-26.md` | ⭐⭐⭐ |
| RPI 工作流 | `development-workflows/rpi/rpi-workflow.md` | ⭐⭐ |
| 跨模型工作流 | `development-workflows/cross-model-workflow/cross-model-workflow.md` | ⭐ |
| Power-ups | `best-practice/claude-power-ups.md` | ⭐⭐ |

---

## 学习原则

1. **读一做二**：每读一篇文档，至少做两次实操。纸上得来终觉浅。
2. **渐进式投入**：不要一次性配置所有东西。先 CLAUDE.md，再 Commands，再 Skills，逐步叠加。
3. **记录犯错模式**：每次 Claude 犯错，更新 CLAUDE.md 或创建对应 Rule。复合工程的核心是"每个错误只犯一次"。
4. **保持上下文健康**：养成看 `/context` 的习惯，主动 compact，不要等到上下文腐蚀。
5. **新任务 = 新会话**：不要在一个越来越长的会话里做所有事情。

---

*Last updated: 2026-05-03*
