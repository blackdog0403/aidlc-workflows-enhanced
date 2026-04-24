#!/usr/bin/env python3
"""Weaker-model `gate` benchmark runner — validates Proposal B.

Drives the Anthropic API through the AI-DLC `gate` stage with the Enhanced
rule set as the system prompt, across three models (Haiku 4.5 / Sonnet 4.6
/ Opus 4.7) and two rule states (pre-B / post-B), with N trials each, all
fired in parallel via asyncio. Scores each run with `grade_skill()`
imported directly from `docs/benchmark/grade.py`.

Pre-B  = Enhanced rule files loaded as-is.
Post-B = same files + the "Gate Output Contract" appended to the system
         prompt (simulates the proposed `build-and-test.md` edit without
         touching disk).

Outputs under docs/benchmark/results/gate-b-validation/:
  run-<model>-<state>-<trial>.md      raw agent output
  run-<model>-<state>-<trial>.json    per-run grade_skill() result
  summary.json                        aggregate + decision

Exit code is always 0; the decision lives in summary.json["decision"].
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Import the pure grader from the sibling module — no subprocess.
SCRIPT_DIR = Path(__file__).resolve().parent
BENCH_DIR = SCRIPT_DIR.parent
REPO_ROOT = BENCH_DIR.parent.parent
sys.path.insert(0, str(BENCH_DIR))
from grade import grade_skill  # noqa: E402


RULE_DETAILS = REPO_ROOT / "aidlc-rules" / "aws-aidlc-rule-details"
CORE_WORKFLOW = REPO_ROOT / "aidlc-rules" / "aws-aidlc-rules" / "core-workflow.md"
SCENARIO = BENCH_DIR / "scenario.md"

# Loaded in order into the system prompt.
RULE_FILES_PRE_B = [
    CORE_WORKFLOW,
    RULE_DETAILS / "common" / "agent-capabilities.md",
    RULE_DETAILS / "common" / "project-mode.md",
    RULE_DETAILS / "common" / "automated-feedback-loops.md",
    RULE_DETAILS / "construction" / "build-and-test.md",
]

# Verbatim from docs/enhanced/proposals/BENCHMARK-DRIVEN-RULE-IMPROVEMENTS.md §3.2
GATE_OUTPUT_CONTRACT = """\
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
"""

# Default model IDs — Bedrock inference profile IDs in us-west-2.
# Override via --model-<slug> if the revision string shifts.
DEFAULT_MODEL_IDS = {
    "haiku": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "sonnet": "us.anthropic.claude-sonnet-4-6",
    "opus": "us.anthropic.claude-opus-4-7",
}
DEFAULT_AWS_REGION = "us-west-2"

# Synthetic prior-stage context so gate runs in isolation reproducibly.
SYNTHETIC_PRIOR_ARTEFACTS = """\
You are at the Build & Test gate stage. Prior AI-DLC stages are complete.
Treat the following synthetic prior-stage artefacts as ground truth for
your evaluation; do not re-run or re-derive them.

**Code Generation (complete):**
- OrderService unit: TypeScript/CDK, implements order CRUD against DynamoDB `orders` table, payment flow via Stripe SDK enqueued to SQS.
- AuthService unit: Cognito user-pool authorizer, JWT verification middleware, role-based access (buyer / seller / admin).
- NotificationService unit: EventBridge rule consumes `OrderStatusChanged` events, fans out to SES (email) and SNS (push).
- All three units: TypeScript strict mode, no `any`, structured logging (pino), OpenTelemetry spans on all public methods.

**Infrastructure (complete):**
- CDK app with three stacks: ApiStack (Lambda + API Gateway), DataStack (DynamoDB + SQS), NotificationStack (EventBridge + SES + SNS).
- All Lambda functions: 512MB memory, 30s timeout, X-Ray tracing enabled.
- DynamoDB: on-demand capacity, point-in-time recovery enabled.

**Test results (complete):**
- Unit tests: 112 / 115 passing, 3 skipped (flaky SES mocks — tracked separately). Line coverage 84%, branch coverage 78%.
- Integration tests: 18 / 18 passing against local DynamoDB + Stripe test mode.
- Contract tests: 6 / 6 passing (OpenAPI schema validated against consumer expectations).
- Load test: sustained 1,200 orders/min for 10 minutes, p99 = 148ms, 0 errors.

**Security scan (complete):**
- Dependency scan (npm audit): 0 critical, 2 medium (both in transitive dev-only deps, not in runtime path).
- IAM policy review: least-privilege verified; no `*` resources in production stacks.
- Secrets scan (trufflehog): 0 findings.
- OWASP quick review: injection vectors checked (parameterized DynamoDB calls); authN/authZ enforced at API Gateway + Lambda entry; no sensitive data in logs.

**Scenario (from scenario.md):**
{scenario}

Execute the `gate` stage per the rule set loaded in your system prompt.
Produce the complete stage output as the rule prescribes, starting
directly with the completion announcement. Do NOT ask clarifying
questions; treat the synthetic artefacts above as sufficient input.
"""


@dataclass(frozen=True)
class RunKey:
    model: str  # slug: haiku / sonnet / opus
    state: str  # pre / post
    trial: int  # 0-indexed


def load_system_prompt(state: str) -> str:
    parts = []
    for path in RULE_FILES_PRE_B:
        parts.append(f"\n\n<!-- ===== {path.relative_to(REPO_ROOT)} ===== -->\n\n")
        parts.append(path.read_text())
    if state == "post":
        parts.append(
            "\n\n<!-- ===== proposal-B: Gate Output Contract "
            "(runtime-appended, not committed to disk) ===== -->\n\n"
        )
        parts.append(GATE_OUTPUT_CONTRACT)
    return "".join(parts)


def load_user_message() -> str:
    scenario = SCENARIO.read_text()
    return SYNTHETIC_PRIOR_ARTEFACTS.format(scenario=scenario)


async def one_run(
    client,
    key: RunKey,
    model_id: str,
    system_prompt: str,
    user_message: str,
    max_tokens: int,
) -> dict:
    started = time.monotonic()
    try:
        msg = await client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        # Concatenate all text blocks (models may split into multiple).
        text = "".join(
            block.text for block in msg.content if getattr(block, "type", None) == "text"
        )
        error = None
    except Exception as exc:  # noqa: BLE001 — record and continue
        text = ""
        error = f"{type(exc).__name__}: {exc}"
    elapsed = time.monotonic() - started

    grades = grade_skill("gate", text) if text else []
    passed = sum(1 for g in grades if g["passed"])
    total = len(grades)
    return {
        "model_slug": key.model,
        "model_id": model_id,
        "state": key.state,
        "trial": key.trial,
        "elapsed_s": round(elapsed, 2),
        "error": error,
        "passed": passed,
        "total": total,
        "pass_rate": round(passed / total, 3) if total else 0.0,
        "details": grades,
        "output_text": text,
    }


def write_run_artefacts(result: dict, out_dir: Path) -> None:
    slug = f"{result['model_slug']}-{result['state']}-{result['trial']}"
    (out_dir / f"run-{slug}.md").write_text(result["output_text"] or f"<<ERROR: {result['error']}>>\n")
    meta = {k: v for k, v in result.items() if k != "output_text"}
    (out_dir / f"run-{slug}.json").write_text(json.dumps(meta, indent=2))


def aggregate(results: list[dict]) -> dict:
    buckets: dict[tuple[str, str], list[int]] = {}
    for r in results:
        if r.get("error") or r["total"] == 0:
            continue
        buckets.setdefault((r["model_slug"], r["state"]), []).append(r["passed"])

    per_bucket = {}
    for (model, state), scores in buckets.items():
        key = f"{model}/{state}-B"
        per_bucket[key] = {
            "trials": len(scores),
            "mean": round(statistics.fmean(scores), 3),
            "stdev": round(statistics.pstdev(scores), 3) if len(scores) > 1 else 0.0,
            "min": min(scores),
            "max": max(scores),
            "per_trial": scores,
        }

    # Decision rule: Proposal B is data-justified iff Haiku pre-B drops
    # below 4.5/5 AND Haiku post-B recovers to >= 4.5/5.
    hp_pre = per_bucket.get("haiku/pre-B", {})
    hp_post = per_bucket.get("haiku/post-B", {})
    b_justified = None
    rationale = "insufficient data (haiku pre/post missing)"
    if hp_pre and hp_post:
        pre_mean = hp_pre["mean"]
        post_mean = hp_post["mean"]
        b_justified = pre_mean < 4.5 <= post_mean
        rationale = (
            f"Haiku 4.5 pre-B mean {pre_mean}/5 "
            f"(trials {hp_pre['per_trial']}), "
            f"post-B mean {post_mean}/5 "
            f"(trials {hp_post['per_trial']}). "
            f"Decision threshold: pre-B < 4.5 AND post-B >= 4.5."
        )

    return {
        "per_bucket": per_bucket,
        "decision": {"b_justified": b_justified, "rationale": rationale},
    }


async def run_all(
    models: list[str],
    states: list[str],
    trials: int,
    model_ids: dict[str, str],
    out_dir: Path,
    max_tokens: int,
    aws_region: str,
) -> dict:
    try:
        from anthropic import AsyncAnthropicBedrock
    except ImportError as exc:
        raise SystemExit(
            "anthropic[bedrock] SDK not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    # Optional .env support for AWS_PROFILE / AWS_REGION overrides.
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(SCRIPT_DIR / ".env")
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass

    out_dir.mkdir(parents=True, exist_ok=True)
    # AsyncAnthropicBedrock uses the boto3 credential chain by default
    # (AWS_PROFILE / AWS_REGION / instance role / bearer token).
    client = AsyncAnthropicBedrock(aws_region=aws_region)
    user_message = load_user_message()

    # Precompute system prompts per state (same across models & trials).
    system_prompts = {s: load_system_prompt(s) for s in states}

    # Build flat task list.
    tasks = []
    for model in models:
        for state in states:
            for trial in range(trials):
                key = RunKey(model=model, state=state, trial=trial)
                tasks.append(
                    one_run(
                        client=client,
                        key=key,
                        model_id=model_ids[model],
                        system_prompt=system_prompts[state],
                        user_message=user_message,
                        max_tokens=max_tokens,
                    )
                )

    print(
        f"Launching {len(tasks)} runs in parallel "
        f"(models={models}, states={states}, trials={trials})..."
    )
    started = time.monotonic()
    results = await asyncio.gather(*tasks, return_exceptions=False)
    wall = round(time.monotonic() - started, 1)
    print(f"All runs complete in {wall}s wall-clock.")

    # Persist per-run artefacts.
    for r in results:
        write_run_artefacts(r, out_dir)

    summary = {
        "matrix": {"models": models, "states": states, "trials": trials},
        "model_ids": {m: model_ids[m] for m in models},
        "wall_clock_s": wall,
        "runs": [
            {k: v for k, v in r.items() if k != "output_text"} for r in results
        ],
    }
    summary.update(aggregate(results))
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--models",
        default="haiku,sonnet,opus",
        help="Comma-separated subset of {haiku,sonnet,opus}. Default all three.",
    )
    p.add_argument(
        "--states",
        default="pre,post",
        help="Comma-separated subset of {pre,post}. Default both.",
    )
    p.add_argument("--trials", type=int, default=3, help="Trials per (model,state). Default 3.")
    p.add_argument(
        "--output-dir",
        default=str(SCRIPT_DIR.parent / "results" / "gate-b-validation"),
        help="Where to write per-run artefacts and summary.json.",
    )
    p.add_argument("--max-tokens", type=int, default=8000)
    p.add_argument("--model-haiku", default=DEFAULT_MODEL_IDS["haiku"])
    p.add_argument("--model-sonnet", default=DEFAULT_MODEL_IDS["sonnet"])
    p.add_argument("--model-opus", default=DEFAULT_MODEL_IDS["opus"])
    p.add_argument(
        "--aws-region",
        default=os.environ.get("AWS_REGION", DEFAULT_AWS_REGION),
        help="AWS region for Bedrock (default: $AWS_REGION or us-west-2).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    states = [s.strip() for s in args.states.split(",") if s.strip()]
    for m in models:
        if m not in DEFAULT_MODEL_IDS:
            raise SystemExit(f"unknown model slug: {m}")
    for s in states:
        if s not in ("pre", "post"):
            raise SystemExit(f"unknown state: {s}")

    model_ids = {
        "haiku": args.model_haiku,
        "sonnet": args.model_sonnet,
        "opus": args.model_opus,
    }
    out_dir = Path(args.output_dir).expanduser().resolve()

    summary = asyncio.run(
        run_all(
            models=models,
            states=states,
            trials=args.trials,
            model_ids=model_ids,
            out_dir=out_dir,
            max_tokens=args.max_tokens,
            aws_region=args.aws_region,
        )
    )

    # Pretty-print the verdict.
    print()
    print("=" * 70)
    print(" Gate B-Validation Summary")
    print("=" * 70)
    print(f"{'bucket':<20} {'trials':<7} {'mean':<7} {'stdev':<7} {'per-trial'}")
    print("-" * 70)
    for k, v in summary["per_bucket"].items():
        print(
            f"{k:<20} {v['trials']:<7} {v['mean']:<7} "
            f"{v['stdev']:<7} {v['per_trial']}"
        )
    print("-" * 70)
    d = summary["decision"]
    verdict = {True: "YES", False: "NO", None: "UNKNOWN"}[d["b_justified"]]
    print(f" Proposal B justified?  {verdict}")
    print(f" Rationale: {d['rationale']}")
    print("=" * 70)
    print(f"Artefacts written to: {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
