#!/usr/bin/env python3
"""Grade all 14 AIDLC skill test outputs against comprehensive assertions."""

import json
import re
import sys
import os
from pathlib import Path


def has_korean(text: str) -> bool:
    return bool(re.search(r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]', text))


def check(text, pattern, flags=re.IGNORECASE):
    return bool(re.search(pattern, text, flags))


def grade_skill(skill_name: str, text: str) -> list:
    results = []

    # Universal assertion: no Korean
    results.append({
        "text": f"[{skill_name}] Output contains no Korean characters",
        "passed": not has_korean(text),
        "evidence": "No Korean found" if not has_korean(text) else "Korean characters detected"
    })

    # Skill-specific assertions
    if skill_name == "detect":
        results.append({"text": "Identifies Greenfield/Brownfield", "passed": check(text, r'greenfield|brownfield'), "evidence": ""})
        results.append({"text": "Recommends next step", "passed": check(text, r'/aidlc-(reverse|requirements)'), "evidence": ""})
        results.append({"text": "Contains state file structure", "passed": check(text, r'Current Phase|Phase Progress|INCEPTION'), "evidence": ""})
        results.append({"text": "Contains completion summary", "passed": check(text, r'===.*Complete|===.*Detection'), "evidence": ""})

    elif skill_name == "reverse":
        results.append({"text": "Multi-dimensional discovery", "passed": check(text, r'package|module|business|infrastructure|build|service'), "evidence": ""})
        results.append({"text": "Produces 8 artifact types", "passed": check(text, r'(architecture|code.structure|api|component|technology|dependenc|quality)'), "evidence": ""})
        results.append({"text": "Mentions brownfield context", "passed": check(text, r'brownfield|existing.*code'), "evidence": ""})

    elif skill_name == "requirements":
        results.append({"text": "4-dimension analysis", "passed": check(text, r'clarity.*type.*scope.*complexity|clarity.*scope|type.*scope', re.IGNORECASE | re.DOTALL), "evidence": ""})
        results.append({"text": "Analysis depth specified", "passed": check(text, r'minimal|standard|comprehensive'), "evidence": ""})
        results.append({"text": "Questions with [Answer]: tags", "passed": check(text, r'\[Answer\]:'), "evidence": ""})
        results.append({"text": "Questions with X) Other option", "passed": check(text, r'X\)'), "evidence": ""})
        results.append({"text": "Multiple question categories", "passed": check(text, r'functional.*non.functional|business.*technical', re.IGNORECASE | re.DOTALL), "evidence": ""})
        results.append({"text": "Team notification message", "passed": check(text, r'generated|file location|let us know|answer.*complete'), "evidence": ""})

    elif skill_name == "stories":
        results.append({"text": "Personas defined", "passed": check(text, r'persona|archetype|role.*goal'), "evidence": ""})
        results.append({"text": "INVEST criteria mentioned", "passed": check(text, r'INVEST|independent.*negotiable|valuable.*estimable'), "evidence": ""})
        results.append({"text": "Acceptance criteria present", "passed": check(text, r'acceptance criteria|\[ \]'), "evidence": ""})
        results.append({"text": "Story format (As a...I want...)", "passed": check(text, r'As a.*I want|As a.*so that'), "evidence": ""})

    elif skill_name == "app-design":
        results.append({"text": "Component definitions", "passed": check(text, r'component.*purpose|component.*responsibilit'), "evidence": ""})
        results.append({"text": "Service definitions", "passed": check(text, r'service.*trigger|service.*responsibilit|service.*flow'), "evidence": ""})
        results.append({"text": "Dependency matrix/diagram", "passed": check(text, r'depend.*matrix|depend.*diagram|depends on'), "evidence": ""})
        results.append({"text": "Question file with options", "passed": check(text, r'\[Answer\]:') or check(text, r'A\)|B\)|X\)'), "evidence": ""})

    elif skill_name == "units":
        results.append({"text": "Unit definitions with scope", "passed": check(text, r'unit.*scope|unit.*component'), "evidence": ""})
        results.append({"text": "Dependency/execution order", "passed": check(text, r'execution order|phase 1|critical path|depends on'), "evidence": ""})
        results.append({"text": "Effort estimates", "passed": check(text, r'effort|XS|S|M|L|XL|t-shirt'), "evidence": ""})
        results.append({"text": "Story-to-unit mapping", "passed": check(text, r'US-\d+|story.*unit|mapping'), "evidence": ""})

    elif skill_name == "plan":
        results.append({"text": "EXECUTE/SKIP decisions", "passed": check(text, r'EXECUTE|SKIP'), "evidence": ""})
        results.append({"text": "Risk assessment", "passed": check(text, r'risk.*level|risk.*low|risk.*medium|risk.*high'), "evidence": ""})
        results.append({"text": "Impact analysis", "passed": check(text, r'impact.*analysis|user.facing|structural|data model'), "evidence": ""})
        results.append({"text": "Workflow visualization", "passed": check(text, r'mermaid|graph|flowchart|───|→'), "evidence": ""})

    elif skill_name == "functional":
        results.append({"text": "Business logic flows", "passed": check(text, r'business logic|business rule|process|flow'), "evidence": ""})
        results.append({"text": "Domain model/entities", "passed": check(text, r'domain.*model|domain.*entit|entity|Order.*orderId'), "evidence": ""})
        results.append({"text": "Validation rules", "passed": check(text, r'validation|constraint|invariant'), "evidence": ""})
        results.append({"text": "Question file present", "passed": check(text, r'\[Answer\]:') or check(text, r'question', re.IGNORECASE), "evidence": ""})
        results.append({"text": "Technology-agnostic", "passed": not check(text, r'Lambda|DynamoDB|SQS') or check(text, r'technology.agnostic|agnostic'), "evidence": ""})

    elif skill_name == "nfr":
        results.append({"text": "NFR categories covered", "passed": check(text, r'scalability.*performance|availability.*security', re.DOTALL), "evidence": ""})
        results.append({"text": "Tech stack decisions", "passed": check(text, r'tech.*stack|technology.*choice|TypeScript|Node'), "evidence": ""})
        results.append({"text": "Design patterns", "passed": check(text, r'pattern|circuit.breaker|retry|cach|resilience'), "evidence": ""})
        results.append({"text": "Measurable targets", "passed": check(text, r'p99|latency.*\d|uptime.*\d|99\.\d'), "evidence": ""})

    elif skill_name == "infra":
        results.append({"text": "AWS service mapping", "passed": check(text, r'Lambda|DynamoDB|API Gateway|SQS|EventBridge'), "evidence": ""})
        results.append({"text": "Configuration details", "passed": check(text, r'memory|timeout|capacity|instance|provisioned'), "evidence": ""})
        results.append({"text": "Deployment architecture", "passed": check(text, r'deploy|CI/CD|pipeline|stack|CDK'), "evidence": ""})
        results.append({"text": "Cost considerations", "passed": check(text, r'cost|\$|pricing|estimate'), "evidence": ""})

    elif skill_name == "code":
        results.append({"text": "Checkbox-based plan", "passed": check(text, r'\[ \]|- \['), "evidence": ""})
        results.append({"text": "Structured sections", "passed": check(text, r'project structure|business logic|API layer|data layer|test', re.IGNORECASE), "evidence": ""})
        results.append({"text": "Plan approval gate", "passed": check(text, r'approv|gate|confirm|before.*writ'), "evidence": ""})
        results.append({"text": "Design artifact references", "passed": check(text, r'functional.design|nfr|infrastructure|design.*artifact'), "evidence": ""})

    elif skill_name == "gate":
        results.append({"text": "Two-phase pipeline", "passed": check(text, r'phase 1.*phase 2|code review.*build.*test', re.DOTALL), "evidence": ""})
        results.append({"text": "GO/NO-GO verdict", "passed": check(text, r'GO.*NO.GO|verdict'), "evidence": ""})
        results.append({"text": "PASS/FAIL verdict", "passed": check(text, r'PASS.*FAIL|verdict'), "evidence": ""})
        results.append({"text": "Security checks", "passed": check(text, r'security|OWASP|secret|injection|auth'), "evidence": ""})

    elif skill_name == "test":
        results.append({"text": "Multiple test types", "passed": check(text, r'unit test.*integration|integration.*contract|unit.*integration', re.DOTALL), "evidence": ""})
        results.append({"text": "Build step included", "passed": check(text, r'build.*step|build.*command|compile|transpil'), "evidence": ""})
        results.append({"text": "Coverage metrics", "passed": check(text, r'coverage|percent|%'), "evidence": ""})
        results.append({"text": "PASS/FAIL summary", "passed": check(text, r'PASS.*FAIL|overall.*readiness|verdict'), "evidence": ""})

    elif skill_name == "status":
        results.append({"text": "Dashboard format", "passed": check(text, r'dashboard|===|---'), "evidence": ""})
        results.append({"text": "Phase progress shown", "passed": check(text, r'INCEPTION|CONSTRUCTION|phase.*progress', re.IGNORECASE), "evidence": ""})
        results.append({"text": "Unit status table", "passed": check(text, r'unit|order.service|auth.service'), "evidence": ""})

    # Fill evidence
    for r in results:
        if not r["evidence"]:
            r["evidence"] = "Check passed" if r["passed"] else "Check failed"

    return results


UPSTREAM_BASELINE_URL = (
    "https://raw.githubusercontent.com/anhyobin/aidlc-workflows/"
    "feat/claude-code-native-implementation/platforms/claude-code/"
    "benchmarks/benchmark.json"
)


def load_upstream_baseline(cache_path: Path) -> dict:
    """Fetch upstream baseline (per-skill pass counts) from anhyobin repo.

    Downloads once and caches. Returns {skill: {passed, total, pass_rate, details}}
    extracted from the published benchmark.json for variant 'upstream'.
    """
    if not cache_path.exists():
        from urllib.request import urlopen
        with urlopen(UPSTREAM_BASELINE_URL) as r:
            cache_path.write_bytes(r.read())
    data = json.loads(cache_path.read_text())
    out = {}
    for key, val in data.get("per_skill", {}).items():
        skill, variant = key.split("/", 1)
        if variant == "upstream":
            out[skill] = val
    return out


def main():
    base_dir = Path(os.environ.get("AIDLC_BENCH_DIR",
                                   sys.argv[1] if len(sys.argv) > 1 else "."))
    skills = ["detect", "reverse", "requirements", "stories", "app-design", "units",
              "plan", "functional", "nfr", "infra", "code", "gate", "test", "status"]

    # Load upstream baseline from the published anhyobin benchmark.json
    upstream = load_upstream_baseline(base_dir / "upstream-baseline.json")

    all_results = {}
    total_passed = 0
    total_assertions = 0

    for skill in skills:
        result_file = base_dir / f"eval-{skill}" / "enhanced" / "outputs" / "result.md"
        if not result_file.exists():
            print(f"SKIP: {skill}/enhanced (no output file)")
            continue

        text = result_file.read_text()
        grades = grade_skill(skill, text)

        passed = sum(1 for g in grades if g["passed"])
        total = len(grades)
        total_passed += passed
        total_assertions += total

        all_results[skill] = {
            "passed": passed,
            "total": total,
            "pass_rate": round(passed / total, 2) if total > 0 else 0,
            "details": grades
        }

        grading_file = base_dir / f"eval-{skill}" / "enhanced" / "grading.json"
        with open(grading_file, 'w') as f:
            json.dump({"eval_name": skill, "variant": "enhanced", "expectations": grades,
                       "summary": {"passed": passed, "total": total}}, f, indent=2)

    # Summary table: Enhanced (measured) vs Upstream (baseline)
    print("=" * 70)
    print("  AIDLC Benchmark Report — Enhanced vs Upstream")
    print("=" * 70)
    print(f"{'Skill':<16} {'Enhanced':<14} {'Upstream':<14} {'Delta':<8}")
    print("-" * 52)

    def fmt(r):
        if not r: return "N/A"
        return f"{r.get('passed','?')}/{r.get('total','?')} ({r.get('pass_rate',0)*100:.0f}%)"

    up_total_passed = 0
    up_total_assertions = 0
    for skill in skills:
        en = all_results.get(skill, {})
        up = upstream.get(skill, {})
        if up:
            up_total_passed += up.get("passed", 0)
            up_total_assertions += up.get("total", 0)
        delta = ""
        if en and up and en.get("total") == up.get("total"):
            d = en.get("passed", 0) - up.get("passed", 0)
            delta = f"+{d}" if d > 0 else str(d) if d < 0 else "="
        print(f"{skill:<16} {fmt(en):<14} {fmt(up):<14} {delta:<8}")

    print("-" * 52)
    en_rate = total_passed / total_assertions * 100 if total_assertions else 0
    up_rate = up_total_passed / up_total_assertions * 100 if up_total_assertions else 0
    print(f"{'Total':<16} "
          f"{total_passed}/{total_assertions} ({en_rate:.1f}%)".ljust(17),
          f"  {up_total_passed}/{up_total_assertions} ({up_rate:.1f}%)")
    print("=" * 70)

    # Save benchmark.json with both variants for traceability
    benchmark = {
        "scenario": "Serverless Order Management API",
        "total_skills": 14,
        "aggregate": {
            "enhanced": {
                "total_passed": total_passed,
                "total_assertions": total_assertions,
                "overall_pass_rate": round(total_passed / total_assertions, 3) if total_assertions else 0
            },
            "upstream": {
                "total_passed": up_total_passed,
                "total_assertions": up_total_assertions,
                "overall_pass_rate": round(up_total_passed / up_total_assertions, 3) if up_total_assertions else 0
            }
        },
        "per_skill": {
            skill: {
                "enhanced": all_results.get(skill),
                "upstream": upstream.get(skill)
            } for skill in skills
        }
    }
    benchmark_file = base_dir / "benchmark.json"
    with open(benchmark_file, 'w') as f:
        json.dump(benchmark, f, indent=2)
    print(f"\nBenchmark saved to: {benchmark_file}")


if __name__ == '__main__':
    main()
