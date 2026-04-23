# Mid-Workflow Changes

Users may request changes to the plan mid-flight. Handle every request with the same protocol, then apply the change-specific guidance below.

## Universal Protocol

1. **Confirm request**: restate what the user wants to change and why.
2. **Assess impact**: which stages, artifacts, dependencies are affected.
3. **Explain consequences**: what will be redone, timeline impact, alternatives.
4. **Get explicit confirmation** before any destructive action.
5. **Archive before destroying**: `{artifact}.backup.{timestamp}`.
6. **Keep tracking in sync**: `aidlc-state.md`, plan-file checkboxes, and `audit.md`.
7. **Log the change** using the format at the bottom of this file.
8. **Validate and resume** normal execution.

## Change Patterns

Change | Core Action | Key Warning
---|---|---
**Add a skipped stage** | Check prereqs complete, add to plan, execute | Later stages may need revision to incorporate new artifacts.
**Skip a planned stage** | Mark `SKIPPED` with reason; user accepts risk | Later stages may fail or need manual setup.
**Restart current stage** | Modify OR restart (with archive) | Restart loses work; modification is often enough.
**Restart earlier stage** | Archive + reset all dependent stages | Significant rework; all dependents must be redone.
**Change depth level** | Update plan, adjust approach, update estimate | Only before/during stage, not after completion.
**Pause & resume** | Finish current step, update checkboxes, log pause | On resume, validate state vs artifacts.
**Change architectural decision** | If early: update decision. If late: restart from Application Design. | Cascading effects; earlier = cheaper.
**Add/remove/split unit** | Update unit-of-work.md, dependency map, story map; reset affected units | Downstream stages for affected units must redo.

## Decision Tree

```
User requests change
  ├─ Is it adding a skipped stage? → Check prereqs → Add → Execute
  ├─ Is it skipping a planned stage? → Warn impact → Confirm → Skip
  ├─ Is it restarting current stage? → Modify vs Restart → Execute
  ├─ Is it restarting earlier stage? → Assess cascade → Confirm → Restart chain
  ├─ Is it changing depth? → Update plan → Adjust approach
  └─ Other → Clarify with user before acting
```

## Resume from Pause

1. Detect existing project via `aidlc-state.md`.
2. Load all artifacts from completed stages.
3. Display current stage and next step.
4. Offer continue-here vs review-previous-work.
5. Log the resume in `audit.md`.

## Change Log Format

```markdown
## Change Request - [Stage Name]
**Timestamp**: [ISO timestamp]
**Request**: [What user wants changed]
**Current State**: [Where we are in workflow]
**Impact Assessment**: [What will be affected]
**User Confirmation**: [Explicit user confirmation — quoted]
**Action Taken**: [What was done]
**Artifacts Affected**: [Files changed/reset]

---
```

## Best Practices

- **Never** make destructive changes without explicit confirmation.
- **Always** archive before destroy.
- **Prefer** modification over restart when feasible.
- **Keep** `aidlc-state.md`, plan files, and `audit.md` in lockstep.
