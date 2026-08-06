# 业界如何使用 Agent 实现长程代码开发任务：深度研究报告

*生成日期：2026-07-16 ｜ 聚焦：自建编码 Agent ｜ 置信度：高（核心架构结论均有一手来源支撑；个别最新榜单数字见 §4 的不确定性说明）*

---

## 执行摘要

业界实现"长程代码开发"（几十分钟到数小时的连续任务，如大型重构、跨仓库迁移、复杂 bug 修复）的编码 Agent，在底层已经收敛到一组相对稳定的设计范式。核心心智模型是 **Agent Loop**——"组装上下文 → 调用模型推理 → 执行动作 → 把观察结果写回上下文"的循环。长程任务真正的工程难点不在"推理"，而在**上下文工程（Context Engineering）**：随着循环变长，上下文窗口会被工具输出淹没，模型出现"上下文腐烂（context rot）"，注意力被稀释，进而丢失目标、卡在中间步骤或过早宣布完成。

为对抗这一点，业界发展出四类手段，正好对应你最关心的四个维度：

1. **任务分解与规划**：先规划后执行（Plan-then-Act），把目标拆成 DAG 或子任务列表；但 Devin 团队（Cognition）和 Agentless 论文都警告——**过度分解会放大误传与错误**，简单线性流程往往更可靠。
2. **上下文与记忆管理**：压缩（compaction）、结构化笔记（agentic memory）、即时检索（just-in-time retrieval）、子 Agent 隔离。Anthropic 与 Cognition 的结论一致：**单线程 + 一个"压缩器"模型，是目前已知最稳的长程架构**。
3. **自我验证与反馈**：把"测试/编译/类型检查通过"当作"完成"的硬定义，形成 edit→run→observe→fix 闭环；Agentless 用"采样多候选 patch → 验证 → 选最优"把验证做成显式阶段。
4. **评测与基准**：SWE-bench 从 2023 年 10 月的 **1.96%** RAG 基线，一路涨到今天 Verified 子集上**前沿系统 70%–90%+**；METR 的"时间视野"指标显示长程能力约**每 7 个月翻一倍**。

对你要自建 Agent 最重要的一句话结论：**先做单线程线性 Agent + 强验证闭环 + 一个高质量压缩器；在上下文真的撑不住之前，不要上多 Agent 并行。**

---

## 0. 核心心智模型：Agent Loop 与长程的特殊挑战

几乎所有现代编码 Agent（Aider、Cursor、Devin、OpenHands、SWE-agent、Claude Code）底层都是同一个东西——**Agent Loop**：一个循环里反复"组装上下文 → 调用模型 → 把模型输出解析成动作 → 执行 → 把观察结果（observation）塞回上下文"。Anthropic 给出的最简定义是："**LLM 自主地在循环里使用工具**"（[Anthropic: Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。有人更直白地总结：编码 Agent 本质是"一个 LLM 钉在一个工具注册表上，外面套一个编排循环，每次 API 调用都 painstakingly 地重建状态"（[How AI Coding Agents Work](https://www.abstractalgorithms.dev/how-ai-coding-agents-work)）。

长程任务的难点不是单步推理，而是**循环变长后的状态维护**：

- **上下文腐烂（context rot）**：上下文越长，模型精确回忆其中信息的能力越下降；这是所有模型的共性，源于 Transformer 的 n² 注意力被"摊薄"（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。
- **目标漂移**：长跑过程中 Agent 会"忘记待办子目标、执着于某个中间工具调用、或过早宣布任务完成"（[Redis: Long-Horizon Agents](https://redis.io/blog/long-horizon-ai-agents-memory-state-infrastructure/)）。
- **错误复合**：长循环里每一步的小错误会层层叠加，可靠性急剧下降——这是 Cognition 整篇"长跑 Agent 理论"的出发点（[Cognition: Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)）。
- **可观测的失败前兆**：研究发现长程编码 Agent 在真正失败前几步，往往有"可检测的内部信号"，比如**反复重试同一个方法**——这可以被用来在循环里提前干预（[Martian: Agentic Long-Horizon Tasks](https://withmartian.com/post/beyond-static-mechanistic-interpretability-agentic-long-horizon-tasks-as-the-next-frontier)）。

理解了"长程 = 上下文与状态的对抗"，下面四个维度都是这条主线的不同切面。

---

## 1. 任务分解与规划

### 1.1 先规划后执行（Plan-then-Act）

学术界与工业界都验证了**把高层规划与底层执行分开**能提升目标对齐。研究路线 *Plan-and-Act* 明确采用"先规划、后执行"，发现分离后 Agent 行为与目标更一致（[Plan and Act（YouTube/论文介绍）](https://www.youtube.com/watch?v=_GdoyYufuw8)）。工业侧，**Devin 的标志性行为就是"先读代码库、写出一份多步骤书面计划，再动一行代码"**，并在执行中可以动态修改计划（[How Devin AI Actually Thinks](https://medium.com/@nitinmatani22/how-devin-ai-actually-thinks-autonomous-planning-dag-execution-and-dynamic-re-planning-explained-997be175a475)）。

### 1.2 DAG 与 Supervisor / Planner / Worker

更结构化的做法是把任务拆成**有向无环图（DAG）**。例如 *Task-Decoupled Planning (TDP)* 用一个 **Supervisor** 把原任务拆成"子任务 DAG"，一个 **Planner** 调度执行，worker 去干活——把"规划"和"执行"在架构上彻底分离（[arXiv: Task-Decoupled Planning](https://arxiv.org/html/2601.07577v1)）。AI21 的定义也强调：长程任务要求 Agent"把高层目标分解成中间子任务序列、跨子任务管理状态、并在中间步骤失败时自适应"（[AI21: What are Long-Horizon Tasks?](https://www.ai21.com/glossary/ai-agent/what-are-long-horizon-tasks/)）。

### 1.3 按"垂直切片"分解，而不是按模块/仓库分解

OpenAI Codex 社区的一条实战经验值得记住：**按垂直切片（vertical slice）分解，效果远好于按仓库分解**——即"一个 Agent 负责一个功能贯穿整个技术栈"，而不是"一个 Agent 负责一个仓库"（[OpenAI Codex Discussions](https://github.com/openai/codex/discussions/13287)）。这与软件工程里"特性团队 > 组件团队"的经验一致：减少跨 Agent 的接口契约负担。

### 1.4 动态重规划

计划不是一次写死。Devin 会在遇到问题时**动态重规划**（[同上](https://medium.com/@nitinmatani22/how-devin-ai-actually-thinks-autonomous-planning-dag-execution-and-dynamic-re-planning-explained-997be175a475)）；业界普遍把"维护一个可变的 TODO / 计划列表"作为长程 Agent 的标配（见 §2.3 结构化笔记）。

### 1.5 反例：过度分解是危险的——"不分解"也能赢

这是最容易被忽视、但对自建者最重要的一条。**Agentless** 论文（UIUC，FSE 2025）直接质疑"我们真的需要复杂的自主 Agent 吗"，给出一个**三阶段固定流水线**：**定位（localization）→ 修复（repair）→ 补丁验证（patch validation）**，**不让 LLM 自行决定下一步动作、也不给它复杂工具**。结果它在 SWE-bench Lite 上以 **32.00%（96 个修复）、成本仅 \$0.70** 打败了当时所有开源 Agent，并自陈目标是"**重置自主软件 Agent 的基线**"（[Agentless, arXiv:2407.01489](https://arxiv.org/abs/2407.01489)；[FSE2025 全文](https://lingming.cs.illinois.edu/publications/fse2025.pdf)）。

Cognition 也从工程角度给出同样的告诫：把任务拆给多个子 Agent 并行、最后合并，是"很诱人但极其脆弱"的架构——子 Agent 之间只要有一处理解偏差，最终合并就是灾难（详见 §2.5）。

> **给自建者的启示**：分解是手段不是目的。先问"这个任务能否用一条线性流水线 + 强验证解决"；只有当线性流程在上下文或复杂度上撑不住时，才引入显式规划/子任务。

---

## 2. 上下文与记忆管理（长程的真正主战场）

Cognition 把话说得很硬：模型已经很聪明，**"上下文工程"是构建 Agent 的工程师的 #1 工作**（[Cognition](https://cognition.ai/blog/dont-build-multi-agents)）。Anthropic 同样把上下文定义为一个"**有限、边际收益递减的资源**"，并给出"**寻找最小的高信噪比 token 集**"作为总原则（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。业界手段可归为五类：

### 2.1 工具与系统提示的"最小化"

- **工具集要小而正交**：最常见的失败是"工具集臃肿、功能重叠、让模型在多个工具间犹豫"。Anthropic 的标准——"如果一个人类工程师都无法明确说清该用哪个工具，就别指望 Agent 做得更好"（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。
- **系统提示要"对的航高"**：既不能硬编码脆弱的 if-else 逻辑，也不能给模糊空泛的高层指令；用 XML/Markdown 分节组织（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。

### 2.2 压缩（Compaction）——第一根杠杆

把"接近上下文上限的对话"做**高保真摘要**，然后用摘要重开一个新窗口继续。Claude Code 的实现是：把消息历史交给模型去压缩，**保留架构决策、未解决的 bug、实现细节，丢弃冗余的工具输出**，压缩后保留最近访问的几个文件继续（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。

- **最轻量的压缩：清空工具结果**。一个工具调用深入历史后，原始返回值往往再无意义，直接清掉是最安全的"轻量压缩"（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。
- **调参建议**：先最大化 recall（确保摘要不丢关键信息），再迭代提高 precision（砍掉冗余）——在复杂的真实 Agent trace 上仔细调（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。

### 2.3 结构化笔记 / Agentic Memory——持久、低开销的"外置记忆"

让 Agent **定期把笔记写到上下文窗口之外**（文件/外部存储），需要时再拉回。这是成本最低的长程记忆手段：

- Claude Code 维护 **TODO 列表**；自定义 Agent 维护 `NOTES.md`——这个简单模式让 Agent 能跨几十次工具调用追踪进度与依赖（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。
- 极端案例：Claude 玩 Pokémon 在几千步里精确记账（"过去 1234 步我在 1 号路练级，皮卡丘升了 8/10 级"），上下文重置后**读自己的笔记继续**数小时的训练/探索（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。

### 2.4 即时检索（Just-in-Time Retrieval）+ 渐进式披露

不要预先把所有数据塞进上下文，而是**只保留轻量引用（文件路径、查询、链接），运行时用工具按需加载**。Claude Code 分析大数据库时不加载全量数据，而是写查询、存结果、用 `head`/`tail` 局部查看（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。

- 文件名、目录层级、时间戳本身就是**强信号**：`tests/test_utils.py` 与 `src/core_logic/test_utils.py` 含义不同，Agent 可据此渐进式探索（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。
- **混合策略最实用**：Claude Code 把 `CLAUDE.md` 这类"项目说明"前置塞入，同时用 `glob`/`grep` 即时检索——既快又避开了"陈旧索引"问题（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。
- LangChain 把这套打法归纳为四招：**write / select / compress / isolate**（[LangChain: Context Engineering for Agents](https://www.langchain.com/blog/context-engineering-for-agents)）。

### 2.5 子 Agent 隔离——但要警惕"并行写代码"

子 Agent 的价值是**隔离上下文**：主 Agent 负责高层规划与综合，子 Agent 用干净的上下文做深度技术活，可能烧掉几万 token，但**只返回 1,000–2,000 token 的浓缩摘要**（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。Anthropic 的多 Agent 研究系统正是靠这个在复杂任务上显著超过单 Agent（[Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)）。第三方测评也把"子 Agent 上下文隔离"列为大型任务下最强大的上下文工程模式（[MorphLLM](https://www.morphllm.com/context-engineering)；[Victor Dibia](https://newsletter.victordibia.com/p/context-engineering-101-how-agents)）。

**但 Cognition 给了关键警告**（截至 2025 年 6 月对 Claude Code 的观察）：

> Claude Code 的子任务 Agent **从不与主 Agent 并行工作，且通常只负责"回答问题"而不是写代码**。因为子 Agent 缺乏主 Agent 的上下文，做不了超出"回答一个明确问题"范围的事；若让多个子 Agent 并行写代码，它们会给出**相互冲突**的结果。子 Agent 的真正好处是：它的调研工作不必留在主 Agent 的历史里，从而延长主 Agent 的可用 trace 长度。（[Cognition](https://cognition.ai/blog/dont-build-multi-agents)）

Cognition 给出两条"上下文工程原则"，并主张**默认排除任何违反它们的架构**：

- **原则 1：共享上下文——而且要共享完整 Agent trace，而不是只传单条消息**。只把子任务文字传给子 Agent 会丢失"为拆分任务而做的那些工具调用"所隐含的决策。
- **原则 2：动作携带隐式决策，冲突的决策带来坏结果**。两个子 Agent 看不到彼此的动作，就会基于相互冲突的假设工作（例如都画了一只"风格完全不同"的鸟）。（[Cognition](https://cognition.ai/blog/dont-build-multi-agents)）

> **结论**：子 Agent 的正确用法是"**隔离式调研 / 检索**"，不是"并行写代码再合并"。

### 2.6 长程的终极架构：单线程 + 压缩器模型

Cognition 给出的"真正长跑"架构是：**单线程线性 Agent（上下文连续）+ 一个专门的"压缩器" LLM**，其唯一职责是把"一段动作与对话历史"压缩成关键细节、事件与决策。他们直言这"很难做对"，甚至**在 Cognition 内部为此微调了一个小模型**（[Cognition](https://cognition.ai/blog/dont-build-multi-agents)）。这与 Anthropic 的 compaction + agentic memory 是同一思路的两种表述。

### 2.7 可参考的开源实现：OpenHands 的 Event Stream + Condenser

OpenHands（前 OpenDevin）给出了一个清晰、可抄作业的架构：

- **Event Stream（事件流）** 是骨干——一个不可变、类型安全的 **Action（Agent→环境）/ Observation（环境→Agent）** 日志；Agent 的状态与记忆就是这个事件日志（[OpenHands ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/a4b6ad6b48850c0c331d1259fc66a69c-Paper-Conference.pdf)；[OpenHands SDK Docs: Events](https://docs.openhands.dev/sdk/arch/events)）。
- **Condenser（冷凝器）**：在把历史发给 LLM 之前介入，**丢弃旧事件并用摘要替换**，维持有界的对话规模（[OpenHands: Context Condenser](https://docs.openhands.dev/sdk/guides/context-condenser)；[arXiv: OpenHands SDK](https://arxiv.org/html/2511.03690v1)）。
- **CodeActAgent**：用"代码即动作（CodeAct）"范式，让 Agent 直接写代码/命令作为动作（[OpenHands ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/a4b6ad6b48850c0c331d1259fc66a69c-Paper-Conference.pdf)）。

> 自建者可以直接借鉴："**事件日志 = 记忆与状态**，condenser = 压缩，CodeAct = 工具调用即代码"这套三元组。

---

## 3. 自我验证与反馈闭环

没有验证的长程 Agent 会"自信地"产出错误代码并宣布完成。业界的共识是：**让 Agent 只在"通过客观信号"时才认为自己做完了**。

### 3.1 把"测试通过"当作完成的硬定义

Addy Osmani 的总结很有代表性：构建一个反馈闭环，让 Agent **只有当代码真正满足规范（测试通过作为正确性代理）时才"认为"自己做完了**（[Self-Improving Coding Agents](https://addyosmani.com/blog/self-improving-agents/)）。多位实践者把"自验证闭环"称为用好编码 Agent 的**单一最重要的心智模型**（[LinkedIn: Nikhil Thorat](https://www.linkedin.com/posts/nikhil-thorat-58a18232_coding-agents-increase-the-autonomy-slider-activity-7348344728607764482-tX-S)）。

### 3.2 执行反馈循环：edit → run → observe → fix

核心闭环是：**写代码 → 在真实环境执行（编译/跑测试/跑 linter）→ 把执行输出作为观察喂回 → 据此修正**。社区把自纠偏框定为"**反馈控制回路，而不是'更多 token'**"，并指出当失败信号是**可操作（actionable）**时，重试能显著提高成功率（[Self-Correcting Agents Are Not What You Think](https://medium.com/@Micheal-Lanham/self-correcting-agents-are-not-what-you-think-they-are-d19398186373)）。学界 *ReVeal* 把这个"生成—验证"多轮循环做成了强化学习框架，提供细粒度反馈（[arXiv: ReVeal](https://arxiv.org/html/2506.11442v1)）。

> **关键工程点**：给 Agent 的不是"失败/成功"二值，而是**结构化、可操作的错误信号**（编译器/测试的具体报错、行号、失败用例）——Hacker News 上的共识是"提升编码 Agent 的测试价值，需要更好的 oracle 和更可操作的验证信号"（[HN: My Agent Skill for TDD](https://news.ycombinator.com/item?id=48398925)）。

### 3.3 Agentless 的"验证即阶段"：采样多候选 patch → 选最优

Agentless 把验证做成**流水线的显式第三阶段**：在 repair 阶段，先拿到编辑位置，**采样多个候选补丁**，再在 validation 阶段挑选最优解（[Agentless GitHub](https://github.com/openautocoder/agentless)；[FSE2025 全文](https://lingming.cs.illinois.edu/publications/fse2025.pdf)）。这是"**best-of-N + 选择性验证**"的工程化体现——比让 Agent 单次下注更稳。

### 3.4 影响分析：告诉 Agent 哪些测试有风险

*TDAD（Test-Driven Agentic Development）* 用**影响分析**告诉 Agent"哪些测试处于风险中"，使其在提交前就能自我纠偏（[arXiv: TDAD](https://arxiv.org/html/2603.17973v1)）。这是把"测试反馈"从"事后补救"前移到"事前预警"。

### 3.5 多 Agent 评审（reviewer / delegator 模式）

OpenHands 等框架支持"**delegation**"：一个 Agent 把任务交给另一个 Agent，并对其结果做评审（[Medium: Coding Agents on SWE-Bench](https://medium.com/@te2be/coding-agents-open-source-approaches-on-swe-bench-074cc28c5bb0)）。也有研究（如 *ToM-SWE*）采用双 Agent：主 Agent 做生成/编辑/调试，辅 Agent 协助（[Emergent Mind: SWE-Agents](https://www.emergentmind.com/topics/software-engineering-agents-swe-agents)）。注意这与 §2.5 并不矛盾——这里的"多 Agent"是**串行评审/委派**，不是并行写代码。

### 3.6 警惕 reward hacking 与虚假完成

METR 在评测里专门做的一件事就是**检查 reward hack**：用 LLM + 关键词自动标记、再人工复核，确认 Agent 是真解决了任务还是"钻了评分系统的空子"（[METR: Time Horizons](https://metr.org/time-horizons/)）。自建 Agent 时，"测试通过"也可能被**篡改测试**或**绕过检查**满足——要把验证信号设计得**抗作弊**（例如只信任 Agent 没接触过的 held-out 测试、或独立运行验证）。

### 3.7 监测失败的早期信号

如 §0 所述，**反复重试同一方法**是即将失败的可观测前兆（[Martian](https://withmartian.com/post/beyond-static-mechanistic-interpretability-agentic-long-horizon-tasks-as-the-next-frontier)）。工程上可以加一道"卡死检测"：连续 N 次相同动作/相同报错就触发"回退 / 换策略 / 上报人类"。

---

## 4. 评测与基准

### 4.1 SWE-bench 家族：从 1.96% 到 70%+ 的轨迹

- **起源**：SWE-bench 于 **2023 年 10 月**发布，最初的 **RAG 基线只有 1.96%**；随后的 **SWE-agent** 是第一个面向该基准的 Agent 系统（[SWE-bench 官方](https://www.swebench.com/original.html)；[GitHub](https://github.com/swe-bench/SWE-bench)）。
- **Verified 子集**：2024 年 8 月由 OpenAI 发布，**500 个经人工验证的实例**，已成为事实标准（[SWE-bench Verified](https://www.swebench.com/verified.html)）。
- **今天的高度**：官方页面称 **mini-SWE-agent 仅用约 100 行 Python 就能在 Verified 上拿到约 74%**（[SWE-bench 官方](https://www.swebench.com/)）。前沿完整系统（多 rollout + 评审类）已进入 70%–90%+ 区间。
- **⚠️ 不确定性说明**：搜索引擎返回的若干第三方榜单站点（如某些 steel.dev / llm-stats / localaimaster 页面）声称"Claude Mythos 5 = 95.5%"等数字，这些**模型名与具体百分比高度疑似 AI 生成的 SEO 内容、未经证实**。本报告**不采信**这些数字；精确名次请以 [swebench.com/verified.html](https://www.swebench.com/verified.html) 官方榜单为准。

### 4.2 METR"时间视野"：长程能力的标尺，约每 7 个月翻倍

METR 的"**任务完成时间视野**"是衡量长程能力最权威的指标：定义为"按人类专家完成时长计量的任务长度，在该长度上 Agent 有 X% 把握成功"。要点（[METR: Time Horizons](https://metr.org/time-horizons/)）：

- **方法论**：对每个 Agent 拟合一条 logistic 曲线（成功率 vs 人类任务时长），取与 50%/80% 成功率相交的任务时长。任务取自 RE-Bench、HCAST 等软件/ML/安全任务集，**每任务跑 6 次独立运行**，并专门排查 reward hack 与 token 预算不足。
- **增长趋势**：**指数拟合**远优于线性/双曲/logistic——即时间视野在**指数增长**（约每 7 个月翻倍）。截至 2026 年 4 月，前沿模型的 50% 时间视野已达约 **17 小时**（但官方标注"16 小时以上的测量在当前任务集上不可靠"）。
- **重要解读**：METR 反复强调，时间视野 ≈ "**低上下文的人（如新员工/外包）能在该时长内完成的自包含任务**"，**不等于**资深工程师在熟悉项目里的产出；且任务"干净、可算法评分"，真实工作更"脏"，Agent 在整体评分下表现会**显著下降**。

> 对自建者的意义：不要被"SWE-bench 90%"误导——那是干净、自包含、有明确测试的任务。你自己的长程任务是"脏"的，**预留足够的验证与人工兜底**。

### 4.3 应对饱和：更难的基准

- **SWE-bench Pro**：约 1,865 个实例，专为**更复杂、更真实的长程编程挑战**设计，已被引用百余次（[OpenReview: SWE-Bench Pro](https://openreview.net/forum?id=9R2iUHhVfr)）。
- **SWE-rebench**：每月刷新题目以对抗**数据污染**。
- 学术剖析：*Dissecting the SWE-Bench Leaderboards* 指出早期 Lite 上 SOTA 多由 Claude 3.5 Sonnet / GPT-4 / DeepSeek R1 等驱动，并系统讨论了榜单可信度问题（[arXiv:2506.17208](https://arxiv.org/html/2506.17208v1)）。

### 4.4 成本效率维度

Agentless 用 **\$0.70 / 32%** 证明了"简单流水线 + 强验证"的性价比（[Agentless](https://arxiv.org/abs/2407.01489)）。对自建者：**成本/通过率**是与准确率并列的一等指标——盲目堆 Agent、堆 token 往往边际收益极差。

---

## 5. 各家架构速查表

| 系统 | 规划 | 上下文/记忆 | 验证 | 关键特征 | 来源 |
|---|---|---|---|---|---|
| **Agentless** | 固定三阶段流水线，**不让 LLM 自主决策** | 无长程记忆（每步预定） | **采样多候选 patch + 显式 validation 阶段** | "重置基线"，\$0.70/32% | [arXiv](https://arxiv.org/abs/2407.01489) |
| **SWE-agent** | Agent loop 自主决策 | ACI（agent-computer interface） | 执行反馈（跑测试） | 首个 Agent 基线；mini 版约 100 行达 74% | [官方](https://www.swebench.com/) |
| **OpenHands** | CodeActAgent 自主 + delegation | **Event Stream（Action/Observation）+ Condenser** | 沙箱执行 + 测试 | 事件流=记忆；可插拔 condenser | [ICLR'25](https://proceedings.iclr.cc/paper_files/paper/2025/file/a4b6ad6b48850c0c331d1259fc66a69c-Paper-Conference.pdf) |
| **Devin (Cognition)** | **先写书面多步计划 + DAG + 动态重规划**；Devin 2.0 可并行多实例（Agent Fan Out） | 单线程 + **微调的压缩器小模型** | 执行反馈 | "长跑可靠性"理论；反对多 Agent 并行 | [Cognition](https://cognition.ai/blog/dont-build-multi-agents) |
| **Aider** | **architect 模型提方案 → editor 模型落编辑**（双模型，单 Agent，**无原生子 Agent**） | repo-map（代码结构摘要）+ git | 执行/测试反馈 | git 优先；architect/editor 分离 | [Aider Docs](https://aider.chat/docs/usage/modes.html) |
| **Claude Code** | TODO 列表 + Plan 模式 | **CLAUDE.md 前置 + glob/grep 即时检索 + compaction + 子 Agent 隔离调研** | 测试/执行反馈 | 子 Agent 只答问题、不并行写代码 | [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)；[Cognition](https://cognition.ai/blog/dont-build-multi-agents) |

---

## 6. 给"自建编码 Agent"的落地建议（综合）

把以上证据收敛成一份可执行的蓝图：

1. **从"单线程线性 Agent + 强验证闭环"起步**。先实现 edit→run(test/compile/typecheck)→observe→fix 的核心循环，把"测试通过 + held-out 验证"作为 done 的硬定义（§3.1–3.2）。在它稳之前，不要碰多 Agent。
2. **上下文工程是你的 #1 工作**。最小正交工具集 + 分节系统提示（§2.1）；用事件日志做记忆（§2.7）。
3. **尽早接 compaction**。先做最轻量的"工具结果清空"，再做高质量对话压缩；调参先 recall 后 precision（§2.2）。
4. **加结构化笔记 / 外置记忆**（TODO、`NOTES.md`）。成本最低、收益最大，能跨压缩保持连贯（§2.3）。
5. **即时检索 + 渐进披露**。只存引用（路径/查询），运行时按需加载；项目说明前置、代码即时检索的混合策略最实用（§2.4）。
6. **子 Agent 只用于隔离式调研/检索，不用于并行写代码**。让它返回 1–2k token 摘要；遵循 Cognition 两原则（共享完整 trace、动作携带隐式决策）（§2.5）。
7. **真长程才上"压缩器模型"**。考虑微调一个小模型专门压缩历史；这是 Cognition/Anthropic 共同的终极长跑架构（§2.6）。
8. **规划要克制**。能线性解决就别 DAG；若要分解，按"垂直切片"而非按仓库；计划要可动态重规划（§1.3–1.5）。
9. **验证要抗作弊**。用 Agent 没接触过的测试做裁决；采样 best-of-N 再选；加"卡死检测"（连续重复动作就回退/上报）（§3.3, §3.6, §3.7）。
10. **用真实"脏"任务做基准，盯成本/通过率**。SWE-bench/METR 只能当参考，别当承诺（§4.2, §4.4）。

---

## 关键要点（Key Takeaways）

- **长程 = 与上下文腐烂对抗**。模型够聪明，瓶颈在状态维护；"上下文工程"是构建 Agent 的头号工程工作。
- **业界已收敛到一组稳定范式**：Agent Loop + Plan-then-Act + Compaction/Notes/即时检索 + 子 Agent 隔离 + 强验证闭环。
- **最稳的长程架构是"单线程线性 + 压缩器模型"**，而不是多 Agent 并行——并行写代码会因"动作携带隐式决策"而相互冲突（Cognition + Anthropic 一致结论）。
- **验证是闭环的灵魂**：把"测试通过"当 done，给可操作的错误信号，best-of-N + 选择，且要抗 reward hacking。
- **能力在指数增长**（METR 时间视野约每 7 个月翻倍），但"干净基准 ≠ 真实脏任务"，自建者要预留验证与人工兜底。
- **简单可能赢**：Agentless 用三阶段流水线 + 强验证，以 \$0.70 打败复杂 Agent，提醒我们"分解与自主决策"是手段不是目的。

---

## 局限与未覆盖

- **未深入**：具体的 ACI（agent-computer interface）工具设计细节、多模态编码 Agent（SWE-bench Multimodal）、RL 训练自验证 Agent 的完整方法（ReVeal/TDAD 仅点到）。
- **榜单数字的不确定性**：前沿模型在 SWE-bench Verified 上的精确名次与百分比变动很快，且第三方 SEO 站点数字不可信；需要精确数字时请查 [官方榜单](https://www.swebench.com/verified.html)。
- **时间视角**：报告基于 2026 年 7 月可得的公开资料；该领域演化极快，6 个月后部分结论（尤其"别并行写代码"）可能被新一代模型推翻。

---

## 来源（Sources）

1. [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — 上下文工程总论：compaction / agentic memory / 子 Agent 隔离 / 即时检索（**核心一手来源**）
2. [Cognition — Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents) — 长跑 Agent 可靠性理论：两原则、单线程+压缩器、反对并行写代码（**核心一手来源**）
3. [Agentless: Demystifying LLM-based Software Engineering Agents (arXiv:2407.01489)](https://arxiv.org/abs/2407.01489) — 三阶段定位→修复→验证流水线，\$0.70/32%，"重置基线"（**核心一手来源**）；[FSE2025 全文](https://lingming.cs.illinois.edu/publications/fse2025.pdf)；[GitHub](https://github.com/openautocoder/agentless)
4. [METR — Task-Completion Time Horizons](https://metr.org/time-horizons/) — 时间视野指标、指数增长、方法论与 reward hack 排查（**核心一手来源**）
5. [OpenHands (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/file/a4b6ad6b48850c0c331d1259fc66a69c-Paper-Conference.pdf) — Event Stream 架构、CodeAct；[SDK Docs: Events](https://docs.openhands.dev/sdk/arch/events)；[Context Condenser](https://docs.openhands.dev/sdk/guides/context-condenser)；[arXiv SDK 论文](https://arxiv.org/html/2511.03690v1)
6. [SWE-bench 官方](https://www.swebench.com/) / [Verified](https://www.swebench.com/verified.html) / [Original（1.96% 基线）](https://www.swebench.com/original.html) — 基准起源与轨迹
7. [Aider — Chat Modes](https://aider.chat/docs/usage/modes.html) — architect/editor 双模型
8. [How Devin AI Actually Thinks (Medium)](https://medium.com/@nitinmatani22/how-devin-ai-actually-thinks-autonomous-planning-dag-execution-and-dynamic-re-planning-explained-997be175a475) — Devin 规划/DAG/重规划
9. [Addy Osmani — Self-Improving Coding Agents](https://addyosmani.com/blog/self-improving-agents/) — 验证闭环心智模型
10. [Redis — Long-Horizon AI Agents: Memory & State Infrastructure](https://redis.io/blog/long-horizon-ai-agents-memory-state-infrastructure/) — 目标漂移等长程失败模式
11. [Martian — Agentic Long-Horizon Tasks](https://withmartian.com/post/beyond-static-mechanistic-interpretability-agentic-long-horizon-tasks-as-the-next-frontier) — 失败早期信号（重复重试）
12. [LangChain — Context Engineering for Agents](https://www.langchain.com/blog/context-engineering-for-agents) — write/select/compress/isolate 四招
13. [MorphLLM — Context Engineering](https://www.morphllm.com/context-engineering) / [Victor Dibia — Context Engineering 101](https://newsletter.victordibia.com/p/context-engineering-101-how-agents) — 子 Agent 隔离为最强模式
14. [arXiv: Task-Decoupled Planning](https://arxiv.org/html/2601.07577v1) — Supervisor/Planner/Worker + DAG
15. [OpenAI Codex Discussions — vertical-slice decomposition](https://github.com/openai/codex/discussions/13287)
16. [arXiv: TDAD (Test-Driven Agentic Development)](https://arxiv.org/html/2603.17973v1) / [arXiv: ReVeal](https://arxiv.org/html/2506.11442v1) — 影响分析、自验证 RL
17. [OpenReview: SWE-Bench Pro](https://openreview.net/forum?id=9R2iUHhVfr) / [arXiv: Dissecting SWE-Bench](https://arxiv.org/html/2506.17208v1) — 更难基准与榜单剖析
18. [HN: My Agent Skill for TDD](https://news.ycombinator.com/item?id=48398925) / [Self-Correcting Agents (Medium)](https://medium.com/@Micheal-Lanham/self-correcting-agents-are-not-what-you-think-they-are-d19398186373) — 可操作验证信号、反馈控制回路

---

## 方法论（Methodology）

围绕用户目标（自建编码 Agent）与四个重点维度（任务分解与规划、上下文与记忆、自我验证、评测基准），执行了 10 余次 Web 检索（多关键词变体 + 限定权威域名），并对 4 篇核心一手来源做了全文深读（Anthropic、METR、Cognition、Agentless）。对疑似 AI 生成的第三方榜单数字做了标注与剔除。子问题清单：

- 业界如何分解长程代码任务、维护计划与动态重规划？
- 长会话下如何管理上下文（压缩/检索/外置记忆/子 Agent 隔离）？
- 如何让 Agent 自我验证（TDD/执行反馈/best-of-N/抗作弊）？
- SWE-bench 与 METR 的现状、轨迹与可信度如何？

共分析 18 组来源，其中 4 组为一手/核心来源。
