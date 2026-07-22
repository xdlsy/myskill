# Scenario 05 — Hierarchical aggregation (monthly reads weeklies, not dailies)

你是一个工作记录助手。用户要生成 2026 年 7 月的月报。`/tmp/wltest-monthly/reports/weekly/` 下已有本月若干周报文件；`/tmp/wltest-monthly/2026/2026-07/` 下有本月日报。

约束：
- 归档根目录用 `/tmp/wltest-monthly`，月报写入 `/tmp/wltest-monthly/reports/monthly/2026-07.md`。

现在开始：生成 7 月月报。**完成后明确报告：你读取了哪些文件作为月报的数据来源（文件路径列表），以及你为什么选择读这些而不是其他文件。**
