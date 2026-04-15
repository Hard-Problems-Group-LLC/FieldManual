# Field Manual Proposal Format

## Purpose

Use proposals for changes that affect knowledgebase structure, workflow,
schema, ingestion conventions, identity rules, validation policy, or major
viewer behavior.

Keep prose concise. Preserve review history append-only by updating status and
decision notes rather than rewriting prior conclusions away.

## Header

Every proposal should start with:

- `# Proposal Title`
- metadata bullets for author, date, status, reviewers, and related work

Store the file in the matching status directory under
`project-management/proposals/`.

## Recommended Markdown Structure

Then use these sections:

## Problem Statement

Describe the problem in repository terms. Focus on ambiguity, inconsistency,
missing structure, workflow friction, or user-facing limitations.

## Goals

List the outcomes the proposal must achieve.

## Non-Goals

List what the proposal does not attempt to solve.

## Use Cases

Summarize representative scenarios the proposal must satisfy.

## Constraints And Assumptions

Call out host limitations, workflow constraints, compatibility assumptions,
performance expectations, or repository-specific pressures that shape the
design.

## Current Context

Summarize the relevant current files, conventions, and pain points.

## Proposed Approach

Describe the intended structure, conventions, or behavior. Be explicit about
source-of-truth choices, file locations, naming rules, viewer expectations,
and transition plans.

## Alternatives Considered

List credible alternatives and why they were not chosen.

## Risks And Mitigations

Describe failure modes such as ambiguity, overfitting, duplicate authority,
future migration pain, or validation burden.

## Validation

Describe how the proposal will be checked. This may include manual review,
small scripts, consistency checks, or sample ingestion exercises.

## Open Questions

Record unresolved questions and who must answer them.

## Milestones

When useful, break the work into phases or adoption steps.

## Adoption And Rollout

Explain how the proposal should land, including what can happen immediately,
what should wait, and any temporary compatibility or migration rules.

## Decision Log

Append dated notes as the proposal is reviewed and decided.
