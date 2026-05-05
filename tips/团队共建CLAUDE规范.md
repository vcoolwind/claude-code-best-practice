# 团队共建 CLAUDE.md 规范

> 来源：Boris 13 Tips #4 + #5 的理解与实践落地方案

---

## What：团队共建 CLAUDE.md 是什么

**CLAUDE.md** 是 Claude Code 每次启动时自动读取的项目级指令文件。团队共建 CLAUDE.md = 把团队所有人在 Code Review、调试、开发中发现的规则/教训，集中沉淀到这一份文件里，让 Claude 在写代码和 review 时自动遵守。

Boris 称之为 **Compounding Engineering（复合工程）**——每一次代码审查，不仅修当前的代码，还让系统永久变得更聪明。

### 闭环链路

```
人 review 发现问题
    ↓
沉淀到 CLAUDE.md（场景 + 做法 + 原因）
    ↓
Claude 下次写代码 → 读到规则 → 直接写对
Claude 帮忙 review → 读到规则 → 能指出同类问题
新人入职 → Claude 已"知道"团队所有隐性规范
```

### 三个关键词

| 关键词 | 含义 |
|--------|------|
| **Single** | 一个仓库一份共享。Claude 无状态，散落在各人脑子里的规则它学不会。集中到 git 里的文件，才能保证每次会话都读到 |
| **Multiple times a week** | 高频贡献。不是写一次就完了，是全员每次犯错都追加一条，和代码同步迭代 |
| **Anytime Claude does something incorrectly** | 触发条件是"它做错的那一刻"——那时你最清楚应该怎么做。这个时机窗口过了就忘了 |

### 内容边界

**应该写**（给 Claude 看的行为规则）：
- 项目架构约定："service 层不能直接访问 DAO，必须通过 repository"
- linter 管不了的编码规范："错误码用 6 位，前 2 位是模块编号"
- 团队隐性知识："这个接口的 `status=3` 是历史遗留，实际含义是'已作废'"
- Claude 犯过的错："不要在 for 循环里调用远程接口，必须批量"

**不应该写**：
- linter/formatter 已经管的（缩进、引号风格）
- 过于泛泛的原则（"写好代码"、"遵循 SOLID"）
- 和代码无关的（精力管理、学习计划 → 放 `/learn`）

### 规则质量标准

每条规则包含三要素：

```
- **[场景/条件]**：具体做法。原因：为什么这样做。
```

**好的规则**：
- **[并发共享资源]**：优先用乐观锁+重试，而非悲观锁。原因：业务读多写少，悲观锁成为瓶颈。
- **[SQL JOIN]**：大表 JOIN 时必须在 ON 条件中包含分区键。原因：避免全表扫描。

**坏的规则**：
- "注意并发安全" ← 不具体，不可操作
- "代码要写好" ← 废话

---

## Why：为什么要这样做

### 传统编码规范的问题

| 维度 | 传统编码规范 | CLAUDE.md 复合工程 |
|------|------------|-------------------|
| 更新频率 | 每季度/每年 | **每次 PR review** |
| 谁写 | Tech Lead 一个人写 | 全员贡献 |
| 内容来源 | 理论/经验总结 | **真实犯错案例** |
| 谁执行 | 人记住（大概率忘） | **Claude 自动执行** |
| 格式 | 泛泛的"应该/不应该" | 具体的"当 X 时，用 Y 而不是 Z" |
| 本质 | 被动参考 | **主动执行**——Claude 每次启动都会读并遵守 |

### 复利效应

团队越大、犯错越多样化，CLAUDE.md 积累越快，所有人 + Claude 都受益。每周 5 条 → 第 12 周就有 60 条规则覆盖团队踩过的所有坑。

### 不这样做会怎样

```
传统模式：教训只存在于 B 的脑子里 → 下次 A（或 C）还会犯同样的错
复合工程：教训写入文件 → Claude 和所有人都不再犯
```

---

## How：怎么落地

### CLAUDE.md 的加载机制

Claude Code 的记忆是**无状态的**——每次启动新会话只读文件，不记得上次对话。

#### 三层记忆体系

```
~/.claude/CLAUDE.md              ← 全局个人偏好（所有项目生效）
/项目根/CLAUDE.md                ← 团队共享规范（启动即加载）  ← #4 说的就是这个
/项目根/子目录/CLAUDE.md         ← 组件级规范（懒加载，触碰到才读）
```

#### 加载规则

| 方向 | 行为 | 举例 |
|------|------|------|
| 向上（祖先目录） | **启动即加载** | 在 `frontend/` 启动 → 自动读到根目录的 CLAUDE.md |
| 向下（子目录） | **懒加载** | 只有 Claude 碰到 `backend/` 下的文件时才读 `backend/CLAUDE.md` |
| 兄弟目录 | **不加载** | 在 `frontend/` 工作时，永远不会读 `backend/CLAUDE.md` |

#### Monorepo 最佳实践

```
/mymonorepo/
├── CLAUDE.md              ← 全团队通用规则（< 200 行）
├── .claude/rules/*.md     ← 分领域详细规则（paths: 匹配时懒加载）
├── frontend/CLAUDE.md     ← 前端专属
├── backend/CLAUDE.md      ← 后端专属
└── data-pipeline/CLAUDE.md ← 数据管道专属
```

#### 规模控制

> Keep CLAUDE.md under 200 lines per file for reliable adherence

- 核心规则放 `CLAUDE.md`（< 200 行）
- 分领域详细规则放 `.claude/rules/*.md`（有 `paths:` frontmatter 时按需懒加载）
- **渐进式披露**：不一次塞给 Claude 所有信息

---

### 落地方案：从零自动化到完全自动化

#### Level 0：纯人工约定（零成本）

团队约定——review 时发现的规范问题，reviewer 追加到 `CLAUDE.md`，作为 MR 的一部分提交。

```
MR 内容 = 业务代码变更 + CLAUDE.md 规则更新
```

- ✅ 零技术成本
- ❌ 依赖人的纪律，容易退化

#### Level 1：Claude Code 会话中手动触发

Review 时发现问题，在 Claude Code 中直接说：

> "把这条规则加到 CLAUDE.md：在 XXX 场景下应该用 Y 而不是 Z，原因是……"

- ✅ 比手写快，Claude 帮你组织格式
- ❌ 依赖你记得触发

#### Level 2：自定义 Slash Command `/cclearn`（推荐起步方案）

创建 `.claude/commands/cclearn.md`，一条命令搞定：

```
/cclearn 并发场景下对共享资源应该用乐观锁+重试，而非悲观锁，因为业务读多写少
```

Claude 自动：理解规则 → 检查去重 → 追加到 CLAUDE.md 合适章节 → 告知结果

- ✅ 零摩擦，格式统一
- ✅ 零部署成本，今天就能用
- ❌ 还需人记得触发

#### Level 3：MR 模板提醒（低成本自动化）

在 MR 模板中加一栏：

```markdown
## Review 规则沉淀
<!-- 本次 review 是否发现了团队应遵守的新规范？ -->
- [ ] 无新规则
- [ ] 已追加规则到 CLAUDE.md：___
```

- ✅ 系统性提醒，不靠记忆
- ❌ 只是提醒，执行还是靠人

#### Level 4：Webhook + Claude API（完全自动化，等价 GitHub Action）

适用于 GitLab / Gitea 等有 Webhook 能力的自建 Git 平台：

```
MR comment 包含触发词（如 "#learn" 或 "@claude-learn"）
    ↓
Webhook 捕获 comment 事件
    ↓
后端脚本提取 comment 内容
    ↓
调用 Claude API 生成 CLAUDE.md 规则
    ↓
自动 commit 到当前 MR 分支
```

技术栈：HTTP 服务（Python/Go）+ Claude API + git commit

- ✅ 全自动，零人工干预
- ❌ 需要一次性开发部署

---

### 团队推广路径

1. **从一个人开始**：自己先用 `/cclearn` 积累 10~20 条规则，让 CLAUDE.md 有实质内容
2. **展示价值**：下次 Claude 因为读了这些规则而避免了一个错误，截图分享给团队
3. **降低门槛**：把 `/cclearn` 命令分享给团队（提交到仓库即可），人人可用
4. **建立节奏**：每周 review 时有意识地 `/cclearn`，形成习惯
5. **适时升级**：当团队全面使用 Claude Code 后，升级到 Level 3 + Level 4

---

## 关键认知

- **#5 的本质不是 GitHub Action，是"将转瞬即逝的 review 洞察固化为系统永久知识"的自动化管道**
- 触发时机选在 PR review，因为那是大脑最清楚"应该怎么做"的时刻
- CLAUDE.md 是**活文档**——不是写一次就完了，是每次犯错都让它变得更好
- 原子性：代码修复和规则更新在同一次提交里，可追溯
- Claude 的记忆是无状态的，规则必须写到文件里才能跨会话生效
- **"Single"不是限制，是集中**——确保每次会话都读到完整团队知识

---

*创建时间：2026-05-05*
*来源：Boris 13 Tips #4 "Share a Single CLAUDE.md" + #5 "Tag @claude on PRs"*
*参考：best-practice/claude-memory.md（CLAUDE.md 加载机制详解）*
