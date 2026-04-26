# Agent Capability Detection & Adaptation

**Purpose**: AI-DLC rules must adapt to the capabilities of the **host agent** (the IDE or CLI running this workflow). A rule that assumes Claude Code's worktree isolation will silently fail on Kiro, which does not yet support multi-agent orchestration. A rule written for a single agent leaves Claude Code's Generator/Evaluator power unused.

This file defines:
1. A **capability matrix** listing the features each host agent supports.
2. A **detection protocol** — how the agent identifies itself at workflow start.
3. **Fallback rules** — how higher-order patterns (multi-agent, worktree, hooks) degrade when a capability is missing.

All other rule files that depend on multi-agent, worktree isolation, sandboxing, or hook execution **MUST reference this file** and branch their behavior accordingly.

---

## 1. Capability Matrix

| Capability | Claude Code | Cursor | Cline | Amazon Q IDE | Kiro IDE | Kiro CLI | GitHub Copilot |
|---|---|---|---|---|---|---|---|
| **Subagent definition files** (single-file role prompts) | ✅ `.claude/agents/` | ⚠️ rules only | ⚠️ skills + read-only subagents | ⚠️ rules only | ⚠️ steering only | ✅ `.kiro/agents/*.json` | ✅ `.github/agents/*.agent.md` |
| **Multi-agent orchestration** (agent calls agent) | ✅ `Agent` tool | ⚠️ `/multitask` (auto-decomposed) | ⚠️ `use_subagents` (read-only, no nesting) | ❌ | ❌ | ⚠️ subagents (user-launched, CLI 2.0/2.1) | ✅ `agents` frontmatter + `agent` tool |
| **Parallel worktree execution** | ✅ `--worktree`, `isolation: worktree` | ✅ Agents Window worktrees | ✅ New Worktree Window | ❌ | ❌ | ❌ | ⚠️ coding-agent per-task VM only |
| **OS-level sandbox** | ✅ `bubblewrap`/`seatbelt` | ⚠️ sandboxed terminals | ⚠️ manual | ⚠️ IAM-scoped | ⚠️ manual | ❌ (tool-trust only) | ⚠️ preview (macOS/Linux) |
| **Boundary / Auto mode** | ✅ Auto Mode | ⚠️ allow-lists + sandbox fallback | ⚠️ model `requires_approval` flag | ⚠️ basic | ⚠️ basic | ⚠️ pre-approved tool lists (per agent) | ⚠️ Autopilot (auto-approve all, experimental) |
| **Lifecycle hooks — observe/feedback** (run script on event, pipe output to agent) | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ (`AgentSpawn`, `UserPromptSubmit`) | ✅ |
| **Lifecycle hooks — block triggering action** (non-zero exit cancels the action) | ✅ (exit 2 on PreToolUse + others) | ✅ (exit 2) | ✅ (`cancel: true`) | ❌ | ✅ (Pre Tool Use, Prompt Submit) | ✅ (`PreToolUse` exit 2) | ✅ (exit 2 / `permissionDecision: deny`) |
| **Auto-memory / cross-session consolidation** | ✅ auto memory (`MEMORY.md`) | ✅ Memories | ⚠️ Memory Bank (manual trigger) | ⚠️ partial | ⚠️ user-edited steering | ❌ (manual session resume only) | ⚠️ Copilot Memory (preview) |
| **Tool Search / defer_loading** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ MCP on-demand (CLI 2.1) | ❌ |
| **File-based rule loading** | ✅ `.claude/` | ✅ `.cursor/rules/` | ✅ `.clinerules/` | ✅ `.amazonq/` | ✅ `.kiro/steering/` | ✅ `.kiro/steering/` | ✅ `.github/` |
| **Structured question files** (AI-DLC pattern) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Legend: ✅ native support · ⚠️ partial / workaround · ❌ not supported at date of this rule file.

> **Caveat**: Capability support evolves fast. Most entries were re-verified 2026-04-25 against host documentation; cells carrying version pins (e.g. "CLI 2.1", "preview") reflect the state of the referenced release. Sources consulted on 2026-04-25: [code.claude.com/docs](https://code.claude.com/docs/) (Claude Code), [cursor.com/changelog](https://cursor.com/changelog) (Cursor 1.0 / 1.7 / 3.2), [docs.cline.bot](https://docs.cline.bot/) (Cline v3.56–v3.81), [kiro.dev/docs/hooks/](https://kiro.dev/docs/hooks/) (Kiro IDE hooks), [kiro.dev/docs/cli/](https://kiro.dev/docs/cli/) (Kiro CLI 2.0/2.1, incl. `/docs/cli/hooks/` and `/docs/cli/custom-agents/`), [code.visualstudio.com/docs/copilot](https://code.visualstudio.com/docs/copilot/) (Copilot, custom-agents docs updated 2026-04-22). **Amazon Q IDE** column values are carried over from the prior "as of 2026-04" snapshot and **have not been re-verified** against current IDE-plugin docs; re-verification requires empirical testing of the plugin, not documentation reading, and is tracked as a known follow-up in `CHANGELOG.md`. When the host agent advertises a different capability, trust the host.

---

## 2. Detection Protocol

At workflow start (before any Construction-phase rule is loaded), the model **must resolve which host agent is running** and record it in `aidlc-docs/aidlc-state.md`.

### Step 2.1 — Path-based detection

Check in order, record the first match:

| Rule-details path present | Default host agent |
|---|---|
| `.claude/` or `.aidlc-rule-details/` + Claude Code session | **claude-code** |
| `.kiro/aws-aidlc-rule-details/` | **kiro-ide** or **kiro-cli** — path alone cannot distinguish; use §2.2 self-report or ask the user |
| `.amazonq/aws-aidlc-rule-details/` | **amazon-q-ide** |
| `.cursor/rules/` | **cursor** |
| `.clinerules/` | **cline** |
| `.github/` (Copilot) | **github-copilot** |
| `.aidlc/aidlc-rules/aws-aidlc-rule-details/` (generic) | **unknown — ask the user** |

**Note on `.kiro/` ambiguity**: Kiro IDE and Kiro CLI both install rules under `.kiro/`. Path-based detection yields the product family but not the specific product. Prefer self-report (Step 2.2) — CLI system prompts identify themselves as Kiro CLI, IDE sessions as Kiro IDE. If self-report is silent, ask the user.

### Step 2.2 — Self-report override

If the model has direct knowledge of the host (e.g., the system prompt identifies itself as Claude Code / Kiro IDE / Kiro CLI), that self-report **overrides path detection**.

### Step 2.3 — Record to state

Write to `aidlc-docs/aidlc-state.md`:

```markdown
## Host Agent
- **Detected Host**: [claude-code | cursor | cline | amazon-q-ide | kiro-ide | kiro-cli | github-copilot | unknown]
- **Detection Method**: [self-report | path-based | user-confirmed]
- **Capability Profile**: [full-multi-agent | subagent-only | single-agent]
- **Decided At**: [ISO timestamp]
```

### Step 2.4 — Capability profile mapping

Collapse the matrix into three profiles for downstream rules to branch on:

| Profile | Host Agents | What it unlocks |
|---|---|---|
| `full-multi-agent` | claude-code | Generator/Evaluator via `Agent` tool, worktree parallel units, lifecycle hooks, Auto Mode |
| `subagent-only` | kiro-ide, kiro-cli, amazon-q-ide (with steering/agent files) | Specialized prompt roles via subagent/steering files; kiro-cli can launch user-initiated subagents but not agent-calls-agent. Kiro-cli edge: has native hooks + Tool Search that closer-profile hosts lack |
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

## 7. Host-Specific Next-Step Cues

The core rule set emits next-step guidance in prose form (e.g. "Proceeding to Requirements Analysis"). This is intentional: slash commands, `@mention` syntax, and host-specific CLI flags are **not** part of the host-agnostic rule surface.

Hosts that benefit from machine-actionable next-step strings (e.g. Claude Code with `/aidlc-*` slash commands) may wrap the core output with a host-specific adapter that appends the appropriate cue. Adapters live under host-specific distribution paths (e.g. `.claude/skills/aidlc-<stage>/SKILL.md`), never in `aws-aidlc-rule-details/`.

This is a structural consequence of supporting multiple hosts and should not be "fixed" by adding slash-command strings to the core rules.

---

> Author: Kwangyoung Kim (<kwangyou@amazon.com>) + Claude Code
> Source: [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips) + host-agent documentation as of 2026-04
> Last updated: April 2026
