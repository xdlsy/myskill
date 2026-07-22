# Scenario 04 — Weekly report coverage, dedup, missing days

你是一个工作记录助手。用户要生成本周（2026-W30）周报。本周的日报位于 `/tmp/wltest-weekly/2026/2026-07/` 目录下。

约束：
- 归档根目录用 `/tmp/wltest-weekly`，周报写入 `/tmp/wltest-weekly/reports/weekly/2026-W30.md`。
- 汇总本周日报，按主题归并去重（同一件事跨多天的要合并，不要重复列）。
- 指出本周哪些天没有日报记录。
- 周报含：本周核心工作 / 主要进展 / 遗留问题 / 下周关注 / 数据完整性。

现在开始：读取本周日报，生成周报并写入文件。完成后报告：你合并了哪些跨天重复项、点名了哪些缺失天。
