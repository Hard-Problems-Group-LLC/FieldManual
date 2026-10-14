# Integrating Unverified Agent Work: Integration

Load this companion to the
[overview](overview.knack.md) when you
decide whether an agent's branch may merge, or when an agent's line of work
and a locally verified line must become one history.

Source review: 2026-10-13. Commands were checked against the Git reference
manual.

## The Merge Gate

Make one rule non-negotiable for agent work: **it builds and runs more than
zero tests on the real toolchain**. Then add what the project needs:

1. a clean build of the branch, in its own worktree, from a clean checkout;
2. the test run reports a count above zero, and above the previous count
   when tests were added;
3. every new test has sabotage evidence;
4. the in-host smoke run passes, where the project has one; and
5. a person or a review agent has read the combined diff.

"More than zero" is not a joke. A test project missing a required test
package or adapter can fail in either direction. In .NET, one project
without `Microsoft.NET.Test.Sdk` saw `dotnet test` report no tests and
succeed, while a check on the .NET 9 SDK aborted with exit code 1 instead;
see the
[.NET project-files companion](../../../dotnet/shared-library/projects.knack.md).
Do not rely on either outcome. Read the count from the runner's output,
not its exit code, and fail the gate when it is below a known minimum.

Where the platform hosting the repository supports it, enforce the gate
with required status checks on the protected branch, so that a pull request
cannot merge seconds after it opens.

## Batching

One pull request per small task, merged at once, produces churn with no
review: in one project, six of seven such requests touched only
documentation or process. Ask the agent to batch related tasks into one
reviewable change, and review the combined diff of any burst of requests
together.

## Building Someone Else's Branch

```sh
git fetch origin
git worktree add --detach ../example-repo-agent origin/agent/task-name
# build and run the tests in ../example-repo-agent
git worktree remove ../example-repo-agent
```

A branch described as merged may never have compiled; its own tests may
assert the bugs it was meant to fix. Building it in a separate worktree
keeps your working tree, and anyone else's, untouched (see
[Shared-Checkout
Subagents](../shared-checkout/overview.knack.md)).

## Reconciling Two Lines of Work

The hard case: the agent's line and a locally verified line diverged, or
began as separate repositories, and both contain something worth keeping.
Typically the verified line has working behavior and the agent's line has
useful scaffolding.

**Decide first, per artifact**, using the review table: keep, rewrite or
drop. Write the decisions down; they become the merge's commit message and
a decision-log entry.

**Preserve provenance.** Merge rather than copy, so that both histories
remain visible:

```sh
git remote add agentline ../agent-repo          # or the agent's remote
git fetch agentline
git merge --no-ff --no-commit --allow-unrelated-histories agentline/trunk
```

- `--allow-unrelated-histories` is needed only when the lines never shared
  an ancestor; Git refuses such merges by default.
- `--no-commit` stops before the merge commit so the result can be
  inspected and adjusted; `--no-ff` ensures there is a merge to stop in.
- For each conflict, take the stage you decided on: `git show :2:<path>`
  is the current (verified) branch's version and `git show :3:<path>` is the
  incoming one. Join both when the decision says so.
- Resolve conflicts in append-only records (decision logs, changelogs) by
  keeping both sides in date order, after correcting fabricated dates.
- Build and run every test before committing the merge. Then remove the
  temporary remote: `git remote remove agentline`.

**Let verified behavior win.** Where both lines implement the same
behavior, keep the verified implementation and port only what the review
found sound from the other. Keep the agent's tests only after their values
have been validated and each has been seen to fail.

**Adopt structure deliberately.** Instruction files, record sets, a
host-free core library and a test project can all be adopted from the
agent's line. Adopting a project file can expose its build settings first:
in one case a library enabled a language feature that the default language
level of its target framework did not support, and compiled only after the
language level was raised and a small compatibility shim was added.

**Record the outcome**: what was kept, rewritten and dropped, and why, in
the decision log, citing the merge commit.

## After the Merge

- Rerun the full gate, including the in-host smoke run, from a clean
  checkout.
- Update the agent's instructions with every signature the review found
  (see the [instructions
  companion](instructions.knack.md)).
- If the agent will keep contributing, point its environment at the real
  toolchain where licensing allows, or accept that its output will always
  need this review.

## Sharp Edges

- **Fast-forward surprises.** Without `--no-ff`, a merge that can
  fast-forward does so, and `--no-commit` cannot stop it.
- **Lost context in squash merges.** Squashing an agent's branch removes
  the record of which commit introduced which claim. Prefer a merge, or
  keep the branch reachable.
- **Conflicts resolved by reflex.** "Take theirs" across the board imports
  every unverified value. Resolve file by file from the review table.
- **Stale tracking refs.** A failed fetch leaves old remote-tracking refs in
  place, and status may report "behind" against a remote state that no
  longer exists. Confirm the fetch succeeded before reconciling.

## Further Information

- Git, [git-merge](https://git-scm.com/docs/git-merge):
  `--allow-unrelated-histories`, `--no-commit` and `--no-ff`.
- Git, [gitrevisions](https://git-scm.com/docs/gitrevisions): the
  `:<n>:<path>` stage syntax during a merge.
- Git, [git-worktree](https://git-scm.com/docs/git-worktree).
- GitHub, [About protected
  branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches):
  required status checks before merging.
- FieldManual, [Version-Control
  Safety](../../../../standards-and-practices/core/version-control-safety.md).
