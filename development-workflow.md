# Field Manual Development Workflow

## Purpose

Describe how work moves through this repository without importing the full
TheKnowledge operating system.

This document keeps the useful project-management doctrine from TheKnowledge
while deliberately leaving out Git-flow doctrine, commit helpers, hooks, and
heavy code-validation expectations that do not fit this repository yet.

## Core Stages

Follow this sequence unless the user explicitly directs otherwise:

1. propose
1. backlog
1. execute
1. clear or defer

Keep every substantive change traceable either to:

- a proposal,
- a backlog or in-progress entry, or
- direct user direction recorded in project-management state.

## Proposals

Use proposals to discuss meaningful structural changes before implementation.

Store each proposal in the matching status directory under
`project-management/proposals/`:

- `under-review/`
- `approved/`
- `rejected/`
- `deferred/`

Keep proposal status metadata aligned with the directory name. Preserve review
history append-only by updating status and decision notes instead of rewriting
earlier rationale out of existence.

Under-review proposals are planning documents by default. Do not treat them as
approved work unless the user explicitly authorizes implementation.

## Backlogging

Capture approved work and direct operator requests in
`project-management/backlog.md`.

For each entry:

- include requestor or owner when known
- include an ISO 8601 timestamp
- keep the summary actionable
- note blockers or dependencies inline

Keep the next item near the top. Preserve original request language where
possible so later status changes remain easy to trace.

## Execution

Move work into `project-management/tasks-in-progress.md` when active work
starts.

When promoting an item:

- carry forward the original request text
- add a fresh start timestamp
- note owners, blockers, and links to the relevant proposal or specification

During execution, keep progress notes concise and dated. Use
`project-management/decision-log.md` for durable decisions rather than hiding
them in transient task text.

## Human Actions

Use `project-management/ai-human-requests.md` for bounded actions that require
human involvement, such as:

- running a privileged command
- making a manual browser check
- installing host dependencies
- confirming an environmental assumption

Use this queue for non-blocking or externally constrained human steps, not as
a substitute for normal backlog items.

## Clearing

When work is complete, move the entry into
`project-management/completed-tasks.md` and summarize:

- what changed
- when it landed
- who completed it when useful
- what follow-up remains, if any

If the work reveals more to do, open a fresh backlog entry instead of
rewriting the completed record.

## Deferrals

When the user intentionally pauses work, move it to
`project-management/deferred.md`.

Preserve the original request substance. Add:

- a short reason for the pause
- a timestamp for when the deferral happened

This repository does not currently need the full quoted-block deferral doctrine
from TheKnowledge. The key requirement is that the original task remains easy
to restore without guesswork.

## Status Hygiene

- Keep backlog entries concise and actionable.
- Promote items only when active work truly begins.
- Return stalled work to the backlog or deferred list instead of leaving it in
  progress indefinitely.
- Record durable decisions in the decision log.
- Record unresolved user-facing questions in open questions.
- Avoid rewriting history when a short appended note will do.

## Validation Expectations

This repository is not code-heavy enough to require TheKnowledge's full
testing and tool-validation doctrine yet.

For now:

- prefer manual and conversational validation first
- add narrow repeatable checks only when the manual workflow proves stable
- focus automation on viewer behavior, manifest integrity, link integrity,
  schema consistency, and derived-index correctness

When the repository gains more durable executable tooling, stronger validation
doctrine can be imported later.
