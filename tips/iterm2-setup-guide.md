# iTerm2 × Claude Code 实操配置指南

> 基于实际配置过程整理，所有步骤均已验证可用。
> 配合阅读：[iterm2-claude-code-best-practice.md](./iterm2-claude-code-best-practice.md)（理论与工作流参考）

---

## 前置条件

```bash
# 安装 iTerm2
brew install --cask iterm2

# 安装字体（Profile 配置依赖此字体，不装会 fallback 到系统默认）
brew install --cask font-jetbrains-mono
```

---

## 一、Dynamic Profiles —— 四角色 Profile 自动导入

iTerm2 支持 **Dynamic Profiles**：把 JSON 配置文件放到指定目录，自动热加载，无需手动在 GUI 里一个个创建。

### 配置文件

**路径**：`~/Library/Application Support/iTerm2/DynamicProfiles/claude-code-profiles.json`

```json
{
  "Profiles": [
    {
      "Name": "CC-AUDIT",
      "Guid": "CC-AUDIT-001",
      "Badge Text": "AUDIT",
      "Use Tab Color": true,
      "Tab Color": {
        "Red Component": 0.6588235294117647,
        "Green Component": 0.3333333333333333,
        "Blue Component": 0.9686274509803922
      },
      "Background Color": {
        "Red Component": 0.050980392156862744,
        "Green Component": 0.043137254901960784,
        "Blue Component": 0.09411764705882353
      },
      "Foreground Color": {
        "Red Component": 0.9176470588235294,
        "Green Component": 0.9176470588235294,
        "Blue Component": 0.9411764705882353
      },
      "Bold Color": { "Red Component": 1.0, "Green Component": 1.0, "Blue Component": 1.0 },
      "Cursor Color": {
        "Red Component": 0.9176470588235294,
        "Green Component": 0.9176470588235294,
        "Blue Component": 0.9411764705882353
      },
      "Cursor Text Color": { "Red Component": 0.0, "Green Component": 0.0, "Blue Component": 0.0 },
      "Selection Color": { "Red Component": 0.2, "Green Component": 0.2, "Blue Component": 0.3 },
      "Selected Text Color": { "Red Component": 1.0, "Green Component": 1.0, "Blue Component": 1.0 },
      "Normal Font": "JetBrainsMono-Regular 14",
      "Non Ascii Font": "JetBrainsMono-Regular 14"
    },
    {
      "Name": "CC-IMPL",
      "Guid": "CC-IMPL-002",
      "Badge Text": "IMPL",
      "Use Tab Color": true,
      "Tab Color": {
        "Red Component": 0.13333333333333333,
        "Green Component": 0.7725490196078432,
        "Blue Component": 0.3686274509803922
      },
      "Background Color": {
        "Red Component": 0.03137254901960784,
        "Green Component": 0.058823529411764705,
        "Blue Component": 0.043137254901960784
      },
      "Foreground Color": {
        "Red Component": 0.9176470588235294,
        "Green Component": 0.9176470588235294,
        "Blue Component": 0.9411764705882353
      },
      "Bold Color": { "Red Component": 1.0, "Green Component": 1.0, "Blue Component": 1.0 },
      "Cursor Color": {
        "Red Component": 0.9176470588235294,
        "Green Component": 0.9176470588235294,
        "Blue Component": 0.9411764705882353
      },
      "Cursor Text Color": { "Red Component": 0.0, "Green Component": 0.0, "Blue Component": 0.0 },
      "Selection Color": { "Red Component": 0.15, "Green Component": 0.25, "Blue Component": 0.18 },
      "Selected Text Color": { "Red Component": 1.0, "Green Component": 1.0, "Blue Component": 1.0 },
      "Normal Font": "JetBrainsMono-Regular 14",
      "Non Ascii Font": "JetBrainsMono-Regular 14"
    },
    {
      "Name": "CC-PROMPT",
      "Guid": "CC-PROMPT-003",
      "Badge Text": "PROMPT",
      "Use Tab Color": true,
      "Tab Color": {
        "Red Component": 0.023529411764705882,
        "Green Component": 0.7137254901960784,
        "Blue Component": 0.8313725490196079
      },
      "Background Color": {
        "Red Component": 0.03137254901960784,
        "Green Component": 0.054901960784313725,
        "Blue Component": 0.06274509803921569
      },
      "Foreground Color": {
        "Red Component": 0.9176470588235294,
        "Green Component": 0.9176470588235294,
        "Blue Component": 0.9411764705882353
      },
      "Bold Color": { "Red Component": 1.0, "Green Component": 1.0, "Blue Component": 1.0 },
      "Cursor Color": {
        "Red Component": 0.9176470588235294,
        "Green Component": 0.9176470588235294,
        "Blue Component": 0.9411764705882353
      },
      "Cursor Text Color": { "Red Component": 0.0, "Green Component": 0.0, "Blue Component": 0.0 },
      "Selection Color": { "Red Component": 0.15, "Green Component": 0.2, "Blue Component": 0.25 },
      "Selected Text Color": { "Red Component": 1.0, "Green Component": 1.0, "Blue Component": 1.0 },
      "Normal Font": "JetBrainsMono-Regular 14",
      "Non Ascii Font": "JetBrainsMono-Regular 14"
    },
    {
      "Name": "CC-PLAN",
      "Guid": "CC-PLAN-004",
      "Badge Text": "PLAN",
      "Use Tab Color": true,
      "Tab Color": {
        "Red Component": 0.9607843137254902,
        "Green Component": 0.6196078431372549,
        "Blue Component": 0.043137254901960784
      },
      "Background Color": {
        "Red Component": 0.050980392156862744,
        "Green Component": 0.043137254901960784,
        "Blue Component": 0.0
      },
      "Foreground Color": {
        "Red Component": 0.9176470588235294,
        "Green Component": 0.9176470588235294,
        "Blue Component": 0.9411764705882353
      },
      "Bold Color": { "Red Component": 1.0, "Green Component": 1.0, "Blue Component": 1.0 },
      "Cursor Color": {
        "Red Component": 0.9176470588235294,
        "Green Component": 0.9176470588235294,
        "Blue Component": 0.9411764705882353
      },
      "Cursor Text Color": { "Red Component": 0.0, "Green Component": 0.0, "Blue Component": 0.0 },
      "Selection Color": { "Red Component": 0.2, "Green Component": 0.18, "Blue Component": 0.1 },
      "Selected Text Color": { "Red Component": 1.0, "Green Component": 1.0, "Blue Component": 1.0 },
      "Normal Font": "JetBrainsMono-Regular 14",
      "Non Ascii Font": "JetBrainsMono-Regular 14"
    }
  ]
}
```

### 效果

文件写入后 iTerm2 **自动热加载**（不需重启），在 `Settings → Profiles` 可看到 4 个新 Profile：

| Profile | Badge | Tab 颜色 | 背景色 | 用途 |
|---------|-------|---------|--------|------|
| `CC-AUDIT` | AUDIT | 🟣 紫色 | 深紫黑 | 代码审查（只读） |
| `CC-IMPL` | IMPL | 🟢 绿色 | 深绿黑 | 代码实现 |
| `CC-PROMPT` | PROMPT | 🔵 青色 | 深青黑 | 提示工程 |
| `CC-PLAN` | PLAN | 🟡 橙色 | 深橙黑 | 架构规划 |

### 踩坑记录

- **必须配置前景色**（Foreground Color）。Dynamic Profiles 不会继承默认 Profile 的颜色，如果只设背景色不设前景色，会出现黑底黑字看不见的问题。
- 同理需要配齐：Bold Color、Cursor Color、Cursor Text Color、Selection Color、Selected Text Color。

---

## 二、Shell 配置 —— 角色别名与启动守卫

在 `~/.zshrc` 末尾追加以下配置。核心逻辑：

1. `cc()` 函数替代 alias（alias 无法做复杂逻辑）
2. **工作目录守卫**：在 `~` 目录时拦截启动，提示先 cd 到工程目录
3. **角色提示**：启动前打印当前角色信息，`sleep 1.5` 让用户看到（因为 `claude-internal` 是全屏 TUI，启动后会清屏覆盖）
4. **`case $ITERM_PROFILE`**：根据 iTerm2 Profile 自动匹配角色参数

### 配置内容

```bash
# ── Claude Code 角色别名（配合 iTerm2 Dynamic Profiles）──
cc() {
  if [[ "$PWD" == "$HOME" ]]; then
    echo "⚠️  当前在 ~ 目录，请先 cd 到工程目录再启动 Claude Code"
    echo "   例如: cd ~/ai_code/your-project"
    return 1
  fi
  # 角色提示
  [[ -n "$_CC_HINT" ]] && echo "$_CC_HINT" && sleep 1.5
  command /opt/homebrew/bin/claude-internal "${_CC_ARGS[@]}" "$@"
}

case "$ITERM_PROFILE" in
  CC-AUDIT)
    PROMPT="%F{magenta}[AUDIT]%f %~ %# "
    _CC_HINT=$'🟣 [AUDIT] 只读审查模式\n   进入后请执行: /model claude-opus-4  切换到 Opus\n   权限模式: plan（只读，不写文件）'
    _CC_ARGS=(--permission-mode plan)
    ;;
  CC-IMPL)
    PROMPT="%F{green}[IMPL]%f %~ %# "
    _CC_HINT=$'🟢 [IMPL] 代码实现模式\n   默认模型: Sonnet | 权限: acceptEdits'
    _CC_ARGS=(--permission-mode acceptEdits)
    ;;
  CC-PROMPT)
    PROMPT="%F{cyan}[PROMPT]%f %~ %# "
    _CC_HINT=$'🔵 [PROMPT] 提示工程模式\n   默认模型: Sonnet'
    _CC_ARGS=()
    ;;
  CC-PLAN)
    PROMPT="%F{yellow}[PLAN]%f %~ %# "
    _CC_HINT=$'🟡 [PLAN] 架构规划模式\n   默认模型: Sonnet'
    _CC_ARGS=()
    ;;
  *)
    _CC_HINT=""
    _CC_ARGS=()
    ;;
esac
```

### 快捷别名

同样在 `~/.zshrc` 的别名区域：

```bash
# iTerm2 四窗格 Claude Code 布局
alias cc4="bash ~/.claude/scripts/iterm2-4pane.sh"
```

### 踩坑记录

- **`claude-internal` 不支持 `--model` 参数**。模型切换必须在会话内用 `/model` 命令。所以 AUDIT 模式的提示里写了"进入后请执行 `/model claude-opus-4`"。
- **`--effort` 参数同样不支持**，已去掉。
- **alias 内无法先打印再执行**：alias 展开后直接交给 shell，无法在中间加逻辑。改为 `cc()` 函数解决。
- **全屏 TUI 会覆盖 echo 输出**：`claude-internal` 启动后清屏，之前打印的角色提示会消失。加 `sleep 1.5` 给用户留阅读时间。
- **非 iTerm2 环境下 `$ITERM_PROFILE` 为空**：在 CodeBuddy 内置终端、VS Code 终端等环境中，`$ITERM_PROFILE` 不存在，会走 `*)` 兜底分支。`cc` 命令仍可用，只是没有角色提示。

---

## 三、四窗格布局脚本

一键在 iTerm2 中创建四窗格布局，每个窗格自动使用对应角色 Profile。

### 配置文件

**路径**：`~/.claude/scripts/iterm2-4pane.sh`

```bash
#!/bin/bash
# ── iTerm2 四窗格 Claude Code 布局 ──
# 用法: bash ~/.claude/scripts/iterm2-4pane.sh [工程目录]
#
# ┌─────────────────┬──────────────────┐
# │  🟣 CC-AUDIT    │  🔵 CC-PROMPT    │
# │  只读审查        │  提示工程         │
# ├─────────────────┼──────────────────┤
# │  🟢 CC-IMPL     │  🟡 CC-PLAN      │
# │  代码实现        │  架构规划         │
# └─────────────────┴──────────────────┘

PROJECT_DIR="${1:-$(pwd)}"

osascript <<EOF
tell application "iTerm2"
    activate

    -- 创建新窗口，使用 CC-AUDIT Profile
    create window with profile "CC-AUDIT"

    tell current window
        tell current session

            -- 左上: CC-AUDIT (已经是了)
            write text "cd '$PROJECT_DIR' && clear"

            -- 右分割 → CC-PROMPT
            set promptSession to (split horizontally with profile "CC-PROMPT")
            tell promptSession
                write text "cd '$PROJECT_DIR' && clear"
            end tell

        end tell

        -- 回到左上 tab 的第一个 session，下分割 → CC-IMPL
        tell first session of current tab
            set implSession to (split vertically with profile "CC-IMPL")
            tell implSession
                write text "cd '$PROJECT_DIR' && clear"
            end tell
        end tell

        -- 回到右上 session(CC-PROMPT)，下分割 → CC-PLAN
        tell second session of current tab
            set planSession to (split vertically with profile "CC-PLAN")
            tell planSession
                write text "cd '$PROJECT_DIR' && clear"
            end tell
        end tell

    end tell
end tell
EOF

echo "✅ 四窗格布局已创建，工程目录: $PROJECT_DIR"
echo "💡 在 iTerm2 中执行 Window → Save Window Arrangement 可保存为默认布局"
```

### 用法

```bash
# 在当前目录创建四窗格
cc4

# 指定工程目录
cc4 ~/ai_code/my-project
```

### 注意事项

- 首次运行会弹 macOS 权限弹窗——"iTerm2 想要控制此应用"，点 **允许**
- 布局创建后可以 **Window → Save Window Arrangement** 保存
- **iTerm2 不支持锁定窗格大小**，鼠标拖到分隔线会调整。应对方式：
  - 误拖后**双击分隔线**恢复均分
  - 或改用多 Tab 模式（每角色一个 Tab，`⌘1`~`⌘4` 切换）

---

## 四、文件清单与快速部署

一键复现全部配置的文件列表：

| 文件 | 路径 | 作用 |
|------|------|------|
| Dynamic Profiles | `~/Library/Application Support/iTerm2/DynamicProfiles/claude-code-profiles.json` | 4 个角色 Profile（颜色、字体、Badge） |
| Shell 配置 | `~/.zshrc`（末尾追加） | `cc()` 函数、角色 case 分支、`cc4` 别名 |
| 布局脚本 | `~/.claude/scripts/iterm2-4pane.sh` | 一键四窗格 |
| 字体 | `brew install --cask font-jetbrains-mono` | JetBrains Mono 14pt |

### 快速部署步骤

```bash
# 1. 安装字体
brew install --cask font-jetbrains-mono

# 2. 写入 Dynamic Profiles（复制上面的 JSON 内容）
mkdir -p ~/Library/Application\ Support/iTerm2/DynamicProfiles
# 将 JSON 写入 claude-code-profiles.json

# 3. 写入布局脚本
mkdir -p ~/.claude/scripts
# 将脚本内容写入 iterm2-4pane.sh
chmod +x ~/.claude/scripts/iterm2-4pane.sh

# 4. 在 ~/.zshrc 末尾追加 Shell 配置（cc 函数 + case 分支）

# 5. 生效
source ~/.zshrc

# 6. 测试：在 iTerm2 中
cc4 ~/ai_code/your-project   # 一键四窗格
# 或 Profiles 菜单 → CC-IMPL → 输入 cc
```

---

## 五、已知限制

| 限制 | 说明 | 应对 |
|------|------|------|
| `--model` 不可用 | `claude-internal` 隐藏了该参数 | 启动后手动 `/model claude-opus-4` |
| `--effort` 不可用 | 同上 | 不影响使用，走默认值 |
| 窗格无法锁定大小 | iTerm2 不支持 | 双击分隔线恢复均分；或用多 Tab 模式 |
| 非 iTerm2 环境无角色 | `$ITERM_PROFILE` 为空 | `cc` 仍可用，走兜底分支 |
| 首次 AppleScript 需授权 | macOS 安全限制 | 弹窗点允许，仅一次 |
