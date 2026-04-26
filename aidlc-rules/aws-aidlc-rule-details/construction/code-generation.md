# Code Generation - Detailed Steps

## Overview
This stage generates code for each unit of work through two integrated parts:
- **Part 1 - Planning**: Create detailed code generation plan with explicit steps
- **Part 2 - Generation**: Execute approved plan to generate code, tests, and artifacts

**Note**: For brownfield projects, "generate" means modify existing files when appropriate, not create duplicates.

## Harness Engineering Enhancements

### Host Capability Required

This stage uses Generator/Evaluator multi-agent patterns. **Load `common/agent-capabilities.md` and branch behavior on the recorded `## Host Capabilities` axis values (`multi_agent` primarily; `hooks_block` and `worktree` for Pattern 3).** Also load `common/project-mode.md` and branch on the recorded `Project Mode`. See `construction/multi-agent-patterns.md` for per-axis implementation paths.

### Evaluator-Optimizer Pattern (from Anthropic)

Code Generation follows Anthropic's **Evaluator-Optimizer workflow**: the context that generates code is never the same context that evaluates it.

> "This workflow is particularly effective when we have clear evaluation criteria, and when iterative refinement provides measurable value."
> — Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

**Application**: After Part 2 (Generation) creates code, run an evaluation pass:
1. **L1–L3 deterministic checks first** (per `common/automated-feedback-loops.md`): linter, type checker, tests — zero cost, instant feedback
2. **L4 AI evaluation** in a fresh context (separate agent when `multi_agent: native`; role switch with explicit context reset when `multi_agent: user-launched`; `/clear` + role-inlined pass when `multi_agent: none`)
3. **Auto-fix loop**: iterate max 2 rounds — if L4 still fails, escalate to human (L5)
4. **L5 human gate applies per Project Mode**:
   - **Production** → per-unit human approval always required after L1–L4 pass
   - **Prototyping** → no per-unit human gate; escalate to human only on L4 failure after 2 auto-fix rounds
   - **Hybrid** → same as Prototyping in Construction (gate preserved at Build & Test)

### Tool Design Principles (from Anthropic)

When generating tools/APIs for the project, follow Anthropic's tool design principles:

> "Put yourself in the model's shoes. Is it obvious how to use this tool based on the description? A good tool definition includes example usage, edge cases, input format requirements, and clear boundaries from other tools."
> — Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

Applied to code generation:
- **Agent-Friendly Error Messages**: Generated error messages must include WHAT went wrong + HOW to fix it
- **Poka-yoke design**: Use absolute paths (not relative), required params (not optional), and strict types
- **Namespacing**: Namespace tools/functions clearly to define boundaries in functionality
- **HTTP status codes for REST/RPC endpoints**: **Load `common/http-error-conventions.md`** before generating endpoint code. Preserve the framework's default for schema-validation errors (e.g., FastAPI + Pydantic `422`) and reserve `400` for domain-level errors only. Do NOT install handlers that downgrade `422` to `400` or return `200` on validation failures or domain errors (e.g., catching an invalid-computation exception inside the route and returning a dict body instead of raising). Apply the status-code table verbatim.

### Context Reset Between Units

Between each unit of code generation, perform a **context reset** (not just compaction):
- Save current unit state to artifacts
- Clear context window
- Start fresh with: `aidlc-state.md` + next unit's design docs + architecture constraints
- This prevents context anxiety and maintains quality across many units

## Prerequisites
- Unit Design Generation must be complete for the unit
- NFR Implementation (if executed) must be complete for the unit
- All unit design artifacts must be available
- Unit is ready for code generation

---

# PART 1: PLANNING

## Step 1: Analyze Unit Context
- [ ] Read unit design artifacts from Unit Design Generation
- [ ] Read unit story map to understand assigned stories
- [ ] Identify unit dependencies and interfaces
- [ ] Validate unit is ready for code generation

## Step 2: Create Detailed Unit Code Generation Plan
- [ ] Read workspace root and project type from `aidlc-docs/aidlc-state.md`
- [ ] Determine code location (see Critical Rules for structure patterns)
- [ ] **Brownfield only**: Review reverse engineering code-structure.md for existing files to modify
- [ ] Document exact paths (never aidlc-docs/)
- [ ] Create explicit steps for unit generation:
  - Project Structure Setup (greenfield only)
  - Business Logic Generation
  - Business Logic Unit Testing
  - Business Logic Summary
  - API Layer Generation
  - API Layer Unit Testing
  - API Layer Summary
  - Repository Layer Generation
  - Repository Layer Unit Testing
  - Repository Layer Summary
  - Frontend Components Generation (if applicable)
  - Frontend Components Unit Testing (if applicable)
  - Frontend Components Summary (if applicable)
  - Database Migration Scripts (if data models exist)
  - Documentation Generation (API docs, README updates)
  - Deployment Artifacts Generation
- [ ] Number each step sequentially
- [ ] Include story mapping references
- [ ] Add checkboxes [ ] for each step

## Step 3: Include Unit Generation Context
- [ ] For this unit, include:
  - Stories implemented by this unit
  - Dependencies on other units/services
  - Expected interfaces and contracts
  - Database entities owned by this unit
  - Service boundaries and responsibilities

## Step 4: Create Unit Plan Document
- [ ] Save complete plan as `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`
- [ ] Include step numbering (Step 1, Step 2, etc.)
- [ ] Include unit context and dependencies
- [ ] Include story traceability
- [ ] Ensure plan is executable step-by-step
- [ ] Emphasize that this plan is the single source of truth for Code Generation

## Step 5: Summarize Unit Plan
- [ ] Provide summary of the unit code generation plan to the user
- [ ] Highlight unit generation approach
- [ ] Explain step sequence and story coverage
- [ ] Note total number of steps and estimated scope

## Step 6: Log Approval Prompt
- [ ] Before asking for approval, log the prompt with timestamp in `aidlc-docs/audit.md`
- [ ] Include reference to the complete unit code generation plan
- [ ] Use ISO 8601 timestamp format

## Step 7: Wait for Explicit Approval
- [ ] Do not proceed until the user explicitly approves the unit code generation plan
- [ ] Approval must cover the entire plan and generation sequence
- [ ] If user requests changes, update the plan and repeat approval process

## Step 8: Record Approval Response
- [ ] Log the user's approval response with timestamp in `aidlc-docs/audit.md`
- [ ] Include the exact user response text
- [ ] Mark the approval status clearly

## Step 9: Update Progress
- [ ] Mark Code Generation Part 1 (Planning) complete in `aidlc-state.md`
- [ ] Update the "Current Status" section
- [ ] Prepare for transition to Code Generation

---

# PART 2: GENERATION

## Step 10: Load Unit Code Generation Plan
- [ ] Read the complete plan from `aidlc-docs/construction/plans/{unit-name}-code-generation-plan.md`
- [ ] Identify the next uncompleted step (first [ ] checkbox)
- [ ] Load the context for that step (unit, dependencies, stories)

## Step 11: Execute Current Step
- [ ] Verify target directory from plan (never aidlc-docs/)
- [ ] **Brownfield only**: Check if target file exists
- [ ] Generate exactly what the current step describes:
  - **If file exists**: Modify it in-place (never create `ClassName_modified.java`, `ClassName_new.java`, etc.)
  - **If file doesn't exist**: Create new file
- [ ] Write to correct locations:
  - **Application Code**: Workspace root per project structure
  - **Documentation**: `aidlc-docs/construction/{unit-name}/code/` (markdown only)
  - **Build/Config Files**: Workspace root
- [ ] Follow unit story requirements
- [ ] Respect dependencies and interfaces

## Step 12: Update Progress
- [ ] Mark the completed step as [x] in the unit code generation plan
- [ ] Mark associated unit stories as [x] when their generation is finished
- [ ] Update `aidlc-docs/aidlc-state.md` current status
- [ ] **Brownfield only**: Verify no duplicate files created (e.g., no `ClassName_modified.java` alongside `ClassName.java`)
- [ ] Save all generated artifacts

## Step 13: Continue or Complete Generation
- [ ] If more steps remain, return to Step 10
- [ ] If all steps complete, proceed to run L1–L4 feedback loop (Step 13.5)

## Step 13.5: Run L1–L4 Feedback Loop (Evaluator Pass)
- [ ] Run L1 per-file checks (syntax, forbidden patterns) — see `common/automated-feedback-loops.md`
- [ ] Run L2 turn-end checks (lint, type-check on changed files)
- [ ] Run L3 tests (unit tests for this unit)
- [ ] Run L4 AI review in a **fresh context** per `construction/multi-agent-patterns.md` §1.A / §1.B / §1.C (selected by host profile)
- [ ] If any of L1–L4 fails → auto-fix and re-run (max 2 rounds)
- [ ] If still failing after 2 rounds → write `aidlc-docs/construction/{unit-name}/escalation.md` and proceed to Step 14 (present escalation instead of approval)
- [ ] If all pass → proceed to Step 14 (present completion)

## Step 14: Present Completion Message

**Mode-dependent behavior**: this step's output depends on the Project Mode recorded in `aidlc-state.md`:
- **Production** → show the standard "WHAT'S NEXT?" 2-option block below (L5 human gate).
- **Prototyping / Hybrid** → skip the 2-option block; show a **short auto-proceed notice** and advance to the next unit (or Build & Test if last unit). The user only sees a gate if L4 escalation occurred.
- Present completion message in this structure:
     1. **Completion Announcement** (mandatory): Always start with this:

```markdown
# 💻 Code Generation Complete - [unit-name]
```

     2. **AI Summary** (optional): Provide structured bullet-point summary
        - **Brownfield**: Distinguish modified vs created files (e.g., "• Modified: `src/services/user-service.ts`", "• Created: `src/services/auth-service.ts`")
        - **Greenfield**: List created files with paths (e.g., "• Created: `src/services/user-service.ts`")
        - List tests, documentation, deployment artifacts with paths
        - Keep factual, no workflow instructions
     3. **Formatted Workflow Message** (mandatory): Always end with this exact format:

```markdown
> **📋 <u>**REVIEW REQUIRED:**</u>**  
> Please examine the generated code at:
> - **Application Code**: `[actual-workspace-path]`
> - **Documentation**: `aidlc-docs/construction/[unit-name]/code/`



> **🚀 <u>**WHAT'S NEXT?**</u>**
>
> **You may:**
>
> 🔧 **Request Changes** - Ask for modifications to the generated code based on your review  
> ✅ **Continue to Next Stage** - Approve code generation and proceed to **[next-unit/Build & Test]**

---
```

## Step 15: Wait for Explicit Approval (Production only)
- **Production mode**: Do not proceed until the user explicitly approves the generated code. If user requests changes, update the code and repeat the approval process.
- **Prototyping / Hybrid mode**: Skip this gate — the unit is considered complete if L1–L4 passed in Step 13.5. Log the auto-proceed decision in audit.md.
- **Escalation (any mode)**: If Step 13.5 escalated (L4 failed after 2 rounds), present the escalation to the user and wait for guidance — the workflow halts here until the user responds.

## Step 16: Record Approval/Auto-Proceed and Update Progress
- Log the user approval response (Production) OR the auto-proceed decision (Prototyping / Hybrid) in audit.md with timestamp
- Record the exact outcome
- Mark Code Generation stage as complete for this unit in aidlc-state.md

---

## Critical Rules

### Code Location Rules
- **Application code**: Workspace root only (NEVER aidlc-docs/)
- **Documentation**: aidlc-docs/ only (markdown summaries)
- **Read workspace root** from aidlc-state.md before generating code

**Structure patterns by project type**:
- **Brownfield**: Use existing structure (e.g., `src/main/java/`, `lib/`, `pkg/`)
- **Greenfield single unit**: `src/`, `tests/`, `config/` in workspace root
- **Greenfield multi-unit (microservices)**: `{unit-name}/src/`, `{unit-name}/tests/`
- **Greenfield multi-unit (monolith)**: `src/{unit-name}/`, `tests/{unit-name}/`

### Brownfield File Modification Rules
- Check if file exists before generating
- If exists: Modify in-place (never create copies like `ClassName_modified.java`)
- If doesn't exist: Create new file
- Verify no duplicate files after generation (Step 12)

### Planning Phase Rules
- Create explicit, numbered steps for all generation activities
- Include story traceability in the plan
- Document unit context and dependencies
- Get explicit user approval before generation

### Generation Phase Rules
- **NO HARDCODED LOGIC**: Only execute what's written in the unit plan
- **FOLLOW PLAN EXACTLY**: Do not deviate from the step sequence
- **UPDATE CHECKBOXES**: Mark [x] immediately after completing each step
- **STORY TRACEABILITY**: Mark unit stories [x] when functionality is implemented
- **RESPECT DEPENDENCIES**: Only implement when unit dependencies are satisfied

### Automation Friendly Code Rules
When generating UI code (web, mobile, desktop), ensure elements are automation-friendly:
- Add `data-testid` attributes to interactive elements (buttons, inputs, links, forms)
- Use consistent naming: `{component}-{element-role}` (e.g., `login-form-submit-button`, `user-list-search-input`)
- Avoid dynamic or auto-generated IDs that change between renders
- Keep `data-testid` values stable across code changes (only change when element purpose changes)

## Completion Criteria
- Complete unit code generation plan created and approved
- All steps in unit code generation plan marked [x]
- All unit stories implemented according to plan
- All code and tests generated (tests will be executed in Build & Test phase)
- Deployment artifacts generated
- Complete unit ready for build and verification
