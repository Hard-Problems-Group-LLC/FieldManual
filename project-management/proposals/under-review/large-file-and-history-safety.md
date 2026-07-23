# Staged Large-File And Git-History Safety

- ID: FM-PROP-2026-003
- Author: FieldManual maintainers
- Date: 2026-07-23
- Status: Under Review
- Reviewers: repository operator and maintainers
- Affected projects or audiences: repositories with large generated or binary
  artifacts
- Related work:
  [version-control safety](../../../standards-and-practices/core/version-control-safety.md)
- Provenance: adapted from an untracked sister-repository proposal reviewed
  on 2026-07-23

## Problem Statement

Broad staging can place very large artifacts into Git history. Discovery after
commit or push can require disruptive history repair. A reusable prevention
standard is useful, but FieldManual should not install Git hooks or ship
language-specific verification machinery.

## Goals

- Define staged-blob inspection as the relevant prevention boundary.
- Require project-owned thresholds and narrow, reviewable exceptions.
- Make diagnostics identify the path, size, threshold, and recovery action.
- Provide cautious, operator-directed history-analysis and recovery guidance.
- Keep executable checks outside FieldManual.

## Non-Goals

- Selecting a universal size threshold.
- Replacing `.gitignore`, artifact storage, or Git LFS policy.
- Installing or managing hooks.
- Automating force pushes or destructive history rewrites.

## Use Cases

1. A staged build artifact exceeds project policy and is rejected before
   commit.
2. A binary-oriented project adopts a reviewed threshold and narrow
   path-specific exceptions.
3. An operator determines whether historical blobs require a coordinated
   rewrite or can remain unchanged.

## Constraints And Assumptions

### Verified Constraints

- Staged blob content, not only working-tree size, is authoritative.
- Paths may contain whitespace, newlines, or non-ASCII characters.
- Any history rewrite affects collaborators and may invalidate signatures.

### Assumptions

- Hosting-provider limits alone detect some problems too late to prevent
  local-history cleanup.
- Projects adopting this guidance can own their thresholds and exceptions.

## Current Context

FieldManual ships no hook installer or Git verifier. Its core version-control
standard provides safety boundaries but does not yet address large blobs or
history recovery.

## Proposed Approach

Add a language-neutral standard recommending that projects with large-artifact
risk:

- inspect staged blob content rather than only working-tree file sizes;
- use filename-safe transport;
- define a reviewed default threshold in project-owned configuration;
- allow only path-specific, visible exceptions;
- distinguish per-file and aggregate staged-size warnings; and
- run the check before a commit enters shared history.

Add a separate knack for analyzing existing history. It must require backup,
remote and signature impact review, collaborator coordination, post-rewrite
verification, and explicit operator authorization before any rewrite or force
push.

## Risks And Mitigations

- A fixed threshold could reject legitimate binary repositories. Projects own
  the threshold and exceptions.
- Recovery instructions could encourage unnecessary rewrites. Analysis and a
  no-op decision are valid outcomes.
- Hook-only guidance could imply FieldManual installs hooks. Documentation
  must keep verifier ownership explicit.

## Alternatives Considered

1. Depend only on `.gitignore`.
   Rejected because broad staging and generated paths can still bypass intent.
2. Depend only on hosting-provider rejection.
   Rejected because the blob has already entered local history.
3. Select one global threshold.
   Rejected because repository artifact profiles differ materially.

## Validation

A future verifier should cover missing, deleted, renamed, whitespace, and
newline-containing paths; boundary sizes; exceptions; and clear diagnostics.
The recovery knack should be reviewed for destructive-action safeguards.

## Open Questions

- Should FieldManual recommend a warning range without defining a blocking
  default? Owner: repository operator.
- What minimum backup and collaborator-notification evidence should a recovery
  knack require? Owner: version-control reviewers.

## Milestones

1. **Decide the prose policy and configuration ownership.** Owner: repository
   operator. Dependencies: answers to the open questions and representative
   repository evidence. Entry: proposal review is complete. Exit: the decision
   log records the policy boundary and configuration owner.
2. **Draft and review the recovery knack.** Owner: version-control reviewers.
   Dependencies: proposal approval and the first milestone. Entry: the
   prevention boundary and destructive-action safeguards are settled. Exit:
   an adversarial review confirms the knack requires backup, coordination, and
   explicit rewrite authorization.
3. **Pilot an external verifier.** Owner: the adopting verifier maintainer.
   Dependencies: the approved policy and source-only and binary-heavy
   fixtures. Entry: a separately owned verifier implements staged-blob
   inspection. Exit: recorded results cover boundary sizes, unusual paths,
   exceptions, and recovery diagnostics.

## Adoption And Rollout

If approved, use the following opt-in rollout:

- **Migration:** Adoption is opt-in; existing repositories keep their current
  policy until they select thresholds, exceptions, and an owner.
- **Compatibility:** Each project defines thresholds appropriate to its
  artifact profile, while filename-safe staged inspection remains invariant.
- **Communication:** Document thresholds, exceptions, diagnostics, and
  destructive recovery prerequisites for contributors.
- **Rollback:** Disable or revert the separately owned verifier without
  rewriting history. Any history rewrite remains a separately authorized
  operation with its own recovery plan.
- **Retirement:** Retire a prior hook or size check only after the project
  verifies equivalent coverage. No FieldManual executable is superseded.

## Decision Log

- 2026-07-23 — Consolidated the reusable prevention and recovery ideas while
  excluding the source repository's hook and scanning implementations.
