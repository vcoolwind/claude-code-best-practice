# proj_docs — 项目需求文档中心

## 目录结构

```
proj_docs/
├── README.md                  ← 你正在看的文件
├── <需求名>/
│   ├── 1-requirements.md      ← 需求描述（PRD/用户故事/原始需求）
│   ├── 2-plan.md              ← 规划文档（活文档，impl 过程中持续更新）
│   └── 3-audit.md             ← Code Review / 审计报告
└── _archived/                 ← 已完结的需求归档
    └── <需求名>/
```

## 使用约定

### 创建新需求

```bash
mkdir proj_docs/<需求名>
touch proj_docs/<需求名>/1-requirements.md
```

命名规范：**纯语义**，使用小写英文 + 连字符（如 `user-login`、`data-pipeline-v2`）。

### 角色分工

| 角色 | 输入 | 工作区 | 职责 |
|------|------|--------|------|
| **Planner** | `1-requirements.md` | `proj_docs/<需求>/` | 需求分析、技术方案设计、任务拆解 → 输出 `2-plan.md` |
| **Implementer** | `2-plan.md` | `src/`（项目代码目录） | 编码实现，方案决策变更**回写 `2-plan.md`** |
| **Auditor** | `2-plan.md` + `src/` | `proj_docs/<需求>/` | Code Review、质量检查 → 输出 `3-audit.md` |

### Plan 是活文档

- Plan 不是写完就不动的——impl 过程中发现方案需要调整，**直接更新 `2-plan.md`**
- 记录决策变更的原因（"为什么从方案 A 改为方案 B"）
- 这样 audit 阶段可以追溯完整的决策链路

### 文件扩展

复杂需求可按编号扩展，无需创建子目录：

```
proj_docs/complex-feature/
├── 1-requirements.md
├── 2-plan.md
├── 2.1-api-design.md          ← plan 的补充文档
├── 2.2-data-model.md          ← plan 的补充文档
└── 3-audit.md
```

### 生命周期

```
创建需求目录 → plan 完成 → impl 开始（持续回写 plan）→ audit review → 归档
```

需求完成后：
```bash
mv proj_docs/<需求名> proj_docs/_archived/
```

## iTerm2 多窗格协作

三个 Claude 实例并行工作：

| 窗格 | 角色 | 启动命令 |
|------|------|---------|
| 左 | Planner | `claude --prompt "你是 Planner 角色，专注 proj_docs/<需求>/"` |
| 中 | Implementer | `claude --prompt "你是 Implementer，参考 proj_docs/<需求>/2-plan.md 进行实现"` |
| 右 | Auditor | `claude --prompt "你是 Auditor，review src/ 代码并输出到 proj_docs/<需求>/3-audit.md"` |

## TODO

- [ ] 定义 plan 模板（目标、范围、技术方案、任务拆解、风险点）
- [ ] 定义 audit 模板（review 范围、发现问题、改进建议、通过标准）
- [ ] 完善 iTerm2 启动脚本（类似 cc4 一键三窗格）
- [ ] **实现 Claude Commands（高优先级）**：
  - [ ] `/new-feature` — 输入需求名，自动创建目录 + 各阶段文件模板（1-requirements.md / 2-plan.md / 3-audit.md）
  - [ ] `/plan` — Planner 角色：读取 1-requirements.md，输出技术方案到 2-plan.md
  - [ ] `/impl` — Implementer 角色：读取 2-plan.md，逐项实现代码，决策变更回写 plan
  - [ ] `/audit` — Auditor 角色：读取 2-plan.md + src 代码，输出 review 报告到 3-audit.md
