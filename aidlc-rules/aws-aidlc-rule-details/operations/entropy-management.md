# Entropy Management

## Problem Statement

AI agents accumulate entropy (code complexity, inconsistency, dead code, documentation drift) **5-10x faster than human developers**. Without active management, the codebase degrades rapidly after AI-DLC Construction phase completes.

> "Everything looks like it's working, but technical debt accumulates like a high-interest loan."
>
> — Ref: Vercel v0

## Gardener Agent

A dedicated maintenance agent that runs periodically (not during active development) to detect and fix entropy:

### Responsibilities

| Task | Frequency | Action |
|------|-----------|--------|
| **Doc-Code Drift** | After each Construction cycle | Scan for inconsistencies between aidlc-docs/ and actual code |
| **Architecture Violations** | Weekly or per-milestone | Check dependency graph against architecture.md constraints |
| **Dead Code Detection** | Per-milestone | Identify unused exports, unreachable functions, orphaned files |
| **Style Consistency** | After multi-unit completion | Verify naming conventions, patterns, code structure consistency |
| **Test Coverage Decay** | After code changes | Ensure coverage hasn't dropped below threshold |
| **Dependency Health** | Monthly | Check for outdated, vulnerable, or unnecessary dependencies |

### Gardener Agent Output

The Gardener produces a **Health Report** in `aidlc-docs/operations/`:

```markdown
# Codebase Health Report
**Date**: [ISO timestamp]
**Scope**: [Full scan / Delta since last report]

## Summary
- **Health Score**: [0-100]
- **Critical Issues**: [N]
- **Warnings**: [N]
- **Improvements Made**: [N]

## Findings

### 🔴 Critical
- [Issue description with file path and line number]
- [Suggested fix]

### 🟡 Warning
- [Issue description]
- [Suggested fix]

### 🟢 Auto-Fixed
- [What was fixed and why]
- [Files modified]

## Entropy Metrics
- **Code Duplication**: [%]
- **Circular Dependencies**: [count]
- **Dead Code**: [lines / files]
- **Doc-Code Consistency**: [%]
- **Test Coverage**: [%]
- **Dependency Vulnerabilities**: [count]
```

## Trace-Based Detection Loop

Use execution traces to identify systematic problems and improve the harness:

```
1. Collect execution traces from Construction phase
   (errors, retries, failed tests, human overrides)
        │
        ▼
2. Error-analysis pass: categorize failures
   - Agent misunderstanding? → Improve rule files
   - Missing context? → Update Knowledge Pyramid
   - Repeated mistake? → Add to L1/L2 automated checks
   - Architecture violation? → Strengthen constraints
        │
        ▼
3. Update harness (rule files, automated checks, constraints)
        │
        ▼
4. Validate improvement in next Construction cycle
```

> This is analogous to ML boosting — each iteration of the harness targets the residual errors from the previous run.

## Feedback Encoding Ladder

When the same issue appears repeatedly, encode it at a stronger level:

```
Level 1: Review Comment (softest)
  → Agent may read it or ignore it

Level 2: Documentation
  → Add to aidlc-docs/ or README for persistence

Level 3: Tool/Rule Design
  → Build the constraint into a rule file or linter config

Level 4: Automated Test (hardest)
  → Violation causes immediate failure, deterministic enforcement
```

> "If you have to give the same feedback twice, it's a system failure."
>
> — OpenAI

## Progressive Deletability

As AI models improve, harness constraints should **decrease**, not increase:

- **Every rule should have a removal condition**: "Remove this rule when [model can reliably do X]"
- **Periodically review rules**: Are they still needed? Has the model learned this pattern?
- **Measure rule impact**: If removing a rule doesn't degrade quality, remove it
- **Version rules**: Track when rules were added and why, so they can be evaluated for removal

Example:
```markdown
## Rule: Explicit null checks in TypeScript
- **Added**: 2026-04-20
- **Reason**: Agent was generating code without null safety
- **Removal Condition**: When TypeScript strict mode is always enabled
  and agent consistently uses optional chaining without prompting
- **Last Evaluated**: [date]
```

## Integration with AI-DLC

### In aidlc-state.md

```markdown
## Entropy Management
- **Last Health Scan**: [ISO timestamp]
- **Health Score**: [0-100]
- **Open Critical Issues**: [N]
- **Harness Version**: [N] (incremented on rule file changes)
- **Rules Added Since Last Review**: [list]
- **Rules Removed Since Last Review**: [list]
```

### In operations/

Replace the placeholder operations.md with this active entropy management workflow:

```
Post-Construction Cycle:
1. Run Gardener Agent scan
2. Generate Health Report
3. Apply auto-fixes (non-breaking only)
4. Present critical findings to human for review
5. Update harness rules based on trace analysis
6. Log all changes in audit.md
```

## AutoDream — Automatic Memory Consolidation (2026 Q1)

Claude Code's **AutoDream** consolidates learning, patterns, and corrections into memory between sessions, similar to how REM sleep consolidates short-term into long-term memory:

> "Auto-memory automatically saves preferences, corrections, and patterns between sessions."
> — [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips)

**Synergy with AI-DLC Gardener Agent:**
- AutoDream automatically accumulates patterns between sessions
- Gardener Agent proposes rule file updates based on accumulated patterns
- "Add to CLAUDE.md every time the agent makes a mistake → Compounding Engineering"

**Compounding Engineering Principle:**
> "Anytime Claude does something incorrectly, add it to CLAUDE.md so it knows not to repeat the mistake. After every correction, end with: 'Update your CLAUDE.md so you don't make that mistake again.'"

Applied to AI-DLC: agent failure → log in audit.md → Gardener analyzes patterns → updates aidlc rule files → prevents same failure in next session.

## Session ≠ Context Window (Managed Agents Pattern)

Anthropic's Managed Agents architecture provides a key insight for AI-DLC state management:

> "The session provides a context object that lives outside Claude's context window. Rather than be stored within the sandbox or REPL, context is durably stored in the session log. The interface, getEvents(), allows the brain to interrogate context by selecting positional slices of the event stream."
>
> — Anthropic, [Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)

### Application to AI-DLC

AI-DLC's `aidlc-state.md` + `audit.md` already serve a similar role as the "session log":

| Managed Agents Concept | AI-DLC Equivalent |
|---|---|
| Session (append-only event log) | `audit.md` (append-only, all interactions logged) |
| Harness (agent loop + routing) | `core-workflow.md` + stage rules |
| Sandbox (isolated execution) | Project workspace (code, tests) |
| `getEvents(id)` | Read `aidlc-state.md` for current state |
| `emitEvent(id, event)` | Append to `audit.md` |

**Key principle**: Never store critical state only in the context window. Everything must be recoverable from files:
- If the session crashes → resume from `aidlc-state.md`
- If context window fills → reset and reload from artifacts
- If agent drifts → `audit.md` provides the audit trail to diagnose

## Progressive Harness Deletability

> "Harnesses encode assumptions that go stale as models improve. A context reset that was essential for Sonnet 4.5 (context anxiety) was unnecessary for Opus 4.5."
>
> — Anthropic, [Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)

### Rule Review Protocol

Every quarter (or after a major model upgrade), review AI-DLC rules:

1. **List all rules** with their original reason for existence
2. **Test without each rule** — does quality degrade?
3. **Remove rules that are no longer needed** — simpler harness = better performance
4. **Document removals** in a changelog with the model version that made them unnecessary

Example questions to ask:
- Does the model still exhibit overconfidence without `overconfidence-prevention.md`?
- Does the model still need explicit Build and Test instructions, or can it infer from context?
- Are all question-format-guide rules still needed, or does the model format questions well enough natively?

> The goal is to converge toward the simplest harness that maintains quality.
