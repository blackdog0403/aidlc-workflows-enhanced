# Multi-Agent Patterns for Construction Phase

## Host Capability Required

- **Reads axis**: `multi_agent` for Generator/Evaluator separation and Pattern 2; `worktree` for Pattern 3 parallel execution. Values come from `aidlc-docs/aidlc-state.md` under `## Host Capabilities`.
- **When `multi_agent` is `native`**: agent-calls-agent orchestration (Claude Code `Agent` tool, Copilot `agent` tool).
- **When `multi_agent` is `user-launched`**: user-initiated subagents (Kiro CLI `.kiro/agents/*.json`, Cursor `/multitask`, Cline `use_subagents`) with explicit context reset between roles.
- **When `multi_agent` is `none`**: single agent with forced context reset (`/clear` or equivalent) between Generator and Evaluator passes.
- **When `worktree` is `native`**: parallel worktree execution (Claude Code, Cursor Agents Window, Cline New Worktree Window).
- **When `worktree` is `per-task-vm`**: coding-agent per-task ephemeral VMs (GitHub Copilot coding-agent).
- **When `worktree` is `none`**: sequential feature-branch loop.
- See `common/agent-capabilities.md` §3.1, §3.2, §3.3 for the full strategy tables.

**None of these paths refuse to proceed.** Degrade gracefully. The load-bearing invariant is **separation of Generator and Evaluator contexts**, not the specific mechanism that achieves it.

---

## Problem Statement

AI-DLC v0.1.8 assumed a **single agent** handling all tasks sequentially. This creates:
- **Self-Evaluation Bias** — an agent positively evaluates its own output regardless of quality
- **Sequential bottleneck** — units processed one-by-one even when independent
- **No specialization** — the same agent does generation, review, and testing

> "Tuning an independent evaluator to be skeptical is far easier than making a generator self-critical."
>
> — Anthropic, [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24)

The structural fix is **separation of concerns**. How to achieve the separation depends on what the host agent supports.

---

## Pattern 1: Generator / Evaluator (Two-Agent System)

The minimum-viable pattern. The agent that generates is **never** the same context that evaluates.

### Why This Works (Anthropic's Research)

Anthropic's harness design research identified **self-evaluation bias** as a core failure mode:

> "When asked to evaluate work they've produced, agents tend to respond by confidently praising the work—even when, to a human observer, the quality is obviously mediocre."
>
> — Anthropic, [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24)

### 1.A When `multi_agent` is `native` (e.g., Claude Code, GitHub Copilot)

Two distinct agents, separate contexts, real orchestration.

```
Generator Agent (Sonnet, /effort high)
    ├── loaded with: architecture, functional design, coding standards
    ├── writes code
    └── Agent tool → invokes Evaluator

Evaluator Agent (Sonnet, /effort max — skeptical system prompt)
    ├── loaded with: architecture, requirements, security rules, test specs
    ├── reviews with fresh context (NOT the generator's context)
    └── returns: issues | approved
```

**Subagent definition template** — place under `.claude/agents/`:

```markdown
---
name: aidlc-evaluator
model: sonnet
description: Skeptical code reviewer for AI-DLC Construction Phase. Invoked by aidlc-generator after each unit's Code Generation Part 2 completes. Assumes there are bugs until proven otherwise.
---

You are a code reviewer. Assume the submitted code contains bugs, architecture violations, or missing edge cases until proven otherwise. Cite specific files and line numbers. Your output:
- CRITICAL issues (must fix)
- WARNINGS (should fix)
- APPROVED (if clean)
```

Interaction:
1. Generator creates code for a unit.
2. Generator invokes Evaluator via Agent tool with paths to artifacts.
3. Evaluator reviews with fresh context.
4. If issues found → Generator fixes → Evaluator re-reviews (max 2 rounds).
5. If clean → proceed to next unit.
6. If unresolved after 2 rounds → escalate to human (L5).

### 1.B When `multi_agent` is `user-launched` (e.g., Kiro CLI, Cursor, Cline)

One agent session, **two sequential passes with forced context reset**. The subagent definition file is used to switch roles, not to orchestrate parallelism.

Interaction:
1. Generator pass — using the `aidlc-generator` subagent/steering profile — creates code.
2. Save artifacts to disk; summarize state in `aidlc-state.md`.
3. **Context reset** — start a fresh session (or use the host's "clear context" command) and load the `aidlc-evaluator` subagent/steering profile. Load only the generated artifacts, design docs, and acceptance criteria — **not the generator's reasoning trace**.
4. Evaluator reviews and writes findings to `aidlc-docs/construction/{unit-name}/review.md`.
5. If issues → load generator profile again, fix, loop (max 2 rounds).
6. If unresolved → escalate to human.

**Kiro IDE specifics**: create two `.kiro/steering/` files — one per role — and switch active steering between passes. Kiro IDE does not have an agents directory; steering is the only mechanism.

**Kiro CLI specifics**: create two `.kiro/agents/*.json` files (per `kiro.dev/docs/cli/custom-agents/`) — one per role — and launch the evaluator agent by name for the second pass. Kiro CLI can also run PreToolUse hooks to enforce the context reset if desired.

### 1.C When `multi_agent` is `none` (e.g., Amazon Q IDE, Kiro IDE)

One agent, two passes, context reset is the only isolation mechanism.

Interaction:
1. Generator pass — system prompt includes "You are writing code. Do NOT evaluate in this pass."
2. Save artifacts; update `aidlc-state.md`.
3. Issue `/clear` (or equivalent) **and** remind the user to confirm the context is clear. This is the weakest separation — log a note in `audit.md` indicating the context reset relies on user cooperation.
4. Evaluator pass — system prompt includes "You are a skeptical reviewer. Assume bugs exist. You did NOT write this code." Load only artifacts + design docs.
5. Findings → re-enter Generator pass for fix loop (max 2 rounds).
6. Escalate to human if unresolved.

---

## Pattern 2: Three-Agent Architecture (Planner / Generator / Evaluator)

For long-running autonomous coding (multi-hour sessions) Anthropic uses a three-agent architecture:

```
Planner → Generator ⟷ Evaluator
```

### Key Design Decisions from Anthropic

1. **Evaluator navigates, doesn't just read** — the evaluator actively inspects the implementation (screenshots UI, runs code), not just static review.
2. **Concrete grading criteria, not vibes** — "Does it follow the design doc? Does it handle the listed edge cases? Does it pass the acceptance criteria?"
3. **Strategic decisions after evaluation** — after each round, Generator chooses: refine current approach, or try a different approach.
4. **5–15 iterations per generation** — multiple rounds push quality higher.
5. **Context resets between features** — hand off via structured artifacts.

> "The final result was a three-agent architecture—planner, generator, and evaluator—that produced rich full-stack applications over multi-hour autonomous coding sessions."
>
> — Anthropic, [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24)

### Mapping to AI-DLC

| AI-DLC Stage | Planner | Generator | Evaluator |
|---|---|---|---|
| Inception (Requirements → Units Generation) | Active | — | — |
| Code Generation Part 1 (Planning) | Produces plan | — | Reviews plan completeness |
| Code Generation Part 2 (Generation) | — | Writes code | Reviews code quality |
| Build and Test | — | — | Validates tests, coverage, acceptance |

### Capability branching

Use the `agent-capabilities.md` §3.2 strategy table. When `multi_agent` is `none`, the Planner role is the `/effort max` pass at Inception; Generator is `/effort high` during Construction Part 2; Evaluator is a separate `/effort max` pass with cleared context. This is the Reasoning Sandwich (see §4).

---

## Pattern 3: Parallel Unit Execution

### 3.A When `worktree` is `native` (e.g., Claude Code, Cursor, Cline)

Claude Code has **native worktree support**:

```bash
claude --worktree unit-a
claude --worktree unit-b --tmux
claude --worktree unit-c --tmux
```

Or, in a subagent definition:

```markdown
---
name: worktree-worker
model: sonnet
isolation: worktree
---
```

For large migrations: `/batch` fans out to dozens/hundreds of worktree agents, each testing independently, each opening a PR.

Architecture:

```
Units Generation identifies:
  Unit A ─── independent ─── Unit B ─── independent ─── Unit C
                    │
                    ▼
  Parallel execution:
  [Worktree Agent 1: Unit A]  [Worktree Agent 2: Unit B]  [Worktree Agent 3: Unit C]
                    │
                    ▼
  Integration + Build and Test (sequential, all units together)
```

**Prerequisites**:
- Units have no code-level dependencies (checked in Units Generation).
- Each agent works in an isolated git worktree.
- Shared: architecture docs, requirements, coding standards.
- Not shared: code in progress, agent memory.

**Conflict resolution**:
- If two agents modify the same file → sequential retry.
- Integration tests run after all parallel units complete.
- Human review of integration points.

### 3.B When `worktree` is `per-task-vm` (e.g., GitHub Copilot coding-agent)

Dispatch each unit as its own coding-agent task. Each task runs on a remote ephemeral VM on its own branch, so N units can be dispatched in parallel. The agent integrates via PRs rather than local git worktrees.

### 3.C When `worktree` is `none` (e.g., Amazon Q IDE, Kiro IDE, Kiro CLI)

**No parallelism** — execute the per-unit loop sequentially. Isolate each unit on its own **feature branch**:

```bash
git checkout -b aidlc/unit-a
# ... run full per-unit Construction loop ...
git commit -am "aidlc: complete unit-a"

git checkout main
git checkout -b aidlc/unit-b
# ...
```

Merge all feature branches at Build and Test time. Log in `aidlc-state.md`:

```markdown
## Parallelism
- **Host Supports**: No
- **Isolation Strategy**: Feature branches (sequential)
- **Branches**: aidlc/unit-a, aidlc/unit-b, aidlc/unit-c
```

The user should know they are leaving performance on the table by not using a `worktree: native` or `worktree: per-task-vm` host for a large project. Surface this in the Workflow Planning recommendations when there are 5+ independent units.

---

## Pattern 4: Architect-Implementer Split

For complex projects, separate planning from execution across agent roles. This is conceptually the three-agent pattern mapped to AI-DLC phases.

| Role | Scope | Model tier (if Cost Optimization extension enabled) |
|---|---|---|
| **Architect** | Inception phase (requirements, design, unit planning) | Premium — Opus 4.7 |
| **Implementer(s)** | Construction phase (code generation per unit) | Standard — Sonnet 4.6 |
| **Reviewer** | Cross-cutting (code review, architecture compliance) | Standard with skeptical tuning |

### Reasoning Sandwich

Different reasoning intensity at different stages produces a measured quality lift:

| Phase | Reasoning Level | Rationale |
|---|---|---|
| Planning (Inception) | **High** (`/effort max`) | Architecture decisions are high-stakes |
| Implementation (Construction Part 2) | **Standard** (`/effort high`) | Well-constrained by prior design |
| Verification (Build & Test, Evaluator) | **High** (`/effort max`) | Catching bugs is critical |

> The "xhigh-high-xhigh" (a.k.a. max-high-max) pattern delivered **+12.6pp over uniform high** on LangChain TerminalBench 2.0.
>
> — Ref: [LangChain TerminalBench 2.0](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)

Applies **regardless of host capabilities** — hosts with `multi_agent: none` still benefit from switching `/effort` tiers per phase.

---

## Pattern Selection Guide

| Situation | Recommended Pattern | Requires | Cost |
|---|---|---|---|
| Simple change, 1–3 files | Single agent, no Evaluator | any host | $ |
| Prototyping mode, 3–10 units | Generator + Evaluator | any host (use capability fallback) | $$ |
| Production mode, 3–10 units | Generator + Evaluator + L5 per-unit human gate | any host | $$$ |
| Large project, 10+ independent units | Parallel execution + Evaluator | `worktree: native` or `worktree: per-task-vm` | $$$ |
| Complex architecture, high-risk | Architect-Implementer + Evaluator + Reasoning Sandwich | `multi_agent: native` preferred; degrades on others | $$$$ |

See `common/project-mode.md` for how Prototyping vs Production vs Hybrid interacts with these pattern choices.

---

## Integration with `aidlc-state.md`

```markdown
## Agent Configuration
- **multi_agent axis**: [native | user-launched | none] (from `## Host Capabilities`)
- **worktree axis**: [native | per-task-vm | none] (from `## Host Capabilities`)
- **Pattern**: [Single | Generator-Evaluator | Planner-Generator-Evaluator | Parallel | Architect-Implementer]
- **Generator Role**: [Model / subagent file / inline]
- **Evaluator Role**: [Model / subagent file / inline]
- **Parallelism**: [worktree | feature-branches-sequential | none]
- **Parallel Units** (if applicable): [List of units running in parallel]
- **Review Rounds Remaining**: [N]
- **Reasoning Sandwich**: [enabled | disabled]
```

---

## Escalation Protocol

When L1–L4 automated feedback + 2 rounds of Generator/Evaluator iteration fail to converge, **escalate to human review**:

1. Write the full issue list to `aidlc-docs/construction/{unit-name}/escalation.md`.
2. Include: what was attempted, why it failed, Evaluator's final findings.
3. Present to user with the standardized "WHAT'S NEXT?" block from `core-workflow.md`.
4. Do NOT continue until the user provides guidance.

This is the one point where the Generator/Evaluator loop re-connects to AI-DLC's explicit human-approval spine.

---

## References

1. Anthropic, [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03-24)
2. Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (2025-06-13)
3. Anthropic, [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips)
4. LangChain, [Improving Deep Agents with Harness Engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering) (2026-02-17)
5. [common/agent-capabilities.md](../common/agent-capabilities.md)
6. [common/project-mode.md](../common/project-mode.md)

---

> Author: Kwangyoung Kim (<kwangyou@amazon.com>) + Claude Code
> Source: Anthropic Engineering Blogs + [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips)
> Last updated: April 2026
