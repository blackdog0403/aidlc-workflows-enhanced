# Agent Capability Detection & Adaptation

**Purpose**: AI-DLC rules must adapt to the capabilities of the **host agent** (the IDE or CLI running this workflow). A rule that assumes Claude Code's worktree isolation will silently fail on Kiro, which does not yet support multi-agent orchestration. A rule written for a single agent leaves Claude Code's Generator/Evaluator power unused.

This file defines:
1. A **capability matrix** listing the features each host agent supports.
2. A **detection protocol** — how the agent identifies itself at workflow start.
3. **Fallback rules** — how higher-order patterns (multi-agent, worktree, hooks) degrade when a capability is missing.

All other rule files that depend on multi-agent, worktree isolation, sandboxing, or hook execution **MUST reference this file** and branch their behavior accordingly.

---

## 1. Capability Matrix

Each cell carries both a short axis-value label (used by downstream rules — see §2.5) and a note describing the host's specific implementation. Axis values are the *interface* downstream files branch on; notes are human context.

| Capability | Axis | Claude Code | Cursor | Cline | Amazon Q IDE | Kiro IDE | Kiro CLI | GitHub Copilot |
|---|---|---|---|---|---|---|---|---|
| **Subagent definition files** | `subagents` | ✅ `native` — `.claude/agents/` | ⚠️ `rules-only` | ⚠️ `rules-only` — skills + read-only subagents | ⚠️ `rules-only` | ⚠️ `rules-only` — steering only | ✅ `native` — `.kiro/agents/*.json` | ✅ `native` — `.github/agents/*.agent.md` |
| **Multi-agent orchestration** | `multi_agent` | ✅ `native` — `Agent` tool | ⚠️ `user-launched` — `/multitask` (auto-decomposed) | ⚠️ `user-launched` — `use_subagents` (read-only, no nesting) | ❌ `none` | ❌ `none` | ⚠️ `user-launched` — subagents (CLI 2.0/2.1) | ✅ `native` — `agents` frontmatter + `agent` tool |
| **Parallel worktree execution** | `worktree` | ✅ `native` — `--worktree`, `isolation: worktree` | ✅ `native` — Agents Window worktrees | ✅ `native` — New Worktree Window | ❌ `none` | ❌ `none` | ❌ `none` | ⚠️ `per-task-vm` — coding-agent per-task VM only |
| **OS-level sandbox** | `sandbox` | ✅ `os-level` — `bubblewrap`/`seatbelt` | ⚠️ `approval-prompt` — sandboxed terminals | ⚠️ `approval-prompt` — manual | ❌ `none` — approval-prompt only | ⚠️ `approval-prompt` — manual | ❌ `none` — tool-trust only | ⚠️ `approval-prompt` — preview (macOS/Linux) |
| **Boundary / Auto mode** | `boundary` | ✅ `classifier` — Auto Mode | ⚠️ `allow-list` — allow-lists + sandbox fallback | ⚠️ `allow-list` — model `requires_approval` flag | ⚠️ `allow-list` — basic | ⚠️ `allow-list` — basic | ⚠️ `allow-list` — pre-approved tool lists (per agent) | ⚠️ `allow-list` — Autopilot (auto-approve all, experimental) |
| **Lifecycle hooks — observe/feedback** | `hooks_observe` | ✅ `native` | ✅ `native` | ✅ `native` | ❌ `none` | ✅ `native` | ✅ `native` — `AgentSpawn`, `UserPromptSubmit` | ✅ `native` |
| **Lifecycle hooks — block triggering action** | `hooks_block` | ✅ `native` — exit 2 on PreToolUse + others | ✅ `native` — exit 2 | ✅ `native` — `cancel: true` | ❌ `none` | ✅ `native` — Pre Tool Use, Prompt Submit | ✅ `native` — `PreToolUse` exit 2 | ✅ `native` — exit 2 / `permissionDecision: deny` |
| **Auto-memory / cross-session consolidation** | `auto_memory` | ✅ `autonomous` — auto memory (`MEMORY.md`) | ✅ `autonomous` — Memories | ⚠️ `semi` — Memory Bank (manual trigger) | ⚠️ `semi` — Memory Bank (manual gen, auto reload) | ⚠️ `semi` — user-edited steering | ❌ `none` — manual session resume only | ⚠️ `semi` — Copilot Memory (preview) |
| **Tool Search / defer_loading** | `tool_search` | ✅ `native` | ❌ `none` | ❌ `none` | ❌ `none` | ❌ `none` | ✅ `native` — MCP on-demand (CLI 2.1) | ❌ `none` |
| **File-based rule loading** | `rule_files` | ✅ `native` — `.claude/` | ✅ `native` — `.cursor/rules/` | ✅ `native` — `.clinerules/` | ✅ `native` — `.amazonq/rules/` | ✅ `native` — `.kiro/steering/` | ✅ `native` — `.kiro/steering/` | ✅ `native` — `.github/` |
| **Structured question files** | `qfiles` | ✅ `native` | ✅ `native` | ✅ `native` | ✅ `native` | ✅ `native` | ✅ `native` | ✅ `native` |

Legend for symbols: ✅ native support · ⚠️ partial / workaround · ❌ not supported at the date this rule file was last verified.

**Axis value vocabulary** (the string after ✅/⚠️/❌ is what downstream rules match on — see §2.5):

| Axis | Possible values |
|---|---|
| `subagents` | `native` · `rules-only` · `none` |
| `multi_agent` | `native` · `user-launched` · `none` |
| `worktree` | `native` · `per-task-vm` · `none` |
| `sandbox` | `os-level` · `approval-prompt` · `none` |
| `boundary` | `classifier` · `allow-list` · `none` |
| `hooks_observe` | `native` · `none` |
| `hooks_block` | `native` · `none` |
| `auto_memory` | `autonomous` · `semi` · `none` |
| `tool_search` | `native` · `none` |
| `rule_files` | `native` · `none` |
| `qfiles` | `native` · `none` |

> **Caveat**: Capability support evolves fast. Most entries were re-verified 2026-04-25 against host documentation; cells carrying version pins (e.g. "CLI 2.1", "preview") reflect the state of the referenced release. Amazon Q IDE column was specifically re-verified on 2026-04-25 against VS Code + JetBrains changelogs (versions 1.52–1.110) — no hooks, no agents directory, Memory Bank is manual-generate / auto-reload. Sources consulted: [code.claude.com/docs](https://code.claude.com/docs/) (Claude Code), [cursor.com/changelog](https://cursor.com/changelog) (Cursor 1.0 / 1.7 / 3.2), [docs.cline.bot](https://docs.cline.bot/) (Cline v3.56–v3.81), [kiro.dev/docs/hooks/](https://kiro.dev/docs/hooks/) (Kiro IDE hooks), [kiro.dev/docs/cli/](https://kiro.dev/docs/cli/) (Kiro CLI 2.0/2.1), [docs.aws.amazon.com/amazonq/](https://docs.aws.amazon.com/amazonq/) (Amazon Q IDE Plugin), [code.visualstudio.com/docs/copilot](https://code.visualstudio.com/docs/copilot/) (Copilot, docs updated 2026-04-22). When the host agent advertises a different capability, trust the host.

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
- **Decided At**: [ISO timestamp]

## Host Capabilities
<!-- Axis values copied from §1 matrix for the Detected Host column. Downstream rules branch on these values, not on the host name. See §2.5 for the lookup procedure. -->
- subagents: [native | rules-only | none]
- multi_agent: [native | user-launched | none]
- worktree: [native | per-task-vm | none]
- sandbox: [os-level | approval-prompt | none]
- boundary: [classifier | allow-list | none]
- hooks_observe: [native | none]
- hooks_block: [native | none]
- auto_memory: [autonomous | semi | none]
- tool_search: [native | none]
- rule_files: [native | none]
- qfiles: [native | none]
```

### Step 2.4 — Capability profile mapping (legacy, retained for compatibility)

> **Status**: Deprecated. Kept so downstream files that still branch on `full-multi-agent` / `subagent-only` / `single-agent` continue to work while they migrate to §2.3 Host Capabilities. New downstream branches MUST use axis values, not this profile. This section will be removed once every downstream file has migrated.

Collapse the matrix into three profiles:

| Profile | Host Agents | What it unlocks (legacy summary) |
|---|---|---|
| `full-multi-agent` | claude-code | Generator/Evaluator via `Agent` tool, worktree parallel units, lifecycle hooks, Auto Mode |
| `subagent-only` | kiro-ide, kiro-cli, amazon-q-ide | Subagent/steering files; kiro-cli adds hooks + Tool Search |
| `single-agent` | cursor, cline, github-copilot | Emulated via context resets; but note cursor/cline now have native worktrees + hooks |

The "one profile per host" framing no longer matches reality (e.g., GitHub Copilot shipped agent-calls-agent in VS Code 1.105 yet is listed as `single-agent`; Cursor 3.2 shipped worktrees yet sits in the same profile as `single-agent`). This is why §3 branches on axis values instead of profile.

If the host is **unknown**, leave axis values as `none` and ask the user.

### Step 2.5 — How to fill Host Capabilities from the matrix

For each row in §1 that carries an **Axis** column, read the cell at the Detected Host's column and copy the axis value (the token immediately after ✅/⚠️/❌) into the corresponding Host Capabilities line in `aidlc-state.md`.

Example — Detected Host is `claude-code`:

- §1 "Multi-agent orchestration" row, Claude Code column: `✅ \`native\` — \`Agent\` tool` → `multi_agent: native`.
- §1 "Auto-memory" row, Claude Code column: `✅ \`autonomous\` — auto memory` → `auto_memory: autonomous`.
- §1 "Tool Search" row, Claude Code column: `✅ \`native\`` → `tool_search: native`.

If a cell shows only a symbol (✅/⚠️/❌) with no axis token, use the default fallback: ✅ → `native`, ❌ → `none`. ⚠️ without a token is ambiguous — ask the user rather than guess.


---

## 3. Fallback Rules (Axis-Value Based)

Each subsection below is a pattern. For each pattern, look up the relevant axis value from `aidlc-state.md` under `## Host Capabilities` (populated from §1 matrix per §2.5) and execute the matching strategy.

**Universal principle**: **Never refuse to proceed.** Every pattern has a path that works even when the relevant axis is `none` — it just costs more model turns or runs sequentially instead of in parallel.

### 3.1 Generator/Evaluator Separation

**Invariant**: Generator and Evaluator must run in different contexts. This is non-negotiable regardless of axis value; what varies is *how* the separation is achieved.

Reads axis: **`multi_agent`**.

| `multi_agent` | Strategy |
|---|---|
| `native` | Two distinct agents in separate contexts. Invoke Evaluator via the host's agent-calls-agent mechanism (Claude Code Agent tool, Copilot `agent` tool). |
| `user-launched` | One session, two sequential passes with explicit context reset between them. Use a subagent / steering / custom-agent file per role (Generator role, Evaluator role). Switch the active role between passes. |
| `none` | One agent, two sequential passes. Between passes, perform an explicit context reset (`/clear` or equivalent). Evaluator prompt is inlined from `construction/multi-agent-patterns.md`. |

### 3.2 Three-Agent Planner / Generator / Evaluator

Reads axis: **`multi_agent`**.

| `multi_agent` | Strategy |
|---|---|
| `native` | Three agents chained via agent-calls-agent. Each agent has its own context. |
| `user-launched` | Three sequential passes, each with its own subagent/steering/custom-agent file and explicit context reset. |
| `none` | Three sequential passes in one agent; explicit `/clear` (or equivalent) between passes. Role prompts inlined. |

### 3.3 Parallel Unit Execution (Worktree)

Reads axis: **`worktree`**.

| `worktree` | Strategy |
|---|---|
| `native` | Use the host's worktree mechanism (Claude Code `--worktree` or `isolation: worktree`; Cursor Agents Window worktrees; Cline New Worktree Window). N units run in parallel; merge via git after all units pass L3. |
| `per-task-vm` | Host spins per-task ephemeral VMs (Copilot coding-agent). Use this when the task can be described as a self-contained PR brief. N tasks can be dispatched in parallel but each lives in its own remote VM, not a local worktree. |
| `none` | Emulate isolation via **feature branches**: `git checkout -b aidlc/<unit-name>` before each unit, commit at unit completion, merge after Build and Test. **Sequential only — no parallelism.** Log the serialization as a known limitation. |

### 3.4 Sandboxing & Boundary-Based Security

See `common/boundary-based-security.md` for the full security discussion. Branching summary here reads two axes: **`sandbox`** for process isolation, **`boundary`** for the approval classifier.

`sandbox` decides how process-level isolation is enforced:

| `sandbox` | Strategy |
|---|---|
| `os-level` | Host provides OS sandbox (bubblewrap on Linux, seatbelt on macOS). Trust the sandbox for file-system scoping; focus approval logic on net-new external calls. |
| `approval-prompt` | No sandbox. Every non-whitelisted Tier 3 action raises an approval prompt. Publish a **Pre-Approved Commands** list at Construction start and ask the user to whitelist once; everything else prompts. |
| `none` | Same as `approval-prompt` for practical purposes — treat the absence of a sandbox as a hard constraint. Never assume isolation. |

`boundary` decides how approvals are classified:

| `boundary` | Strategy |
|---|---|
| `classifier` | Use the host's classifier (Claude Code Auto Mode) to auto-approve Tier 1+2 and prompt only on Tier 3. Log the classifier's false-positive/false-negative rates if the host publishes them. |
| `allow-list` | Pre-declare pre-approved commands in `aidlc-state.md` under `## Pre-Approved Commands`. Host confirms Tier 3 via its built-in permission prompts. |
| `none` | Every action prompts. This is the safe default; no auto-approval. |

### 3.5 Lifecycle Hooks

Reads two axes: **`hooks_block`** for enforcement, **`hooks_observe`** for feedback/logging. They can be both `native`, one `native` and one `none`, or both `none`.

L1 (per-file) checks:

| `hooks_observe` | `hooks_block` | Strategy |
|---|---|---|
| `native` | `native` | Wire L1 checks to a `PostToolUse`-equivalent hook so every file write triggers syntax + forbidden-pattern scans without a model turn. Configure the hook to **block** on critical violations (non-zero exit). This is the lowest-cost, highest-enforcement path. |
| `native` | `none` | Wire L1 checks to the observe-only hook. Violations surface in the agent's context but cannot cancel the triggering action — the agent must recognize and self-correct. |
| `none` | `none` | No hooks available. Run L1 checks as an **in-prompt post-step** after each file write (one extra model turn per write). Log the turn cost — this is the price of not having hooks. |

### 3.6 Auto-Memory / Cross-Session Consolidation

Reads axis: **`auto_memory`**.

| `auto_memory` | Strategy |
|---|---|
| `autonomous` | Host writes cross-session memory automatically (Claude Code `MEMORY.md`, Cursor Memories). Let the host's native system carry learned patterns across sessions; the Gardener Agent proposes rule-file updates based on recent memory entries. |
| `semi` | Host loads a memory file automatically but only writes it when the user triggers it (Amazon Q Memory Bank generate button, Kiro steering refine, Cline Memory Bank initialize). At Construction end, **prompt the user** to trigger the host's memory-update action; document what they did in `aidlc-docs/operations/harness-learnings.md`. |
| `none` | Persist cross-session learning to `aidlc-docs/operations/harness-learnings.md` manually. Reload at workflow start as context. |

### 3.7 Tool Search / Deferred Loading

Reads axis: **`tool_search`**.

| `tool_search` | Strategy |
|---|---|
| `native` | Use the host's Tool Search. Rules are loaded on-demand per stage. The host handles schema lazy-loading for MCP tools (Kiro CLI 2.1) or extension tools (Claude Code). |
| `none` | Use AI-DLC's existing `*.opt-in.md` convention and staged loading from `common/context-optimization.md`. The agent loads only the opt-in stubs at workflow start and pulls full rule files when the relevant stage opts in. |

---

## 4. How Downstream Rules Must Reference This File

Any rule file describing a multi-agent / parallel / hooked / memory / tool-search pattern **must**:

1. Open with a "Reads axis" note that names the one or two axes whose value it branches on (e.g. `Reads axis: multi_agent`).
2. Reference this file: `See common/agent-capabilities.md §3.N for the full strategy table.`
3. Provide a strategy for **every** axis value in the vocabulary (`native`, `user-launched`, `none`, etc.) — not just the best-case one. Use the tables in §3 as the authoritative mapping.
4. **Never** hardcode `claude --worktree` or Agent-tool calls without checking the relevant axis first.
5. Look up axis values from `aidlc-state.md` under `## Host Capabilities`. Do not branch on `Detected Host` name or the legacy `Capability Profile` field — the former couples the rule to a specific product and the latter is deprecated.

### Template

```markdown
## Host Capability Required
- **Reads axis**: `[axis-name]` (from `aidlc-state.md` → `## Host Capabilities`)
- **When `[axis-name]` is `native`**: [primary recipe]
- **When `[axis-name]` is `[intermediate-value]`**: [partial recipe, if the axis has an intermediate value]
- **When `[axis-name]` is `none`**: [fallback recipe, must still work]
- See `common/agent-capabilities.md` §3.[subsection] for the full strategy table.
```

---

## 5. When the User Can Override

At Workflow Planning, the user may override any axis value to a *lower* value than detected (e.g., disable `multi_agent` on a hook-capable host to save cost, or downgrade `sandbox: os-level` to `approval-prompt` for visibility). Record the override:

```markdown
## Host Capabilities — User Override
- **Axis**: [multi_agent | worktree | hooks_block | ...]
- **Detected Value**: [value from §1 matrix]
- **Active Value**: [user-chosen lower value]
- **Reason**: [user-provided]
- **Decided At**: [ISO timestamp]
```

**User cannot force an axis HIGHER than detected** — the capability simply does not exist. If the user asks for `multi_agent: native` on a host whose detected value is `none`, reply with the matrix row in §1 and propose the detected value as the maximum.

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
