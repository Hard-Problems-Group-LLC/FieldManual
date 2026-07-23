# Risk-Triggered Expert Review Board

- ID: FM-PROP-2026-001
- Author: FieldManual maintainers
- Date: 2026-07-23
- Status: Under Review
- Reviewers: repository operator and maintainers
- Affected projects or audiences: FieldManual maintainers and consuming
  projects that adopt the review process
- Related work:
  [review templates](../../../templates/project-management/reviews/)
- Provenance: adapted from an untracked, under-review proposal in the sister
  repository working tree examined on 2026-07-23

## Problem Statement

Changes to reusable standards, bootstrap contracts, security boundaries, and
cross-platform behavior can propagate into many projects. Ordinary author and
maintainer review may leave important questions implicit when the same context
shapes design, implementation, and approval.

FieldManual needs a bounded, evidence-based review option for high-risk work.
It must improve coverage without turning an advisory panel into a policy or
risk authority.

## Goals

- Define seven stable, independent review lenses.
- Use a separate, non-voting evidence and adjudication chair.
- Trigger structured review only when risk warrants the cost.
- Give every reviewer the same immutable, versioned packet.
- Bound design and delivery review to three rounds each.
- Preserve every raw finding, disposition, and resolution.
- Leave scope, policy, deferral, and accepted risk with the operator.

## Non-Goals

- Requiring structured review for routine edits or bookkeeping.
- Replacing project maintainers, the operator, or applicable external review.
- Giving a board power to establish policy or accept risk by vote.
- Requiring every seat to be filled by a human.
- Activating this process merely by storing this proposal or its neutral
  record skeletons.

## Use Cases

1. A reusable bootstrap contract needs independent governance, portability,
   security, operability, and verification review.
2. Several upstream requests converge into one standard whose source and
   disposition must remain traceable.
3. A security-boundary change needs both an adversarial case and a practical,
   evidence-backed mitigation.
4. The operator designates unusual work as high risk even though no automatic
   trigger applies.

## Constraints And Assumptions

### Verified Constraints

- Every seat and the chair are distinct within one review.
- Evidence points to repository content, diffs, test results, or reproducible
  observations.
- Only the operator approves policy, scope, deferral, or accepted risk.

### Assumptions

- Reviewers may be humans or isolated AI contexts.
- The available execution environment may not run seven reviewers
  concurrently; independence matters more than simultaneity.
- Distinct review lenses will expose material issues that ordinary review can
  leave implicit.

## Current Context

FieldManual has neutral packet, finding, and decision templates but no active
board standard, adopted trigger policy, recusal rule, or pilot record. This
proposal is the only authority under discussion and therefore cannot require
its own review process retroactively.

## Proposed Approach

Adopt the following trigger, composition, packet, round, finding, and
decision-gate contract after the open questions are resolved and a pilot
demonstrates it.

## Triggers And Exemptions

Convene the board for:

- major standards or governance changes;
- reusable contracts intended for consuming projects;
- proposals that converge multiple change requests;
- bootstrap, installer, environment-selection, or runtime changes;
- privilege, trust-boundary, secret-handling, supply-chain, or OPSEC changes;
- cross-platform compatibility contracts; and
- other work the operator designates as high risk.

Typographical changes, routine status transitions, and append-only
bookkeeping that changes no behavior are exempt unless the operator says
otherwise.

Approved work receives two distinct reviews:

1. a design review before policy or specification approval; and
2. a delivery review before the implementation is closed.

## Board Composition

| Seat | Review lens |
| --- | --- |
| 1 | Governance and traceability |
| 2 | Knowledge architecture and technical editing |
| 3 | Software architecture and maintainability |
| 4 | Developer experience and bootstrap behavior |
| 5 | Systems, portability, and operations |
| 6 | Adversarial security and OPSEC |
| 7 | Verification, reliability, and defensive controls |
| Chair | Evidence validation, deduplication, and record quality |

Each seat may be filled by a human or an isolated AI reviewer context. Seats
and the chair must be distinct for one review. Reviewers receive equal access
to the packet and prepare first-round findings independently.

The chair determines whether evidence supports a finding and maintains the
record. The chair does not approve scope, set policy, approve deferrals, or
accept risk.

## Immutable Review Packet

The sponsor prepares a packet, and the chair freezes it before review. It
identifies:

- stage, trigger, scope, non-goals, and applicable operator policy;
- proposal, specification, or other design sources;
- implementation diff, validation results, diagnostics, and rollback
  information for delivery review;
- repository revision or explicit worktree snapshot;
- constraints, open questions, and claimed acceptance criteria; and
- packet version and an integrity identifier.

The first-round packet remains immutable. Corrections or new evidence become
versioned addenda supplied to every reviewer before a later round.

## Bounded Review Rounds

Each stage permits at most three rounds:

1. **Independent findings.** Reviewers submit findings without seeing other
   reviewers' conclusions.
2. **Evidence and mitigation.** The chair checks evidence, exposes findings,
   and maps duplicates without deleting raw records. Adversarial claims and
   practical defensive controls are compared directly.
3. **Correction or rebuttal.** The sponsor supplies at most one corrected
   addendum or evidence-backed rebuttal. Reviewers address only affected
   findings, and the chair records final dispositions.

There is no fourth round. Unresolved issues pass to the operator as explicit
gate items, deferrals, rejections, or risk-acceptance decisions.

## Finding Record

Every raw finding contains:

| Field | Requirement |
| --- | --- |
| ID | Stable and never reused |
| Lens | The submitting review seat |
| Stage | `design` or `delivery` |
| Severity | `blocker`, `major`, or `minor` |
| Claim | The alleged problem and consequence |
| Evidence | Repository location, result, diff, or reproducible observation |
| Recommendation | Concrete correction, mitigation, or decision request |
| Chair disposition | Controlled disposition with rationale |
| Resolution | Fix, deferral, accepted risk, or other recorded outcome |

Severities mean:

- `blocker`: approval or completion would violate an explicit safety,
  governance, or required-behavior boundary;
- `major`: a material correctness, reliability, maintainability, portability,
  or usability gap; and
- `minor`: a bounded improvement that does not prevent approval.

Chair dispositions are:

- `confirmed`;
- `duplicate`, with a canonical finding ID;
- `already addressed`;
- `not substantiated`; or
- `out of scope`.

Raw duplicates and not-substantiated findings remain in the audit record.

## Decision Gates

Before design approval or delivery completion, every confirmed blocker and
major must be:

- fixed and verified;
- deferred into a named, traceable record; or
- explicitly accepted as risk by the operator.

Confirmed minors receive a recorded resolution but do not automatically block
approval. Review summaries preserve raw totals by stage, lens, severity,
disposition, and resolution.

## Risks And Mitigations

- Review cost could burden ordinary maintenance. Explicit triggers and
  behavioral exemptions constrain use.
- AI-filled seats could reproduce one model's assumptions. Isolated contexts,
  identical packets, independent first rounds, and evidence requirements
  reduce anchoring.
- Role overlap could create duplicates. The chair maps duplicates without
  erasing them.
- The chair could become a policy authority. Controlled dispositions and
  reserved operator decisions prevent that.
- A dirty worktree may lack a simple integrity identifier. The specification
  must define a reproducible snapshot before adoption.

## Alternatives Considered

1. Continue with ordinary unstructured maintainer review.
   Rejected because high-risk reusable changes can miss specialized lenses
   and leave no controlled finding record.
2. Convene the board for every change.
   Rejected because routine maintenance would bear disproportionate cost.
3. Use one generalist reviewer and the operator.
   Rejected because independent adversarial and operational lenses are
   intentional controls.
4. Let a majority vote approve changes.
   Rejected because the board is advisory and operator authority must remain
   explicit.

## Validation

Before adoption:

- define reviewer recusal and replacement behavior;
- define packet integrity for committed and dirty-worktree reviews;
- decide where raw findings and decision summaries live;
- verify the supplied review templates represent every required field;
- run a tabletop design review with isolated first-round findings; and
- run one design-and-delivery pilot chosen by the operator.

## Open Questions

1. What packet integrity identifier is sufficient for a dirty worktree?
   Owner: evidence chair. Decision point: specification approval.
2. How is a recused or unavailable reviewer replaced without dropping the
   review lens? Owner: governance steward. Decision point: specification
   approval.
3. Do raw findings live beside the packet or in a review-specific directory?
   Owner: repository operator. Decision point: template approval.
4. What sequential execution model preserves independent contexts when
   concurrency is limited? Owner: verification reviewer. Decision point:
   pilot planning.

## Milestones

1. **Operator disposition.** Owner: repository operator. Dependencies:
   resolved open questions and maintainer review. Entry: the proposal and
   review evidence are decision-ready. Exit: approval, rejection, or deferral
   is recorded with rationale.
2. **Canonical standard and templates.** Owner: governance maintainers.
   Dependencies: proposal approval and the first milestone. Entry: triggers,
   authorities, and record locations are approved. Exit: the standard and
   templates define unambiguous triggers, authority, records, and reviewer
   replacement behavior.
3. **Tabletop design review.** Owner: a designated pilot sponsor and evidence
   chair. Dependencies: the canonical standard, complete reviewer roles, and
   a frozen design packet. Entry: packet integrity and recusal behavior are
   testable. Exit: packet, independent-round, and controlled-finding records
   work without granting the chair policy authority.
4. **Delivery pilot.** Owner: the pilot sponsor and repository operator.
   Dependencies: a completed tabletop and an approved bounded implementation.
   Entry: delivery evidence and rollback information are frozen. Exit:
   resolutions, deferrals, and operator risk decisions remain auditable.

## Adoption And Rollout

If approved, use the following rollout:

- **Migration:** This proposal is not active policy. A project adopts it only
  after approval, publication of the canonical standard, and a pilot.
- **Compatibility:** The neutral review templates remain usable without the
  board; adopters may fill seats with humans or isolated AI contexts while
  preserving independence and operator authority.
- **Communication:** Publish triggers, exemptions, role boundaries, packet
  rules, and decision gates before asking a project to adopt the board.
- **Rollback:** Suspend new board reviews if the pilot fails, retain all
  evidence already collected, and return pending decisions to the operator.
- **Retirement:** No current FieldManual review policy is superseded. An
  adopter may retire an informal process only after recording its replacement
  and preserving prior review history.

## Decision Log

- 2026-07-23 — Imported and adapted the sister repository's current proposal
  as under-review FieldManual material. No board requirement was activated.
