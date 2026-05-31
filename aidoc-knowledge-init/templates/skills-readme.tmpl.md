# 领域能力目录

本目录存放可复用的领域能力（Skills）。每个 skill 是一个独立目录，包含：

```
skill-name/
├── SKILL.md          # 必需：skill 定义（YAML frontmatter + 工作流）
├── scripts/          # 可选：辅助脚本
└── references/       # 可选：参考资料
```

## 什么是 Skill？

Skill 是一段封装好的操作流程，AI 编码助手可按需加载执行。它不像 AGENTS.md 那样始终存在于上下文中，而是当用户请求匹配其描述时触发。

## 当前 Skills

| Skill 名称 | 描述 | 状态 |
|-----------|------|------|
{{SKILLS_LIST}}

## 何时将能力封装为 Skill？

- 操作需要多个步骤（如"部署到测试环境"）
- 流程依赖特定脚本或配置文件
- 希望跨会话复用同一操作模式
<!-- HUMAN_REVIEW: 请补充你希望封装为 skill 的常见操作 -->
