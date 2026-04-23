# Project Mode: Prototyping vs Production

**Purpose**: AI-DLC and Harness Engineering solve different failure modes. AI-DLC's strength is **intent defects** caught by explicit human approval; HE's strength is **execution defects** caught by automated feedback loops. The right mix depends on whether the project is a **throwaway prototype** or a system that will be maintained.

This rule file lets the user (or the model) choose the mix at the start of every **Greenfield** project. Brownfield projects default to **Production** mode because real code is already in service.

---

## 1. Why Introduce a Project Mode

| Failure mode AI-DLC catches best | Failure mode HE catches best |
|---|---|
| A well-implemented *wrong feature* (misunderstood intent) | A badly-implemented *right feature* (bugs, regressions, architecture drift) |

- In a **prototype**, building the wrong feature is cheap — you iterate. The expensive failure is *spending a week of approval cycles on a throwaway*.
- In **production code**, building the wrong feature is expensive — retrofit and customer-impact cost. The expensive failure is *merging an unreviewed feature*.

The two frameworks push in opposite directions here:

- AI-DLC's default: *every stage ends with "Wait for Explicit Approval — DO NOT PROCEED"*. Safer for production, bottleneck for prototyping.
- HE's default: *Fix cost < Wait cost*. Auto-fix via L1–L4, human only at L5. Faster for prototyping, risky for regulated production.

**Project Mode picks the appropriate default and lets the user override per stage.**

---

## 2. The Two Modes

| Dimension | Prototyping Mode | Production Mode |
|---|---|---|
| Inception gates (Requirements / Stories / Workflow Planning) | **Present, abbreviated** — approve once, don't re-ask per refinement | **Full** — every stage ends in explicit approval |
| User Stories stage | Conditional, lean toward SKIP for solo prototypes | Conditional, lean toward EXECUTE |
| Application Design | Skip unless architecturally complex | Execute |
| NFR Requirements / NFR Design / Infrastructure Design | Skip by default | Execute per unit |
| Code Generation feedback levels | **L1–L4 automated + Auto Mode (if host supports)**; no human gate per unit | **L1–L3 automated + L4 AI review + L5 human gate per unit** |
| Generator/Evaluator multi-agent | Enabled if host supports | Enabled if host supports + **always** for `full-multi-agent` hosts |
| Boundary-Based Security (Construction) | Full — Tier 1+2 auto-approved, Tier 3 prompted | Full — same, plus pre-approved commands list published upfront |
| Build and Test final gate | **Present** — this is the one non-negotiable human gate | **Present** |
| Operations (Gardener / Health Report) | Optional post-hoc | Required after every Construction cycle |
| Extensions (security baseline, property-based testing) | Opt-in, default OFF | Opt-in, default ON for security baseline |

### 2.1 What stays the same in both modes

- **Audit trail** (`audit.md`) — mandatory, verbatim user input capture.
- **Question file format** — A/B/C/D/E with `[Answer]:` tag.
- **Content validation** — Mermaid / ASCII syntax checks before file write.
- **State persistence** — `aidlc-state.md` tracks mode, host agent profile, progress.
- **Final Build-and-Test gate** — human approval always required before declaring a unit complete.

### 2.2 What changes by mode

Only the **frequency** and **depth** of human approval and the **aggressiveness** of automated feedback change. The underlying artifacts produced per stage do not change (per `common/depth-levels.md`).

---

## 3. When to Ask for the Mode

### 3.1 Greenfield

Ask **once**, during **Requirements Analysis Step 5.1** (co-located with extension opt-ins). Use the question file format defined in `common/question-format-guide.md`.

### Project Mode Selection (Greenfield)

```markdown
## Project Mode

This is a Greenfield project. Please select the execution mode:

A) **Prototyping** — fast iteration, minimal human gates during Construction, automated L1–L4 feedback loops, Harness Engineering automation enabled. Recommended for: proof-of-concept, solo exploration, research spikes, throwaway demos.

B) **Production** — full AI-DLC human approval at every design stage, conservative automation, design stages (NFR / Infrastructure) execute by default. Recommended for: customer-facing features, regulated systems, code that will be maintained.

C) **Hybrid** — Production-grade gates for Inception (Requirements, Stories, Workflow Planning), Prototyping-grade speed for Code Generation within each unit. Recommended for: internal tools, time-boxed MVPs where intent must be right but implementation can iterate.

X) Other (please describe after [Answer]: tag below)

[Answer]:
```

Record in `aidlc-docs/aidlc-state.md`:

```markdown
## Project Mode
- **Mode**: [Prototyping | Production | Hybrid]
- **Decided At**: [ISO timestamp] — Requirements Analysis
- **Rationale**: [User-provided or model-inferred]
```

### 3.2 Brownfield

**Do not ask**. Brownfield defaults to **Production Mode** — the existing code is real and already-shipped. Record:

```markdown
## Project Mode
- **Mode**: Production (auto-selected for Brownfield)
- **Decided At**: [ISO timestamp] — Workspace Detection
- **Rationale**: Brownfield project, existing code in service.
```

The user can still override to Prototyping or Hybrid with an explicit request — useful for "let me do a spike on top of this codebase" scenarios.

---

## 4. Mode × Host Profile Interaction

Mode and host-agent capability profile are **orthogonal** — see `common/agent-capabilities.md`. The effective automation level is `min(mode_cap, host_cap)`.

| Mode | Host = `full-multi-agent` | Host = `subagent-only` | Host = `single-agent` |
|---|---|---|---|
| **Prototyping** | L1–L4 auto + Auto Mode + multi-agent Generator/Evaluator + worktree parallel units | L1–L4 auto + subagent-based sequential Evaluator + feature-branch isolation | L1–L4 auto + context-reset sequential Evaluator + feature-branch isolation |
| **Production** | L1–L3 auto + L4 AI review + **L5 per-unit human gate** + multi-agent Evaluator | L1–L3 auto + L4 AI review (sequential subagent) + L5 per-unit human gate | L1–L3 auto + L4 AI review (context-reset pass) + L5 per-unit human gate |
| **Hybrid** | Production-style Inception gates + Prototyping-style Construction (L1–L4 auto, no per-unit gate, multi-agent Evaluator) | Same shape, sequential | Same shape, sequential |

**Practical implication**: A Prototyping project on Kiro does NOT get Claude Code's worktree parallelism. It does get the L1–L4 automated feedback loop and the skipped per-unit human gate — the two biggest wins.

---

## 5. What Each Mode Changes in `core-workflow.md`

### 5.1 Prototyping Mode

- Requirements Analysis, User Stories, Workflow Planning, Application Design, Units Generation → **still ask for approval but present as a single "approve Inception package" gate at the end**, not per-stage.
- Functional Design, NFR Requirements, NFR Design, Infrastructure Design (Construction per-unit design stages) → **skipped by default** unless the user or the model flags a real need.
- Code Generation Part 1 (Planning) → still requires approval (high-stakes contract).
- Code Generation Part 2 (Generation) → **no per-unit human gate**; L1–L4 feedback runs automatically; escalate to human only on L4 failure after 2 auto-fix retries.
- Build and Test → **human gate retained** (final release check).

### 5.2 Production Mode

- Every stage keeps its current "Wait for Explicit Approval — DO NOT PROCEED" gate.
- Construction per-unit design stages (Functional Design, NFR Requirements, NFR Design, Infrastructure Design) run as CONDITIONAL per the existing logic.
- Code Generation Part 2 adds L1–L3 automated feedback **in addition to** the L5 human gate — the human gate is the final arbiter, but L1–L3 prevents sending obviously-broken code to review.
- L4 AI review runs before the L5 gate so the human sees a pre-reviewed diff.

### 5.3 Hybrid Mode

- Inception = Production (all human gates preserved).
- Construction = Prototyping (no per-unit gate, L1–L4 automated, Auto Mode if host supports).
- Build and Test = Production (final human gate retained).
- Operations = Production (Gardener scan required).

---

## 6. Operations Phase by Mode

| Mode | Operations Phase Behavior |
|---|---|
| Prototyping | Gardener scan is **opt-in**. Health Report generated only if user requests or harness learnings flag it. |
| Production | Gardener scan is **mandatory** after every Construction cycle. Health Report is a required artifact. |
| Hybrid | Same as Production. |

---

## 7. Defaults Summary

| If... | Default Mode |
|---|---|
| Brownfield | Production (user can override) |
| Greenfield, user picks A | Prototyping |
| Greenfield, user picks B | Production |
| Greenfield, user picks C | Hybrid |
| Greenfield, user picks X (custom) | Ask follow-up questions and synthesize a mix; record the synthesis |
| User does not answer | **Production** — safest default |

---

## 8. Mode Switching Mid-Project

A user can escalate mode mid-project. Example: a Prototyping project that succeeded and is now going to production.

```markdown
Escalation Prototyping → Production
- At the transition, add: per-unit design stages (NFR Requirements, NFR Design, Infrastructure Design), L5 per-unit human gate, Gardener scan.
- Re-run Operations phase on the accumulated prototype code before declaring production-ready.
```

A user can **de-escalate** too (rare — Production → Prototyping for a feature spike). Record the transition in `aidlc-state.md`:

```markdown
## Mode Transitions
- 2026-04-21T14:00:00Z — Prototyping → Production — reason: "going to pilot with 3 customers"
```

---

> Author: Kwangyoung Kim (kwangyou@amazon.com) + Claude Code
> Source: [harness-engineering_EN.md](../../../../harness-engineering_EN.md) + [AWS_AI-DLC_Whitepaper_KO.md](../../../../AWS_AI-DLC_Whitepaper_KO.md) + [HE_Perspective_on_AIDLC_EN.md](../../../../HE_Perspective_on_AIDLC_EN.md)
> Last updated: April 2026
