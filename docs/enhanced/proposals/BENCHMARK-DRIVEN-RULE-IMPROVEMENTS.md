# Benchmark-Driven Rule Improvements

> Three rule-level improvements surfaced by the Enhanced vs Upstream
> benchmark run (see `docs/benchmark/AIDLC-Rules-Comparison.md`).
> Enhanced currently scores 69/71 (97.2%) on the shared 71-assertion
> rubric, two points behind the Claude Code skill-native variant
> (71/71). Both gaps live in the `detect` skill; a third observation
> concerns the `gate` skill, which passes today but through synthesis
> rather than explicit guidance.

**Author:** Kwangyoung Kim (<kwangyou@amazon.com>)
**Status:** Draft — not yet implemented
**Last updated:** 2026-04-23

---

## 1. Context

The Enhanced rule set and the Claude Code skill-native variant differ
by two assertions on `detect` and nominally by zero on `gate` in the
measured run. Static prediction (Phase A) expected a four-point gap;
the actual measured gap was two points because the agent composed a
2-phase `GO/NO-GO` + `PASS/FAIL` pipeline for `gate` from adjacent
rules without any single Enhanced file prescribing it. That synthesis
is good news for Enhanced's score but bad news for reproducibility:
the same run under a weaker model or different context budget may not
repeat it.

The three proposals below address the three observations, ordered by
cost-to-ship and expected benefit.

| # | Proposal | Cost | Benefit | Risk |
| --- | --- | --- | --- | --- |
| A | Swap `workspace-detection.md` completion header to setext `===` | 2 lines | +1 assertion (69 → 70/71, 98.6%) | None |
| B | Make `build-and-test.md` 2-phase gate explicit | ~25 lines | Locks in the `gate` 5/5 result across agents/models | +25 lines of context |
| C | Document slash-command next-step as a host-adapter concern | ~10 lines | Defensive — prevents future contributors from "fixing" it by adding Claude Code-specific phrasing to the host-agnostic core | None |

Proposal A is a no-brainer. B is a hardening change that should land
once we have two or three independent measured runs confirming the
synthesis is model-fragile. C is documentation.

---

## 2. Proposal A — Setext completion header in `workspace-detection.md`

### 2.1 The failing assertion

`grade.py` (line 34) asserts for the `detect` skill:

```python
results.append({"text": "Contains completion summary",
                "passed": check(text, r'===.*Complete|===.*Detection'),
                "evidence": ""})
```

The regex accepts any line containing `===` *and then* either
`Complete` or `Detection`. The Claude Code skill template satisfies
this with a setext-style heading banner in `result.md`:

```markdown
=== Workspace Detection Complete ===
```

Enhanced's current template in
`aidlc-rules/aws-aidlc-rule-details/inception/workspace-detection.md`
uses an ATX heading:

```markdown
# 🔍 Workspace Detection Complete
```

No `===`, so the regex misses. This is the sole reason Enhanced
scores 3/5 on `detect` instead of 4/5.

### 2.2 Proposed change

Lines 99 and 109 of `workspace-detection.md` currently read:

```markdown
# 🔍 Workspace Detection Complete
```

Replace with one of:

**Option 1 — pure setext (recommended):**

```markdown
=== Workspace Detection Complete ===
```

**Option 2 — keep ATX heading, add setext rule underneath:**

```markdown
# 🔍 Workspace Detection Complete
===================================
```

Option 1 is cleaner and more portable — `===` banner headers render
identically across every markdown renderer and do not depend on emoji
support. Option 2 preserves the existing visual style at the cost of
one extra line.

### 2.3 Why this is host-agnostic-safe

`===` is plain ASCII markdown convention, not a Claude Code primitive
or a slash command. Every supported host (Cursor, Cline, Amazon Q,
Kiro, GitHub Copilot, Claude Code) renders it the same way. Nothing
in the change binds the rule to any specific agent.

### 2.4 Expected impact

- `detect` goes 3/5 → 4/5
- Total Enhanced score goes **69/71 (97.2%) → 70/71 (98.6%)**
- The gap to Native narrows from 2 points to 1 point

### 2.5 Verification

After the edit:

1. Re-run the `detect` stage against `scenario.md` in Claude Code
   (or any supported host) using the Enhanced rule set.
2. Confirm the produced `result.md` contains a line matching
   `/=== .*(Complete|Detection)/`.
3. Run `python3 docs/benchmark/grade.py .` — `detect` should report
   4/5 with only `Recommends next step` still failing.

---

## 3. Proposal B — Make `build-and-test.md` 2-phase gate explicit

### 3.1 Current fragile behavior

Enhanced's `gate` skill currently scores 5/5 in the measured run,
matching Native. That happens because the agent composes the
following structure by itself:

- `## Phase 1: Code Review` with `**Verdict: GO**` / `**Verdict: NO-GO**`
- `## Phase 2: Build & Test` with `**Verdict: PASS**` / `**Verdict: FAIL**`

Neither `build-and-test.md` nor `automated-feedback-loops.md`
prescribes this shape verbatim. The agent synthesizes it from:

- The L1–L5 verification ladder in `automated-feedback-loops.md`
  (L1-L4 as deterministic checks, L5 as the human gate)
- The build/test discussion in `build-and-test.md`
- Whatever implicit "gate" framing the underlying LLM associates with
  the word "gate"

This means the 5/5 could collapse under:

- A weaker model that doesn't invent the 2-phase framing
- A smaller context budget that drops `automated-feedback-loops.md`
  before `build-and-test.md` is read
- A different agent host that reads the rules in a different order

In other words, we are currently scoring 5/5 on luck plus a capable
model. The benchmark would report this as a regression as soon as
that condition changes.

### 3.2 Proposed change

Add a "Gate output contract" section to
`aidlc-rules/aws-aidlc-rule-details/construction/build-and-test.md`
that explicitly mandates the 2-phase structure. Suggested text:

```markdown
## Gate Output Contract

When the Build & Test stage runs as a gate (i.e. when a unit is being
promoted out of Construction), the stage output MUST be structured as
two explicit phases:

### Phase 1 — Code Review

- Section heading exactly: `## Phase 1: Code Review` (or
  `## Phase 1 — Code Review`, with the word "Phase 1" at the start).
- Content: architecture review, code-quality review, security checks
  (OWASP Top 10, secrets, injection vectors, authentication).
- Verdict line at the end: `**Verdict: GO**` or `**Verdict: NO-GO**`.
  The words `GO` and `NO-GO` must both appear in the section even if
  only one is the chosen verdict (e.g. in a decision rationale).

### Phase 2 — Build & Test

- Section heading exactly: `## Phase 2: Build & Test`.
- Content: build execution, automated test execution, coverage
  metrics, integration/contract test results.
- Verdict line at the end: `**Verdict: PASS**` or `**Verdict: FAIL**`.
  The words `PASS` and `FAIL` must both appear even if only one is
  the chosen verdict.

The two-phase structure separates readiness assessment (Phase 1, a
subjective decision) from quality validation (Phase 2, an
objective measurement). Collapsing them into a single pass hides the
subjective/objective boundary and was observed to cost ~2 rubric
points against upstream variants that did so.
```

### 3.3 Why not just let the synthesis happen

Because implicit contracts are not reproducible contracts. The
rule-file surface should be legible enough that a junior model or a
new agent can produce the same output the senior model produces.
This is the same principle Lopopolo calls out in the OpenAI harness
engineering writeup:

> "Anything not in the repository effectively does not exist to Codex."
>
> — Ryan Lopopolo, OpenAI, *Harness engineering: leveraging Codex
> in an agent-first world* (2026-02-11)

The 2-phase contract currently exists only in the more capable LLM's
training distribution. Moving it into the repository is the harness
engineering discipline.

### 3.4 Cost

~25 lines added to `build-and-test.md`. Context impact negligible
(the file is already 365 lines and loaded at Construction only).

### 3.5 Verification

1. Re-run the `gate` stage with a weaker model (e.g. Sonnet 4.5 or
   Haiku 4.5) against `scenario.md`.
2. Expected result: without this change, weaker models score less
   than 5/5 on `gate` — specifically, `Two-phase pipeline`,
   `GO/NO-GO verdict`, `PASS/FAIL verdict` become fragile.
3. With this change, weaker models should reach the same 5/5 as
   capable models.

This should ideally be validated against two models before merging.

---

## 4. Proposal C — Document the slash-command next-step escape hatch

### 4.1 The assertion Enhanced cannot pass

`grade.py` line 32:

```python
results.append({"text": "Recommends next step",
                "passed": check(text, r'/aidlc-(reverse|requirements)'),
                "evidence": ""})
```

This requires the literal string `/aidlc-reverse` or
`/aidlc-requirements` somewhere in the `detect` output. Those are
Claude Code slash commands and do not exist on other hosts.

Emitting them from Enhanced's host-agnostic core would cause Cursor
or Cline or Amazon Q to print meaningless strings. The gap is the
*correct* behavior given the design goal — not a bug.

### 4.2 Why this still needs a documentation change

Because a future contributor reading the benchmark results might see
"Enhanced is 1 point from Native, let me fix that" and add
slash-command phrasing to `workspace-detection.md`, which would
silently degrade UX on every non-Claude-Code host.

### 4.3 Proposed change

Add a short "Host adapter escape hatch" note to
`aidlc-rules/aws-aidlc-rule-details/common/agent-capabilities.md`
(existing file, capability-matrix authority). Suggested text:

```markdown
## Host-Specific Next-Step Cues

The core rule set emits next-step guidance in prose form (e.g.
"Proceeding to Requirements Analysis"). This is intentional: slash
commands, `@mention` syntax, and host-specific CLI flags are
**not** part of the host-agnostic rule surface.

Hosts that benefit from machine-actionable next-step strings (e.g.
Claude Code with `/aidlc-*` slash commands) may wrap the core
output with a host-specific adapter that appends the appropriate
cue. Adapters live under host-specific distribution paths (e.g.
`.claude/skills/aidlc-<stage>/SKILL.md`), never in
`aws-aidlc-rule-details/`.

This is a structural consequence of supporting multiple hosts and
should not be "fixed" by adding slash-command strings to the core
rules.
```

### 4.4 Cost

~10 lines added to an existing file. No behavior change.

### 4.5 Verification

None required — this is pure documentation. Read-through review is
sufficient.

---

## 5. Bundling strategy

- **Proposal A alone** → a single-commit change, mechanical, safe
  to merge on observation. Publish as a point release.
- **Proposal A + B** → land together if the harness team agrees that
  a weaker-model run showed the synthesis is fragile. Requires the
  two-model validation described in §3.5.
- **Proposal C** → land whenever §A lands, as the two pair naturally:
  A closes the closable gap, C explains why the remaining gap is
  intentional.

Recommendation: land A + C together in a small PR. Defer B until a
second measured run (ideally on a different model tier) is available
to quantify the fragility risk.

---

## 6. Out of scope

- Re-running the full 14-stage benchmark on a weaker model is the
  right follow-up work but is not part of these proposals. It is the
  gating data for Proposal B.
- Extending the rubric itself (beyond what `anhyobin/aidlc-workflows`
  publishes) would change the comparison contract with upstream and
  should be a separate discussion.

---

## 7. References

- Benchmark harness and full comparison: `docs/benchmark/README.md`
- Full rule comparison: `docs/benchmark/AIDLC-Rules-Comparison.md`
  (Phase B §5.8 for measured numbers; §6.5 for the one-line fix
  recommendation)
- Upstream baseline: [`anhyobin/aidlc-workflows` — `platforms/claude-code/benchmarks`](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code/benchmarks)
- Harness Engineering pattern — "Anything not in the repository
  effectively does not exist to Codex":
  [Ryan Lopopolo, OpenAI, *Harness engineering: leveraging Codex in
  an agent-first world*](https://openai.com/index/harness-engineering/) (2026-02-11)
