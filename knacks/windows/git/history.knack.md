# Git History and Repository Hygiene for Agents

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when an agent merges histories, moves a project to a
new repository, reconciles its branch with someone else's rewrite,
rewrites history, edits ignore rules, or runs automated Git checks on a
repository it does not fully trust. Read the
[Git for agents overview](overview.knack.md) first, and
follow FieldManual's
[version-control safety](../../../standards-and-practices/core/version-control-safety.md)
standard for anything that changes shared history.

## Merge Only From Fresh Remote Refs

Remote-tracking refs such as `origin/trunk` are whatever the last
successful fetch left. In a sandbox where fetches fail, they can be days
old, and `git merge origin/trunk` then silently misses upstream work.
Before merging from a remote branch:

```bash
git -C <repo> ls-remote origin refs/heads/trunk   # what the server has
git -C <repo> rev-parse origin/trunk              # what the local ref says
```

If they differ, fetch successfully first. The age of `.git/FETCH_HEAD`
also shows when a fetch last succeeded.

## Move a Project Into a New Repository

To keep the full history when a project moves:

```bash
git -C <new> remote add old ../old-project
git -C <new> fetch old
git -C <new> merge --allow-unrelated-histories --no-commit old/trunk
# resolve add/add conflicts, then commit
git -C <new> remote remove old
```

For an add/add conflict, `git show :2:<path>` prints this side's version
and `git show :3:<path>` the incoming one, which makes deliberate joins
easy. Do renames in a separate follow-up commit, so the merge shows only
the history join. Finally, freeze the old repository with one commit whose
README points to the new home.

## Reconcile an Agent Branch With a Verified Rewrite

When an unverified agent branch and a verified parallel rewrite of the
same work meet, merge rather than rebase so both histories stay
inspectable, resolve conflicts by class of file (for example, verified
source wins while agent infrastructure is kept), and state that policy in
the merge commit message. The full procedure, including append-only logs,
is in
[Integrating Unverified Agent Work: Integration](../../AI/agent-orchestration/unverified-work/integration.knack.md).

## Identity and Provenance

- Never derive a commit identity from a remote URL or an SSH host alias.
  Use the identity the operator provides; see the overview.
- Some agent tools commit with the human's author identity and add no
  trailer, so provenance survives only in the hosting service's merge
  messages. Keep those merge commits, or require an agreed trailer such
  as `Co-authored-by:` on agent commits.
- When several agents share a checkout, commit by path and leave shared
  records to one writer; see
  [Shared-Checkout Subagents](../../AI/agent-orchestration/shared-checkout/overview.knack.md).

## Restore Old Versions Safely on Windows

To build or test the pre-change code temporarily:

- `git stash push -- <paths>` stashes only those paths; untracked new
  files are not stashed unless `-u` is given, so move them aside or
  include them deliberately; and
- `git restore --source=HEAD -- <path>` restores a committed version
  through Git's own filters.

Avoid `git show HEAD:<path> > <path>` on Windows: it bypasses
line-ending conversion, and in Windows PowerShell 5.1 the `>` operator
writes UTF-16. See the
[text files companion](../shells/text-files.knack.md).

## Rewriting History

Changing an author address, removing a file, or squashing published
commits changes every later commit's hash. Before doing it with
permission:

- create a backup branch, such as `backup/<branch>-before-rewrite`;
- find records that cite the old hashes, such as decision logs, issues,
  or release notes, and update them; and
- coordinate with everyone who has the old history.

FieldManual's
[purge large or sensitive files](../../version-control/purge-large-files-from-git-history.knack.md)
knack covers the heavier case.

## Executable Bits and Byte-Exact Files

- Windows filesystems do not record the POSIX executable bit, so shell
  scripts committed from Windows can lose it. Stage it explicitly with
  `git add --chmod=+x <path>`, and test direct execution (`./script.sh`)
  on a POSIX host.
- Byte-exact fixtures, such as signed archives or recorded outputs, need
  `* -text` in a `.gitattributes` file inside the fixture folder, or
  `core.autocrlf` may rewrite them. A shell script checked out with CRLF
  does not run under Bash.

## Ignore Files Shared With Tools

- Tools that manage part of `.gitignore` often mark their region with
  `# BEGIN ... managed by <tool>` and `# END` lines. Treat each block as
  owned by its tool: never deduplicate or rewrite another tool's block,
  even when entries overlap.
- Check the bytes after any automated edit. In a test, a line ending in
  `\r\r\n`, as produced by a tool that wrote CRLF into an already-CRLF
  checkout, silently stopped that entry from matching, while a CRLF line
  worked.
- Verify ignore rules per path with `git check-ignore -v <path>`.

## Automated Checks on Untrusted Repositories

Repository configuration can run commands. When a tool inspects a
repository it does not control, disable the hooks it could trigger and
use literal paths:

```bash
env -u GIT_LITERAL_PATHSPECS -u GIT_GLOB_PATHSPECS -u GIT_NOGLOB_PATHSPECS \
    -u GIT_ICASE_PATHSPECS \
    git -c core.fsmonitor=false -C <root> ls-files -z -- ':(literal,icase)<path>'
```

- `core.fsmonitor` in a repository's own configuration can name a command
  that Git runs; overriding it on the command line prevents that.
- `:(literal)` stops wildcard interpretation; add `icase` on
  case-insensitive filesystems.
- With `GIT_LITERAL_PATHSPECS` set, pathspec magic such as `:(literal)` is
  itself taken literally, matches nothing, and a "not tracked" check
  passes silently, so clear those variables first.

## Submodules in Bootstrap Code

Bootstrap scripts should initialize submodules that are missing and leave
initialized ones alone: `git submodule update` moves an initialized
submodule back to the recorded commit. Before writing into a submodule
path, check that no component of the path is a link or junction that
could redirect writes into another repository.

## Branches Missing New Tooling

Tools added to the default branch after a feature branch was cut, such as
a new submodule or helper script, do not exist on that branch until the
default branch is merged in. Meanwhile, run them from a worktree of the
default branch rather than copying files across.

## Further Information

- Git, [git-merge: `--allow-unrelated-histories`](https://git-scm.com/docs/git-merge)
- Git, [git-restore](https://git-scm.com/docs/git-restore)
- Git, [git-stash](https://git-scm.com/docs/git-stash)
- Git, [gitglossary: pathspec magic](https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddefpathspecapathspec)
- Git, [git: `GIT_LITERAL_PATHSPECS`](https://git-scm.com/docs/git)
- Git, [git-config: `core.fsmonitor`](https://git-scm.com/docs/git-config)
- Git, [git-check-ignore](https://git-scm.com/docs/git-check-ignore)
- Git, [git-submodule](https://git-scm.com/docs/git-submodule)
- Git, [gitattributes](https://git-scm.com/docs/gitattributes)
