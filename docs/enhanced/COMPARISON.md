# AI-DLC vs AI-DLC Optimized vs Harness Engineering

> Objective Comparative Analysis across the full scope of AI-native software development.

**Author:** Kwangyoung Kim (<blackdog0403@gmail.com>)
**Last updated:** 2026-04-21

> [!NOTE]
> **Key Takeaways**
>
> - This document is a **3-party qualitative comparison** of **AI-DLC**, **AI-DLC Optimized (April 2026 revision)**, and **Harness Engineering (HE)** across the full scope of AI-native software development.
> - **AI-DLC and HE are deep in completely opposite areas** — AI-DLC owns Planning & Human-AI Collaboration, HE owns Implementation / Verification / Operations runtime, and each is essentially blank where the other is deep.
> - **AI-DLC Optimized absorbs strengths from both sides** — it adds Construction-time feedback loops, multi-agent patterns, context engineering, cost optimization, and entropy management, while retaining AI-DLC's Inception and Human-AI Collaboration depth.
> - **New in the April 2026 revision**: a **Host Capability Layer** that detects the IDE/CLI (Claude Code / Kiro IDE / Kiro CLI / Amazon Q IDE / Cursor / Cline / Copilot) and degrades multi-agent/parallel patterns gracefully; and a **Project Mode Layer** (Prototyping / Production / Hybrid) that lets the user pick gate density once for Greenfield projects.
> - **Remaining gap** is OS-level infrastructure (true bubblewrap/seatbelt sandboxing, 2-layer prompt injection defense) and deployment automation — areas that require platform engineering beyond rule files.
> - **No numeric scores appear in this document.** Coverage is reported qualitatively from direct reading of the source artefacts. There is no public rubric from Anthropic, AWS, or a neutral third party against which to quantify "X/25 coverage" of an AI-native SDLC framework, so numeric aggregation would be author synthesis rather than measurement.

## Table of Contents

- [Reference Documents](#reference-documents)
- [1. Definitions](#1-definitions)
- [2. Coverage Map](#2-coverage-map)
- [3. Domain-by-Domain Coverage (Qualitative)](#3-domain-by-domain-coverage-qualitative)
- [4. Areas Improved by Optimized vs Original](#4-areas-improved-by-optimized-vs-original)
- [5. Areas Still Missing from Optimized (Gap vs HE)](#5-areas-still-missing-from-optimized-gap-vs-he)
- [6. Areas in AI-DLC / Optimized Only (Not in HE)](#6-areas-in-ai-dlc--optimized-only-not-in-he)
- [7. Autonomy & Supervision](#7-autonomy--supervision-what-each-framework-says-about-itself)
- [8. Philosophy Comparison](#8-philosophy-comparison)
- [9. Latest Trends Coverage (April 2026)](#9-latest-trends-coverage-as-of-april-2026)
- [10. Conclusion](#10-conclusion)
- [References](#references)

---

## Reference Documents

- **AI-DLC** — reference implementation: [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) v0.1.8 (30 rule files, 233KB)
- **AI-DLC Optimized** (April 2026 revision) — `aidlc-rules-optimized/` — 40 rule files, ~302KB (AI-DLC + HE enhancements + Capability Layer + Project Mode)
- **Harness Engineering** — Anthropic Engineering Blog corpus + [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips) + [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24)

---

## 1. Definitions

|                     | AI-DLC                             | AI-DLC Optimized                                                                                 | Harness Engineering                                                                  |
|---------------------|------------------------------------|--------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| **Type**            | Process Methodology                | Methodology + Runtime Optimization + **Host-Adaptive Runtime**                                   | Engineering Pattern Catalog                                                          |
| **Scope**           | Entire SDLC                        | Entire SDLC + Agent Runtime + **Host Portability + Mode Selection**                              | Agent Runtime                                                                        |
| **Number of Files** | 30 `.md` files                     | **40 `.md` files (+10)**                                                                         | Conceptual (not rule files)                                                          |
| **Size**            | 233KB                              | **~302KB (+69KB)**                                                                               | —                                                                                    |
| **Philosophy**      | "Workflow adapts to the work"      | Same + "Systems respond to failure" + **"Rules adapt to the host and to the project's purpose"** | "Humans steer. Agents execute."                                                      |
| **Format**          | Executable rule files loaded by AI | Same                                                                                             | Patterns/principles implemented by humans                                            |
| **Knowledge Scope** | awslabs/aidlc-workflows repo       | AI-DLC + HE enhancements + **Anthropic harness-design-long-running-apps (2026-03-24)**           | Anthropic Engineering Blog + Research Blog + Claude Code documentation + whitepapers |

> [!NOTE]
> **HE Scope Definition:** HE in this comparison includes the Anthropic Engineering Blog, Research Blog, Claude Code Power User Tips, and the **entire Anthropic agent engineering knowledge system**. If it exists in Anthropic's official blog but not in the original PDF, it is considered part of HE.

---

## 2. Coverage Map

**Legend:** ✅✅ Deep · ✅ Present · 🟡 Partial · ⚪ Placeholder · ❌ Absent · 🆕 New in Optimized

```text
┌──────────────────────────────┬──────────────┬──────────────┬──────────────────┐
│ Sub-domain                   │ AI-DLC       │ Optimized    │ HE               │
├──────────────────────────────┴──────────────┴──────────────┴──────────────────┤
│ ▼ PLANNING & DESIGN                                                           │
├──────────────────────────────┬──────────────┬──────────────┬──────────────────┤
│ Requirements Analysis        │ ✅✅ Deep     │ ✅✅ Deep     │ ❌ None          │
│ User Stories                 │ ✅✅ Deep     │ ✅✅ Deep     │ ❌ None          │
│ Architecture Design          │ ✅✅ Deep     │ ✅✅ Deep     │ ❌ None          │
│ Workflow Planning            │ ✅✅ Deep     │ ✅✅ Deep     │ ❌ None          │
│ Brownfield Analysis          │ ✅✅ Deep     │ ✅✅ Deep     │ 🟡 Brief         │
│ Adaptive Depth               │ ✅✅ Deep     │ ✅✅ Deep     │ ❌ None          │
│ Project Mode (Proto/Prod)    │ ❌ None      │ 🆕 Deep      │ ❌ None          │
├──────────────────────────────┴──────────────┴──────────────┴──────────────────┤
│ ▼ IMPLEMENTATION                                                              │
├──────────────────────────────┬──────────────┬──────────────┬──────────────────┤
│ Code Generation              │ ✅ Standard  │ ✅✅ Deep     │ ✅✅ Deep         │
│ Multi-Agent Patterns         │ ❌ None      │ ✅✅ Deep     │ ✅✅ Deep         │
│ Context Management           │ 🟡 Partial  │ ✅✅ Deep     │ ✅✅ Deep         │
│ Tool Optimization            │ ❌ None      │ ✅ Medium    │ ✅✅ Deep         │
│ Host Capability Adaptation   │ ❌ None      │ 🆕 Deep      │ 🟡 Claude only  │
├──────────────────────────────┴──────────────┴──────────────┴──────────────────┤
│ ▼ VERIFICATION                                                                │
├──────────────────────────────┬──────────────┬──────────────┬──────────────────┤
│ Automated Feedback (L1-L5)   │ 🟡 L5 only  │ ✅✅ Deep     │ ✅✅ Deep         │
│ Generator-Evaluator          │ ❌ None      │ ✅✅ Deep     │ ✅✅ Deep         │
│ Security / Sandbox           │ 🟡 Code     │ ✅ Medium    │ ✅✅ Deep         │
│ Swiss Cheese Trust           │ 🟡 Multiple │ 🟡 Multiple │ ✅ Partial       │
├──────────────────────────────┴──────────────┴──────────────┴──────────────────┤
│ ▼ OPERATIONS                                                                  │
├──────────────────────────────┬──────────────┬──────────────┬──────────────────┤
│ Entropy Management           │ ⚪ Placehol. │ ✅✅ Deep     │ ✅✅ Deep         │
│ Cost Optimization            │ 🟡 Depth    │ ✅✅ Deep     │ ✅✅ Deep         │
│ Progressive Deletability     │ ❌ None      │ ✅ Medium    │ ✅ Partial       │
│ Deployment                   │ ⚪ Placehol. │ ❌ None      │ ❌ None          │
├──────────────────────────────┴──────────────┴──────────────┴──────────────────┤
│ ▼ HUMAN-AI COLLABORATION                                                      │
├──────────────────────────────┬──────────────┬──────────────┬──────────────────┤
│ Structured Questions         │ ✅✅ Deep     │ ✅✅ Deep     │ ❌ None          │
│ Audit Trail                  │ ✅✅ Deep     │ ✅✅ Deep     │ 🟡 Session      │
│ Approval Flow                │ ✅ Per-Stage │ ✅ Mode+Bnd  │ ✅ Boundary      │
│ Overconfidence Prevention    │ ✅ Deep      │ ✅✅ Dual     │ 🟡 Structural   │
└──────────────────────────────┴──────────────┴──────────────┴──────────────────┘
```

---

## 3. Domain-by-Domain Coverage (Qualitative)

> [!IMPORTANT]
> **On not assigning scores.** Earlier revisions assigned star ratings and summed them to an overall "X/25" score (14.5/25, 21.5/25, 14/25). No public rubric from Anthropic, AWS, or a neutral third party defines what "5/5 Planning coverage" means for an AI-native SDLC framework, so numeric aggregation is author synthesis, not measurement. This section reports coverage qualitatively with pointers to the rule files and blog posts a reader can check.

**Legend:** ✅ Deep · 🟡 Partial · ⚪ Placeholder · ❌ Absent · 🆕 New in Optimized

| Domain                     | AI-DLC                                                                                                    | AI-DLC Optimized                                                                                                      | Harness Engineering                                                                                            |
|----------------------------|-----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| **Planning & Design**      | ✅ **Deep** — 7 Inception stages · adaptive depth · brownfield reverse engineering                         | ✅ **Deep** — AI-DLC + Project Mode gate-density selection                                                             | ❌ **Absent** — Assumes requirements already exist                                                              |
| **Implementation**         | 🟡 **Partial** — Standard code generation · single-agent                                                  | ✅ **Deep** — Multi-agent (3-path capability-branched) · context engineering · tool optimization                       | ✅ **Deep** — Multi-agent · context engineering · tool optimization                                             |
| **Verification**           | 🟡 **Partial** — L5 human approval per stage only                                                         | ✅ **Deep\*** — L1–L4 feedback + Generator-Evaluator · *No OS-level sandbox*                                           | ✅ **Deep** — L1–L5 Ladder · Generator-Evaluator · OS-level sandbox · Auto Mode                                 |
| **Operations**             | ⚪ **Placeholder** — 19-line `operations/operations.md`                                                    | 🟡 **Partial** — Entropy mgmt added (Gardener, AutoDream, Compounding); deployment still absent                       | ✅ **Deep (maintenance)** / ❌ Deployment — Gardener · AutoDream · Progressive Deletability                      |
| **Human-AI Collaboration** | ✅ **Deep** — Parseable question format · verbatim audit · adaptive depth · soft overconfidence prevention | ✅ **Deep** — AI-DLC + structural Generator-Evaluator (soft + hard dual defense)                                       | ❌ **Absent** — Structural Generator-Evaluator only                                                             |
| **Host Portability**       | ❌ **Absent** — Implicit single-agent                                                                      | 🆕 **Deep** — Capability matrix · detection protocol · fallback ladder for Kiro IDE / Kiro CLI / Amazon Q IDE / Cursor / Cline / Copilot | 🟡 **Claude-Code-centric** — OpenAI Codex variant per [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (Lopopolo, 2026-02-11) |
| **Project Mode**           | ❌ **Absent** — Every stage approval is the default                                                        | 🆕 **Deep** — Prototyping / Production / Hybrid gate density, user-selected once                                      | ❌ **Absent** — Same L1–L5 pipeline regardless of project type                                                  |

### Primary Evidence per Domain

- **Planning & Design** — `inception/*.md`; `common/project-mode.md` (Optimized); HE corpus has no requirements stage.
- **Implementation** — `construction/code-generation.md`; `construction/multi-agent-patterns.md` (Optimized); [multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system), [advanced-tool-use](https://www.anthropic.com/engineering/advanced-tool-use).
- **Verification** — `core-workflow.md` ("Wait for Explicit Approval"); `common/automated-feedback-loops.md` (Optimized); [harness-design-long-running-apps](https://www.anthropic.com/engineering/harness-design-long-running-apps), [claude-code-sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing), [claude-code-auto-mode](https://www.anthropic.com/engineering/claude-code-auto-mode).
- **Operations** — `operations/operations.md`; `operations/entropy-management.md` (Optimized); [managed-agents](https://www.anthropic.com/engineering/managed-agents), [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips).
- **Human-AI Collaboration** — `common/question-format-guide.md`, `aidlc-docs/audit.md`, `common/depth-levels.md`, `common/overconfidence-prevention.md`.
- **Host Portability** — `common/agent-capabilities.md` (Optimized); HE has no cross-host portability layer.
- **Project Mode** — `common/project-mode.md` (Optimized).

> [!TIP]
> **Pattern.** AI-DLC and HE are **deep in opposite places**. Optimized stays deep where AI-DLC is deep *and* goes deep where HE is deep. The two layers Optimized adds — **Host Portability** and **Project Mode** — are covered by neither AI-DLC nor HE.

---

## 4. Areas Improved by Optimized vs Original

| Domain                        | AI-DLC Baseline                          | Optimized Change                                       | Added / Modified Files                               | Source Pattern                                |
|-------------------------------|------------------------------------------|--------------------------------------------------------|------------------------------------------------------|-----------------------------------------------|
| **Code Generation**           | Sequential Plan → Generate, single agent | Adds L1–L4 auto-fix loop and mode-aware gate           | `code-generation.md` modified                        | Evaluator-Optimizer, Poka-yoke                |
| **Multi-Agent**               | Absent                                   | Capability-branched 3-path pattern                     | `construction/multi-agent-patterns.md` **rewritten** | 3-Agent, Worktree, /batch, Reasoning Sandwich |
| **Context Management**        | Depth-levels only                        | Knowledge Pyramid, Tool Search                         | `common/context-optimization.md` new                 | Knowledge Pyramid, Tool Search                |
| **Automated Feedback**        | L5 (human approval) only                 | L1–L4 + Auto-Fix added                                 | `common/automated-feedback-loops.md` new             | L1-L5, Auto-Fix, Verification                 |
| **Security**                  | Code-level (OWASP) only                  | Boundary-Based Security, Auto Mode references          | `common/boundary-based-security.md` new              | Auto Mode, Dual Isolation                     |
| **Entropy Management**        | Placeholder                              | Gardener, AutoDream, Compounding Engineering           | `operations/entropy-management.md` new               | Gardener, AutoDream                           |
| **Cost Optimization**         | Depth only                               | Model Routing, Effort Level, Programmatic Tool Calling | `extensions/cost-optimization/` new                  | Model Routing, Effort Level                   |
| **Overconfidence Prevention** | Soft (prompt-level) only                 | Adds structural Generator-Evaluator                    | Generator-Evaluator added                            | Dual defense (soft+hard)                      |
| **🆕 Host Portability**       | Absent                                   | Capability matrix, detection protocol, fallback ladder | `common/agent-capabilities.md` **new**               | Author synthesis (2026-04)                    |
| **🆕 Project Mode**           | Absent                                   | Prototyping / Production / Hybrid gate density         | `common/project-mode.md` **new**                     | Author synthesis (2026-04)                    |

**Unchanged areas:** Planning & Design and Human-AI Collaboration — AI-DLC was already deep on both, so Optimized inherits the Inception stages and common protocols without modification.

---

## 5. Areas Still Missing from Optimized (Gap vs HE)

| Domain                               | HE Level                          | Optimized Level                        | Gap Reason                                      |
|--------------------------------------|-----------------------------------|----------------------------------------|-------------------------------------------------|
| **OS-level Sandbox Implementation**  | ✅ bubblewrap/seatbelt             | ⚠️ Principles + host-fallback guidance | Requires infrastructure outside rule file scope |
| **Prompt Injection 2-Layer Defense** | ✅ Input probe + Output classifier | ❌ Not implemented                      | Infrastructure level                            |
| **Dark Factory (Full Autonomy)**     | ✅ L4+                             | ❌ Intentionally omitted                | Conflicts with human collaboration philosophy   |
| **Swiss Cheese Explicit Principles** | ✅ 5-Layer defined                 | ⚠️ Indirect coverage                   | Partially replaced by Generator-Evaluator       |
| **Deployment Automation**            | ❌ None                            | ❌ None                                 | Both are future areas                           |

---

## 6. Areas in AI-DLC / Optimized Only (Not in HE)

| Domain                                                                         | AI-DLC | Optimized | HE                     |
|--------------------------------------------------------------------------------|--------|-----------|------------------------|
| **Requirements Analysis** (adaptive depth)                                     | ✅      | ✅         | ❌                      |
| **User Stories** (personas, acceptance criteria)                               | ✅      | ✅         | ❌                      |
| **Architecture Design** (components, services)                                 | ✅      | ✅         | ❌                      |
| **Structured Questions** (multiple choice + `[Answer]:`)                       | ✅      | ✅         | ❌                      |
| **Audit Trail** (verbatim human input)                                         | ✅      | ✅         | ⚠️ Session only        |
| **Adaptive Complexity** (Minimal/Standard/Comprehensive)                       | ✅      | ✅         | ❌                      |
| **Brownfield Auto-Analysis** (Reverse Engineering)                             | ✅      | ✅         | ❌                      |
| **Overconfidence Prevention (Soft)** (question-generation philosophy)          | ✅      | ✅         | ❌                      |
| **🆕 Project Mode Selection** (Prototyping / Production / Hybrid)              | ❌      | ✅         | ❌                      |
| **🆕 Host Capability Adaptation** (Kiro IDE / Kiro CLI / Amazon Q IDE / Cursor / Cline / Copilot) | ❌      | ✅         | ⚠️ Claude-Code–centric |

> [!NOTE]
> HE does not address these 10 domains. Focused on agent autonomy on a single host platform, **it neglects human-AI interaction design and cross-host portability**.

---

## 7. Autonomy & Supervision: What Each Framework Says About Itself

There is no canonical public ladder that cleanly ranks all three frameworks on a single autonomy axis. Public references use different taxonomies:

- **Salesforce Agentic Maturity Model** ([Shibani Ahuja, 2025-04](https://www.salesforce.com/news/stories/agentic-maturity-model/)) — a CIO-oriented five-level ladder (Fixed Rules → Information Retrieval → Simple Orchestration → Complex Orchestration → Multi-Agent Orchestration).
- **Anthropic** ([Measuring AI agent autonomy in practice](https://www.anthropic.com/research/measuring-agent-autonomy), 2026-02) — deliberately avoids numbered tiers; uses a continuous 1–10 risk/autonomy score per tool call.
- **AWS AI-DLC** ([aidlc-workflows](https://github.com/awslabs/aidlc-workflows)) and the [AWS AI-DLC whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com/) — describe a 3-phase lifecycle (Inception / Construction / Operations) and do not define autonomy levels.

Because these taxonomies are not interchangeable, this section does not score the three frameworks on a shared axis. Instead it records what each framework explicitly says about its own default human-involvement stance, with a public source for verification:

| Framework               | Self-stated stance on autonomy & supervision (public source)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **AI-DLC**              | Human-in-the-loop by design: "The agent proposes, the human approves." Per-stage human approval on high-stakes decisions (requirements, architecture) is the **intended default**. ([awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows))                                                                                                                                                                                                                                                                                      |
| **AI-DLC Optimized**    | Retains AI-DLC's human approval philosophy but **makes gate density user-selectable per-project** via Project Mode. Prototyping collapses Inception into one approval and removes per-unit Construction gates; Production preserves every gate; Hybrid combines them. Construction runs L1–L4 automated feedback inside whatever gate survives. References Anthropic's three-agent architecture ([harness-design-long-running-apps](https://www.anthropic.com/engineering/harness-design-long-running-apps), 2026-03) and Auto Mode (FPR 0.4%). |
| **Harness Engineering** | Monitor-and-intervene: autonomous execution within pre-defined boundaries, human attention reserved for boundary-crossing events. Anthropic observations: experienced supervisors auto-approve >40%, interrupt ~9%, and agent voluntary stops are ~2x user interrupts. Anthropic measures autonomy on a continuous 1–10 scale rather than fixed levels.                                                                                                                                                                                         |

> [!TIP]
> **Bottom line:** Rather than ranking these frameworks on a single ladder, read each one's **default human-involvement stage** as an explicit design choice. AI-DLC treats Inception as the stage where human approval is the default; HE treats Construction/Operations as the stages where boundary-based autonomy is the default. **AI-DLC Optimized makes that choice explicit and user-controlled** via Project Mode.

---

## 8. Philosophy Comparison

| Dimension               | AI-DLC                     | AI-DLC Optimized                                                 | Harness Engineering                  |
|-------------------------|----------------------------|------------------------------------------------------------------|--------------------------------------|
| **Starting Question**   | "What should we build?"    | "What should we build, on which host, for what purpose?"         | "How do we make agents trustworthy?" |
| **Human Role**          | Co-creator                 | Co-creator (Production) / Supervisor (Prototyping / Hybrid)      | Supervisor                           |
| **Agent Role**          | Assistant                  | **Host-adaptive assistant → autonomous worker (mode-dependent)** | Autonomous worker                    |
| **Failure Prevention**  | Proactive via requirements | **Proactive gates (Production) + reactive loops (Construction)** | Reactive via feedback loops          |
| **Optimization Target** | Decision quality           | **Decision quality × Execution quality × Project-fit**           | Execution quality                    |
| **Host Assumption**     | Implicit (single agent)    | **Explicit detection + fallback**                                | Claude Code implicit                 |

**Optimized's Differentiator:** Retains AI-DLC's "decision quality" philosophy while selectively absorbing HE's "execution quality" patterns — and **adapts both to the host agent and the project's purpose** rather than assuming one environment. **Three-dimensional hybrid** (phase × host × mode).

---

## 9. Latest Trends Coverage (As of April 2026)

| Recent Item                                                                    | AI-DLC | Optimized                                   | HE                                           |
|--------------------------------------------------------------------------------|--------|---------------------------------------------|----------------------------------------------|
| **Auto Mode** (Safety Classifier, FPR 0.4%)                                    | ❌      | ✅ `boundary-based-security.md`              | ✅ Anthropic blog (2026-03)                   |
| **Tool Search** (85% token reduction)                                          | ❌      | ✅ `context-optimization.md`                 | ✅ Anthropic Advanced Tool Use (2025-11)      |
| **Programmatic Tool Calling**                                                  | ❌      | ✅ `cost-optimization.md`                    | ✅ Anthropic Advanced Tool Use (2025-11)      |
| **Worktree + /batch**                                                          | ❌      | ✅ `multi-agent-patterns.md` (with fallback) | ✅ Claude Code Power User Tips                |
| **AutoDream**                                                                  | ❌      | ✅ `entropy-management.md`                   | ✅ Claude Code Power User Tips                |
| **3-Agent Architecture (Planner/Generator/Evaluator)**                         | ❌      | ✅ `multi-agent-patterns.md` Pattern 2       | ✅ harness-design-long-running-apps (2026-03) |
| **Reasoning Sandwich (max-high-max, +12.6pp)**                                 | ❌      | ✅ `multi-agent-patterns.md` Pattern 4       | ✅ LangChain TerminalBench 2.0 (2026-02)      |
| **AGENTS.md Security Vulnerability**                                           | ❌      | ✅ `boundary-based-security.md`              | ❌ Outside HE scope                           |
| **SWE-bench Pro** (Verified replacement)                                       | ❌      | Reflected in reference docs                 | ✅ PDF mentions Verified deprecation          |
| **🆕 Host Capability Adaptation** (Kiro IDE / Kiro CLI / Amazon Q IDE / Cursor / Cline / Copilot) | ❌      | ✅ `agent-capabilities.md`                   | ❌ Claude-Code–only                           |
| **🆕 Project Mode** (Prototyping / Production / Hybrid)                        | ❌      | ✅ `project-mode.md`                         | ❌                                            |

> [!NOTE]
> HE includes the entire Anthropic official blog knowledge system. Auto Mode, Tool Search, Programmatic Tool Calling, Worktree, AutoDream, 3-Agent Architecture, Reasoning Sandwich all originate from Anthropic engineering blogs and are therefore considered part of HE. However, HE does **not** address cross-host portability (Kiro IDE / Kiro CLI / Cursor / etc.) or project-purpose-aware gate density — those are Optimized-only contributions.

---

## 10. Conclusion

### The Complete Picture

```text
╔═══════════════════════════════════════════════════════════════════════════╗
║  AI-Native Development — Qualitative Coverage                             ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║   SDLC Question               │ AI-DLC       │ Optimized  │ HE            ║
║   ────────────────────────────┼──────────────┼────────────┼──────────────  ║
║   What should we build?       │ ✅ Deep       │ ✅ Deep    │ ❌ Absent      ║
║   How should we execute?      │ 🟡 Partial    │ ✅ Deep    │ ✅ Deep        ║
║   How should we verify?       │ 🟡 Partial    │ ✅ Deep*   │ ✅ Deep        ║
║   How should we maintain?     │ ⚪ Placehol.  │ 🟡 Partial │ ✅ Deep (maint)║
║   How should we collaborate?  │ ✅ Deep       │ ✅ Deep    │ ❌ Absent      ║
║   On which host / purpose?    │ ❌ Absent     │ 🆕 Deep    │ 🟡 Claude only║
║                                                                           ║
║   * Optimized lacks OS-level sandbox (bubblewrap/seatbelt)                ║
║   Legend: ✅ Deep · 🟡 Partial · ⚪ Placeholder · ❌ Absent · 🆕 New       ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Final Assessment

| Dimension                     | AI-DLC                                               | AI-DLC Optimized                                                                  | Harness Engineering                                    |
|-------------------------------|------------------------------------------------------|-----------------------------------------------------------------------------------|--------------------------------------------------------|
| **Strengths**                 | Planning, requirements, human collaboration          | Balance across all areas + host portability + mode flexibility                    | Runtime, feedback, multi-agent                         |
| **Weaknesses**                | Automated feedback, Multi-Agent, cost, portability   | OS-level security (sandbox), prompt injection                                     | Requirements, human collaboration, cross-host support  |
| **Default Human Involvement** | Every stage                                          | User-selectable: Inception-heavy (Production) or Construction-light (Prototyping) | Boundary-crossing only                                 |
| **Host Assumption**           | Implicit single-agent                                | Detected, recorded, branched on                                                   | Claude Code implicit                                   |
| **Latest Trends**             | Fixed at creation time                               | Fully updated April 2026 (incl. 3-agent + Reasoning Sandwich)                     | Claude-Code-centric, blog-driven                       |
| **Best For**                  | Systematic project starts, regulated/production work | Full-range AI-native development, any host, any project type                      | Large-scale autonomous-agent operations on Claude Code |

> [!IMPORTANT]
> **Conclusion:**
>
> - **AI-DLC and HE are deep in completely opposite areas** — each is essentially blank where the other is deep.
> - **Optimized stays deep in AI-DLC's areas and also goes deep in HE's areas**, and adds two layers covered by neither: host capability adaptation and project-purpose gate density.
> - **The remaining gap** is OS-level infrastructure (bubblewrap/seatbelt, 2-layer prompt injection) and deployment automation — areas that genuinely require platform engineering beyond rule files.
> - The largest new contribution in the April 2026 revision is the **Host Capability Layer** and **Project Mode Layer**, which together make AI-DLC portable across every major AI coding IDE/CLI and tuneable per project without forking the ruleset.

---

## References

### AI-DLC

1. [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) — reference implementation used in this comparison: **v0.1.8** (30 files)
2. AI-DLC Optimized (April 2026 revision) — 40 files, ~302KB (AI-DLC + 10 new/rewritten + additional trims)
3. [AWS AI-DLC Whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com/aidlc.pdf) (Method Definition Paper)

### Harness Engineering

1. Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24)
2. Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
3. Anthropic, [Measuring AI agent autonomy in practice](https://www.anthropic.com/research/measuring-agent-autonomy) (2026-02)
4. Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (2025-06-13)
5. [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips)
6. LangChain, [Improving Deep Agents with Harness Engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) (2026-02-17)

### Maturity Frameworks

1. [Salesforce Agentic Maturity Model](https://www.salesforce.com/news/stories/agentic-maturity-model/) (2025-04)

---

**Author:** Kwangyoung Kim (<blackdog0403@gmail.com>)
**Source:** [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) (reference implementation: v0.1.8) + aidlc-rules-optimized (April 2026 revision) + Anthropic Engineering Blogs
**Last updated:** April 2026
