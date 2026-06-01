const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const {
  FaSearch, FaFileAlt, FaCubes, FaSitemap, FaBook,
  FaClipboardList, FaLightbulb, FaCog, FaRocket,
  FaCheckCircle, FaArrowRight, FaLayerGroup, FaBrain,
  FaProjectDiagram, FaBalanceScale
} = require("react-icons/fa");

// ═══════════════════════════════════════════════════════════════
// Design System
// ═══════════════════════════════════════════════════════════════
const C = {
  darkBg:   "0F172A", darkBg2:  "1E293B",
  primary:  "0EA5E9", primaryD: "0284C7",
  teal:     "14B8A6", tealD:    "0D9488",
  amber:    "F59E0B", amberL:   "FDE68A",
  white:    "FFFFFF", lightBg:  "F8FAFC", lightBg2: "F1F5F9",
  textDark: "0F172A", textBody: "334155", textMuted:"64748B",
  red:      "EF4444", green:    "10B981", purple:   "8B5CF6",
};

// ── Layout constants (inches) ──
const HDR = { x: 0.7, y: 0.35, w: 8.5, h: 0.5 };       // white-slide header
const SUB = { x: 0.7, y: 0.82, w: 8.5, h: 0.35 };       // white-slide subtitle
const ICON_CIRCLE = { x: 8.5, y: 0.2, w: 0.85, h: 0.85 }; // icon circle
const ICON_IMG = { x: 8.6, y: 0.3, w: 0.65, h: 0.65 };   // icon inside circle
const ACCENT_BAR = { x: 0, y: 0, w: 0.08, h: 5.625 };     // left accent bar
const FOOTER_BAR = { x: 0.7, y: 4.7, w: 8.5, h: 0.45 };
const FOOTER_BAR2 = { x: 0.7, y: 5.05, w: 8.5, h: 0.35 };

const DARK_HDR = { x: 0.8, y: 0.35, w: 8.4, h: 0.7 };
const DARK_SUB = { x: 0.8, y: 0.95, w: 8.4, h: 0.4 };

const cardShadow = () => ({ type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.08 });

// ═══════════════════════════════════════════════════════════════
// Icon rendering
// ═══════════════════════════════════════════════════════════════
function render(comp, color, size = 256) {
  return ReactDOMServer.renderToStaticMarkup(React.createElement(comp, { color, size: String(size) }));
}
async function png(comp, color, size = 256) {
  return "image/png;base64," + (await sharp(Buffer.from(render(comp, color, size))).png().toBuffer()).toString("base64");
}

// ═══════════════════════════════════════════════════════════════
// Slide builders
// ═══════════════════════════════════════════════════════════════

// White slide header (title + subtitle + icon + left accent bar)
function whiteHeader(slide, title, subtitle, color, iconName) {
  slide.background = { color: C.white };
  slide.addShape("rect", { ...ACCENT_BAR, fill: { color } });
  slide.addText(title, { ...HDR, fontSize: 26, fontFace: "Georgia", color: C.textDark, bold: true, margin: 0 });
  slide.addText(subtitle, { ...SUB, fontSize: 14, fontFace: "Calibri", color, margin: 0 });
  slide.addShape("oval", { ...ICON_CIRCLE, fill: { color, transparency: 88 } });
  return ICON_IMG;
}

// Dark slide header
function darkHeader(slide, title, subtitle) {
  slide.background = { color: C.darkBg };
  slide.addShape("oval", { x: 7.8, y: 0.1, w: 2.0, h: 2.0, fill: { color: C.primary, transparency: 85 } });
  slide.addShape("oval", { x: 8.3, y: 0.35, w: 1.5, h: 1.5, fill: { color: C.teal, transparency: 80 } });
  slide.addShape("oval", { x: 0.2, y: 4.4, w: 1.2, h: 1.2, fill: { color: C.primaryD, transparency: 88 } });
  slide.addText(title, { ...DARK_HDR, fontSize: 32, fontFace: "Georgia", color: C.white, bold: true, margin: 0 });
  slide.addText(subtitle, { ...DARK_SUB, fontSize: 14, fontFace: "Calibri", color: C.textMuted, margin: 0 });
}

// Output bar at bottom of slide
function outputBar(slide, text, color) {
  slide.addShape("rect", { ...FOOTER_BAR, fill: { color: C.lightBg2 } });
  slide.addText(text, { x: 0.85, y: 4.7, w: 8.2, h: 0.45, fontSize: 12, fontFace: "Consolas", color, valign: "middle", margin: 0 });
}
function outputBar2(slide, text, color) {
  slide.addShape("rect", { ...FOOTER_BAR2, fill: { color: C.lightBg2 } });
  slide.addText(text, { x: 0.85, y: 5.05, w: 8.2, h: 0.35, fontSize: 11, fontFace: "Consolas", color, valign: "middle", margin: 0 });
}

// Research insight bar (bottom callout)
function researchBar(slide, lines) {
  slide.addShape("rect", { x: 0.7, y: 4.7, w: 8.5, h: 0.55, fill: { color: C.lightBg2 } });
  slide.addText(lines, { x: 0.9, y: 4.72, w: 8.1, h: 0.5, margin: 0 });
}

// ═══════════════════════════════════════════════════════════════
// Build Presentation
// ═══════════════════════════════════════════════════════════════
async function build() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "aidoc";
  pres.title = "aidoc 智能文档体系";

  // Pre-render all icons
  const I = {};
  for (const [k, comp, col] of [
    ["search",FaSearch,C.primary],["file",FaFileAlt,C.teal],["cubes",FaCubes,C.purple],
    ["sitemap",FaSitemap,C.primary],["book",FaBook,C.teal],["clip",FaClipboardList,C.amber],
    ["bulb",FaLightbulb,C.green],["cog",FaCog,C.primary],["rocket",FaRocket,C.primary],
    ["check",FaCheckCircle,C.green],["arrow",FaArrowRight,C.primary],["layer",FaLayerGroup,C.primary],
    ["brain",FaBrain,C.purple],["diagram",FaProjectDiagram,C.teal],["balance",FaBalanceScale,C.amber],
    ["searchW",FaSearch,C.white],["fileW",FaFileAlt,C.white],["cubesW",FaCubes,C.white],
    ["sitemapW",FaSitemap,C.white],["bookW",FaBook,C.white],["bulbW",FaLightbulb,C.white],
    ["clipW",FaClipboardList,C.white],["cogW",FaCog,C.white],["rocketW",FaRocket,C.white],
    ["brainW",FaBrain,C.white],["diagramW",FaProjectDiagram,C.white],["balanceW",FaBalanceScale,C.white],
  ]) I[k] = await png(comp, "#"+col, 256);

  const icon = (s,n,x,y,w,h) => { if(I[n]) s.addImage({data:I[n],x,y,w,h}); };

  // ──────────────── S1: Title ────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape("oval", { x: 7.8, y: 0.1, w: 2.0, h: 2.0, fill: { color: C.primary, transparency: 85 } });
    s.addShape("oval", { x: 8.3, y: 0.35, w: 1.5, h: 1.5, fill: { color: C.teal, transparency: 80 } });
    s.addShape("oval", { x: 0.2, y: 4.4, w: 1.2, h: 1.2, fill: { color: C.primaryD, transparency: 88 } });

    s.addText("aidoc", { x: 1.2, y: 1.2, w: 7.6, h: 1.2, fontSize: 64, fontFace: "Arial Black", color: C.white, bold: true, margin: 0 });
    s.addText("智能文档体系", { x: 1.2, y: 2.3, w: 7.6, h: 0.8, fontSize: 36, fontFace: "Georgia", color: C.primary, margin: 0 });
    s.addShape("rect", { x: 1.2, y: 3.3, w: 1.5, h: 0.06, fill: { color: C.teal } });
    s.addText("AI 驱动的代码仓文档化 · Progressive Disclosure & JIT Retrieval", {
      x: 1.2, y: 3.6, w: 6.5, h: 0.5, fontSize: 14, fontFace: "Calibri", color: C.textMuted, margin: 0
    });
    s.addShape("rect", { x: 1.2, y: 4.6, w: 2.4, h: 0.5, fill: { color: C.primary, transparency: 80 } });
    s.addText("9 个技能  ·  5 层知识架构", {
      x: 1.2, y: 4.6, w: 2.4, h: 0.5, fontSize: 13, fontFace: "Calibri", color: C.white, align: "center", valign: "middle", margin: 0
    });
  }

  // ──────────────── S2: 什么是 aidoc ────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.white };
    s.addText("什么是 aidoc？", { x: 0.8, y: 0.35, w: 8.4, h: 0.65, fontSize: 32, fontFace: "Georgia", color: C.textDark, bold: true, margin: 0 });
    s.addText("面向 AI 编码助手的代码仓文档化方案。核心理念来自 Anthropic 2025 上下文工程研究：\n用 Progressive Disclosure 将存量代码转化为 AI 可消费的结构化知识，而非把所有信息塞进上下文窗口。", {
      x: 0.8, y: 1.1, w: 8.4, h: 0.7, fontSize: 13, fontFace: "Calibri", color: C.textBody, margin: 0 });

    const cards = [
      { i:"sitemapW", t:"结构化文档", d:"自动生成 AGENTS.md\nARCHITECTURE.md\n代码地图与模块说明\n（matklad 三段式范式）", c:C.primary },
      { i:"bookW", t:"知识管理", d:"ADR 决策记录\n经验库持续积累\n跨模块知识图谱\n（五层知识架构 L0-L4）", c:C.teal },
      { i:"cogW", t:"AI 原生适配", d:"Claude Code 规则加载\n路径作用域智能注入\nHook 自动触发\n（Anthropic 四层加载模型）", c:C.purple },
    ];
    const cy = 2.0, cw = 2.7, ch = 2.4, cg = 0.25;
    cards.forEach((cd,i) => {
      const cx = 0.8 + i*(cw+cg);
      s.addShape("rect", { x:cx, y:cy, w:cw, h:ch, fill:{color:cd.c}, shadow:cardShadow() });
      s.addShape("oval", { x:cx+cw/2-0.35, y:cy+0.3, w:0.7, h:0.7, fill:{color:C.white, transparency:85} });
      icon(s,cd.i, cx+cw/2-0.22, cy+0.38, 0.44,0.44);
      s.addText(cd.t, { x:cx+0.2, y:cy+1.15, w:cw-0.4, h:0.4, fontSize:16, fontFace:"Calibri", color:C.white, bold:true, margin:0 });
      s.addText(cd.d, { x:cx+0.2, y:cy+1.55, w:cw-0.4, h:0.75, fontSize:10.5, fontFace:"Calibri", color:C.white, margin:0, lineSpacingMultiple:1.35 });
    });
    s.addText("理论基础：Anthropic Effective Context Engineering (2025)  ·  Vercel AGENTS.md evals (2026)  ·  Princeton AI Docs 研究", {
      x: 0.8, y: 4.8, w: 8.4, h: 0.35, fontSize: 10.5, fontFace: "Calibri", color: C.textMuted, italic: true, align: "center", margin: 0
    });
  }

  // ──────────────── S3: 核心设计原理 ────────────────
  {
    const s = pres.addSlide();
    const ic = whiteHeader(s, "核心设计原理", "来自 Anthropic、Vercel、Princeton 等研究的方法论基础", C.purple, "");
    icon(s, "brain", ic.x, ic.y, ic.w, ic.h);

    const principles = [
      { t:"Progressive Disclosure", st:"渐进式披露", d:"不把所有信息塞进上下文窗口。agent 持有轻量标识符（路径、查询、URL），在运行时按需获取数据。入口文件 ≤200 行，详细文档由指针引导读取。", src:"Anthropic, 2025", c:C.primary, i:"brain" },
      { t:"Just-in-Time Retrieval", st:"即时检索", d:"Claude Code 混合模式：CLAUDE.md 预先加载 + glob/grep 原语按需导航。用 Grep 找符号、Glob 找路径、Read 确认，比预加载高效 10 倍。避免 n² attention 导致的 context rot。", src:"Anthropic Context Engineering", c:C.teal, i:"diagram" },
      { t:"Pointer over Copy", st:"指针优于副本", d:"入口文件只放路径引用和一句话说明，不复制详细内容。@-import 语法支持 5 跳递归。what/where 自动生成，why/when 手写。CLAUDE.md 只用一行 @AGENTS.md。", src:"HumanLayer / Julep-AI 实践", c:C.amber, i:"arrow" },
    ];
    principles.forEach((pr, i) => {
      const py = 1.5 + i * 1.3;
      s.addShape("rect", { x:0.7, y:py, w:8.5, h:1.15, fill:{color:C.lightBg}, shadow:cardShadow() });
      s.addShape("rect", { x:0.7, y:py, w:0.06, h:1.15, fill:{color:pr.c} });
      icon(s, pr.i, 0.95, py+0.2, 0.4, 0.4);
      s.addText(pr.t, { x:1.5, y:py+0.08, w:4, h:0.28, fontSize:14, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });
      s.addText(pr.st, { x:1.5, y:py+0.34, w:4, h:0.2, fontSize:10, fontFace:"Calibri", color:pr.c, margin:0 });
      s.addText(pr.d, { x:1.5, y:py+0.58, w:7.4, h:0.5, fontSize:10.5, fontFace:"Calibri", color:C.textBody, margin:0, lineSpacingMultiple:1.3 });
      s.addText(pr.src, { x:8.0, y:py+0.08, w:1.1, h:0.22, fontSize:7.5, fontFace:"Calibri", color:C.textMuted, italic:true, align:"right", margin:0 });
    });
  }

  // ──────────────── S4: 五层知识架构 ────────────────
  {
    const s = pres.addSlide();
    darkHeader(s, "五层知识架构 (L0–L4)", "业界 2025-2026 共识模型 — 从热记忆到知识图谱");

    const layers = [
      { l:"L0", n:"热记忆", f:"AGENTS.md / CLAUDE.md", d:"始终加载，≤200行。基本规则和入口索引", c:C.primary, w:8.4 },
      { l:"L1", n:"领域能力", f:"skills/*/SKILL.md", d:"按需触发，<2000 tokens。可复用的专家工作流", c:C.teal, w:6.8 },
      { l:"L2", n:"决策记录", f:"docs/adr/NNNN-title.md", d:"按需检索，MADR 格式。为什么做这个选择", c:C.amber, w:5.2 },
      { l:"L3", n:"经验库", f:"learnings/*.md", d:"索引引导检索。踩过的坑、调过的参数", c:C.green, w:3.6 },
      { l:"L4", n:"知识图谱", f:"GRAPH.md", d:"文本化关系图。改 A 会影响 B/C/D，因为...", c:C.purple, w:2.0 },
    ];
    const sy = 1.55;
    layers.forEach((ly, i) => {
      const lx = (10 - ly.w)/2, lyY = sy + i*0.76;
      s.addShape("rect", { x:lx, y:lyY, w:ly.w, h:0.62, fill:{color:C.darkBg2} });
      s.addShape("rect", { x:lx, y:lyY, w:0.06, h:0.62, fill:{color:ly.c} });
      s.addText(ly.l, { x:lx+0.15, y:lyY, w:0.45, h:0.62, fontSize:18, fontFace:"Georgia", color:ly.c, bold:true, valign:"middle", margin:0 });
      s.addText(ly.n, { x:lx+0.65, y:lyY+0.04, w:1.4, h:0.25, fontSize:13, fontFace:"Calibri", color:C.white, bold:true, margin:0 });
      s.addText(ly.f, { x:lx+2.0, y:lyY+0.04, w:ly.w-2.5, h:0.25, fontSize:9.5, fontFace:"Consolas", color:ly.c, margin:0 });
      s.addText(ly.d, { x:lx+0.65, y:lyY+0.32, w:ly.w-1.0, h:0.22, fontSize:10, fontFace:"Calibri", color:C.textMuted, margin:0 });
    });
    s.addText("关键发现 (Vercel, 2026)：被动上下文（L0 直接注入）始终优于按需检索 — Agent 不检索率高达 56%", {
      x: 0.8, y: 5.05, w: 8.4, h: 0.35, fontSize: 11, fontFace: "Calibri", color: C.amberL, align: "center", margin: 0
    });
  }

  // ──────────────── S5: 工作流全景 ────────────────
  {
    const s = pres.addSlide();
    darkHeader(s, "工作流全景", "5 阶段渐进式文档合成管线 — 每阶段确认后推进，不跳步不覆盖");

    const phases = [
      { n:"0", t:"代码仓\n探索", sk:"repo-explore", c:C.primary },
      { n:"1", t:"根目录\n文档", sk:"repo-init", c:C.teal },
      { n:"2", t:"模块\n文档", sk:"module-init", c:C.purple },
      { n:"3", t:"架构\n文档", sk:"architecture", c:C.amber },
      { n:"4", t:"知识\n架构", sk:"knowledge-init", c:C.green },
    ];
    const bw=1.7, bh=1.6, bg=0.15, sx=0.45, by=1.75;
    phases.forEach((p,i) => {
      const bx = sx + i*(bw+bg);
      s.addShape("rect", { x:bx, y:by, w:bw, h:bh, fill:{color:C.darkBg2} });
      s.addShape("rect", { x:bx, y:by, w:bw, h:0.06, fill:{color:p.c} });
      s.addText(p.n, { x:bx, y:by+0.15, w:bw, h:0.55, fontSize:36, fontFace:"Georgia", color:p.c, bold:true, align:"center", margin:0 });
      s.addText(p.t, { x:bx+0.1, y:by+0.7, w:bw-0.2, h:0.55, fontSize:13, fontFace:"Calibri", color:C.white, align:"center", margin:0, lineSpacingMultiple:1.2 });
      s.addText(p.sk, { x:bx+0.05, y:by+1.25, w:bw-0.1, h:0.28, fontSize:8, fontFace:"Consolas", color:C.textMuted, align:"center", margin:0 });
      if (i < 4) s.addText("▸", { x:bx+bw+0.02, y:by+0.45, w:0.12, h:0.4, fontSize:14, color:C.textMuted, align:"center", margin:0 });
    });

    const ey = 3.65;
    // Phase 5
    s.addShape("rect", { x:0.45, y:ey, w:3.5, h:0.65, fill:{color:C.darkBg2} });
    s.addShape("rect", { x:0.45, y:ey, w:0.06, h:0.65, fill:{color:C.primary} });
    s.addText("Phase 5: aidoc-adapt-claude", { x:0.7, y:ey, w:3.1, h:0.32, fontSize:14, fontFace:"Calibri", color:C.white, bold:true, margin:0 });
    s.addText("Claude Code 原生适配 | @-import 加载链 | Hook 注册", { x:0.7, y:ey+0.32, w:3.1, h:0.28, fontSize:10, fontFace:"Calibri", color:C.textMuted, margin:0 });
    // Support skills
    [{ t:"aidoc-create-adr", d:"架构决策记录（MADR 格式）" },{ t:"aidoc-learning", d:"经验捕获与技能升级（L3 持续积累）" }].forEach((sk,i)=>{
      const sx2 = 4.2 + i*2.55;
      s.addShape("rect", { x:sx2, y:ey, w:2.4, h:0.65, fill:{color:C.darkBg2} });
      s.addShape("rect", { x:sx2, y:ey, w:0.06, h:0.65, fill:{color:C.amber} });
      s.addText(sk.t, { x:sx2+0.2, y:ey+0.05, w:2.1, h:0.28, fontSize:12, fontFace:"Calibri", color:C.white, bold:true, margin:0 });
      s.addText(sk.d, { x:sx2+0.2, y:ey+0.33, w:2.1, h:0.25, fontSize:9, fontFace:"Calibri", color:C.textMuted, margin:0 });
    });
    // Orchestrator
    s.addShape("rect", { x:2.5, y:4.6, w:5, h:0.55, fill:{color:C.primary, transparency:85} });
    s.addText("aidoc-create — 主流程编排器，一键串联 Phase 0–5", { x:2.5, y:4.6, w:5, h:0.55, fontSize:14, fontFace:"Calibri", color:C.white, align:"center", valign:"middle", margin:0 });
  }

  // ──────────────── S6-S10: Phase Details ────────────────
  const detailSlides = [
    { t:"Phase 0: aidoc-repo-explore", st:"代码仓探索与画像采集 — L0 层数据基础", i:"search", c:C.primary,
      desc:"LLM 自主探索代码仓，采集规模、语言、模块、构建、测试、CI/CD。自动生成的画像数据作为全流程单一数据源。",
      pts:[{h:"代码规模统计",d:"tokei/cloc 统计各语言行数、文件数、占比"},
           {h:"模块结构分析",d:"识别根模块与叶子模块，判定 service/library/adapter 类型"},
           {h:"构建系统检测",d:"扫描 pom.xml/go.mod/package.json，推断构建命令"},
           {h:"测试框架识别",d:"检测 JUnit/pytest/jest 等框架和测试目录"},
           {h:"CI/CD 与规范",d:"解析 GitHub Actions/GitLab CI，分析 commit 规范"}],
      out:"→ .aidoc/phase0/repo-profile.md" },
    { t:"Phase 1: aidoc-repo-init", st:"根目录 AGENTS.md 生成 — L0 热记忆层（≤150 行）", i:"file", c:C.teal,
      desc:"基于画像数据生成根 AGENTS.md。遵循 Anthropic ≤200 行约束和信息密度排序（Quickstart 30% > Repo Layout 25% > How to Change 15% > ...）。",
      pts:[{h:"项目概览",d:"从 README + 画像数据提取定位（30% 篇幅）"},
           {h:"构建与测试命令",d:"自动采集构建/测试命令（25% 篇幅，最高优先级）"},
           {h:"代码风格指南",d:"检测 lint/formatter 配置（15% 篇幅）"},
           {h:"仓库结构图",d:"目录树 + 模块依赖关系（15% 篇幅）"},
           {h:"注意事项/坑点",d:"自动检测约束 + HUMAN_REVIEW 占位（10% 篇幅）"}],
      out:"→ AGENTS.md（根目录，≤150 行）" },
    { t:"Phase 2: aidoc-module-init", st:"子模块 AGENTS.md 批量生成 — L0 模块热记忆层", i:"cubes", c:C.purple,
      desc:"通过子代理并行为每个叶子模块生成 AGENTS.md。遵循\"最近优先\"嵌套语义，不重复根文档内容。",
      pts:[{h:"批量确认职责",d:"一次性展示所有模块清单，支持编辑/跳过"},
           {h:"子代理并行生成",d:"每个模块独立子代理，并发执行"},
           {h:"重复模式检测",d:"识别 controller/service/repo 等模式，批量处理"},
           {h:"约定自动提取",d:"错误处理、命名约定、分层架构自动识别"},
           {h:"遵循嵌套语义",d:"只写本子树独有内容，不复制父级 AGENTS.md"}],
      out:"→ <module>/AGENTS.md × N（每个 30-50 行）" },
    { t:"Phase 3: aidoc-architecture", st:"架构文档 — matklad 三段式范式（Bird's-eye → Code map → Cross-cutting）", i:"sitemap", c:C.primary,
      desc:"使用 matklad 三段式格式生成架构文档。\"在哪里改\"比\"怎么改\"重要 5 倍 — 代码地图是第一公民。",
      pts:[{h:"鸟瞰视图",d:"2-3 句说明项目做什么、用户是谁"},
           {h:"代码地图",d:"每个模块 2-5 句：入口文件、关键导出、架构角色"},
           {h:"横切关注点",d:"错误处理、可观测性、测试策略、构建部署"},
           {h:"关键约束",d:"不直接链接文件（防失效）· ≤300 行"},
           {h:"智能标注",d:"[✓ 自动] / [~ 推断] / [? 待审核]"}],
      out:"→ docs/ARCHITECTURE.md（≤300 行）" },
    { t:"Phase 4: aidoc-knowledge-init", st:"知识架构骨架 — 对应五层架构的 L1+L2+L3 层", i:"book", c:C.teal,
      desc:"构建四维知识目录：L1 领域能力（skills/）、L2 决策记录（adr/）、L3 经验库（learnings/）、知识库（knowledge/）。",
      pts:[{h:"领域能力 L1",d:"docs/skills/ — 封装 scripts/Makefile 的可复用操作"},
           {h:"决策记录 L2",d:"docs/adr/ — 检测并生成 MADR 格式架构决策"},
           {h:"经验库 L3",d:"docs/learnings/ — LEARNINGS+ERRORS+FEATURE_REQUESTS"},
           {h:"知识文章",d:"docs/knowledge/ — 跨模块深层知识（错误处理/测试/可观测性）"},
           {h:"回写入口索引",d:"将四维索引写回根 AGENTS.md，确保 AI 可发现"}],
      out:"→ docs/skills/ + docs/adr/ + docs/learnings/ + docs/knowledge/" },
  ];

  for (const ds of detailSlides) {
    const s = pres.addSlide();
    const icp = whiteHeader(s, ds.t, ds.st, ds.c, "");
    icon(s, ds.i, icp.x, icp.y, icp.w, icp.h);
    s.addText(ds.desc, { x:0.7, y:1.3, w:8.5, h:0.4, fontSize:12, fontFace:"Calibri", color:C.textBody, margin:0 });

    const psy=1.85, pw=2.95, ph=0.65, pgx=0.17, pgy=0.12;
    ds.pts.forEach((pt,i)=>{
      const col=i>=3?i-3:i, row=i>=3?1:0;
      let px;
      if (i<3) { px=0.7+col*(pw+pgx); }
      else { const r2tw=2*pw+pgx; px=0.7+(8.5-r2tw)/2+col*(pw+pgx); }
      const py=psy+row*(ph+pgy);
      s.addShape("rect",{x:px,y:py,w:pw,h:ph,fill:{color:C.lightBg}});
      s.addShape("rect",{x:px,y:py,w:0.05,h:ph,fill:{color:ds.c}});
      s.addText(pt.h,{x:px+0.15,y:py+0.06,w:pw-0.25,h:0.26,fontSize:12,fontFace:"Calibri",color:C.textDark,bold:true,margin:0});
      s.addText(pt.d,{x:px+0.15,y:py+0.32,w:pw-0.25,h:0.28,fontSize:9,fontFace:"Calibri",color:C.textMuted,margin:0});
    });
    outputBar(s, ds.out, ds.c);
  }

  // ──────────────── S11: 方法论选型与文档防腐 ────────────────
  {
    const s = pres.addSlide();
    const icp = whiteHeader(s, "方法论选型与文档防腐", "约定 → 流程 → 组织 三阶梯  +  Docs-as-Code 维护机制", C.amber, "");
    icon(s, "balance", icp.x, icp.y, icp.w, icp.h);

    // ── Left: methodology ladder as stacked tier cards ──
    s.addText("方法论阶梯", { x:0.7, y:1.2, w:4.4, h:0.35, fontSize:15, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });

    const tiers = [
      { l:"L1 约定层", n:"vanilla AGENTS.md", sc:"单文件 ≤200 行，30+ 工具兼容", ct:"< 30 min", ft:"个人 / 原型", c:C.green, w:4.4 },
      { l:"L2 流程层", n:"Aider CONVENTIONS / GitHub Spec-Kit", sc:"constitution + spec + plan + tasks 四件套", ct:"0.5–1 天", ft:"4–10 人 / 新项目", c:C.teal, w:4.4 },
      { l:"L3 组织层", n:"BMAD-METHOD", sc:"角色驱动 Agile 全生命周期，34+ workflow", ct:"1–3 天", ft:"企业 / 强治理", c:C.amber, w:4.4 },
    ];
    tiers.forEach((t, i) => {
      const ty = 1.7 + i * 0.65;
      // Card
      s.addShape("rect", { x:0.7, y:ty, w:t.w, h:0.58, fill:{color:C.lightBg}, shadow:cardShadow() });
      // Left color strip
      s.addShape("rect", { x:0.7, y:ty, w:0.06, h:0.58, fill:{color:t.c} });
      // Tier badge
      s.addShape("rect", { x:0.9, y:ty+0.07, w:0.9, h:0.22, fill:{color:t.c, transparency:85} });
      s.addText(t.l, { x:0.9, y:ty+0.07, w:0.9, h:0.22, fontSize:8, fontFace:"Calibri", color:t.c, bold:true, align:"center", valign:"middle", margin:0 });
      // Name
      s.addText(t.n, { x:1.95, y:ty+0.04, w:3.0, h:0.22, fontSize:11, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });
      // Scope + cost + fit
      s.addText(t.sc + "  |  上手 " + t.ct + "  |  " + t.ft, { x:1.95, y:ty+0.3, w:3.0, h:0.2, fontSize:8, fontFace:"Calibri", color:C.textMuted, margin:0 });
      // Upward arrow between tiers
      if (i < 2) {
        s.addText("▲", { x:0.7+t.w/2-0.15, y:ty+0.56, w:0.3, h:0.12, fontSize:9, color:C.textMuted, align:"center", margin:0 });
      }
    });
    // Small note below
    s.addText("原则：不要跨阶梯升级。轻→重 有 5 个触发点，重→轻 有实战剪枝策略。", {
      x:0.7, y:3.72, w:4.4, h:0.2, fontSize:8.5, fontFace:"Calibri", color:C.textMuted, italic:true, margin:0
    });

    // ── Right: Anti-rot strategies as numbered cards ──
    s.addText("文档防腐核心策略", { x:5.5, y:1.2, w:4.3, h:0.35, fontSize:15, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });
    const antiRot = [
      { n:"①", t:"风格 & 结构检查", d:"Vale + markdownlint-cli2 自动拦截", c:C.primary },
      { n:"②", t:"链接失效检测", d:"lychee 增量 PR 门禁 + 全量定期巡检", c:C.teal },
      { n:"③", t:"周审计 SOP", d:"15 项 checklist：行数/死规则/矛盾/过期", c:C.purple },
      { n:"④", t:"YOU MUST 封顶", d:"每次会话 ≤5 条强调；2 次纠错 → 写规则", c:C.red },
      { n:"⑤", t:"5 大失败模式", d:"Kitchen Sink / Over-Correct / Over-Spec / Trust-Verify Gap / Infinite Explore", c:C.amber },
    ];
    antiRot.forEach((ar, i) => {
      const ay = 1.7 + i * 0.52;
      s.addShape("rect", { x:5.5, y:ay, w:4.2, h:0.46, fill:{color:C.lightBg} });
      s.addShape("oval", { x:5.6, y:ay+0.08, w:0.3, h:0.3, fill:{color:ar.c, transparency:82} });
      s.addText(ar.n, { x:5.6, y:ay+0.08, w:0.3, h:0.3, fontSize:11, fontFace:"Georgia", color:ar.c, bold:true, align:"center", valign:"middle", margin:0 });
      s.addText(ar.t, { x:6.05, y:ay+0.04, w:3.5, h:0.2, fontSize:10.5, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });
      s.addText(ar.d, { x:6.05, y:ay+0.25, w:3.5, h:0.17, fontSize:8.5, fontFace:"Calibri", color:C.textMuted, margin:0 });
    });

    researchBar(s, [
      { text:"关键洞察 (ThoughtWorks Radar, 2026)：", options:{bold:true,fontSize:11,color:C.textDark,breakLine:true}},
      { text:"\"Continue to re-evaluate the need for SDD tooling as models grow more powerful.\" — 重型 SDD 的边际价值随模型能力提升而下降。方法选型当成\"当下能力补丁\"，不是\"永久基础设施\"。轻量起步，按需升级。", options:{fontSize:10,color:C.textMuted}},
    ]);
  }

  // ──────────────── S12: aidoc-create-adr ────────────────
  {
    const s = pres.addSlide();
    const icp = whiteHeader(s, "aidoc-create-adr", "架构决策记录 — MADR 格式 · L2 决策知识层 · AI 可程序化检索", C.amber, "");
    icon(s, "clip", icp.x, icp.y, icp.w, icp.h);

    // ── Left: ADR structure as styled section cards ──
    s.addText("ADR 文档结构", { x:0.7, y:1.25, w:4.2, h:0.4, fontSize:16, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });
    const adrSections = [
      { emoji:"📋",t:"背景上下文",d:"问题陈述、技术约束、业务需求"},
      { emoji:"🎯",t:"决策",d:"所选方案与明确的选型理由"},
      { emoji:"✅",t:"正面后果",d:"POS-NNN 编码，有益成果与优势"},
      { emoji:"⚠️",t:"负面后果",d:"NEG-NNN 编码，权衡与风险"},
      { emoji:"🔄",t:"备选方案",d:"ALT-NNN 编码，描述及放弃理由"},
      { emoji:"🔧",t:"实施注意事项",d:"IMP-NNN 编码，迁移策略与监控"},
    ];
    adrSections.forEach((sec, i) => {
      const sy2 = 1.78 + i * 0.42;
      s.addShape("rect", { x:0.7, y:sy2, w:4.3, h:0.37, fill:{color:C.lightBg} });
      s.addShape("rect", { x:0.7, y:sy2, w:0.05, h:0.37, fill:{color:C.amber} });
      s.addText(sec.emoji + "  " + sec.t, { x:0.88, y:sy2+0.02, w:1.8, h:0.33, fontSize:11, fontFace:"Calibri", color:C.textDark, bold:true, valign:"middle", margin:0 });
      s.addText(sec.d, { x:2.7, y:sy2+0.02, w:2.2, h:0.33, fontSize:9, fontFace:"Calibri", color:C.textMuted, valign:"middle", margin:0 });
    });

    // ── Right: feature cards with icon circles ──
    s.addText("核心特性", { x:5.5, y:1.25, w:4, h:0.4, fontSize:16, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });
    const featIcons = ["clip","layer","arrow","search","check"];
    const features = [
      ["MADR 格式","标准化模板 + YAML frontmatter\nagent 可程序化检索决策"],
      ["前缀编码","POS / NEG / ALT / IMP / REF\n体系化编号，永不失效"],
      ["状态追踪","Proposed → Accepted\n→ Deprecated → Superseded"],
      ["智能检测","从 build tag · DI 框架 · DB 驱动\n自动识别值得记录的决策点"],
      ["幂等安全","已存在则展示 diff\n让用户选择，不静默覆盖"],
    ];
    features.forEach((f, i) => {
      const fy2 = 1.78 + i * 0.62;
      s.addShape("rect", { x:5.5, y:fy2, w:3.9, h:0.56, fill:{color:C.lightBg}, shadow:cardShadow() });
      s.addShape("oval", { x:5.65, y:fy2+0.08, w:0.4, h:0.4, fill:{color:C.amber, transparency:82} });
      icon(s, featIcons[i], 5.72, fy2+0.15, 0.26, 0.26);
      s.addText(f[0], { x:6.2, y:fy2+0.05, w:3.0, h:0.22, fontSize:12, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });
      s.addText(f[1], { x:6.2, y:fy2+0.27, w:3.0, h:0.26, fontSize:8.5, fontFace:"Calibri", color:C.textMuted, margin:0, lineSpacingMultiple:1.25 });
    });

    outputBar2(s, "→ docs/adr/NNNN-title.md  |  命名: adr-0001-数据库选型.md  |  MADR 2.1.2", C.amber);
  }

  // ──────────────── S13: aidoc-learning ────────────────
  {
    const s = pres.addSlide();
    const icp = whiteHeader(s, "aidoc-learning", "持续学习与经验管理 — L3 经验库层 · 自动化知识闭环", C.green, "");
    icon(s, "bulb", icp.x, icp.y, icp.w, icp.h);

    // ── Left: Trigger scenarios grouped in 3×2 grid ──
    s.addText("触发场景", { x:0.7, y:1.25, w:4.4, h:0.35, fontSize:16, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });

    const triggerGroups = [
      { items: [
        { icon:"🔴", t:"命令失败", d:"返回非零退出码或异常" },
        { icon:"🟡", t:"用户纠错", d:"\"不对，应该是...\" / \"实际上...\"" },
        { icon:"🔵", t:"功能请求", d:"用户请求不存在的功能" },
      ]},
      { items: [
        { icon:"🟣", t:"知识过时", d:"Agent 发现知识已过时" },
        { icon:"🟠", t:"外部故障", d:"API 或外部工具失败" },
        { icon:"🟢", t:"最佳实践", d:"为重复任务找到更好方式" },
      ]},
    ];

    triggerGroups.forEach((group, gi) => {
      group.items.forEach((tr, i) => {
        const tx = 0.7 + (gi === 0 ? 0 : 2.25);
        const ty = 1.72 + i * 0.46;
        s.addShape("rect", { x:tx, y:ty, w:2.15, h:0.4, fill:{color:C.lightBg} });
        s.addShape("rect", { x:tx, y:ty, w:0.05, h:0.4, fill:{color:C.green} });
        s.addText(tr.icon + " " + tr.t, { x:tx+0.15, y:ty+0.03, w:1.9, h:0.18, fontSize:10.5, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });
        s.addText(tr.d, { x:tx+0.15, y:ty+0.22, w:1.9, h:0.16, fontSize:8, fontFace:"Calibri", color:C.textMuted, margin:0 });
      });
    });

    // ── Right: file structure with large colored cards ──
    s.addText("三文件结构", { x:5.5, y:1.25, w:4.3, h:0.35, fontSize:16, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });

    const fileCards = [
      { n:"LEARNINGS.md", id:"LRN-YYYYMMDD-XXX", tags:"correction · insight · knowledge_gap · best_practice", c:C.green, ic:"bulbW" },
      { n:"ERRORS.md", id:"ERR-YYYYMMDD-XXX", tags:"命令失败 · 异常堆栈 · 集成错误 · 超时", c:C.red, ic:"searchW" },
      { n:"FEATURE_REQUESTS.md", id:"FEAT-YYYYMMDD-XXX", tags:"用户请求 · 复杂度评估 · 实现建议", c:C.amber, ic:"clipW" },
    ];
    fileCards.forEach((fc, i) => {
      const fy3 = 1.72 + i * 0.78;
      // Card with colored bg
      s.addShape("rect", { x:5.5, y:fy3, w:3.9, h:0.7, fill:{color:C.lightBg}, shadow:cardShadow() });
      // Color header strip
      s.addShape("rect", { x:5.5, y:fy3, w:3.9, h:0.05, fill:{color:fc.c} });
      // Icon badge
      s.addShape("rect", { x:5.65, y:fy3+0.12, w:0.46, h:0.46, fill:{color:fc.c, transparency:85} });
      icon(s, fc.ic, 5.73, fy3+0.2, 0.30, 0.30);
      // Filename + ID
      s.addText(fc.n, { x:6.25, y:fy3+0.07, w:2.0, h:0.24, fontSize:13, fontFace:"Calibri", color:C.textDark, bold:true, margin:0 });
      s.addText(fc.id, { x:8.2, y:fy3+0.09, w:1.1, h:0.2, fontSize:8, fontFace:"Consolas", color:fc.c, align:"right", margin:0 });
      // Tags
      s.addText(fc.tags, { x:6.25, y:fy3+0.34, w:2.6, h:0.28, fontSize:8.5, fontFace:"Calibri", color:C.textMuted, margin:0 });
    });

    // ── Quality gate highlight bar ──
    s.addShape("rect", { x:0.7, y:4.25, w:8.5, h:0.28, fill:{color:C.green, transparency:92} });
    s.addText("⛩  知识质量门禁：可复现？有时效？有上下文？有排他性？    |    升级路径：LEARNINGS → CLAUDE.md/AGENTS.md → Skill 提取", {
      x:0.85, y:4.25, w:8.2, h:0.28, fontSize:10.5, fontFace:"Calibri", color:C.green, bold:true, valign:"middle", margin:0
    });

    researchBar(s, [
      { text:"核心原则 (Vercel/Princeton, 2026)：", options:{bold:true,fontSize:11,color:C.textDark,breakLine:true}},
      { text:"人类审核是经验库的最后闸门 — LLM 自生成的 AGENTS.md 反而降低成功率 2%、增加成本 23%。索引引导检索优于向量 RAG（<500 篇时）。精简 > 详尽：每多 100 行，遵循率降 3-5%。", options:{fontSize:10,color:C.textMuted}},
    ]);
  }

  // ──────────────── S14: Phase 5: aidoc-adapt-claude ────────────────
  {
    const s = pres.addSlide();
    const icp = whiteHeader(s, "Phase 5: aidoc-adapt-claude", "Claude Code 原生适配 — 接通 Anthropic 四层加载模型", C.primary, "");
    icon(s, "cog", icp.x, icp.y, icp.w, icp.h);

    const stps = [
      { n:"01", t:"CLAUDE.md 桥接", d:"创建/追加 @AGENTS.md 入口\n铁律：绝不覆盖已有文件", c:C.primary },
      { n:"02", t:".claude/rules/ 规则", d:"全局 3 个（style/testing/arch）\n模块 ≤15 行 @-import 索引", c:C.teal },
      { n:"03", t:"Skills 软链接", d:"ln -s ../docs/skills .claude/skills\n版本控制真源 → 原生发现", c:C.purple },
      { n:"04", t:"Hook 注册", d:"部署 activator.sh\nUserPromptSubmit 自动触发", c:C.amber },
    ];
    stps.forEach((st,i)=>{
      const sx2=0.7+i*2.32, sy2=1.5;
      s.addShape("rect",{x:sx2,y:sy2,w:2.15,h:2.6,fill:{color:C.lightBg},shadow:cardShadow()});
      s.addShape("oval",{x:sx2+0.7,y:sy2+0.2,w:0.75,h:0.75,fill:{color:st.c,transparency:85}});
      s.addText(st.n,{x:sx2+0.7,y:sy2+0.2,w:0.75,h:0.75,fontSize:22,fontFace:"Georgia",color:st.c,bold:true,align:"center",valign:"middle",margin:0});
      s.addText(st.t,{x:sx2+0.15,y:sy2+1.1,w:1.85,h:0.35,fontSize:14,fontFace:"Calibri",color:C.textDark,bold:true,align:"center",margin:0});
      s.addText(st.d,{x:sx2+0.15,y:sy2+1.5,w:1.85,h:0.9,fontSize:10,fontFace:"Calibri",color:C.textMuted,align:"center",margin:0,lineSpacingMultiple:1.4});
    });

    researchBar(s, [
      { text:"路径作用域加载（Anthropic 四层加载模型第二层）", options:{bold:true,fontSize:12,color:C.textDark,breakLine:true}},
      { text:"global-style.md → paths: [\"**/*.java\", \"**/*.py\"] — 仅编辑源码时加载  |  global-testing.md → paths: [\"**/*Test.java\", \"tests/**\"] — 仅编辑测试时加载  |  architecture.md → paths: [] — 始终加载（架构不变式）", options:{fontSize:10,color:C.textMuted}},
    ]);
  }

  // ──────────────── S15: aidoc-create 主流程 ────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.white };

    s.addText("aidoc-create — 主流程编排器", { x:0.8, y:0.35, w:8.4, h:0.65, fontSize:30, fontFace:"Georgia", color:C.textDark, bold:true, margin:0 });
    s.addText("一键串联 Phase 0–5，交互式确认 + 幂等安全 + 数据驱动", { x:0.8, y:0.95, w:8.4, h:0.35, fontSize:14, fontFace:"Calibri", color:C.textMuted, margin:0 });

    const fw=1.45, fh=1.1, fg=0.12, fsx=0.35, fy=1.7;
    [{p:"0",n:"探索画像",sk:"repo-explore",c:C.primary},{p:"1",n:"根文档",sk:"repo-init",c:C.teal},{p:"2",n:"模块文档",sk:"module-init",c:C.purple},{p:"3",n:"架构文档",sk:"architecture",c:C.amber},{p:"4",n:"知识架构",sk:"knowledge-init",c:C.green},{p:"5",n:"Claude适配",sk:"adapt-claude",c:C.primary}]
    .forEach((fs,i)=>{
      const fx=fsx+i*(fw+fg);
      s.addShape("rect",{x:fx,y:fy,w:fw,h:fh,fill:{color:C.white},shadow:cardShadow()});
      s.addShape("rect",{x:fx,y:fy,w:fw,h:0.05,fill:{color:fs.c}});
      s.addText("Phase "+fs.p,{x:fx,y:fy+0.1,w:fw,h:0.3,fontSize:11,fontFace:"Calibri",color:fs.c,bold:true,align:"center",margin:0});
      s.addText(fs.n,{x:fx,y:fy+0.4,w:fw,h:0.3,fontSize:13,fontFace:"Calibri",color:C.textDark,bold:true,align:"center",margin:0});
      s.addText(fs.sk,{x:fx,y:fy+0.72,w:fw,h:0.25,fontSize:7.5,fontFace:"Consolas",color:C.textMuted,align:"center",margin:0});
      if(i<5) s.addText("▸",{x:fx+fw+0.02,y:fy+0.25,w:0.1,h:0.4,fontSize:12,color:C.textMuted,align:"center",margin:0});
    });

    const kfy=3.1;
    s.addText("核心设计原则",{x:0.8,y:kfy,w:8.4,h:0.35,fontSize:16,fontFace:"Calibri",color:C.textDark,bold:true,margin:0});
    [{i:"layer",t:"阶段化合成",d:"Phase 0→5 渐进式生成，每阶段确认后再推进，不跳步不覆盖"},
     {i:"check",t:"幂等安全",d:"已存在文件展示 diff，用户选择保留/合并/替换，永不静默覆盖"},
     {i:"arrow",t:"数据驱动",d:"Phase 0 画像贯穿全流程，下游直接消费，避免重复采集"}]
    .forEach((kf,i)=>{
      const kx=0.8+i*3.1;
      s.addShape("rect",{x:kx,y:kfy+0.45,w:2.85,h:1.0,fill:{color:C.lightBg},shadow:cardShadow()});
      icon(s,kf.i,kx+0.15,kfy+0.58,0.35,0.35);
      s.addText(kf.t,{x:kx+0.6,y:kfy+0.5,w:2.1,h:0.28,fontSize:13,fontFace:"Calibri",color:C.textDark,bold:true,margin:0});
      s.addText(kf.d,{x:kx+0.15,y:kfy+0.82,w:2.55,h:0.5,fontSize:9.5,fontFace:"Calibri",color:C.textMuted,margin:0,lineSpacingMultiple:1.3});
    });

    s.addShape("rect",{x:0.8,y:4.7,w:8.4,h:0.5,fill:{color:C.primary,transparency:90}});
    s.addText("最终产出：AGENTS.md × N + ARCHITECTURE.md + CLAUDE.md + docs/ + .claude/rules/  |  对应五层架构 L0–L4", {
      x:0.8, y:4.7, w:8.4, h:0.5, fontSize:12, fontFace:"Calibri", color:C.primary, align:"center", valign:"middle", margin:0
    });
  }

  // ──────────────── S16: 总结 ────────────────
  {
    const s = pres.addSlide();
    darkHeader(s, "开始使用", "一句话启动 aidoc 文档化流程");

    s.addShape("rect", { x:1.2, y:1.8, w:7.6, h:1.0, fill:{color:C.darkBg2} });
    s.addText("帮我为代码仓生成结构化文档", { x:1.2, y:1.8, w:7.6, h:1.0, fontSize:22, fontFace:"Georgia", color:C.teal, align:"center", valign:"middle", italic:true, margin:0 });
    s.addText("→ 触发 aidoc-create，自动执行 Phase 0-5 全流程，构建 L0-L4 知识架构", { x:1.2, y:2.85, w:7.6, h:0.3, fontSize:11, fontFace:"Calibri", color:C.textMuted, align:"center", margin:0 });

    [{ cmd:"探索项目结构", sk:"aidoc-repo-explore", d:"快速了解陌生代码仓全貌" },
     { cmd:"创建 ADR", sk:"aidoc-create-adr", d:"记录关键架构决策及理由" },
     { cmd:"记录学习经验", sk:"aidoc-learning", d:"捕获错误/纠正/最佳实践" }]
    .forEach((uc,i)=>{
      const ux=1.2+i*2.65, uy=3.4;
      s.addShape("rect",{x:ux,y:uy,w:2.45,h:0.85,fill:{color:C.darkBg2}});
      s.addShape("rect",{x:ux,y:uy,w:0.05,h:0.85,fill:{color:C.primary}});
      s.addText(uc.cmd,{x:ux+0.15,y:uy+0.08,w:2.15,h:0.28,fontSize:12,fontFace:"Calibri",color:C.white,bold:true,margin:0});
      s.addText(uc.sk,{x:ux+0.15,y:uy+0.36,w:2.15,h:0.2,fontSize:8,fontFace:"Consolas",color:C.primary,margin:0});
      s.addText(uc.d,{x:ux+0.15,y:uy+0.56,w:2.15,h:0.22,fontSize:9,fontFace:"Calibri",color:C.textMuted,margin:0});
    });

    s.addShape("rect",{x:0,y:5.15,w:10,h:0.475,fill:{color:C.primary,transparency:85}});
    s.addText("9 个技能  ·  5 个阶段  ·  5 层知识架构  ·  1 套完整的 AI 文档化方案", { x:0, y:5.15, w:10, h:0.475, fontSize:15, fontFace:"Calibri", color:C.white, align:"center", valign:"middle", margin:0 });
  }

  // ════════════════════════════════════════════════════════════
  const outPath = "/Users/lsy/skills/pptx/aidoc-introduction.pptx";
  await pres.writeFile({ fileName: outPath });
  console.log("✅ Saved: " + outPath);
}
build().catch(err => { console.error(err); process.exit(1); });
