# Proposal and Bug Lifecycle

## Purpose

Give proposals and defects stable, auditable states without duplicating their
authoritative content across several records.

## Proposal States

Use these standard proposal states:

- `under-review`: awaiting a decision;
- `approved`: accepted for specification or execution;
- `rejected`: declined with rationale; and
- `deferred`: intentionally paused with reconsideration conditions when
  known.

Store proposal files in a directory matching their status and keep the
metadata aligned. Move the authoritative record when status changes rather
than copying it into multiple status directories.

Projects may define additional states through their own approved policy. Do
not infer a new state from an unfamiliar directory name.

## Bug States

Use these standard detailed bug states:

- `open`: confirmed or accepted for investigation;
- `in-progress`: actively being diagnosed or corrected; and
- `closed`: resolved, intentionally declined, or otherwise disposed with
  rationale.

Each bug should have a stable identifier and, when known:

- observed behavior and impact;
- environment and reproduction evidence;
- expected behavior;
- owner and priority;
- related changes or decisions;
- root cause;
- resolution; and
- closure timestamp and validation.

Do not mark a bug resolved merely because its symptom stopped reproducing
without understanding whether the underlying risk remains.

## Indexes and Queues

An ordered backlog or bug index may be useful for prioritization, but it must
point to authoritative records rather than becoming a divergent copy of
them. Derived indexes should be reproducible or easy to reconcile.

Keep empty lifecycle directories visible with a short README when the
repository format requires tracked placeholders.

## Transitions

Record who or what authority changed status, when it changed, and why. Link
approved proposals to specifications and work items; link closed bugs to the
change and evidence that resolved them.
