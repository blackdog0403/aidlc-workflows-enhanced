# Automated Feedback Loops (L1-L5)

## Problem Statement

AI-DLC currently relies on **human approval at every stage** ("Wait for Explicit Approval — DO NOT PROCEED until user confirms"). This is the Harness Engineering equivalent of **L0 maturity (Ad-hoc, Step-by-step approval)**.

Issues with step-by-step approval:
- **Approval Fatigue** — users start approving without reading
- **Slow feedback** — problems caught late are expensive to fix
- **No automated quality gates** — code quality depends entirely on human review

> "Don't send problems to L5 that L1 could catch."
>
> — Ref: Anthropic, [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)

## Verification = #1 Tip

> "The single most impactful tip is **verification** — giving Claude a way to check its own output. If Claude can close the feedback loop on its own, it will iterate until the output is right."
> — Anthropic, [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips)

Verification applies differently per domain:
- **Code**: test suites, linters, type checkers
- **UI**: browser screenshots + visual verification (Chrome extension, Desktop app)
- **Docs**: structural validation (Mermaid parsing, ASCII art rendering)

## Layered Verification Model

### L1: Per-File Checks (0-3 seconds, $0)

**Trigger**: Every file creation or modification  
**Automated checks**:
- [ ] File size within limits (warn if >500 lines for a single file)
- [ ] No forbidden patterns (hardcoded credentials, API keys, secrets)
- [ ] Syntax validation (JSON, YAML, Mermaid, Markdown)
- [ ] Import/dependency structure matches architectural constraints

**Implementation**: Add to Code Generation Part 2 — after each file write, run validation before proceeding.

### L2: Turn-End Checks (5-30 seconds, $0)

**Trigger**: After completing a unit of code generation  
**Automated checks**:
- [ ] Linter passes (language-specific: ESLint, Pylint, Clippy, etc.)
- [ ] Type checker passes (TypeScript, MyPy, etc.)
- [ ] File structure matches architecture document
- [ ] No circular dependencies introduced
- [ ] Code follows patterns established in prior units

**Implementation**: Add as mandatory step between Code Generation Part 2 and next unit.

### L3: Test Verification (30s-5 minutes, $0)

**Trigger**: After L2 passes for a unit  
**Automated checks**:
- [ ] Unit tests pass for the current unit
- [ ] Integration tests pass with previously completed units
- [ ] Test coverage meets minimum threshold (configurable, default 80%)
- [ ] No regression in previously passing tests

**Implementation**: Run before marking unit as complete. If tests fail, auto-retry fix (max 2 attempts) before escalating to human.

### L4: AI Review (1-5 minutes, $token)

**Trigger**: After L3 passes  
**AI-powered checks** (use a separate review context, NOT the coding context):
- [ ] Code review: logic correctness, edge cases, error handling
- [ ] Security review: OWASP Top 10 patterns, input validation
- [ ] Architecture compliance: does implementation match design docs?
- [ ] Consistency: naming conventions, patterns, style across units

**Implementation**: If using multi-agent setup, delegate to a dedicated reviewer agent. If single-agent, create a separate review pass with fresh context.

> "Tuning an independent evaluator to be skeptical is far more tractable than making a generator self-critical."
> (Tuning an independent evaluator to be skeptical is far easier than making a generator self-critical.)
>
> — Anthropic

### L5: Human Review (10+ minutes, $labor)

**Trigger**: After all units complete L1-L4 (i.e., at Build and Test stage)  
**Human reviews**:
- [ ] Architecture decisions and trade-offs
- [ ] Business logic correctness
- [ ] Domain-specific requirements satisfaction
- [ ] Release readiness decision

**This is the ONLY level that requires "Wait for Explicit Approval".**

## Auto-Fix Loop (Ralph Wiggum Pattern)

When L1-L3 checks fail, attempt automated fix before escalating:

```
Agent generates code
    → L1/L2/L3 check fails
        → Agent reads error message
            → Agent attempts fix (max 2-3 retries)
                → If fixed: continue
                → If not fixed after retries: escalate to human
```

### Agent-Friendly Error Messages

Error messages MUST include **what went wrong + how to fix it**:

| ❌ BAD | ✅ GOOD |
|--------|---------|
| `Error: dependency violation` | `ERROR: service/auth.ts → ui/LoginPage.tsx dependency violation. Service layer cannot import UI. Keep auth logic in service, call from UI.` |
| `TypeError: undefined` | `TypeError: user.email is undefined at line 42. Likely cause: missing null check. Add optional chaining: user?.email` |
| `Build failed` | `Build failed: missing dependency @types/node. Run: npm install --save-dev @types/node` |

## Integration with AI-DLC Stages

| AI-DLC Stage | Feedback Level | What Changes |
|---|---|---|
| Requirements Analysis | L5 only | Keep human approval (high-stakes decisions) |
| User Stories | L5 only | Keep human approval |
| Workflow Planning | L5 only | Keep human approval |
| Application Design | L5 only | Keep human approval |
| **Code Generation** | **L1-L4 automated, L5 at PR** | Add automated checks per-file and per-unit |
| **Build and Test** | **L1-L5 full stack** | Automated test execution with human final review |

## Monitoring Metrics

Track these to measure feedback loop effectiveness:
- **L1-L3 catch rate**: % of issues caught before human review
- **Auto-fix success rate**: % of L1-L3 failures fixed without human intervention
- **Mean time to detection**: How quickly are issues found?
- **Escalation rate**: % of issues that reach L5 human review
