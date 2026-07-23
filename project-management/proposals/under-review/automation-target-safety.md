# Automation Target And User-Home Safety

- ID: FM-PROP-2026-002
- Author: FieldManual maintainers
- Date: 2026-07-23
- Status: Under Review
- Reviewers: repository operator and maintainers
- Affected projects or audiences: maintainers of operator-facing automation
  adopted alongside FieldManual
- Related work: [bootstrap behavior](../../../docs/bootstrap.md) and
  [session boundaries](../../../standards-and-practices/core/session-and-project-boundaries.md)
- Provenance: adapted from an untracked sister-repository proposal reviewed
  on 2026-07-23

## Problem Statement

Project-local automation homes intentionally isolate tool state, but ambient
home-directory and desktop-session variables can then identify the automation
account rather than the human operator. A tool can report success after
writing to an isolated home while the live account uses different files.

## Goals

- Distinguish project-local automation state, an operator account, a live
  session, and system scope.
- Require an explicit target before user-scoped mutation from an isolated
  automation context.
- Derive dependent paths once from that target.
- Report the selected target, source, scope, and intended effects.
- Fail before writing when target evidence conflicts.

## Non-Goals

- Authorizing FieldManual's bootstrap to mutate a user home.
- Selecting one operating-system account-discovery mechanism.
- Bypassing sandbox, privilege, or cross-project approvals.

## Use Cases

1. A tool running with an isolated automation home refuses to install
   user-scoped files without an explicit target.
2. An operator intentionally selects an isolated target and receives accurate
   scope and result reporting.
3. A desktop integration sees conflicting account and session evidence and
   stops before mutation.

## Constraints And Assumptions

### Verified Constraints

- FieldManual's bootstrap remains project-root confined.
- An explicit target does not replace privilege or cross-project approval.

### Assumptions

- Target discovery differs across operating systems and session managers.
- Child operations can inherit misleading ambient home variables.

## Current Context

FieldManual defines local project state under `.local/` but has no
operator-home automation. Future verifier submodules may need this contract;
the bootstrap explicitly prohibits home-directory mutation.

## Proposed Approach

Adopt a general fail-closed standard for future automation:

1. classify the requested scope;
2. accept an explicit target through a documented project-owned interface;
3. detect whether ambient state belongs to an isolated automation home;
4. refuse implicit user or live-session mutation when evidence is ambiguous;
5. pass the resolved target to child operations instead of recomputing it;
6. display the target and mutation class before action; and
7. verify the intended authority actually observes the result.

FieldManual's sole bootstrap remains outside this scope: it may write only
inside the configured project root and must not inspect or mutate a user home.

## Risks And Mitigations

- Conservative detection could reject legitimate custom homes. An explicit,
  validated target provides the recovery path.
- Platform-specific session registries can disagree. Conflicts must stop the
  operation rather than be resolved by precedence guesswork.
- Child processes can reintroduce ambient-state drift. Pass explicit paths
  and validate their confinement.

## Validation

A future implementation should cover normal, isolated, explicit, live-session,
and system scopes; prove no mutation precedes an unsafe-target rejection; and
exercise conflicting authority evidence.

## Alternatives Considered

1. Trust the ambient home unconditionally.
   Rejected because isolation deliberately makes it unsuitable for live-user
   targeting.
2. Always use an operating-system account database.
   Rejected because it may not identify the intended live session or a
   deliberately isolated target.

## Open Questions

- Which target classes belong in the core standard? Owner: repository
  operator. Decision point: proposal disposition.
- Should implementation guidance live in one platform-neutral specification
  plus platform profiles? Owner: documentation maintainers. Decision point:
  standard drafting.

## Milestones

1. **Approve target classes and authority boundaries.** Owner: repository
   operator. Dependencies: answers to the open questions and representative
   platform evidence. Entry: proposal review is complete. Exit: the decision
   log identifies the accepted classes and reserved authorities.
2. **Publish a platform-neutral prose standard.** Owner: documentation
   maintainers. Dependencies: proposal approval and the first milestone.
   Entry: an approved disposition defines the contract. Exit: the canonical
   standard states targeting, failure, and recovery behavior.
3. **Pilot a separately owned implementation.** Owner: the adopting
   automation maintainer. Dependencies: the canonical standard and isolated,
   explicit, and conflicting-target fixtures. Entry: an external automation
   project adopts the contract. Exit: recorded evidence demonstrates safe
   behavior for every required target class.

## Adoption And Rollout

If approved, use the following rollout for this new standard:

- **Migration:** No existing FieldManual home-targeting automation exists, so
  FieldManual has no migration. An adopting tool must document how it replaces
  implicit ambient-home targeting.
- **Compatibility:** Keep platform-specific discovery in adopter-owned
  profiles behind the same fail-closed contract.
- **Communication:** Publish the target classes, authority boundary, and
  operator-visible failure behavior with each adoption.
- **Rollback:** An adopter can disable its target resolver and return to
  non-mutating behavior; rollback must not restore implicit user-home writes.
- **Retirement:** Retire ambient-home targeting only in tools that adopt the
  approved contract. No FieldManual bootstrap behavior is superseded.

## Decision Log

- 2026-07-23 — Adapted the fail-closed target principle and excluded the
  source proposal's Python, XDG, and environment-installer implementation.
