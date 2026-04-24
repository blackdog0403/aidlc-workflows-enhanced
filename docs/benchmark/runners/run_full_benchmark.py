#!/usr/bin/env python3
"""Full 14-stage AI-DLC benchmark runner — hybrid sequential pipeline.

Drives the Anthropic Bedrock API through every AI-DLC stage in order,
using the Enhanced rule set as the system prompt and the previous
stage's `result.md` as cumulative context for the next stage. Outputs
are written to `docs/benchmark/results/eval-<skill>/enhanced/outputs/result.md`
so the existing `docs/benchmark/grade.py` can score them directly:

    python3 docs/benchmark/grade.py docs/benchmark/

Compared to the gate-only runner (`run_gate_benchmark.py`), this is a
**sequential** pipeline — each stage depends on the previous one, so
runs cannot be parallelized. Expect ~15-20 minutes for a full run
with Opus 4.7, ~5-7 minutes with Sonnet 4.6 or Haiku 4.5.

**Prompt caching**: the shared `common/*` rules (≈45k tokens) are
marked with `cache_control` so they're re-read from cache on every
stage after the first, cutting token cost ~10x.

**Design principle**: this runner is for *ad-hoc local refresh* of
`benchmark.json`. For CI the authoritative evaluator is
`scripts/aidlc-evaluator/`.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BENCH_DIR = SCRIPT_DIR.parent
REPO_ROOT = BENCH_DIR.parent.parent
sys.path.insert(0, str(BENCH_DIR))
from grade import grade_skill  # noqa: E402

RULE_DETAILS = REPO_ROOT / "aidlc-rules" / "aws-aidlc-rule-details"
CORE_WORKFLOW = REPO_ROOT / "aidlc-rules" / "aws-aidlc-rules" / "core-workflow.md"
SCENARIO = BENCH_DIR / "scenario.md"

# Always loaded into the cacheable system prompt for every stage.
COMMON_RULES = [
    CORE_WORKFLOW,
    RULE_DETAILS / "common" / "process-overview.md",
    RULE_DETAILS / "common" / "agent-capabilities.md",
    RULE_DETAILS / "common" / "project-mode.md",
    RULE_DETAILS / "common" / "context-optimization.md",
    RULE_DETAILS / "common" / "automated-feedback-loops.md",
    RULE_DETAILS / "common" / "content-validation.md",
    RULE_DETAILS / "common" / "depth-levels.md",
    RULE_DETAILS / "common" / "question-format-guide.md",
    RULE_DETAILS / "common" / "terminology.md",
    RULE_DETAILS / "common" / "error-handling.md",
    RULE_DETAILS / "common" / "overconfidence-prevention.md",
    RULE_DETAILS / "common" / "session-continuity.md",
    RULE_DETAILS / "common" / "workflow-changes.md",
    RULE_DETAILS / "common" / "welcome-message.md",
    RULE_DETAILS / "common" / "ascii-diagram-standards.md",
]

# Per-stage rule file + the grade.py skill name. The `status` stage has
# no dedicated rule detail — it's a synthesized dashboard summarizing
# prior state, so the runner provides a purpose-specific instruction.
STAGES: list[tuple[str, Path | None, str]] = [
    ("detect",        RULE_DETAILS / "inception"    / "workspace-detection.md",  "Workspace Detection"),
    ("reverse",       RULE_DETAILS / "inception"    / "reverse-engineering.md",  "Reverse Engineering (skip if Greenfield — emit a short 'skipped, Greenfield' note)"),
    ("requirements",  RULE_DETAILS / "inception"    / "requirements-analysis.md","Requirements Analysis"),
    ("stories",       RULE_DETAILS / "inception"    / "user-stories.md",         "User Stories"),
    ("plan",          RULE_DETAILS / "inception"    / "workflow-planning.md",    "Workflow Planning"),
    ("app-design",    RULE_DETAILS / "inception"    / "application-design.md",   "Application Design"),
    ("units",         RULE_DETAILS / "inception"    / "units-generation.md",     "Units Generation"),
    ("functional",    RULE_DETAILS / "construction" / "functional-design.md",    "Functional Design"),
    ("nfr",           RULE_DETAILS / "construction" / "nfr-design.md",           "NFR Design"),
    ("infra",         RULE_DETAILS / "construction" / "infrastructure-design.md","Infrastructure Design"),
    ("code",          RULE_DETAILS / "construction" / "code-generation.md",      "Code Generation"),
    ("gate",          RULE_DETAILS / "construction" / "build-and-test.md",       "Build and Test (Gate)"),
    ("test",          RULE_DETAILS / "construction" / "build-and-test.md",       "Test Execution"),
    ("status",        None,                                                      "Status Dashboard"),
]

DEFAULT_MODEL_IDS = {
    "haiku":  "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "sonnet": "us.anthropic.claude-sonnet-4-6",
    "opus":   "us.anthropic.claude-opus-4-7",
}
DEFAULT_AWS_REGION = "us-west-2"


def build_cached_system(common_text: str, stage_rule_text: str, stage_label: str) -> list[dict]:
    """Return Anthropic system-prompt blocks with cache_control on the
    stable `common/*` segment. The stage rule and stage label follow
    unlatched so they change per call.
    """
    return [
        {
            "type": "text",
            "text": common_text,
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": (
                f"\n\n===== STAGE RULE =====\n\n"
                f"Stage: {stage_label}\n\n"
                f"{stage_rule_text}\n"
            ),
        },
    ]


def build_user_message(
    scenario: str,
    stage_skill: str,
    stage_label: str,
    prior_outputs: list[tuple[str, str]],
) -> str:
    prior_block = ""
    if prior_outputs:
        parts = []
        for name, text in prior_outputs:
            parts.append(f"\n\n<!-- PRIOR STAGE: {name} -->\n\n{text}")
        prior_block = (
            "\n\nYou have already completed the earlier stages. "
            "Treat the following prior-stage outputs as ground truth — "
            "do not re-derive them, but reference them where relevant:\n"
            + "".join(parts)
        )

    return (
        f"# User Request\n\n{scenario}\n\n"
        f"# Current Stage: {stage_label}\n\n"
        f"Execute the **{stage_label}** stage per the rule set loaded in "
        f"your system prompt. Produce the complete stage output the rule "
        f"prescribes, starting directly with the stage's expected "
        f"completion header. Do NOT ask clarifying questions; make "
        f"reasonable assumptions and proceed. Do NOT output anything "
        f"except the stage artefact itself (no preamble, no summary "
        f"of what you're about to do)."
        f"{prior_block}"
    )


def status_instruction() -> str:
    """No rule file exists for the `status` stage; this synthetic rule
    replicates what the Claude Code `aidlc-status` skill produces.
    """
    return (
        "## Status Dashboard\n\n"
        "Produce a single-file dashboard summarizing AI-DLC progress so "
        "far. Required elements:\n"
        "- `===` banner heading (setext style).\n"
        "- Phase progress (INCEPTION / CONSTRUCTION / OPERATIONS).\n"
        "- Per-unit table listing unit name, stage, status. At minimum "
        "reference `order-service`, `auth-service`.\n"
        "- A compact summary of next steps.\n"
    )


async def one_stage(
    client,
    model_id: str,
    common_text: str,
    scenario: str,
    stage: tuple[str, Path | None, str],
    prior_outputs: list[tuple[str, str]],
    max_tokens: int,
) -> tuple[str, str, float]:
    skill, rule_path, label = stage
    if rule_path is None:
        stage_rule_text = status_instruction()
    else:
        stage_rule_text = rule_path.read_text()

    system_blocks = build_cached_system(common_text, stage_rule_text, label)
    user_message = build_user_message(scenario, skill, label, prior_outputs)

    started = time.monotonic()
    msg = await client.messages.create(
        model=model_id,
        max_tokens=max_tokens,
        system=system_blocks,
        messages=[{"role": "user", "content": user_message}],
    )
    elapsed = time.monotonic() - started
    text = "".join(
        b.text for b in msg.content if getattr(b, "type", None) == "text"
    )
    return skill, text, elapsed


async def run_pipeline(
    model_id: str,
    aws_region: str,
    stages: list[tuple[str, Path | None, str]],
    max_tokens: int,
) -> dict[str, dict]:
    try:
        from anthropic import AsyncAnthropicBedrock
    except ImportError as exc:
        raise SystemExit(
            "anthropic[bedrock] SDK not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(SCRIPT_DIR / ".env")
        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass

    client = AsyncAnthropicBedrock(aws_region=aws_region)

    # Concatenate common rules once with file-header separators.
    common_parts = []
    for path in COMMON_RULES:
        common_parts.append(
            f"\n\n<!-- ===== {path.relative_to(REPO_ROOT)} ===== -->\n\n"
        )
        common_parts.append(path.read_text())
    common_text = "".join(common_parts)

    scenario = SCENARIO.read_text()
    prior_outputs: list[tuple[str, str]] = []
    results: dict[str, dict] = {}

    print(f"Running {len(stages)} stages sequentially on {model_id}...")
    total_started = time.monotonic()

    for idx, stage in enumerate(stages, 1):
        skill, _, label = stage
        print(f"  [{idx:>2}/{len(stages)}] {skill:<14} ({label}) ... ", end="", flush=True)
        try:
            skill, text, elapsed = await one_stage(
                client=client,
                model_id=model_id,
                common_text=common_text,
                scenario=scenario,
                stage=stage,
                prior_outputs=prior_outputs,
                max_tokens=max_tokens,
            )
            grades = grade_skill(skill, text)
            passed = sum(1 for g in grades if g["passed"])
            total = len(grades)
            print(f"{elapsed:5.1f}s  {passed}/{total}")

            # Save to the convention grade.py expects.
            out_dir = BENCH_DIR / "results" / f"eval-{skill}" / "enhanced" / "outputs"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "result.md").write_text(text)

            # Append to cumulative prior-outputs (truncate long ones to
            # keep context budget sane — later stages don't need every
            # word of earlier ones).
            excerpt = text if len(text) <= 6000 else text[:6000] + "\n\n[...truncated...]"
            prior_outputs.append((label, excerpt))
            results[skill] = {
                "passed": passed, "total": total, "elapsed_s": round(elapsed, 2),
            }
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED: {type(exc).__name__}: {exc}")
            results[skill] = {"error": str(exc)}

    total_elapsed = time.monotonic() - total_started
    print(f"\nPipeline complete in {total_elapsed/60:.1f} minutes.")
    print("Stage outputs saved to docs/benchmark/results/eval-*/enhanced/outputs/result.md")
    print("Run `python3 docs/benchmark/grade.py docs/benchmark/` to refresh benchmark.json.")
    return results


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--model",
        default="opus",
        choices=list(DEFAULT_MODEL_IDS.keys()) + ["custom"],
        help="Model slug (haiku/sonnet/opus) or 'custom' with --model-id.",
    )
    p.add_argument("--model-id", default=None, help="Explicit Bedrock inference profile ID.")
    p.add_argument("--aws-region", default=os.environ.get("AWS_REGION", DEFAULT_AWS_REGION))
    p.add_argument("--max-tokens", type=int, default=16000)
    p.add_argument(
        "--stages",
        default=None,
        help=("Comma-separated subset of stage skill names. "
              "Default: all 14 (detect,reverse,requirements,...)."),
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.model == "custom":
        if not args.model_id:
            raise SystemExit("--model custom requires --model-id")
        model_id = args.model_id
    else:
        model_id = args.model_id or DEFAULT_MODEL_IDS[args.model]

    if args.stages:
        wanted = {s.strip() for s in args.stages.split(",") if s.strip()}
        stages = [s for s in STAGES if s[0] in wanted]
        # Preserve ordering even if user passes them out of order.
        missing = wanted - {s[0] for s in stages}
        if missing:
            raise SystemExit(f"unknown stage(s): {sorted(missing)}")
    else:
        stages = STAGES

    results = asyncio.run(
        run_pipeline(
            model_id=model_id,
            aws_region=args.aws_region,
            stages=stages,
            max_tokens=args.max_tokens,
        )
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
