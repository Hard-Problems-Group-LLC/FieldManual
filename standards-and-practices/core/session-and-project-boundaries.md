# Session and Project Boundaries

## Purpose

Prevent stale sessions, adjacent repositories, and ambiguous external targets
from causing changes in the wrong place.

## Session Reorientation

After a resume, handoff, compaction, or interruption, verify:

- the active workspace and repository;
- the current request and authorized scope;
- relevant branch or worktree state;
- applicable project and local instructions; and
- signs of another active writer when they are discoverable.

Do not assume the newest terminal, remote session, or agent transcript is the
correct continuation. If multiple candidates exist, compare their workspace,
origin, age, and current activity before acting.

## Project Boundary

Read-only inspection may cross a project boundary when needed to identify an
owner, dependency, or source of truth.

Before mutating outside the active project root, obtain explicit confirmation
in the current session. State:

- the active project or path;
- the target project, system, or path;
- the intended class of change; and
- any detected concurrent writer or material risk.

Cross-project mutation includes file changes, generated output, record
updates, service operations, queued jobs, commits, pushes, deployments, and
changes to another project's external resources.

Do not infer authority from a nearby path, URL, prior session, command
approval, or discussion of the other project. Stop when ownership or intent
remains ambiguous.

## Handoffs

Preserve the active project, exact scope, completed work, remaining work, and
known hazards in handoffs. Do not silently turn an unresolved assumption into
a fact during summarization.
