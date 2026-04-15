# Wiki Link Conventions

Status: Draft

## Purpose

Define how Markdown wiki links resolve to canonical pages while supporting
human-friendly display text across the repository's browsable documents.

## Questions To Settle

- What is the canonical page naming convention?
- How should aliases and former names be represented?
- What link syntax will be authoritative?
- How should display-text links such as `[my first car|Honda Accord]` be
  interpreted?
- How should missing or ambiguous targets be handled?

## Initial Direction

Canonical identities should remain stable even when display text changes.
Display aliases in links should improve readability without changing the target
entity or document.

Wiki-link conventions should apply not only to `data/wiki/`, but also to
viewer-browsable Markdown in `project-management/`, `docs/`, and active
guidance documents in `FieldManual/`.
