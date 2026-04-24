# AI-DLC Rules: Claude Code Skills-Native vs Platform-Agnostic Enhanced — A Comparative Review

**Author:** Kwangyoung Kim (<kwangyou@amazon.com>)
**Date:** 2026-04-23

> **Key Takeaways**
>
> - **Design premise of Enhanced:** AI-DLC is an **interface-level methodology** (the three-phase workflow, DDD vocabulary, Mob Elaboration rituals, Level-1 planning) and is independent from any particular agent host. The Construction-phase harness — Claude Code, Cursor, Cline, Amazon Q, Kiro, GitHub Copilot — is a Harness Engineering implementation detail that should be pluggable per team / per project. Enhanced was designed **first** to separate those two layers cleanly; the Skills-native packaging is one valid instantiation of the Construction-layer harness, observed here in parallel as a comparison point.
> - **Not a response to Skills-native.** Enhanced did not start from Skills-native and strip Claude Code affordances. It started from the AI-DLC whitepaper and built up a host-agnostic rule surface with an explicit **capability matrix** covering six hosts. That Skills-native and Enhanced share most of the `common/` + `inception/` + `construction/` rule files is a consequence of both converging on the same AI-DLC methodology, not of one deriving from the other.
> - **The benchmark used for comparison** is the Claude Code-native skills benchmark published at [`anhyobin/aidlc-workflows` — platforms/claude-code](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code). It was built to demonstrate the value of packaging AI-DLC as Claude Code Skills (slash commands, subagents, hooks). The question this document asks is: **while keeping AI-DLC's methodology intact and making the Construction-layer harness pluggable, what does the same rubric say?**
> - Enhanced adds seven rule files that encode Harness Engineering patterns in pure Markdown instead of host primitives: `agent-capabilities.md`, `project-mode.md`, `context-optimization.md`, `automated-feedback-loops.md`, `boundary-based-security.md`, `multi-agent-patterns.md`, `entropy-management.md`, plus a `cost-optimization` extension. These live at the rule layer precisely because not every supported host has Claude Code's Skills/subagents/hooks.
> - Running the benchmark against Enhanced (Serverless Order Management API, 14 stages × 71 regex assertions, Opus 4.7 full sequential pipeline via Bedrock): **Enhanced 68/71 (95.8%)** — tied with Upstream `awslabs/aidlc-workflows` (68/71) and three points below Skills-native (71/71). The three missing assertions are **all direct consequences of the design intent**: `detect/slash-command` (host-agnostic prose instead of Claude-Code-only `/aidlc-*`), `nfr/tech-stack` (AI-DLC mandates technology-agnostic NFR output), `reverse/8-artifact-types` (Greenfield skipped this stage, so there are no artifacts to enumerate). Closing any of these would require walking back either host portability or AI-DLC methodology.
> - The benchmark therefore **confirms the design intent** rather than exposing a weakness: Enhanced pays exactly the points the design said it would pay, and gains back two elsewhere (`functional/technology-agnostic`, `gate/2-phase` — the latter now explicit after Proposal B landed). It does **not** score the capabilities where Enhanced is objectively stronger — host portability, entropy management, L1–L5 feedback loops, boundary-based security — because the rubric was built to showcase Claude Code skill formatting, not methodology fidelity.
> - Separately from this rubric, Enhanced also passes the upstream AI-DLC evaluation gate run in CI via `scripts/aidlc-evaluator/` (Bedrock-backed, default config `opus-4-6`). That evaluator is the authoritative quality check for methodology compliance; the regex rubric in this document is a surface-level format check reused for honest cross-variant comparison.
> - **Framing:** the two repos are **complementary Construction-layer harnesses for the same AI-DLC interface**, not competing rule sets. Skills-native optimizes for Claude Code–specific UX; Enhanced optimizes for host-agnostic rule-layer encoding of Harness Engineering patterns. Which one a team uses is a matter of which Construction host they run on, not which is "better."

---

## Agenda

1. Executive Summary (design premise, framing, and why `anhyobin/aidlc-workflows` is the yardstick)
2. Architecture Comparison
3. Content Diff — Enhanced-only Rules Mapped to Harness Engineering Patterns
4. AI-DLC Principle Cross-check (Whitepaper Principles 1, 3, 7, 9, 10)
5. Benchmark Analysis — measured 14-stage Opus 4.7 run post A/B/C
6. Closing Observations
7. References

---

## 1. Executive Summary

### 1.0 Design premise — why Enhanced exists

AI-DLC, as defined in the [whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com/aidlc.pdf), is an **interface-level methodology**: a three-phase workflow (`INCEPTION → CONSTRUCTION → OPERATIONS`), a DDD-flavored artifact vocabulary, Mob Elaboration rituals, Level-1 planning. The whitepaper says little about which agent host should execute it — that is deliberately left to the implementer. In Harness Engineering terms, AI-DLC defines *what* the human / agent collaboration should look like; the *how* — which coding agent sandbox, which tool permission model, which subagent topology — belongs to the Construction-layer harness.

Enhanced is a rule set that takes that separation seriously. The `aidlc-rules/` tree encodes AI-DLC methodology in pure Markdown. The capability matrix in `common/agent-capabilities.md` classifies six host agents (Claude Code, Cursor, Cline, Amazon Q, Kiro, GitHub Copilot) into three capability profiles, and every Enhanced-specific rule file (`multi-agent-patterns.md`, `boundary-based-security.md`, etc.) branches on profile, not on host name. A team can adopt the AI-DLC methodology once and pick the Construction-layer harness that fits their context — Claude Code if they want the full Skills experience, GitHub Copilot if that is what their org already runs on.

### 1.1 Why this comparison — and why *anhyobin/aidlc-workflows* is the right yardstick

The reference benchmark published at [`anhyobin/aidlc-workflows` — platforms/claude-code](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code) was built to answer one specific question: *is packaging AI-DLC as Claude Code–native Skills worth the effort?* Its published scores — `with_skill` 71/71, `upstream` 68/71, `without_skill` 58/71 — answer that question with "yes, +3 over the plain rule file; +13 over no guidance."

That benchmark is the natural yardstick for Enhanced because it exercises the same AI-DLC methodology on the same scenario with the same rubric. Running Enhanced through it does **not** re-ask Anhyobin's question. It asks an adjacent one that Anhyobin's design correctly did not address: *if you keep AI-DLC methodology intact but make the Construction-layer harness pluggable, what does the same rubric say?*

The Enhanced score — **68/71, tied with Upstream** — reads at first glance like "host portability costs three points." A closer look at which three assertions fail tells a different story:

- `detect/slash-command` — Enhanced emits prose next-step guidance because `/aidlc-*` is meaningless on non–Claude Code hosts. Closing this gap would break host portability.
- `nfr/tech-stack` — Enhanced deliberately avoids naming "TypeScript" / "Node" in NFR output because AI-DLC mandates technology-agnostic NFR design. Closing this gap would violate the methodology.
- `reverse/8-artifact-types` — The scenario is Greenfield, so reverse engineering is legitimately skipped. Closing this gap would require fabricating artifact categories for a stage that correctly produced none.

All three failures are **exactly where the design premise in §1.0 said they would fall**. The benchmark therefore confirms that Enhanced pays the points it was designed to pay. It also gains back two points (`functional/technology-agnostic`, `gate/2-phase` after Proposal B) for the symmetric reason — rule files that explicitly encode what upstream merely implied.

An honest caveat: this regex rubric cannot measure what Enhanced actually delivers at the interface layer — host portability, L1–L5 verification ladder, boundary-based security tiers, entropy management, capability fallback. Those belong to a second benchmark axis that does not yet exist publicly. For methodology-level quality the authoritative check is the upstream AI-DLC evaluator wired into `scripts/aidlc-evaluator/` (Bedrock-backed, default config `opus-4-6`), which Enhanced passes in CI.

### 1.2 Framing

AI-DLC and the Construction-layer harness are two layers:

- **Interface layer** — AI-DLC methodology (three phases, 14 stages, DDD vocabulary). Identical in both repos because both implement AI-DLC.
- **Construction-layer harness** — how an agent actually reads the rules and produces artefacts. This is where Skills-native and Enhanced diverge.

The comparison in the rest of this document is therefore *two Construction-layer harnesses for the same interface*, not *two competing rule sets*.

- **Skills-native (`aidlc-workflows`)** answers with Claude Code's native primitives. It ships 14 `/aidlc-*` slash commands (one per AI-DLC stage), 4 role-based subagents (`aidlc-analyst`, `aidlc-architect`, `aidlc-developer`, `aidlc-reviewer`), SessionStart/SubagentStop hooks for state/audit logging, and 6 `.claude/rules/` cross-cutting constraints. The `aidlc-rules/` directory is a rule library; the actual orchestration lives in `.claude/`.
- **Enhanced (`aidlc-workflows-enhanced`)** answers with pure Markdown and a **capability matrix** covering Claude Code, Cursor, Cline, Amazon Q Developer, Kiro, and GitHub Copilot. Instead of binding to one host's primitives, it detects the host at runtime (via path resolution + self-report override) and branches behavior across three capability profiles (`full-multi-agent`, `subagent-only`, `single-agent`). It removes every Claude Code-only construct and compensates with additional rule files that encode the missing functionality in Markdown.

The trade-off is classical harness engineering. Quoting Lopopolo's framing:

> "Central boundaries, local autonomy."
> — Ryan Lopopolo, OpenAI, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11)

Skills-native puts the central boundaries in the Claude Code platform layer (hooks, permission allowlist, subagent routing). Enhanced puts them in the rule files themselves. Both are defensible; they optimize for different *blast radii*.

| Dimension | Skills-native | Enhanced |
|---|---|---|
| Primary surface | `.claude/` + `aidlc-rules/` | `aidlc-rules/` only |
| Host coverage | Claude Code only | 6 hosts via capability matrix |
| Total Markdown LOC (rules) | ~5,721 (29 files) | ~6,748 (39 files) |
| Claude Code–specific files | 16 SKILL.md + 4 subagents + 6 `.claude/rules/` + settings.json | 0 |
| Hooks | SessionStart (state), SubagentStop (audit) | None (rule-level equivalents) |
| Rule layer additions (vs Skills-native) | — | 7 common/phase files + cost-optimization extension |
| Benchmark (grade.py aggregate) | 71/71 (published) | 68/71 (measured 2026-04-23, Opus 4.7 via Bedrock) |

---

## 2. Architecture Comparison

### 2.1 Directory Tree

**Skills-native** (`/Users/kwangyou/Documents/dev/test-aidlc/aidlc-workflows/`):

```text
aidlc-workflows/
├── .claude/                                 ← Claude Code integration
│   ├── CLAUDE.md                            (5.1 KB — routing logic)
│   ├── settings.json                        (hooks + permission allowlist)
│   ├── agents/                              (4 × role-based subagents)
│   │   ├── aidlc-analyst.md
│   │   ├── aidlc-architect.md
│   │   ├── aidlc-developer.md
│   │   └── aidlc-reviewer.md
│   ├── skills/                              (14 slash commands, one per stage)
│   │   ├── aidlc-detect/
│   │   ├── aidlc-reverse/
│   │   ├── aidlc-requirements/
│   │   ├── aidlc-stories/
│   │   ├── aidlc-app-design/
│   │   ├── aidlc-units/
│   │   ├── aidlc-plan/
│   │   ├── aidlc-functional/
│   │   ├── aidlc-nfr/
│   │   ├── aidlc-infra/
│   │   ├── aidlc-code/
│   │   ├── aidlc-gate/
│   │   ├── aidlc-test/
│   │   └── aidlc-status/
│   └── rules/                               (6 cross-cutting constraint files)
│       ├── aidlc-terminology.md
│       ├── aidlc-content-validation.md
│       ├── aidlc-error-handling.md
│       ├── aidlc-workflow-changes.md
│       ├── aidlc-ext-security-baseline.md
│       └── aidlc-ext-property-based-testing.md
└── aidlc-rules/                             ← rule library (~5,721 LOC)
    ├── aws-aidlc-rules/
    │   └── core-workflow.md                 (538 lines — the orchestrator)
    └── aws-aidlc-rule-details/
        ├── common/                          (11 files, ~2,033 LOC)
        ├── inception/                       (7 files, ~1,726 LOC)
        ├── construction/                    (6 files, ~1,003 LOC)
        ├── operations/                      (1 placeholder, 19 LOC)
        └── extensions/                      (security/baseline, testing/property-based)
```

**Enhanced** (`/Users/kwangyou/Documents/dev/test-aidlc/aidlc-workflows-enhanced/`):

```text
aidlc-workflows-enhanced/
└── aidlc-rules/                             ← single source of truth (~6,748 LOC)
    ├── aws-aidlc-rules/
    │   └── core-workflow.md                 (588 lines — +50 vs Skills-native)
    └── aws-aidlc-rule-details/
        ├── common/                          (16 files, ~2,166 LOC — +5 new files)
        │   ├── agent-capabilities.md        ★ new — capability matrix for 6 hosts
        │   ├── automated-feedback-loops.md  ★ new — L1-L5 verification ladder
        │   ├── boundary-based-security.md   ★ new — Auto Mode-style tiering
        │   ├── context-optimization.md      ★ new — Knowledge Pyramid
        │   ├── project-mode.md              ★ new — Prototyping/Production/Hybrid
        │   └── [11 files shared with Skills-native]
        ├── inception/                       (7 files, ~1,768 LOC)
        ├── construction/                    (7 files, ~1,316 LOC — +1)
        │   ├── multi-agent-patterns.md      ★ new — Generator/Evaluator + fallbacks
        │   └── [6 files shared]
        ├── operations/                      (2 files, ~299 LOC — +1)
        │   ├── entropy-management.md        ★ new — Gardener Agent, trace-based detection
        │   └── operations.md                (80 LOC vs 19 LOC placeholder)
        └── extensions/                      (+1 extension)
            ├── cost-optimization/           ★ new (2 files)
            │   ├── cost-optimization.md
            │   └── cost-optimization.opt-in.md
            ├── security/baseline/           (shared)
            └── testing/property-based/      (shared)
```

### 2.2 Shared Backbone

Both repositories share the same backbone — the AI-DLC three-phase workflow (`INCEPTION → CONSTRUCTION → OPERATIONS`), the same 14 stages, the same artifact vocabulary (Intent, Unit, Bolt, Domain Design, Logical Design, Deployment Units), and the same `aidlc-docs/` output convention. The Inception phase file count (7), Construction core files (6), and extension structure (`.opt-in.md` convention) match 1:1. Eleven common/*.md files are either identical or near-identical between the two repos.

### 2.3 Where They Diverge

**Skills-native** binds three kinds of enforcement to Claude Code primitives:

1. **Stage entry** — each stage has a SKILL.md (`.claude/skills/aidlc-<stage>/SKILL.md`) that Claude Code matches against a `/aidlc-<stage>` slash command. The SKILL.md tells the agent which rule files to load.
2. **Role specialization** — four subagents (`aidlc-analyst`, `aidlc-architect`, `aidlc-developer`, `aidlc-reviewer`) are defined as `.claude/agents/*.md` and invoked via the `Agent` tool. They provide the Generator/Evaluator separation described in Anthropic's [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24) quote:
   > "Tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work."
3. **State/audit** — `.claude/settings.json` wires two hooks:
   - `SessionStart` reads `aidlc-docs/aidlc-state.md`, injects the current phase/stage and any pending question files into `additionalContext`.
   - `SubagentStop` (matcher `aidlc-.*`) appends an ISO-timestamped line to `aidlc-docs/audit.md`.

**Enhanced** removes every Claude Code primitive and replaces them with rule-file constructs:

1. **Stage entry** — `aws-aidlc-rules/core-workflow.md` becomes the single orchestrator. It explicitly spells out which rule details to load for each phase and stage, and resolves `aws-aidlc-rule-details/` against whichever host path-convention applies (`.aidlc/`, `.cursor/`, `.clinerules/`, `.amazonq/rules/`, `.kiro/steering/`, `.github/copilot-instructions/`).
2. **Role specialization** — replaced by `construction/multi-agent-patterns.md`, which describes Generator/Evaluator, parallel execution, and Architect-Implementer patterns, with three **capability-branched implementations**: full-multi-agent (delegates to subagents), subagent-only (sequential), and single-agent (context resets between roles).
3. **State/audit** — replaced by rule-level discipline in `common/session-continuity.md` and `common/overconfidence-prevention.md`. The agent is instructed to read/write `aidlc-state.md` and append to `audit.md` without hook enforcement.

### 2.4 Path Resolution Strategy

The most technically interesting design choice in Enhanced is the path-resolution preamble in `core-workflow.md`:

> "All subsequent rule detail file references (e.g., `common/process-overview.md`, `inception/workspace-detection.md`) are relative to whichever rule details directory was resolved above."
> — `aidlc-workflows-enhanced/aidlc-rules/aws-aidlc-rules/core-workflow.md` line 34

This one sentence is the hinge on which the whole host-agnostic design pivots. The agent tries a list of candidate paths (`.aidlc/…`, `.cursor/…`, etc.), picks the first that resolves, and then all subsequent relative references (of which there are 35+) work unchanged. It is the rule-file equivalent of Claude Code's `.claude/` convention, lifted into the content layer. This preserves the **Repository as Single Source of Truth** principle from Lopopolo:

> "Anything not in the repository effectively does not exist to Codex."
> — Ryan Lopopolo, OpenAI, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11)

---

## 3. Content Diff — Enhanced-only Rules Mapped to Harness Engineering Patterns

Enhanced introduces eight net-new rule assets. Each corresponds to a named Harness Engineering pattern from the [Anthropic Engineering blog corpus](https://www.anthropic.com/engineering). The table below is the core of the comparison.

| Enhanced rule file | Lines | Harness Engineering pattern | Anthropic / OpenAI source |
|---|---|---|---|
| `common/agent-capabilities.md` | 181 | Progressive Deletability; host-agnostic Brain/Hands separation | [Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents) |
| `common/project-mode.md` | 188 | "Fix cost < wait cost"; risk-based gate modulation | [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (Minimal Merge Gates + Agent Self-Merge) |
| `common/context-optimization.md` | 156 | Knowledge Pyramid (L0–L3) + Context Budget | [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) |
| `common/automated-feedback-loops.md` | 129 | Hierarchical Verification L1–L5 | [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) |
| `common/boundary-based-security.md` | 145 | Boundary-based security; Anthropic Auto Mode (FPR 0.4%) | [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) · [Auto mode for Claude Code](https://www.anthropic.com/engineering/claude-code-auto-mode) |
| `construction/multi-agent-patterns.md` | 313 | Orchestrator-Worker + capability fallback | [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) |
| `operations/entropy-management.md` | 219 | Gardener Agent; trace-based detection; AutoDream | [Harness engineering (Lopopolo, OpenAI)](https://openai.com/index/harness-engineering/) (Golden Principles, Taste Invariants) + [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips) (AutoDream) |
| `extensions/cost-optimization/` | 107 + 24 | Model Routing + Prompt Caching + Tool minimization | [Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) |

### 3.1 `agent-capabilities.md` — Progressive Deletability

This file maintains a capability matrix across six hosts (Claude Code, Cursor, Cline, Amazon Q, Kiro, GitHub Copilot) and maps them to three profiles. It is the direct expression of the Progressive Deletability principle from Anthropic's Managed Agents writing: encode host-specific assumptions so they can be *deleted* when the host gains capability parity. Skills-native has no equivalent — its assumptions about Claude Code are fused into the file layout, not isolated.

### 3.2 `project-mode.md` — Risk-based Gate Modulation

Defines three modes — **Prototyping**, **Production**, **Hybrid** — that modulate which gates fire and when. Prototyping skips per-unit human approval on L1–L4 passes (escalates only on L4 failure after two auto-fix rounds); Production requires human approval after every L1–L4 pass; Hybrid keeps Construction permissive but restores the Build & Test gate. This is the operational form of "Fix cost < wait cost" — letting teams dial the harness for their cost structure. Skills-native defaults to a single strict gating regime baked into the `.claude/skills/aidlc-gate/SKILL.md`.

### 3.3 `context-optimization.md` — Knowledge Pyramid

Implements the L0–L3 loading strategy: CLAUDE.md / AGENTS.md index (L0) → phase rules (L1) → stage rules (L2) → extension rules (L3, JIT). The file explicitly cites the Context Budget (<5% entry point, >80% working context) from Anthropic's writing. Skills-native loads rule details more eagerly through SKILL.md descriptions and does not expose an explicit budget.

### 3.4 `automated-feedback-loops.md` — L1–L5 Ladder

Codifies a five-layer verification ladder — drawn from the same "layered verification" framing Anthropic describes in [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24) — as a reusable block that Code Generation and Build & Test load during Construction:

- **L1** — per-file syntax/size/forbidden pattern (0–3 s)
- **L2** — linter + structural tests (5–30 s)
- **L3** — unit + integration tests (30 s–5 min)
- **L4** — reviewer agent (1–5 min)
- **L5** — human gate (modulated by Project Mode)

Skills-native's `.claude/rules/aidlc-error-handling.md` touches similar territory but does not structure the levels.

### 3.5 `boundary-based-security.md` — Auto Mode Implementation

Defines three permission tiers (Read-only → Write within project → Shell/Network/Agent). For Tier 3, it requires a classifier-style second check. This mirrors the production Auto Mode behavior Anthropic shipped in March 2026:

> "A dedicated Sonnet 4.6 Safety Classifier evaluates each tool call in real time: low-risk actions (file reads, in-project edits, test runs) are auto-approved; high-risk actions (force push, production deploy, external network) are blocked or require user confirmation. Final FPR: **0.4%** after Stage 2 CoT reasoning."
> — Anthropic, [Auto mode for Claude Code](https://www.anthropic.com/engineering/claude-code-auto-mode) (2026-03-25)

Skills-native relies on `settings.json` `permissions.allow` for Tier 1 enforcement and otherwise defers to Claude Code's default approval UX.

### 3.6 `multi-agent-patterns.md` — Capability-Branched Orchestration

Three implementations of the same pattern (Generator/Evaluator, parallel execution, Architect-Implementer) for three capability profiles:

- `full-multi-agent` — dispatch via subagent delegation (maps to Claude Code's Agent tool and `--worktree` isolation)
- `subagent-only` — sequential subagent invocation without parallelism
- `single-agent` — context-reset between roles

Skills-native's subagents (`.claude/agents/*.md`) implement only the `full-multi-agent` profile.

### 3.7 `entropy-management.md` — Gardener Agent

Introduces a Gardener pass at the Operations phase that (a) quantifies entropy via a Health Report (duplication %, circular dependencies, dead code %, doc-code consistency %, test coverage %), (b) opens cleanup PRs, and (c) tracks trace-based failure patterns for harness improvement. Skills-native's `operations/` is a 19-line placeholder.

### 3.8 `cost-optimization/` — Model Routing Extension

An opt-in extension wiring the Haiku 4.5 (1×) / Sonnet 4.6 (12×) / Opus 4.7 (60×) routing, plus prompt-caching discipline and tool-minimization. Not present in Skills-native.

---

## 4. AI-DLC Principle Cross-check

The [AI-DLC Whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com/aidlc.pdf) (Raja SP, 2026) defines ten Key Principles for AI-native methodology. Below I compare how each repository operationalizes the five principles most relevant to this comparison.

### Principle 1 — Reimagine Rather Than Retrofit

Both repos respect the principle at the AI-DLC workflow level (three phases, hours/days iteration, Mob Elaboration ritual). **Enhanced is stronger at the harness layer** because it decouples the method from a single host's primitives — a retrofit to six hosts would otherwise require six forks.

### Principle 3 — Integration of Design Techniques into the Core

Both are DDD-flavor (Domain Design → Logical Design → Deployment Units). Identical.

### Principle 7 — Facilitate Transition Through Familiarity

Skills-native wins for Claude Code users: `/aidlc-detect` is immediately discoverable. **Enhanced wins for heterogeneous teams**: a team running Claude Code + Cursor + Amazon Q can adopt one rule set without forking. This principle is explicitly about reducing per-team onboarding cost; Enhanced takes it further up the org-complexity axis.

### Principle 9 — Minimise Stages, Maximise Flow

Both define the same stages. Enhanced's `project-mode.md` goes *beyond* the whitepaper by parametrising the gate density — a team can legitimately skip per-unit human approval in Prototyping while preserving the Build & Test gate in Hybrid. Skills-native keeps a single gating regime.

### Principle 10 — No Hard-Wired, Opinionated SDLC Workflows

This is the deepest divergence. The whitepaper says AI-DLC **is not prescriptive** about the workflow; AI proposes a Level-1 Plan and humans iterate on it. **Both repos implement Level-1 planning** in `workflow-planning.md`. But Enhanced extends this with:

- `common/workflow-changes.md` (69 lines) — explicit rules for adapting the workflow mid-execution
- Capability-profile branching that causes the same method to expand/contract based on host
- Extension opt-in mechanics that let the user disable rule sets at Requirements Analysis time

Enhanced is measurably closer to the whitepaper's intent here.

---

## 5. Benchmark Analysis

### 5.1 Benchmark Recap

**Rubric provenance.** The rubric (`grade.py`, scenario, and per-skill pass counts in `upstream-baseline.json`) was authored and published by the owner of [`anhyobin/aidlc-workflows`](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code) — a personal third-party repository. AWS's official [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows) ships rule files only; it has no benchmark tooling of its own. The rubric is not an AWS official, Anthropic official, or independently-validated evaluation. It is reused here because it is the one publicly available comparison point that covers the same 14 AI-DLC stages on the same scenario across multiple rule-set variants.

The rubric file (`grade.py`) and the pinned per-skill scores (`upstream-baseline.json`) are committed in this repository under `docs/benchmark/` so the comparison is reproducible offline.

- **Scenario** (`scenario.md`) — Serverless Order Management API: Cognito + Lambda + DynamoDB + Stripe + SQS + SES + SNS + EventBridge; TypeScript/CDK; 1,000 orders/minute peak; 99.9% availability; p99 < 200 ms.
- **Grader** (`grade.py`, ~210 lines) — pure regex rubric, no LLM-as-judge. 71 assertions per variant (1 universal "no Korean" + 3–6 skill-specific × 14 skills). One flag-composition bug fixed locally vs. upstream (see §5.8 and Proposal doc §6.1).
- **Variants compared** — `Native` (`with_skill`, Claude Code Skills), `Upstream` (single-file `awslabs/aidlc-workflows` rule), `Baseline` (`without_skill`, no guidance), **`Enhanced`** (this repository).
- **Scores:**

| Variant | Passed | Total | Pass rate | Source |
|---|---|---|---|---|
| Native (`with_skill`) | 71 | 71 | 100.0% | Anhyobin published `benchmark.json` |
| **Enhanced** | **68** | **71** | **95.8%** | `docs/benchmark/benchmark.json` — measured 2026-04-23 on Opus 4.7 via Bedrock, post Proposal A/B/C |
| Upstream | 68 | 71 | 95.8% | Anhyobin published `benchmark.json` (pinned in `upstream-baseline.json`) |
| Baseline (`without_skill`) | 58 | 71 | 81.7% | Anhyobin published `benchmark.json` |

(The benchmark README on the Anhyobin side claims 76/76, 73/76, 54/71 — numbers from an earlier grader. The current `grade.py` emits 71 assertions per variant; we use the current numbers throughout.)

Enhanced ties Upstream on total but fails a different set of assertions — see §5.5 for the per-assertion decomposition and why those specific failures are design-intent, not regressions.

### 5.2 Methodology

The grader is a pure regex rubric over each stage's `result.md`. To score Enhanced:

1. The runner at `docs/benchmark/runners/run_full_benchmark.py` drives Opus 4.7 through the 14 stages sequentially via Bedrock, with prompt caching on the `common/*` rule bundle and prior-stage outputs fed forward as context.
2. Stage outputs land in `docs/benchmark/results/eval-<skill>/enhanced/outputs/result.md` (gitignored — LLM output, regenerate locally).
3. `python3 docs/benchmark/grade.py docs/benchmark/` applies the 71 regex assertions and writes `benchmark.json`.

The rubric file is behaviorally the original rubric published at `anhyobin/aidlc-workflows` with one flag-composition bug fixed locally (`check()` now OR-composes `re.IGNORECASE` with caller flags; three call-sites that passed `re.DOTALL` alone were silently case-sensitive before the fix). See Proposal doc §6.1 for details.

### 5.3 Headline Result

**Enhanced: 68/71 = 95.8%** — tied with Upstream (68/71), three points below Native (71/71). The per-skill picture is in §5.8 below; the per-assertion shape of the three missing points is in §5.5.

### 5.5 Where Enhanced Differs from Upstream

After Proposal A/B/C landed (see `docs/enhanced/proposals/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md`), the per-assertion picture is:

| Variant | `detect` slash-cmd | `detect` `===` hdr | `functional` tech-agnostic | `nfr` tech-stack | `reverse` 8-artifacts | `gate` 2-phase | `gate` GO/NO-GO |
|---|---|---|---|---|---|---|---|
| Native | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Upstream | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Enhanced** | **❌** | **✅** (A) | **✅** | **❌** | **❌** | **✅** (B) | **✅** (B) |

Enhanced **gains** on `functional/technology-agnostic` (rule explicitly forbids AWS service names) and on `gate/2-phase` + `gate/GO-NO-GO` (Proposal B's Gate Output Contract makes the 2-phase structure explicit so every model emits it, not just Opus with full 14-stage context).

Enhanced **loses** on three assertions, all by design:

- `detect/slash-command` — host-agnostic prose avoids `/aidlc-*` strings that would be meaningless on Cursor / Cline / Amazon Q. Documented as intentional in Proposal C (`common/agent-capabilities.md §7`).
- `nfr/tech-stack` — AI-DLC methodology mandates that NFR output stay technology-agnostic; naming "TypeScript" or "Node" at the NFR stage would collapse the NFR → Infrastructure separation the whitepaper requires.
- `reverse/8-artifact-types` — the test scenario is Greenfield, so Reverse Engineering correctly skips. A skipped stage has no artifacts to enumerate; emitting artifact category names anyway would be dishonest output.

### 5.6 Interpretation

The three assertions Enhanced loses are not "Claude Code formatting wins we failed to copy." They are the **measurable cost of two explicit design commitments**: host portability (one point) and AI-DLC methodology compliance (two points). Closing any of them would require walking back exactly those commitments.

Equivalently: the benchmark **confirms the design intent**. Every failing assertion maps 1:1 to a design decision that is documented elsewhere in the rule set or the proposals. There are no surprises, no unexplained gaps, and no "we tried but couldn't" cases.

The +1 gain Enhanced still has over Upstream (`functional/technology-agnostic`) and the +2 gain on `gate/*` it now shares with Native (via Proposal B) come from the same source: rule files that explicitly encode AI-DLC principles Upstream only implies.

### 5.7 Limits of the Rubric

1. The grader is regex, not LLM-as-judge. It does not score methodological fidelity; it scores whether a specific string appears. A methodologically better but differently-formatted output can score worse. This is a property of the regex rubric, not of either rule set.
2. The rubric rewards Claude Code skill-template conventions (setext `===` headers, `/aidlc-*` slash commands, specific section titles). Rule sets that emit semantically equivalent but textually different output are penalized regardless of methodology quality.
3. For methodology fidelity, use `scripts/aidlc-evaluator/` instead (see §5.9).

### 5.8 Measured Run (2026-04-23, post A/B/C)

The measured run uses the new ad-hoc runner at `docs/benchmark/runners/run_full_benchmark.py` — a sequential 14-stage pipeline driving Opus 4.7 via Bedrock, with the `common/*` rules prompt-cached and each stage's prior-stage outputs fed forward as context. Proposal A / B / C are applied to the rule files before the run. Outputs land in `docs/benchmark/results/eval-<skill>/enhanced/outputs/result.md` (gitignored — regenerate locally) and are scored with the unchanged `grade.py` rubric (one flag-composition bug fixed; see §6.1 of the proposal doc).

**Headline result: 68/71 = 95.8%** — tied with Upstream (68/71), three points below Native (71/71). The per-skill breakdown:

| Skill | Native (published) | Upstream (published) | Enhanced — **measured** | Δ vs Upstream | Note |
|---|---|---|---|---|---|
| detect | 5/5 | 5/5 | **4/5** | −1 | A recovered the `===` header; slash-command lost by design |
| reverse | 4/4 | 4/4 | **3/4** | −1 | Greenfield → stage skipped → no artifacts to enumerate |
| requirements | 7/7 | 7/7 | 7/7 | = | |
| stories | 5/5 | 5/5 | 5/5 | = | |
| app-design | 5/5 | 5/5 | 5/5 | = | |
| units | 5/5 | 5/5 | 5/5 | = | |
| plan | 5/5 | 5/5 | 5/5 | = | |
| functional | 6/6 | 5/6 | 6/6 | +1 | rule explicitly technology-agnostic |
| nfr | 5/5 | 5/5 | **4/5** | −1 | rule mandates tech-agnostic NFR; regex demands "TypeScript/Node" |
| infra | 5/5 | 5/5 | 5/5 | = | |
| code | 5/5 | 5/5 | 5/5 | = | |
| gate | 5/5 | 3/5 | 5/5 | +2 | Proposal B (Gate Output Contract) makes 2-phase structure explicit |
| test | 5/5 | 5/5 | 5/5 | = | |
| status | 4/4 | 4/4 | 4/4 | = | |
| **Total** | **71/71** | **68/71** | **68/71** | **=** | |

**Interpretation:**

1. **Benchmark confirms design intent.** Every one of the three failing assertions maps 1:1 to a design commitment documented in the rule set or the proposals. There are no unexplained gaps.
2. **Enhanced's +3 gains are also design-driven.** `functional/technology-agnostic` comes from rule lines that explicitly forbid AWS service names. `gate/2-phase` and `gate/GO-NO-GO` come from the Gate Output Contract that Proposal B added to `build-and-test.md` after measuring that even Opus 4.7 could not synthesize the 2-phase structure in isolation (see Proposal doc §6).
3. **Tied score, different shape.** Enhanced and Upstream both land on 68/71, but they fail different assertions. Upstream fails `functional/tech-agnostic` + both `gate/*` assertions (methodology gaps). Enhanced fails `detect/slash-command` + `nfr/tech-agnostic` + `reverse/8-artifacts` (portability + methodology wins, mechanical skip cost). The shape of the failures is the actual comparison, not the headline number.

**Relation to earlier measurements:**

An earlier measurement (before Proposal A/B/C and before the runner existed) reported 69/71 — taken via manual Claude Code sessions. That number included an incidental +1 on `reverse` (the interactive session produced a more verbose skip message that coincidentally contained an artifact-category word). The new automated runner produces terser skip messages, surfacing the underlying `reverse/8-artifacts` gap that was always present but masked by session verbosity. 68/71 is the reproducible floor.

**Artifacts produced:**

- 14 × `docs/benchmark/results/eval-<skill>/enhanced/outputs/result.md` — ~3,300 lines of stage output (gitignored).
- `docs/benchmark/results/eval-<skill>/enhanced/grading.json` — per-skill assertion detail.
- `docs/benchmark/benchmark.json` — committed aggregate report.

### 5.9 What the Benchmark Does Not Measure

The benchmark was designed to demonstrate Claude Code–native skill value on a regex rubric, and it does. It does **not** probe:

- **Host portability** (Enhanced's main claim).
- **Entropy management** at the Operations phase (Enhanced-only `entropy-management.md`).
- **L1–L5 layered verification** (Enhanced-only `automated-feedback-loops.md`).
- **Boundary-based security gating** (Enhanced-only `boundary-based-security.md`).
- **Capability fallback** for non-multi-agent hosts.
- **Cost behavior** under Model Routing.
- **Methodology fidelity** — the rubric rewards output-format strings, not whether the stage actually produced a correct artefact by AI-DLC standards.

Any fair comparison needs a second benchmark axis that covers these capabilities. Defining one is out of scope for this PR; the shape of what that axis should look like — one mini-experiment per Harness Engineering pattern — is proposed in [`docs/enhanced/proposals/HARNESS-ENGINEERING-BENCHMARK-AXIS.md`](../enhanced/proposals/HARNESS-ENGINEERING-BENCHMARK-AXIS.md).

**Where methodology fidelity is checked instead:** the upstream AI-DLC evaluator lives at [`scripts/aidlc-evaluator/`](../../scripts/aidlc-evaluator/) in this repository. It is Bedrock-backed (default config `config/default.yaml` pins `opus-4-6` as executor / simulator / scorer), runs end-to-end AI-DLC scenarios in a Docker sandbox, and is the authoritative CI gate for this fork. Enhanced currently passes that gate. Readers evaluating Enhanced for their own use should treat `scripts/aidlc-evaluator/` as the quality signal and the regex rubric in this document as a surface-level format check reused for honest cross-variant comparison.

### 5.10 Future benchmark axis — pointer to proposal

Proving the Harness Engineering patterns Enhanced adds (§3) requires runtime measurement the regex rubric cannot do. The proposal at [`docs/enhanced/proposals/HARNESS-ENGINEERING-BENCHMARK-AXIS.md`](../enhanced/proposals/HARNESS-ENGINEERING-BENCHMARK-AXIS.md) sketches one mini-experiment per pattern (L1–L5 ladder, Generator/Evaluator, host portability, context budget, boundary-based security, entropy management, cost optimization, project mode), each as a small follow-up PR sized measurement. None are run inside this PR.

Until those axes land, the claim that Enhanced delivers Harness Engineering benefits beyond the current regex rubric rests on design argument + literature citations + [Proposal B §6](../enhanced/proposals/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md)'s fragility measurement (the one existing quantitative data point).

---

## 6. Closing observations

### 6.1 Proposals landed (2026-04-23)

Three rule-level improvements (A/B/C in [`docs/enhanced/proposals/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md`](../enhanced/proposals/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md)) have been implemented:

- **Proposal A** — `workspace-detection.md` completion header changed to `=== Workspace Detection Complete ===` (setext banner). Outcome: `detect/Contains completion summary` now passes, raising `detect` from 3/5 to 4/5.
- **Proposal B** — `build-and-test.md` now has an explicit "Gate Output Contract" section mandating the `Phase 1 / Phase 2 + GO/NO-GO + PASS/FAIL` structure. Outcome: every tested model (Haiku 4.5 / Sonnet 4.6 / Opus 4.7) now scores 5/5 on `gate` in isolation — validated by the 18-run fragility matrix in the Proposal doc §6.
- **Proposal C** — `common/agent-capabilities.md §7` now documents that next-step cues like `/aidlc-*` are a host-adapter concern, not a core-rule concern, so future contributors will not "fix" Enhanced's `detect/slash-command` gap by silently degrading UX on non–Claude Code hosts.

### 6.2 Structural gaps that remain

Enhanced commits to two design principles:

1. **Host portability** — the rule set must work on any agent host (Claude Code, Cursor, Cline, Amazon Q, Kiro, GitHub Copilot), not just one.
2. **AI-DLC methodology fidelity** — the core AI-DLC structures (question-file format, audit log, human-approval gates, technology-agnostic NFR design, Greenfield / Brownfield branching) must be preserved as the whitepaper defines them.

Keeping both principles has a measurable cost. Two examples:

- Emitting Claude Code slash commands (`/aidlc-requirements`) would pick up a rubric point, but break host portability — Cursor / Cline / Amazon Q users would see meaningless strings.
- Naming concrete technologies ("TypeScript", "Node") at the NFR stage would pick up a rubric point, but violate AI-DLC's technology-agnostic NFR principle.

Enhanced deliberately omits those outputs. The regex rubric, however, only checks "does this pattern appear in the output?" It cannot tell apart:

- **"Didn't try"** — the rule set lacks the capability, so the pattern is missing by accident.
- **"Tried and correctly chose not to"** — the rule set has the capability but deliberately excluded the output on principle.

Enhanced's three remaining failures are all the second kind:

| Failure | Why the pattern is absent | Design principle violated if closed |
|---|---|---|
| `detect/Recommends next step` | Enhanced uses prose ("Proceeding to Requirements Analysis") instead of `/aidlc-*` literals | Host portability (documented in Proposal C) |
| `nfr/Tech stack decisions` | NFR rule explicitly forbids naming technologies at this stage | AI-DLC methodology (tech-agnostic NFR → Infra separation) |
| `reverse/Produces 8 artifact types` | Greenfield scenario → stage correctly skipped → no artifacts exist | Honest output (a skipped stage cannot legitimately enumerate artifacts) |

**A subtle but important nuance — runtime environment can mask rule-layer behavior.** The Anhyobin benchmark was executed inside Claude Code, and some of these regex patterns can be satisfied either by the *rule file* explicitly encoding the pattern **or** by the *runtime environment* supplying it for free. Examples:

- `detect/slash-command` — Claude Code renders `/aidlc-*` commands as clickable UI affordances during an interactive session, so a Claude Code run can surface slash-command strings even when the rule file does not prescribe them. A run of the same rule set on Cursor / Cline / Amazon Q would not get that free string.
- `reverse/8-artifact-types` — an interactive conversational session (Claude Code UX default) tends to produce more verbose, explanatory output where category words like `architecture`, `api`, `component` show up in prose commentary. An automated API run emits tighter artefacts and loses that incidental match. This is exactly why Enhanced's earlier interactive measurement scored 69/71 and the automated runner now scores 68/71.

Enhanced's rule-layer design deliberately does **not** rely on either source. The rules produce the same output whether the host is Claude Code, Cursor, or a raw Bedrock API call, because host portability is an explicit design goal (§1.0). The rubric cannot observe that property — it only sees whether specific strings ended up in `result.md`, regardless of whether the rule or the environment put them there.

**Bottom line:** the 68/71 score is not a quality shortfall in the rule set. It is a limitation of the rubric — a regex rubric cannot distinguish (a) principled exclusion from missing capability, nor (b) rule-layer output from environment-supplied output. It penalizes Enhanced for both.

---

## References

1. [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows) v0.1.8 — upstream reference rule file (AWS official, rule files only; no benchmark tooling).
2. [`anhyobin/aidlc-workflows` — platforms/claude-code](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code) — personal third-party repository that authored the Claude Code–specialized rule packaging ("Native Claude Code Skills"), the regex rubric (`grade.py`), the test scenario (`scenario.md`), and the published per-skill scores (`benchmark.json`). All pinned in this repo under `docs/benchmark/`.
3. Raja SP, Amazon Web Services, [*AI-Driven Development Lifecycle (AI-DLC) Method Definition*](https://prod.d13rzhkk8cj2z0.amplifyapp.com/aidlc.pdf) (2026) — methodology source.
4. Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24) — Generator/Evaluator pattern.
5. Anthropic, [Auto mode for Claude Code](https://www.anthropic.com/engineering/claude-code-auto-mode) (2026-03-25) — boundary-based security, FPR 0.4%.
6. Anthropic, [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) (2025-10-20) — 84% permission-prompt reduction.
7. Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09-29) — Knowledge Pyramid.
8. Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (2025-06-13) — Orchestrator-Worker pattern.
9. Anthropic, [Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) (2025-11-24) — Tool Search, Programmatic Tool Calling.
10. Anthropic, [Decoupling the brain from the hands (Managed Agents)](https://www.anthropic.com/engineering/managed-agents) — Progressive Deletability.
11. Ryan Lopopolo (OpenAI), [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11) — legibility, central-boundary/local-autonomy.

---

> Author: Kwangyoung Kim (<kwangyou@amazon.com>) + Claude Code
> Source: [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows) benchmarks + [Anthropic Engineering Blog](https://www.anthropic.com/engineering) + [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) + [AI-DLC Whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com/aidlc.pdf)
> Last updated: April 2026
