# Changelog

All notable changes to this project will be documented in this file.

## [0.1.9] - 2026-04-23

### Bug Fixes

- resolve markdownlint violations in fork docs
- format tables and relax MD060 for emoji/wide-unicode rows
- point rules_repo at this fork instead of upstream
- make detect-changes return explicit false instead of defaulting to true

### CI/CD

- retrigger CodeBuild to re-run evaluator (rerun #1)
- skip CodeBuild for non-rule commits via per-commit diff
- skip CodeBuild on non-rule push/tag events (#3)

### Documentation

- add fork rationale, comparison, and file-level change index
- add EVALUATOR-REDESIGN proposal for k-sample gate
- reorganize fork-only docs under docs/enhanced/ and add model-capability proposal

### Features

- adopt AI-DLC Optimized rule set (April 2026 revision)
- restore Quality Bar and Anti-Pattern in question-format-guide

### Miscellaneous

- retarget CI workflows and CODEOWNERS to this fork
- adopt plain SemVer (drop -enhanced.N pre-release suffix) (#4)

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


