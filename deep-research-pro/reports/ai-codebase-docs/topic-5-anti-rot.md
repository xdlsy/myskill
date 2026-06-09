# 主题 5 深挖：AI agent 项目文档防腐化策略

> 上下文工程 / Auto Memory / 剪枝 / 失效检测
> 父研究：`/Users/lsy/clawd/research/ai-codebase-docs/report.md` 主题 5（约 310-350 行）
> 调研日期：2026-04-26

---

## 0. TL;DR（工程师视角）

防腐的核心是把"加载"与"信任"分开：CLAUDE.md 只放 agent 推不出来的事实（每会话 < 200 行），
程序性知识下沉到 skills（按需加载），偶发学习走 auto memory（agent 自写、人工周审），失效信号用 `InstructionsLoaded` hook + 转录回放主动捕获，而不是等 agent 出错才发现规则已死。

---

## 1. Just-in-time retrieval：从原则到命令级落地

### 1.1 Anthropic 上下文工程文章的原话

> "Rather than preloading data, agents keep lightweight identifiers (file paths, stored queries, web links, etc.) and fetch data dynamically at runtime via tools."
> "Claude Code uses a hybrid: CLAUDE.md dropped in upfront + glob/grep primitives for navigating filesystem just-in-time."
> 这能 "sidestep stale indexing and complex syntax trees"。

来源：[Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 1.2 Claude Code 里的具体使用模式

| 模式 | 反模式（preload） | 推荐（JIT） |
|---|---|---|
| 找接口实现 | 把整个 `src/api/` 塞进 CLAUDE.md | `Grep(pattern="export.*Handler", path="src/api/")` 按需 |
| 大数据库分析 | `cat dump.sql` 进上下文 | 写 SQL 查询 → 落 CSV → `head/tail` 查看 |
| 多文件改造 | 一次 Read 30 个文件 | 派 subagent，subagent 在自己窗口里 Read → 回 1-2k 字摘要 |
| 文档参考 | 把 README/ADR 全 import 到 CLAUDE.md | 只在 CLAUDE.md 写 `See @docs/adr/` 路径，agent 需要时自查 |
| 接口约定 | 把 200 行 API 规范写进 CLAUDE.md | 拆 `.claude/skills/api-conventions/SKILL.md`，描述触发，按需加载 |

### 1.3 落到命令的最小集合

```
Grep   → 找符号 / 用法 / 旧 API 调用点
Glob   → 找文件路径（命名约定即提示，文件名比目录树更便宜）
Read   → 仅在路径已确定后调用；尽量 offset/limit
Bash   → head / tail / wc / git log -- file 取元信息（大小、时间、作者）
```

文章里的"渐进披露"信号：
- 文件大小（复杂度）、命名约定（用途）、时间戳（相关性）、目录层级（角色：`tests/test_utils.py` 与 `src/core/test_utils.py` 是两个东西）。

### 1.4 vs 预加载的"经验对比数据"

Anthropic 没有发布单一 benchmark 数字，但文档里明确两条机制性结论：
1. **n² attention**：n token 形成 n² 配对关系，注意力被稀释 → "context rot"。
2. **训练分布**：长序列在训练数据里少，位置编码插值带来 "some degradation in token position understanding"。

公开的间接证据（来源：awesome-claude-code 收录的工程师工具）：
- `claude-code-tools` (pchalasani) 把"避免 compaction"作为目标，理由是压缩后 nested CLAUDE.md 不会自动重新注入。
- `claude-rules-doctor` (nulone) 报告：renamed 目录 / typo glob 会导致 "silent rule failure"——规则在 disk 上看似存在，但永远不被加载。

---

## 2. Auto memory 机制详解（v2.1.59+）

### 2.1 存储位置（实测路径）

```
~/.claude/projects/<project>/memory/
├── MEMORY.md          ← 索引；每会话首 200 行 / 25KB 自动加载
├── debugging.md       ← 主题文件，按需读
├── api-conventions.md
└── ...
```

`<project>` 由 git 仓库根决定，所以同一仓库下的所有 worktree / 子目录共享同一份 auto memory。非 git 项目用项目根路径。

来源：[How Claude remembers your project](https://code.claude.com/docs/en/memory)

### 2.2 写入触发与决策

文档原文：
> "Claude doesn't save something every session. It decides what's worth remembering based on whether the information would be useful in a future conversation."

显式触发：用户说 "remember that X" / "always use pnpm not npm" → 直接写 auto memory（不是 CLAUDE.md）。

隐式触发（agent 自决）的典型类型：
- Build / test 命令（你纠正过一次的）
- 调试方法论（"先 run docker compose down -v 才能重置 fixtures"）
- 风格偏好（"prefer arrow functions"）
- 项目历史 / 架构注释

### 2.3 与 CLAUDE.md 的边界（官方对照表）

|  | CLAUDE.md | Auto memory |
|---|---|---|
| 谁写 | 人 | Agent |
| 内容 | Instructions / rules | Learnings / patterns |
| 作用域 | project / user / org | per working tree（机器本地） |
| 加载量 | 完整加载 | MEMORY.md 首 200 行 / 25KB |
| 用途 | 编码规范、工作流、架构 | 构建命令、调试洞见、agent 自学的偏好 |
| 团队共享 | 是（git） | 否（机器本地，不上传） |

关键差异：
- CLAUDE.md 完整加载，超过 200 行 adherence 下降；MEMORY.md 是**截断加载**——超出部分要靠 agent 用 file tool 主动读。
- Auto memory 是 *per working tree*，所以同事不会读到你的；同一项目跨机器也不同步。

### 2.4 关 / 开 / 改路径

```jsonc
// .claude/settings.json
{ "autoMemoryEnabled": false }
// 或 ENV
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
// 改路径（仅 user/local/policy 设置接受，不接受 project，防止恶意重定向）
{ "autoMemoryDirectory": "~/my-mem" }
```

`/memory` 命令：列出当前 session 加载的所有 CLAUDE.md / .local.md / rules，并给一个打开 auto memory 文件夹的链接。

---

## 3. 失效信号的检测方法

### 3.1 唯一原生 hook：`InstructionsLoaded`

来源：[Hooks reference](https://code.claude.com/docs/en/hooks)

事件载荷：
```json
{
  "session_id": "...",
  "hook_event_name": "InstructionsLoaded",
  "file_path": "/path/CLAUDE.md",
  "memory_type": "Project",     // User | Project | Local | Managed
  "load_reason": "session_start", // | nested_traversal | path_glob_match | include | compact
  "globs": ["src/api/**/*.ts"], // 仅 path_glob_match
  "trigger_file_path": "...",   // lazy 触发文件
  "parent_file_path": "..."     // include 链
}
```

**重要限制**：hook 不阻塞、不能改变加载内容；只用于审计。它告诉你"哪条规则进了上下文"，不告诉你"agent 是否照做"。

### 3.2 一个最小可用的审计日志（拷贝即用）

```jsonc
// .claude/settings.json
{
  "hooks": {
    "InstructionsLoaded": [{
      "hooks": [{
        "type": "command",
        "command": "jq -c '{ts:now,file:.file_path,type:.memory_type,reason:.load_reason}' >> ~/.claude/instruction-audit.log"
      }]
    }]
  }
}
```

跑一周后用 `jq` 聚合，可以回答：
- 哪些 CLAUDE.md 文件从未在 `path_glob_match` 触发过 → 候选剪枝
- 哪些 nested CLAUDE.md 从未 `nested_traversal` → 死目录或人没在那边干活
- compact 之后哪些规则没被重新注入 → 容易"漂移"的规则

### 3.3 "规则被忽略"检测的工程化做法（无原生支持）

文档明确没有 native hook 检测 follow vs ignore。社区方案：

1. **Stop hook + agent 评审**（开销大但准）：
   ```jsonc
   { "hooks": { "Stop": [{ "hooks": [{
     "type": "agent",
     "prompt": "Review the transcript at $ARGUMENTS. Did Claude violate any rules from the loaded CLAUDE.md? Return decision:block with reason if so.",
     "timeout": 60
   }]}]}}
   ```
2. **PostToolUse + 静态规则**：把可机检的规则（"必须先 typecheck"、"不准动 migrations/"）下沉到 hook，hook 比 prompt 更可靠（文档原话："Hooks are deterministic"）。
3. **第三方工具**：
   - `agnix`（agent-sh）— CLAUDE.md / AGENTS.md / SKILL.md / hooks / MCP 全栈 lint
   - `claude-rules-doctor`（nulone）— 检测 `.claude/rules/*.md` 的 paths glob 是否还匹配真实文件
   - `claudekit` — 6-aspect code reviewer + oracle 二次评估

### 3.4 经验法则：rules 失效的三个间接信号

| 信号 | 含义 |
|---|---|
| 用户在同一会话内**两次以上**纠正同一行为 | 规则要么没写，要么写得太弱 / 太长被忽略 |
| `/memory` 列出某 rule 文件，但近 2 周 audit log 里 0 次加载 | 路径作用域写错了 |
| compaction 之后 agent 又开始犯之前纠正过的错 | 规则只在 conversation 里出现过，没进 CLAUDE.md |

---

## 4. `/memory` 周审计 SOP

### 4.1 审计 Checklist（建议每周 30 分钟）

> 跑 `/memory` 列文件 → 翻 `~/.claude/instruction-audit.log` → 按下表过一遍

| # | 检查项 | 操作 |
|---|---|---|
| 1 | CLAUDE.md 是否 > 200 行？ | 拆成 path-scoped rule 或 skill |
| 2 | 是否有相互矛盾的规则（多个 CLAUDE.md / rules）？ | 留更具体的，删另一个 |
| 3 | 是否有"agent 不写也能做对"的规则？ | 删（best-practices 原话："If Claude already does without it, delete"） |
| 4 | 是否有"应该是 hook 而不是 prompt"的规则？（必做且可机检） | 转 hook，CLAUDE.md 留一句指针 |
| 5 | audit log 里 0 次命中的 rule 文件 | path glob 改对，或删 |
| 6 | auto memory MEMORY.md 是否超 200 行？ | 把详情 split 到主题文件，MEMORY.md 只留索引 |
| 7 | auto memory 里是否有该升进 CLAUDE.md 的事实？（团队都该知道） | 升 CLAUDE.md，原 entry 删 |
| 8 | auto memory 里是否有过期的"调试历史"？ | 删（per-bug 历史不是知识） |
| 9 | CLAUDE.md / rules 引用的文件路径是否还存在？ | 跑 `claude-rules-doctor` 或简单 grep |
| 10 | ADR / 长说明是否被抄进了 CLAUDE.md？ | 改成 `@docs/adr/...` 引用 |
| 11 | "IMPORTANT/YOU MUST" 是否泛滥？ | 强调超过 5 条 = 没强调；保留最关键 2-3 条 |
| 12 | 是否有 nested CLAUDE.md 在已废弃目录里？ | 直接删 |
| 13 | 团队成员有没有人改了 CLAUDE.md 没说？ | git log + diff |
| 14 | CLAUDE.local.md 里有没有该上升团队级的事实？ | 升 CLAUDE.md |
| 15 | 是否还需要某 skill / rule 的存在？（看用户最近 1 个月 prompt） | 不再需要的归档 |

### 4.2 决策树：剪枝 / 改写 / 合并

```
看一条规则 →
├─ agent 没它也做对  →  删
├─ agent 偶尔忘     →
│   ├─ 内容是事实  →  留 CLAUDE.md，加"YOU MUST"
│   └─ 内容是流程  →  下沉 skill（按需），CLAUDE.md 留一句"对 X 用 /skill"
├─ agent 经常违反   →
│   ├─ 可机检       →  转 hook（PreToolUse / PostToolUse）
│   └─ 不可机检     →  改写得更具体（带例子、反例）
└─ 多个规则讲同一事 → 合并到最具体那一处
```

---

## 5. 上下文窗口压力的实证数据

### 5.1 官方明确说的硬约束

- CLAUDE.md：建议 < 200 行；超过会"consume more context and reduce adherence"。无 benchmark 数字，但文档把"bloated CLAUDE.md causes Claude to ignore your actual instructions"列为常见失败模式之一。
- MEMORY.md：硬截断 200 行 / 25KB，超出不在会话开始时加载。
- Skill description 总预算：context window 的 1%（fallback 8000 字符），单条 description+when_to_use 1536 字符封顶。
- Skill 内容 compaction 预算：每条 skill 重新注入首 5000 token，全部 skills 共享 25000 token；溢出时**最旧的 skill 整条丢弃**。

来源：[memory.md](https://code.claude.com/docs/en/memory)、[skills.md](https://code.claude.com/docs/en/skills)、[best-practices](https://code.claude.com/docs/en/best-practices)

### 5.2 间接的"曲线"信号

公开的项目分享里没有"行数 vs adherence"标定数据，但有方向性证据：
- best-practices 文档把"too long → rules get lost in noise"反复出现 4 次。
- awesome-claude-code 推荐的 `pre-commit-hooks` (aRustyDev) 被表扬为 "thorough but not verbose, doesn't shout in all-caps"——反衬出社区里 ALL-CAPS 长 CLAUDE.md 是常见反模式。
- `Context Engineering Kit` (LeoVS09) 把"minimal token footprint"作为卖点。

工程实践建议：
- 用 InstructionsLoaded hook 落 token 数，自己画一条"项目 CLAUDE.md 行数 vs 用户每周纠正次数"的曲线。
- 200 行不是宪法，是 schelling point；真正的指标是"用户纠正频率是否上升"。

---

## 6. 失败模式表（含早期信号 / 根因 / 对策）

### 6.1 Anthropic 官方 5 模式

| 失败模式 | 早期信号 | 根因 | 对策 |
|---|---|---|---|
| **Kitchen sink session** | 用户切话题 ≥ 2 次仍同一会话 | 上下文混入无关信息，相互污染 | 不同任务必 `/clear`；用 `/btw` 处理一次性问答 |
| **Correcting over and over** | 同一缺陷纠正 ≥ 2 次 | 失败尝试堆积，agent 在历史里看到错误样本 | 第二次纠错后立即 `/clear`，重写一个含"刚学到的事"的 prompt |
| **Over-specified CLAUDE.md** | 用户在 chat 重复 CLAUDE.md 已写过的事；agent 问已答过的问 | 长 CLAUDE.md 重要规则被噪音淹没 | 周审计删冗余；可机检的转 hook |
| **Trust-then-verify gap** | "看起来对"的实现，PR review 才发现边界没处理 | 没给 agent 验证手段 | 强制提供 tests / screenshots / lint；agent 自我验证 |
| **Infinite exploration** | "investigate" 类无范围 prompt 让 agent 读上百文件 | 范围不明 + 主上下文承担探索成本 | 用 subagent 做调研；prompt 里限定文件 / 步骤数 |

### 6.2 社区补充模式

| 失败模式 | 早期信号 | 根因 | 对策 |
|---|---|---|---|
| **Silent dead rule** | rule 文件还在 git，但 audit log 永不命中 | path glob 写错（typo / 改名 / 重构） | `claude-rules-doctor`；CI 跑 InstructionsLoaded 命中率检查 |
| **Compaction-induced amnesia** | compact 后又犯之前纠正过的错 | 规则只在 chat，没进 CLAUDE.md；nested CLAUDE.md 不会自动重注入 | 核心规则上 CLAUDE.md 项目根；用 `SessionStart(matcher:"compact")` 重注入关键上下文 |
| **Memory leak（auto memory 膨胀）** | MEMORY.md 超 200 行，老条目开始失效 | agent 一直追加，没人剪枝 | 周审计 SOP 第 6/7/8 项 |
| **Conflicting CLAUDE.md（monorepo）** | 跨子目录行为不一致 | 多团队各写各的 CLAUDE.md | 用 `claudeMdExcludes` 排除别人的；或合并到 path-scoped rule |
| **All-caps fatigue** | "IMPORTANT/YOU MUST" 满篇还是不听 | 强调通胀 → 等于没强调 | 每个 CLAUDE.md 至多 2-3 条 caps；其余删除或转 hook |
| **AGENTS.md / CLAUDE.md drift** | 两个文件说法不一致 | Claude Code 不读 AGENTS.md，团队改了一边漏了另一边 | CLAUDE.md 第一行 `@AGENTS.md` 单一信源 |
| **Skill 触发不到** | `/skill-name` 工作，但 agent 自己从不调用 | description 关键词与用户 prompt 不匹配 | 在 description 里前置 "Use when ..." 触发短语 |
| **Skill 内容失活** | 调用过的 skill 在长会话里似乎"被忘" | compaction 把旧 skill 内容驱逐（25000 token 预算溢出） | 关键 skill 后期重新 `/skill-name` 一次刷新 |
| **Going rogue / 无限循环** | 长跑任务无人监督时持续消耗 API | 无终止条件、无 circuit breaker | 参考 `Ralph for Claude Code` 的 circuit breaker；非交互模式用 auto mode（分类器自动 abort） |

---

## 7. "进哪个层"的决策树

```
新知识 ────────────────────────────
│
├─ 是机器可强制的吗（lint / test / 路径限制）？
│   └─ 是 → HOOK（.claude/settings.json）
│           理由：deterministic > advisory，零遗漏
│
├─ 是组织级合规 / 安全？
│   └─ 是 → MANAGED CLAUDE.md（/Library/Application Support/ClaudeCode/）
│           或 managed settings（permissions.deny 等硬约束）
│
├─ 每会话都需要、且全队该知道？
│   ├─ 是事实（命令、约定、架构）→ ./CLAUDE.md（< 200 行）
│   └─ 是流程（多步、按需）  → .claude/skills/<name>/SKILL.md
│
├─ 仅在某些路径触发？
│   └─ .claude/rules/<name>.md + paths frontmatter
│
├─ 仅自己用，不入 git？
│   └─ ./CLAUDE.local.md（gitignore）或 ~/.claude/CLAUDE.md
│
├─ Agent 自己学到的（build cmd / debugging insight / 偏好）？
│   └─ AUTO MEMORY（让 agent 写，人定期审计；不用手写）
│
├─ 长参考材料（API spec、长教程、设计文档）？
│   └─ 留在 docs/，CLAUDE.md 只放路径引用 @docs/...；
│      或做成 skill 的 supporting file（按需 Read）
│
└─ 一次性问答 / 短期上下文？
    └─ 不要沉淀；必要时用 /btw 让结果不进历史
```

### 7.1 反例（"压根不该沉淀"）

- 单次 bug 调试历史（除非提炼出"以后排查类似问题用此法"）
- 文件级描述（让 agent grep）
- 标准语言/框架知识（agent 已会）
- 频繁变化的信息（API key 价位、版本号）—— 让 agent 现查
- 长篇大论的"为什么"（除非进 ADR；CLAUDE.md 只放结论）

---

## 8. 文档防腐 SOP（人 + agent 各自职责）

### 8.1 人的职责

| 频率 | 任务 |
|---|---|
| 每会话 | 同一缺陷纠正 ≥ 2 次 → `/clear` 并写更具体的 prompt |
| 每 PR | review 改了哪些代码 / 接口 → 同步 CLAUDE.md / rules / skill |
| 每周 | 跑 §4.1 的 15 项 checklist；看 instruction-audit.log；剪 auto memory |
| 每月 | 走一遍决策树（§7）；把"该上升 team"的 auto memory 升进 CLAUDE.md |
| 每季 | 检查 hooks 是否还匹配实际工作流；CLAUDE.md size 趋势 |

### 8.2 Agent 的职责

| 触发 | 行为 |
|---|---|
| 用户说 "remember X" / "always Y" | 写 auto memory；不要直接改 CLAUDE.md（除非用户明说） |
| 同一次会话内学到 build/test 命令 | 候选写入 auto memory（agent 自决"以后是否有用"） |
| 用户纠正一次同一行为 | 候选写入 auto memory |
| 调用某个 skill 后失败 | 不动 skill 文件，向用户提议改进 |
| compaction 后 | 自动重读项目根 CLAUDE.md（官方机制）；nested 不会自动重注入 |

### 8.3 推荐 hook 配置（拷贝即用）

```jsonc
// .claude/settings.json — 防腐三件套
{
  "hooks": {
    "InstructionsLoaded": [{
      "hooks": [{
        "type": "command",
        "command": "jq -c '{ts:now,file:.file_path,reason:.load_reason}' >> ~/.claude/instruction-audit.log"
      }]
    }],
    "SessionStart": [{
      "matcher": "compact",
      "hooks": [{
        "type": "command",
        "command": "echo '[CRITICAL] Re-reading project CLAUDE.md after compact' && cat ./CLAUDE.md"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "npm run lint --silent || echo 'LINT FAILED — agent must fix before proceeding'"
      }]
    }]
  }
}
```

---

## 9. 五条最反直觉的发现

1. **Auto memory 是"agent 自写、人后审"，不是"人手写的快捷方式"**——很多人把 `/memory` 当成 CLAUDE.md 的别名，结果两个文件被同步污染。正确分工：用户记结论、规范、约定（CLAUDE.md），agent 记构建命令、调试洞见、风格偏好（auto memory）。
2. **InstructionsLoaded hook 只告诉你"加载"，不告诉你"遵守"**——这是当前唯一的原生 telemetry，但它只能审计死规则，不能审计被忽略的规则。要查 follow，必须靠 Stop hook + agent 评审 transcript（开销大）或把可机检规则全转 hook。
3. **"YOU MUST / IMPORTANT" 用多了等于没用**——文档允许加重语气，但 best-practices 同时把"过载强调"列为 bloat 信号；社区被表扬的 CLAUDE.md（pre-commit-hooks）特点是"thorough but not shouting in all-caps"。
4. **Skills 在长会话里会被默默驱逐**——compaction 后所有 skill 共享 25000 token 预算，超出时**最旧的 skill 整条消失**，但 agent 不会告诉你。处理多次 skill 切换的长任务时，关键 skill 要主动 `/skill-name` 重新注入。
5. **Project-root CLAUDE.md 在 compact 时会自动重注入，但 nested CLAUDE.md 不会**——这是非常细但常坑人的差异。深目录里的规则只在 agent 下次读那个目录时才回来，意味着 compaction 之后行为可能"突然变"，且看不见原因。关键规则要么放项目根，要么用 `SessionStart(matcher:"compact")` hook 强制重注入。

---

## Sources

1. [Anthropic — How Claude remembers your project (memory)](https://code.claude.com/docs/en/memory) — CLAUDE.md vs auto memory 对照表、200 行限制、`~/.claude/projects/<project>/memory/` 路径、`autoMemoryEnabled`、claudeMdExcludes
2. [Anthropic — Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices) — 5 大失败模式、CLAUDE.md size guidance、`/clear` 时机、subagent 用法
3. [Anthropic — Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — just-in-time retrieval、progressive disclosure、context rot 三大根因（n²/训练分布/位置编码）、compaction / note-taking / sub-agent 三技
4. [Anthropic — Hooks reference](https://code.claude.com/docs/en/hooks) — InstructionsLoaded 事件载荷、matcher 用法、SessionStart(compact) 重注入
5. [Anthropic — Skills](https://code.claude.com/docs/en/skills) — SKILL.md 结构、25000 token compaction 预算、context: fork 子代理、skill description 1536 字符封顶
6. [GitHub — awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — agnix（lint）、claude-rules-doctor（dead rule 检测）、pre-commit-hooks（CLAUDE.md 范本）、Ralph 系列（circuit breaker）、claude-code-tools（avoid compaction）

---

## Methodology & Confidence

- **Confidence: High**——核心结论（CLAUDE.md vs auto memory 边界、5 大失败模式、InstructionsLoaded 限制）来自 ≥ 2 份 Anthropic 一手文档；社区补充失败模式来自 awesome-claude-code 收录的开源工具自述。
- **Caveats**：
  - "200 行 adherence 下降"是文档定性表述，没有公开 benchmark 数字；建议团队用 InstructionsLoaded hook 自采。
  - WebSearch 在本次调研被 API 拒绝，因此 Reddit / HN 一手贴未抓到；社区证据通过 awesome-claude-code 的二手汇总间接获得。
  - Auto memory 是 v2.1.59+ 特性；老版本无此机制，老 CLAUDE.md 模板可能不区分两者。
