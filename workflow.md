# Field Manual Workflow

## Purpose

This workflow keeps repository changes traceable without importing the full
TheKnowledge operating system.

See [Field Manual Development Workflow] for the fuller stage-by-stage doctrine.

## Core Cycle

1. Capture candidate work in `project-management/backlog.md`.
1. Use proposals for meaningful changes to schema, process, naming, storage,
   validation, or viewer assumptions.
1. Move active work into `project-management/tasks-in-progress.md`.
1. Record durable decisions in `project-management/decision-log.md`.
1. Track unresolved fact questions, interview follow-ups, and modeling
   uncertainties in `project-management/open-questions.md`.
1. Track defects and regressions in `project-management/bugs.md`.
1. Track bounded human-only actions in `project-management/ai-human-requests.md`
   when they should not live in the main backlog.
1. When work lands, record it in `project-management/completed-tasks.md`.
1. If work pauses intentionally, move it to `project-management/deferred.md`.

## When To Write A Proposal

Write a proposal when a change affects any of the following:

- repository structure
- canonical schema
- time and uncertainty modeling
- wiki-link semantics
- identity and alias rules
- validator behavior
- timeline viewer assumptions
- process-document structure

Do not require a proposal for ordinary fact capture, routine page creation, or
small clerical fixes unless those changes expose a broader structural issue.

## Working Principles

- Favor honesty over false precision.
- Preserve raw recollection separately from normalized interpretation when
  practical.
- Avoid creating multiple sources of truth without a clear reason.
- Keep process lightweight and conversational.
- Use Markdown by default for project-management and working documents.
- Add automation only after the manual workflow proves stable.

## Validation Expectations

At first, validation is mostly manual and conversational. As the repository
grows, add narrow consistency checks for link integrity, identity collisions,
time-shape validity, missing required metadata, and viewer manifest integrity.
