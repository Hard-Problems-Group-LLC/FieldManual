# Field Manual Shopping List

Last updated: 2026-04-04

> Historical note: this was the initial import plan for the first,
> knowledge-management-focused FieldManual. It is retained as migration
> provenance and is not the current framework roadmap.

## Purpose

- Record candidate pieces from an upstream `TheKnowledge` checkout that are
  worth importing or adapting into this repository.
- Separate lightweight process assets from heavyweight development-platform
  machinery.

## Copy Almost As-Is

- `templates/project-management/backlog.md`
- `templates/project-management/tasks-in-progress.md`
- `templates/project-management/completed-tasks.md`
- `templates/project-management/deferred.md`
- `templates/project-management/bugs.md`
- `templates/project-management/proposals/`
- `templates/project-management/state/README.md`

## Adapt Before Importing

- `standards-and-practices/docs/format-for-proposals.txt`
- `standards-and-practices/docs/development-workflow.txt`
- `templates/project-management/ai-human-requests.txt`
- `templates/project-management/proposals/README.md`
- `standards-and-practices/docs/human-orders-for-AI-agents.txt`

## Probably Add Locally, Not Imported From TheKnowledge

- `FieldManual/proposal-format.md`
- `FieldManual/workflow.md`
- `project-management/open-questions.md`
- `project-management/decision-log.md`
- `project-management/bugs.md`
- `docs/specifications/time-and-uncertainty-model.md`
- `docs/specifications/wiki-link-conventions.md`
- `docs/specifications/knowledgebase-schema.md`
- `docs/specifications/repository-document-conventions.md`

## Defer Until There Is Clear Need

- `standards-and-practices/docs/sop/`
- `scripts/run_tool_with_timeout.py`
- `scripts/run_quality_gate_cached.py`
- `tool_execution_constraints.json`
- `tool_validation_profiles.json`
- Python environment bootstrap and install scripts

## Likely Future Validator Scope For This Repo

- broken wiki links
- missing referenced entities
- canonical-name collisions
- alias collisions
- malformed dates or date ranges
- impossible temporal constraints
- orphan records or pages
- missing required metadata on canonical records

## Suggested Import Order

1. Create `project-management/` with the lightweight Markdown files and
   proposal directories.
1. Write a local `FieldManual/proposal-format.md`.
1. Write a local `FieldManual/workflow.md`.
1. Add repo-specific specification docs for schema, wiki links, document
   conventions, and temporal uncertainty.
1. Only then consider a tiny validator layer for knowledgebase consistency.
