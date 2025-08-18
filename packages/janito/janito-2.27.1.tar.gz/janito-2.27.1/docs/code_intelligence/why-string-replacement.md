# Why Janito Prefers String‑Replacement Rules over Unified Diffs

## Overview

Janito is an LLM‑driven code‑editing agent. Instead of asking the model to **provide a unified diff**, Janito provides tooling primitives that steer the model to emit a set of **deterministic plain‑string find/replace rules**, which Janito then applies atomically. This choice maximises reliability, prompt economy, and alignment with the model’s learned behaviour.

---

## 1  Training‑Signal Alignment

* **Dominant exposure to raw code.** In public‑code crawls, plain source lines outnumber diff tokens by **~20‑40 : 1**. The model has far richer “muscle memory” for patterns like `foo(bar)` than for hunk headers such as `@@ -42,7 +42,8 @@`.
* **Micro‑edit datasets reinforce replacements.** Fine‑tune corpora like *Google Codediffs* and *CommitPack* present before/after snippets aligned token‑by‑token. The most common gradient update is “substitute X with Y,” not “parse and merge a patch.”
* **Pull‑request & review corpora add contextual edits.** Large crawls ingest GitHub PR diffs, mailing‑list patches (e.g., LKML), and Stack Overflow suggested edits. These sources boost the model’s familiarity with diff syntax, but they remain a minority slice of the overall training mix and are often noisier than pristine source.
* **Forums & step‑by‑step tutorials reinforce direct replacements.** Blog posts and Q&A answers frequently present code “before” and “after,” or instruct: *“Change `foo = false` to `foo = true` in your config.”* These snippets rarely include full diff headers; they mirror the granularity of plain string edits, further tuning the model toward replacement‑style transformations.

> **Implication:** A replacement rule asks the model to perform the transformation it has practised millions of times; interpreting a diff asks it to switch to a much rarer skill.

---

## 2  Token‑Budget Efficiency

| Expression of the same change | Typical token cost |
| ----------------------------- | ------------------ |
| Unified diff (6‑line hunk)    | ~70–90 tokens     |
| Plain string‑replacement rule | ~10–15 tokens     |

Shorter prompts leave more room for *actual code* and *high‑level instructions*, reducing context‑window pressure and latency.

---

## 3  Robustness in Real Codebases

* **Line‑shift tolerance.** If the file drifts after the diff was generated, context lines may no longer match. A string rule keyed to the target pattern still fires.
* **Noise immunity.** Email trailers, MIME boundaries, or CI banners embedded in patches confuse parsers but do not affect literal pattern matching.
* **Encoding quirks.** Different EOL conventions or charset mishaps break patch offsets; a plain string match usually survives them.

---

## Takeaway

Plain string‑replacement rules line up with the LLM’s most frequent training examples, use a fraction of the tokens, and sidestep brittle patch‑parsing failure modes. That is why Janito’s selected edit strategy is **rule‑first**.
