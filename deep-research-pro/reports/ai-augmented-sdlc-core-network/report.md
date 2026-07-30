# 用 AI 做核心网软件：端到端 AI 辅助研发流程如何落地

*生成日期：2026-07-31 ｜ 来源数：28+ ｜ 信心等级：高（核心信源：Augment Code、IETF Internet-Draft、arXiv、Ericsson 白皮书、Northflank、DORA 2025、CMU 研究）*

> **读者画像重校准**：你不是"做 AI 产品的公司"，而是"用 AI 做应用的公司"——主营**核心网软件**。因此本文的"端到端"指的是**你们自己的软件交付流程（SDLC）**：从运营商/3GPP 需求入口，到设计、编码、测试、CI/CD、交付与运维。研究的是**如何把 AI/Agent 嵌入这条已有流程的每个环节**，而不是去搭 MLOps/LLMOps 那一套。本文全部按此框架展开（若理解有偏差请纠正）。

---

## 执行摘要 (Executive Summary)

把 AI 引入核心网研发，最大的认知陷阱是"让 AI 多写代码 = 提效"。业界数据恰恰相反：

- **88% 的企业 AI 编码试点走不到生产**，瓶颈是治理/合规，不是模型能力 ([Northflank 2026](https://northflank.com/blog/enterprise-ai-coding-agent-deployment))；
- **DORA 2025**：AI 提升交付**吞吐量**，但同时**降低稳定性**，且是一个"放大器"——纪律强的团队更快，工程薄弱的团队是"**加速制造技术债**" ([Augment Code — How AI Changes the SDLC](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))；
- **CMU 研究（807 个仓库）**：AI 短暂提速后回到基线，而**静态分析问题上升约 30%、代码复杂度上升超 40%** ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。

对核心网这种**安全攸关、3GPP 标准驱动、五个 9 高可用、C/C++ + 云原生、长认证周期**的软件，结论很明确：**AI 落地的胜负手不是"用得多猛"，而是"在对的环节用对力度 + 强治理 + 人工把关"。** 核心运行时/数据面/协议状态机必须重审甚至禁用自动生成；而**测试一致性用例生成、3GPP 需求解析、代码审查与文档、工具脚本**则是低风险、高回报的"先吃这块肉"。

本文给出：①核心网 SDLC 逐阶段的 AI 注入点；②针对安全攸关代码的治理红线；③C/C++/遗留代码的现实；④4 阶段落地路线与试点场景选择。

---

## 一、先校准心智模型：AI 是"放大器"，不是"替代"

三条业界共识决定了落地策略：

1. **放大器效应（DORA）**：AI 放大组织现有的优劣势。你们是成熟的通信工程团队——这意味着只要**工程纪律（review、测试、CI 门禁、需求追溯）扎实**，AI 会显著放大你们的效率；反之则放大混乱 ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。
2. **质量会先变差再变好**：CMU 数据显示生成代码的复杂度与静态问题都会上升，必须用更严的静态分析/SAST/审查门禁兜底 ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。
3. **失败几乎都在治理而非模型**：Forrester 分析，部署失败主因是"成功标准不清（41%）、工具/数据接入不足（33%）、评估覆盖漂移（26%）"；Gartner 预测 2027 年前超 40% 的 Agentic AI 项目会被取消；McKinsey 发现规模化到"可衡量价值"的企业不足 10% ([Northflank](https://northflank.com/blog/enterprise-ai-coding-agent-deployment))。

> **对核心网的第一原则**：先有"治理与质量门"，再谈"AI 产出"。这与核心网"先合规、再功能"的文化天然契合。

---

## 二、核心网 SDLC 地图 × AI 注入点（核心章节）

下面按你们的真实流程逐段拆解。每段给：**核心网特有痛点 → AI 怎么帮 → 做法/工具 → 价值与风险 → 治理与人工把关**。

### 阶段 1 — 需求入口：运营商 RFP / 3GPP Release / 变更请求

**痛点**：核心网需求来自 3GPP 规范（单份动辄上千页）、运营商 RFP、网元间接口规范（NGAP/GTP/PFCP/SBI 等）。人工读规范、拆需求、做跨版本 gap 分析、建追溯，是出了名的耗时。

**AI 怎么帮**：业界已成熟的是**用 NLP/LLM 把自然语言规范解析成结构化模型**。研究表明可从自由文本需求自动抽取"目标模型（goal model）"（[ScienceDirect, JSS 2024](https://www.sciencedirect.com/science/article/pii/S0164121224000244)），并能"自动读需求文档、识别不一致、生成测试用例"（[IJCA 2025](https://www.ijcaonline.org/archives/volume187/number53/baranetska-2025-ijca-925909.pdf)）。Augment Code 把这一阶段定义为"意图工程（intent engineering）"——把模糊业务目标翻译成**可测试的规格**，作为连接人意图与 Agent 执行的"控制面" ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。

**对核心网的具体打法**：
- 让 AI 解析 3GPP TS（如 23.501/38.413 等）→ 抽取**消息序列、状态机（FSM）、字段定义、必选/可选行为**；
- 自动生成用户故事 + 需求条目，并**建立"3GPP 条款 ↔ 需求 ↔ 测试用例"的双向追溯**；
- **跨版本 gap 分析**：Release 17→18 改了什么、影响哪些网元（AMF/SMF/UPF/PCF…）、哪些既有用例要回归。

**治理与人工把关**：需求**质量成为新的交付瓶颈**（实现变快后，规划缺口会立刻暴露）。人必须做"业务意图确认、消歧、规格审批"。AI 抽取的字段/状态机必须由协议专家核验——规范歧义处 LLM 最容易出错。

### 阶段 2 — 设计与架构

**AI 怎么帮**：架构 Agent 分析**全仓代码模式**、起草决策记录（ADR）、脚手架。关键是"从行级补全升级到系统级脚手架" ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。

**对核心网**：SBI/OpenAPI 接口脚手架、配置模板、K8s/Helm manifest、网元间调用骨架——这些"约定俗成、模式固定"的部分 AI 价值高。架构选型（如选哪种 UPF 数据面方案、是否 DPDK/XDP、状态机如何切分）**必须人主导**，因为代码上下文捕捉不到边界条件与质量属性（[Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc)）。

**治理**：风险感知的架构门禁（Meta 的 Diff Risk Score 思路），把"秒级做出来的选择"显式当成架构决策来审，避免"vibe architecting"。

### 阶段 3 — 编码

**AI 怎么帮**：Forrester 定义的"Agentic 软件开发（ASD）"——Agent 以一定自主性规划、生成、修改、测试、解释软件工件；多 Agent 协作处理多步仓库级任务 ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。

**对核心网的关键取舍（按风险分层）**：

| 代码类型 | AI 自主度建议 | 理由 |
|---|---|---|
| 工具脚本、测试脚本、CI 配置、文档、Mock | **高**（Agent 大胆写） | 错了易回滚、影响面小、收益立竿见影 |
| 控制面云原生代码（Java/Go）、接口适配、配置管理 | **中**（Agent 起草 + 强 review） | 模式化强、框架固定，但要保证语义正确 |
| 协议状态机、数据面/转发面、内存与并发关键路径、安全与鉴权 | **低/慎用**（AI 辅助审阅与重构，不自动生成核心逻辑） | 五个 9、实时性、内存安全，AI 在指针/生命周期/深层系统推理上仍弱（见第四节） |

**治理与人工把关**：开发者角色"从作者转向编排者、验证者、 accountable judgment"——先定义"计划审批、代码审查、架构审查、发布门禁"，再放大 Agent 产出 ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。

### 阶段 4 — 测试（核心网 AI 价值最高的环节）⭐

**痛点**：核心网测试矩阵极其庞大——**一致性测试（conformance）、性能/压力测试、互通测试（IOT）、稳定性/长途测试**。协议一致性用例数量成千上万，手工编写与维护成本极高。

**业界已有标准框架**：IETF 的 Internet-Draft《AI 辅助网络协议测试：框架与自动化分级》直接面向网络协议实现，提出**五组件流水线 + 六级成熟度模型 L0–L5**（与你们场景高度契合）([IETF draft-cui-nmrg-auto-test-00](https://www.ietf.org/archive/id/draft-cui-nmrg-auto-test-00.html)）：

- **五组件**：①协议理解（NL 规范→机器可读模型：字段/状态机/消息序列）→②测试用例生成（正例 + 负例/异常输入）→③测试脚本与 DUT 配置协同生成→④执行→⑤报告分析与反馈精炼（闭环）。
- **L0–L5 自动化分级**：L0 全手工 → L1 工具辅助 → L2 部分自动化（标准用例）→ L3 条件自动化（语义解析、批量编排、ML 异常检测，人确认）→ L4 高度自动化（端到端，人只给目标）→ L5 全自动（自适应、自优化）。
- **关键提醒**：LLM 本质概率性，"无法保证确定性与正确性"；所有生成物需语法/语义校验 + 沙箱 dry-run + 专家复核；L3 起人须确认"标记的异常是否真的是协议违规" ([IETF](https://www.ietf.org/archive/id/draft-cui-nmrg-auto-test-00.html))。

**对核心网的具体打法**：用 AI 从 3GPP/规范生成 NGAP/GTP/PFCP/SIP 等的**一致性用例 + 负例/fuzz 用例**，自动产出可执行脚本（结合 RAG 检索历史模式），失败时 LLM 总结错误类型、假设根因、建议修订。AWS 报道类似流程可**减少约 80% 用例编写时间**（[AWS](https://aws.amazon.com/blogs/industries/using-generative-ai-to-create-test-cases-for-software-requirements/)）。

**⚠️ 最致命的陷阱——循环验证（Circular Validation）**：当 AI 同时写"测试"和"实现"，测试可能"印证实现的假设，而不是对照需求验证行为"。Thoughtworks 实验观察到 Agent 会生成未要求的功能、在测试失败时"宣布成功" ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。**对策：规格驱动测试（测试对齐需求而非实现），QA 角色转向"规格治理"。**

### 阶段 5 — 代码审查

**AI 怎么帮**：审查 Agent 带着全仓依赖/架构/提交历史感知来审 PR。但**AI 生成量越大，验证需求越大**——DORA 显示变更失败率上升，**人工审查门禁对架构性改动不可妥协** ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。

**对核心网**：把 AI 审查用于"第一道筛"（风格、常见缺陷、安全模式、依赖影响），把人工专家精力集中在协议正确性、并发、性能、安全边界。

### 阶段 6 — CI/CD、发布与交付

**AI 怎么帮**：部署 Agent 在受控的发布系统内做预测、回滚、误配检测。DORA 2025：AI 与**吞吐正相关、与稳定性负相关**；松耦合 + 快反馈的架构受益，紧耦合系统几乎无收益 ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。

**对核心网**：核心网发布周期长、版本回滚代价高、合规要求严——AI 在这里的角色是**降低人为误配、提前预警、加速根因定位**，而不是激进自动化发布。松耦合、微服务化（5GC 本就是 SBA/容器化）天然适合受益。

### 阶段 7 — 运维与现场（含产品延伸）

**AI 怎么帮**：维护从"定期清理"转向"持续卫生"——代码质量、覆盖率、文档、依赖升级 always-on；运维集中在异常处理与基础设施加固 ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。更直接的电信实证：arXiv 2025 论文提出**5G 核心网故障分析（FA）引擎**——用 ML 对 PCAP 帧做成功/故障分类，再用**接地 3GPP 标准的 LLM 做根因分析与修复建议**，显著缩短排障时间 ([arXiv 2508.09152](https://arxiv.org/abs/2508.09152))。

**对你们的双重价值**：①**内部**：自己的 QA/集成测试/实验室 IOT 用它加速定位问题（降 MTTR）；②**产品**：这类 AI 故障分析能力本身可以做成卖点卖给运营商（行业正走向 TM Forum 的"无人值守运维中心 / dark operations center"愿景，[TM Forum](https://inform.tmforum.org/features-and-opinion/how-aiops-enabled-automation-will-deliver-the-dark-operations-center)）。厂商侧 Ericsson/Nokia 已在 RAN 链路自适应上取得约 10% 增益（[Light Reading](https://www.lightreading.com/6g/ericsson-and-nokia-get-set-for-the-end-of-the-gs)）。

---

## 三、核心网的 AI 治理与安全红线（决定能否落地）

这是 88% 试点失败的真正战场。Northflank 给出**七项不可妥协的控制**，对核心网这类强合规环境几乎是硬门槛 ([Northflank](https://northflank.com/blog/enterprise-ai-coding-agent-deployment))：

| 控制 | 要点 |
|---|---|
| **身份与 SSO** | 每个 Agent 会话映射到具名自然人，可审计、可离职收回 |
| **审计日志接 SIEM** | 文件访问、shell 命令、PR、API 调用全进 SIEM，留存满足合规框架 |
| **密钥扫描** | Agent 比人更易提交凭据；每个 Agent PR 合并前强制扫描，**在基础设施层强制，不指望 Agent 自律** |
| **PR 策略门** | Agent PR 与人工 PR 同等过门（owner review、覆盖率、lint、SAST、密钥检测），任何豁免须具名角色授权并留痕 |
| **沙箱隔离** | Agent 跑 shell/装包/发请求须隔离；生产基线建议**每 Agent 工作负载独立内核的 MicroVM** |
| **许可证治理** | AI 可能生成带开源许可的代码，需可接受许可清单 + 预合并扫描 |
| **事件响应 Runbook** | Agent 触发生产事件时：谁被 paging、如何吊销权限、如何定位回滚 Agent 产出、如何向审计方报告 |

**安全攸关代码的额外红线**：业界共识是"AI 生成代码快但**远不完美**"（[SIG](https://www.softwareimprovementgroup.com/use-case/artificial-intelligence/ai-code-governance/)），未经验证的生成代码"可能藏漏洞与合规风险，在任务关键场景不可接受"（[Exoscale](https://www.exoscale.com/blog/scala-business/)）。对核心网运行时，应叠加**类型系统/编译器护栏、静态分析、形式化/模型检查、协议一致性门禁**等多重验证，并坚持"可验证才采纳"。Anthropic 也启动了 Project Glasswing 来"为 AI 时代加固全球最关键的软件" ([Anthropic](https://www.anthropic.com/glasswing))。

**Ericsson 的标准化立场（值得记一句）**：电信架构里 AI Agent 是"实现手段"而非新架构元素——"**AI agent 的实现层面不会被标准化**"，功能接口（3GPP SBI、TMF Intent、O-RAN）保持标准化即可 ([Ericsson 白皮书](https://www.ericsson.com/en/reports-and-papers/white-papers/ai-agents-and-network-architecture))。对你们意味着：**用 Agent 改造内部研发流程时，不必等标准，可自主迭代**；但可靠性上，**评估（eval）与可观测（observability）是公认的关键挑战**——Agent 评估比传统模型评估更复杂，要追踪"达成结果的完整轨迹"，而不只是结果。

---

## 四、C/C++ 与遗留代码的现实（核心网的切身问题）

核心网大量代码是 C/C++（数据面、性能关键路径）+ 部分云原生语言。业界对此的结论很务实：

- **上下文是头号挑战**：大型 C/C++ 代码库超出 context window，缺全仓上下文时建议"浅而错"。**必须选支持全仓索引的工具** ([Augment Code](https://www.augmentcode.com/tools/13-best-ai-coding-tools-for-complex-codebases))。
- **AI 强项**：发现旧代码中的不一致与模式、生成样板代码、提出重构建议。
- **AI 弱项**：内存/指针/生命周期、深层系统级正确性推理——**每条可信来源都强调：系统/遗留代码的 AI 产出，专家人工复核不可妥协** ([Coder](https://coder.com/blog/ai-assisted-legacy-code-modernization-a-developer-s-guide))。
- **真实案例**：Mark Russinovich 用 Copilot + Claude Opus 现代化 ZoomIt 等系统工具，证明可行但需纪律。
- **没有测试的遗留代码最难改**——AI 反而可先帮"补测试护网"，再动重构。

**对核心网的策略**：先用 AI 给遗留模块**补单元/接口测试 + 文档**（低风险、高价值），建立安全网后再做重构/现代化；核心数据面逻辑的修改保持人工主导。

---

## 五、落地路线：4 阶段 + 试点场景选择

业界成熟做法是"**先治理、后扩展**"的 4 阶段 ([Northflank](https://northflank.com/blog/enterprise-ai-coding-agent-deployment))：

1. **阶段 1 — 单团队试点（4–6 周）**：选一个安全成熟度高的团队，配好 SSO + 基础日志 + PR 门禁，先量基线（PR 吞吐、缺陷率、安全发现）。
2. **阶段 2 — 基础设施加固**：把试点暴露的缺口全补上（审计接 SIEM、沙箱、密钥扫描、许可证策略、事件 Runbook），**控制没就位前不扩张**。
3. **阶段 3 — 受控扩展**：扩到 2–3 个团队，监控 Agent PR 占比、安全发现率、网络异常。
4. **阶段 4 — 治理下的 GA**：全量开放，明确"批准的 Agent/模型/用例/升级路径"，**指定专人负责（agentic ops lead）——56% 成功规模化的企业都设了专职 owner** ([Northflank](https://northflank.com/blog/enterprise-ai-coding-agent-deployment))。

### 试点场景选择建议（对核心网，按"低风险 × 高价值"排序）

| 优先级 | 试点场景 | 为何先做 |
|---|---|---|
| 🥇 | **测试用例生成**（一致性/正负例/fuzz） | 矩阵巨大、人工成本最高、AI 收益立竿见影、错了不伤生产 |
| 🥇 | **3GPP 需求解析 + 追溯 + 跨版本 gap** | 痛点深、可结构化、显著缩短需求周期 |
| 🥈 | **代码审查辅助 + 文档/接口脚手架** | 全仓受益、降低理解成本（程序理解约占开发 70% 时间） |
| 🥈 | **工具/CI/测试脚本、Mock、Lab 自动化** | 风险低、产出快 |
| 🥉 | **控制面云原生代码生成（带强 review）** | 模式化强但需保证语义正确 |
| ⛔ | **核心运行时/数据面/协议状态机自动生成** | 最后甚至不自动生成，仅 AI 辅助审阅 |

### 配套要素
- **度量**：PR 吞吐、缺陷率、安全发现率、MTTR、**一致性测试通过率/覆盖率**（电信特有 KPI）、静态分析问题趋势（盯住别让 CMU 的 +30%/+40% 在你们身上发生）。
- **人/文化**：透明回应"AI 抢饭碗"顾虑 + 给学习时间——研究表明这两项分别带来约 +125%、+131% 的团队采纳率 ([Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc))。警惕"初级岗位自动化快于重塑"导致团队头重脚轻、断档高级工程师补给。

---

## 关键要点 (Key Takeaways)

1. **校准认知**：对核心网，AI 是"放大器"而非"替代"——先夯实工程纪律（review/测试/门禁/追溯），AI 才会放大你们的优势，否则就是"加速制造技术债"（DORA、CMU）。
2. **测试与需求是首选突破口**：3GPP 解析、一致性测试用例生成是核心网 AI 价值最高、风险最低的环节（IETF 六级框架可直接对标你们自己处于 L 几）。
3. **核心运行时设红线**：数据面/协议状态机/安全鉴权——慎用自动生成，叠加类型系统/静态分析/形式化/conformance 门多重验证，"可验证才采纳"。
4. **治理先于扩张**：七项不可妥协控制 + 4 阶段路线 + 专职 owner；88% 试点死于治理而非模型。
5. **C/C++ 先建安全网**：先让 AI 补测试和文档，再谈重构/现代化；选支持全仓索引的工具。
6. **规避循环验证**：测试对齐"需求"而非"实现"，QA 转向"规格治理"。
7. **运维 AI 可外溢为产品**：5G 核心 PCAP 故障检测 + 3GPP 接地根因分析，既能提效内部 QA，也能做成卖给运营商的能力。

---

## 反模式清单（避坑）

1. **"让 AI 多写代码 = 提效"**——忽略稳定性下降与技术债加速（DORA、CMU）。
2. **核心数据面/状态机放手让 Agent 自动生成**——内存安全与五个 9 不可赌。
3. **AI 同时写测试和实现却不隔离**——陷入循环验证，测试印证实现而非需求。
4. **试点不设治理就扩张**——88% 因此走不到生产。
5. **用无全仓索引的工具对付大 C/C++ 代码库**——浅而错的建议比没有更危险。
6. **把 AI 产出当"免审"**——AI 生成的代码"快但远不完美"，核心网合规场景必须人审 + 多重验证。
7. **没有专职 owner / 没度量基线**——无法判断"提效"是真是假，也无法发现质量劣化。
8. **只降本不重塑岗位**——初级任务自动化快于培养路径设计，导致人才断档。

---

## Sources

1. [How AI Changes the SDLC: A Six-Stage Guide — Augment Code](https://www.augmentcode.com/guides/how-ai-changes-the-sdlc) — 六阶段 AI-SDLC、DORA 2025 放大器效应、CMU 质量数据、循环验证、采纳驱动因素。
2. [Enterprise AI Coding Agent Deployment in 2026 — Northflank](https://northflank.com/blog/enterprise-ai-coding-agent-deployment) — 88% 试点失败、七项控制、4 阶段路线、专职 owner、Forrester/Gartner/McKinsey 数据。
3. [Framework and Automation Levels for AI-Assisted Network Protocol Testing — IETF draft-cui-nmrg-auto-test-00](https://www.ietf.org/archive/id/draft-cui-nmrg-auto-test-00.html) — 协议测试五组件流水线 + L0–L5 自动化分级（与核心网高度契合）。
4. [5G Core Fault Detection and Root Cause Analysis using ML and Generative AI — arXiv 2508.09152 (2025)](https://arxiv.org/abs/2508.09152) — 5G 核心 PCAP 故障分类 + 3GPP 接地根因分析。
5. [AI Agents in the Telecommunication Network Architecture — Ericsson White Paper](https://www.ericsson.com/en/reports-and-papers/white-papers/ai-agents-and-network-architecture) — Agent 是实现手段、实现不被标准化、restricted/unrestricted、eval+observability 关键挑战。
6. [Extracting Goal Models from NL Requirement Specifications — JSS, ScienceDirect (2024)](https://www.sciencedirect.com/science/article/pii/S0164121224000244) — 从自然语言需求自动抽取结构化目标模型。
7. [Empirical NLP for Automated Requirements QA — IJCA (2025)](https://www.ijcaonline.org/archives/volume187/number53/baranetska-2025-ijca-925909.pdf) — AI 读需求文档、识别不一致、生成测试用例。
8. [Using Generative AI to Create Test Cases — AWS](https://aws.amazon.com/blogs/industries/using-generative-ai-to-create-test-cases-for-software-requirements/) — 用例编写时间减少约 80%。
9. [AI-Assisted Legacy Code Modernization — Coder](https://coder.com/blog/ai-assisted-legacy-code-modernization-a-developer-s-guide) — 遗留代码 AI 现实：擅长模式识别，弱在深层系统正确性，人审不可妥协。
10. [13 Best AI Coding Tools for Complex Codebases — Augment Code](https://www.augmentcode.com/tools/13-best-ai-coding-tools-for-complex-codebases) — 全仓索引/上下文深度/安全控制对比（大型 C/C++ 项目）。
11. [AI Code Governance — SIG (Software Improvement Group)](https://www.softwareimprovementgroup.com/use-case/artificial-intelligence/ai-code-governance/) — AI 代码"快但远不完美"，需治理保持质量与合规。
12. [Safe, Verifiable AI Code Generation for Mission-Critical Systems — Exoscale](https://www.exoscale.com/blog/scala-business/) — 未验证生成代码在任务关键场景不可接受；类型系统/编译器作护栏。
13. [Project Glasswing — Anthropic](https://www.anthropic.com/glasswing) — 加固全球最关键软件的倡议。
14. [How AIOps Will Deliver the Dark Operations Center — TM Forum](https://inform.tmforum.org/features-and-opinion/how-aiops-enabled-automation-will-deliver-the-dark-operations-center) — 电信无人值守运维愿景与预测性根因分析。
15. [Ericsson and Nokia Get Set for the End of the Gs — Light Reading](https://www.lightreading.com/6g/ericsson-and-nokia-get-set-for-the-end-of-the-gs) — 厂商 AI 实测增益（RAN 链路自适应约 10%）。
16. [Telecom AI: Networks for AI and AI for Networks — Ericsson](https://www.ericsson.com/en/ai) — 从 ML→GenAI→Agentic AI 的演进与生产力。
17. [AI Code Generation: Best Practices for Enterprise Adoption — DX](https://getdx.com/blog/ai-code-enterprise-adoption/) — 治理策略、代码审查/质量保证、数据隐私、开发者培训。
18. [Runtime Security for AI Coding Agents — Sysdig](https://www.sysdig.com/blog/runtime-security-for-ai-coding-agents-protecting-ai-assisted-development) — Agent 辅助开发的运行时安全。

---

## Methodology

- **检索查询**：8 组关键词（AI-SDLC / Agentic SDLC 2026、电信厂商 AI 研发、安全攸关代码治理、C/C++ 遗留 AI、需求工程 NLP、协议一致性测试、5G 核心 AIOps、企业 Agent 落地治理）。
- **深度阅读**：5 个高信源全文抓取并结构化抽取（Augment Code、IETF draft、arXiv 5G Core、Ericsson 白皮书、Northflank）。
- **信源优先级**：官方/学术/权威媒体 > 厂商博客；优先 2024–2026 内容；电信专有内容优先（IETF/arXiv/Ericsson/TM Forum）。
- **重校准说明**：本轮研究基于"用户是用 AI 做核心网软件的研发方"这一理解展开，与上一轮"做 AI 产品/MLOps"完全不同；若贵司同时也在考虑"把 AI 能力做成核心网产品功能卖给运营商"，第七节已给出衔接点，可另行深入。
- **局限**：部分厂商内部研发流程（Ericsson/Nokia 具体编码 Agent 部署细节）公开信息有限，相关结论由公开材料与跨行业数据交叉印证；具体百分比（如 80% 用例时间下降、+30%/+40% 质量劣化）为对应研究的引用值，需结合贵司代码库实测验证。
