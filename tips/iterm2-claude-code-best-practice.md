# iTerm2 × Claude Code macOS 最佳实践指引

> 从零配置到并行工作流，按操作顺序排列。

---

## 一、基础配置（必做，10 分钟）

### 1.1 安装 iTerm2

```bash
brew install --cask iterm2
```

### 1.2 Shift+Enter 换行

iTerm2 **无需额外配置**，开箱支持 Shift+Enter 多行输入。

> 备用方案：所有终端都可用 `Ctrl+J` 或输入 `\` 后按 Enter 换行。

### 1.3 Option 键设为 Meta（光标跳词必备）

> **iTerm2 → Settings → Profiles → Keys → General → Left Option Key** → 选 **Esc+**

不设这个的话，`Option+←/→` 跳词、`Option+Backspace` 删词都不能用。

### 1.4 终端通知（核心能力）

Claude 完成任务或需要你授权时，能弹系统通知告诉你。

#### 方法 A：iTerm2 原生通知

> iTerm2 → Settings → Profiles → Terminal → 勾选 **Notification Center Alerts** → 点 **Filter Alerts** → 启用 **Post notifications for escape-sequence-generated alerts**

#### 方法 B：增强版通知（推荐，支持点击跳转到对应 Tab）

```bash
git clone https://github.com/stevemeisner/claude-iterm-notify.git
cd claude-iterm-notify
./install.sh
```

安装后效果：

| 事件 | 通知内容 | 点击行为 |
|------|---------|---------|
| Claude 完成响应 | `项目名 — Ready for input` | 跳转到对应 iTerm2 Tab |
| Claude 需要权限 | `项目名 — Permission — xxx` | 跳转到对应 Tab |
| Claude 提问 | `项目名 — Question — xxx` | 跳转到对应 Tab |

> ⚠️ 首次触发通知时，去 **系统设置 → 通知 → terminal-notifier** 允许通知权限。

#### 方法 C：声音提示（最简方案）

```bash
claude config set --global preferredNotifChannel terminal_bell
```

或者用 Hook 自定义音效：

```json
// ~/.claude/settings.json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [{ "type": "command", "command": "afplay /System/Library/Sounds/Glass.aiff" }]
      }
    ]
  }
}
```

### 1.5 主题匹配

```
# 在 Claude Code 中运行
/theme
```

选一个和你 iTerm2 配色一致的主题（有 `auto` 选项自动检测深色/浅色）。

也可以自定义主题——在 `~/.claude/themes/` 下创建 JSON 文件：

```json
{
  "name": "MyDark",
  "base": "dark",
  "overrides": {
    "claude": "#bd93f9",
    "success": "#50fa7b",
    "error": "#ff5555"
  }
}
```

---

## 二、并行工作流（进阶，15 分钟）

这是 Boris Cherny 的核心实践——多个 Claude 并行跑，互不干扰。

### 2.1 方案选择

| 方案 | 复杂度 | 适合 |
|------|--------|------|
| **Tab 模式**（简单） | 低 | 2-3 个独立任务并行 |
| **4 窗格模式**（完整） | 中 | 有明确角色分工的团队工作流 |

### 2.2 Tab 模式（推荐入门）

最简单的并行方式——开多个 Tab，每个跑一个 Claude：

```
Tab 1 (⌘1): claude → "实现新功能"
Tab 2 (⌘2): claude → "写单元测试"
Tab 3 (⌘3): claude → "写文档"
```

**操作**：
- `⌘T` 新建 Tab
- `⌘1` ~ `⌘9` 快速切 Tab
- Tab 上的颜色圆点自动指示活动状态
- 配合通知，Claude 做完了会弹窗告诉你

### 2.3 四窗格模式（角色分工）

把一个 iTerm2 窗口分成 4 格，每格有固定角色：

```
┌─────────────────┬──────────────────┐
│  🟣 AUDIT       │  🔵 PROMPT       │
│  Opus · 只读审查 │  Sonnet · 提示工程│
├─────────────────┼──────────────────┤
│  🟢 IMPL        │  🟡 PLAN         │
│  Sonnet · 写代码 │  Sonnet · 架构讨论│
└─────────────────┴──────────────────┘
```

#### 步骤 1：创建 4 个 iTerm2 Profile

> iTerm2 → Settings → Profiles → 点 `+` 新建

| Profile 名 | 背景色 | Tab 颜色 | 角色 |
|---|---|---|---|
| `CC-AUDIT` | `#0d0b18` | 🟣 `#a855f7` | 代码审查（只读） |
| `CC-IMPL` | `#080f0b` | 🟢 `#22c55e` | 代码实现 |
| `CC-PROMPT` | `#080e10` | 🔵 `#06b6d4` | 提示工程 |
| `CC-PLAN` | `#0d0b00` | 🟡 `#f59e0b` | 架构规划 |

每个 Profile：
- **Colors** → 设背景色 + 勾 Use Tab Color
- **General** → Badge 填角色名（如 `AUDIT`）
- **Text** → 字体推荐 **JetBrains Mono 13pt**

#### 步骤 2：配置 Shell 别名

在 `~/.zshrc` 底部追加：

```bash
# ── Claude Code 角色别名 ──
case "$ITERM_PROFILE" in
  CC-AUDIT)
    PROMPT="%F{magenta}[AUDIT]%f %~ %# "
    alias cc='claude --model opus --effort high --permission-mode plan'
    ;;
  CC-IMPL)
    PROMPT="%F{green}[IMPL]%f %~ %# "
    alias cc='claude --model sonnet --effort high --permission-mode acceptEdits'
    ;;
  CC-PROMPT)
    PROMPT="%F{cyan}[PROMPT]%f %~ %# "
    alias cc='claude --model sonnet --effort medium'
    ;;
  CC-PLAN)
    PROMPT="%F{yellow}[PLAN]%f %~ %# "
    alias cc='claude --model sonnet --effort low'
    ;;
esac
```

`source ~/.zshrc` 生效后，每个窗格输入 `cc` 就自动以对应角色启动。

#### 步骤 3：创建窗口布局

1. 用 `CC-AUDIT` Profile 新开窗口
2. `⌘D` 右分割 → 右键 Tab 选 `CC-PROMPT` Profile
3. 点左窗格 → `⌘⇧D` 下分割 → 选 `CC-IMPL`
4. 点右上窗格 → `⌘⇧D` 下分割 → 选 `CC-PLAN`
5. **Window → Save Window Arrangement** 保存布局
6. **Settings → General → Startup** → 选 **Open Default Window Arrangement**（每次启动自动恢复）

#### 步骤 4：工作流

```
PLAN 窗格：讨论方案，不写文件
    ↓ 方案确定
IMPL 窗格：写代码，跑测试 → 测试通过
    ↓
AUDIT 窗格：/clear 后审查（只读模式，物理上无法写文件）
    ↓ 发现问题
IMPL 窗格：修改 → 重新提交审查
```

> 💡 **关键纪律**：AUDIT 窗格每次审查前先 `/clear`，确保读的是磁盘最新文件而不是上下文中的旧版本。

---

## 三、tmux 集成（可选，适合远程服务器）

如果你在 tmux 里用 Claude Code：

```bash
# ~/.tmux.conf
set -g allow-passthrough on        # 通知透传
set -s extended-keys on             # Shift+Enter 支持
set -as terminal-features 'xterm*:extkeys'
```

```bash
tmux source-file ~/.tmux.conf
```

---

## 四、实用快捷键速查

| 快捷键 | 功能 | 场景 |
|--------|------|------|
| `⌘T` | 新建 Tab | 开新的 Claude 会话 |
| `⌘1`~`⌘9` | 切换到第 N 个 Tab | 多 Tab 并行时快速切换 |
| `⌘D` | 水平分割 | 创建窗格布局 |
| `⌘⇧D` | 垂直分割 | 创建窗格布局 |
| `⌘⌥ ←/→/↑/↓` | 切换窗格 | 4 窗格模式下跳转 |
| `⌘⇧↵` | 缩放/还原当前窗格 | 临时全屏某个窗格 |
| `Shift+Tab` (×2) | 切换到 Plan 模式 | Claude Code 内 |
| `Esc` | 中断 Claude 生成 | 发现方向不对时 |

---

## 五、防坑指南

| 坑 | 原因 | 解决 |
|---|---|---|
| 多个 Claude 改同一个文件冲突 | 并行会话无锁机制 | 按角色分工，AUDIT 只读；或用 `git worktree` 给每个 Claude 独立目录 |
| Token/请求限流 | 并行 = 倍数消耗 | Pro 计划足够 3 并行，Max 支持 5+ |
| 上下文膨胀 | 长会话积累太多上下文 | 定期 `/compact`（压缩保留摘要）或 `/clear`（清空） |
| 通知不弹 | macOS 通知权限没开 | 系统设置 → 通知 → terminal-notifier → 允许 |
| Opus 费用高 | AUDIT 窗格用 Opus | Opus 仅在代码审查时使用，不做生成；日常 3 个窗格用 Sonnet 足够 |

---

## 六、推荐的渐进式采用路径

```
阶段 1（今天就能做）：
  ✅ 配好通知（方法 B）
  ✅ 配好 Option 键
  ✅ 匹配主题

阶段 2（明天试试）：
  ✅ 开 2-3 个 Tab 并行跑独立任务
  ✅ 体验 ⌘1~⌘3 + 通知 的工作节奏

阶段 3（熟练后）：
  ✅ 搭建 4 窗格角色分工布局
  ✅ IMPL + AUDIT 分离的审查流程
```

---

## 参考资料

- [Claude Code 官方终端配置文档](https://code.claude.com/docs/zh-CN/terminal-config)
- [4-Pane Claude Code Setup for iTerm2](https://pravindurgani.github.io/claude-code-multipane-iterm2/)
- [Claude Code iTerm2 Notifications](https://github.com/stevemeisner/claude-iterm-notify)
- [Boris Cherny 的 13 条 Claude Code 技巧](https://x.com/bcherny/status/1875192552164094076)
