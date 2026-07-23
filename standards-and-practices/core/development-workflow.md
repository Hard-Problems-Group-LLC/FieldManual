# Development Workflow

## Purpose

Keep work deliberate, traceable, and easy to resume without turning
project-management records into a second implementation system.

The normal sequence is:

1. propose when a decision needs review;
2. backlog approved or directly requested work;
3. execute one bounded item;
4. clear completed work or defer paused work.

Small, explicit operator requests may enter the backlog without a separate
proposal. Record enough context to make the authorization and acceptance
criteria clear.

## One Primary State

A work item has exactly one primary lifecycle location at a time:

- backlog;
- in progress;
- completed; or
- deferred.

Move the item between primary state records; do not leave active copies in
both the backlog and in-progress records. Preserve a stable identifier, the
substance of the original request, and dated transition notes so the history
remains traceable.

Proposals, specifications, decisions, and bug reports are linked evidence, not
duplicate primary task states.

## Propose

Use a proposal for changes that materially affect behavior, public contracts,
architecture, security boundaries, shared standards, repository structure, or
multiple downstream projects.

An under-review proposal is not authorization to implement it. Record an
explicit approval, rejection, or deferral before turning proposal scope into
backlog work.

Write or update a specification before implementation when an approved change
needs a durable behavioral contract.

## Backlog

Keep the backlog ordered by current priority. Each item should include:

- a stable identifier;
- an actionable summary;
- the requestor or owner when known;
- an ISO 8601 creation timestamp;
- acceptance criteria or a link to them;
- dependencies and blockers; and
- links to related proposals, specifications, decisions, or bugs.

Add dated notes instead of rewriting earlier context when new information
changes priority or scope.

## Execute

When work starts, move the item from backlog to in progress and add a start
timestamp, current owner, and known blockers.

During execution:

- keep the change bounded to the authorized scope;
- preserve unrelated work;
- update durable decisions when assumptions change;
- test in proportion to risk;
- keep documentation aligned with behavior; and
- record any validation that could not be performed and why.

If work stops without being intentionally deferred, move it back to the
backlog with a dated status note.

## Clear

When acceptance criteria are met, move the item to completed and record:

- the outcome;
- the completion timestamp;
- validation performed;
- important decisions or risk acceptances; and
- any follow-up records.

Open a new backlog item for additional work rather than expanding a completed
record after the fact.

## Defer

When work is intentionally paused, move it to deferred. Preserve its stable
identifier and original substance, then add:

- the deferral timestamp;
- the reason;
- the authority that chose to defer it; and
- the condition or date for reconsideration, when known.

Reactivation moves the same item back to the backlog or in-progress record
with a new transition note.

## Validation Ownership

This workflow defines required evidence, not a universal command suite.
Consuming projects own executable checks for their languages and platforms.
Future verifier submodules may provide reusable implementations without
making them part of FieldManual's core policy.
