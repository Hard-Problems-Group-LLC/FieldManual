# Project-Owned Overlays And Record Paths

- ID: FM-PROP-2026-005
- Author: FieldManual maintainers
- Date: 2026-07-23
- Status: Under Review
- Reviewers: repository operator and maintainers
- Affected projects or audiences: FieldManual and consuming projects with
  deliberate layout variations
- Related work: [tracked configuration](../../../FieldManual-config.toml) and
  [configuration contract](../../../docs/configuration.md)
- Provenance: adapted from an untracked sister-repository proposal reviewed
  on 2026-07-23

## Problem Statement

Consuming projects need deterministic ways to specialize reusable defaults
without editing a read-only submodule, carrying compatibility symlinks, or
letting a framework refresh erase deliberate project policy.

## Goals

- Define narrow, typed, source-aware configuration overlays.
- Preserve project ownership of record paths and policy.
- Distinguish tracked configuration from checkout-local state.
- Make effective values and precedence explainable.
- Reject accidental whole-file drift as a substitute for configuration.

## Non-Goals

- Building a general-purpose configuration framework.
- Preserving arbitrary edits to framework-owned content.
- Putting secrets into tracked configuration.

## Use Cases

1. A project uses a nested FieldManual submodule path without editing managed
   instructions.
2. A checkout temporarily selects a different local FieldManual path while
   the tracked project configuration stays portable.
3. A Markdown-first project proposes a different record layout and receives a
   source-aware conflict instead of a silently overwritten managed file.

## Constraints And Assumptions

### Verified Constraints

- Tracked configuration is visible project policy and cannot contain secrets.
- Local configuration is ignored and must not become durable policy.
- Merge behavior must be deterministic and diagnosable.

### Assumptions

- Every overlay needs a named consumer and versioned schema.
- At least one consuming project will demonstrate a need before FieldManual
  adds an overlay beyond the implemented root configuration.

## Current Context

The two-root configuration is the first narrow overlay:

1. tracked `FieldManual-config.toml` declares the distributed roots;
2. ignored `.local/FieldManual-localconfig.toml` loads afterward; and
3. the installer validates the effective values against the project and the
   running framework checkout.

This implemented root contract does not decide whether FieldManual should
support configurable project-management filenames or other policy maps.

## Proposed Approach

For each proposed overlay:

- identify the document or program that consumes it;
- define a versioned schema and known keys;
- state whether values replace, append, or merge;
- report each effective value's source;
- reject unknown keys and conflicting types;
- keep tracked, reviewable project policy outside `.local/`; and
- reserve `.local/` for checkout-specific paths, operator notes, and mutable
  state.

Record-path configuration should be considered only if real projects need
layouts that cannot be expressed by the Markdown-first defaults. Managed
AGENTS content should refer to configured paths rather than silently
reinstalling stale hard-coded names.

## Alternatives Considered

1. Copy and modify every framework file in each project.
   Rejected because copies drift and hide upstream corrections.
2. Preserve every local difference automatically.
   Rejected because accidental drift would become permanent policy.
3. Put all overrides in one untyped mapping.
   Rejected because ownership and merge behavior would be ambiguous.

## Risks And Mitigations

- Many overlays could create a second framework. Require one named consumer
  and demonstrated need for every schema.
- Automatic merging could hide semantic conflicts. Fail with source-aware
  diagnostics.
- Local overrides could become an unreviewed policy channel. Keep durable
  policy tracked and restrict local use to checkout facts.

## Validation

Test default, tracked, and local precedence; invalid keys and types; source
diagnostics; refresh behavior; and absence of secrets from tracked examples.

## Open Questions

- Which record paths have demonstrated configuration needs? Owner: consuming
  project maintainers. Decision point: before schema design.
- Should project-owned policy overlays use the root TOML or separate,
  consumer-specific files? Owner: repository operator. Decision point: schema
  approval.

## Milestones

1. **Gather demonstrated use cases.** Owner: consuming-project maintainers.
   Dependencies: concrete layout or policy constraints from at least one
   adopter. Entry: a default FieldManual path cannot meet a documented need.
   Exit: each use case identifies its consumer, ownership, and conflict.
2. **Specify one narrow schema.** Owner: FieldManual maintainers.
   Dependencies: the first milestone and the root- versus separate-file
   decision. Entry: demonstrated cases bound the schema. Exit: keys, versions,
   precedence, diagnostics, and recovery behavior are decision-ready.
3. **Pilot refresh behavior.** Owner: the pilot project's maintainers.
   Dependencies: an approved schema and representative default, tracked, and
   local configurations. Entry: the pilot opts into the overlay. Exit: refresh
   succeeds without compatibility symlinks, silent merges, or policy loss.

## Adoption And Rollout

If an additional overlay is approved, use the following rollout:

- **Migration:** Keep the implemented two-root configuration unchanged.
  Additional overlays are opt-in and require an explicit project migration.
- **Compatibility:** Version each schema and preserve default record paths for
  projects that do not opt in.
- **Communication:** Publish keys, precedence, ownership, diagnostics, and
  migration steps with each overlay.
- **Rollback:** Remove the optional overlay and return to default paths after
  preserving project-owned records and recording any path reversal.
- **Retirement:** Retire compatibility paths or aliases only after adopters
  migrate and stale references are removed; otherwise no current behavior is
  retired.

## Decision Log

- 2026-07-23 — Imported the broader overlay question. The user-directed
  two-root TOML contract is being implemented independently and does not
  pre-approve other overlay types.
