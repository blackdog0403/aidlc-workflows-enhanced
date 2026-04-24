# Harness Engineering Benchmark Axis — Proposal

> Design note for a second benchmark axis that measures the Harness
> Engineering patterns Enhanced adds on top of upstream AI-DLC.
> The existing regex rubric (reused from `anhyobin/aidlc-workflows` for
> cross-variant comparison) measures output-format compliance only and
> cannot probe runtime properties like verification-ladder catch rate,
> token efficiency, or cross-host portability.

**Author:** Kwangyoung Kim (<kwangyou@amazon.com>)
**Status:** Draft — roadmap, no measurements run yet
**Last updated:** 2026-04-24

---

## 1. Motivation

The current benchmark at [`docs/benchmark/`](../../benchmark/) is a regex rubric over final stage outputs. It was useful for confirming that Enhanced's design intent lands on the assertions we expected, and that [Proposals A / B / C](../landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md) improved the metrics they targeted. But the rubric has a hard ceiling: it rewards whether a string pattern shows up in `result.md`, not whether the rule set actually provides the Harness Engineering benefit it claims.

Enhanced adds eight Harness Engineering patterns on top of upstream AI-DLC (see [`AIDLC-Rules-Comparison.md` §3](../../benchmark/AIDLC-Rules-Comparison.md)). One of them — Lopopolo's "anything not in the repository effectively does not exist" — was validated inside this repo via the Proposal B fragility runner ([`docs/benchmark/runners/run_gate_benchmark.py`](../../benchmark/runners/run_gate_benchmark.py)). Haiku 4.5 / Sonnet 4.6 / Opus 4.7 each moved from 2.0 / 5 → 5.0 / 5 on the `gate` stage after the 2-phase Gate Output Contract was encoded in the rule file.

That single measurement is the proof-of-concept for how the remaining seven patterns should be validated.

---

## 2. Proposed benchmark axis

One mini-experiment per Harness Engineering pattern. Each experiment isolates **one** HE claim and measures a **delta**, not an absolute pattern.

| HE pattern | Enhanced rule file | Mini-experiment shape | Cost to run |
|---|---|---|---|
| **Feedback Encoding Ladder (L1–L5)** | `common/automated-feedback-loops.md` | Inject N known bugs across severity tiers; measure catch rate at each L1–L5 layer in isolation | ~$5–10 per scenario |
| **Generator/Evaluator separation** | `construction/multi-agent-patterns.md` | Same code review task, 1-agent (self-review) vs 2-agent (independent evaluator); measure bug-catch delta | ~$10 per scenario |
| **Host Portability** | `common/agent-capabilities.md` | Run the 14-stage pipeline against 3 hosts (Claude Code, Cursor, Bedrock raw API); measure output-diff on methodology-relevant fields | ~$30 × host count |
| **Context Budget / Knowledge Pyramid** | `common/context-optimization.md` | Token consumption × final rubric score curve across 3 loading strategies (upfront / JIT / full monolithic) | ~$15 per strategy |
| **Boundary-Based Security** | `common/boundary-based-security.md` | Count tool-call approval prompts with / without boundary tiers over a fixed scenario | ~$5 |
| **Entropy Management** | `operations/entropy-management.md` | Multi-session simulation; measure duplication / dead-code / doc-drift metrics after N sprints | 1 sprint ≈ $20 |
| **Cost Optimization (Model Routing)** | `extensions/cost-optimization/` | Haiku / Sonnet / Opus routing vs single-tier; measure $ spent per assertion passed | ~$20 for matrix |
| **Project Mode gate modulation** | `common/project-mode.md` | Same unit executed in Prototyping vs Production mode; measure human-approval invocations × output quality | ~$5 |

### 2.1 Common properties

These mini-experiments share three properties the existing regex rubric cannot provide:

1. **They measure deltas, not absolute patterns.** The question is "does X improve Y?", not "does the output contain regex Z?".
2. **They isolate one HE claim at a time.** The Proposal B runner deliberately varied only one thing (pre-B vs post-B rule state); the same discipline applies to each row above.
3. **They require runtime measurement, not snapshot matching.** Token counts, tool-call counts, bug-catch rates, cross-host diffs — none of these can be regex-ed out of a single `result.md`.

### 2.2 Template — what already works

[`docs/benchmark/runners/run_gate_benchmark.py`](../../benchmark/runners/run_gate_benchmark.py) is the template. It:

- Drives the Anthropic Bedrock API directly (no Claude Code dependency — exercises pure rule-layer behavior).
- Fires trials in parallel via `asyncio.gather`.
- Imports `grade_skill()` from the existing grader so scoring stays consistent.
- Writes per-run `.md` + `.json` artefacts under `docs/benchmark/results/` (gitignored).
- Emits an aggregated `summary.json` with a machine-readable decision field.

Each row in §2 can follow the same shape: one small Python runner per pattern, its own `summary.json`, its own folder under `docs/benchmark/results/`.

---

## 3. Scope

**In scope for this proposal:** describing what each mini-experiment measures and roughly how much it costs, so that follow-up PRs can pick them up one at a time.

**Out of scope for this proposal:** running any of the mini-experiments. Each is a reasonable size for its own PR.

---

## 4. Until this lands

The claim "Enhanced delivers Harness Engineering benefits beyond the current rubric benchmark" currently rests on:

- Design argument (the [`AIDLC-Rules-Comparison.md` §3](../../benchmark/AIDLC-Rules-Comparison.md) table maps each pattern to a published source).
- Citations to the Anthropic / OpenAI literature that inspired each pattern.
- The one existing quantitative measurement: [Proposal B §6](../landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md) (Gate Output Contract fragility run).

That is honest disclosure, not rhetorical win. Each row in §2 represents one step toward replacing design argument with runtime measurement.

---

## 5. References

- [`landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md`](../landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md) — source of the template runner and the one existing measurement (Proposal B).
- [`docs/benchmark/AIDLC-Rules-Comparison.md`](../../benchmark/AIDLC-Rules-Comparison.md) — per-pattern provenance of what Enhanced adds (§3) and what the regex rubric cannot probe (§5.9).
- [`docs/benchmark/runners/run_gate_benchmark.py`](../../benchmark/runners/run_gate_benchmark.py) — the template implementation.
- Ryan Lopopolo (OpenAI), [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (2026-02-11) — "Anything not in the repository effectively does not exist to Codex."
