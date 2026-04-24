# Gate-stage B-validation runner

Python benchmark runner that tests whether **Proposal B** in
`docs/enhanced/proposals/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md` is
data-justified. The current `gate` score of 5/5 may be Opus 4.7
synthesizing a 2-phase structure from adjacent rules, not something any
single rule file prescribes. If weaker models (Haiku 4.5, Sonnet 4.6)
score < 5/5 without Proposal B but recover to 5/5 with it, B earns its
~25 lines of rule-file surface. Otherwise B should not ship.

## What it does

- 3 models × 2 states × 3 trials = **18 runs, fired in parallel** via `asyncio`.
- `pre-B` loads the Enhanced rule set unchanged. `post-B` appends the proposed
  "Gate Output Contract" to the system prompt at runtime — **no file on disk
  is modified**.
- Each run is scored with `grade_skill()` imported directly from
  `docs/benchmark/grade.py` (no subprocess, byte-identical rubric).
- Writes 18 × (`.md` + `.json`) plus one aggregated `summary.json` with a
  boolean `decision.b_justified` verdict.

## Prerequisites

- Python 3.8+.
- `pip install -r requirements.txt` → `anthropic[bedrock]>=0.40`, `python-dotenv`.
- **AWS Bedrock access** in a region that has the Claude 4.x inference
  profiles (verified on `us-west-2` with account `596560085204`).
  Uses the boto3 credential chain — `AWS_PROFILE`, `AWS_REGION`, or
  `AWS_BEARER_TOKEN_BEDROCK` all work.

## Run it

```bash
cd docs/benchmark/runners

# AWS creds already in your shell? Just run it.
export AWS_PROFILE=claude-596560085204       # or your profile
export AWS_REGION=us-west-2
python3 run_gate_benchmark.py
```

Defaults: `--models haiku,sonnet,opus --states pre,post --trials 3`
→ 18 runs in parallel, landing in `results/gate-b-validation/`.
Expected wall-clock under ~60s (bounded by the slowest Opus run).

### Smaller runs

Smoke wiring check (1 API call, pennies):

```bash
python3 run_gate_benchmark.py --models haiku --states pre --trials 1
```

Haiku-only gate validation (6 calls, the core experiment):

```bash
python3 run_gate_benchmark.py --models haiku --states pre,post --trials 3
```

### Model ID overrides

The default Bedrock inference profile IDs (us-west-2 region):

| Model | Profile ID |
|---|---|
| Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Sonnet 4.6 | `us.anthropic.claude-sonnet-4-6` |
| Opus 4.7 | `us.anthropic.claude-opus-4-7` |

Override if the revision string shifts, or point at the `global.*` profile family:

```bash
python3 run_gate_benchmark.py \
  --model-haiku global.anthropic.claude-haiku-4-5-20251001-v1:0 \
  --aws-region us-east-1
```

## How to interpret `summary.json`

Decision rule (implemented in code):

| Haiku pre-B mean | Haiku post-B mean | `b_justified` | Action |
|---|---|---|---|
| < 4.5 | ≥ 4.5 | **`true`** | Ship Proposal B alongside A + C. |
| ≥ 4.5 | ≥ 4.5 | `false` | B is currently unnecessary — Haiku already synthesizes the 2-phase structure. Close B without shipping. |
| < 4.5 | < 4.5 | `false` | B as drafted is insufficient; the contract wording needs a rethink before shipping. |

Sonnet / Opus numbers are reported for context but do not drive the binary
verdict — Haiku is the weakest supported tier and the one the decision hinges
on.

## What this runner does **not** do

- Not re-running the other 13 stages — `gate` is the only stage where the B
  hypothesis lives.
- Not touching `aidlc-rules/aws-aidlc-rule-details/construction/build-and-test.md`
  on disk. The "post-B" state is a runtime prompt append; reverting is just
  re-running with `--states pre`.
- Not changing `grade.py`. The `grade_skill()` function is imported as-is.
- Not committing the 18 raw outputs — `results/` is gitignored.

## Files

| Path | Purpose |
|---|---|
| `run_gate_benchmark.py` | The async runner. |
| `requirements.txt` | Python deps. |
| `.gitignore` | Excludes `results/`, `.env`, pycache. |
| `results/gate-b-validation/run-<model>-<state>-<trial>.md` | Raw agent output. |
| `results/gate-b-validation/run-<model>-<state>-<trial>.json` | Per-run score. |
| `results/gate-b-validation/summary.json` | Aggregate + decision. |

## Next step after a run

Paste the relevant `summary.json` excerpt into
`docs/enhanced/proposals/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md §6` as the
gating evidence for Proposal B's disposition.
