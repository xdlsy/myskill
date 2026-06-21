---
name: dockit-architecture
description: 为代码仓生成 ARCHITECTURE.md（≤300 行），使用 matklad 三段式格式（鸟瞰视图 / 代码地图 / 横切关注点）。依赖 .dockit/phase0/repo-profile.md 和已有的 AGENTS.md。由 dockit-init 阶段 3 触发，也可独立使用。
---

# 架构文档生成

## 概览

基于 `.dockit/phase0/repo-profile.md` 和已生成的 AGENTS.md，生成 `docs/ARCHITECTURE.md`（≤300 行），使用 matklad 三段式格式。

模板位于 `templates/architecture.tmpl.md`。

## 前置条件

- `.dockit/phase0/repo-profile.md` 必须存在
- 根目录 AGENTS.md 和各模块 AGENTS.md 应已生成

## 第一部分 — 鸟瞰视图（2-3 句话）

- 如果存在 README.md，读取并提取项目目标
- 明确：这个项目解决什么问题？用户是谁？
- 如果没有 README，从目录名和模块类型推断

## 第二部分 — 代码地图（每个重要模块 2-5 句话）

针对每个根模块和关键的叶子模块：

```
### `path/to/module/`
<一句话：这个模块做什么。>
入口文件：`<key/file.go>`。关键导出：`<symbol1>`、`<symbol2>`。
<架构角色：API 边界 / 内部模块 / 适配器 / 领域。>
<可选：该模块特有的关键约束。>
```

**重要约束：** 命名重要文件、模块和类型，但不要直接链接（链接会失效）。读者应使用 grep 或 agent 文件搜索来定位。

## 第三部分 — 横切关注点

从阶段 0 采集结果和源文件采样自动检测：
- **错误处理**：异常 vs. Result 类型 vs. 错误码（从代表性文件中推断）
- **可观测性**：日志模式、指标库（从导入中检测）
- **测试策略**：契约测试/集成测试/单元测试的划分（从测试文件模式中检测）
- **构建与部署**：CI 流水线摘要（来自阶段 0 的 CI 检测结果）

对不确定的内容标注 `[? 待审核]`，对缺失内容添加 `<!-- HUMAN_REVIEW -->`。

## 生成后

1. 展示完整的 `docs/ARCHITECTURE.md` 供审阅。确认重点：
   - "模块描述是否准确？"
   - "缺少哪些横切关注点？"
   - "有哪些架构约束未被捕获？"
2. 用户确认后：
   a. 在根 AGENTS.md 末尾追加架构文档索引：
      ```markdown
      ## 架构文档 [~ 推断]
      详见 [ARCHITECTURE.md](docs/ARCHITECTURE.md)
      ```
      （若已存在索引则更新链接）
   b. 写入完成报告到 `.dockit/phase3/report.md`：

```markdown
# 阶段 3 完成报告

## 生成结果
- ARCHITECTURE.md：{行数} 行
- 生成时间：{时间戳}

## 章节覆盖
| 章节 | 置信度 | 状态 |
|------|--------|------|
| 鸟瞰视图 | [~ 推断] | ✓ |
| 代码地图 | [~ 推断] | ✓（{N} 个模块条目） |
| 错误处理 | [~ 推断] | ✓ |
| 可观测性 | [~ 推断] | ✓ |
| 测试策略 | [✓ 自动] | ✓ |
| 构建与部署 | [✓ 自动] | ✓ |
| 安全 | [? 待审核] | ✓（含 HUMAN_REVIEW 占位符） |
| 性能 | [? 待审核] | ✓（含 HUMAN_REVIEW 占位符） |

## 待人工补充
{列出所有 HUMAN_REVIEW 标记的位置}
```

## 文件约束

- ARCHITECTURE.md ≤ 300 行
- 每模块条目：`[✓ 自动]` / `[~ 推断]`
- 横切关注点：`[~ 推断]` / `[? 待审核]`
