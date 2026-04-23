# Error Handling and Recovery

## Principles

When an error occurs: **identify → assess impact → communicate → offer solutions → log in `audit.md`**.

Severity | Description
---|---
**Critical** | Workflow cannot continue (missing required files, broken inputs, FS errors)
**High** | Stage cannot complete (incomplete answers, contradictions, missing prior-stage deps)
**Medium** | Stage continues with workarounds (optional artifact missing, partial progress)
**Low** | Non-blocking (formatting, missing optional info)

## Stage-Specific Patterns

Use these responses for the most common stage-specific errors. All follow the same shape: **Cause → Solution → Do-Not-Proceed / Workaround**.

### Workspace Detection
- **Cannot read workspace** → verify permissions; proceed with user-provided info only.
- **Corrupted `aidlc-state.md`** → back up as `.backup`, ask fresh-start vs recovery.
- **Cannot determine stages** → ask clarifying questions; default to comprehensive plan.

### Requirements Analysis
- **Contradictory requirements** → follow-up questions. **Do not proceed** until resolved.
- **Unsupported format** → ask user for a supported format; fallback to verbal description.
- **Incomplete answers** → highlight unanswered questions with examples. **Do not proceed**.

### User Stories
- **Cannot map requirements to stories** → return to Requirements; or create partial stories marked incomplete.
- **Ambiguous story-planning answers** → follow-up questions with examples. **Do not proceed**.
- **Plan has uncompleted steps** → resume from first uncompleted `[ ]`.

### Application / Unit Design
- **Unclear architectural decision** → follow-up questions. **Do not proceed** until documented.
- **Circular unit dependencies** → identify cycles, propose boundary refactor.
- **Cannot determine number of services/units** → ask about deployment / team / scaling; default to monolith.

### NFR
- **Incompatible tech choices** → highlight incompatibilities, user chooses.
- **Org constraints not met** → document, escalate for human intervention.
- **Step requires human action** → mark as **HUMAN TASK** with clear instructions; wait.

### Code Generation
- **Plan incomplete** → return to Design; or generate with gaps marked.
- **Dependencies not satisfied** → reorder, or stub and integrate later.
- **Generated code has syntax errors** → fix and regenerate; verify before proceeding.
- **Test generation fails** → generate basic scaffolding, mark for manual completion.

### Build / Deployment
- **Cannot determine build tool** → ask user; fall back to generic instructions.
- **Deployment target unclear** → ask user; fall back to common-platform instructions.

## Session Resumption Errors

**Rule**: on resume, always validate `aidlc-state.md` matches the on-disk artifacts.

Pattern | Symptom | Action
---|---|---
State-says-complete / artifact-missing | Stage marked complete but files absent | Mark incomplete, re-execute, verify after.
Artifact-exists / state-says-incomplete | Files present but stage flag not set | Verify artifacts valid, update state.
Multiple "current" stages | State file corrupted | Inspect artifacts, ask user, rebuild state.
Corrupted artifact | Empty or malformed file | Back up as `.backup`, regenerate or ask user.
Contradictory artifacts | Manual edits diverged | Present contradictions to user, reconcile before proceeding.

## Generic Recovery Procedures

1. **Partial stage completion** → load plan, identify last `[x]`, resume from next `[ ]`.
2. **Corrupted state file** → back up, ask user which stage, regenerate from artifacts.
3. **Missing artifacts** → identify, regenerate if possible, else ask user; document the gap.
4. **Restart stage** → archive existing `{artifact}.backup`, reset checkboxes + state, re-execute.
5. **Skip stage** → confirm implications, mark `SKIPPED` in state, note downstream risk.

## Escalation

**Ask the user immediately when** input is contradictory / ambiguous, required information is missing, a technical constraint is outside AI scope, or a business-judgment decision is required.

**Suggest starting over when** multiple stages have errors, the state file is severely corrupted, requirements have changed significantly, or artifacts are inconsistent across phases. Before starting over: archive, capture lessons, confirm with user.

## Logging

```markdown
## Error - [Stage Name]
**Timestamp**: [ISO timestamp]
**Severity**: [Critical/High/Medium/Low]
**Description**: [What went wrong]
**Cause**: [Why]
**Resolution**: [How resolved]
**Impact**: [Effect on workflow]

---
```

Use an analogous `## Recovery - [Stage Name]` block after recovery actions.

## Prevention

- Validate inputs and dependencies before starting.
- Update checkboxes `[x]` immediately after each step.
- Ask instead of assuming; clarify ambiguities early.
- Log all decisions and changes in `audit.md`.
