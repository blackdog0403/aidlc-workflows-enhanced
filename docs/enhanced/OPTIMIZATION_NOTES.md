# AI-DLC Optimized Rules — Optimization Notes

Summary of changes introduced in the April 2026 revision and the design invariants preserved across them.

> [!NOTE]
> **Key Takeaways**
>
> - AI-DLC's explicit human-decision gates (L1/L5 in the AI-DLC sense: intent at Inception, approval at Construction, release at Build & Test) are preserved; HE's automated L1–L4 feedback loop runs *inside* them.
> - A new capability layer (`common/agent-capabilities.md`) detects the host agent (Claude Code / Kiro / Amazon Q / Cursor / Cline / GitHub Copilot) and collapses it into three profiles — `full-multi-agent`, `subagent-only`, `single-agent` — that downstream rules branch on.
> - A new mode layer (`common/project-mode.md`) asks Greenfield projects once — Prototyping / Production / Hybrid — and toggles gate density accordingly. Brownfield auto-selects Production.
> - Multi-agent, worktree-parallel, and sandbox patterns **degrade gracefully** rather than refusing to run. The invariant preserved across all profiles is **separation of Generator and Evaluator contexts**, not a specific mechanism (Agent tool vs context reset vs fresh session).
> - The Build & Test final gate and the `audit.md` verbatim rule remain non-negotiable in every mode.

## Table of Contents

- [What Changed and Why](#what-changed-and-why)
- [Design Invariants Preserved](#design-invariants-preserved)
- [What's Intentionally Unchanged](#whats-intentionally-unchanged)
- [References](#references)

---

## What Changed and Why

### 1. New `common/agent-capabilities.md`

- Capability matrix for 6 hosts × 10 capabilities.
- Detection protocol (path-based + self-report override).
- Three capability profiles for downstream branching.
- Fallback rules for multi-agent, worktree, sandboxing, hooks, auto-memory, tool search.
- **Rule for downstream files**: declare required capability and link §3 fallback table; never hardcode `claude --worktree`.

### 2. New `common/project-mode.md`

- Greenfield asks A/B/C/X during Requirements Analysis Step 5.1.
- Brownfield auto-defaults to Production.
- Mode × Host Profile matrix defines the **effective automation = min(mode_cap, host_cap)**.
- Mode switching protocol (e.g., Prototyping → Production when a prototype graduates).

### 3. Rewritten `construction/multi-agent-patterns.md`

- Three implementation paths per pattern:
  - `full-multi-agent` — real `Agent` tool orchestration + worktrees.
  - `subagent-only` — sequential subagent passes with context reset between roles (Kiro / Amazon Q steering).
  - `single-agent` — sequential passes with `/clear`-style resets + feature-branch isolation (Cursor / Cline / Copilot).
- Pattern 1 (Generator/Evaluator), Pattern 2 (three-agent Planner/Generator/Evaluator), Pattern 3 (parallel units), Pattern 4 (Architect-Implementer + Reasoning Sandwich).
- Escalation protocol reconnects to AI-DLC's L5 human-approval spine when L1–L4 + 2 auto-fix rounds fail.

### 4. Updated `aws-aidlc-rules/core-workflow.md`

- Loads the capability and mode files **at workflow start**, before any multi-agent/parallel decision.
- Adds a summary table showing how Project Mode modulates approval gates in each phase.
- Code Generation (per-unit) now has mode-dependent behavior: L5 human gate in Production; auto-proceed in Prototyping/Hybrid unless L4 escalates.

### 5. Updated `construction/code-generation.md`

- New **Step 13.5** runs L1–L4 feedback automatically; auto-fixes up to 2 rounds; escalates on failure.
- **Step 14** completion message is mode-aware: standard 2-option block in Production; auto-proceed notice in Prototyping/Hybrid.
- Step 15/16 split into Production gate vs Prototyping/Hybrid auto-proceed paths.

### 6. Updated `inception/workspace-detection.md`

- **New Step 0** runs host-agent detection (capability profile) and records it in `aidlc-state.md`.
- State file template now includes `## Host Agent` and `## Project Mode` blocks.
- Brownfield immediately sets Project Mode = Production.

### 7. Updated `inception/requirements-analysis.md`

- **Step 5.1** now asks the Project Mode question (Greenfield only) before extension opt-ins.

### 8. Updated `inception/workflow-planning.md`

- Reads Project Mode and Capability Profile before planning.
- Warns user when they are leaving parallelism on the table (5+ independent units but host is not `full-multi-agent`).

### 9. Updated `construction/build-and-test.md`

- Capability block notes that `full-multi-agent` hosts can wire L1–L3 to `PostToolUse` hooks; other hosts run as in-prompt step.
- Final human gate is **retained in all modes** — this is the load-bearing AI-DLC invariant HE's "fix cost < wait cost" cannot override.

### 10. Updated `common/welcome-message.md`

- Adds Host-Aware and Mode-Aware bullets.
- Step list reflects detection + mode selection in the Inception phase.

### 11. Trimmed for length (no semantic loss)

| File                              | Before    | After      | Notes                                                                                                                        |
|-----------------------------------|-----------|------------|------------------------------------------------------------------------------------------------------------------------------|
| `common/error-handling.md`        | 373 lines | ~170 lines | Collapsed near-duplicate per-stage blocks into a table; kept all error → action mappings.                                    |
| `common/workflow-changes.md`      | 285 lines | ~95 lines  | Replaced the 8 change-type sections with a universal protocol + 8-row pattern table.                                         |
| `common/question-format-guide.md` | 332 lines | ~150 lines | Removed redundant examples; kept the single canonical template, validation responses, and the contradiction-detection block. Re-added an explicit Quality Bar (5-point) and Anti-Pattern (Yes/No/Maybe filler) block after initial trimming proved too aggressive for weaker models. |

Total rule corpus: **6650 → 5949 lines** (~11% reduction) while **adding** two new rule files and the capability-aware paths.

---

## Design Invariants Preserved

**From AI-DLC:**

- **Verbatim `audit.md`** — every user input captured raw; never summarized.
- **Question-file format** — A/B/C/D/E + mandatory `Other`, `[Answer]:` tag.
- **Build and Test human gate** — non-negotiable, all modes.
- **Content validation** before file write (Mermaid / ASCII syntax).
- **State persistence** — `aidlc-state.md` tracks every decision.

**From Harness Engineering:**

- **Separation of Generator and Evaluator** — structural, not prompt-based.
- **Deterministic-before-AI** — L1–L3 always run before L4; L4 only after L1–L3 pass.
- **Context reset between units** — saved state + fresh context, not compaction.
- **Boundary-based trust** — Tier 1/2 auto-approved, Tier 3 prompted.
- **Reasoning Sandwich** — `/effort` levels per phase (max-high-max) even on single-agent hosts.

---

## What's Intentionally Unchanged

- All Inception `*.md` files' stage structure (Requirements / Stories / Workflow Planning / etc.) keep their question-and-approval shape. Only the gate *enforcement* changes by mode.
- Extension opt-in/opt-out mechanism in Step 5.1.
- `code-generation.md` Part 1 (Planning) approval — required in **all modes** because it's a high-stakes contract.
- Gardener / Health Report structure in Operations.

---

## References

1. `harness-engineering_EN.md` — internal working note, not included in this repo
2. `HE_Perspective_on_AIDLC_EN.md` — internal working note, not included in this repo
3. `AIDLC_Perspective_on_HE_EN.md` — internal working note, not included in this repo
4. [AWS AI-DLC Whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com/) (Method Definition Paper)
5. Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24)
6. Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

---

**Author:** Kwangyoung Kim (<kwangyou@amazon.com>) + Claude Code
**Source:** internal working notes + [AWS AI-DLC Whitepaper](https://prod.d13rzhkk8cj2z0.amplifyapp.com/) + Anthropic Engineering Blogs
**Last updated:** April 2026
