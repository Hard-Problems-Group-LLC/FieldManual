# Reusable Roadmap And Frontend Maintainability Guidance

- ID: FM-PROP-2026-006
- Author: FieldManual maintainers
- Date: 2026-07-23
- Status: Under Review
- Reviewers: repository operator and maintainers
- Affected projects or audiences: long-running projects and frontend
  maintainers
- Related work:
  [roadmap template](../../../templates/project-management/development-roadmap.md)
  and [guidelines](../../../standards-and-practices/guidelines/)
- Provenance: adapted from an untracked sister-repository proposal reviewed
  on 2026-07-23

## Problem Statement

Long-running work benefits from a durable phase and workstream view, while
frontend code often hides lifecycle, focus, event-ordering, cleanup,
asynchronous, fallback, and accessibility hazards that deserve nearby
rationale.

These needs are reusable, but the source proposal combined them with one
specific observability product and a proposed mechanical complexity policy.

## Goals

- Define an optional roadmap that complements the backlog and active record.
- Make status projections derive from tracked planning rather than inventing
  scope.
- Improve documentation of non-obvious frontend lifecycle and event hazards.
- Treat complexity metrics as review signals, not proofs of quality.

## Non-Goals

- Requiring a dashboard or named observability product.
- Replacing the backlog with a roadmap.
- Mandating one complexity score or whole-tree rewrite.
- Treating comments as a substitute for simplifying code.

## Use Cases

1. A long-running effort exposes stable phases without reconstructing them
   from backlog history after every context change.
2. A derived status view cites the roadmap and does not invent future scope.
3. A host-managed frontend documents focus, cleanup, and event-order hazards
   beside the affected behavior.
4. A complexity signal prompts review without acting as a mechanical proof of
   poor design.

## Constraints And Assumptions

### Verified Constraints

- The backlog remains the ordered queue.
- The active-task record remains the current execution detail.
- Roadmaps contain approved or directed scope only.

### Assumptions

- Frontend ecosystems differ, so core policy cannot prescribe one metric.
- A durable roadmap reduces recovery cost for sufficiently long-running work.

## Current Context

The clean templates now include `development-roadmap.md`. That create-only
skeleton establishes a place for durable planning but does not require a
dashboard, projection format, or universal roadmap.

FieldManual's UI guidelines already treat cognitive limits as heuristics. More
specific frontend guidance should remain optional and language- or
technology-aware.

## Proposed Approach

For roadmaps:

- keep approved phases and workstreams in one tracked record;
- keep backlog ordering and active-task detail in their existing records;
- link roadmap items to proposals, specifications, and decisions;
- derive compact status views without creating a second source of truth; and
- exclude local runtime, credentials, prompts, and host identifiers.

For frontend maintainability:

- document host lifecycle, focus, event ordering, asynchronous completion,
  cleanup, fallback, and accessibility rationale where it is not obvious;
- recommend review when control-flow complexity obscures behavior;
- apply new guidance to new or behaviorally changed code; and
- allow projects to select metrics and thresholds.

## Alternatives Considered

1. Derive the roadmap from every historical record on demand.
   Rejected because recovery becomes expensive and can invent scope.
2. Replace the backlog with the roadmap.
   Rejected because planning and priority queues serve different purposes.
3. Set one universal complexity threshold.
   Rejected because language, generated code, and risk contexts differ.

## Risks And Mitigations

- The roadmap could become a competing task queue. Keep backlog and active
  ownership explicit.
- Derived status could become a second source of truth. Treat it as
  reproducible projection only.
- Comment requirements could create syntax narration. Require rationale for
  lifecycle and event hazards, not line-by-line description.

## Open Questions

- Should the roadmap remain optional or become a default starter only?
  Owner: operator.
- Which frontend hazards belong in language-neutral guidance versus React or
  TypeScript pages? Owner: documentation maintainers.

## Milestones

1. **Pilot the roadmap skeleton.** Owner: FieldManual maintainers.
   Dependencies: the existing roadmap starter and sustained migration work.
   Entry: approved work spans more than one phase or workstream. Exit: the
   pilot records whether the roadmap improves recovery without duplicating the
   backlog.
2. **Reconcile planning responsibilities.** Owner: governance maintainers.
   Dependencies: evidence from the roadmap pilot. Entry: any overlap or drift
   is documented. Exit: roadmap, backlog, and active-state ownership are
   unambiguous.
3. **Review a frontend application.** Owner: frontend maintainers.
   Dependencies: a real behaviorally changed frontend and applicable language
   or technology guidance. Entry: lifecycle or event hazards need explanation.
   Exit: review evidence shows the guidance explains hazards without requiring
   syntax narration or a universal metric.

## Validation

Pilot the roadmap on one sustained effort and verify the backlog, active
record, and roadmap do not conflict. Review one frontend change to confirm
comments explain hazards rather than syntax.

## Adoption And Rollout

If the broader guidance is approved, use the following rollout:

- **Migration:** The roadmap remains an optional create-only starter; no
  existing project must populate it. Frontend guidance applies to new or
  behaviorally changed code.
- **Compatibility:** Projects retain their existing planning records and
  choose ecosystem-appropriate metrics, if any.
- **Communication:** Document the roadmap's non-authoritative role and place
  frontend guidance in the applicable core, language, or technology page.
- **Rollback:** A project may stop maintaining the optional roadmap or revert
  proposed frontend guidance while preserving its authoritative backlog and
  decisions.
- **Retirement:** No current FieldManual policy is retired. Product-specific
  observability guidance remains excluded.

## Decision Log

- 2026-07-23 — Split reusable planning and maintainability concepts from
  product-specific integration. No universal dashboard or metric was adopted.
