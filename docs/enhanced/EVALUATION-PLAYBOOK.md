# Evaluation Playbook

> A reusable procedure for validating rule changes in this fork. Anytime you touch a file under `aidlc-rules/` — add a rule, move a section, reword a template — follow this playbook before merging. The approach isn't novel, but writing it down makes the loop repeatable and hands it off to future contributors (including your future self) as an explicit technique rather than tribal knowledge.

**Author:** Kwangyoung Kim (<kwangyou@amazon.com>)
**Last updated:** 2026-04-24

---

## 1. Why a playbook

Rule-file changes are small-diff, high-leverage edits: two lines can shift a 14-stage generation pipeline's output by 30% on some axes. The corresponding risk is that the same two lines can quietly regress a different axis nobody was measuring. This fork has already seen one such case (see [`docs/enhanced/landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md`](landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md) §3.6 — a Gate Output Contract placed at the top of a rule file inadvertently shortened unrelated instruction files generated earlier in the same stage).

The only reliable defense is **measure → analyze → fix → re-measure** as a standard loop, not an ad-hoc investigation.

The fork maintains **two independent measurement axes** so each change can be checked from a different angle:

| Axis | What it measures | Tool | Wall-clock | Cost |
|---|---|---|---|---|
| **Rubric compliance** | Does the output contain specific strings the regex rubric looks for? Surface-level format conformance across 14 stages × 71 assertions. | `docs/benchmark/runners/run_full_benchmark.py` (full pipeline) + `docs/benchmark/runners/run_gate_benchmark.py` (single-stage fragility) | ~30 min (full) / ~1 min (gate-only) | ~$20–40 / ~$1 |
| **Methodology quality** | Does the generated `aidlc-docs/` tree match the golden reference on intent, design, and completeness? LLM-graded pairwise comparison. | `scripts/aidlc-evaluator/` (same repo) | ~20 min (CodeBuild) | AWS CodeBuild credits |

Neither axis alone is enough. The rubric measures format compliance but cannot tell whether the content is actually good. The evaluator measures content quality but can be noisy across runs, and its qualitative scores drift slowly enough that a single run can mislead. Running both, and cross-checking when they disagree, is what caught the Gate Output Contract side effect.

---

## 2. The loop

### Step 1 — Before you change anything, record a baseline

This step is cheap and the "free insurance" payoff is disproportionate.

**Rubric baseline:**

```bash
# Regenerate `docs/benchmark/benchmark.json` against the current rule files.
cd docs/benchmark/runners
source .venv/bin/activate   # or create: python3 -m venv .venv && pip install -r requirements.txt
export AWS_PROFILE=<your-bedrock-profile>
export AWS_REGION=us-west-2
python3 run_full_benchmark.py --model opus
cd ../..
python3 docs/benchmark/grade.py docs/benchmark
```

`benchmark.json` at HEAD is the rubric baseline. Commit it if you intend to compare against it later; don't if you consider it ephemeral snapshot (it's committed in this repo because CI uses it as a reference point).

**Methodology-quality baseline:**

On CI, this already runs automatically when a PR changes `aidlc-rules/**` (see `.github/workflows/codebuild.yml`). The baseline is the "golden" reference at `scripts/aidlc-evaluator/test_cases/sci-calc/golden-aidlc-docs/`. The trend report comparing the latest PR against the golden is posted as a PR comment.

### Step 2 — Make the rule change

Edit `aidlc-rules/...` as usual. Keep the change small and focused on one hypothesis — mixing two unrelated rule edits in the same commit makes it much harder to diagnose which one caused a regression.

### Step 3 — Fast rubric re-measurement (gate-only fragility check)

If the change is **stage-local** — a single file edit that should only affect one of the 14 stages — run the gate fragility runner first. It's cheap and quick and catches the category of bug where a change makes a stage's output non-reproducible across model tiers.

```bash
cd docs/benchmark/runners
python3 run_gate_benchmark.py --models haiku --states pre,post --trials 2
```

You want:

- `haiku/pre-B mean == 5/5` (or whatever assertion count) **with zero variance** — meaning the change is reproducible even on the weakest tier.
- If variance > 0, the rule is still relying on model capability instead of explicit instruction. This is the "Anything not in the repository effectively does not exist to Codex" lesson — make the rule more explicit until variance collapses.

### Step 4 — Full rubric re-measurement

After the gate check passes, run the full 14-stage pipeline once.

```bash
cd docs/benchmark/runners
python3 run_full_benchmark.py --model opus
cd ../..
python3 docs/benchmark/grade.py docs/benchmark
```

Compare the resulting per-skill table against the baseline from Step 1.

- **Same total** — rubric-level stable; still check the per-skill shape because you might have swapped a gain on one assertion for a loss on another.
- **Higher total** — your change recovered an assertion. Record which one in the commit message.
- **Lower total** — the change regressed a rubric check. Before fixing, read the `notes` field in the failing assertion's `docs/benchmark/results/eval-<skill>/enhanced/grading.json` to confirm whether the regression is structural (a rule issue) or variance (LLM nondeterminism). Three options in increasing cost:
  - Re-run once more — if the next run recovers, it's variance.
  - Re-run with a different seed-equivalent (trial index) — same.
  - Bisect your change by reverting half of the diff.

### Step 5 — Methodology-quality measurement

This is where content regressions that the rubric cannot see surface. It costs more, so only run it if the rubric pass in Step 4 left you confident enough to ship.

**On CI** — push your branch and open a PR. The CodeBuild workflow runs `scripts/aidlc-evaluator/` against the PR's rule set and posts a trend report comment on the PR comparing to the golden baseline.

**Locally** — possible but non-trivial; see `scripts/aidlc-evaluator/README.md` for the standalone invocation. In practice, running it in CI is the low-friction path.

Read the trend report comment carefully. It includes:

| Metric | Watch for |
|---|---|
| Unit tests passed | Sudden drop of >5 vs golden → content regression in generated tests |
| Contract tests | Anything below 100% is a hard failure |
| Lint findings | Non-zero means generated code stopped being clean |
| Qualitative score | Drop of >0.03 is meaningful; investigate via `qualitative-comparison.yaml` under the run artefacts |
| Execution time / tokens | Improvements here are a feature; don't flag them |

### Step 6 — When an evaluator regression surfaces, analyze before patching

The failure mode observed in PR #8 is worth studying because it's the template for how rule-level changes misfire:

1. Rubric measurement (Step 4) passed — Enhanced stayed at 68/71.
2. Evaluator measurement (Step 5) showed **completeness 0.35–0.65** on four `construction/build-and-test/*` instruction documents.
3. Those templates in `build-and-test.md` are byte-identical to upstream — this fork had not edited them.
4. The only edit we *had* made to that file was adding the **Gate Output Contract** at the top.
5. Hypothesis: agents read the contract first, interpreted Phase 1 / Phase 2 as the "real" output, and generated the earlier instruction files more tersely than the templates prescribe.
6. Fix: move the contract to **between Step 8 and Step 9** and prefix with an explicit "applies only to Step 9" scope guard, so it's read only after the earlier instruction files are produced.
7. Re-measure (Step 3 → Step 4 → Step 5) to confirm recovery.

The discipline is: **don't just patch the regressing metric**. Understand *why* the change affected what it affected. Rule files are a single-layer prompt-engineering surface, so every section can indirectly influence every other section. Name the influence pathway before editing again.

### Step 7 — Commit, ship, or iterate

If both axes are clean, commit. If they disagree, iterate Step 2 with a narrower hypothesis.

---

## 3. Two concrete examples

### Example A — Proposal B fragility measurement

See [`landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md`](landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md) §6.

- **Hypothesis:** Opus 4.7 scores 5/5 on the `gate` stage because it synthesizes a 2-phase output structure the rule file doesn't prescribe. Weaker models will regress.
- **Measurement (Step 3):** gate fragility runner, 3 models × 2 rule states (pre/post explicit Gate Output Contract) × 3 trials = 18 runs.
- **Result:** all three tiers moved from 2.0/5 to 5.0/5 after the contract was in the file. Zero variance. Hypothesis confirmed.
- **Cost:** one gate-only runner invocation. ~$5. 1 minute.

### Example B — Gate Output Contract side effect

See [`landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md`](landed/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md) §3.6.

- **Step 4 result** after Proposal B landed: rubric 68/71, same as the pre-PR baseline (the shape of the per-assertion failures shifted but the total held).
- **Step 5 result:** evaluator flagged four `build-and-test/*` instruction files with completeness 0.35–0.65.
- **Step 6 analysis:** Contract position at top of rule file influenced Steps 2–7 indirectly. Not a templates issue.
- **Fix:** relocate contract between Step 8 and Step 9 + scope guard. Re-run Step 3 (still 5/5), re-run Step 5 (in progress at time of writing).

---

## 4. Things that can go wrong

- **Interpreting variance as regression.** A single rubric run is noisy. Anything below ~3-point delta at the total level is within run-to-run noise. Repeat the measurement if in doubt.
- **Reading the trend report executive summary without the details.** The PR comment shows headline numbers. The actual diagnostic signal is in `qualitative-comparison.yaml` per-document notes under the CodeBuild run artefacts. Download the `evaluation.zip`, extract, read the notes.
- **Assuming the rubric measures what you care about.** The current rubric is a regex check authored for a Claude Code–specialized benchmark and does not score the Harness Engineering patterns Enhanced adds. See [`docs/benchmark/AIDLC-Rules-Comparison.md` §5.9](../benchmark/AIDLC-Rules-Comparison.md) for what the rubric cannot see, and [`proposals/HARNESS-ENGINEERING-BENCHMARK-AXIS.md`](proposals/HARNESS-ENGINEERING-BENCHMARK-AXIS.md) for the roadmap to measure those patterns properly.
- **Optimizing for the rubric instead of methodology fidelity.** The rubric is a comparison anchor, not a quality gate. If a rule change raises the rubric by closing a legitimately-failing assertion, good. If it raises the rubric by forcing output to match a Claude Code–specialized string that breaks host portability, that's a regression you chose to accept.
- **Skipping Step 5 to save cost.** The cheap one is Step 3–4. But Step 5 is the only one that would have caught the Gate Output Contract side effect. Don't skip it on rule-level changes.

---

## 5. Tools reference

| Tool | Purpose | Input | Output |
|---|---|---|---|
| `docs/benchmark/runners/run_gate_benchmark.py` | Gate-only fragility check — does the rule file survive the weakest model? | `--models haiku\|sonnet\|opus`, `--states pre,post`, `--trials N` | `docs/benchmark/results/gate-b-validation/summary.json` + per-run `.md`/`.json` |
| `docs/benchmark/runners/run_full_benchmark.py` | Full 14-stage rubric run | `--model opus\|sonnet\|haiku` | `docs/benchmark/results/eval-<skill>/enhanced/outputs/result.md` for each stage |
| `docs/benchmark/grade.py` | Regex rubric scorer (reuses the rubric from `anhyobin/aidlc-workflows`) | `docs/benchmark/results/eval-<skill>/` tree | Prints per-skill table, writes `docs/benchmark/benchmark.json` |
| `scripts/aidlc-evaluator/` (via CodeBuild on PR) | Methodology-quality evaluator | PR changing `aidlc-rules/**` | Trend report as PR comment, `evaluation.zip` artefact with per-document `qualitative-comparison.yaml` notes |

---

## 6. A note on what this playbook isn't

This is not an exhaustive evaluation framework. It is a minimal, reproducible loop for the day-to-day act of changing a rule file and not breaking something. For axis-level validation of individual Harness Engineering patterns (e.g., "does the L1–L5 ladder actually catch more bugs than a single-layer check?"), see the roadmap in [`proposals/HARNESS-ENGINEERING-BENCHMARK-AXIS.md`](proposals/HARNESS-ENGINEERING-BENCHMARK-AXIS.md). Each pattern there is its own follow-up PR, not a day-to-day loop.
