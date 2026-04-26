# Changelog

All notable changes to this project will be documented in this file.

> This repository is an experimental fork of [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows),
> maintained as a personal R&D playground. Version numbers here evolve independently
> of upstream tags; they are not official AWS releases.

## [Unreleased]

### Changes

- refresh `common/agent-capabilities.md` capability matrix against 2026-04-25 host documentation — most non–Amazon-Q columns show material upgrades (Cursor 1.0/1.7/3.2, Cline v3.56–v3.81, Copilot custom-agents, Kiro hooks)
- split the single `Amazon Q Dev` / `Kiro` columns into three AWS-family columns — `Amazon Q IDE`, `Kiro IDE`, `Kiro CLI` — to match the post-2026 product fragmentation (the Amazon Q Developer CLI was succeeded by Kiro CLI; IDE Plugin and Kiro IDE remain as distinct products)
- split the single "Lifecycle hooks" matrix row into two rows — `observe/feedback` and `block triggering action` — because a single boolean cannot represent Kiro's "some hooks can block, others cannot" reality
- add `kiro-cli` to the host enum in `common/agent-capabilities.md` §2.3 and `inception/workspace-detection.md`, and rename `amazon-q-dev` → `amazon-q-ide` and `kiro` → `kiro-ide`; downstream files updated (breaking change for any external consumer that hardcodes the prior strings)
- update `construction/multi-agent-patterns.md` §1.B to list Kiro IDE, Kiro CLI, and Amazon Q IDE separately, with per-product specifics for steering files vs `.kiro/agents/*.json`
- update `common/welcome-message.md`, `docs/enhanced/OPTIMIZATION_NOTES.md`, `docs/enhanced/COMPARISON.md`, and `docs/enhanced/FORK-CHANGES.md` host listings to match the new column split
- **capability axes refactor**: introduce per-axis capability values in `common/agent-capabilities.md` §1 matrix. Each row now carries an **Axis** column (e.g. `multi_agent`, `hooks_block`, `worktree`) and each cell a short axis-value label (`native`, `user-launched`, `none`, etc.). §2.3 state schema gains a `## Host Capabilities` block; §2.5 documents the matrix → axis-value lookup. §3 fallback tables rewritten to branch on axis values instead of the three-band profile, fixing several incorrect branches (hooks were previously gated to `full-multi-agent` only; Tool Search missed Kiro CLI; worktree missed Cursor/Cline/Copilot).
- **Amazon Q IDE empirical verification**: column re-verified on 2026-04-25 against VS Code (1.52–1.110) and JetBrains changelogs. Corrections landed: `sandbox` was "⚠️ IAM-scoped" → now `none` (IAM governs service calls, not filesystem/shell); `auto_memory` annotated as `semi` with Memory Bank specifics (manual generate, auto reload); `rule_files` path tightened from `.amazonq/` to `.amazonq/rules/`.
- migrate six downstream rule files from `Capability Profile` (3-band) to axis-value branches: `construction/multi-agent-patterns.md`, `construction/code-generation.md`, `construction/build-and-test.md`, `common/automated-feedback-loops.md`, `common/project-mode.md`, `inception/workflow-planning.md`. Behavior-neutral on hosts where the profile and axis values agreed; corrects branches on Cursor/Cline/Copilot where the profile label was historically wrong.
- `Capability Profile` field kept in `aidlc-state.md` as a legacy compatibility bridge (§2.4 marked Deprecated). Removal deferred until no external consumer reads it.

### Known follow-ups

- Remove the legacy `Capability Profile` state field once all external consumers have migrated to `## Host Capabilities` axis values.

## [0.1.9] - 2026-04-23

First release of this fork. Extends upstream AI-DLC **v0.1.8** with patterns from
Anthropic's Harness Engineering corpus (Engineering & Research blog posts published
through 2026-04-22) and adds two new layers (Host Capability, Project Mode) that
keep AI-DLC's decision-quality spine intact while absorbing HE's execution-quality
patterns.

### Features

- adopt AI-DLC Optimized rule set (April 2026 revision) — adds Host Capability Layer, Project Mode Layer, multi-agent patterns, automated feedback loops, context/cost optimization, and entropy management
- add `common/agent-capabilities.md` — capability matrix and detection protocol for Claude Code / Kiro / Amazon Q / Cursor / Cline / Copilot
- add `common/project-mode.md` — Prototyping / Production / Hybrid gate-density selection for Greenfield projects
- add `common/automated-feedback-loops.md` — L1–L4 auto-fix loop inside AI-DLC's L5 approval gate
- add `common/boundary-based-security.md` — Auto Mode and AGENTS.md vulnerability guidance
- add `common/context-optimization.md` — Knowledge Pyramid + Tool Search
- add `construction/multi-agent-patterns.md` — capability-branched 3-path Generator/Evaluator patterns
- add `operations/entropy-management.md` — Gardener / AutoDream / Compounding Engineering
- add `extensions/cost-optimization/` — Model Routing, Effort Level, Programmatic Tool Calling
- restore Quality Bar and Anti-Pattern sections in `common/question-format-guide.md` — five-point quality bar plus Yes/No/Maybe filler anti-pattern, re-added after the initial trim proved too aggressive for weaker models
- add `docs/enhanced/COMPARISON.md`, `docs/enhanced/OPTIMIZATION_NOTES.md`, and `docs/enhanced/FORK-CHANGES.md` — rationale, design invariants, and file-level change index for the optimized rule set
- add `docs/enhanced/proposals/EVALUATOR-REDESIGN.md` — draft proposal for a k-sample distribution-based gate, replacing the current single-run snapshot comparison
- add `docs/enhanced/proposals/MODEL-CAPABILITY-LAYER.md` — draft proposal for a model capability axis (anthropic-native / openai-style / other) complementary to the host capability layer

### Changes

- rewrite `construction/multi-agent-patterns.md` with three implementation paths per pattern (full-multi-agent / subagent-only / single-agent)
- update `aws-aidlc-rules/core-workflow.md` to load capability and mode files at workflow start
- update `construction/code-generation.md` with Step 13.5 (L1–L4 feedback + auto-fix) and mode-aware gates
- update `inception/workspace-detection.md` with Step 0 host-agent detection
- update `inception/requirements-analysis.md` Step 5.1 with Project Mode question
- update `inception/workflow-planning.md` to read Project Mode + Capability Profile
- update `construction/build-and-test.md` — L1–L3 hook wiring on capable hosts; final human gate retained in all modes
- update `common/welcome-message.md` with Host-Aware and Mode-Aware bullets
- trim `common/error-handling.md` (373 → ~170 lines, no semantic loss)
- trim `common/workflow-changes.md` (285 → ~95 lines, no semantic loss)
- trim `common/question-format-guide.md` (332 → ~150 lines, preserves Quality Bar and Anti-Pattern blocks)

### Documentation

- restructure README: move Table of Contents above the Design Rationale, split the About note into identity / motivation / pointers, add "Coverage at a glance" mini-table with link to full 23-row map, record HE corpus cut-off (2026-04-22) alongside upstream v0.1.8 baseline
- fix broken links in fork-only docs — replace references to private internal notes (`harness-engineering_EN.md`, `HE_Perspective_on_AIDLC_EN.md`, `AIDLC_Perspective_on_HE_EN.md`) with public URLs where available or mark as "internal working note" otherwise
- relocate fork-authored docs under `docs/enhanced/` (and `docs/enhanced/proposals/` for design proposals) so upstream-origin docs stay clean and syncable
- remove the just-released Opus 4.7 row from `docs/enhanced/COMPARISON.md` §9 (stale risk — model shipped days before this release)

### CI/CD

- retarget workflows to this fork: replace hardcoded `awslabs/aidlc-workflows` references with `${{ github.repository }}` in `release-pr.yml`, and with fork path in `codebuild.yml` fallback, `pull_request_template.md`, and `ISSUE_TEMPLATE/feature_request.yml`
- switch CODEOWNERS from `@awslabs/aidlc-*` teams to `@blackdog0403` and mark the repo as an experimental fork
- fix evaluator config — point `rules_repo` in `scripts/aidlc-evaluator/config/default.yaml` at this fork instead of upstream so PR evaluation can clone the fork's branches
- skip CodeBuild on non-rule `push` / tag events via `paths-ignore` in `codebuild.yml` — docs-only pushes to main no longer trigger the 18-minute evaluator run (#3)

### Infrastructure

- bump `aidlc-rules/VERSION` to `0.1.9` — first release of this fork; versioning evolves independently of upstream tags (#4)

## [0.1.8] - 2026-04-22

### Bug Fixes

- typo in core-workflow.md
- rename rule and move to bottom of Critical Rules section
- require actual system time for audit timestamps (#56)
- correct GitHub Copilot instructions and Kiro CLI rule-details path resolution (#82, #84) (#87)
- codebuild cache and download fix (#93)
- correct copy-paste error in error-handling.md (#96)
- add required environmental github token (#137)
- Add security extension disclaimer (#134)
- refactor error handling and PR creation in release workflow (#140)
- address PR #140 review feedback for release workflow (#141)
- remove retention-days limit from CodeBuild workflow artifacts (#149)
- skip PR comment steps for fork PRs with read-only GITHUB_TOKEN (#154)
- correct GitHub API path for deleting label-reminder comment (#157)
- remove report-bundle CodeBuild secondary artifact and add --local-run-dir support (#162)
- use PR head branch for rules-ref instead of merge ref (#168)
- write aidlc-rules/VERSION in release PR to trigger CodeBuild (#169)
- restore PR head branch detection lost in #172 merge (#173)
- Modify tag creation process in tag-on-merge workflow (#174)
- Update CodeBuild action version and add trigger (#175)
- forks skip codebuild (#178)
- present extension opt-in prompts in user's conversation language (#177)
- Minor updates to README (#192)
- explicitly set tag_name in release workflow (#197)
- address security scanners follow-up items (#180) (#199)

### CI/CD

- add markdownlint infrastructure (#159)

### Documentation

- update README to direct users to GitHub Releases (#61)
- add Windows CMD setup instructions and ZIP note (#68)
- clarify ZIP download location and consolidate notes (#70)
- add developer's guide for running CodeBuild locally (#94)
- add working-with-aidlc interaction guide and writing-inputs documents (#121)
- comprehensive documentation review and remediation (#113)

### Features

- add Kiro CLI support and multi-platform architecture
- adding AIDLC skill to work with IDEs such as Claude, OpenCode and others
- addin
- add leo file
- add test automation friendly code generation rules
- add frontend design coverage in Construction phase
- add CodeBuild workflow (#92)
- add code owners (#112)
- changelog-first release flow with build artifacts on draft releases (#125)
- add AIDLC Evaluation & Reporting Framework (#115)
- update pull request linting conditions (#131)
- add cross-release trend reporting package (#136)
- align CodeBuild workflow with current evaluator CLI and add trend report pipeline  (#147)
- gate CodeBuild on 'codebuild' label + aidlc-rules paths (#150)
- auto-label PRs touching aidlc-rules/ with codebuild label (#158)
- post trend report executive summary as PR comment (#172)
- add security scanners workflow (#161)
- agent-driven setup —  drop the manual steps (#109)
- detect and flag infrastructure failures in trend reports (#202)

### Miscellaneous

- removing wrong files
- removing wrong files
- add templates for github issues (#97)
- bump pyjwt in /scripts/aidlc-evaluator (#129)
- bump pillow in /scripts/aidlc-evaluator (#130)
- bump requests in /scripts/aidlc-evaluator (#146)
- bump cryptography in /scripts/aidlc-evaluator (#148)
- bump pygments in /scripts/aidlc-evaluator (#151)
- bump aiohttp in /scripts/aidlc-evaluator (#163)
- bump cryptography in /scripts/aidlc-evaluator (#179)
- bump pytest in /scripts/aidlc-evaluator (#184)
- bump pillow in /scripts/aidlc-evaluator (#183)
- Fix CodeQL action versions in workflow (#191)
- bump python-multipart in /scripts/aidlc-evaluator (#186)
- bump python-dotenv (#201)


