# Wiki Link Conventions

Status: Draft

## Purpose

Define how Markdown wiki links resolve to canonical pages while supporting
human-friendly display text across the repository's browsable documents.

## Questions To Settle

- What is the canonical page naming convention?
- How should aliases and former names be represented?
- What link syntax will be authoritative?
- If the project adopts `[[target|display text]]` wiki links, which side names
  the canonical target, and how are literal brackets escaped?
- How should missing or ambiguous targets be handled?

## Initial Direction

Canonical identities should remain stable even when display text changes.
Display aliases in links should improve readability without changing the target
entity or document.

If a project adopts wiki links outside the knowledge-base content tree, it
should define how those links coexist with portable Markdown links and how
automated or manual validation detects broken targets.
