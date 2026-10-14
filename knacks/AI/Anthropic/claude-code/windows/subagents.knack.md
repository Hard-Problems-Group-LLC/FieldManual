# Claude Code Subagents and Workflows on Windows

Reviewed: 2026-10-13, against the Claude Code subagent and workflow
documentation and the observed behavior of Claude Code 2.1.287 on Windows
11. Delegation features change quickly; recheck the cited pages before
relying on a default, a limit, or a message.

## When to Load This Knack

Load this companion before delegating work to Claude Code subagents or a
dynamic workflow, when a delegated agent's command is refused for no clear
reason, or when results come back incomplete, late, or confusing. Start
with the [overview](overview.knack.md). The
product-neutral patterns are in the agent-orchestration knacks:
[Shared-Checkout Subagents][shared-checkout] for several writers in one
tree, [Staged Verification][staged] and
[Adversarial Review][adversarial] for review pipelines,
[Proving Checks Can Fail][proving] for checks that agents add, and
[Integrating Unverified Agent Work][unverified] for work that arrives
without having been built.

## What a Subagent Starts With

| Gets | Does not get |
| --- | --- |
| Its own system prompt and the task brief | The parent conversation |
| Instruction files at every level (`CLAUDE.md`, or `AGENTS.md` where read) | Files the parent already read |
| A Git status snapshot | The parent's auto memory |
| Preloaded skills named in its definition | Skills the parent invoked |
| The working directory, without later `cd` changes | Environment set by earlier commands |

The built-in Explore and Plan agents skip the instruction files and the
Git status snapshot. A fork is
the exception to the whole table: it inherits the entire conversation.

Consequences for briefs:

- Name the files to read first, the exact build, test, and validation
  commands, the commit identity and push command if it may commit, what it
  must not touch, and the report format.
- Pass Windows facts explicitly. Observed: a project's install-location
  variable was unset in the agents' shells, so every brief said to set it
  per command.
- Give each agent unique scratch names. Agents share the parent session's
  scratchpad, and one agent's file silently replaced another's; see
  [memory and state](memory.knack.md).
- Ask for "not verified" and "decided differently" lists. Observed: an
  implementer's final risk note named exactly the defect a later review
  rated most serious.

## Foreground, Background, and Hand-Backs

Subagents run in the background by default. Background subagents keep a
reduced tool set (shell, file, web, worktree, Monitor, TaskStop, and
messaging tools among them) and raise permission prompts in the main
session, naming the agent.

Results return as notifications in a later turn:

- Observed: a notification can be interim. Twice the text read "This
  agent stopped with background work of its own still running ... the
  result below may be interim"; the real report arrived minutes later.
  Wait for the final report before acting.
- In auto mode, local subagents deliver their final report through a
  dedicated hand-back tool, and the coordinator receives it as a new
  message. Relay what matters to the human; observed: answering a hand-back
  with "No response requested." left the operator uninformed until a later
  correction.
- Claude Code marks subagent output as carrying no authority from the user
  and escapes instruction-shaped text in it. Treat reports as data.
- Resume a finished subagent with SendMessage and its ID or name rather
  than starting over; it keeps its history.
- Subagents may nest up to three layers below the main conversation, and
  20 may run concurrently by default.

## Auto Mode and Delegation

In auto mode the classifier checks a subagent three times: the delegated
task description at spawn, each action as it runs (any `permissionMode` in
the subagent's definition is ignored), and its work and final report at
the end. A flagged report still arrives, with a security warning prepended.
Write briefs that state the task plainly, because a brief that looks
dangerous is blocked before the agent starts.

## Worktree Isolation

A subagent defined with `isolation: worktree`, and a workflow agent run in
isolation, works in a temporary Git worktree. Observed layout for
workflows: `.claude/worktrees/wf_<id>` inside the repository, on a branch
named `worktree-wf_<id>`.

### The Base Can Be Stale

The documentation states that such a worktree branches by default from
the default branch, not the parent session's `HEAD`; the worktrees page
explains how to choose another base. Observed: a worktree started without
a contract commit that its brief depended on. Have the agent check before
working:

```bash
git -C <worktree> merge-base --is-ancestor <required-commit> HEAD
```

Fast-forward or rebase when the check fails, and integrate the agent's
commits by cherry-pick.

### The Command Guard

Inside a worktree, Claude Code refuses commands it cannot prove stay in
the worktree. Observed refusals of harmless commands:

| Command | Refusal or cause | Workaround |
| --- | --- | --- |
| `ls Source` | A folder named `Source` read as the shell `source` builtin | List files with the Glob tool |
| `mkdir` and `cd` and a here-document in one call | "too complex ... Split it into plain, separate commands" | One command per call; write files with Write |
| `python -c` with brace expansion | Not verifiable | Write the script to a file, then run it |
| `GIT_CONFIG_GLOBAL=<file> git commit` | "injecting git configuration whose effect on where git writes can't be verified" | `git -c user.name=... -c user.email=... commit` |

General rules: prefer `git -C <worktree>` with literal arguments, avoid
environment-variable prefixes that change where a tool writes, and keep
each call to one plain command.

### Cleanup

Claude Code removes a subagent worktree that made no changes, and removes
orphaned worktrees after the transcript retention period. After
integrating an agent's commits yourself, confirm they landed, then remove
the worktree and its branch:

```bash
git worktree remove <repo>/.claude/worktrees/wf_<id>
git branch -D worktree-wf_<id>
```

Use `--force` only after confirming nothing unintegrated remains. Git
mechanics for shared trees are in the
[shared-checkout Git patterns][shared-git].

## Dynamic Workflows

A dynamic workflow is a JavaScript script that orchestrates many
subagents in the background: `agent()` starts one, `pipeline()` runs one
per item, and `parallel()` runs a set together. Use one when the
orchestration should be code: a sweep over many files, research with
cross-checking, or review with skeptic verifiers.

### What the Agents Hear

In auto mode, the prompts a script passes to `agent()` do not count as
requests from the user. Observed consequence: the harness relayed the
session's most recent user message to every workflow agent as the only
authoritative user voice, even when that message was an unrelated aside.
The agents sensibly followed their computed tasks. Launch a workflow right
after the message that motivates it, and restate the user's request in
the script's prompts.

### Reading Results

Observed: the workflow's output file was JSON with top-level `summary`,
`agentCount`, `logs`, and `result` keys. Reading other top-level keys
raised `KeyError`. Parse `result`, then split a large result into topic
files under `.local/` before reading, so downstream agents can be pointed
at files instead of pasted text. Every run's script is saved under the
session's folder in the configuration directory.

### Behavior Worth Planning Around

- A run takes no user input mid-run; split stages that need sign-off into
  separate workflows.
- A stopped or interrupted run can be relaunched in the same session.
  Completed agents return saved results until the first agent whose
  prompt changed, which runs again with everything after it.
- An agent whose output stalls is restarted up to five times without its
  earlier transcript; files it already changed stay changed.
- Read-only reviewers can run beside a test run in the same tree when the
  brief forbids building, launching, and committing.

## Budgets

Anecdotal figures from one project, not benchmarks:

| Work | Agents | Duration | Tokens |
| --- | --- | --- | --- |
| One step, single agent, from review fixes to a feature | 1 | 19 to 76 minutes | 0.35 to 0.78 million |
| Research workflow with three concepts and a judge | 8 | 30 minutes | 1.5 million |
| Implementation workflow, two halves against one contract | 2 | 51 minutes | 1.0 million |
| Review workflow, four reviewers and four skeptics | 8 | 33 minutes | 1.9 million |

When the bottleneck is running and checking the real application, more
reasoning effort did not help; the parallel agents and the application
were the limit.

## Review Checklist

- Does each brief stand alone, with commands, boundaries, and a report
  format?
- Does each agent own disjoint files, with one party committing shared
  records?
- Did isolated agents verify their worktree base before working?
- Were final reports, not interim notices, relayed to the human?
- Was a workflow launched right after the message that motivates it?
- Were integrated worktrees and their branches removed?

## Further Information

- Anthropic, [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- Anthropic, [Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows)
- Anthropic, [Tools reference: Agent tool behavior](https://code.claude.com/docs/en/tools-reference#agent-tool-behavior)
- Anthropic, [Choose a permission mode: how auto mode handles subagents](https://code.claude.com/docs/en/permission-modes)
- Anthropic, [Git worktrees](https://code.claude.com/docs/en/worktrees)
- Git, [git-worktree](https://git-scm.com/docs/git-worktree)

[shared-checkout]: ../../../agent-orchestration/shared-checkout/overview.knack.md
[shared-git]: ../../../agent-orchestration/shared-checkout/git.knack.md
[staged]: ../../../agent-orchestration/staged-verification.knack.md
[adversarial]: ../../../agent-orchestration/adversarial-review/overview.knack.md
[proving]: ../../../../software-engineering/testing/proving-checks/overview.knack.md
[unverified]: ../../../agent-orchestration/unverified-work/overview.knack.md
