# Shared-Checkout Subagents

Load this knack when an orchestrating agent, or a person, runs background
agents that edit, build, test, or commit in one working tree, or when you are
deciding whether they should share one. Load the companions for the exact
commands and brief templates:

- [Git patterns](git.knack.md): committing by
  path, the commands that sweep up other writers' work, integrating and
  pushing, and worktrees.
- [Briefs and records](briefs.knack.md): what
  each agent's brief must say, contract-first parallel work, commit cadence,
  final reports, and reorientation after an interruption.

Source review: 2026-10-13. Command behavior was checked against Git 2.5x and
the current Git reference manual; recheck both, and your agent tool's own
documentation, before relying on specific behavior.

## Mental Model

A working tree shared by several agents is shared mutable state with almost
no locking. Each agent sees files, not intentions. Everything in the checkout
is common to all of them:

- the working files and any edits not yet committed;
- the index (the staging area), which every `git add` changes;
- `HEAD` and the checked-out branch;
- build output, intermediate and cache folders;
- the remote-tracking refs that `git fetch` updates.

Git's convenience commands assume a single writer. `git commit -a`,
`git add -A`, `git stash`, `git restore .` and `git pull --rebase` treat every
uncommitted change in the tree as yours. With several writers they commit,
hide or discard someone else's work.

Collisions fall into four classes:

1. **Edit collisions.** Two writers change one file, and the later write wins
   or the two interleave.
2. **Commit sweeps.** One writer's commit includes another writer's
   unfinished edits. This happens in practice: an agent ran a broad commit and
   recorded a colleague's half-finished file under its own message.
3. **Build collisions.** Concurrent builds of one project share its output
   folders. Files are locked, assemblies are half written, and one agent's
   tests run against another agent's binary.
4. **History collisions.** Pushes race, a rebase meets uncommitted edits, or
   two agents commit the same shared record.

Durability is the fifth concern. Uncommitted and unpushed work exists on one
disk inside one session. When a session dies (a forced operating-system
restart, a crash, an exhausted quota), its running agents die with it, and
their final reports never arrive. Only pushed work is safe.

## Operating Rules

1. **Partition by file.** Give each concurrent agent a disjoint set of files
   and name them in its brief. One agent owns each contested file; any other
   agent that needs a change there proposes it in its report or waits.
2. **Commit by path.** `git commit -m "..." -- <paths>` records only those
   paths and leaves everything else, staged or not, alone. Never use
   `commit -a`, `add -A`, `add .` or `stash` in a shared tree. A path commit
   takes the whole file, so check `git diff -- <paths>` first.
3. **Give shared records one writer.** TODO lists, decision logs, changelogs
   and indexes belong to the orchestrator. Agents propose entries in their
   final reports. Commit a shared record only when no other writer is active.
4. **Integrate before pushing.** Use `git pull --rebase`, then push. In a
   shared tree the rebase refuses while any tracked file is dirty, which
   usually means another agent is mid-edit. Push at a quiet point, let the
   orchestrator integrate, or push from a worktree. Do not reach for
   `--autostash` while others are writing: it lifts their edits out of the
   tree for the length of the rebase.
5. **Give builds their own tree.** An agent that must build or run tests
   while others build gets a worktree (a second working tree of the same
   repository) or waits its turn.
6. **Agree the contract first.** When two agents' work meets at an interface,
   commit the shared types and signatures as compiling stubs. Then one agent
   fills the library while another writes the host side against the stubs.
   Merge and run the integrated checks last.
7. **Commit and push after each sub-step.** A sub-step is the smallest unit
   that builds and passes its own checks. Pushed sub-steps survive a lost
   session; a finished but unpushed feature does not.
8. **Reorient after any interruption.** Read the record, then check the
   branch, status, and divergence from the remote. Rebuild and rerun the
   tests before continuing. Do not trust a summary of what you were doing.
9. **Relay the final reports.** A subagent's final report is the record of
   what it changed, what it verified, and what it left unverified. The
   orchestrator checks the key claims and passes on what matters.

## Shared Tree or Worktree?

| Situation | Arrangement |
| --- | --- |
| Edits only, disjoint files, no builds | Shared tree, commit by path |
| An agent must build or run tests while others build | Worktree for that agent |
| Long, independent line of work | Branch plus worktree, merged when complete |
| Two agents need the same file | Serialize: one owner, the other waits |
| Shared records need updating | Orchestrator, at a quiet point |

Worktrees isolate files, the index, `HEAD` and build output, but they share
the object store and refs. Two worktrees cannot check out the same branch.

## Sharp Edges

- **A path commit takes the whole file.** If two agents edited one file, the
  first to commit records both sets of edits. Partitioning, not a clever
  command, prevents this.
- **New files need an explicit add.** `git commit -- new-file` fails until
  `git add -- new-file` makes the path known to Git. Add by path, never by
  directory.
- **Git commands collide.** Two agents running Git at once can fail with
  `Unable to create '.git/index.lock': File exists`. Retry after a pause.
  Delete the lock only after confirming no Git process is running.
- **Cleanup commands destroy others' work.** `git restore .`,
  `git checkout -- .`, `git reset --hard` and `git clean -fd` act on the whole
  tree. Restore only your own paths.
- **Branch switches move everyone.** Switching branches in a shared tree
  rewrites files under every agent at once.
- **Tree-wide tools touch others' files.** Formatters, code generators and
  "fix all" commands run over the whole tree. Scope them to owned paths.
- **Builds dirty the tree.** Regenerated lock files, project files and
  generated sources appear in `git status` as someone's change. Agree who
  owns them.
- **Worktrees start incomplete.** Ignored files such as local configuration,
  restored packages and build output are absent from a new worktree. Restore
  or rebuild them there.
- **Silence is not success.** An agent that died with its session produced no
  report. Treat missing reports as unverified work.

The [staged verification](../staged-verification.knack.md) knack gives the
simpler rule for scripted builder fleets: builders own disjoint files and
none commits while others edit. That rule is the safe default when agents
cannot be trusted to commit by path. This knack refines it so that each
agent can commit and push its own sub-steps.

## Review Checklist

- Each concurrent agent's brief names the files it owns and the files it may
  only read.
- No brief permits `commit -a`, `add -A`, `add .`, `stash`, whole-tree
  restores, or branch switches.
- Every commit was made by path and inspected with `git show --stat`.
- Shared records were written by one writer at a quiet point.
- Building agents had their own worktree, or builds were serialized.
- Interfaces between parallel agents were committed as stubs first.
- Each completed sub-step was committed and pushed.
- After any interruption, the branch, status, remote divergence, build and
  tests were checked before work resumed.
- Every agent's final report was received, checked against the history, and
  relayed; missing reports were treated as unverified work.

## Further Information

- FieldManual, [Staged Verification for Multi-Agent
  Work](../staged-verification.knack.md): parallel builders, gates and
  escalation.
- FieldManual, [Version-Control
  Safety](../../../../standards-and-practices/core/version-control-safety.md)
  and [Session and Project
  Boundaries](../../../../standards-and-practices/core/session-and-project-boundaries.md):
  preserving concurrent work and reorienting after interruption.
- Git, [git-commit](https://git-scm.com/docs/git-commit): the `--only`
  behavior used when paths are given.
- Git, [git-worktree](https://git-scm.com/docs/git-worktree): linked
  worktrees and their per-worktree files.
- Git, [git-pull](https://git-scm.com/docs/git-pull): `--rebase` and
  `--autostash`.
- Anthropic, [How we built our multi-agent research
  system](https://www.anthropic.com/engineering/multi-agent-research-system):
  task descriptions with objectives, output formats and boundaries; outputs
  that persist outside the lead agent; resuming after failures.
