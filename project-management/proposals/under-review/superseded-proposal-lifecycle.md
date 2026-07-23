# Superseded Proposal Lifecycle

- ID: FM-PROP-2026-007
- Author: FieldManual maintainers
- Date: 2026-07-23
- Status: Under Review
- Reviewers: repository operator and maintainers
- Affected projects or audiences: projects that retain durable proposal
  history
- Related work:
  [proposal lifecycle](../../../standards-and-practices/core/proposal-and-bug-lifecycle.md)
- Provenance: adapted from a committed, under-review sister-repository
  proposal examined on 2026-07-23

## Problem Statement

An approved or under-review proposal can become inaccurate after another
decision replaces it. Leaving the old record in its prior status implies that
it remains actionable, while rejection or deletion misrepresents its history.

## Goals

- Represent replacement without erasing the old decision.
- Require a link from the old proposal to its replacement.
- Prevent superseded work from authorizing new implementation.
- Keep status metadata and directory placement aligned.

## Non-Goals

- Creating a general archive state.
- Relabeling rejected or deferred proposals as superseded.
- Moving records merely because implementation finished.

## Use Cases

1. A once-approved design is replaced by a later approved contract.
2. An under-review draft is withdrawn in favor of a consolidated proposal.
3. A reader needs to follow both directions between the historical and
   replacement records.

## Constraints And Assumptions

### Verified Constraints

- Existing proposal history is append-only.
- Status metadata and directory placement must agree.
- The core currently recognizes only under-review, approved, rejected, and
  deferred.

### Assumptions

- Supersession requires a concrete replacement, not merely age.
- One additional state may be sufficient for every approved replacement case;
  the open question about under-review records remains undecided.

## Current Context

The template and bootstrap create only the four established proposal status
directories. FieldManual has no superseded-state standard or validation
contract.

## Proposed Approach

Add one `superseded/` proposal state. A record may enter it only when a named
later proposal or decision replaces its operative guidance.

The transition must append:

- date and actor;
- replacement record;
- scope that was replaced;
- any portions that remain historically or operationally relevant; and
- follow-up needed to remove stale references.

The replacement should link back. Superseded proposals remain durable history
but do not authorize future work.

## Alternatives Considered

- Use `rejected/`: inaccurate when the proposal was once accepted.
- Use `deferred/`: implies possible resumption without a new decision.
- Add both `obsolete/` and `superseded/`: unnecessary ambiguity for the first
  lifecycle extension.

## Risks And Mitigations

- Maintainers could use the state as a vague archive. Require a concrete
  replacement.
- Links could point to nonexistent replacements. Validate both directions
  before moving the record.

## Open Questions

- May an under-review proposal be superseded, or should it be rejected with a
  replacement link? Owner: operator.
- Is one bidirectional link sufficient, or should the decision log also name
  the exact replaced scope? Owner: governance maintainers.

## Milestones

1. **Decide whether under-review records qualify.** Owner: repository
   operator. Dependencies: the open-question review and representative
   approved and withdrawn examples. Entry: both lifecycle interpretations are
   documented. Exit: the decision log defines eligible source states.
2. **Update the lifecycle contract.** Owner: governance maintainers.
   Dependencies: proposal approval and the first milestone. Entry: the new
   state's transition rules are approved. Exit: the core standard, manifest,
   status directories, and clean templates agree.
3. **Validate one real transition.** Owner: the affected repository
   maintainer. Dependencies: the updated lifecycle contract and a concrete
   replacement record. Entry: old and replacement records link bidirectionally.
   Exit: the record moves once, stale references are addressed, and status
   metadata matches its directory.

## Validation

Review examples for approved, under-review, rejected, deferred, implemented,
and genuinely replaced proposals. Verify only the last category transitions.

## Adoption And Rollout

If approved, use the following rollout:

- **Migration:** Do not move any record until this proposal is approved and
  the core standard and templates are updated. Then inventory only records
  with concrete replacements.
- **Compatibility:** Readers and project-owned tooling must recognize the new
  state before a project adopts it; projects may retain the four-state
  lifecycle until then.
- **Communication:** Document eligible source states, required replacement
  links, and the non-authorizing meaning of superseded records.
- **Rollback:** If a record was misclassified, move it back to its prior state
  with an append-only correction; never delete its transition history.
- **Retirement:** No existing state is retired. Update stale references that
  treated a genuinely replaced proposal as actionable.

## Decision Log

- 2026-07-23 — Imported as under review. The bootstrap manifest deliberately
  retains only the four established proposal status directories.
