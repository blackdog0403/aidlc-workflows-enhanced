# Context Optimization Guide

## Problem Statement

AI-DLC rule files total ~234KB across 30 files. Loading all files at once causes **Context Rot** — as context grows, agent performance degrades as a gradient (not a cliff). Attention becomes "stretched thin," rules get ignored, and the agent starts re-reading the same files repeatedly.

> "The smallest possible set of high-signal tokens" — the goal is minimal, high-signal context.
>
> — Ref: Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

## Knowledge Pyramid (L0-L3)

Structure rule files in layers. Load only what's needed at each stage.

```
L0: core-workflow.md (~24KB, always loaded — index/roadmap)
    │
    ├── L1: common/ rules (load at workflow start)
    │   ├── process-overview.md
    │   ├── session-continuity.md
    │   ├── content-validation.md
    │   └── question-format-guide.md
    │
    ├── L2: Phase-specific rules (load when entering phase)
    │   ├── inception/*.md → load when entering Inception
    │   └── construction/*.md → load when entering Construction
    │
    └── L3: Extensions + reference (load on-demand only)
        ├── extensions/**/*.md → load only when opted-in
        └── common/error-handling.md → load only on error
```

### Loading Strategy

| Strategy | When | What to Load |
|----------|------|--------------|
| **Upfront** | Session start | core-workflow.md + L1 common rules (4 files) |
| **JIT (Phase Entry)** | Entering Inception/Construction | Phase-specific rule files only |
| **On-Demand** | Error or opt-in | error-handling.md, extensions |
| **Never Pre-load** | — | ASCII diagram standards, workflow-changes.md, terminology.md (reference only) |

## Context Budget

Target: **80%+ of context window for actual work** (code, tests, error logs, user artifacts)

| Source | Budget | Guideline |
|--------|--------|-----------|
| core-workflow.md | ~15% | Always present — serves as index |
| Active stage rules | ~10% | Only the current stage's detail file |
| Common rules | ~5% | Only session-continuity + content-validation |
| Extensions | ~5% | Only opted-in extensions |
| **Actual work context** | **≥65%** | Code, tests, designs, user artifacts, error logs |

### Context Obesity Symptoms

If you observe these, context is too bloated:
- Agent ignores rules it was given
- Agent re-reads the same files repeatedly
- Auto-compaction triggers frequently
- Quality degrades mid-session
- Agent "forgets" earlier decisions

### Remediation

1. **Unload completed stage rules** — After leaving a stage, its detail file can be dropped from context
2. **Summarize don't repeat** — Reference artifacts by path, don't paste their full content
3. **Pointer, not payload** — In CLAUDE.md/AGENTS.md, include pointers to docs, not the docs themselves
4. **Progressive Disclosure** — Give the agent a map, not a 1,000-page manual

## Prompt Caching Optimization

When constructing prompts for the AI model, order content for cache efficiency:

```
[STATIC — cacheable, load first]
├── System prompt / role definition
├── core-workflow.md (stable across sessions)
├── Common rules (rarely change)
└── Active stage rules (stable within stage)

[VARIABLE — append after static]
├── Current artifacts (requirements.md, stories.md, etc.)
├── Code context
├── User's latest input
└── Error logs
```

> Static content first, variable content last (Append-Only pattern).
> This maximizes cache hit rates and reduces token costs.
>
> — Ref: Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

## Context Anxiety & Context Resets

Models can exhibit **"context anxiety"** — prematurely wrapping up work as they sense the context limit approaching. Two remediation strategies:

### Compaction (Summary-in-place)
- Summarize earlier conversation content and continue with shortened history
- **Pro**: Preserves continuity
- **Con**: Context anxiety can still persist because the agent doesn't get a clean slate
- Best for: Mid-session context management

### Context Reset (Clean Slate)
- Clear the context window entirely and start a fresh agent session
- Hand off state via structured artifacts (not in-context memory)
- **Pro**: Eliminates context anxiety completely
- **Con**: Costs continuity — agent loses conversational nuance
- Best for: Between major stages (e.g., between AI-DLC Inception and Construction)

> "Context resets—clearing the context window entirely and starting a fresh agent, combined with a structured handoff—addresses context anxiety. This differs from compaction, which doesn't give the agent a clean slate."
>
> — Anthropic, [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)

### AI-DLC Application

Apply **context resets between AI-DLC phases**:
1. After **Inception** completes → reset context, hand off via `aidlc-state.md` + `aidlc-docs/inception/` artifacts
2. After each **Construction unit** completes → reset context, hand off via unit artifacts
3. After **Build and Test** → reset context for Operations phase

State handoff artifacts (what persists across resets):
- `aidlc-state.md` — workflow state, current phase/stage
- `audit.md` — decision history
- Phase-specific artifacts in `aidlc-docs/`

## Tool Search — Dynamic Tool Loading (2025-11)

When using large tool sets, pre-loading all definitions consumes 50K-134K tokens. **Tool Search** loads on-demand:

| Approach | Token Usage | Accuracy |
|------|----------|--------|
| Full pre-load (50+ tools) | ~77K tokens | Opus 4.5: 79.5% |
| **Tool Search (on-demand)** | **~8.7K tokens (85% reduction)** | Opus 4.5: **88.1%** |

> "Tool Search Tool discovers tools on-demand. Claude only sees the tools it actually needs for the current task."
> — Anthropic, [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) (2025-11-24)

**AI-DLC Application:**
- Don't load Construction tool definitions during Inception phase
- Unload Inception rule files during Construction
- Load only opted-in extensions (matches existing mechanism)
- Apply `defer_loading: true` principle to rule files as well

## Don't Over-Stuff Edge Cases

> "Teams will often stuff a laundry list of edge cases into a prompt in an attempt to articulate every possible rule. We do not recommend this. Instead, work to curate the most important examples and let the model generalize."
>
> — Anthropic, [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

Applied to AI-DLC:
- **Don't** load all 37 rule files at once
- **Do** load the minimum set for the current stage
- **Don't** enumerate every possible error in error-handling.md
- **Do** provide representative examples and let the model generalize
- **Don't** repeat rules across multiple files
- **Do** use pointers: "See `common/error-handling.md` for details"
