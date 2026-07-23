# Version-Control Safety

## Purpose

Keep repository history intentional, reviewable, and attributable without
depending on a particular helper program, branch name, or hosting provider.

## Before Staging

- Inspect repository status and the unstaged diff.
- Identify the exact files intended for the change.
- Preserve unrelated user or concurrent work.
- Review generated files, dependency lock changes, submodule pointers, and
  file-mode changes deliberately.
- Run the project-owned validation appropriate to the change.

Before staging on another person's behalf, offer a meaningful review
opportunity or obtain an explicit instruction to proceed without one.

## Identity

Require an explicitly configured author and committer identity before
creating a commit. Never infer an email address from history, hostnames,
remote URLs, network identifiers, or neighboring repositories.

When author and committer differ, make the distinction deliberate and
traceable.

## Commits

- Keep each commit coherent and reviewable.
- Separate unrelated refactors, formatting churn, generated updates, and
  behavior changes when practical.
- Use a concise subject and enough body context to explain why the change
  exists.
- Inspect the staged diff before committing.
- Do not claim validation that was not performed.

Projects may choose their own default branch, branch prefixes, merge strategy,
and pull-request policy. Record those choices in project-owned guidance rather
than assuming one universal convention.

## History-Changing Operations

Treat force pushes, history rewrites, destructive resets, and broad removals
as exceptional. Confirm the exact target, collaborators, backup or recovery
path, and required authority before proceeding.

If a credential entered history, revoke or rotate it before treating history
cleanup as remediation.

## Remote and Dependency Changes

Review incoming changes before adopting a new dependency, submodule revision,
or shared framework version. Record the reviewed revision and validate the
consuming project's resulting state.

Executable enforcement belongs to consuming projects or separately versioned
verifier submodules.
