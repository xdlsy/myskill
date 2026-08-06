# AI 时代程序员综合提升 · 12 周学习计划

> **目标人群**:初中级开发者(2–5 年经验,能独立交付,仍在补系统设计与底层)
> **目标方向**:综合提升(基本功 + 系统设计 + AI 工程化 + 元能力,均衡推进)
> **时间投入**:5–10 小时/周(按均值 7 小时/周设计,可按 ±2 小时弹性调整)
> **周期**:12 周(3 个月,3 个阶段 × 4 周)
> **生成时间**:2026-06-14 ｜ **资源库调研补充**:2026-06(4 个并行 agent 检索 50+ 来源)
> **依据**:深度研究报告《AI 时代,传统程序员如何提升自己、不被淘汰》(`report.md`)

---

## 一、你的画像与定位

你处在报告里**最关键的"分叉点"**:已经能独立交付,但还没建立起"判断 / 设计 / 负责"这条资深护城河。好消息是——你不属于"22–25 岁初级岗 -20%"的高风险区,但如果不主动迁移,2–3 年后会撞上"只会照单实现 ticket"的天花板。

**这份计划针对你的核心矛盾**:
- ✅ 要补的:**系统设计 / 底层原理**(AI-proof 第 1 答案)、**代码评审**(GitHub 点名的头号差异化技能)、**把 AI 用成杠杆而非拐杖**。
- ⚠️ 要警惕的:**"初级程序员过度依赖 AI,基础算法理解下降 37%"**(MIT 2025 报告)——你正处在容易被"AI 拐杖"拖垮基础的阶段,计划里专门安排了对抗练习。
- 🎯 你的终局画像:**π 型人才**——第一支柱(一个垂直业务领域)+ 第二支柱(AI 协作工程师)+ 横梁(商业洞察 × 技术判断)。

---

## 二、总体策略(5 条原则,贯穿全程)

1. **重心迁移**:从"写代码"迁移到"判断代码、设计系统、理解业务"。每周必须有**评审 / 设计 / 复盘**的时间,不能全是"动手写"。
2. **AI 是杠杆不是拐杖**:让 AI 写大部分代码,**你的精力放在方案、评审与理解上**。每用一次 AI,都要能讲清楚"它为什么这么写"。
3. **重投 AI-proof 技能**:系统设计、分布式、底层原理、代码评审、文档——被所有高质量来源一致点名的高 ROI 方向。
4. **警惕效率陷阱**:报告里的反面教材——"代码量 +120%、有效交付 -15%"。**衡量标准是"交付了什么",不是"产了多少代码"。**
5. **输出倒逼输入**:每阶段必须有**可展示的产出**(设计文档、评审记录、技术博客、毕业项目)。没有输出的学习不算完成。

---

## 三、12 周分阶段路线图

 :**1 个核心目标 + 4 周主题 + 每周时间分配 + 毕业标准**。
每周典型分配(共 ~7h):📖 结构化学习 3h ｜ 🛠️ 动手实践 3h ｜ 🔍 评审与复盘 1h。

---

### 🟩 阶段一(W1–W4):系统设计与分布式系统(最 AI-proof 的护城河)

**核心目标**:补齐被所有来源点名的 #1 高 ROI 方向。这是 AI 当前最薄弱、人类最值钱的环节。

| 周 | 主题 | 关键动作 | 产出 |
|---|---|---|---|
| **W1** | 从单机到分布式 | DDIA(《数据密集型应用系统设计》)第 1–3 章;理解可靠性/可扩展性/可维护性三大目标、数据模型与查询语言 | DDIA 读书笔记 + 思维导图 |
| **W2** | 存储与索引穿透 | DDIA 第 3–5 章;**B+ 树 vs LSM 树 vs 红黑树** 的权衡(报告点名);事务隔离级别;用 AI 帮你画"写一条记录,存储引擎发生了什么" | 存储引擎对比表 + 时序图 |
| **W3** | 可扩展性实战 | 负载均衡 / 分片 / 缓存 / 消息队列;做一个系统设计练习:**报告里的"支持 10 万 TPS 的秒杀接口,防超卖 + 库存预扣"** | 1 份完整系统设计文档(架构图 + 容量估算 + 失败模式) |
| **W4** | 分布式难点 + 阶段验收 | CAP / 一致性 / 共识(Paxos→Raft);MIT 6.824 选读(Raft 论文 + 实验);复盘"高负载下会怎样" | Raft 选举/日志复制流程图 + 阶段一复盘 |

**🏁 阶段一毕业标准**:
- [ ] 能独立做一道中等难度的系统设计题(30 分钟内出架构图 + 关键权衡)
- [ ] 能讲清 B+ 树、事务隔离、CAP 三者的核心权衡
- [ ] 秒杀设计文档经得起"高负载 / 节点宕机 / 数据不一致"三类追问
- [ ] 写一篇系统设计主题的技术博客(对外发布或团队分享)

---

### 🟨 阶段二(W5–W8):AI 工程化核心(把 AI 变成第二大脑)

**核心目标**:掌握报告 §3.2 + §5.4 的 AI 集成工程主线。这是从"会用 AI"到"能驾驭 AI"的跨越。**你不必成为算法专家,但要建立 Karpathy 说的"心智模型"。**

| 周 | 主题 | 关键动作 | 产出 |
|---|---|---|---|
| **W5** | LLM / Transformer 基础 | Karpathy「Neural Networks: Zero to Hero」+「Let's build GPT」;3Blue1Brown Transformer 可视化。**目标:建立心智模型,不必推公式** | Transformer 注意力机制手绘图 + 白话讲解 |
| **W6** | Prompt Engineering 精进 | 吴恩达《ChatGPT Prompt Engineering for Developers》;Few-shot / CoT / ReAct;把此前的工程级 Prompt 模板升级到"智能体级" | Prompt 模式库 + A/B 效果对比记录 |
| **W7** | Agentic Workflow 抽象层 | 学透 Claude Code 的 **subagent / skill / hook / MCP / workflow**(报告 §5.4 点名的新可编程层);读 Anthropic《Building Effective Agents》 | 一个自定义 skill 或 MCP server |
| **W8** | 完整智能体闭环 + 阶段验收 | 在**真实项目**里跑通"理解代码库 → 实现 → 测试 → 修复"全闭环多智能体编排;沉淀团队级 AI 编码规范 | 真实项目智能体闭环 demo + 规范文档 |

**🏁 阶段二毕业标准**:
- [ ] 能用白话向非算法同事讲清 Transformer / 注意力 / 上下文窗口
- [ ] 手上有一套自己的 Prompt 模式库,产出质量可量化对比
- [ ] 在真实项目跑通过 ≥1 个多智能体闭环,而不是玩具 demo
- [ ] 写一份团队可复用的"AI 编码规范"

---

### 🟥 阶段三(W9–W12):元能力 + π 型人才 + 毕业项目

**核心目标**:补齐报告第四板块"不可替代的元能力",并用一个**毕业项目**把前两阶段所有能力串起来——这就是你未来面试 / 晋升 / 跳槽的核心弹药。

| 周 | 主题 | 关键动作 | 产出 |
|---|---|---|---|
| **W9** | 三大元能力训练 | 抽象建模(把模糊需求 → 领域模型)、价值判断(让 AI 给 10 个方案,你来选最优并说理)、系统思维(看代码背后的业务图谱) | 3 个元能力刻意练习记录 |
| **W10** | 产品思维 + 业务洞察 | 深入你的**垂直领域**(前置选定):读该领域 3 篇行业报告 / 业务文档,理解业务全貌;练习"产品意识"提问 | 垂直领域业务图谱 |
| **W11** | 4C 软技能 + 技术输出 | 批判性思维 / 创造力 / 协作 / 沟通刻意练习;做一次**技术分享或写一篇深度博客**;练习"把模糊业务讲清楚" | 1 次公开技术输出 |
| **W12** | 毕业项目 + 总复盘 | 在你的垂直领域,用 AI 工程化方法交付一个真实系统:**含设计文档 + 测试 + 文档(Diátaxis 四类)+ 代码评审记录**;做 12 周总复盘 | 毕业项目仓库 + 复盘报告 |

**🏁 阶段三(全程)毕业标准**:
- [ ] 毕业项目同时体现:系统设计能力 + AI 工程化 + 元能力 + 业务理解
- [ ] 有 ≥1 个对外可见的成果(开源仓库 / 博客 / 技术分享 / 团队规范)
- [ ] 完成 12 周复盘,明确下一个 3 个月的方向

---

## 四、贯穿全程的周常习惯(每周必做,雷打不动)

这些是把报告"本周可做"清单**常态化**的习惯,比任何单次学习都重要:

- [ ] **每周 ≥2 次高质量代码评审**(自己 / AI 代码都算),套用四步法
- [ ] **每周 ≥1 次"工程级 Prompt"实战**,记录 prompt + 产出 + 复盘
- [ ] **每周 ≥1 次"底层穿透"提问**(让 AI 解释某个底层机制,你复述)
- [ ] **每周 15 分钟周复盘**:这周交付了什么?AI 帮了我多少?有没有"代码量涨但交付没涨"的陷阱?
- [ ] **每月 1 篇输出**(笔记 / 博客 / 内部分享)——**没有输出,学习不算闭环**

---

## 五、防坑指南(报告里的警示,务必内化)

| 陷阱 | 表现 | 对策 |
|---|---|---|
| **AI 拐杖效应** | 技能萎缩有实证:Anthropic RCT 实测依赖 AI 工具组相关技能掌握度下降约 **17%**([anthropic.com](https://www.anthropic.com/research/AI-assistance-coding-skills);报告原文引的"37%"系二手数据,以此 RCT 为准) | **测试驱动**:让 AI 生成正常用例,**自己专注写异常流测试**;每周设"AI 戒断日"手写一道基础题 |
| **效率陷阱** | 代码量 +120%、交付 -15% | 衡量标准是"交付了什么",不是"产了多少行";每个 AI 产出都要能讲清原理 |
| **学而不练** | 囤课囤书不动手 | 每阶段必须有可展示产出,否则不许进入下一阶段 |
| **全面铺开** | 什么都想学,什么都不精 | 锁定 1 个垂直领域;系统设计优先于语言多面手(后者正在贬值) |
| **把 AI 当搜索引擎** | 只问浅层问题 | 升级到"工程级 Prompt"+ 让 AI 当深潜教练解释底层 |

---

## 六、精选资源库(按阶段,2026-06 调研补充)

> 以下资源由 4 个并行调研 agent 检索 **50+ 来源交叉验证**整理。所有链接均在搜索结果中核实存在;标注 **⚠️** 的为未逐字打开核验、建议自行确认。优先级:官方文档/权威课程 > 经典书籍 > 社区文章 > 视频。

### 🟩 阶段一(W1–W4):系统设计与分布式系统(最 AI-proof)

**系统设计入门与面试(ByteByteGo / SDI)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| ByteByteGo 官网课程 | 图文课程 | 入门→进阶 | 付费 | 自定速 | Alex Xu 主理,大量插图的 text-based 课程。W1–W4 | https://bytebytego.com |
| ByteByteGo Newsletter(Substack) | 周报 | 入门→进阶 | 免费 | 每周10min | 每周一篇"简单语言讲复杂系统",全阶段碎片补充。全阶段 | https://blog.bytebytego.com |
| *System Design Interview* Vol.1 / Vol.2(Alex Xu) | 经典书 | 入门→进阶 | 付费 | 各2–3周 | 面试圣经,清晰四步法框架;Vol.2 涵盖 news feed/payment 等更难场景。W1–W4 | https://bytebytego.com 或 Amazon |
| system-design-primer(donnemartin)**中文版** | 开源教程 | 入门 | 免费 | 2–3 周 | GitHub 最经典系统设计教程,中文版完整,新手建立全局认知首选。W1 | https://github.com/donnemartin/system-design-primer/blob/master/README-zh-Hans.md |
| 《系统设计面试:内幕指南》中文 GitBook | 开源教程 | 入门→进阶 | 免费 | 1–2 周 | Alex Xu Vol.1 社区中文翻译,配图全保留。W1–W3 | https://learning-guide.gitbook.io/system-design-interview |

**DDIA(数据密集型应用系统设计)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| *Designing Data-Intensive Applications*(Kleppmann)英文原版 | 经典书 | 进阶→硬核 | 付费 | 4–6 周 | 系统设计 #1 必读。W1–W4 核心 | https://dataintensive.net |
| 《数据密集型应用系统设计》第一版中文版 | 经典书 | 进阶→硬核 | 付费 | 4–6 周 | 翻译质量高,配英文对照最佳。W1–W4 | 豆瓣 https://book.douban.com/subject/30329536 |
| DDIA 第二版中文翻译(vonng 社区版) | 开源书 | 进阶→硬核 | 免费 | 4–6 周 | 第二版(2025/2026)新增 AI/流处理,时效最佳。W1–W4 互补 | https://github.com/vonng/ddia · 在线 https://ddia.vonng.com |
| 对话 Martin Kleppmann(第二版与 AI) | 访谈 | 进阶 | 免费 | 1h | 2026 专访,讲第二版更新与 AI 对分布式的影响。W4 收尾 | https://tonybai.com/2026/04/26/interview-martin-kleppmann-ddia-2nd-edition-ai-distributed-systems |

**分布式系统原理(CAP / 一致性 / 共识 / Raft)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| MIT 6.824 / 6.5840 分布式系统 | 名校课程 | 硬核 | 免费 | 选读2–3周 | 领域权威课,每节读一篇经典论文。W4 选读 Raft/一致性章节 | https://pdos.csail.mit.edu/6.824/ |
| MIT 6.824 Lab 2(Raft 实现)+ 自学指南 | 编程实验 | 硬核 | 免费 | 2–3周/全lab | 实现 Raft 选举/日志/持久化,做过胜过读十遍。W4 进阶挑战 | 自学指南 https://lieuzhenghong.com/mit_6.824_self_study |
| Raft 论文扩展版 | 经典论文 | 进阶→硬核 | 免费 | 1–2周 | Paxos 的"可理解版本",含 client interaction。W4 必读 | https://raft.github.io/raft.pdf |
| raft.github.io 官方可视化 | 交互工具 | 入门→进阶 | 免费 | 1h | 浏览器跑 5 节点集群,手动触发分区/选举。W4 配合论文 | https://raft.github.io |
| The Secret Lives of Data(Raft 动画) | 交互工具 | 入门 | 免费 | 1h | 分步动画讲 Raft 选举+日志复制,最佳起点。W4 先看再读论文 | https://thesecretlivesofdata.com/raft/ |

**数据库与存储(CMU 15-445 等)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| CMU 15-445/645 数据库(Spring 2026) | 名校课程 | 进阶→硬核 | 免费 | 选读2–3周 | Andy Pavlo 主讲,讲透 B+树/LSM/事务/查询优化。W2 核心 | https://15445.courses.cs.cmu.edu |
| CMU 15-445 BusTub 实验(B+ Tree Index Lab) | 编程实验 | 硬核 | 免费 | 3–4周/全lab | 手写 Buffer Pool/B+Tree Index/查询执行。W2–W4 硬核挑战(时间紧只做 B+Tree lab) | 课程网站 assignments |
| 小林 coding《图解 MySQL》 | 图文教程 | 入门→进阶 | 免费 | 1–2周 | 中文图解,索引/事务/锁讲得极清楚。W2 中文补强 | https://xiaolincoding.com/mysql |

**高并发实战(秒杀 / 缓存 / 消息队列)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| 腾讯云《秒杀系统技术拆解:从架构到落地》 | 长文 | 进阶 | 免费 | 2–3h | 最全面中文秒杀拆解:Redis 原子扣减、分布式锁、多级缓存。W3 主线 | https://cloud.tencent.com/developer/article/2570438 |
| 极客时间《秒杀系统"减库存"设计的核心逻辑》 | 精品文章 | 进阶 | 付费 | 1–2h | 对比下单减/付款减/预扣三种方案。W3 核心 | https://time.geekbang.org/column/article/40743 |
| CSDN《如何设计一个支持 10 万 QPS 的秒杀系统?》 | 长文 | 进阶 | 免费 | 1–2h | 明确针对 10 万 QPS,直接对标毕业标准。W3 | https://blog.csdn.net/cxyxus/article/details/160022298 |
| xqoasis/Flash-Sale-System-backend(GitHub) | 实战项目 | 进阶 | 免费 | 1周拆解 | Java+Redis+RocketMQ+Lua,500→10000 QPS,完整可跑。W3 落地参考首选 | https://github.com/xqoasis/Flash-Sale-System-backend |
| JavaGuide《高性能系统设计面试题》 | 八股 | 入门→进阶 | 免费 | 1–2h | 缓存/读写分离/分库分表/负载均衡梳理。W3 面试向复习 | https://javaguide.cn/high-performance/high-performance-interview-questions.html |

🏆 **阶段一 Top 3 必做**:① 精读 DDIA 第1–5章(vonng 中文版对照)——护城河地基,B+树/LSM/事务隔离讲最深;② 通读 Raft 论文扩展版 + 玩 raft.github.io 可视化——动手玩一遍胜过看十遍;③ 拆解 xqoasis 秒杀开源项目 + 自己画一遍架构图——直接对标毕业标准。
🛠️ **推荐实战(含毕业素材)**:完整《支持 10 万 TPS 的秒杀系统设计》文档(需求估算/架构图/Redis+Lua 防超卖+预扣 TTL/容灾降级/三类追问预案);MIT 6.824 Lab 2A(Raft 选举);CMU 15-445 BusTub B+Tree Index Lab;W4 写一篇带架构图+权衡的系统设计博客。
⚠️ **待验证**:Grokking the System Design Interview(designgurus.io/educative.io,内容存在但未抓到确切最新 URL 与定价);DDIA 第二版 O'Reilly 官方中文版(需订阅,未验证免费预览入口)。

---

### 🟨 阶段二(W5–W8):AI 工程化核心(把 AI 变成第二大脑)

**LLM / Transformer 基础(建立心智模型)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| Karpathy — **Deep Dive into LLMs like ChatGPT** | 视频 | 入门 | 免费 | 3h31m | 2025 最新、面向非算法背景的 LLM 全景深潜,先看建立全局心智。W5 必看 | https://youtube.com/watch?v=7xTGNNLPyMI |
| Karpathy — **Let's build GPT: from scratch** | 视频+代码 | 进阶 | 免费 | ~2h | 约 200 行手搓 GPT,配 nanoGPT;"造一遍"是建立心智最快方式。W5 核心 | https://youtube.com/@AndrejKarpathy |
| Karpathy — **Neural Networks: Zero to Hero** | 课程系列 | 进阶 | 免费 | ~20h | micrograd→makemore→nanoGPT 一条线打通。W5 进阶补强 | https://karpathy.ai/zero-to-hero.html |
| 3Blue1Brown — But what is a GPT?(Ch.5)+ Attention(Ch.6) | 视频 | 入门 | 免费 | 各~25min | 注意力机制最佳可视化,Query/Key/Value 一图通透。W5 必备 | Ch.5 https://youtube.com/watch?v=wjZofJX0v4M · Ch.6 https://youtube.com/watch?v=eMlx5fFNoYc |
| 李宏毅 **机器学习 2025**(生成式AI时代的 ML) | 视频课程 | 入门 | 免费 | 全学期 | 2025 新增推理 + AI Agent;中文授课。W5 中文备选 | https://speech.ee.ntu.edu.tw/~hylee/ml/2025-spring.php |
| 《动手学深度学习》(李沐)— 注意力/Transformer 章 | 书+代码 | 进阶 | 免费 | 选读~6h | 第10章 + PyTorch 代码可跑。W5 查漏 | https://zh.d2l.ai |

**Prompt Engineering(工程级 + 智能体级)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| 吴恩达 & Isa Fulford — **ChatGPT Prompt Engineering for Developers** | 短课 | 入门 | 免费 | ~1–2h | DeepLearning.AI 旗舰短课,工程级 prompt 最佳实践。W6 第一步 | https://deeplearning.ai/courses/chatgpt-prompt-eng |
| 吴恩达 — **Agentic AI(四设计模式)** | 短课 | 进阶 | 免费 | ~3h | Reflection/Tool Use/Planning/Multi-Agent 四大模式总纲。W6–W7 | https://learn.deeplearning.ai/courses/agentic-ai |
| DeepLearning.AI — **AI Agents in LangGraph** | 短课 | 进阶 | 免费 | ~2–3h | 从零建智能体再用 LangGraph 重构,把 prompt 升级到智能体级。W6–W7 衔接 | https://deeplearning.ai/courses/ai-agents-in-langgraph |
| Anthropic — **Prompt Engineering 交互教程** | 教程 | 入门 | 免费 | ~2h | 官方 Notebook,Few-shot/CoT/工具使用/复杂任务分解,做"Prompt 模式库"起点。W6 ⚠️仓库名以官方为准 | https://github.com/anthropics |

**Agentic Workflow(Claude Code / MCP / 多智能体编排)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| **Claude Code 官方文档**(Skills/Subagents/Hooks/MCP/Workflows) | 官方文档 | 进阶 | 免费 | 通读~4h | 2026 文档已迁至 code.claude.com,各占一页。W7 必读主线 | https://code.claude.com/docs/en/features-overview |
| Claude Code — **Orchestrate subagents at scale**(workflows) | 官方文档 | 硬核 | 免费 | ~1h | 编排大量 subagent 做代码库审计/大规模迁移。W8 闭环理论依据 | https://code.claude.com/docs/en/workflows |
| Claude Code — **Automate actions with hooks** | 官方文档 | 进阶 | 免费 | ~1h | 生命周期事件/JSON/异步 hooks,"自动化约束"的落点。W7–W8 | https://code.claude.com/docs/en/hooks-guide |
| **Model Context Protocol(MCP)**官方规范 + SDK | 官方文档+SDK | 进阶 | 免费 | ~3h | MCP 唯一权威源,Python/TS/C# SDK 齐全。W7–W8 | https://modelcontextprotocol.io/docs/getting-started/intro |
| DeepLearning.AI — **Introduction to MCP**(Anthropic 联合) | 短课 | 入门 | 免费 | ~1.5h | 含动手:同时搭 server 和 client,最快跑通一个 MCP server。W7 | https://anthropic.skilljar.com/introduction-to-model-context-protocol |
| **LangGraph** | 框架 | 硬核 | 免费 | — | 显式状态机,精细编排/分支循环的多智能体闭环首选。W8 | https://github.com/langchain-ai/langgraph |
| **CrewAI** | 框架 | 进阶 | 免费 | — | 角色化智能体团队,上手最快,快速原型。W8 备选 | https://github.com/crewAIInc/crewAI |
| Datawhale **Hello-Agents**(AI Native Agent 实战) | 中文教程 | 入门 | 免费 | ~15h | 13K+ star,中文最系统的 Agent 实战。W7–W8 中文主线 | https://datawhalechina.github.io/hello-agents |

**权威文章与设计模式(Anthropic 等)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| Anthropic — **Building Effective Agents** | 经典文章 | 入门 | 免费 | ~30min | Agent 设计"圣经":从最简单开始按需加复杂度,workflow vs agent 五模式。W7 必读 | https://anthropic.com/research/building-effective-agents |
| Anthropic — **How we built our multi-agent research system** | 文章 | 硬核 | 免费 | ~40min | Opus 4 主 agent 编排 Sonnet 4 subagents 达 90.2% 准确率。W8 真实工程参考 | https://anthropic.com/engineering/multi-agent-research-system |
| Anthropic — **Effective Context Engineering for AI Agents** | 文章 | 进阶 | 免费 | ~30min | 上下文工程(比 prompt engineering 更上层):子 agent 干净窗口/token 预算/记忆压缩。W7–W8 | https://anthropic.com/engineering/effective-context-engineering-for-ai-agents |

🏆 **阶段二 Top 3 必做**:① Karpathy《Deep Dive into LLMs》+ 3Blue1Brown 注意力可视化——两周内能白话讲清 Transformer/注意力/上下文窗口;② Anthropic《Building Effective Agents》+ Claude Code 官方文档通读——前者设计哲学,后者可落地原语;③ 跑通一个真实多智能体闭环(Claude Code workflows 或 LangGraph),顺手交付自定义 MCP server / skill。
🛠️ **推荐实战**:自训一个 nanoGPT(W5);个人 Prompt 模式库做成 Claude Code SKILL.md(W6);写一个自定义 MCP server 包日常内部工具(W7,最具可展示性);真实代码库多智能体闭环 demo + 团队《AI 编码规范》(W8);给团队配一套 hooks 做提交前 lint/安全/规范提醒。
⚠️ **待验证**:Anthropic Prompt Engineering 交互教程仓库路径(用前到 github.com/anthropics 核对);Karpathy LLM101n(仓库存在但内容未完整释出,当长期参考而非 W5 主线)。
📌 **注**:这是变化最快领域,Claude Code 文档已从旧 docs.anthropic.com 迁至 code.claude.com,以实际访问为准。

---

### 🟥 阶段三(W9–W12):元能力 + π 型人才 + 毕业项目

**抽象建模 / 领域驱动设计(DDD)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| *Learning Domain-Driven Design*(Vlad Khononov, O'Reilly 2021) | 书籍 | 进阶 | 付费 | ~20h | 当代最易读 DDD 入门,"模糊需求→领域模型"讲得最清楚,DDD 第一本必读。W9 主力 | https://oreilly.com/library/view/what-is-domain-driven/9781492057802 |
| 《领域驱动设计精粹》(DDD Distilled, Vernon) | 书籍 | 入门 | 付费 | ~6h | 最薄 DDD 概览,1–2 天读完,建立战略/战术全局观。W9 快速预热 | https://kalele.io/books |
| 《领域驱动设计》蓝皮书(Eric Evans) | 书籍 | 硬核 | 付费 | ~40h | DDD 开山之作,理论最权威但密集,当查阅字典而非首本。长期参考 | https://oreilly.com/library/view/domain-driven-design-tackling/0321125215 |
| 码如云《产品代码都给你看了,可别再说不会DDD》 | 社区文章 | 进阶 | 免费 | ~3h | 以真实上线项目逐文件拆解 DDD 落地。W12 毕业项目参考 | https://docs.mryqr.com/ddd-introduction |

**系统思维与技术决策**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| *Thinking in Systems: A Primer*(Donella Meadows) | 书籍 | 进阶 | 免费 PDF | ~8h | 系统思维最佳入门,反馈回路/存量流量/杠杆点;有官方免费 PDF。W9 主力 | https://chelseagreen.com · PDF 见 https://research.fit.edu |
| *An Introduction to General Systems Thinking*(Weinberg) | 书籍 | 硬核 | 付费 | ~12h | 经典,"标签缺失时如何思考",训练看透复杂系统的元能力。W9 深读选读 | https://geraldmweinberg.com/Site/General_Systems.html |
| 《架构整洁之道》(Clean Architecture, Bob Martin) | 书籍 | 进阶 | 付费 | ~12h | 技术决策/权衡核心框架,依赖倒置/组件边界/SOLID 的系统级视角。W9–W12 决策框架 | 豆瓣 https://book.douban.com/subject/26915970 · 中文在线 https://cactus-proj.github.io/Clean-Architecture-zh |

**产品思维 / product-minded engineer / 业务洞察**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| The Product-Minded Software Engineer(Gergely Orosz,博客) | 文章 | 入门 | 免费 | ~1h | product-minded engineer 概念源头文章。W10 必读 | https://blog.pragmaticengineer.com/the-product-minded-engineer |
| *The Product-Minded Engineer*(Drew Hoskins, O'Reilly 2024) | 书籍 | 进阶 | 付费 | ~12h | 把概念发展成完整方法论,Kent Beck/Orosz 背书。W10 主力 | https://newsletter.pragmaticengineer.com/p/the-product-minded-engineer |
| *The Software Engineer's Guidebook*(Gergely Orosz, 2023) | 书籍 | 进阶 | 付费 | 选读 | 按职业阶段组织,Part 3"Well-Rounded Senior"直接讲元能力+业务+协作。W10–W11 参考 | https://engguidebook.com |

**批判性思维 / 沟通 / 协作(4C 软技能)**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| *Thinking, Fast and Slow*(Kahneman) | 书籍 | 硬核 | 付费 | ~20h | 价值判断与决策底层教材,系统1/2 + 认知偏误,支撑"让 AI 给 10 方案你选最优并说理"。W9 | https://goodreads.com/book/show/11468377 |
| *Nonviolent Communication*(Rosenberg) | 书籍 | 进阶 | 付费 | ~8h | 观察→感受→需要→请求四步法,评审/跨团队冲突黄金工具。W11 协作 | https://cnvc.org/store/nonviolent-communication-a-language-of-life |
| Is Critical Thinking the Most Important Skill for SE?(Pragmatic Engineer) | 文章 | 入门 | 免费 | ~20min | 论证"AI 时代批判性思维反而更重要",本阶段定位锚定。W9/W11 | https://blog.pragmaticengineer.com/critical-thinking |
| *The Pyramid Principle*(Barbara Minto) | 书籍 | 进阶 | 付费 | ~8h | 结论先行 + SCQA,技术分享/深度博客的表达骨架。W11 技术输出 | https://strategyu.co/pyramid-principle-partone |

**技术写作与输出 / 个人知识管理**

| 资源 | 类型 | 难度 | 费用 | 时长 | 一句话推荐 + 适用周次 | 链接 |
|---|---|---|---|---|---|---|
| Diátaxis 文档框架 | 官方框架 | 入门 | 免费 | ~1h | 毕业标准"四类文档"官方定义,W12 必用。W12 | https://diataxis.fr |
| Google Technical Writing 专项课程 | 课程 | 入门 | 免费 | ~8h | Google 官方结构化技术写作教程。W11 主力练习 | https://developers.google.com/tech-writing/one/documents |
| Write the Docs 社区 | 社区/指南 | 入门 | 免费 | 按需 | 全球技术写作最权威社区,Docs as Code 理念。W11–W12 | https://writethedocs.org |
| *Building a Second Brain*(Tiago Forte,PARA) | 书籍 | 进阶 | 付费 | ~10h | Projects/Areas/Resources/Archives 知识组织,支撑长期沉淀。W12 | https://parazettel.com/articles/fusing-the-two-most-powerful |
| Blameless Postmortem Culture(Google SRE Book) | 章节 | 入门 | 免费 | ~1h | W12"评审记录 + 总复盘"方法论标准:无指责复盘 + 5 Whys。W12 | https://sre.google/sre-book/postmortem-culture |

🏆 **阶段三 Top 3 必做**:① *Learning Domain-Driven Design*(Khononov)——抽象建模的"肌肉",决定毕业项目能否把模糊需求落成领域模型;② *Thinking in Systems*(免费 PDF)+ The Product-Minded Software Engineer(免费文章)——一训练"系统/杠杆点"视角,一训练"产品/业务"提问,零成本护城河内核;③ Diátaxis + Google Technical Writing + Blameless Postmortem——毕业项目"文档四件套 + 评审记录 + 复盘"执行手册,免费权威。
🛠️ **毕业项目候选 ideas(W12 可选)**:① **AI 增强的领域知识助手**(DDD 建模 + RAG/Agent,回答垂直领域业务问题,demo + Diátaxis 文档 + ADR);② **"让 AI 给 10 方案,人来选"决策工作台**(价值判断训练产品化,结构化评分卡 + 说理记录);③ **代码评审/技术复盘自动化 Agent**(接 PR 流,自动生成无指责复盘初稿 + 文档草稿);④ **垂直领域"系统图谱"可视化器**(抽取限界上下文/依赖/事件流画业务图谱);⑤ **Product-minded 反馈闭环**(为真实产品痛点做"需求→领域模型→AI 方案→权衡→原型→文档"全链路 + 决策日志)。
⚠️ **待验证**:极客时间《带你吃透DDD》(链接存在,章节/价格以平台为准);Thinking in Systems 的 Florida Tech PDF 为第三方托管(试读可,正式学习建议购书);码如云 DDD 文档为第三方维护,链接稳定性需留意。

---

## 七、进度追踪表

> 复制本表到你的笔记软件,每周勾选 + 写一句话复盘。

| 阶段 | 周次 | 主题 | 完成 | 一句话复盘 |
|---|---|---|---|---|
| 一 | W1 | 单机→分布式 | ☐ | |
| 一 | W2 | 存储与索引 | ☐ | |
| 一 | W3 | 可扩展性 + 秒杀设计 | ☐ | |
| 一 | W4 | 分布式难点 + 验收 | ☐ | |
| 二 | W5 | LLM/Transformer 基础 | ☐ | |
| 二 | W6 | Prompt 精进 | ☐ | |
| 二 | W7 | Agentic 抽象层 | ☐ | |
| 二 | W8 | 智能体闭环 + 验收 | ☐ | |
| 三 | W9 | 三大元能力 | ☐ | |
| 三 | W10 | 产品思维 + 业务洞察 | ☐ | |
| 三 | W11 | 4C + 技术输出 | ☐ | |
| 三 | W12 | 毕业项目 + 总复盘 | ☐ | |

---

## 附录 A:能力自检表(前置准备,建立基线)

给自己每项打分(1=几乎不懂,5=能教别人):

**正在升值的硬技能**
- [ ] 系统设计 / 分布式 ___
- [ ] 底层原理(操作系统 / 网络 / 数据库) ___
- [ ] 代码评审能力 ___
- [ ] 文档能力 ___
- [ ] AI 工程化(Prompt / Agentic / MLOps) ___

**不可替代的元能力**
- [ ] 抽象建模 ___
- [ ] 价值判断(在多方案中选最优) ___
- [ ] 系统思维(看业务图谱) ___
- [ ] 产品 / 业务洞察 ___
- [ ] 沟通 / 协作 / 批判性思维 ___

**正在贬值的(不必刻意补,知道即可)**:语法记忆、语言多面手、栈专家分野、照单实现 ticket、机械式手工重构。

---

## 附录 B:垂直领域选择指南(前置选定,π 型第一支柱)

选领域的三条标准:
1. **你所在公司 / 团队的主业务**(近水楼台,有真实场景和数据)
2. **有足够复杂度**(能练系统设计,不是 CRUD)
3. **未来 3–5 年有需求**(医疗信息化、金融风控、电商交易、广告 / 推荐、出海支付、AI 基础设施、数据平台……)

**选定后做的事**:列出该领域 3 个待攻克的子问题,作为 W3 系统设计练习和 W12 毕业项目的素材池。

---

*本计划是活文档。每阶段验收后,根据实际进度调整下一阶段的深度与节奏——计划服务于你,不是你服务于计划。*
