# Cost Optimization Extension

## Opt-In Prompt

Ask the user during Requirements Analysis:

```markdown
### Cost Optimization Extension

Would you like to enable **AI cost optimization** strategies?

This includes:
- **Model routing** — use cheaper models for simple tasks, powerful models for complex ones
- **Token optimization** — minimize context window usage without losing quality
- **Response format control** — DETAILED vs CONCISE output modes

This is recommended for projects with **10+ units** or expected **high token consumption**.

A) **Yes** — Enable cost optimization
B) **No** — Use default settings (single model, standard verbosity)
C) **Custom** — I'll configure specific optimizations

[Answer]:
```
