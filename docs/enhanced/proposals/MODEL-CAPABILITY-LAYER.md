# Model Capability Layer — Proposal

> Design note for adding a **model capability axis** to AI-DLC, complementing
> the existing host capability layer. This proposal is forward-looking; no
> rule files change as part of it.

**Author:** Kwangyoung Kim (<blackdog0403@gmail.com>)
**Status:** Draft — deferred until trigger conditions met (§6)
**Last updated:** 2026-04-23

---

## 1. Motivation

AI-DLC's host capability layer ([`common/agent-capabilities.md`](../../../aidlc-rules/aws-aidlc-rule-details/common/agent-capabilities.md))
answers the question *"what does this IDE/CLI let me do?"* — `full-multi-agent`
vs `subagent-only` vs `single-agent`. It does not answer the orthogonal
question *"what does this model let me do?"*.

That second question is becoming load-bearing for three reasons:

1. **Model-specific capabilities diverge.** Thinking blocks, prompt caching,
   programmatic tool calling, effort levels, safety classifiers — each is
   available only on certain model families and sometimes only on specific
   versions within a family.
2. **Non-Claude models on Claude-native harnesses.** Codex-on-Claude-Code
   and similar cross-host/cross-model configurations are starting to appear.
   The current rule set implicitly assumes Claude models.
3. **Version-specific behavior changes within one family.** Opus 4.7 (April
   2026) introduced `xhigh` effort level, `/ultrareview` in Claude Code, and
   a new tokenizer that changes token count for the same text by roughly
   1.0–1.35×. Rules that hardcode a single model version age quickly.

A model capability layer isolates these differences into **one place** so
downstream rules can branch on capabilities rather than on specific model
IDs or vendors.

---

## 2. Non-goals

What this proposal **does not** do:

- **Hardcode model-version spec tables** in rule files. Any `Opus 4.7: xhigh
  supported` line in a rule becomes stale the day 4.8 ships.
- **Cross-model interoperability** (Claude ↔ GPT ↔ Gemini in the same run).
  Orchestrating a heterogeneous multi-model swarm is a separate problem;
  this proposal just lets a single run know which model it's on.
- **Benchmark tracking.** Which model scores what on SWE-bench is tracked
  upstream by Anthropic / OpenAI / Google; not our job to mirror.
- **Replace the host capability layer.** Model and host are orthogonal axes;
  both remain.

---

## 3. Proposed Architecture

### 3.1 New rule file: `common/model-capabilities.md`

Sibling to `common/agent-capabilities.md`. Same structure:

- **Capability matrix** — families × capabilities, not versions × capabilities.
- **Detection protocol** — how to identify the family (env var, self-report
  question, host inference).
- **Profile collapse** — map the full matrix down to a small number of
  profiles downstream rules can branch on.

### 3.2 Model profiles (3 initial)

| Profile               | Families in scope                              | Hallmark capabilities                                                                   |
| --------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------- |
| `anthropic-native`    | Claude Opus / Sonnet / Haiku (any version)     | Thinking blocks, prompt caching, programmatic tool calling, effort levels, Auto Mode    |
| `openai-style`        | GPT / Codex                                    | JSON-schema tool calls, function calling, different effort/reasoning semantics          |
| `other`               | Gemini, open-source (Llama), unknown           | Fall back to lowest-common-denominator: single-turn tool calls, no caching assumptions  |

These three profiles are deliberately coarse, mirroring the host layer's
`full-multi-agent / subagent-only / single-agent`. Rules branch on
profile, not on specific model IDs.

### 3.3 What each profile gates

Rules that depend on model capabilities become **conditional on profile**:

| Capability (rule-side)               | `anthropic-native` | `openai-style` | `other`            |
| ------------------------------------ | ------------------ | -------------- | ------------------ |
| `/effort` or xhigh-style hints       | native             | map to equivalent | omit               |
| Thinking blocks / reasoning_effort   | native             | omit           | omit               |
| Prompt caching of rule corpus        | use aggressively   | probe first    | assume none        |
| Programmatic tool calling            | native             | JSON fallback  | per-tool sequential |
| Safety classifier / Auto Mode refs   | native             | N/A            | N/A                |
| Tool-call format                     | XML-style          | JSON-schema    | JSON-schema (best effort) |

Each rule that currently assumes an Anthropic-specific feature would gain
a one-line branch like *"if `model_profile != anthropic-native`, fall back
to …"*.

### 3.4 Composition with host profile

`effective_behavior = f(host_profile, model_profile, project_mode)` — three
independent axes already baked into the fork's design:

- `host_profile` (3) × `model_profile` (3) × `project_mode` (3) = 27 cells
- Most cells collapse because the default (fallback) is well-defined
- Only a handful of cells need explicit coverage; the rest inherit defaults

Example composition:

- `full-multi-agent` host + `anthropic-native` model + `Production` mode →
  full multi-agent patterns, effort levels, all gates retained
- `single-agent` host + `other` model + `Prototyping` mode → sequential
  `/clear`-style resets, no effort hints, collapsed gates

### 3.5 Detection protocol (sketch)

Priority order, first match wins:

1. **Explicit override** — `aidlc-state.md` already has a `## Model` block
   the user can set.
2. **Environment hint** — `AIDLC_MODEL_FAMILY` env var (`anthropic` / `openai` /
   `other`), trivial for CI / automation.
3. **Host default** — Claude Code defaults to `anthropic-native`, Amazon Q
   defaults to `anthropic-native` (Q Developer runs on Claude), Codex /
   Copilot Chat default to `openai-style`, etc.
4. **Ask the user** — last resort, same A/B/C/X question format as
   project-mode.md.

---

## 4. Worked example — what changes in an existing rule

`construction/multi-agent-patterns.md` Pattern 4 (Reasoning Sandwich,
max-high-max) currently reads:

> Use `/effort max` for architecture, `/effort high` for implementation,
> `/effort max` for verification.

With a model capability layer, this becomes:

> **`anthropic-native`:** `/effort max → high → max` (native support).
> **`openai-style`:** closest equivalent reasoning setting per phase, or
> omit if not supported.
> **`other`:** no effort hints; rely on prompt-level "think step by step"
> cues only.

Same intent, version-agnostic expression.

---

## 5. Open questions

| # | Question                                                          | Default if no answer                                    |
| - | ----------------------------------------------------------------- | ------------------------------------------------------- |
| Q1 | Is `model_profile` auto-detected or user-declared?               | Auto-detect via host, fall back to asking.              |
| Q2 | How do we handle a host that supports multiple model backends?   | Ask once per session; persist in `aidlc-state.md`.      |
| Q3 | What's the minimum number of profiles? 3? 4? more granularity?   | Start with 3; split only when a rule truly needs it.    |
| Q4 | Do we track the *specific* version for anything?                 | Only for telemetry / reports, never for gate logic.     |
| Q5 | Where do version-specific features (e.g., Opus 4.7 `xhigh`) go? | In release notes / CHANGELOG, not in rule files.        |

---

## 6. Implementation triggers

This proposal stays a draft until **at least two** of the following are true:

1. **Codex-on-Claude-Code (or inverse) has measurable real-world use** —
   i.e., a non-Anthropic model is meaningfully run inside a
   Claude-native harness in the wild.
2. **A rule change is blocked by model-vendor divergence** — i.e., we
   want to add a rule but can't express it uniformly across vendors.
3. **Opus family introduces a capability that cannot be expressed
   vendor-neutrally** — e.g., a Claude-only primitive that a rule depends
   on in a way that would be wrong for GPT/Gemini.
4. **Cross-vendor effort-level mapping becomes well-defined** — i.e., the
   community converges on a standard for "effort" across vendors, making
   Reasoning Sandwich portable.

Until then, the fork keeps implicitly assuming `anthropic-native` and
documents that assumption in [`docs/enhanced/FORK-CHANGES.md`](../FORK-CHANGES.md).

---

## 7. Alternatives considered

### A. Bake model-specific branches directly into existing rules

Every capability-using rule grows an `If Claude do X; if Codex do Y; …`
block.

- **Pros:** No new file; changes are visible where they apply.
- **Cons:** Every future model family edits N files; capability
  definitions drift; rules become unreadable; same branching logic
  repeats across 10+ rules.

### B. A single `common/models.md` table with version-by-version specs

- **Pros:** All facts in one place.
- **Cons:** Stale within weeks of any model release; forces the fork to
  maintain vendor release notes; conflates *fact* (what exists) with
  *rule* (what we do about it).

### C. Do nothing, assume Anthropic forever

- **Pros:** Zero work.
- **Cons:** Implicit assumption means the day a user runs this on a
  non-Anthropic backend, rules silently misbehave. Accumulates over
  time into an unowned compatibility debt.

**Chosen approach:** §3 — profile-based layer that mirrors the existing
host capability layer, implemented only when triggered by §6.

---

## 8. Non-goals reiterated

This proposal does **not** commit the fork to:

- Supporting non-Anthropic models in the near term.
- Maintaining a benchmark comparison of models.
- Changing the executor or evaluator model choice.
- Adding new configuration flags before triggers in §6 fire.

---

## References

- [`docs/enhanced/FORK-CHANGES.md`](../FORK-CHANGES.md) — what this fork already changed
- [`common/agent-capabilities.md`](../../../aidlc-rules/aws-aidlc-rule-details/common/agent-capabilities.md) — the host capability layer this proposal mirrors
- [`common/project-mode.md`](../../../aidlc-rules/aws-aidlc-rule-details/common/project-mode.md) — the third independent axis (phase × host × mode × model)
- Anthropic, [Claude Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7) (2026-04-16) — example of a version that introduces capability deltas (`xhigh` effort, new tokenizer, `/ultrareview`)
- [`docs/enhanced/proposals/EVALUATOR-REDESIGN.md`](EVALUATOR-REDESIGN.md) — a sibling proposal following the same Status / Triggers pattern

---

**Author:** Kwangyoung Kim (<blackdog0403@gmail.com>)
**Status:** Draft — awaiting trigger conditions in §6
**Last updated:** 2026-04-23
