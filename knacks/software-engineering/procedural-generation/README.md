# Procedural-Generation Knacks

Reviewed: 2026-10-13

Use these knacks when code generates content that people will see or play:
layouts, levels and settlements placed into a host world, and the 2D art
that fills them. Both treat generation as a deterministic, testable program
whose output is data, kept apart from the host code that applies it.

## Contents

- [Data-First Generation](data-first/overview.knack.md) —
  a host-free planner that produces a declarative plan, a thin host-side
  executor, invariant tests, and explainable site selection
  - [Plan model and invariants](data-first/plan.knack.md)
  - [Site selection](data-first/sites.knack.md)
- [Procedural Sprite Generation](sprites/overview.knack.md) —
  2D art from code: supersampling, role-named palettes, shared helpers, an
  art-direction document, and review at display size
  - [Python with Pillow](sprites/Python.knack.md)
  - [Review and maintenance](sprites/review.knack.md)

## Related

- [In-Host Smoke Testing](../testing/in-host-smoke/overview.knack.md)
  — checking generated content inside the host

A consuming project owns its art-direction document, palette, host data
identifiers, size limits and thresholds.
