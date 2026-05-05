---
paths:
  - "**/*.md"
---

# Markdown Docs

## Documentation Standards

- Keep files focused and concise — one topic per file
- Use relative links between docs (e.g., `../best-practice/claude-memory.md`), not absolute GitHub URLs
- Include back-navigation link at top of best-practice and report docs (see existing files for pattern)
- When adding a new concept or report, update the corresponding table in README.md (CONCEPTS or REPORTS)

## 文档叙事结构：What → Why → How

写知识性/实践性文档时，按以下顺序组织：

1. **What（是什么）**：先把事情定义清楚——它是什么、边界在哪
2. **Why（为什么）**：为什么要这样做，解决什么问题，不这样做会怎样
3. **How（怎么做）**：具体的落地方案、操作步骤、配置示例

不要上来就讲操作步骤（How），读者不知道为什么要做这件事时，步骤再详细也没用。

## Structure Conventions

- Best practice docs go in `best-practice/`
- Implementation docs go in `implementation/`
- Reports go in `reports/`
- Tips go in `tips/`
- Changelog tracking goes in `changelog/<category>/`

## Formatting

- Use tables for structured comparisons (see README CONCEPTS table as reference)
- Use badge images from `!/tags/` for visual consistency when linking best-practice or implementation docs
- Keep headings hierarchical — don't skip levels (e.g., don't jump from `##` to `####`)
