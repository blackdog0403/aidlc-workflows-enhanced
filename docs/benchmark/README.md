# Benchmark: Enhanced Rule Set vs Upstream

Reproducible benchmark comparing this repository's **Enhanced (platform-agnostic) AI-DLC rule set** against the upstream `awslabs/aidlc-workflows` single-file rule (the same baseline used in the Claude Code skills benchmark at [`anhyobin/aidlc-workflows`](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code/benchmarks)).

> **TL;DR** — Enhanced scored **69/71 (97.2%)** vs Upstream **68/71 (95.8%)** on the same regex rubric. See [AIDLC-Rules-Comparison.md](AIDLC-Rules-Comparison.md) for the full analysis.

## Test scenario

**Serverless Order Management API** — e-commerce backend with:

- User authentication (Cognito)
- Order CRUD (Lambda + DynamoDB)
- Payment processing (Stripe via SQS)
- Order notifications (SES / SNS via EventBridge)
- NFR targets: 1,000 orders/min peak, 99.9% availability, sub-200 ms p99 latency
- Tech stack: TypeScript, AWS CDK

Full text in [`scenario.md`](scenario.md) — identical to the upstream reference scenario.

## Methodology

Each of the 14 AI-DLC stages is evaluated under two conditions:

| Condition | Description |
|---|---|
| **Enhanced** | Agent reads the Enhanced rule set in `aidlc-rules/` and produces the stage output |
| **Upstream** | Baseline scores loaded from [`anhyobin/aidlc-workflows`](https://github.com/anhyobin/aidlc-workflows/blob/feat/claude-code-native-implementation/platforms/claude-code/benchmarks/benchmark.json) (`upstream` variant) |

The Enhanced variant is measured by driving an AI-DLC-capable agent (Claude Code, Cursor, Amazon Q, etc.) with this repository's rule set against `scenario.md`, collecting one `result.md` per stage, and scoring each with `grade.py`.

Upstream scores are not re-run — we reuse the published numbers because `grade.py` here is byte-identical to the upstream grader in assertion logic (only infrastructure changes; see §Grader below). This keeps the comparison honest.

## Assertions (71 per variant)

Regex-based rubric, **no LLM-as-judge**. Each skill has 3–7 assertions covering:

- **Structural compliance** — `[Answer]:` tags, `X) Other` options, categorized sections
- **Methodology adherence** — 4-dimension analysis, INVEST criteria, EXECUTE / SKIP decisions, 2-phase gate pipeline, technology-agnostic constraint
- **Artifact completeness** — expected output sections present

## Results

| Approach | Assertions passed | Pass rate |
|---|---|---|
| **Enhanced** | **69/71** | **97.2%** |
| Upstream | 68/71 | 95.8% |

### Enhanced vs Upstream per-skill deltas

| Stage | Enhanced | Upstream | Δ | Notes |
|---|---|---|---|---|
| functional | 6/6 | 5/6 | **+1** | Enhanced's `functional-design.md` explicitly mandates technology-agnostic output (no AWS service names leak) |
| gate | 5/5 | 3/5 | **+2** | Enhanced agents compose 2-phase `GO/NO-GO` + `PASS/FAIL` from `automated-feedback-loops.md` (L1–L5 ladder) + `build-and-test.md` |
| detect | 3/5 | 5/5 | **−2** | Enhanced uses prose next-step phrasing to stay host-agnostic (no `/aidlc-*` slash command); setext `===` completion-header style also differs — both are host-binding cues, not methodology gaps |
| 11 other skills | same | same | = | Identical assertion coverage |

### How Enhanced wins

- `functional/technology-agnostic` — rule file explicitly forbids AWS service names in this stage (`construction/functional-design.md` lines 10, 21).
- `gate/2-phase pipeline` — not prescribed by any single rule file; the agent synthesizes it from L1–L5 ladder + build-and-test rules when both are loaded.

### Structural cost of portability

Two `detect` assertions check for Claude Code slash-command strings and setext `===` heading style — cues Native skill templates carry but the host-agnostic Enhanced rule deliberately does not. A one-line change to `workspace-detection.md` (use `=== Workspace Detection Complete ===` instead of `# 🔍 Workspace Detection Complete`) would close one of the two gaps without breaking host-agnostic design; the slash-command gap is non-closable by design.

## Reproducing locally

### Prerequisites

- Python 3.8+
- Network access on first run (fetches upstream baseline from GitHub; cached afterwards in `upstream-baseline.json`)
- An AI-DLC-capable agent with access to this repository's rule set:
  - **Claude Code** — via `.claude/` in repo root
  - **Cursor / Cline / Amazon Q / Kiro / GitHub Copilot** — see `aidlc-rules/aws-aidlc-rule-details/common/agent-capabilities.md` for path-resolution conventions

### 1. Generate stage outputs

For each of the 14 stages, drive your agent to execute that stage against the scenario in [`scenario.md`](scenario.md) using this repository's rule set. Save each output as:

```text
docs/benchmark/eval-<skill>/enhanced/outputs/result.md
```

Where `<skill>` is one of:

```text
detect reverse requirements stories app-design units
plan functional nfr infra code gate test status
```

Tips:

- Copy the `scenario.md` content as the user request.
- Ensure the agent loads the Enhanced rule set from `aidlc-rules/` (not a different variant).
- Keep outputs **English-only** — the grader enforces this.

### 2. Run the grader

```bash
cd docs/benchmark
python3 grade.py .
```

Output:

```text
======================================================================
  AIDLC Benchmark Report — Enhanced vs Upstream
======================================================================
Skill            Enhanced       Upstream       Delta
----------------------------------------------------
detect           3/5 (60%)      5/5 (100%)     -2
reverse          4/4 (100%)     4/4 (100%)     =
...
----------------------------------------------------
Total            69/71 (97.2%)   68/71 (95.8%)
======================================================================
```

The grader writes:

- `docs/benchmark/eval-<skill>/enhanced/grading.json` — per-skill assertion detail
- `docs/benchmark/benchmark.json` — aggregate report with both Enhanced (measured) and Upstream (baseline) numbers

### 3. Re-fetch the upstream baseline (optional)

If the upstream `benchmark.json` changes, delete the cache and re-run:

```bash
rm docs/benchmark/upstream-baseline.json
python3 grade.py .
```

## Grader (`grade.py`)

This repository's `grade.py` is **behaviorally identical** to [`anhyobin/aidlc-workflows` `grade.py`](https://github.com/anhyobin/aidlc-workflows/blob/feat/claude-code-native-implementation/platforms/claude-code/benchmarks/grade.py) in its assertion logic — the 71-assertion regex rubric is copied verbatim. The only changes are infrastructure:

1. `base_dir` is read from `$AIDLC_BENCH_DIR`, `sys.argv[1]`, or `.` (was hardcoded to the original author's local path).
2. The runner only reads `enhanced` variant result files (was `with_skill` / `upstream` / `without_skill`).
3. The summary table compares Enhanced measured vs Upstream baseline (loaded from the upstream `benchmark.json` via `upstream-baseline.json` cache).
4. Output `benchmark.json` is restructured to hold both variants under `per_skill[<skill>].{enhanced, upstream}`.

The `grade_skill()` function and all `check()` regex calls are untouched.

## Files

| File | Purpose |
|---|---|
| `README.md` | This document |
| `scenario.md` | Serverless Order Management API scenario (identical to upstream) |
| `grade.py` | Regex rubric grader (see §Grader) |
| `benchmark.json` | Latest aggregate results (Enhanced + Upstream) |
| `upstream-baseline.json` | Cached upstream `benchmark.json` for offline runs |
| `AIDLC-Rules-Comparison.md` | Full comparison report — architecture, content diff, Harness Engineering mapping, benchmark analysis |

Stage outputs (`eval-<skill>/enhanced/outputs/result.md`) are **not committed** — they are LLM output, not reproducible byte-for-byte. Regenerate them locally per §Reproducing.

## References

- Upstream benchmark: [`anhyobin/aidlc-workflows` — platforms/claude-code/benchmarks](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code/benchmarks)
- AI-DLC methodology: [AI-DLC Whitepaper (Raja SP, AWS)](https://prod.d13rzhkk8cj2z0.amplifyapp.com/aidlc.pdf)
- Full comparison: [AIDLC-Rules-Comparison.md](AIDLC-Rules-Comparison.md)
