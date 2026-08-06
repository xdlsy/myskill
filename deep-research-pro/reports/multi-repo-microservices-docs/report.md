# 多仓库微服务项目的文档资产管理:深度研究报告

*生成日期:2026-07-25 | 来源数:~22(精读 7)| 置信度:高*

> **场景前提**:当前目录下 3 个独立 Git 仓库,均为后端微服务,通过 API/gRPC 互相调用;从零搭建文档体系,目标是管理 API 接口文档 / 架构文档 / spec 等「文档资产」。

---

## 执行摘要

3 个独立 Git 仓共同构成一个项目,这是典型的 **polyrepo 微服务** 场景。业界共识是:**不要在「集中式」和「分布式」之间二选一,而是采用「混合/专业化(Specialized)」拓扑**——把**与代码强耦合的文档(API spec、服务级 runbook、服务级 ADR)留在各自服务仓**(docs-as-code,随代码原子提交、随版本演进),同时**建立一个中央文档仓**承载**跨服务的全局资产**(系统级 C4 架构图、全局 ADR、onboarding、聚合后的 API 目录)。中央仓通过 **CI 在构建期拉取各仓的 spec/文档**自动聚合,而非用脆弱的 Git submodule 手动同步。

核心抓手四件事,缺一不可:
1. **接口契约是单一事实来源(Single Source of Truth)**——OpenAPI/proto 先行(design-first),代码由 spec 生成桩,而非反过来。
2. **架构文档分层级落地**——C4 的 System Context / Container 级放中央仓,Component 级放服务仓;ADR 按作用域分仓存放。
3. **一个聚合门户**——3 个服务规模建议 MkDocs Material + Redocly/Redoc 起步;若看重服务目录和未来扩展,选 Backstage。
4. **防漂移靠自动化**——spec lint、契约测试(Pact)、文档进入「Definition of Done」、CI 在 spec 变更时自动重建聚合文档。

---

## 1. 核心决策:文档到底「住在哪里」?—— 4 种文档拓扑模式

Fabrizio Ferri Benedetti 在 *Docs-as-code topologies* 中把跨仓文档组织方式归纳为四种,这是选择策略的基础框架 [(passo.uno)](https://passo.uno/docs-as-code-topologies/):

| 拓扑模式 | 结构 | 优点 | 缺点 | 适用场景 |
|---|---|---|---|---|
| **Sidecar(随代码仓)** | 文档(Markdown)与代码同仓 | 随代码版本化、原子提交;工程师自然维护;起步最简单 | 文档易被视为「附件」;与代码发版节奏耦合时可能卡 pipeline | 早期项目、内部开发文档、参考/生成型文档 |
| **Orthogonal(完全分离)** | 官方文档独占一个仓,与代码仓几乎无联系 | 文档有独立身份、写作者完全掌控 | 与开发者脱节;内容重复;用户困惑该看哪个 | 通常只是过渡态,作者认为几乎不可取 |
| **Federated(联邦式)** | 文档分散在多个代码仓,中央仓**拉取**各仓内容拼成统一站点 | 适合「同一伞下多个自治项目」;团队自治 | 难维护;基于 git submodule 的网络「过度脆弱」 | 多个半独立项目 |
| **Specialized(专业化分工)**★ | 中央仓放概念/架构/教程;代码仓产出强耦合内容(API ref、配置),中央站点在构建/运行期**按需拉取** | 真正的劳动分工;站点「从最新鲜处取数据」;避开 submodule 脆弱性;随组织平滑扩展 | 需要成熟的自动化文化与协作信任 | **复杂产品、成熟工程+编辑文化** |

**对多仓微服务,作者明确推荐 Specialized 模式**:每个微服务仓生成自己的 API reference 和配置文档(与代码深度耦合),中央仓负责架构指南、onboarding、跨服务的概念性内容;中央站点通过 CI/CD 拉取**已生成的产物(JSON/YAML)**,而不是挂载整个内容树,从而避开 git submodule 的脆弱性 [(passo.uno)](https://passo.uno/docs-as-code-topologies/)。

> 关键洞察:不要让中央仓去 mount 各仓的源码树( submodule 路线 ),而要让各仓在 CI 里**产出标准化的数据文件**(spec、生成的 Markdown),中央仓只消费这些产物。这是「随代码」与「集中治理」的优雅平衡。

---

## 2. 真实案例:Grab 从「分布式 docs-as-code」演进到「中央仓 + 拉取同步」

Grab 工程团队的实践是这个问题的最佳参照样本 [(Grab Engineering, 2025)](https://engineering.grab.com/evolving-documentation-strategy):

- **阶段一(2021,分布式 docs-as-code)**:文档作为 Markdown 存在每个团队的服务仓里,与代码共用 Git/MR/CI 流程。收益:单一事实来源、文档不再是「事后补充」、可与代码同 PR 审查、可做 link 校验/style lint/preview build 等自动检查。
- **阶段二(~4 年后,转向中央仓)**:所有文档收拢进**一个中央仓**,仍保持 Markdown + docs-as-code,但叠加统一治理、模板、发现能力。

**驱动转向的痛点(正是多仓场景迟早会遇到的)**:
- **碎片化体验**:信息架构、术语、粒度在各仓间逐渐分叉。
- **标准不齐**:不同仓 lint/CI 约定不一致,组织级自动化「不可靠」。
- **可发现性衰退**:团队迁移源码仓却不通知文档负责团队,追踪断裂。
- **AI 就绪**:文档不再只写给人类看,集中、干净的 Markdown 是内部 AI agent 的知识库。

**他们最终采用「中央仓 + 自动同步」的混合做法**:过渡期对关键服务/平台仓做**自动同步**进中央 hub,并刻意「让重叠期很短,避免出现两个事实来源」。配套:统一 linter、按文档类型强制模板、Glean 驱动的跨文档企业搜索、ownership 元数据。

核心教训:**「目标不是永远选一种模式,而是识别何时该切换」**——文档策略要随组织规模、受众广度、AI 等新需求演进 [(Grab Engineering)](https://engineering.grab.com/evolving-documentation-strategy)。

---

## 3. API 契约 / 接口文档管理(Single Source of Truth)

这是 polyrepo 微服务最关键、也最容易失控的资产。原则:**契约(spec)是源,代码是派生物**。

### 3.1 Design-first(契约先行)

API Design-First(schema-first / contract-first)指**先设计 API 接口、再写任何代码** [(ApisYouWonthHate)](https://apisyouwonthate.com/blog/a-developers-guide-to-api-design-first/)。对微服务尤其有价值:它能并行团队工作、强制一致性、让接口成为可复用资产 [(Swagger / API-First)](https://swagger.io/blog/understanding-the-api-first-approach-to-building-products/) [(F5/NGINX)](https://www.f5.com/company/blog/nginx/benefits-of-api-first-approach-to-building-microservices)。

落地形态:
- **REST** → OpenAPI 3.x(OAS,业界事实标准,机器可读 JSON/YAML) [(Fern, 2026)](https://buildwithfern.com/post/api-design-best-practices-guide)。
- **gRPC** → `.proto` + [Buf](https://buf.build)(lint、breaking change 检测、BSR registry)。proto 同样是 API-first 思路在 RPC 侧的体现 [(Medium, API-first gRPC)](https://www.medium.com/@ankitsingh1583/api-first-design-how-graphql-grpc-openapi-are-redefining-system-boundaries-7e2f800023c3)。
- **事件/消息** → AsyncAPI(对 Kafka/MQ 等事件驱动契约)。

### 3.2 spec 放哪、怎么管

- **每个服务仓持有自己的 spec**(如 `service-a/openapi.yaml`、`service-b/proto/*.proto`)——这是它的对外契约,与实现同仓、同版本。这是 Stack Overflow 社区对「多个微服务共享/管理 spec」的主流答案 [(SO #71583589)](https://stackoverflow.com/questions/71583589/openapi-spec-what-is-the-best-practice-that-multiple-microservices-use-the-sam)。
- **共享的数据模型(DTO/schema)** 单独发到共享库仓,各服务依赖,**「publish once, reuse everywhere」** [(Medium, krpsanthoshkumar)](https://medium.com/@krpsanthoshkumar/streamlining-shared-libraries-and-openapi-specs-publish-once-reuse-everywhere-3afcbe2debeb)。
- **面向消费者的「聚合 spec」**:如果对调用方暴露的是统一 API,可在 CI 中把多个服务的 spec **自动合并(composite/merge)** 成单一机器可读定义——保留各 server URL、去重重叠 schema、可过滤内部端点——再据此统一生成 SDK/文档/portal [(APIMatic, 2022)](https://www.apimatic.io/blog/2022/09/auto-merging-apis-and-microservices-specifications-to-ease-api-integration)。Redocly 的多 spec 配置也走类似聚合路线 [(Redocly)](https://redocly.com/docs-legacy/developer-portal/guides/document-microservices)。
- **集中式 Swagger UI / 网关聚合**:也可通过 API 网关(如 Spring Cloud Gateway + Springdoc)在运行期聚合多个服务的 doc 暴露为单一 UI [(SO #70791231)](https://stackoverflow.com/questions/70791231/centralized-swagger-openapi-ui-for-all-the-different-microservices-on-a-single-s)。

### 3.3 契约测试(防破坏性变更)

spec 是「写下来的契约」,契约测试是「会被执行的契约」。**Consumer-Driven Contract Testing(Pact)**:消费方定义期望,提供方必须满足,从而在 CI 里**提前发现破坏性变更并强制版本化**;契约发布到 **Pact Broker / PactFlow** 集中管理、可做 can-i-deploy 检查 [(Pact docs)](https://docs.pact.io/) [(Senacor)](https://senacor.blog/consumer-driven-contract-testing-in-practice/) [(Dev.to notes)](https://dev.to/muratkeremozcan/my-thoughts-and-notes-about-consumer-driven-contract-testing-11id)。3 个服务规模下契约测试不是必须,但一旦服务间依赖变复杂、或要支持多团队并行,它能极大降低集成回归成本。

---

## 4. 架构文档管理(C4 模型 + ADR)

### 4.1 C4:从「画图」转向「建模」

Simon Brown(C4 作者)对分布式/微服务架构的建议直击痛点:**问题不在 C4 模型,而在规模——一张含 20+ 元素的图就很难读了** [(Simon Brown, dev.to)](https://dev.to/simonbrown/diagramming-distributed-architectures-with-the-c4-model-51cm)。

各级别在微服务下的落点:
- **System Context(系统上下文)**:不受服务数量影响,放**中央仓**(全系统一张)。
- **Container(容器级)**:微服务架构最复杂处——每个独立部署的服务都是一个 container,10/20/100 个服务时单图不可读。做法是**「建模一次,生成多个聚焦视图」**:从同一模型按「单服务 + 其上下游依赖」「单一业务域/bounded context」等维度切出小图。
- **Component(组件级)**:深入单个服务内部,**放该服务仓**。

核心原则:**「定义一次模型 → 存入版本控制 → 生成多个 diagram 视图」**(Structurizr DSL/CLI、Mermaid、PlantUML、Ilograph),图只是模型的视图而非独立产物;模型一改,所有图同步更新。**远离 Confluence 里散落的静态 PNG**,转向「diagrams-as-code / model-first」 [(Simon Brown)](https://dev.to/simonbrown/diagramming-distributed-architectures-with-the-c4-model-51cm) [(Decathlon, Docs as Code)](https://medium.com/decathlondigital/software-architecture-architecture-decision-record-c4-11ceff211baf)。

### 4.2 ADR(架构决策记录):按作用域分仓

- **服务级决策**(只影响本服务的)→ 各服务仓 `docs/adr/`。
- **全局/跨服务决策**(影响整体架构的,如「统一用 gRPC」「统一鉴权方案」)→ **中央仓** `adr/`。
- 模板推荐 MADR 或 Nygard LADR;工具可用 adr-tools / [log4brains](https://github.com/log4brains/log4brains)。AWS 的 Prescriptive Guidance 是建立 ADR 实践的权威参考 [(AWS ADR PDF)](https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/architectural-decision-records/architectural-decision-records.pdf) [(repowise ADR guide)](https://www.repowise.dev/guides/decisions-adr) [(Microservices ADRs on GitHub)](https://github.com/implementing-microservices/ADRs)。

---

## 5. 聚合门户与工具选型(2025/2026 现状)

### 5.1 门户层(MkDocs / Docusaurus / Backstage)

| 工具 | 类型 | 对你的场景的契合度 |
|---|---|---|
| **MkDocs + Material** | Python 静态站点生成器,免费开源 | ★ **3 服务规模的首选起步**:轻量、Markdown、单 `mkdocs.yml`、API ref 用 redoc/swagger 插件嵌入。社区有 `mkdocs-multirepo-plugin`(由 Backstage 维护)**「从多个仓拉取文档构建统一站点」** [(Backstage mkdocs-monorepo-plugin #57)](https://github.com/backstage/mkdocs-monorepo-plugin/issues/57)。 |
| **Docusaurus** | React/MDX 静态站点(Meta),免费开源 | 想要 React 生态、多版本、i18n、Algolia 搜索时选;API ref 配 Redocusaurus/Redoc 插件。无内建交互 console [(Docusaurus)](https://docusaurus.io/docs.html)。 |
| **Backstage** | 开发者门户(Spotify),含服务目录 + TechDocs | ★ **看重「服务目录 + 文档聚合 + 未来扩展」时选**。TechDocs 用 `techdocs-ref` 注解把每个 catalog 实体的文档关联起来,支持 Basic 与 Recommended(集中构建存储)两种部署 [(Backstage TechDocs)](https://backstage.io/docs/features/techdocs/) [(Roadie monorepo guide)](https://roadie.io/blog/backstage-monorepo-guide/)。3 个服务可能「略重」,但作为长期底座值得评估。 |

### 5.2 API 参考与治理工具(Mintlify 2026 盘点) [(Mintlify, 2025/2026)](https://www.mintlify.com/library/best-api-documentation-tools-of-2025)

- **Redoc / Redocly**:免费开源的 API 参考渲染(三栏布局),Redocly 可从 OpenAPI 自动更新文档并做 spec lint/治理 [(Redocly CLI)](https://redocly.com/docs/cli/api-docs)。
- **Swagger UI**:免费,快速发布 OpenAPI + 「Try it out」交互测试。
- **Stoplight**:可视化 API 设计器(免写 YAML)+ style guide + mock server + 治理,适合 design-first 工作流。
- **SwaggerHub**:企业级 API 治理平台,spec 版本/发布环境/团队权限,但「规模上去后成本上升快」。
- **Postman**:统一 API 生命周期(设计/测试/文档),支持 HTTP/GraphQL/gRPC/WebSocket,文档随 collection 自动更新。
- **Mintlify**:从 OpenAPI 生成可编辑 MDX、双向 Git sync、AI agent 自动开 PR 更新文档——适合「快速迭代 + 想要 AI 就绪」的工程团队。

> 选型建议(3 个后端服务、从零、自托管偏好):**MkDocs Material 做概念/架构文档 + Redocly/Redoc 渲染每个服务的 OpenAPI + Spectral 做 spec lint**。这是零授权成本、完全 docs-as-code、可平滑演进到 Backstage 的组合。若团队已用 Postman/SwaggerHub 且不想自建,可直接用其作为 spec 单一事实来源。

---

## 6. 同步与防漂移:让文档不与代码脱节

多仓文档的头号敌人是**漂移(doc-code drift)**。综合 vFunction 与 Grab 的建议 [(vFunction)](https://vfunction.com/blog/guide-on-documenting-microservices/) [(Grab)](https://engineering.grab.com/evolving-documentation-strategy):

1. **Design-first + 生成**:spec 是源,服务端桩与客户端 SDK 由 `openapi-generator`/`buf` 生成,代码与 spec 天然不脱节。
2. **CI gate**:每个服务仓 PR 上跑 `spectral lint`/`buf lint` + `buf breaking`(检测破坏性变更)+ 契约测试(Pact)。
3. **自动聚合发布**:spec 变更触发中央仓 CI 拉取最新 spec、重建 Redoc 页与聚合 spec、重发布站点(Grab 的「自动同步」思路)。
4. **把文档放进 Definition of Done**:功能未更新文档不算完成——vFunction 的头号建议 [(vFunction)](https://vfunction.com/blog/guide-on-documenting-microservices/)。
5. **模板 + linter 统一标准**:中央仓提供文档模板,各仓 CI 强制 lint/markdown lint/link 检查。
6. **ownership 元数据**:每个服务/文档标注负责团队(如 `catalog-info.yaml` / `OWNERS`),解决 Grab 遇到的「迁移不通知」问题。

**关于 Git submodule**:多源明确建议**谨慎**——它给 git 概念模型增加大量复杂性、易出现 detached HEAD、很多开发者主动回避;文档场景更推荐「CI 拉取产物」而非 submodule mount [(passo.uno)](https://passo.uno/docs-as-code-topologies/) [(Level Up 对比)](https://levelup.gitconnected.com/monorepo-vs-multi-repo-vs-git-submodule-vs-git-subtree-a-complete-guide-for-developers-961535aa6d4c)。

---

## 7. 一个可落地的起步蓝图(3 个服务仓)

**仓库结构建议**(新增一个中央仓,共 4 个仓):

```
service-a/                      # 服务仓 A
  openapi.yaml (或 proto/)
  docs/
    README.md        # 服务概览、运行手册(runbook)、依赖、SLA
    adr/             # 仅影响本服务的决策
  catalog-info.yaml  # (可选 Backstage) ownership + techdocs-ref
service-b/                      # 同构
service-c/                      # 同构

docs-portal/                    # ★ 新建:中央文档仓(Specialized 拓扑)
  mkdocs.yml                    # Material 主题 + multirepo/redoc 插件
  docs/
    architecture/
      c4-model.dsl              # System Context + Container 级(唯一模型)
      system-overview.md        # 由模型生成的视图 + 说明
    adr/                        # 全局/跨服务决策
    onboarding.md
    api-index.md                # CI 生成:聚合 3 个服务的 API 入口
  specs/                        # CI 拉取各仓 spec 到此处(不手改)
  .github/workflows/
    aggregate.yml               # 定时/被触发拉 spec、跑 spectral、重建聚合 spec
    build-deploy.yml            # 构建 MkDocs + Redoc,发布到 Pages/S3
```

**CI 协同(防漂移闭环)**:
- 服务仓 push → 发布 `openapi.yaml`/`proto` 为 artifact,或 dispatch 触发 `docs-portal` 的 `aggregate.yml`。
- `docs-portal` CI:拉取 3 个仓最新 spec → `spectral lint` → (可选)合并成 composite spec → 渲染 Redoc 页 + 构建 MkDocs → 部署。
- 架构图:`c4-model.dsl` 改动 → Structurizr/mermaid 生成视图 → 进站。

**最小可行起步(MVP,1~2 天可搭)**:先不要 Backstage。用 **MkDocs Material + Redoc 插件 + 一个 GitHub Action 定时拉 spec**。先把 API ref 聚合起来,再逐步加 C4 模型与 ADR。规模或治理需求增长后,再评估迁移到 Backstage 作为长期底座(Grab 路径的演进)。

---

## 8. 要不要合并成 monorepo?

这是 polyrepo 痛点时常被问到的根因问题。结论:**仅为「文档管理」而合并 monorepo 不划算**。

- 多仓的文档痛点**完全可以用 Specialized 拓扑 + CI 聚合解决**(本报告核心方案),不需要物理合并。
- monorepo 的真正收益在「跨服务原子提交、统一工具链、代码所有权」等工程维度,而非文档;且它带来仓库膨胀、访问控制 all-or-nothing、跨组织难扩展等成本 [(Aviator monorepo guide)](https://www.aviator.co/blog/monorepo-a-hands-on-guide-for-managing-repositories-and-microservices/) [(Level Up 对比)](https://levelup.gitconnected.com/monorepo-vs-multi-repo-vs-git-submodule-vs-git-subtree-a-complete-guide-for-developers-961535aa6d4c)。
- 社区共识:微服务应独立可构建/部署/扩展,**3 个服务多仓管理开销尚可控**;若服务数与团队数持续增长且耦合加深,再重新评估 monorepo [(Reddit r/dotnet 讨论)](https://www.reddit.com/r/dotnet/comments/uaub7x/when_it_comes_to_microservices_do_you_put_each/) [(Harness repo guide)](https://www.harness.io/harness-devops-academy/best-code-repository-for-microservices)。

> 对当前 3 仓场景:保持多仓,新建中央文档仓做聚合,是投入产出比最高的选择。

---

## 关键要点(Key Takeaways)

1. **采用「Specialized 专业化」混合拓扑**:服务级文档随代码放各仓(OpenAPI/proto、runbook、服务级 ADR);跨服务资产放新建的中央仓(C4 模型、全局 ADR、onboarding、聚合 API 目录)。
2. **接口契约是单一事实来源**:OpenAPI/proto 先行(design-first),代码由 spec 生成;共享 DTO 发共享库仓;必要时 CI 合并成 composite spec 供消费方。
3. **架构文档分层**:C4 的 System Context + Container 模型放中央仓(建模一次、生成多视图);Component 级放服务仓;ADR 按作用域分仓。
4. **建聚合门户**:3 服务规模用 **MkDocs Material + Redocly/Redoc** 起步(零授权、docs-as-code);看重目录与长期扩展则评估 **Backstage**。
5. **防漂移靠自动化**:CI 拉取 spec 重建聚合文档 + Spectral/buf lint + (可选)Pact 契约测试 + 文档进 DoD + 模板/linter 统一 + ownership 元数据。
6. **避免 Git submodule** 做文档同步,改用 CI 拉取产物。
7. **别为文档合并 monorepo**:用聚合方案即可解决;除非工程维度另有诉求。

---

## 来源(Sources)

精读(✓)与检索引用:

1. ✓ [From decentralized Docs-as-Code to a centralized repository — Grab Engineering](https://engineering.grab.com/evolving-documentation-strategy) — 多仓微服务文档策略的真实演进,核心案例
2. ✓ [Docs-as-code topologies — Fabrizio Ferri Benedetti (passo.uno)](https://passo.uno/docs-as-code-topologies/) — 跨仓文档 4 种拓扑分类框架
3. ✓ [Diagramming distributed architectures with the C4 model — Simon Brown](https://dev.to/simonbrown/diagramming-distributed-architectures-with-the-c4-model-51cm) — C4 创作者对微服务的建模建议
4. ✓ [The comprehensive guide to documenting microservices — vFunction](https://vfunction.com/blog/guide-on-documenting-microservices/) — 微服务文档分类、结构、防漂移
5. ✓ [Auto-merging APIs and microservices specifications — APIMatic](https://www.apimatic.io/blog/2022/09/auto-merging-apis-and-microservices-specifications-to-ease-api-integration) — composite spec 聚合为单一事实来源
6. ✓ [Best API documentation tools of 2025/2026 — Mintlify](https://www.mintlify.com/library/best-api-documentation-tools-of-2025) — 当前工具全景对比
7. [TechDocs Documentation — Backstage](https://backstage.io/docs/features/techdocs/) — 开发者门户聚合文档的官方方案
8. [mkdocs-monorepo-plugin Issue #57 — Backstage](https://github.com/backstage/mkdocs-monorepo-plugin/issues/57) — mkdocs-multirepo-plugin 从多仓拉取构建统一站点
9. [How to model monorepos in Backstage — Roadie](https://roadie.io/blog/backstage-monorepo-guide/) — TechDocs 多套文档聚合
10. [Architecture Decision Records (AWS Prescriptive Guidance)](https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/architectural-decision-records/architectural-decision-records.pdf) — ADR 实践权威参考
11. [Architecture Decision Records & ADRs — repowise](https://www.repowise.dev/guides/decisions-adr) — ADR 在仓库中的管理
12. [Pact — Consumer-Driven Contract Testing docs](https://docs.pact.io/) — 契约测试工具与 Broker
13. [Consumer-Driven Contract Testing in Practice — Senacor](https://senacor.blog/consumer-driven-contract-testing-in-practice/) — CDC 与 API 版本化治理
14. [A Developer's Guide to API Design-First — APIs You Won't Hate](https://apisyouwonthate.com/blog/a-developers-guide-to-api-design-first/) — design-first/契约先行
15. [Understanding the API-First approach — Swagger](https://swagger.io/blog/understanding-the-api-first-approach-to-building-products/) — API-first 治理与生命周期
16. [Benefits of an API-First approach to microservices — F5/NGINX](https://www.f5.com/company/blog/nginx/benefits-of-api-first-approach-to-building-microservices) — API-first 对微服务的价值
17. [API design best practices guide (2026) — Fern](https://buildwithfern.com/post/api-design-best-practices-guide) — OpenAPI 作为业界标准
18. [Streamlining shared libraries and OpenAPI specs — krpsanthoshkumar (Medium)](https://medium.com/@krpsanthoshkumar/streamlining-shared-libraries-and-openapi-specs-publish-once-reuse-everywhere-3afcbe2debeb) — publish once, reuse everywhere
19. [Centralized Swagger/OpenAPI UI for multiple microservices — Stack Overflow](https://stackoverflow.com/questions/70791231/centralized-swagger-openapi-ui-for-all-the-different-microservices-on-a-single-s) — 网关/UI 聚合方案
20. [Document microservices APIs with the developer portal — Redocly](https://redocly.com/docs-legacy/developer-portal/guides/document-microservices) — 多服务聚合到单一 portal
21. [Monorepo vs Multi-repo vs Submodule vs Subtree — Level Up Git Connected](https://levelup.gitconnected.com/monorepo-vs-multi-repo-vs-git-submodule-vs-git-subtree-a-complete-guide-for-developers-961535aa6d4c) — 仓库策略对比(submodule 成本)
22. [How to choose the right code repository for microservices — Harness](https://www.harness.io/harness-devops-academy/best-code-repository-for-microservices) / [Monorepo hands-on guide — Aviator](https://www.aviator.co/blog/monorepo-a-hands-on-guide-for-managing-repositories-and-microservices/) / [Reddit r/dotnet 多仓讨论](https://www.reddit.com/r/dotnet/comments/uaub7x/when_it_comes_to_microservices_do_you_put_each/) — mono vs multi-repo 权衡

---

## 方法论(Methodology)

- **检索工具**:WebSearch(8 组查询,覆盖:多仓文档策略、拓扑模式、API spec 治理、Backstage 聚合、C4/ADR、契约测试、design-first、工具对比、submodule/monorepo 对比);DDG 脚本在 macOS 不可用,改用平台 WebSearch/WebFetch。
- **精读来源**:7 篇(Grab、passo.uno、Simon Brown、vFunction、APIMatic、Mintlify、Backstage TechDocs)。
- **子问题覆盖**:① 文档住哪(拓扑)② API 契约/spec 单一事实来源 ③ 架构文档(C4/ADR)④ 聚合门户选型 ⑤ 防漂移自动化 ⑥ monorepo 取舍。
- **局限**:AsyncAPI 与 gRPC/proto 治理的具体工具链(Buf BSR)在搜索中以概要覆盖,未单独精读;契约测试(Pact)对 3 服务规模的 ROI 判断基于社区共识而非用户实测。

---

# Part 2 — 面向 Agent 的文档评估(AI 时代增量)

*更新日期:2026-07-25 | 增量来源 9(精读 5)| 置信度:高*

> **前提更新**:文档的第二类、且日益主要的受众是 AI agent。设计目标从「人类可读 + 好看」扩展为「**可发现 / 可解析 / 上下文经济 / 可执行**」。本部分是对 Part 1 方案的增量评估,不推翻既有架构。

## A. 范式转变:四条新设计准则

| 维度 | 给人看 | 给 agent 看 |
|---|---|---|
| **发现 Discovery** | 导航菜单、搜索框 | 约定路径:`/llms.txt`、`/AGENTS.md`、`/sitemap.md`、`/.well-known/` |
| **解析 Structure** | HTML + JS 渲染、折叠面板 | 干净 Markdown 镜像、YAML/JSON spec、`Accept: text/markdown` 内容协商、JSON-LD |
| **上下文经济 Context** | 越全越好 | 模块化、可裁剪、分层摘要、按需检索(避免「instruction 诅咒」) |
| **可执行 Actionability** | 描述性说明 | intent-rich 描述(何时用 / 前置条件 / 状态迁移 / 恢复)+ 工作流编排 |

Vercel 的 *Agent Readability Spec* 把前三块归纳为 **Discovery / Structure / Context** 三要素,并给出可量化打分的检查清单 [(Vercel)](https://vercel.com/kb/guide/agent-readability-spec);Addy Osmani 强调上下文预算与模块化是「智能 spec」的核心 [(Addy Osmani)](https://addyosmani.com/blog/good-spec/)。

## B. 对 Part 1 方案的评估:架构不变,但必须叠加 4 层「agent 表面」

**核心结论(好消息):Part 1 的 Specialized 拓扑——各仓持有源 spec + 中央仓聚合——在 agent 视角下不仅成立,而且更对**。agent 正好需要一个中央聚合点来发现全部服务;Grab 转向中央仓的诱因之一就是「我们不再只写给人类工程师」(AI 就绪) [(Grab)](https://engineering.grab.com/evolving-documentation-strategy)。**无需推翻架构**,只需在现有 4 仓之上叠加四层:

1. **每个服务仓加 `AGENTS.md`(机器版 README)**:setup/build/test/lint 命令、项目结构、代码规范、**三层边界(✅ 默认做 / ⚠️ 先问 / 🚫 绝不)**、PR 规范。AGENTS.md 天然支持嵌套(monorepo/多包),「最近者优先、用户指令最高」[(agents.md)](https://agents.md/) [(GitHub 2500+ 仓分析)](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/)。
2. **中央文档仓对外发 agent 发现面**:`/llms.txt`(策划过的索引,带 `## Optional` 可裁剪段)、`/sitemap.xml` + `/sitemap.md`、每页 Markdown 镜像 + `<link rel=alternate type=text/markdown>` + `Accept: text/markdown` 协商、JSON-LD、语言标注代码块、术语表 [(llmstxt.org)](https://llmstxt.org/) [(Vercel)](https://vercel.com/kb/guide/agent-readability-spec)。
3. **OpenAPI 描述升级为「可执行契约」**:每个端点 `description` 写清「何时用、前置条件、状态迁移、错误恢复、破坏性边界」;补充**跨服务工作流**(有序调用序列);术语全局统一。这是 agent 正确调用 API 的最大单一杠杆 [(LogRocket)](https://blog.logrocket.com/how-write-agent-friendly-api-documentation/)。
4. **(进阶)暴露 MCP server**:让 agent 能程序化查询/发现 API 与目录。Redocly Realm 内建 MCP、Backstage 有官方 `@backstage/plugin-mcp-actions-backend`、Stainless 可从 OpenAPI 生成 MCP [(Redocly Realm)](https://redocly.com/docs/realm/customization/mcp-server) [(Backstage MCP)](https://backstage.io/api/next/modules/_backstage_plugin-mcp-actions-backend.html) [(Stainless)](https://www.stainless.com/mcp/mcp-api-documentation-the-complete-guide/)。**先做只读 MCP**;对 catalog 的写权限要慎之又慎 [(nitin15j)](https://nitin15j.medium.com/turning-backstage-into-an-ai-ready-platform-with-mcp-2412bf744a64)。

## C. 防漂移:agent 表面也要自动化(关键,易被忽视)

`llms.txt` / `AGENTS.md` / Markdown 镜像 / MCP 工具清单**绝不能纯手维护**,否则与代码同样会漂移——而 agent 比人更难发现「过期索引」。把 Part 1 的 CI 聚合管线扩展为:**从 catalog + spec 自动生成** llms.txt、sitemap.md、AGENTS.md 的可注入段落、composite spec、MCP 工具清单。手写部分只保留纯约定(规范、边界) [(Grab 自动同步思路)](https://engineering.grab.com/evolving-documentation-strategy)。

## D. 工具选型在 agent 视角下的微调

| 工具 | 人类视角(Part 1) | agent 视角(关键差异) |
|---|---|---|
| **MkDocs Material** | ★ 起步首选 | Markdown 输出干净;但 llms.txt/markdown 镜像需插件或 CI 生成。3 服务仍可。 |
| **Docusaurus** | 灵活、React | 有社区 `docusaurus-plugin-llms` 自动生成 llms.txt——agent 表面更省事 [(llmstxt.org integrations)](https://llmstxt.org/)。 |
| **Backstage** | 目录+文档,偏重 | ★ **agent 视角性价比提升**:catalog + TechDocs + 官方 MCP 插件 + 可发 llms.txt,是「目录即工具」的最 agent-native 形态。 |
| **Redocly Realm** | API ref 渲染 | 内建 MCP server,API 文档直接暴露给 agent——API 为核心时最强 [(Redocly Realm)](https://redocly.com/docs/realm/customization/mcp-server)。 |

**结论**:若「主要给 agent 看」是硬需求,把 Part 1 的「MkDocs 起步」升级为 **「MkDocs + llms.txt 插件 + 薄 MCP wrapper」作为 MVP**,并把 **Backstage / Realm** 列为**更早**(而非更晚)的演进目标——因为 MCP/catalog 是 agent 原生能力的分水岭。

## E. 3 仓 Agent 化的增量清单(可直接执行)

**各服务仓(service-a/b/c)**:
- [ ] 根目录 `AGENTS.md`(setup/build/test/style/边界/PR,含三层边界)
- [ ] `openapi.yaml` 所有端点 `description` 改写为 intent-rich + 跨服务工作流注释
- [ ] 根目录 `llms.txt`(本服务视角,指向本服务 spec/docs)——LogRocket 建议 per-service 维护 [(LogRocket)](https://blog.logrocket.com/how-write-agent-friendly-api-documentation/)

**中央文档仓(docs-portal)**:
- [ ] CI 生成 `/llms.txt`(全局索引:3 服务 spec 入口 + 架构/onboarding + `## Optional` 可裁剪段)
- [ ] CI 生成 `/sitemap.md`,并保留 `/sitemap.xml`(含 `<lastmod>`)
- [ ] 每页 Markdown 镜像 + `Accept: text/markdown` 协商(MkDocs 原生 `.md` 可直接服务)
- [ ] 根 `AGENTS.md`(系统全局:3 服务关系、跨服务工作流、统一术语表/glossary、各服务 ownership)
- [ ] (进阶)薄 MCP server:tools = `search_docs` / `get_openapi(service)` / `list_services` / `get_workflow(name)`

## Part 2 关键要点(增量)

1. 受众多了一类 agent,设计准则加 4 条:**可发现(约定路径)/ 可解析(Markdown+spec)/ 上下文经济(模块化)/ 可执行(intent-rich 描述 + 工作流)**。
2. **Part 1 架构不变**,只需叠加 4 层 agent 表面:per-repo `AGENTS.md`、portal 的 `llms.txt` + markdown 镜像、intent-rich OpenAPI、(进阶)MCP。
3. agent 表面必须 **CI 自动生成**,否则同样漂移——agent 比人更难察觉过期索引。
4. 「主要给 agent 看」时,Backstage/Realm 的优先级应**前移**(MCP/catalog 是分水岭);MVP 仍可 MkDocs + llms.txt 插件 + 薄 MCP。
5. **OpenAPI 的 `description` 字段从「装饰」变成「执行关键」**——这是提升 agent 调用正确率的最大单一杠杆。

## Part 2 来源(增量)

- [Agent Readability: A Specification for AI-Optimized Websites — Vercel](https://vercel.com/kb/guide/agent-readability-spec) — Discovery/Structure/Context 三要素 + 可打分检查清单(最权威可操作)
- [The /llms.txt file — llmstxt.org (Jeremy Howard)](https://llmstxt.org/) — llms.txt 格式规范、`## Optional` 裁剪语义、`.md` 镜像约定
- [AGENTS.md 官方约定](https://agents.md/) + [How to write a great agents.md — GitHub(2500+ 仓分析)](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/) — AGENTS.md 章节 / 嵌套 / 优先级 / 六要素
- [How to write agent-friendly API documentation — LogRocket](https://blog.logrocket.com/how-write-agent-friendly-api-documentation/) — intent-rich OpenAPI、跨服务工作流、glossary、per-service llms.txt
- [How to Write a Good Spec for AI Agents — Addy Osmani](https://addyosmani.com/blog/good-spec/) — 上下文预算、模块化、三层边界、living spec
- [Turning Backstage into an AI-Ready Platform with MCP — nitin15j](https://nitin15j.medium.com/turning-backstage-into-an-ai-ready-platform-with-mcp-2412bf744a64) + [Backstage 官方 MCP 插件](https://backstage.io/api/next/modules/_backstage_plugin-mcp-actions-backend.html) — catalog 即 MCP 工具(含写权限警示)
- [Redocly Realm MCP server](https://redocly.com/docs/realm/customization/mcp-server) — 内建 MCP 暴露 API 文档
- [MCP API Documentation: The Complete Guide — Stainless](https://www.stainless.com/mcp/mcp-api-documentation-the-complete-guide/) + [Model Context Protocol 官方](https://modelcontextprotocol.io/docs/getting-started/intro) — MCP 作为 agent 与文档/API 的标准桥
- [docusaurus-plugin-llms — llmstxt.org integrations](https://llmstxt.org/) — Docusaurus 自动生成 llms.txt
