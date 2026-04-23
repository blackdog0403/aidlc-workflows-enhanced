# Fork Changes — File-Level Index

> One-page index of every file in this fork that differs from upstream
> [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows) **v0.1.8**.
> Use this to audit, review, or cherry-pick changes without opening each file.

**This release:** `0.1.9-enhanced.0`
**Upstream baseline:** `v0.1.8`
**Author:** Kwangyoung Kim (blackdog0403@gmail.com)

> [!NOTE]
> **Design principle.** The `aidlc-rules/` tree (what agents actually load) is changed **in place**,
> but all fork metadata — this file, `COMPARISON.md`, `OPTIMIZATION_NOTES.md`, `CHANGELOG.md` —
> lives **outside** the rule tree so agents do not parse it as a rule. See the repo root
> [`README.md`](../README.md#why-this-fork-exists--design-rationale) for the why.

## Quick Navigation

- [Rule Files — New](#rule-files--new-in-this-fork)
- [Rule Files — Modified](#rule-files--modified-from-upstream)
- [CI / Infrastructure Changes](#ci--infrastructure-changes)
- [Meta Documents](#meta-documents-this-fork-only)
- [How to Diff Against Upstream](#how-to-diff-against-upstream)

---

## Rule Files — New in This Fork

All paths are relative to `aidlc-rules/aws-aidlc-rule-details/` unless noted. These files **do not
exist** in upstream v0.1.8.

| File | Purpose (1-line) | Detailed rationale |
| --- | --- | --- |
| `common/agent-capabilities.md` | Host detection + 3-profile fallback matrix (Claude Code / Kiro / Amazon Q / Cursor / Cline / Copilot) | [OPTIMIZATION_NOTES §1](OPTIMIZATION_NOTES.md#1-new-commonagent-capabilitiesmd) |
| `common/project-mode.md` | Prototyping / Production / Hybrid gate-density selection (Greenfield asks once; Brownfield auto-Production) | [OPTIMIZATION_NOTES §2](OPTIMIZATION_NOTES.md#2-new-commonproject-modemd) |
| `common/automated-feedback-loops.md` | L1–L4 auto-fix loop running *inside* AI-DLC's L5 human gate | [OPTIMIZATION_NOTES §11 (related)](OPTIMIZATION_NOTES.md#what-changed-and-why) · [COMPARISON §4](COMPARISON.md#4-areas-improved-by-optimized-vs-original) |
| `common/boundary-based-security.md` | Auto Mode references · AGENTS.md vulnerability guidance · Tier 1/2/3 trust boundaries | [COMPARISON §4](COMPARISON.md#4-areas-improved-by-optimized-vs-original) |
| `common/context-optimization.md` | Knowledge Pyramid + Tool Search (≈85% token reduction) | [COMPARISON §4](COMPARISON.md#4-areas-improved-by-optimized-vs-original) |
| `construction/multi-agent-patterns.md` | 3-path Generator/Evaluator, 3-agent Planner/Generator/Evaluator, parallel units, Architect-Implementer + Reasoning Sandwich | [OPTIMIZATION_NOTES §3](OPTIMIZATION_NOTES.md#3-rewritten-constructionmulti-agent-patternsmd) |
| `operations/entropy-management.md` | Gardener / AutoDream / Compounding Engineering | [COMPARISON §4](COMPARISON.md#4-areas-improved-by-optimized-vs-original) |
| `extensions/cost-optimization/cost-optimization.md` | Model Routing, Effort Level, Programmatic Tool Calling | [COMPARISON §4](COMPARISON.md#4-areas-improved-by-optimized-vs-original) |
| `extensions/cost-optimization/cost-optimization.opt-in.md` | Cost-optimization extension opt-in prompt | (same) |

---

## Rule Files — Modified from Upstream

These files exist in upstream v0.1.8 and are **modified** in this fork. The modification *preserves*
upstream behaviour as the default (in Production mode / on single-agent hosts) and adds branching.

### Core

| File | Change (1-line) | Detailed rationale |
| --- | --- | --- |
| `aws-aidlc-rules/core-workflow.md` | Load capability + mode files at workflow start; mode-modulated approval-gate summary table | [OPTIMIZATION_NOTES §4](OPTIMIZATION_NOTES.md#4-updated-aws-aidlc-rulescore-workflowmd) |

### Inception

| File | Change | Detailed rationale |
| --- | --- | --- |
| `inception/workspace-detection.md` | **New Step 0** runs host-agent detection; state file adds `## Host Agent` / `## Project Mode` blocks; Brownfield auto-selects Production | [OPTIMIZATION_NOTES §6](OPTIMIZATION_NOTES.md#6-updated-inceptionworkspace-detectionmd) |
| `inception/requirements-analysis.md` | **Step 5.1** asks the Project Mode question (Greenfield only) before extension opt-ins | [OPTIMIZATION_NOTES §7](OPTIMIZATION_NOTES.md#7-updated-inceptionrequirements-analysismd) |
| `inception/workflow-planning.md` | Reads Project Mode + Capability Profile; warns when parallelism is left on the table | [OPTIMIZATION_NOTES §8](OPTIMIZATION_NOTES.md#8-updated-inceptionworkflow-planningmd) |

### Construction

| File | Change | Detailed rationale |
| --- | --- | --- |
| `construction/code-generation.md` | **New Step 13.5** L1–L4 feedback + 2-round auto-fix; Step 14/15/16 mode-aware | [OPTIMIZATION_NOTES §5](OPTIMIZATION_NOTES.md#5-updated-constructioncode-generationmd) |
| `construction/build-and-test.md` | `full-multi-agent` hosts wire L1–L3 to `PostToolUse` hooks; final human gate **retained in all modes** | [OPTIMIZATION_NOTES §9](OPTIMIZATION_NOTES.md#9-updated-constructionbuild-and-testmd) |

### Common (also trimmed)

| File | Change | Detailed rationale |
| --- | --- | --- |
| `common/welcome-message.md` | Host-Aware + Mode-Aware bullets; step list reflects detection + mode selection | [OPTIMIZATION_NOTES §10](OPTIMIZATION_NOTES.md#10-updated-commonwelcome-messagemd) |
| `common/error-handling.md` | Trim 373 → ~170 lines (duplicates collapsed into table; all error→action mappings preserved) | [OPTIMIZATION_NOTES §11](OPTIMIZATION_NOTES.md#11-trimmed-for-length-no-semantic-loss) |
| `common/workflow-changes.md` | Trim 285 → ~95 lines (universal protocol + 8-row pattern table) | [OPTIMIZATION_NOTES §11](OPTIMIZATION_NOTES.md#11-trimmed-for-length-no-semantic-loss) |
| `common/question-format-guide.md` | Trim 332 → ~120 lines (single canonical template + validation responses + contradiction-detection block retained) | [OPTIMIZATION_NOTES §11](OPTIMIZATION_NOTES.md#11-trimmed-for-length-no-semantic-loss) |

### Operations

| File | Change | Detailed rationale |
| --- | --- | --- |
| `operations/operations.md` | Updated to reference new `entropy-management.md` | [COMPARISON §3 Operations](COMPARISON.md#3-domain-by-domain-coverage-qualitative) |

> **Corpus size:** upstream 6 650 lines → fork 5 949 lines (~11% reduction) while **adding**
> 9 new rule files and the capability-aware paths. See
> [OPTIMIZATION_NOTES §11](OPTIMIZATION_NOTES.md#11-trimmed-for-length-no-semantic-loss).

---

## CI / Infrastructure Changes

Not loaded by agents — but relevant when re-releasing from a fork.

| File | Change |
| --- | --- |
| `.github/workflows/release-pr.yml` | Hardcoded `awslabs/aidlc-workflows` URLs → `${{ github.repository }}` template |
| `.github/workflows/codebuild.yml` | Fallback `GITHUB_REPOSITORY` default → `blackdog0403/aidlc-workflows-enhanced` |
| `.github/pull_request_template.md` | Contributing + LICENSE URLs → this fork |
| `.github/ISSUE_TEMPLATE/feature_request.yml` | RFC template URL → this fork |
| `.github/CODEOWNERS` | `@awslabs/aidlc-*` teams → `@blackdog0403`; header notes experimental fork |
| `aidlc-rules/VERSION` | `0.1.8` → `0.1.9-enhanced.0` |
| `CHANGELOG.md` | Added `[0.1.9-enhanced.0]` section + fork preamble |

See [`CHANGELOG.md`](../CHANGELOG.md#019-enhanced0---2026-04-22) for the authoritative release record.

---

## Meta Documents (this fork only)

These documents explain **why** the fork exists. Agents do not load them — they live in `docs/`, outside
the rule tree.

| File | Purpose |
| --- | --- |
| [`docs/COMPARISON.md`](COMPARISON.md) | 3-party qualitative comparison: upstream AI-DLC, this fork, and Harness Engineering. Coverage maps, domain-by-domain analysis, philosophy comparison, latest-trends coverage. |
| [`docs/OPTIMIZATION_NOTES.md`](OPTIMIZATION_NOTES.md) | Section-by-section rationale for each `### N. …` change in this fork, plus invariants preserved from AI-DLC and Harness Engineering. |
| [`docs/FORK-CHANGES.md`](FORK-CHANGES.md) | *This file* — one-page index of every file-level change. |

---

## How to Diff Against Upstream

Three ways to audit this fork's changes:

### 1. On GitHub (easiest)

Once this repo is marked as a fork of `awslabs/aidlc-workflows` in its settings, the repo landing
page will show **"This branch is N commits ahead of awslabs/aidlc-workflows:main"**. Click
**Contribute → Compare** to see the full diff.

Alternative: manual compare URL:
<https://github.com/awslabs/aidlc-workflows/compare/v0.1.8...blackdog0403:aidlc-workflows-enhanced:main>

### 2. Locally with git

```bash
# Add upstream as a remote once
git remote add upstream https://github.com/awslabs/aidlc-workflows.git
git fetch upstream --tags

# Diff a single rule file against the upstream v0.1.8 tag
git diff upstream/v0.1.8 -- aidlc-rules/aws-aidlc-rule-details/construction/code-generation.md

# List every file that differs
git diff --stat upstream/v0.1.8 -- aidlc-rules/

# Diff only the rule tree (ignore CI / docs / fork metadata)
git diff upstream/v0.1.8 -- aidlc-rules/aws-aidlc-rules aidlc-rules/aws-aidlc-rule-details
```

### 3. Release assets

Each release attaches `ai-dlc-rules-v<version>.zip`. Unzip upstream's `v0.1.8` and this fork's
`v0.1.9-enhanced.0` side-by-side and run `diff -r` on the two `aidlc-rules/` trees.

---

**Last updated:** 2026-04-22
