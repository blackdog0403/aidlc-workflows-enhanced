# Agent Capability Detection & Adaptation

**Purpose**: AI-DLC rules must adapt to the capabilities of the **host agent** (the IDE or CLI running this workflow). A rule that assumes Claude Code's worktree isolation will silently fail on Kiro, which does not yet support multi-agent orchestration. A rule written for a single agent leaves Claude Code's Generator/Evaluator power unused.

This file defines:
1. A **capability matrix** listing the features each host agent supports.
2. A **detection protocol** — how the agent identifies itself at workflow start.
3. **Fallback rules** — how higher-order patterns (multi-agent, worktree, hooks) degrade when a capability is missing.

All other rule files that depend on multi-agent, worktree isolation, sandboxing, or hook execution **MUST reference this file** and branch their behavior accordingly.

---

## 1. Capability Matrix

| Capability | Claude Code | Cursor | Cline | Amazon Q Dev | Kiro | GitHub Copilot |
|---|---|---|---|---|---|---|
| **Subagent definition files** (single-file role prompts) | ✅ `.claude/agents/` | ⚠️ rules only | ⚠️ rules only | ⚠️ rules only | ✅ steering/agents | ⚠️ instructions only |
| **Multi-agent orchestration** (agent calls agent) | ✅ `Agent` tool | ❌ | ❌ | ❌ | ❌ (roadmap) | ❌ |
| **Parallel worktree execution** | ✅ `--worktree`, `isolation: worktree` | ❌ | ❌ | ❌ | ❌ | ❌ |
| **OS-level sandbox** | ✅ `bubblewrap`/`seatbelt` | ⚠️ manual | ⚠️ manual | ⚠️ IAM-scoped | ⚠️ manual | ❌ |
| **Boundary / Auto mode** | ✅ Auto Mode (FPR 0.4%) | ⚠️ basic allow-lists | ⚠️ basic | ⚠️ basic | ⚠️ basic | ❌ |
| **Lifecycle hooks** (PreToolUse/PostToolUse/Stop) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Auto-memory / cross-session consolidation** | ✅ AutoDream | ❌ | ❌ | ⚠️ partial | ✅ steering | ❌ |
| **Tool Search / defer_loading** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **File-based rule loading** | ✅ `.claude/` | ✅ `.cursor/rules/` | ✅ `.clinerules/` | ✅ `.amazonq/` | ✅ `.kiro/` | ✅ `.github/` |
| **Structured question files** (AI-DLC pattern) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Legend: ✅ native support · ⚠️ partial / workaround · ❌ not supported at date of this rule file.

> **Caveat**: Capability support evolves fast. Treat the matrix as "as of 2026-04"; when the host agent advertises a different capability, trust the host.

---

## 2. Detection Protocol

At workflow start (before any Construction-phase rule is loaded), the model **must resolve which host agent is running** and record it in `aidlc-docs/aidlc-state.md`.

### Step 2.1 — Path-based detection

Check in order, record the first match:

| Rule-details path present | Default host agent |
|---|---|
| `.claude/` or `.aidlc-rule-details/` + Claude Code session | **claude-code** |
| `.kiro/aws-aidlc-rule-details/` | **kiro** |
| `.amazonq/aws-aidlc-rule-details/` | **amazon-q-dev** |
| `.cursor/rules/` | **cursor** |
| `.clinerules/` | **cline** |
| `.github/` (Copilot) | **github-copilot** |
| `.aidlc/aidlc-rules/aws-aidlc-rule-details/` (generic) | **unknown — ask the user** |

### Step 2.2 — Self-report override

If the model has direct knowledge of the host (e.g., the system prompt identifies itself as Claude Code / Kiro), that self-report **overrides path detection**.

### Step 2.3 — Record to state

Write to `aidlc-docs/aidlc-state.md`:

```markdown
## Host Agent
- **Detected Host**: [claude-code | cursor | cline | amazon-q-dev | kiro | github-copilot | unknown]
- **Detection Method**: [self-report | path-based | user-confirmed]
- **Capability Profile**: [full-multi-agent | subagent-only | single-agent]
- **Decided At**: [ISO timestamp]
```

### Step 2.4 — Capability profile mapping

Collapse the matrix into three profiles for downstream rules to branch on:

| Profile | Host Agents | What it unlocks |
|---|---|---|
| `full-multi-agent` | claude-code | Generator/Evaluator via `Agent` tool, worktree parallel units, lifecycle hooks, Auto Mode |
| `subagent-only` | kiro, amazon-q-dev (with steering/agent files) | Specialized prompt roles via subagent files, but sequential only — no agent-calls-agent |
| `single-agent` | cursor, cline, github-copilot | One agent executes end-to-end; patterns emulated via context resets, not parallelism |

If the host is **unknown**, default to `single-agent` and ask the user.

---

## 3. Fallback Rules (Feature-by-Feature)

When a downstream rule file requires a capability the host doesn't have, apply these fallbacks. **Never refuse to proceed** — degrade to the next-best pattern.

### 3.1 Multi-Agent Orchestration

| Required by | `full-multi-agent` | `subagent-only` | `single-agent` |
|---|---|---|---|
| Generator/Evaluator (Code Generation) | Two distinct agents, separate contexts; Evaluator invoked via Agent tool | One agent, two sequential passes in **fresh contexts** (context reset between passes); Evaluator pass uses a separate subagent definition file if one exists | One agent, two sequential passes with context reset; Evaluator prompt is inlined from `construction/multi-agent-patterns.md` |
| Planner / Generator / Evaluator (Anthropic 3-agent) | Three agents, chained via Agent tool | Three sequential passes, each with its own subagent file + context reset | Three sequential passes in one agent; explicit between-pass reset via `/clear` or equivalent |
| Parallel unit execution | `--worktree` or `isolation: worktree` per unit, N worktrees in parallel | **Sequential** per-unit loop (no parallelism); log this as a known limitation | **Sequential** per-unit loop |

**Universal fallback rule**: the *separation of concerns* between Generator and Evaluator must be preserved even in `single-agent` mode — via a **context reset** between passes. Never let the generator "review its own work" in the same context.

### 3.2 Worktree Isolation

| Host profile | Strategy |
|---|---|
| `full-multi-agent` | Use `claude --worktree <unit-name>` or subagent `isolation: worktree`. Merge via git after all parallel units pass L3. |
| `subagent-only` / `single-agent` | Emulate isolation via **feature branches**: `git checkout -b aidlc/<unit-name>` before each unit, commit at unit completion, merge after Build and Test. No parallelism. |

### 3.3 Sandboxing & Boundary-Based Security

See `common/boundary-based-security.md`. Branching summary:

| Host profile | Boundary enforcement |
|---|---|
| `full-multi-agent` with Auto Mode | Use Auto Mode classifier for real-time boundary evaluation. Tier 1+2 auto-approved; Tier 3 raises approval prompt. |
| `full-multi-agent` without Auto Mode | Pre-declare pre-approved commands in `aidlc-state.md`; host confirms Tier 3. |
| `subagent-only` / `single-agent` | Rely on host's built-in permission prompts; publish a **Pre-Approved Commands** list at Construction start and ask the user to whitelist once. Every non-whitelisted Tier 3 action still prompts. |

### 3.4 Lifecycle Hooks (PreToolUse / PostToolUse / Stop)

| Host profile | Strategy |
|---|---|
| `full-multi-agent` | Wire L1 (per-file) checks to `PostToolUse` (on Write/Edit) so every file write triggers syntax + forbidden-pattern scans without a model turn. |
| `subagent-only` / `single-agent` | L1 checks run as an **in-prompt post-step** after each file write (one model turn cost). Log the turn cost — this is the price of not having hooks. |

### 3.5 Auto-Memory / Cross-Session Consolidation

| Host profile | Strategy |
|---|---|
| `full-multi-agent` (AutoDream) + `subagent-only` (Kiro steering) | Let the host's native memory system carry learned patterns across sessions; the Gardener Agent proposes rule-file updates. |
| `single-agent` | Persist cross-session learning to `aidlc-docs/operations/harness-learnings.md`; reload at workflow start as context. |

### 3.6 Tool Search / Defer-Loading

| Host profile | Strategy |
|---|---|
| `full-multi-agent` | Use native Tool Search: rules loaded on-demand per stage. |
| `subagent-only` / `single-agent` | Use AI-DLC's existing `*.opt-in.md` convention + staged loading from `common/context-optimization.md` as the equivalent mechanism. |

---

## 4. How Downstream Rules Must Reference This File

Any rule file describing a multi-agent / parallel / hooked pattern **must**:

1. Open with a short "Host capability required" note.
2. Reference this file: `See common/agent-capabilities.md §3.N for fallback.`
3. Provide the `full-multi-agent` path as the primary recipe and the `single-agent` path as the fallback recipe.
4. **Never** hardcode `claude --worktree` or Agent-tool calls without a capability check.

### Template

```markdown
## Host Capability Required
- **Primary (full-multi-agent)**: [what the pattern expects]
- **Fallback (subagent-only / single-agent)**: [the degraded path]
- See `common/agent-capabilities.md` §3.[subsection] for the full fallback table.
```

---

## 5. When the User Can Override

At Workflow Planning, the user can force a profile lower than detected (e.g., "I'm on Claude Code but prefer single-agent for this small task to save cost"). Record the override:

```markdown
## Host Agent — User Override
- **Detected Profile**: full-multi-agent
- **Active Profile**: single-agent
- **Reason**: [user-provided]
- **Decided At**: [ISO timestamp]
```

**User cannot force a profile HIGHER than detected** — the capability simply does not exist. If the user asks for multi-agent on Kiro, reply with the capability matrix in §1 and propose the `subagent-only` fallback.

---

## 6. Updating the Matrix

This file's matrix is a **snapshot**. When a host ships a new capability (e.g., Kiro adds multi-agent), update only the matrix and the fallback table — downstream rule files automatically inherit the change because they branch on the profile, not on the host name.

---

> Author: Kwangyoung Kim (<kwangyou@amazon.com>) + Claude Code
> Source: [harness-engineering_EN.md](../../../../harness-engineering_EN.md) + [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips) + host-agent documentation as of 2026-04
> Last updated: April 2026
