# Cost Optimization Rules

## Model Routing

Use different model tiers for different tasks to optimize cost-performance ratio:

| Agent Role | Recommended Tier | Relative Cost | When to Use |
|-----------|-----------------|--------------|-------------|
| **Reviewer** | Light (Haiku 4.5) | 1x ($0.25/$1.25 per 1M) | Code style review, simple checks |
| **Coder** | Standard (Sonnet 4.6) | 12x ($3/$15 per 1M) | Code generation, standard tasks |
| **Architect/Supervisor** | Premium (Opus 4.7) | 60x ($5/$25 per 1M) | Architecture decisions, complex reasoning |
| **Safety Classifier** | Standard (Sonnet 4.6) | — | Auto Mode real-time tool call evaluation (automatic) |

### Routing Rules

```
IF task = "code review" OR "lint check" OR "style review":
    → Use Light model
ELIF task = "code generation" OR "test generation" OR "documentation":
    → Use Standard model
ELIF task = "architecture design" OR "complex algorithm" OR "security review":
    → Use Premium model
```

### Effort Level Usage (Claude Code)

> "The Claude Code team uses high for everything; switch to /effort max for hard debugging or architecture decisions."
> — [Claude Code power user tips](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips)

- **Inception (planning)**: `/effort max` — maximum reasoning for architecture decisions
- **Construction (implementation)**: `/effort high` — default
- **Build and Test (verification)**: `/effort max` — maximum reasoning for bug detection → Reasoning Sandwich (max-high-max)

### Escalation

If a Light or Standard model encounters a task it cannot handle well (hallucinations, repeated failures):
1. Log the escalation reason
2. Retry with next tier up
3. Track escalation frequency to improve routing rules

## Token Optimization

### Programmatic Tool Calling (2025-11)

> "Claude writes code that calls multiple tools, processes their outputs, and controls what information actually enters its context window."
> — Anthropic, [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)

Calling tools via code prevents intermediate results from polluting context. Example: aggregating 10 unit test results with 1 code execution instead of 10 inference passes.

### Tool Definition Minimization

- Load only tool definitions relevant to the current stage
- Don't load build tools during Inception; don't load design tools during Build and Test
- Target: **85% reduction** in tool definition tokens when using selective loading

> Vercel v0 reduced from 15 tools to 2 → accuracy improved from 80% to 100%, tokens reduced by 37%.

### Response Format Control

| Mode | Avg Tokens | When to Use |
|------|-----------|-------------|
| **DETAILED** | ~200 tokens | Architecture decisions, complex explanations, user-facing docs |
| **CONCISE** | ~70 tokens | Status updates, simple confirmations, intermediate steps |

### Rules

1. **CONCISE mode for intermediate steps**: When processing units sequentially, use concise responses between units
2. **DETAILED mode for user-facing artifacts**: Requirements, designs, and summaries use detailed mode
3. **CONCISE mode for automated feedback loops**: L1-L3 check results use minimal formatting
4. **DETAILED mode for escalations**: When escalating to human review, provide full context

## Context Window Management

### Sliding Window Strategy

For projects with many units:
1. **Keep in context**: Current unit's design + code + tests
2. **Summarize in context**: Previously completed units (1-2 line summary each)
3. **Available via tool**: Full details of prior units (read file when needed)
4. **Drop from context**: Completed stage rules (e.g., requirements-analysis.md after Inception)

### Cost Tracking

Track and report token consumption per stage:

```markdown
## Token Usage Summary
| Stage | Input Tokens | Output Tokens | Estimated Cost |
|-------|-------------|---------------|---------------|
| Inception | [N] | [N] | $[N] |
| Construction - Unit 1 | [N] | [N] | $[N] |
| Construction - Unit 2 | [N] | [N] | $[N] |
| Build and Test | [N] | [N] | $[N] |
| **Total** | **[N]** | **[N]** | **$[N]** |
```

## Integration with aidlc-state.md

```markdown
## Cost Optimization
- **Enabled**: Yes/No
- **Model Routing**: [Light/Standard/Premium model names]
- **Response Mode**: [DETAILED/CONCISE/AUTO]
- **Token Budget**: [Total budget if set]
- **Tokens Used**: [Running total]
- **Escalation Count**: [N]
```
