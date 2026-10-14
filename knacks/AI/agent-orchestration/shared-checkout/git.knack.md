# Shared-Checkout Subagents: Git Patterns

Load this companion to the
[shared-checkout overview](overview.knack.md) when an
agent must commit, integrate, push, or set up a worktree in a checkout that
other writers are using at the same time.

Source review: 2026-10-13. The behavior below was checked with Git 2.5x on a
scratch repository and against the Git reference manual. Run `git help
<command>` on the installed version when it differs from an example.

## Inspect Before Touching History

Before any commit, find out what is in the tree and whose it is:

```sh
git status --porcelain=v1         # every modified, staged and untracked path
git diff -- src/route/planner.cs  # your unstaged changes, path by path
git diff --cached --name-only     # paths someone has already staged
```

Compare the output with the paths your brief says you own. A modified file
you do not own is another writer's work in progress: leave it alone, and do
not report it as yours.

## Commit by Path

When paths are given, `git commit` uses its `--only` mode. The manual
describes it as taking "the updated working tree contents of the paths
specified on the command line, disregarding any contents that have been
staged for other paths." Anything another agent has staged stays staged and
stays out of your commit.

```sh
git add -- src/route/planner.cs tests/route/planner_tests.cs  # new files only
git commit -m "Route planner: reject unreachable goals" \
  -- src/route/planner.cs tests/route/planner_tests.cs
git show --stat HEAD                  # confirm exactly these paths
```

Observed behavior worth knowing:

- **Untracked paths fail.** `git commit -- new-file` stops with
  `pathspec 'new-file' did not match any file(s) known to git`. Run
  `git add -- new-file` first. Adding by explicit path touches only that
  entry in the shared index.
- **Deletions and renames.** Name both the old and the new path, or the
  deleted path, in the commit's pathspec.
- **Whole files only.** The commit records the entire working-tree content of
  each path, including any other writer's edits to the same file. Interactive
  hunk selection (`git add -p`, `git commit -p`) needs a person at the
  keyboard and is unsuitable for unattended agents. Needing hunk-level
  commits is a sign that the file is contested; stop and give it one owner.
- **Directory pathspecs sweep.** `git commit -- src/` takes every tracked
  change under `src/`, including other writers' changes. Name files.

## Commands That Sweep

| Command | What it takes | Use instead |
| --- | --- | --- |
| `git commit -a` | Every modified tracked file | `git commit -- <paths>` |
| `git commit` with no paths | Everything anyone has staged | `git commit -- <paths>` |
| `git add -A`, `git add .` | Every change, untracked files too | `git add -- <paths>` |
| `git stash` | Every uncommitted change in the tree | A worktree |
| `git restore .`, `git checkout -- .` | Discards every unstaged edit | `git restore -- <your paths>` |
| `git reset --hard` | Discards all uncommitted work | Restore your own paths |
| `git clean -fd` | Deletes every untracked file | Delete your own files by name |
| `git switch <branch>` | Rewrites files under every writer | A worktree on that branch |
| `git pull --rebase --autostash` | Lifts everyone's edits out during the rebase | A quiet point, or a worktree |

Put the forbidden commands in each agent's brief by name. Agents follow
explicit lists more reliably than a general warning.

## Integrate and Push

A push is rejected when the remote branch has moved on. Check divergence
first:

```sh
git fetch origin
git rev-list --left-right --count HEAD...@{upstream}   # prints "ahead behind"
```

If the second number is zero, push. Otherwise integrate first. The standard
`git pull --rebase` refuses whenever the tree has uncommitted changes to
tracked files, with `cannot pull with rebase: You have unstaged changes` or
`Your index contains uncommitted changes`. Untracked files do not block it.
In a shared tree those uncommitted changes are usually another agent's work
in progress, so choose one of these:

1. **Wait for a quiet point.** The orchestrator integrates and pushes when no
   agent is editing.
2. **Push from a worktree.** The agent commits on its own branch in its own
   worktree, rebases there, and pushes; the orchestrator merges.
3. **Merge instead of rebasing.** `git pull --no-rebase` tolerates dirty
   files that the incoming commits do not touch, and refuses ("Your local
   changes ... would be overwritten") when they do. It records a merge
   commit; use it only where project policy accepts merge commits.

`--autostash` works on a dirty tree by creating a temporary stash and
applying it afterwards. The manual warns that the final application "might
result in non-trivial conflicts." While it runs, every other agent's edits
are missing from the tree; an agent that writes during that window can lose
work or create conflicts. Use it only when no one else is writing.

Never force-push a branch other writers use. If a push is rejected, fetch and
integrate again; do not overwrite.

## Worktrees for Building Agents

A linked worktree is a second working directory of the same repository. The
manual says it shares "everything except per-worktree files such as `HEAD`,
`index`, etc." Commits made in one are visible in the other at once, because
refs and objects are shared.

```sh
git worktree add -b agent/route-host ../example-repo-route-host trunk
git worktree list
# ...the agent builds, tests and commits inside ../example-repo-route-host...
git worktree remove ../example-repo-route-host
git worktree prune          # clears records of worktrees deleted by hand
```

Rules and behavior:

- **Check the base first.** A worktree created by a tool, or from a stale
  ref, may start before the commit the brief relies on, such as a contract
  stub commit. Check with
  `git merge-base --is-ancestor <required-commit> HEAD` (exit status 0 means
  it is present) and fast-forward or rebase before starting work.
- **One branch, one worktree.** `add` refuses a branch already checked out
  elsewhere unless forced. Give each agent its own branch.
- **Build output stays apart.** Build folders inside the worktree directory
  are separate, so builds no longer collide. Output configured to an absolute
  path outside the tree, and shared package or compiler caches, are still
  shared; check the build configuration.
- **Ignored files are absent.** A new worktree has no ignored local
  configuration, restored packages or previous build output. Restore and
  build before running tests.
- **Removal needs a clean tree.** `git worktree remove` refuses a worktree
  with modified or untracked files. Commit or deliberately discard the work;
  use `--force` only after checking what it would delete.
- **Build before merging.** Check out another agent's branch in its own
  worktree and build and test it there before merging. A branch reported as
  finished may never have compiled on a clean checkout, and its tests may
  assert the very bugs it was meant to fix.
- **Merging back is ordinary Git.** Merge, rebase or cherry-pick the agent's
  commits into the target branch from a clean tree, then run the integrated
  checks.
- **A second worktree for the orchestrator.** When an agent owns the feature
  branch in the main checkout and the orchestrator must commit elsewhere,
  such as a fix to the trunk, it does so in a worktree of that branch rather
  than switching the shared tree.

## Contract-First in Git Terms

1. On the base branch, commit the shared interface as compiling stubs:
   types, signatures, and documented behavior, with bodies that fail loudly
   (for example, by throwing "not implemented").
2. Push the stub commit. Both agents start from it, in disjoint files or in
   separate worktrees.
3. Each agent commits and pushes its sub-steps on its own path or branch.
4. A change to the contract goes through the orchestrator as a new stub
   commit that both agents pull. An agent never edits the contract file
   unilaterally.
5. Merge, build, and run the integrated tests from one tree.

## Reorientation Commands

After an interruption, before continuing:

```sh
git branch --show-current
git status --porcelain=v1
git fetch origin
git rev-list --left-right --count HEAD...@{upstream}
git log --oneline -10
git worktree list
git stash list        # a stash nobody remembers making needs an owner
```

Then rebuild and rerun the tests. Compare the history with the last reports
and records: a sub-step that a record calls finished but whose commit is
absent was lost or never pushed.

## Lock Contention

Git takes `.git/index.lock` while it writes the index. A second command
started meanwhile fails with `Unable to create '.../index.lock': File
exists`, followed by a note that another Git process may be running or the
lock may be stale. Retry after a short pause. Delete the lock only when you
have confirmed that no Git process is running. Deleting a live lock lets two
commands write the index at once, and one of them can lose its changes.

## Further Information

- Git, [git-commit](https://git-scm.com/docs/git-commit): `--only`,
  `--include`, `--all`, and pathspec behavior.
- Git, [git-worktree](https://git-scm.com/docs/git-worktree): `add`,
  `list`, `remove`, `prune`, `lock`, and per-worktree files.
- Git, [git-pull](https://git-scm.com/docs/git-pull): `--rebase`,
  `--no-rebase`, and `--autostash`.
- Git, [git-stash](https://git-scm.com/docs/git-stash): what a stash takes
  from the tree.
- Git, [git-status](https://git-scm.com/docs/git-status): the porcelain
  formats.
- Git, [git-rev-list](https://git-scm.com/docs/git-rev-list):
  `--left-right --count` for divergence.
- FieldManual, [Version-Control
  Safety](../../../../standards-and-practices/core/version-control-safety.md).
- FieldManual, [Git for Agents on
  Windows](../../../windows/git/overview.knack.md):
  transport, identity, prompts and time limits when agents run Git on
  Windows.
