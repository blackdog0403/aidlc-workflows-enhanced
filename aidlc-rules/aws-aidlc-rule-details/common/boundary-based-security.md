# Boundary-Based Security

## Problem Statement

Per-action approval ("Allow this? y/n") causes **Approval Fatigue** — users start mindlessly approving without reading, which **makes the security mechanism weaken security**.

> Anthropic's internal data: sandboxing safely reduces permission prompts by **84%**.
>
> — Ref: [Making Claude Code more secure and autonomous with sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)

### Key Insight from Anthropic

> "Effective sandboxing requires both filesystem AND network isolation. Without network isolation, a compromised agent could exfiltrate sensitive files like SSH keys; without filesystem isolation, a compromised agent could easily escape the sandbox and gain network access. It's by using both techniques that we can provide a safer and faster agentic experience."

The most frequent security risk is NOT malicious scheming — it's **over-eager helpfulness**:
> "The most common safety issue is not adversarial behavior but 'an overly enthusiastic AI' that exceeds the scope of what was asked."
> — Anthropic, [Trustworthy agents in practice](https://www.anthropic.com/research/trustworthy-agents)

## Principle: Define Boundaries, Not Per-Action Gates

| Per-Action Approval | Boundary-Based |
|---------------------|---------------|
| Every action asks permission | Pre-define safe zones, alert on boundary crossing only |
| Approval Fatigue → rubber-stamping | Human attention focused where it matters |
| Security mechanism weakens security | Security maintained through structural constraints |

## Plan Mode (Strategy-Level Oversight)

Anthropic's research on trustworthy agents introduces **Plan Mode** as a middle ground:

> "Rather than asking for approval for each action one-by-one, Claude shows the user its intended plan of action up-front. The user can review, edit, and approve the whole thing before anything happens—and can still intervene at any point during execution."
> — Anthropic, [Trustworthy agents in practice](https://www.anthropic.com/research/trustworthy-agents)

**Application to AI-DLC:**
- During **Inception**: Present full Workflow Planning for approval (already exists)
- During **Construction**: Present Code Generation Part 1 (Planning) for approval, then Part 2 (Generation) runs with boundary-based security — no per-file approval needed
- **Escalation only** on boundary crossing or evaluator rejection

This shifts oversight from individual actions to **overall strategy**.

## Auto Mode — Production Implementation of Boundary-Based Security (2026-03)

Anthropic shipped **Auto Mode** in March 2026, implementing Boundary-Based Security in production:

> "Auto mode is a new mode for Claude Code that delegates approvals to model-based classifiers — a middle ground between manual review and no guardrails."
> — Anthropic, [Auto mode for Claude Code](https://www.anthropic.com/engineering/claude-code-auto-mode) (2026-03-25)

**How it works:**
- **Sonnet 4.6 Safety Classifier** evaluates each tool call in real-time
- Low-risk (file reads, in-project edits, test runs) → **auto-approved**
- High-risk (force push, production deploy, external network) → **blocked or user confirmation**
- False Positive Rate: **0.4%** (after Stage 2 CoT reasoning)

**AI-DLC Application:**
- **Inception phase**: Auto Mode NOT applied — high-stakes decisions require human approval
- **Construction - Code Generation**: ✅ Auto Mode candidate
  - L1-L3 automated feedback + Auto Mode = code generation/test/fix loop without human intervention
  - Human intervention only at L4-L5
- **Build and Test**: ✅ Auto Mode candidate
  - Build/test commands auto-execute as Pre-Approved

> ⚠️ **AGENTS.md Security Vulnerability (2026-04-20)**: NVIDIA Red Team discovered attack vector where build dependencies modify AGENTS.md to alter agent behavior.
> AI-DLC rule files are exposed to the same risk — recommend integrity checks (hash verification, git diff review) for rule files.

## Dual Isolation (Apply Both Simultaneously)

### 1. Filesystem Isolation

**Allowed zones** (agent can read/write freely):
```
✅ ALLOWED:
├── <project-root>/src/          # Application code
├── <project-root>/tests/        # Test code
├── <project-root>/aidlc-docs/   # AI-DLC documentation
├── <project-root>/package.json  # Dependencies
├── <project-root>/tsconfig.json # Config
└── <project-root>/.aidlc/       # AI-DLC rules (read-only)

❌ BLOCKED (require explicit approval):
├── ../ (parent directories)
├── ~/.ssh/
├── ~/.aws/
├── /etc/
├── .env, .env.local            # Secrets
└── Any path outside project root
```

### 2. Network Isolation

**Allowed** (no approval needed):
- `npm install`, `pip install`, `maven dependency:resolve` — package managers
- `localhost` / `127.0.0.1` — local services for testing

**Blocked** (require approval):
- Any external API calls not in allowlist
- `curl`, `wget` to external URLs
- SSH connections
- Database connections to non-local hosts

## 3-Tier Permission Model

| Tier | Actions | Approval Required? |
|------|---------|-------------------|
| **Tier 1: Safe** | Read files, search code, list directories, view git log | ❌ Never |
| **Tier 2: Project-Scoped** | Write/edit files in project, run tests, build project | ❌ No (within boundaries) |
| **Tier 3: Elevated** | Shell commands, external network, git push, file deletion, dependency install | ✅ Yes |

## Integration with AI-DLC Stages

### Inception Phase
- **Tier 1 only** — reading, analyzing, documenting
- No human approval needed for file reads and document generation within `aidlc-docs/`

### Construction Phase — Code Generation
- **Tier 1 + Tier 2** — reading and writing code within project
- Human approval only for Tier 3 (shell commands, dependency installs)

### Construction Phase — Build and Test
- **Tier 1 + Tier 2 + Tier 3 (with approval)** — needs shell access for builds/tests
- Pre-approve specific build/test commands at stage start:

```markdown
## Pre-Approved Commands for Build and Test
The following commands are pre-approved and do not require per-execution approval:
- `npm install` / `pip install -r requirements.txt` / `mvn dependency:resolve`
- `npm test` / `pytest` / `mvn test`
- `npm run build` / `mvn clean package`
- `docker-compose up -d` (for integration test environment)
- `docker-compose down`
```

## Escalation Protocol

When an action crosses a boundary:

```
Agent encounters boundary-crossing action
    → Log the action and reason in audit.md
    → Present to user with context:
        "I need to [ACTION] because [REASON].
         This is outside the pre-approved boundaries.
         Approve? [y/n]"
    → If approved, log approval in audit.md
    → If denied, find alternative approach within boundaries
```
