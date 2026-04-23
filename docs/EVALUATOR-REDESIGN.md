# Evaluator Redesign — pass@k Gate Proposal

> Design note for replacing the current single-run evaluator gate with a
> k-sample, distribution-based gate. Written against observations from
> PR #1 where the same commit produced three wildly different gate
> verdicts across three runs.

**Author:** Kwangyoung Kim (<blackdog0403@gmail.com>)
**Status:** Draft — not yet implemented
**Last updated:** 2026-04-23

---

## 1. Motivation

The current evaluator is inherited from upstream `awslabs/aidlc-workflows`
and runs once per PR. It compares this single run to a single-run
baseline snapshot and fails the PR if any metric regressed. During the
first release cycle of this fork we observed three back-to-back runs of
**the same commit** produce the following verdicts:

| Run | Rules changed since last run | Contract tests | Qualitative overall | Gate |
| --- | --- | --- | --- | --- |
| 1   | — (initial)                    | 88/88 (100%)   | 0.750 (Δ −0.025)    | FAIL (qualitative) |
| 2   | None (same commit)             | 76/88 (86.4%)  | — (early fail)      | FAIL (contract)    |
| 3   | +40 lines in `question-format-guide.md` | 88/88 (100%) | 0.718 (Δ −0.057) | FAIL (qualitative) |

Observations:

- With **zero rule changes** between Run 1 and Run 2, contract pass
  rate dropped from 100% to 86.4%. That is pure LLM non-determinism
  producing a regression verdict.
- The failure axis shifts between runs (contract ↔ qualitative).
- Regression magnitude is not even stable (−0.025 vs −0.057 for
  qualitative).
- The gate blocks merges on noise. False positives this frequent
  erode trust until the gate is effectively ignored.

**Conclusion:** the gate's signal quality is too low to act as a merge
blocker in its current form. We need a statistical redesign.

---

## 2. Goals & Non-Goals

**Goals.**

- Replace snapshot-vs-snapshot comparison with distribution-vs-distribution.
- Absorb LLM output variance so noise does not block merges.
- Keep cost bounded — full k-sample runs only when they add value.
- Keep deterministic checks (unit tests, lint, security) as hard gates.

**Non-goals.**

- Reduce LLM variance at the source (model/prompt redesign is separate).
- Replace the evaluator altogether. This redesign reuses its plumbing
  and changes the aggregation layer only.
- Upstream these changes to `awslabs/aidlc-workflows`. This is a fork
  decision; upstream may or may not adopt.

---

## 3. Proposed Architecture

### 3.1 k-sample execution

Every gated build runs the evaluator **k** times in parallel and
aggregates. Recommended default: **k = 5**.

```text
trigger (GitHub Actions)
   ↓
CodeBuild batch build (build-list × k + aggregator)
   ├─ run_1 → evaluation-1.zip → S3
   ├─ run_2 → evaluation-2.zip → S3
   ├─ run_3 → evaluation-3.zip → S3
   ├─ run_4 → evaluation-4.zip → S3
   └─ run_5 → evaluation-5.zip → S3
              ↓
       aggregator job (depends on all k)
              ↓
   pass@k stats, median / mean / std / CI  →  gate verdict
```

Recommended implementation path: **CodeBuild Batch builds** (native
fan-out + `depend-on` dependency). Alternative paths (GitHub Actions
matrix, in-container parallelism) discussed in §7.

### 3.2 Raw metrics collected per run

```yaml
run_i:
  # Deterministic (variance ~ 0)
  unit_tests: { passed, failed, total }
  lint_findings: int
  security_findings_high: int

  # Stochastic (LLM variance)
  contract_tests: { passed, failed, total }
  qualitative:
    inception: float       # 0.0 - 1.0
    construction: float
    operations: float
    overall: float

  # Reliability signals
  aidlc_execution: bool    # Stage 1 completion
  infra_failure: bool      # throttle / 5xx / timeout
```

### 3.3 k-sample aggregation rules

| Metric                 | Aggregation               | Reasoning                                                       |
| ---------------------- | ------------------------- | --------------------------------------------------------------- |
| `unit_tests`           | all k must pass           | Deterministic; any failure is real.                             |
| `lint / security_high` | `max` across k            | One detection is meaningful.                                    |
| `contract_pass_rate`   | **median**                | Robust to outliers; mean is pulled by a single bad run.         |
| `qualitative_overall`  | **mean ± std**            | Continuous judge score; mean is the natural point estimate.     |
| `aidlc_execution`      | ≥ `k − 1` succeed         | 1/5 failures tolerated as infra noise.                          |
| `infra_failure`        | excluded from quality gate | Throttle / 5xx must not count against quality.                  |

### 3.4 Gate logic

```python
# For each metric comparing current to baseline distribution.

baseline_mean = baseline.qualitative_mean   # baseline is also k-sample
baseline_std  = baseline.qualitative_std
current_mean  = current.qualitative_mean

# A regression must clear BOTH an absolute floor AND a statistical threshold.
regression_threshold = baseline_mean - max(
    0.05,              # absolute floor — drops smaller than this are noise
    2 * baseline_std   # 2σ (~95% CI) statistical threshold
)

if current_mean < regression_threshold:
    GATE_FAIL(reason="qualitative regression")
```

Gate thresholds for each metric:

| Metric               | Current (broken)     | Proposed                                              |
| -------------------- | -------------------- | ----------------------------------------------------- |
| Unit tests           | all pass             | all pass (unchanged)                                  |
| Lint errors          | 0                    | 0 (unchanged)                                         |
| Security (high)      | 0                    | 0 (unchanged)                                         |
| Contract pass rate   | `== baseline`        | `median ≥ baseline.p25 − 0.05`                        |
| Qualitative overall  | `≥ baseline`         | `mean ≥ baseline.mean − 2·std − 0.05`                 |
| AIDLC execution      | all succeed          | `≥ (k−1)/k` succeed                                   |

### 3.5 Baseline as a distribution

Current `test_cases/sci-calc/golden.yaml` stores a single snapshot.
Replace with a distribution file:

```yaml
# baseline-distribution.yaml
qualitative_overall:
  samples: [0.775, 0.820, 0.791, 0.768, 0.803]
  mean: 0.791
  std: 0.019
  n: 5

contract_pass_rate:
  samples: [1.00, 0.98, 1.00, 0.95, 1.00]
  median: 1.00
  p25: 0.98
  n: 5
```

Baseline regeneration: only on **release tag** (e.g. `v0.1.9-enhanced.0`).
PRs read the baseline, they never rewrite it.

### 3.6 pass@k (reliability metric)

Recorded for observability only, not part of the gate:

```text
pass@k := P(at least one run out of k produces perfect output)
```

Example: with `k=5`, if three runs achieve `contract_pass_rate == 100%`,
`pass@5 = 60%`. This is a reliability health metric — it tells us how
flaky the rules are, independent of whether any specific run regressed.

---

## 4. Worked example — applying the new rules to our three runs

Treating our three runs as a k=3 sample:

```yaml
contract_pass_rate:
  samples: [1.00, 0.864, 1.00]
  median: 1.00
  p25:    0.932

qualitative_overall:
  samples: [0.750, null, 0.718]   # one early-failed run
  mean:    0.734   # n=2
  std:     0.016
```

With the proposed gate (and an illustrative baseline of
`qualitative.mean=0.775, std=0.02`):

- Contract: `median 1.00 ≥ 0.98 − 0.05 = 0.93` → **PASS**
- Qualitative: `0.734 ≥ 0.775 − 2·0.02 − 0.05 = 0.685` → **PASS**

Both would pass under the proposed gate. Today both fail.

---

## 5. Cost control

Full k=5 execution costs roughly 5× compute and 5× Bedrock. To keep
this sustainable:

- **Regular PRs** → single run, `--report-only`, no gate. ~$0.40 / run.
- **Full evaluation on demand** → PR label `full-eval` triggers batch k=5
  with gate. ~$2 compute + Bedrock. On-demand only.
- **Release tag (`v*`)** → always batch k=5 with gate, and regenerate
  baseline on success.

Wall-clock time for a k=5 batch is the same as a single run (parallel
fan-out) — approximately 18 min on `BUILD_GENERAL1_LARGE`.

---

## 6. Open questions

| # | Question | Default |
| --- | --- | --- |
| Q1 | Sample size k | **5** (balances std estimation and cost) |
| Q2 | When to regenerate baseline | **Release tag only** (manual override via workflow_dispatch) |
| Q3 | Regression threshold formula | **`mean − 2·std − 0.05`** (2σ plus absolute floor) |
| Q4 | AIDLC execution tolerance | **≥ (k−1)/k** (allow 1 infra failure) |
| Q5 | Which PRs get k=5 | **`full-eval` label OR release tag** (not every PR) |

These are defaults; revise after first month of data.

---

## 7. Alternatives considered

### A. GitHub Actions matrix fan-out

`strategy.matrix.run: [1..5]`, each cell triggers its own CodeBuild.
Then a separate aggregator job.

- Pros: buildspec unchanged.
- Cons: five concurrent OIDC assumes; aggregator plumbing across
  GitHub artifacts; more moving parts than needed.

### B. In-container parallelism

Add `run.py full --repeat 5 --parallel 5` and do it inside one
CodeBuild.

- Pros: minimal infra change.
- Cons: single container fights itself for CPU / memory / Bedrock
  throughput; no true isolation; Stage 1 executor is already Bedrock-
  heavy and won't benefit from in-process threading.

### C. Do nothing; keep single-run gate

- Pros: zero work.
- Cons: continues to block merges on noise; gate loses credibility;
  real regressions get lost in the false positives.

**Chosen approach:** §3, **CodeBuild Batch builds with a separate
aggregator** (option A from §3.1).

---

## 8. Implementation plan (if approved)

Phased, so we never block the release pipeline while rebuilding it.

1. **Phase 0 — unblock.** Remove `--gate` from `codebuild.yml` trend
   step. Evaluator runs as report-only until the new gate lands.
2. **Phase 1 — baseline generator.** Script that runs k=5 on a given
   ref and writes `baseline-distribution.yaml`. Invoked manually at
   first, via `workflow_dispatch`.
3. **Phase 2 — aggregator.** New package under
   `scripts/aidlc-evaluator/packages/aggregator` that reads k run
   folders and produces the new verdict file.
4. **Phase 3 — batch buildspec.** Rewrite `codebuild.yml` as a batch
   build with k+1 entries. Wire GitHub Actions workflow to
   `start-build-batch`.
5. **Phase 4 — gate on release only.** Enable the new gate for tagged
   release builds. Regular PRs stay report-only.
6. **Phase 5 — opt-in full-eval on PRs.** Label `full-eval` triggers
   batch on a PR. Default stays single-run report-only.

Each phase is independently shippable.

---

## 9. Non-goals reiterated

This proposal does not:

- Change which model the evaluator uses (Opus remains the executor).
- Change the rules under test.
- Introduce new golden documents.
- Coordinate with upstream — upstream keeps its own gate; our fork
  diverges here intentionally.

---

## References

- [`docs/FORK-CHANGES.md`](FORK-CHANGES.md) — file-level change index for this fork
- [`docs/OPTIMIZATION_NOTES.md`](OPTIMIZATION_NOTES.md) — rule-set change rationale
- [pass@k](https://arxiv.org/abs/2107.03374) — original definition from the HumanEval paper
- CodeBuild Batch builds — <https://docs.aws.amazon.com/codebuild/latest/userguide/batch-build.html>

---

**Author:** Kwangyoung Kim (<blackdog0403@gmail.com>)
**Status:** Draft — awaiting review
**Last updated:** 2026-04-23
