# Backlog

Use this backlog to track pending work in priority order. Keep the next item
at the top. Use a dated bullet with an indented body for each entry. Include a
stable ID, concise context, requestor or owner details, acceptance criteria,
dependencies and blockers, links to authoritative proposals, bugs, or
specifications, and ISO 8601 timestamps.

## Current Queue

- FM-TASK-002 — Review and disposition the imported proposals, beginning with
  [the risk-triggered expert review board](proposals/under-review/risk-triggered-expert-review-board.md).
  Owner: repository operator. Created: 2026-07-23. Dependencies: maintainer
  and decision-authority availability. Blockers: none recorded. Acceptance:
  every proposal is approved, rejected, or deferred with an append-only
  decision record.

- FM-TASK-003 — Conduct a dedicated legal and currency review before deciding
  whether to import the sister repository's license knacks. Owner: repository
  operator or designated legal reviewer. Created: 2026-07-23. Dependencies:
  an assigned reviewer and current authoritative sources. Blocker: no review
  has been assigned. Acceptance: each candidate is independently reviewed or
  explicitly excluded. Related: `knacks/README.md` and FM-DEC-005.

- FM-TASK-005 — Define separately versioned verification submodules only
  after a concrete project demonstrates the need and ownership model. Owner:
  repository operator. Created: 2026-07-23. Dependencies: a concrete adopter,
  bounded verification contract, and named maintainer. Blockers: none
  recorded. Acceptance: FieldManual remains scriptless except for
  `bootstrap.py`. Related: FM-DEC-001 and
  `standards-and-practices/core/development-workflow.md`.
