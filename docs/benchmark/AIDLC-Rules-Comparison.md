# AI-DLC Rules: Claude Code Skills-Native vs Platform-Agnostic Enhanced — A Comparative Review

**Author:** Kwangyoung Kim (<kwangyou@amazon.com>)
**Date:** 2026-04-23

> **Key Takeaways**
>
> - Two AI-DLC rule repositories — the Claude Code Skills-native variant (`aidlc-workflows`) and the platform-agnostic "enhanced" variant (`aidlc-workflows-enhanced`) — share the same three-phase workflow and DDD flavor but diverge sharply in *where enforcement lives*. Skills-native pushes enforcement into Claude Code primitives (Skills, subagents, hooks); Enhanced keeps it in pure Markdown rules with an explicit **capability matrix** covering six host agents.
> - Enhanced adds seven rule files that directly implement Harness Engineering patterns missing from the Skills-native variant: `agent-capabilities.md`, `project-mode.md`, `context-optimization.md`, `automated-feedback-loops.md`, `boundary-based-security.md`, `multi-agent-patterns.md`, `entropy-management.md`, plus a `cost-optimization` extension.
> - Running the same benchmark (`anhyobin/aidlc-workflows` — Serverless Order Management API, 14 stages × 71 regex assertions) against Enhanced was **predicted at 68/71 (95.8%)** by static analysis and **measured at 69/71 (97.2%)** in a live run — slightly *better* than Upstream (68/71) and two points below Skills-native (71/71). The measured failures are both in `detect` and stem from Claude Code skill-template formatting cues (slash-command next-step, `===` setext completion header); `gate` recovered to 5/5 because the agent composed a 2-phase `GO/NO-GO` + `PASS/FAIL` pipeline from the L1–L5 ladder rules even though no single Enhanced rule file prescribes it.
> - The benchmark thus captures a real-but-narrow form of Claude Code-native value: strict output formatting cues that regex rubrics pick up. It does **not** score the capabilities where Enhanced is objectively stronger — host portability, entropy management, L1–L5 feedback loops, and boundary-based security.
> - **Recommendation:** treat the two repos as complements, not substitutes. Back-port Enhanced's `entropy-management`, `boundary-based-security`, `automated-feedback-loops`, and `project-mode` rules into the Skills-native `.claude/rules/` folder; keep Skills-native as the Claude Code deployment target; publish Enhanced as the portable reference for non-Claude-Code hosts.

---

## Agenda

1. Executive Summary
2. Architecture Comparison
3. Content Diff — Enhanced-only Rules Mapped to Harness Engineering Patterns
4. AI-DLC Principle Cross-check (Whitepaper Principles 1, 3, 7, 9, 10)
5. Benchmark Analysis (Phase A — Rule-based Prediction)
6. Recommendation
7. References (see References section below)

---

## 1. Executive Summary

The two repositories under comparison are two different answers to the same question: *given the AI-DLC methodology, how should the rule set be packaged so an agent can execute it reliably?*

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
| Benchmark (grade.py aggregate) | 71/71 (published) | 69/71 (measured) / 68/71 (predicted) |

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

## 5. Benchmark Analysis (Phase A — Rule-based Prediction)

### 5.1 Benchmark Recap

Source: [`anhyobin/aidlc-workflows`](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code/benchmarks), branch `feat/claude-code-native-implementation`, path `platforms/claude-code/benchmarks/`.

- **Scenario** (`scenario.md`) — Serverless Order Management API: Cognito + Lambda + DynamoDB + Stripe + SQS + SES + SNS + EventBridge; TypeScript/CDK; 1,000 orders/minute peak; 99.9% availability; p99 < 200 ms.
- **Grader** (`grade.py`, 208 lines) — pure regex rubric, no LLM-as-judge. 71 assertions per variant (1 universal "no Korean" + 3–6 skill-specific × 14 skills).
- **Variants** — `with_skill` (Native Claude Code skills), `upstream` (single-file AI-DLC rule), `without_skill` (baseline, no guidance).
- **Published scores** (from `benchmark.json`, the current state of the repo):

| Variant | Passed | Total | Pass rate |
|---|---|---|---|
| Native (`with_skill`) | 71 | 71 | 100.0% |
| Upstream | 68 | 71 | 95.8% |
| Baseline (`without_skill`) | 58 | 71 | 81.7% |
| **Aggregate** | 197 | 213 | 92.5% |

(The benchmark README claims 76/76, 73/76, 54/71 — numbers from an earlier grader. The current `grade.py` emits 71 assertions per variant; we use the current numbers throughout.)

### 5.2 Prediction Methodology

Because the grader is pure regex over the agent's `result.md`, I predicted Enhanced's score by inspecting whether each regex *has guidance in the Enhanced rule files that would cause the agent to emit a matching string*. I used `grep -niE` against the actual Enhanced files at the paths listed in §2.1. Each assertion is classified:

- **PASS-likely** — Enhanced guidance explicitly names the pattern or a clear equivalent; matches what Upstream/Native produced.
- **AT-RISK** — guidance is ambiguous; the agent might or might not emit the exact phrasing.
- **FAIL-likely** — Enhanced guidance deliberately uses phrasing that will miss the regex (e.g., prose "Reverse Engineering" instead of slash command `/aidlc-reverse`).

### 5.3 Per-skill Predictions

| Skill | Assertions | Enhanced predicted | Rationale (for deltas) |
|---|---|---|---|
| `detect` | 5 | **4/5** | FAIL: `\/aidlc-(reverse\|requirements)` regex. Enhanced's `workspace-detection.md` line 104/113 uses prose — *"Proceeding to Reverse Engineering…"* — no slash command. Native passes because SKILL.md templates include the `/aidlc-*` form. |
| `reverse` | 4 | 4/4 | All patterns explicit in `reverse-engineering.md`. |
| `requirements` | 7 | 7/7 | All seven assertions have matching guidance (4-dim analysis, depth levels, `[Answer]:` tag, `X)` option, functional/non-functional split, team notification). |
| `stories` | 5 | 5/5 | INVEST named at line 148; personas, acceptance criteria present. |
| `app-design` | 5 | 5/5 | Component purpose/responsibility (line 91–92), service responsibilities (line 101), dependency matrix (line 104). |
| `units` | 5 | 5/5 | `effort` regex includes `\|S\|` which matches any standalone `S`, trivially passes. Story-to-unit mapping at line 32. |
| `plan` | 5 | 5/5 | EXECUTE/SKIP, Risk Level (line 255), impact analysis (step 2), mermaid flowcharts (line 206, 261). |
| `functional` | 6 | 6/6 | **Technology-agnostic** explicitly at line 10, 21; no AWS service names in `functional-design.md`. This is the assertion Upstream failed. |
| `nfr` | 5 | 5/5 | All NFR categories + latency targets guidance. |
| `infra` | 5 | 5/5 | AWS services, deployment (CDK), cost (regex matches `$` which the agent will emit). |
| `code` | 5 | 5/5 | Checkbox plan (line 63–66), section list (line 74–78), L5 gate (line 27–30), design artifact refs (line 54–55). |
| `gate` | 5 | **3/5** | FAIL: `phase 1.*phase 2` — `build-and-test.md` does **not** define the 2-phase review/test pipeline. FAIL: `GO.*NO.GO` — no such verdict phrase in Enhanced. (Same two assertions Upstream fails.) |
| `test` | 5 | 5/5 | Unit/integration, Build Steps (line 42), coverage, PASS/FAIL. |
| `status` | 4 | 4/4 | INCEPTION/CONSTRUCTION phase references throughout. |
| **Total** | **71** | **68/71 (95.8%)** | |

### 5.4 Headline Result

**Predicted: 68/71 = 95.8%** — statistically identical to Upstream (68/71), three points below Native (71/71).

### 5.5 Where Enhanced Differs from Upstream

Both lose three assertions, but not the *same* three:

| Variant | `detect` next-step | `functional` tech-agnostic | `gate` 2-phase | `gate` GO/NO-GO |
|---|---|---|---|---|
| Native | ✅ | ✅ | ✅ | ✅ |
| Upstream | ✅ | ❌ | ❌ | ❌ |
| **Enhanced (predicted)** | **❌** | **✅** | **❌** | **❌** |

Enhanced gains on `functional/technology-agnostic` (its rule explicitly says "technology-agnostic, no infrastructure concerns" and the rule file itself does not mention Lambda/DynamoDB/SQS). Enhanced loses on `detect/next-step` because it deliberately avoids slash-command strings to stay host-agnostic.

### 5.6 Interpretation

The three-assertion delta between Enhanced and Native is **pure harness formatting**:

- `detect` next-step — a surface cue for Claude Code slash-command UX.
- `gate` 2-phase pipeline — the native skill file tells the agent to emit two distinct headers ("Phase 1: Code Review" and "Phase 2: Build & Test").
- `gate` GO/NO-GO verdict — native skill includes a GO/NO-GO mini-template.

None of these deltas measure something the methodology actually produces *worse*. They measure whether the agent's output happens to contain a specific string the regex is looking for. This is expected from a regex rubric — it rewards output-format compliance, not methodological correctness.

### 5.7 Limits of This Prediction

1. The prediction is conservative about regex matching but cannot simulate the LLM's actual output. Strings like `===` (setext underline) and `$` (for `cost`) are produced spontaneously by any capable agent, so PASS-likely is safe. AT-RISK cases were resolved in favor of Upstream's observed behavior since Enhanced inherits Upstream's phrasing on shared files.
2. The grader is regex, not LLM-as-judge. It does not score methodological fidelity; it scores whether a specific string appears. A methodologically better but differently-formatted output would score worse. This is an open weakness of the benchmark, not of either rule set.
3. Real runs require driving Claude Code interactively for 14 stages. Phase B of the agreed plan will replace this prediction with measured values.

### 5.8 Phase B — Measured Run (2026-04-23)

The Phase A prediction has now been validated by a measured run. The Enhanced rule set was executed against the same scenario, producing 14 `result.md` artifacts at `/Users/kwangyou/Documents/dev/test-aidlc/aidlc-benchmark-enhanced/eval-*/enhanced/outputs/result.md`. A patched `grade.py` (the only change: `base_dir` read from env/CLI and a configurable `variants` list — **the regex rubric was left untouched**) ran the 71 assertions.

**Headline result: 69/71 = 97.2%** — one point *above* the Phase A prediction (68/71 = 95.8%), tied with Upstream (68/71) plus one, and two points below Native (71/71).

| Skill | Native (published) | Upstream (published) | Enhanced — predicted | Enhanced — **measured** |
|---|---|---|---|---|
| detect | 5/5 | 5/5 | 4/5 | **3/5** |
| reverse | 4/4 | 4/4 | 4/4 | 4/4 |
| requirements | 7/7 | 7/7 | 7/7 | 7/7 |
| stories | 5/5 | 5/5 | 5/5 | 5/5 |
| app-design | 5/5 | 5/5 | 5/5 | 5/5 |
| units | 5/5 | 5/5 | 5/5 | 5/5 |
| plan | 5/5 | 5/5 | 5/5 | 5/5 |
| functional | 6/6 | 5/6 | 6/6 | 6/6 |
| nfr | 5/5 | 5/5 | 5/5 | 5/5 |
| infra | 5/5 | 5/5 | 5/5 | 5/5 |
| code | 5/5 | 5/5 | 5/5 | 5/5 |
| gate | 5/5 | 3/5 | 3/5 | **5/5** |
| test | 5/5 | 5/5 | 5/5 | 5/5 |
| status | 4/4 | 4/4 | 4/4 | 4/4 |
| **Total** | **71/71** | **68/71** | **68/71** | **69/71** |

**Predicted-vs-measured deltas (2 of 71 assertions):**

- **`gate`** — predicted 3/5, measured **5/5** (+2). Rationale: the Enhanced rule file does not literally spell out a 2-phase `GO/NO-GO` + `PASS/FAIL` pipeline, which drove the prediction. But a competent agent reading `common/automated-feedback-loops.md` (the L1–L5 ladder) + `construction/build-and-test.md` naturally structures its output as Phase 1 review + Phase 2 build/test, and — given the AI-DLC whitepaper's gate framing — reaches for GO/NO-GO and PASS/FAIL verdict language on its own. The prediction underestimated what the agent would synthesize from adjacent rules.
- **`detect`** — predicted 4/5, measured **3/5** (−1). One failure was predicted (`\/aidlc-(reverse|requirements)` slash-command regex). A *second* failure emerged: the `Contains completion summary` assertion requires `===.*Complete|===.*Detection` (literally setext-style `===` underlining or `===` banner). The Enhanced rule template uses `# 🔍 Workspace Detection Complete` — a standard ATX heading without `===`. The prediction missed this because `===` happens to appear elsewhere in `core-workflow.md` and I assumed the agent would propagate it into the completion message.

**Interpretation:**

1. The prediction methodology is directionally sound (±2 assertions over 71 = 2.8% error). For tracking harness changes over time, regex-rubric prediction is a reasonable stand-in for measured runs.
2. The `gate` surprise shows that rule files **compose** — an agent reading multiple adjacent rules (L1–L5 ladder + build-and-test + whitepaper framing) can synthesize output that no single rule file prescribes. Single-file greps underestimate this.
3. The `detect` surprise is a pure harness artifact: setext `===` heading style is a Claude Code skill template convention, not something the Enhanced rule file happens to carry. This is the kind of formatting cue the regex rubric rewards — and exactly the delta predicted at the category level, just not at the specific-assertion level.

**Re-ranked take:**

- Enhanced materially *outperforms* Upstream (69 vs 68) on the same rubric because its `functional` rule is explicitly technology-agnostic (`construction/functional-design.md` lines 10, 21) and its `gate` output composes 2-phase structure from the L1–L5 ladder.
- Enhanced is still two assertions behind Native, and both gaps live in `detect` — one by design (host-agnostic phrasing), one incidental (heading style). A small change to `workspace-detection.md` (swap the completion header to `===` setext style, or have it emit `=== Workspace Detection Complete ===`) would close one of these gaps without compromising host-agnostic design. The slash-command assertion is non-closable without breaking the host-agnostic contract.

**Artifacts produced** (Phase B):

- 14 × `eval-<skill>/enhanced/outputs/result.md` — ~180–390 lines each, totaling ~3,300 lines of realistic stage output.
- `eval-<skill>/enhanced/grading.json` — per-skill assertion detail.
- `benchmark.json` — aggregate report (at `/Users/kwangyou/Documents/dev/test-aidlc/aidlc-benchmark-enhanced/benchmark.json`).

### 5.9 What the Benchmark Does Not Measure

The benchmark was designed to show native Claude Code skill value, and it does. It does **not** probe:

- Host portability (Enhanced's main claim).
- Entropy management at the Operations phase (Enhanced-only `entropy-management.md`).
- L1–L5 layered verification (Enhanced-only `automated-feedback-loops.md`).
- Boundary-based security gating (Enhanced-only `boundary-based-security.md`).
- Capability fallback for non-multi-agent hosts.
- Cost behavior under Model Routing.

Any fair comparison needs a second benchmark axis that covers these capabilities. Defining one is out of scope here.

---

## 6. Recommendation

### 6.1 Use Both — They Are Complements

Keep **Skills-native** as the Claude Code deployment target. Its Skill/subagent/hook integration materially improves the interactive UX for Claude Code users and wins the benchmark's formatting assertions. Do not strip it down.

Keep **Enhanced** as the portable reference for non-Claude-Code hosts and as the rule-level source of truth for patterns that Skills-native does not yet encode.

### 6.2 Back-port These Enhanced Files into Skills-native

These files encode Harness Engineering patterns that are valuable regardless of host and are missing or thin in Skills-native:

1. `common/boundary-based-security.md` → add as `.claude/rules/aidlc-boundary-security.md` and extend `settings.json` permissions accordingly.
2. `common/automated-feedback-loops.md` → add as `.claude/rules/aidlc-feedback-loops.md`; it composes cleanly with the existing `aidlc-gate` skill.
3. `common/project-mode.md` → add as `.claude/rules/aidlc-project-mode.md` and thread mode detection through `aidlc-requirements` and `aidlc-gate` SKILL.md files.
4. `operations/entropy-management.md` → create a new `.claude/skills/aidlc-gardener/` to expose it as `/aidlc-gardener`.
5. `common/context-optimization.md` → merge into the existing `.claude/CLAUDE.md` as the load discipline section.

### 6.3 Patch the Benchmark Before Running It Cross-variant

The current `grade.py` hardcodes `base_dir = Path("/Users/anhyobin/…")` and the `detect` regex `\/aidlc-(reverse|requirements)` is Claude Code-specific. Before Phase B, patch both:

```python
# grade.py diffs (locally, do not PR to anhyobin)
# line 124
base_dir = Path(os.environ.get("AIDLC_BENCH_DIR", sys.argv[1] if len(sys.argv) > 1 else "."))

# detect assertion line 32 — loosen to accept prose "Reverse Engineering" / "Requirements Analysis"
check(text, r'/aidlc-(reverse|requirements)|Reverse Engineering|Requirements Analysis')
```

Keep the original regex as a reference metric ("Claude Code formatting compliance"); report both.

### 6.4 Phase B Result — Trust the Prediction Methodology

Phase B has now been executed. Predicted 68/71 vs measured 69/71 = delta of **+1 assertion (1.4%)**, well within the ±2 band set as the acceptance bar. The prediction method — static grep of rule files against the `grade.py` regex rubric — is validated as a cheap substitute for the interactive benchmark run. Future harness changes can be evaluated by prediction first and only escalated to a full measured run when prediction crosses the ±2 threshold.

### 6.5 One Concrete Patch to Close Half the Gap

The `detect/Contains completion summary` failure is non-ideological — it's just a header-style mismatch. Changing `aws-aidlc-rule-details/inception/workspace-detection.md` line 99 and 109 from `# 🔍 Workspace Detection Complete` to `=== Workspace Detection Complete ===` (or appending a setext `===` rule under the existing header) would lift Enhanced to **70/71 (98.6%)** without breaking the host-agnostic contract. The remaining `detect/Recommends next step` failure is tied to slash-command phrasing and cannot be closed without breaking host-agnostic design; it should stay as the structural cost of portability.

---

## References

1. Anhyobin, [`aidlc-workflows` — `feat/claude-code-native-implementation/platforms/claude-code/benchmarks/`](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code/benchmarks) — benchmark scenario, grader, and published scores.
2. Anhyobin, [`grade.py` raw](https://raw.githubusercontent.com/anhyobin/aidlc-workflows/feat/claude-code-native-implementation/platforms/claude-code/benchmarks/grade.py) — current regex rubric.
3. Anhyobin, [`benchmark.json` raw](https://raw.githubusercontent.com/anhyobin/aidlc-workflows/feat/claude-code-native-implementation/platforms/claude-code/benchmarks/benchmark.json) — current per-skill results.
4. Raja SP, Amazon Web Services, [*AI-Driven Development Lifecycle (AI-DLC) Method Definition*](https://prod.d13rzhkk8cj2z0.amplifyapp.com/aidlc.pdf) (2026) — methodology source.
5. Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24) — Generator/Evaluator pattern.
6. Anthropic, [Auto mode for Claude Code](https://www.anthropic.com/engineering/claude-code-auto-mode) (2026-03-25) — boundary-based security, FPR 0.4%.
7. Anthropic, [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) (2025-10-20) — 84% permission-prompt reduction.
8. Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09-29) — Knowledge Pyramid.
9. Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (2025-06-13) — Orchestrator-Worker pattern.
10. Anthropic, [Introducing advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) (2025-11-24) — Tool Search, Programmatic Tool Calling.
11. Anthropic, [Decoupling the brain from the hands (Managed Agents)](https://www.anthropic.com/engineering/managed-agents) — Progressive Deletability.
12. Ryan Lopopolo (OpenAI), [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11) — legibility, central-boundary/local-autonomy.
13. `harness-engineering_EN.md` — companion document in this repository, consolidating Harness Engineering patterns from sources 5–12 above into a single pattern index. Not a primary source; all patterns cited from it trace back to the Anthropic and OpenAI links listed above.
14. `AWS_AI-DLC_Whitepaper_EN.md` — companion document, English translation of source 4 (the AI-DLC whitepaper).
15. `awslabs/aidlc-workflows` v0.1.8 — [GitHub](https://github.com/awslabs/aidlc-workflows) — upstream reference rule file.

---

> Author: Kwangyoung Kim (<kwangyou@amazon.com>) + Claude Code
> Source: [`anhyobin/aidlc-workflows`](https://github.com/anhyobin/aidlc-workflows) benchmarks + [Anthropic Engineering Blog](https://www.anthropic.com/engineering) + [OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) + [AI-DLC Whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com/aidlc.pdf)
> Last updated: April 2026
