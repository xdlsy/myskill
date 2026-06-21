# 如何系统学习 5G 核心网（5GC）：面向通信工程师的深度研究报告

*生成日期：2026-06-14 ｜ 来源数：30+ ｜ 置信度：高*

> **适用读者**：已有 LTE/EPC、IP 网络基础，希望系统、全面掌握 5G 核心网（架构 + 协议规范 + 实验环境 + 学习路线）的通信网络工程师。

---

## 摘要（Executive Summary）

5G 核心网（5GC）相对 4G EPC 是一次**架构范式的重构**，而非渐进改良。它由三大支柱支撑：**服务化架构（SBA）**、**云原生（Cloud-Native）**、**控制与用户面分离（CUPS）**——网元从"硬件盒子"变成"HTTP/2 + JSON 的微服务"，控制面集中、用户面（UPF）可下沉到边缘。对通信工程师而言，系统学习 5GC 最有效的路径是**"规范驱动 + 动手抓包"双轨并行**：一手抓 3GPP TS 23.501/23.502/29.5xx 等核心规范建立权威认知，一手用 free5GC / Open5GS / OpenAirInterface 搭建开源实验网、用 Wireshark 把 NAS/NGAP/PFCP/GTP/HTTP-SBI 信令"看"明白。本报告整合了架构原理、必读规范、中英文书籍、MOOC、B 站课程、厂商白皮书、开源实验与抓包教程，并给出一条可落地的**四阶段学习路线图**。

---

## 1. 先建立认知框架：5GC"变"在哪里

### 1.1 三大设计支柱

5G 核心网从 3GPP **Release 15**（2017 年 12 月冻结）开始标准化，并在 R16/R17/R18 持续增强。其架构基于三个核心理念（CafeTele，2026）：

- **服务化架构（SBA）**：网元（Network Function, NF）通过基于 **HTTP/2 的 RESTful API** 互相通信，每个 NF 向 **NRF（网络仓储功能）** 注册并被其他 NF 动态发现。SBI 使用 JSON 编码消息。这彻底取代了 4G 时代的点对点 Diameter/S1-AP 接口。
- **云原生（Cloud-Native）**：NF 被设计为容器化微服务，可部署在任何云基础设施上，支持水平扩展、零停机升级，通过 Kubernetes/Helm/Service Mesh 编排。
- **控制/用户面分离（CUPS）**：控制面（SMF、AMF 等）集中部署，用户面（UPF）可分布式下沉到边缘（MEC）。SMF 通过 **N4 接口、PFCP 协议**控制 UPF。

### 1.2 必须记住的网元（NF）与 4G 对照

| 5G NF | 全称 | 职责 | ≈ 4G 对应 |
|---|---|---|---|
| **AMF** | Access & Mobility Management | 终止 N1(NAS)/N2(NGAP)，注册、连接、移动性、安全上下文 | MME（部分） |
| **SMF** | Session Management | PDU 会话建立/修改/释放、IP 地址分配、选 UPF、N4 管理、QoS 流 | MME + SGW/PGW 控制面 |
| **UPF** | User Plane | 数据包路由转发、QoS、移动性锚点、边缘部署 | SGW + PGW 用户面 |
| **UDM** | Unified Data Management | 签约数据、生成 5G-AKA 鉴权向量、SUPI 处理 | HSS |
| **AUSF** | Authentication Server | 5G-AKA / EAP-AKA' 鉴权、生成锚点密钥 | （HSS 内） |
| **PCF** | Policy Control | 策略与计费决策（PCC 规则） | PCRF |
| **NRF** | Network Repository | NF 注册/发现/心跳、OAuth2 令牌 | （无，新增） |
| **NSSF** | Network Slice Selection | 为 UE 选切片、确定 allowed NSSAI | （无，新增） |
| **NEF** | Network Exposure | 能力开放给第三方 AF | （无，新增） |
| **UDR/UDSF** | 数据仓储/无状态存储 | UDM/PCF 的后端数据库；NF 状态外置 | （无，新增） |
| **NWDAF** | Network Data Analytics | AI/ML 网络数据分析（R16+） | （无，新增） |
| **CHF** | Charging | 融合在线/离线计费 | （OCS/OFCS） |

> 设计哲学补充（ShareTechnote）：5GC 的"过度复杂"背后是 **灵活性、可扩展性、虚拟化、自动化、安全性、云原生** 六大目标。网元被拆碎，是为了可按需组合、按切片定制、按云原生方式弹性伸缩。

### 1.3 关键接口（参考点）速查

记住这几条主干即可（ShareTechnote，依据 TS 23.501 §4.2.7）：

- **N1**：UE ↔ AMF，承载 **NAS** 信令（TS 24.501）
- **N2**：(R)AN ↔ AMF，承载 **NGAP**（基于 SCTP）（TS 38.413）
- **N3**：(R)AN ↔ UPF，用户面 **GTP-U**（TS 29.281）
- **N4**：SMF ↔ UPF，控制面 **PFCP**（TS 29.244）
- **N6**：UPF ↔ 数据网络（DN），通常以太网/IP
- **N9**：UPF ↔ UPF（跨切片/漫游）
- 服务化接口（SBI）：**Namf / Nsmf / Nudm / Nnrf / Npcf…**，每个对应 TS 29.5xx 系列的一个 API 规范

### 1.4 一句话理解网络切片

切片用 **S-NSSAI = SST + 可选 SD** 标识。标准 SST 值（TS 23.501 Table 5.15.2.2-1）：**SST=1 eMBB**（增强移动宽带）、**SST=2 URLLC**（超可靠低时延，<1ms）、**SST=3 MIoT**（海量物联网）、**SST=4 V2X**（R16+）、**SST=5 HMTC**（R17+）。NSSF 负责为 UE 选切片。

---

## 2. 把 3GPP 规范用起来（最重要的自学武器）

对工程师而言，**3GPP 规范是唯一权威、零成本、可相伴终身的资料**。养成"遇到细节就查规范"的习惯，比读十本二手书都管用。

### 2.1 必读规范清单（按优先级）

| 规范 | 主题 | 阶段 | 学什么 |
|---|---|---|---|
| **TS 23.501** | 5G 系统架构 | Stage 2 | **第一本必读**。整体架构、所有 NF、参考点、切片、QoS |
| **TS 23.502** | 5G 系统流程 | Stage 2 | 注册、PDU 会话建立、切换、去注册的**信令流程图** |
| **TS 23.503** | 策略与计费控制框架 | Stage 2 | PCC 规则、URSP |
| **TS 29.500 / 29.501** | SBI 技术实现 | Stage 3 | HTTP/2、REST、OpenAPI 如何落地 |
| **TS 29.502~29.520** | 各 NF 服务 API | Stage 3 | Nsmf / Nudm / Nnrf / Npcf… 逐个接口 |
| **TS 29.244** | N4 接口 / PFCP | Stage 3 | SMF↔UPF 的会话建立、QoS、用量上报 |
| **TS 24.501** | NAS（N1） | Stage 3 | UE↔AMF 非接入层信令 |
| **TS 38.413** | NGAP（N2） | Stage 3 | gNB↔AMF 应用层协议 |
| **TS 33.501** | 5G 安全架构 | — | 5G-AKA、密钥层级（K_AUSF…）、SUCI/SUPI 隐私 |

> CafeTele（2026）特别强调三大"地基规范"：TS 23.501（架构）、TS 23.502（流程）、TS 29.5xx 系列（NF API）。先把 23.501 通读一遍建立全局观，再用 23.502 配合流程图"看流程"，遇到接口细节再到 29.5xx 对号入座。

### 2.2 怎么读、怎么查

- **官方入口**：3GPP 规范主页 `3gpp.org/dynareport/23501.htm`，ETSI 提供同内容的免费 PDF（如 `etsi.org` 的 123 501 系列）。完整目录见 `3gpp.org/dynareport/23-series.htm`。
- **理解 Stage 分层**：Stage 1（需求）→ Stage 2（架构/逻辑，如 23.501）→ Stage 3（协议实现细节，如 29.5xx）。学架构读 Stage 2，做开发/抓包读 Stage 3。
- **按 Release 看演进**：R15（基线 SBA、基础切片）→ R16（增强切片、URLLC、工业 IoT）→ R17（NR-Light/RedCap、NTN、定位）→ R18（**5G-Advanced** 起点，AI/ML、NWDAF 增强）→ R19/20/21（持续演进，走向 6G）。
- **配套工作文档**：3GPP SA2 工作组的 TDoc（技术文档）列表能看到规范演进背后的提案讨论。

---

## 3. 系统化学习资源（书籍 + 课程 + 视频）

### 3.1 推荐书籍

**中文**
- **《5G核心网原理与实践》**（清华大学出版社，2023.10）—— 市面上少见的专门讲 5GC 的中文书，结合 TS 23.501，涵盖架构、接口、网元、NGAP/PFCP/HTTP-2/GTP-U 协议。知乎通信好书推荐多次点名。
- **《5G核心网》**（电子工程专辑"现代通信不可不读 7 本书"推荐）—— 对 3GPP 规范深入浅出，适合入门到进阶。

**英文**
- **CafeTele《5G Core Network — SBA, Slicing, VoNR》**（约 400 页）—— 系统覆盖架构、信令、切片、安全、VoNR、漫游、云原生部署，标题即点题 SBA。
- **《The 5G Core: Architecture and Functions Explained》**（Rajarshi Pathak，2026 新版）—— 实战向参考，含 BSS/OSS 集成。
- **《A Network Architect's Guide to 5G》**（O'Reilly）—— 面向网络架构师/规划工程师。
- **Ericsson 官方 5G 技术丛书**（`ericsson.com/en/reports-and-papers/books`）—— 厂商专家执笔，权威。

### 3.2 免费在线教程站（强烈推荐，工程师日常查阅）

- **ShareTechnote 5G**（`sharetechnote.com/html/5G/`）—— 通信圈公认的经典免费教程站，有 5G 整体架构图、AMF/SMF/UPF 逐网元详解、NAS/NGAP 信令、抓包解读，配图极其丰富。**入门首选**。
- **CafeTele 架构长文**（`cafetele.com/articles/article-5g-core-architecture.html`）—— 一篇覆盖 SBA、CUPS、切片、4G/5G 对照、注册流程、UPF 实现（DPDK/VPP/P4/eBPF）的"百科级"技术指南，每个结论都标注 3GPP 规范号。
- **3G4G**（`3g4g.co.uk/5G/`）—— 5G 标准与规范的策展清单。

### 3.3 MOOC / 在线课程

- **Coursera**：
  - *5G Network Fundamentals*（`coursera.org/learn/5g-network-fundamentals`）—— 服务、架构、NR、数据流、安全。
  - *5G Mobile Networks* 三课专项（含 *5G Network Architecture and Protocols*）。
  - *5G for Everyone*（高通出品，零基础友好）。
  - 提示：选 **"Audit"** 可免费看视频。
- **edX**：*Learn 5G*（`edx.org/learn/5g`）与 **CurtinX 5G Networking 职业证书**。
- **中国大学 MOOC**：南京信息职业技术学院《5G通信技术》含 5G 空口、基站、应用场景五大模块（`icourse163.org/course/NJCIT-1468830185`）。
- **Class Central / MOOC-List**：聚合的 5G 课程清单可横向比较。

### 3.4 B 站视频（中文，适合建立直觉）

- *从局部到整体：5G 系统观*（vivo 通信研究院出品）—— 厂商一线视角，系统观强，适合进阶。
- *5GC 典型信令流程*（中国联通出品）—— 运营商视角讲注册/PDU/切换流程，**非常实用**。
- UP 主「计算机与移动通信」（5G 小课堂系列）、「5G漫话」（专讲核心网架构）、「爱浦路 IPLOOK」（UPF 等网元细节、厂商视角）。
- 检索关键词："5G核心网"、"5GC"、"SBA架构"、"AMF SMF UPF"，优先选**系列已完结**的课程。

### 3.5 厂商白皮书（PDF，免费，工程视角）

- **华为**：《5G 核心网 CICD 技术与实践白皮书》；华为人才在线（`e.huawei.com/cn/talent/`）有官方课程。
- **中兴 ZTE**：《5G 核心网技术与挑战专题导读》《5G 核心网创新技术研究及应用探索》（覆盖 SBA、切片、MEC、用户面云化、IPv6）。
- **Red Hat**：*Evolution to a 5G Core*（云原生/容器化部署视角）。
- **5G Americas**：*5G-Advanced Overview* 白皮书（R15→R21 标准时间线）。

---

## 4. 动手实践：用开源核心网搭实验环境

**这是把"知道"变成"真懂"的关键一跃。** 开源 5G 栈让你在自己电脑上跑通注册→PDU 会话→上网全流程。

### 4.1 三大开源实现对比

| 项目 | 语言/许可 | 特点 | 适合 |
|---|---|---|---|
| **free5GC** | Go / Apache 2.0（Linux Foundation） | 纯 3GPP R15，云原生、Docker/K8s 友好；最新 **v4.x**（含并行注册、Quick Setup Script，2025 持续更新，含 eBPF 调度、NEF PFD 管理等新实现） | 想学**云原生部署 + SBI** 的开发者 |
| **Open5GS** | C 语言 | 轻量、易上手；同时支持 4G EPC + 5G SA；基于 **3GPP R17**；2025 年更新至 **v2.7.6** | 想快速**单机跑通**、对照 4G/5G 的工程师 |
| **OpenAirInterface (OAI)** | C/C++ | **RAN + Core 全栈**，可做端到端、CU/DU 切分、RF 仿真；学术/工业用得多 | 想**深入 RAN↔Core 交互**、做研究 |

> 搭配 **UERANSIM**（UE/gNB 模拟器，纯软件）可在没有真实射频硬件的情况下模拟接入，是最省事的"假 RAN"。

### 4.2 推荐入门路径

**路径 A（最快跑通，半天）：Open5GS + UERANSIM，单机/Docker Compose**
- NYU WITEST 实验室 *Exploring the 5G Core Network*（`witestlab.poly.edu/blog/exploring-the-5g-core-network/`）是公认的**最佳端到端动手教程**：单台服务器用 OAI 容器（oai-amf/smf/udm/udr/ausf/nrf/nssf/spgwu）拉起完整核心网，再编译 OAI gNB + UE（RF 仿真模式），全程 `tcpdump`/`tshark` 观察信令——直接把第 5 节的抓包学习一并做了。

**路径 B（云原生进阶，1-2 天）：free5GC + Helm on Kubernetes**
- 官方 `free5gc-helm`（`free5gc.org/guide/7-free5gc-helm/`）步骤明确：
  1. 装 **MicroK8s**（`snap install microk8s --classic --channel=1.28/stable`）+ kubectl + helm；
  2. **关键坑**：Calico CNI 默认不开 IP 转发，需改 `cni.yaml` 加 `container_settings.allow_ip_forwarding: true`，并在 kubelet 参数加 `--allowed-unsafe-sysctls "net.ipv4.ip_forward"`；
  3. 启用插件：`microk8s enable community multus hostpath-storage`；
  4. 建 mongo/cert 的 PersistentVolume；
  5. `helm install -n free5gc free5gc-helm ./free5gc/` + UERANSIM chart；
  6. WebConsole（`<external_ip>:30500`）加用户；
  7. 验证：`kubectl exec ... -- ping -I uesimtun0 8.8.8.8`（走 GTP 隧道）。
- 进阶可参考 Nephio 文档、Medium 多集群 K8s 部署、TelecomHall 视频教程。

### 4.3 资源清单

- free5GC 官网/历史/GitHub Releases/Helm 仓库；Open5GS 官网与 release notes（v2.7.5 2025-03、v2.7.6 2025-07）。
- OAIBOX 5G Lab Manual（OAI 官方配套实验手册）。
- arXiv *Tutorial on Communication between Access Networks and the 5G Core*（学术向，讲 NG-RAN↔5GC、Initial Context Setup）。
- 帕多瓦大学 2025 学位论文 *Comparative Performance Analysis of free5GC and Open5GS*（两平台性能对比，进阶可读）。

---

## 5. 用抓包把协议"看"明白

学核心网最大的误区是"只读不抓"。把一条**注册流程**用 Wireshark 逐包拆开，胜过读十遍流程图。

### 5.1 关键协议栈与对应过滤器

| 协议 | 在哪 | Wireshark 过滤器 | 对应规范 |
|---|---|---|---|
| HTTP/2 + JSON（SBI） | NF↔NF（NRF 等） | `http` / `http2` | TS 29.500 |
| **NRF 心跳** | NF→NRF，每 ~10s PATCH `/nnrf-nfm/v1/nf-instances/{id}` | `http and http.request.uri contains "nnrf-nfm"` | TS 29.510 |
| **PFCP** | SMF↔UPF（N4），Heartbeat Request/Response | `pfcp` | TS 29.244 |
| **NGAP**（SCTP） | gNB↔AMF（N2），NGSetup/InitialUEMessage | `sctp` / `ngap` | TS 38.413 |
| **GTP-U** | RAN↔UPF（N3）、UPF↔UPF（N9） | `gtp` | TS 29.281 |
| **NAS** | UE↔AMF（N1），注册/鉴权/安全模式 | `nas-5gs` | TS 24.501 |

### 5.2 实操：注册流程抓包（以 NYU WITEST 实验为例）

1. 拉起 OAI 核心网后，先 `tcpdump -i demo-oai -c 150 -w core.pcap` 抓 150 包，用 `tshark -Y 'http'` 就能看到 **AUSF/UDM/UDR/SMF/SPGW-U 周期性向 NRF 发 PATCH 心跳**（状态 REGISTERED/UNDISCOVERABLE）——直观理解"NRF 是服务注册中心"。
2. `tshark -Y 'pfcp'` 看到 **SMF↔SPGW-U 的 PFCP Heartbeat**——直观理解"N4 通路保活"。
3. 启动 gNB（`--sa --rfsim`），AMF 日志里 gNB 列表从空变 Connected；`tshark -Y 'sctp'` 看 SCTP 关联建立，`tshark -Y 'ngap' -V` 看 **NGSetupRequest/Response** 全文（含 gNB Global ID、PLMN、PLMN MCC/MNC）。
4. 启动 UE，`tshark -Y 'ngap or http'` 还原 **UE 注册全流程**：InitialUEMessage → 鉴权（AMF↔AUSF↔UDM 的 SBI 调用）→ 安全模式 → 注册接受。
5. 外部 DN ping UE，用 `tshark -T fields -e eth.src -e eth.dst -e ip.len 'icmp'` 看清 **GTP 隧道封装/解封装**：下行包目的 MAC 指向 UPF，UPF 加 GTP 头转给 gNB；上行反之。

### 5.3 学习资源

- *How to Analyze 5G PCAPs in Wireshark*（5G/6G Academy，逐包拆一条真实注册抓包）。
- *Analyzing 5G Signalling with Wireshark*（Mpirical，结构化课程，覆盖 NAS/NGAP/XnAP/F1AP/E1AP/HTTP-2/PFCP/GTP）。
- **free5GC Labs / Lab 5**（`github.com/free5gc/free5GLabs`）—— 配套实验，专门抓 NGAP 看 UE 连接/断开。
- *Open5GS and srsRAN 5G Network Log Analysis*（Nu Radio Concepts，多种场景排障）。
- Wireshark 官方已内置 5G NAS / NGAP / PFCP 解析器，直接拖 `.pcap` 即可。

---

## 6. 进阶主题与前沿演进

- **网络切片**：端到端由 NSSF 选切片，管理面有 CSMF→NSMF→NSSMF 分层（O-RAN）。学习重点是把切片映射到 RAN/Transport/Core 三段的资源隔离。
- **MEC 边缘计算**：靠 CUPS 把 UPF 下沉到边缘节点实现低时延与数据不出场；3GPP 有专门的 edge computing 标准化方向（`3gpp.org/technologies/edge-computing`）。Dell'Oro 报告指出 MEC 节点是 5G-Advanced 核心网市场的关键差异化点。
- **UPF 实现技术**：高性能 UPF 常用 **DPDK、VPP、P4（SmartNIC）、eBPF/XDP**；free5GC 2025 年新增了 *GTP-driven Automatic Scheduling Optimization with eBPF-based Scheduler*。想深入数据面的工程师值得专攻。
- **5G-Advanced 与走向 6G**：
  - **R18** = 5G-Advanced 起点（AI/ML 增强、切片能力开放）；
  - **R19/20** 持续演进，**R21** 起 6G 标准化推进。Ericsson、5G Americas 均有专题。CafeTele 总结："5G 核心网建立的模式与原则将演化为 6G 的基础。"
- **安全**：5G-AKA 密钥层级（K → K_SEAF → K_AMF…）、SUCI 隐私保护、SEPP 跨网漫游安全（N32），详见 **TS 33.501**。

---

## 7. 推荐学习路线图（分阶段）

> 基于你的工程师背景，建议**约 8–12 周**走完，每阶段配合动手。

**阶段 0 · 温故（1 周）**：复盘 4G EPC（MME/SGW/PGW/HSS/PCRF）、Diameter、GTP-C/U、S1-AP。这是理解 5GC"为什么这么改"的锚点。

**阶段 1 · 建立全局观（2 周）**
- 读 CafeTele 架构长文 + ShareTechnote 5G 架构页，背下 **三大支柱 + 全部 NF + N1–N9 主干接口**。
- 通读 **TS 23.501**（Stage 2，先不求甚解，建立目录感）。
- 产出：能徒手画出 5GC 非漫游架构图，标注每个 NF 和主干参考点。

**阶段 2 · 流程与协议（3 周）**
- 读 **TS 23.502** 的注册、PDU 会话建立、切换流程图；遇到接口细节查 **TS 29.5xx / 29.244 / 38.413 / 24.501**。
- 配 B 站《5GC 典型信令流程》（联通）建立直觉。
- 产出：能讲清一次"开机注册→建立 PDU 会话→上网"经过哪些 NF、走哪些协议、每步干什么。

**阶段 3 · 动手 + 抓包（3 周）**
- 路径 A：Open5GS/OAI + UERANSIM 单机跑通（NYU WITEST 教程）。
- 路径 B：free5GC + Helm on K8s 跑通，顺便练云原生。
- 用 Wireshark 抓注册全流程，逐包对照阶段 2 学的协议。
- 产出：一份自己抓的 `.pcap` + 信令流程时序图。

**阶段 4 · 专精与前沿（2+ 周，持续）**
- 选一个深水区：**切片 / MEC / UPF 数据面（DPDK,eBPF） / 安全 / NWDAF**。
- 跟进 5G-Advanced（R18+）与 6G 趋势；持续刷 3GPP 规范版本更新。

---

## Key Takeaways（关键要点）

1. **三大支柱（SBA + 云原生 + CUPS）是一切的钥匙**——理解它们，5GC 90% 的设计决策都能自洽解释。把 4G EPC↔5GC 对照表刻进脑子。
2. **3GPP 规范是最强自学武器**：TS 23.501（架构）+ 23.502（流程）+ 29.5xx（接口 API）是铁三角，零成本、最权威、终身受用。
3. **"读规范 + 抓包"双轨**：ShareTechnote/CafeTele 建立直觉，free5GC/Open5GS/OAI 跑实验，Wireshark 把 NAS/NGAP/PFCP/GTP/HTTP-SBI 信令逐包看清——这是把知识"焊死"的唯一方法。
4. **选对开源栈**：想快速跑通用 Open5GS，想学云原生用 free5GC+Helm，想深挖 RAN↔Core 用 OAI；UERANSIM 是省事的假 RAN。
5. **厂商白皮书补工程视角**：华为/中兴/Red Hat/5G Americas 的免费白皮书能补齐"实际网络怎么部署"的落地经验。
6. **面向未来**：5G-Advanced（R18+）与 6G 正在演进，关注切片开放、MEC、AI/ML（NWDAF）、UPF 数据面加速等方向。

---

## Sources（来源，分类整理）

**架构与原理**
1. [5G System Overview — 3GPP 官方](https://www.3gpp.org/technologies/5g-system-overview) — 官方对 SBA/NF 架构的权威概述
2. [5G Core Architecture: Complete Technical Guide — CafeTele](https://www.cafetele.com/articles/article-5g-core-architecture.html) — 覆盖 R15–18、SBA/CUPS/切片、4G 对比、UPF 实现的百科级长文（2026）
3. [NR Core Network Architecture — ShareTechnote](https://www.sharetechnote.com/html/5G/5G_NetworkArchitecture.html) — 经典免费教程，架构图+全部 NF+全部参考点 N1–N59
4. [The 5G Core Network Demystified — Dell Technologies](https://infohub.delltechnologies.com/p/the-5g-core-network-demystified/) — 概念入门
5. [5G Core Network Architecture Components — NxgConnect](https://www.nxgconnect.com/post/5g-core-network-architecture-components-their-functional-descriptions) — NF 功能描述
6. [5G核心网网络架构及关键技术 — 安全内参](https://www.secrss.com/articles/14219) — 中文，SBA/云原生/能力开放

**3GPP 规范**
7. [TS 23.501 — 5G System Architecture（3GPP）](https://www.3gpp.org/dynareport/23501.htm) — 第一必读规范（Stage 2 架构）
8. [TS 23.501 V16.6.0 — ETSI PDF](https://www.etsi.org/deliver/etsi_ts/123500_123599/123501/16.06.00_60/ts_123501v160600p.pdf)
9. [TS 29.500 — Technical Realization of SBA — ETSI PDF](https://www.etsi.org/deliver/etsi_ts/129500_129599/129500/15.03.00_60/ts_129500v150300p.pdf) — SBI 的 HTTP/2/OpenAPI 实现
10. [3GPP 23-series 规范目录](https://www.3gpp.org/dynareport/23-series.htm) — 全部 Stage 2 规范索引
11. [5G Standards & Specifications — 3G4G](https://www.3g4g.co.uk/5G/5Gtech_0003_Standards.html) — 规范策展清单

**书籍**
12. [2024 通信好书推荐（含《5G核心网原理与实践》清华 2023）— 知乎](https://zhuanlan.zhihu.com/p/693911884)
13. [现代通信不可不读的 7 本好书 — 电子工程专辑](https://www.eet-china.com/mp/a55046.html) — 含《5G核心网》
14. [5G Core Network — SBA, Slicing, VoNR — CafeTele Book](https://www.cafetele.com/5g-core-book/) — 约 400 页系统书
15. [The 5G Core: Architecture and Functions Explained — Rajarshi Pathak (2026)](https://www.rajarshipathak.com/2026/03/My-New-Book-Release-The-5G-Core-Architecture-and-Functions-Explained.html)
16. [A Network Architect's Guide to 5G — O'Reilly](https://www.oreilly.com/library/view/a-network-architects/9780137376834/)
17. [Ericsson 官方 5G 技术丛书](https://www.ericsson.com/en/reports-and-papers/books)

**在线教程与课程**
18. [ShareTechnote 5G（含 SMF 等网元专题）](https://www.sharetechnote.com/html/5G/5G_Core_SMF.html)
19. [5G Network Fundamentals — Coursera](https://www.coursera.org/learn/5g-network-fundamentals)
20. [5G Mobile Networks 专项 — Coursera](https://www.coursera.org/specializations/5g-mobile-networks-technology-architecture-and-protocols)
21. [Learn 5G — edX](https://www.edx.org/learn/5g)
22. [5G通信技术 — 中国大学 MOOC（南京信息职业技术学院）](https://www.icourse163.org/course/NJCIT-1468830185)
23. [5G 核心网架构概述（《5G核心网规划与应用》第二章）— 博客园](https://www.cnblogs.com/jzssuanfa/p/19321694)

**开源实验与部署**
24. [Exploring the 5G Core Network（OAI 端到端实验）— NYU WITEST](https://witestlab.poly.edu/blog/exploring-the-5g-core-network/) — 最佳动手教程
25. [free5gc-helm 官方 K8s 部署指南](https://free5gc.org/guide/7-free5gc-helm/)
26. [free5GC 官网/历史（v4.x）](https://free5gc.org/history/)
27. [Open5GS v2.7.5 Release（2025-03）](https://open5gs.org/open5gs/release/2025/03/30/release-v2.7.5.html)
28. [Free5GC Testbed Deployment with UERANSIM — Nephio Docs](https://docs.nephio.org/docs/guides/user-guides/usecase-user-guides/exercise-1-free5gc/)
29. [OAIBOX 5G Lab Manual](https://oaibox.com/5g-lab-manual/)
30. [Tutorial: Communication between Access Networks and 5G Core — arXiv](https://arxiv.org/pdf/2112.04257)

**抓包与协议分析**
31. [How to Analyze 5G PCAPs in Wireshark — 5G/6G Academy](https://www.5g6gacademy.com/learn/wireshark-5g-pcap-analysis-guide)
32. [Analyzing 5G Signalling with Wireshark — Mpirical](https://www.mpirical.com/courses/5g/analyzing-5g-signalling-with-wireshark)
33. [free5GC Labs Lab5 — NGAP 抓包实验](https://github.com/free5gc/free5GLabs/blob/master/lab5/README.md)
34. [Open5GS and srsRAN 5G Network Log Analysis — Nu Radio Concepts](https://nuradioconcepts.io/2023/12/15/open5gs-and-srsran-5g-network-log-analysis/)

**演进与前沿**
35. [5G-Advanced & the 5G Core Market — Dell'Oro](https://www.delloro.com/5g-advanced-what-does-it-meanfor-the-5g-core-market/)
36. [5G-Advanced Overview（R15→R21 时间线）— 5G Americas PDF](https://www.5gamericas.org/wp-content/uploads/2025/07/5G-Advanced-Overview.pdf)
37. [5G-Advanced — Ericsson](https://www.ericsson.com/en/5g/5g-for-service-providers/5g-advanced)
38. [Edge Computing — 3GPP](https://www.3gpp.org/technologies/edge-computing)

**厂商白皮书（中文）**
39. [《5G核心网技术与挑战专题导读》— ZTE PDF](https://www.zte.com.cn/content/dam/zte-site/res-www-zte-com-cn/mediares/magazine/publication/com_cn/article/202003/cn202003001.pdf)
40. [《5G核心网CICD技术与实践白皮书》— 华为 PDF](https://www-file.huawei.com/-/media/corporate/pdf/news/5gcicd.pdf?la=zh)
41. [Evolution to a 5G Core — Red Hat](https://www.redhat.com/zh-cn/topics/5g-networks/evolution-to-a-5g-core)

---

## Methodology（研究方法）

- **检索策略**：围绕 6 个子问题（架构、3GPP 规范、学习资源、开源实验、抓包/协议、演进前沿），使用 Web 搜索进行 14 组中英文关键词检索，覆盖 3GPP 官方、厂商、学术（arXiv/学位论文）、社区（ShareTechnote/CafeTele/知乎/CSDN/B 站）、MOOC（Coursera/edX/中国大学 MOOC）多类来源。
- **深读验证**：对 4 个最具权威性的来源抓取全文深读——CafeTele 架构长文（确认 R15–18 规范映射、NF 服务定义、切片 SST 值、4G/5G 对照表）、ShareTechnote（确认参考点 N1–N59 全表与设计哲学）、NYU WITEST 端到端实验（确认 OAI 容器、tcpdump/tshark 抓包命令与协议对应关系）、free5GC Helm 指南（确认 MicroK8s/Calico IP 转发/Multus/PV/Helm/UERANSIM/ping 验证的完整步骤）。
- **交叉核验**：网元定义、参考点、规范号、切片 SST 值、开源项目版本号等关键事实均在 ≥2 个独立来源间核对一致。
- **局限说明**：部分中文 B 站 UP 主与具体视频会随时间下架或改名，链接以检索时（2026-06）状态为准；free5GC/Open5GS 版本号更新较快，建议直接访问其官网/GitHub 取最新 release。认证（HCIA-5G 等）内容未作为主轴（用户选择"系统全面学习"而非"应试导向"），仅在认证课程资源处简要提及。

