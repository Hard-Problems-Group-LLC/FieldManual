# Operator-Facing Tool Audit, Mutation, And Output Contract

- ID: FM-PROP-2026-004
- Author: FieldManual maintainers
- Date: 2026-07-23
- Status: Under Review
- Reviewers: repository operator and maintainers
- Affected projects or audiences: operators and maintainers of command-line
  tooling used with FieldManual
- Related work: [FieldManual bootstrap](../../../bootstrap.py) and future
  verifier submodules
- Provenance: adapted from an untracked sister-repository proposal reviewed
  on 2026-07-23

## Problem Statement

Operator-facing tools become difficult to invoke safely when help behavior,
dependencies, audit claims, network effects, mutation boundaries, and required
human follow-up are unclear. Ambiguous success messages can also imply that a
tool completed work that remains the operator's responsibility.

## Goals

- Require usable help without optional dependencies.
- Reserve audit or status-only terminology for genuinely non-mutating work.
- Disclose filesystem, network, repository, user-home, and live-session
  effects.
- Use actor-clear outcome language.
- Offer machine-readable output when recurring automation materially benefits.

## Non-Goals

- Requiring one packaging or command-line framework.
- Claiming that network fetches or local-ref updates are read-only.
- Adding more scripts to FieldManual.

## Use Cases

1. An operator can request help even when optional integrations are absent.
2. A dry run reports the exact mutation plan and performs no project writes.
3. A network refresh is not mislabeled as a read-only audit.
4. Required privileged follow-up is labeled as an operator action rather than
   reported as completed tool work.

## Constraints And Assumptions

### Verified Constraints

- Output labels are an interface and can create compatibility obligations.
- Filesystem audit, network refresh, repair, and apply are distinct mutation
  classes.

### Assumptions

- Some tools legitimately have no useful machine-readable consumer.
- A shared vocabulary can improve operator understanding without requiring
  identical command-line frameworks.

## Current Context

FieldManual has one operator-facing program, `bootstrap.py`. It already
supports dry-run and bounded project-root writes, but there is no adopted
framework-wide output vocabulary for future verifier submodules.

## Proposed Approach

Define an operator-tool standard with these defaults:

- one documented canonical invocation and a clear source fallback;
- argument parsing and help before optional third-party imports;
- a pre-action summary for meaningful mutations;
- separate names for local audit, network refresh, repair, and apply;
- output classes such as `CREATED`, `PRESERVED`, `UPDATED`, `DRY RUN`,
  `NOTE`, `WARN`, `FAIL`, and `ACTION REQUIRED`;
- explicit actor and timing for follow-up work; and
- stable nonzero exit behavior for incomplete or failed operations.

Labels should appear at state transitions, not on every line.

FieldManual's bootstrap is the first candidate for evaluating this contract.
Independent safety defects remain bugs to fix through normal authorization;
this proposal does not authorize implementation.

## Risks And Mitigations

- Too many labels could make output noisy. Apply them only to meaningful
  outcomes.
- A nominal audit mode might still mutate caches or refs. Document and test
  every side effect.
- Machine-readable output can become another compatibility surface. Add it
  only with a versioned schema and real consumer.

## Validation

Review help and no-argument behavior, dry-run truthfulness, missing-dependency
failure, audit side effects, partial failure, and required human actions.

## Alternatives Considered

1. Let each tool invent its own terminology.
   Rejected because audit and actor ambiguity recur across tools.
2. Require machine-readable output universally.
   Rejected because it adds an interface without a demonstrated consumer.

## Open Questions

- Which labels are normative and which are examples? Owner: operator.
- Should exit status distinguish preserved differences from hard failure?
  Owner: tool maintainers.

## Milestones

1. **Review the vocabulary against the FieldManual bootstrap.** Owner:
   bootstrap maintainers. Dependencies: the current bootstrap output contract
   and the open-question decisions. Entry: the candidate labels and mutation
   classes are enumerated. Exit: a review maps every current transition and
   identifies any incompatible label.
2. **Approve a concise core standard.** Owner: repository operator.
   Dependencies: the bootstrap review and resolved normative vocabulary.
   Entry: compatibility and actor-clarity impacts are documented. Exit: an
   approved standard defines required behavior and optional examples.
3. **Validate an external adoption.** Owner: the adopting verifier maintainer.
   Dependencies: the approved standard and, if needed, a versioned output
   schema. Entry: a separately versioned verifier elects to adopt the
   contract. Exit: recorded evidence covers help, dry-run, failure, side
   effects, and required human actions.

## Adoption And Rollout

If approved, use the following rollout:

- **Migration:** Apply the contract to new or behaviorally changed tools;
  existing tools may migrate incrementally.
- **Compatibility:** Treat established labels and machine-readable schemas as
  interfaces, and version incompatible changes.
- **Communication:** Document mutation classes, exit behavior, and
  operator-required follow-up in each adopting tool's user guidance.
- **Rollback:** Revert an adopter to its prior documented interface when a
  migration fails, while preserving truthful mutation and actor reporting.
- **Retirement:** Retire ambiguous legacy labels only after their consumers
  migrate. FieldManual itself retains only its bootstrap.

## Decision Log

- 2026-07-23 — Adapted the reusable invocation and output contract; removed
  package-runtime and specific tool-registry assumptions.
