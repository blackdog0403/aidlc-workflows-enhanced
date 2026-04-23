# Question Format Guide

## MANDATORY Rules

- **NEVER ask questions directly in chat**. All questions go in dedicated `aidlc-docs/{phase}-questions.md` files.
- **Every question** uses multiple choice with **"Other" as the MANDATORY last option**.
- **Options must be meaningful** — don't pad to fill A/B/C/D slots.
- **Minimum 2 meaningful options + Other** per question. Typical 3–4.
- **Options must be mutually exclusive** and specific.
- **Always wait** for user completion before reading / analyzing.

## Question File Structure

File name: `aidlc-docs/{phase-name}-questions.md`. Examples: `classification-questions.md`, `requirements-questions.md`, `story-planning-questions.md`.

```markdown
# [Phase Name] Questions

Please answer each question by filling in the letter after [Answer]:.
If none of the options match, choose the last option (Other) and describe.

## Question 1
[Clear, specific question text]

A) [Meaningful option]
B) [Meaningful option]
...
X) Other (please describe after [Answer]: tag below)

[Answer]:
```

## User Response Format

```markdown
## Question 1
What is the primary user authentication method?

A) Username and password
B) Social media login (Google, Facebook)
C) Single Sign-On (SSO)
D) Multi-factor authentication
E) Other (please describe after [Answer]: tag below)

[Answer]: C
```

## Workflow Integration

1. **Create** `aidlc-docs/{phase}-questions.md` with all questions.
2. **Inform the user**: "I've created `{phase}-questions.md` with N questions. Please answer each by filling the letter after `[Answer]:`. If none match, pick Other and describe. Let me know when you're done."
3. **Wait** for "done" / "completed" / "finished".
4. **Read and validate** — all `[Answer]:` tags filled, letters valid.
5. **Detect contradictions/ambiguities** (see below) → if any, create a clarification file and loop.
6. **Proceed** with the phase work only when responses are complete and consistent.

## Answer Validation

| Issue | Response |
|---|---|
| Missing answer | "Question [X] is not answered. Please provide a letter choice for all questions before proceeding." |
| Invalid letter | "Question [X] has invalid answer '[x]'. Use only the letter choices provided." |
| Free-text instead of letter | "For Question [X], please provide the letter that best matches. If none match, choose Other and describe." |

## Contradiction & Ambiguity Detection (MANDATORY)

After reading responses, scan for:
- **Scope mismatch** (e.g., "bug fix" + "entire codebase affected")
- **Risk mismatch** ("low risk" + "breaking changes")
- **Timeline mismatch** ("quick fix" + "multiple subsystems")
- **Impact mismatch** ("single component" + "major architecture change")
- **Ambiguity** — answers that could fit multiple classifications, lack specificity, or conflict across questions.

If any detected:
1. Create `aidlc-docs/{phase}-clarification-questions.md`.
2. State each contradiction/ambiguity explicitly, reference original question numbers.
3. Provide targeted multiple-choice questions (with Other) to resolve each.
4. Wait for answers. Re-validate.
5. Do **not** proceed until all contradictions are resolved.

### Clarification File Template

```markdown
# [Phase] Clarification Questions

I detected contradictions/ambiguities that need clarification:

## Contradiction 1: [Brief description]
You indicated "[Answer]" (Q[X]:[Letter]) but also "[Answer]" (Q[Y]:[Letter]).
These are contradictory because [reason].

### Clarification Question 1
[Targeted question]

A) [Resolves toward first]
B) [Resolves toward second]
C) [Middle ground]
D) [Reframe]
E) Other (please describe after [Answer]: tag below)

[Answer]:
```

## Question Quality Bar

Every question must satisfy all five:

- **Specific** — one topic per question; no compound questions.
- **Comprehensive** — the set of questions covers every decision the phase needs.
- **Concise** — no nested conditionals or multi-part prompts inside one question.
- **Practical** — options are realistic choices the user can actually pick (not abstractions).
- **Mutually exclusive** — options don't overlap; any two answers imply different downstream actions.

## Anti-Pattern — MUST avoid

Option padding is the #1 failure mode. Never add filler options just to reach A/B/C/D.

```markdown
# BAD — filler options, non-specific, not mutually exclusive
## Question
What database will you use?

A) Yes
B) No
C) Maybe
```

```markdown
# GOOD — specific, mutually exclusive, practical
## Question
What database technology will be used?

A) Relational (PostgreSQL, MySQL)
B) NoSQL Document (MongoDB, DynamoDB)
C) NoSQL Key-Value (Redis, Memcached)
D) Graph Database (Neo4j, Neptune)
E) Other (please describe after [Answer]: tag below)

[Answer]:
```

If you cannot produce at least two *meaningful* options, the topic is not ready to be a question — refine the topic or ask a different one.

## Quick Reference

- ✅ Create question files; never chat questions
- ✅ Multiple choice, Other is MANDATORY last option
- ✅ Only meaningful options — no filler (see Anti-Pattern above)
- ✅ `[Answer]:` tags; wait for completion
- ✅ Validate for contradictions; resolve before proceeding
- ❌ Never assume on ambiguous answers
- ❌ Never proceed without completed answers
