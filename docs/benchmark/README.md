# Benchmark: Enhanced Rule Set vs Upstream

Exploratory benchmark comparing this repository's **Enhanced (platform-agnostic) AI-DLC rule set** against:

1. **Upstream** — [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows) (AWS's official AI-DLC rule source; this fork's baseline — rule files only, no benchmark tooling)
2. **Native Claude Code Skills** — [`anhyobin/aidlc-workflows` — platforms/claude-code](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code), a personal repository where a third-party author packaged AWS's rule files as Claude Code–specific Skills and authored the regex rubric (`grade.py`, `benchmark.json`) this document reuses.

> [!IMPORTANT]
> **This is not an authoritative quality benchmark.** `grade.py` is a personal regex rubric authored by the owner of `anhyobin/aidlc-workflows` to demonstrate the value of their Claude Code Skills packaging; it is not an AWS official, Anthropic official, or independently-validated evaluation. We reuse it unchanged (except for one flag-composition bug fix) only because it is the one publicly published comparison point that covers the same 14 AI-DLC stages and the same scenario. Treat the scores here as an **exploratory comparison** between a host-agnostic rule set and a Claude Code–specialized variant, not as a quality ranking.

---

> **TL;DR** — Enhanced scores **68/71 (95.8%)** on this rubric, tied with Upstream (68/71) and three points below Native (71/71). The three gaps are all design-intent (host portability + AI-DLC methodology compliance + legitimate Greenfield skip). See [AIDLC-Rules-Comparison.md](AIDLC-Rules-Comparison.md) §1.0-§1.2 for why the design expected exactly this shape.

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
| **Upstream** | Baseline scores pinned into `upstream-baseline.json` — the `upstream` variant from `anhyobin/aidlc-workflows`'s `benchmark.json`, which scored the [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows) rule files under the same rubric. |

The Enhanced variant is measured by driving an AI-DLC-capable agent (Claude Code, Cursor, Amazon Q, etc.) with this repository's rule set against `scenario.md`, collecting one `result.md` per stage, and scoring each with `grade.py`.

Upstream scores are not re-run — we reuse a pinned snapshot of previously-published numbers because `grade.py` here preserves the original rubric (authored by the owner of `anhyobin/aidlc-workflows`) verbatim, with only infrastructure changes and one bug fix (see §Grader below). This keeps the cross-variant comparison honest.

## Assertions (71 per variant)

Regex-based rubric, **no LLM-as-judge**. Each skill has 3–7 assertions covering:

- **Structural compliance** — `[Answer]:` tags, `X) Other` options, categorized sections
- **Methodology adherence** — 4-dimension analysis, INVEST criteria, EXECUTE / SKIP decisions, 2-phase gate pipeline, technology-agnostic constraint
- **Artifact completeness** — expected output sections present

## Results (2026-04-23, Opus 4.7 via Bedrock, post Proposals A/B/C)

| Approach | Assertions passed | Pass rate |
|---|---|---|
| Native (`with_skill`, published) | 71/71 | 100.0% |
| **Enhanced** | **68/71** | **95.8%** |
| Upstream (published) | 68/71 | 95.8% |

### Enhanced vs Upstream per-skill deltas

| Stage | Enhanced | Upstream | Δ | Notes |
|---|---|---|---|---|
| functional | 6/6 | 5/6 | **+1** | `functional-design.md` explicitly mandates technology-agnostic output |
| gate | 5/5 | 3/5 | **+2** | Proposal B's Gate Output Contract makes 2-phase `GO/NO-GO` + `PASS/FAIL` explicit across all models |
| detect | 4/5 | 5/5 | **−1** | Host-agnostic prose instead of `/aidlc-*` slash command — documented in Proposal C |
| nfr | 4/5 | 5/5 | **−1** | NFR rule mandates technology-agnostic output (AI-DLC methodology); rubric requires "TypeScript/Node" literal |
| reverse | 3/4 | 4/4 | **−1** | Greenfield scenario → stage legitimately skipped → no artifacts to enumerate |
| 10 other skills | same | same | = | Identical assertion coverage |

### Why the three Enhanced losses are design-intent, not regressions

- `detect/slash-command` — `/aidlc-*` is meaningless on Cursor / Cline / Amazon Q. Enhanced uses prose to stay host-agnostic. Closing this gap would break portability.
- `nfr/tech-stack` — AI-DLC methodology mandates NFR output stay technology-agnostic so the NFR → Infrastructure separation holds. Naming "TypeScript" at the NFR stage would violate the whitepaper.
- `reverse/8-artifacts` — The scenario is Greenfield; the stage correctly produced a short "skipped" message. Emitting artifact category names for a stage that was not executed would be dishonest output.

See [AIDLC-Rules-Comparison.md §5.5–5.6](AIDLC-Rules-Comparison.md) for the per-assertion decomposition and why each gap cannot be closed without walking back a design commitment.

## Reproducing locally

### Prerequisites

- Python 3.8+
- No network required — the upstream baseline is committed as `upstream-baseline.json`
- An AI-DLC-capable agent with access to this repository's rule set:
  - **Claude Code** — via `.claude/` in repo root
  - **Cursor / Cline / Amazon Q / Kiro / GitHub Copilot** — see `aidlc-rules/aws-aidlc-rule-details/common/agent-capabilities.md` for path-resolution conventions

### 1. Generate stage outputs

Two supported paths:

**Option A — automated, ad-hoc local refresh** (recommended, ~15-20 min on Opus 4.7):

```bash
cd docs/benchmark/runners
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export AWS_PROFILE=<your-bedrock-profile>
export AWS_REGION=us-west-2
python3 run_full_benchmark.py --model opus
```

Outputs land in `docs/benchmark/results/eval-<skill>/enhanced/outputs/result.md` (gitignored).

**Option B — interactive Claude Code session:** drive each of the 14 `/aidlc-*` slash commands against the scenario in [`scenario.md`](scenario.md) and save each output to the same path.

The 14 skill names are:

```text
detect reverse requirements stories app-design units
plan functional nfr infra code gate test status
```

Tips:

- The scenario must be provided verbatim.
- The agent must load the Enhanced rule set from `aidlc-rules/` (not a different variant).
- Outputs must be **English-only** — the grader enforces this.

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
detect           4/5 (80%)      5/5 (100%)     -1
reverse          3/4 (75%)      4/4 (100%)     -1
...
gate             5/5 (100%)     3/5 (60%)      +2
----------------------------------------------------
Total            68/71 (95.8%)   68/71 (95.8%)
======================================================================
```

The grader writes:

- `docs/benchmark/results/eval-<skill>/enhanced/grading.json` — per-skill assertion detail
- `docs/benchmark/benchmark.json` — aggregate report with both Enhanced (measured) and Upstream (baseline) numbers (committed)

## Grader (`grade.py`)

**Provenance.** `grade.py` was authored by the owner of [`anhyobin/aidlc-workflows`](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code/benchmarks) — a personal repository. It is *not* part of AWS's official `awslabs/aidlc-workflows` (which ships rule files only, no benchmark tooling) and is not an Anthropic or AWS official evaluation. We pin it here because it is the one publicly available rubric that covers the same 14 AI-DLC stages against the same Serverless Order Management scenario, which makes it a valid — though narrow — cross-variant comparison point.

**Changes from the original:**

1. `base_dir` is read from `$AIDLC_BENCH_DIR`, `sys.argv[1]`, or `.` (was hardcoded to the original author's local path).
2. The runner only reads `enhanced` variant result files (was `with_skill` / `upstream` / `without_skill`).
3. The summary table compares Enhanced measured vs Upstream baseline (loaded from the committed `upstream-baseline.json`).
4. Output `benchmark.json` is restructured to hold both variants under `per_skill[<skill>].{enhanced, upstream}`.
5. **Flag-composition bug fix**: the original `check(text, pattern, flags=re.IGNORECASE)` is replaced with `check(text, pattern, flags=0)` that OR-composes `re.IGNORECASE` inside the body. This lets the three call-sites that pass `re.DOTALL` (nfr / gate / test) keep case-insensitive matching as the assertion text implies, rather than silently degrading to case-sensitive.

The `grade_skill()` function and each assertion's regex are otherwise untouched.

## Files

| File | Purpose |
|---|---|
| `README.md` | This document |
| `scenario.md` | Serverless Order Management API scenario (identical to upstream) |
| `grade.py` | Regex rubric grader (see §Grader) |
| `benchmark.json` | Latest aggregate results (Enhanced + Upstream) — committed |
| `upstream-baseline.json` | Pinned snapshot of per-skill scores for the `upstream` and `with_skill` variants from `anhyobin/aidlc-workflows`'s `benchmark.json` — the cross-variant comparison targets |
| `AIDLC-Rules-Comparison.md` | Full comparison report — architecture, content diff, Harness Engineering mapping, benchmark analysis |
| `runners/run_full_benchmark.py` | Ad-hoc local runner — 14-stage sequential pipeline via Bedrock, produces everything in `results/` |
| `runners/run_gate_benchmark.py` | Gate-only fragility runner used to validate Proposal B |
| `results/` | Per-run LLM outputs and per-skill `grading.json` — **gitignored** (regenerate via runners) |

Stage outputs (`results/eval-<skill>/enhanced/outputs/result.md`) and fragility-test artefacts (`results/gate-b-validation/`) are **not committed** — they are LLM output, not reproducible byte-for-byte. Regenerate them locally per §Reproducing.

## Authoritative methodology quality gate

The regex rubric in this document is a *surface-level format check* reused for honest cross-variant comparison. For methodology fidelity — whether an AI-DLC stage actually produced a correct artefact — the authoritative CI gate is [`scripts/aidlc-evaluator/`](../../scripts/aidlc-evaluator/), a Bedrock-backed end-to-end evaluator (default config `config/default.yaml` pins `opus-4-6` as executor / simulator / scorer). Enhanced passes that gate; treat it as the quality signal, and treat the results here as the format/portability comparison.

## References

- Upstream rule set (AWS official): [`awslabs/aidlc-workflows`](https://github.com/awslabs/aidlc-workflows)
- Claude Code–native variant and source of the regex rubric (personal, third-party): [`anhyobin/aidlc-workflows` — platforms/claude-code](https://github.com/anhyobin/aidlc-workflows/tree/feat/claude-code-native-implementation/platforms/claude-code)
- AI-DLC methodology: [AI-DLC Whitepaper (Raja SP, AWS)](https://prod.d13rzhkk8cj2z0.amplifyapp.com/aidlc.pdf)
- Full comparison: [AIDLC-Rules-Comparison.md](AIDLC-Rules-Comparison.md)
