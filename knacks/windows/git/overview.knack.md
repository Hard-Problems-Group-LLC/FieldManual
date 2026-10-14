# Git for Agents on Windows

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when an AI agent runs Git on a Windows workstation: when a
fetch or push hangs, when commits carry the wrong or no identity, when two
agents need different branches at once, or when long runs must survive
interruption. The
[transport companion](transport.knack.md) covers SSH,
HTTPS, credential prompts, time limits, and submodules in detail. The
[history companion](history.knack.md) covers merging
histories, moving repositories, rewrites, provenance, ignore files shared
with tools, and safe checks on untrusted repositories.

For several GitHub organizations or accounts on one machine, also load
[GitHub SSH and Git identity across organizations](../../authentication/GitHub-SSH-multi-org-sanity.knack.md).
This knack does not repeat its alias and conditional-include patterns.

## Mental Model

An agent's Git differs from a person's Git in four ways:

1. **Nobody answers prompts.** A credential dialog, passphrase prompt, or
   host-key question that a person would answer in seconds blocks an agent
   until the harness times out, and the dialog may be invisible.
2. **The environment may be rewritten.** Harnesses often redirect `HOME` or
   isolate configuration, which changes the global Git configuration, the
   SSH configuration that MSYS tools read, and `~` expansion.
3. **Several writers share one machine.** Another agent or the operator may
   be using the main checkout at the same moment.
4. **Runs are interrupted.** Restarts, crashes, and quota limits end long
   sessions without warning. Work that exists only in a working tree is at
   risk.

The defaults below follow from those four facts.

## Fail Fast Instead of Prompting

- Prefer SSH remotes and Windows' own OpenSSH client in batch mode, so a
  missing or locked key fails at once instead of waiting for input.
- Set `GIT_TERMINAL_PROMPT=0` so Git does not prompt on the terminal, and
  `GCM_INTERACTIVE=never` so Git Credential Manager fails instead of opening
  a dialog.
- Put a time limit around every network command: fetch, pull, push, clone,
  `ls-remote`, and submodule update.
- Treat a timeout as unknown state. Check whether a push landed with
  `git ls-remote` before retrying.

Concrete commands are in the
[transport companion](transport.knack.md).

## Identity Under a Redirected Home

When `HOME` points into a sandbox, Git stops reading the operator's
`~/.gitconfig`. Symptoms include "Author identity unknown", commits with a
generated or wrong email address, and `user.useConfigOnly` refusals.

Fixes, from most to least preferred:

1. **Point Git at the real global file** for the commands that need it:
   `GIT_CONFIG_GLOBAL=<path to the operator's .gitconfig>`. When this is
   set, Git reads neither `$HOME/.gitconfig` nor the XDG global file.
2. **Pass identity per command**:

   ```bash
   git -c user.name="Example Developer" \
       -c user.email=dev@alpha.example commit ...
   ```

   This also works where a sandbox refuses environment variables that
   redirect Git's configuration.
3. **Set repository-local identity** with `git config user.email`, only
   when the operator agrees, because it persists in `.git/config`.

Never invent a name or address to get past an error. Ask the operator.

Two traps survive even the first fix:

- Include paths and `includeIf "gitdir:~/..."` patterns that start with
  `~/` expand against `$HOME`, so conditional identity rules can stop
  matching under a redirected home. Prefer absolute paths in rules that
  automation relies on.
- `GIT_AUTHOR_*` and `GIT_COMMITTER_*` environment variables override
  configuration.

Verify before the first commit and after any environment change:

```bash
git -C <repo> config --show-origin --get user.email
git -C <repo> var GIT_AUTHOR_IDENT
git -C <repo> var GIT_COMMITTER_IDENT
```

After committing, check both identities on the new commit:

```bash
git -C <repo> log -1 --format='%an <%ae> | %cn <%ce>'
```

## Worktrees for Parallel Writers

Give each agent that builds, runs tests, or works on its own branch a
separate worktree. Agents that only edit disjoint files can share one tree
if they commit by path and never use sweeping commands; that discipline,
and the general worktree rules (shared refs and objects, one branch per
worktree, removal, and checking the base), are in
[Shared-Checkout Subagents](../../AI/agent-orchestration/shared-checkout/overview.knack.md).

```bash
git -C <repo> worktree add ../example-app-feature-x feature/x
git -C <repo> worktree add -b feature/y ../example-app-feature-y trunk
git -C <repo> worktree list
```

Points that matter on a workstation:

- Do not override Git's refusal to check out a branch that another
  worktree holds with `--force` to "unblock" an agent; pick or create
  another branch.
- Stashes live in shared refs, so `git stash` in one worktree is visible
  from the others.
- Git documents multiple checkouts of a superproject with submodules as
  incomplete and not recommended. Use a separate clone for repositories
  with submodules.
- Place worktrees beside the repository rather than inside its working
  tree, so search, build, and packaging tools in the main checkout do not
  pick up a second copy of the sources.
- A linked worktree's Git directory lives under the main repository's
  `.git/worktrees/`, so `gitdir:` conditions follow the main repository
  even when the worktree sits elsewhere. Recheck identity in each new
  worktree anyway.

## Commit and Push Cadence

Assume the session can end at any moment. A restart for operating-system
updates is a common cause on Windows; see
[reboot forensics](../event-logs/reboots.knack.md).

- Work on a feature branch, never directly on the shared default branch.
- Commit after each verified step, with a message that states what was
  done and what remains.
- Push the feature branch after each commit when the remote and the
  project's policy allow it.
- Record in-flight intent in tracked notes or the commit message, not only
  in the agent's context, so a successor can resume.
- Do not force-push shared branches, rewrite published history, or delete
  remote branches without explicit authorization. Follow FieldManual's
  [version-control safety](../../../standards-and-practices/core/version-control-safety.md)
  standard.

## Read-Only Checks Worth Knowing

- `git check-ignore -v <path>` names the rule that ignores a path, or
  confirms that nothing does.
- `git clean -nd` and `git clean -ndX` preview untracked and ignored files
  without deleting anything.
- `git status` reports "ahead" and "behind" against the last fetched
  tracking refs. When fetches have been failing, those counts are stale;
  compare with `git ls-remote` before acting on them.

## Line Endings

Git for Windows commonly sets `core.autocrlf=true`, and agent tools often
write LF, which produces "LF will be replaced by CRLF" warnings. Those are
usually harmless. See the
[text files companion](../shells/text-files.knack.md)
for the rules, the warning's meaning, and byte-preserving edits.

## Review Checklist

- Does every network command have a time limit and a non-interactive
  configuration?
- Is the remote an SSH URL using the intended host alias?
- Do `git var GIT_AUTHOR_IDENT` and `GIT_COMMITTER_IDENT` show the intended
  identity in this exact environment?
- Is this writer alone in its working tree, or following the
  shared-checkout rules?
- Has every verified step been committed and, where allowed, pushed?

## Further Information

- Git, [git: environment variables, including `GIT_TERMINAL_PROMPT` and `GIT_CONFIG_GLOBAL`](https://git-scm.com/docs/git)
- Git, [git-config: files, includes, and conditional includes](https://git-scm.com/docs/git-config)
- Git, [git-worktree](https://git-scm.com/docs/git-worktree)
- Git, [git-var](https://git-scm.com/docs/git-var)
- Git Credential Manager, [environment variables](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/environment.md)
- FieldManual, [session and project boundaries](../../../standards-and-practices/core/session-and-project-boundaries.md)
