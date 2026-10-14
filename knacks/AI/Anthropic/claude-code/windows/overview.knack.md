# Claude Code on Native Windows

Reviewed: 2026-10-13, against the Claude Code documentation and the
observed behavior of Claude Code 2.1.287 on Windows 11. Claude Code
changes weekly. Statements marked "observed" record what happened on that
date, not documented guarantees; recheck the cited pages before relying on
a version-sensitive detail.

## When to Load This Knack

Load this knack when Claude Code works as a coding agent on native Windows,
not inside WSL, and the task needs its tools to cooperate: choosing a
shell, getting past permission refusals, waiting for slow work, keeping
state across sessions, delegating to subagents, or recovering after an
interruption. It assumes Git for Windows and PowerShell 7 are installed.

Companions:

- [Tools](tools.knack.md): tool-by-tool behavior
  and traps on Windows;
- [Subagents and workflows](subagents.knack.md):
  what delegated agents inherit, how results come back, and worktree
  isolation; and
- [Memory and state](memory.knack.md):
  instruction files, memory, compaction, scratch space, and transcripts.

Shell mechanics live in [Agent Shells][agent-shells], Git transport and
identity in [Git for Agents][git-agents], and process ownership in
[Processes and Files][proc-files]. Isolation from the operator's profile is
in [Windows Agent Isolation][isolation].

## Mental Model

On native Windows the harness maps its tools to these programs:

| Tool | What runs | Notes |
| --- | --- | --- |
| Bash | Git Bash from Git for Windows | Set `CLAUDE_CODE_GIT_BASH_PATH` if it is not found |
| PowerShell | `pwsh.exe`, else `powershell.exe` 5.1 | Profiles are not loaded |
| Monitor | A background command run by Git Bash | Unavailable without Git Bash |
| Read, Edit, Write, Glob, Grep | Claude Code itself | Governed by permission rules, not a shell |

Without Git for Windows only the PowerShell tool exists. With it, the
PowerShell tool is on by default for claude.ai and Console accounts and
opt-in for cloud-provider accounts.

Three facts shape everything else:

1. **There is no operating-system sandbox.** Claude Code's sandbox runs on
   macOS, Linux, and WSL2. On native Windows every command runs with the
   full rights of the Windows account. Permission rules and the auto-mode
   classifier decide what starts; nothing contains what it does once
   started.
2. **Each command is a new process.** Environment variables never persist
   between calls, and the working directory persists only while it stays
   inside the project.
3. **The conversation is not storage.** Context compacts, the session
   scratchpad can disappear, and Windows restarts. Durable facts belong in
   files.

## Choose the Shell per Task

- Use PowerShell for Windows-native work: processes, services, event logs,
  the registry, ACLs, .NET, MSBuild, and anything documented for
  PowerShell.
- Use Bash for POSIX tooling: `grep`, `sed`, `find`, Git pipelines, shell
  scripts, and Monitor until-loops.
- Keep one interpreter per command. Calling `powershell.exe` from Bash, or
  `bash` from PowerShell, adds a quoting layer; write a script file instead.
- A Bash deny rule silently turns the PowerShell tool off unless
  PowerShell is enabled explicitly or has its own rule, so a narrow Bash
  deny can cost you PowerShell for the session.

## Permissions: Adjust, Do Not Retry

Permission modes set the baseline: `default` (shown as Manual),
`acceptEdits`, `plan`, `auto`, `dontAsk`, and `bypassPermissions`. Since
2.1.283, interactive terminal sessions start in auto mode where it is
available. In auto mode a classifier reviews shell commands, network
actions, and protected-path writes; reads and edits inside the working
directory skip it.

When the classifier blocks an action, Claude receives the rule it matched.
Treat the block as information:

- Do not resubmit the command or a disguised variant. Three blocks in a
  row, or twenty in a session, pause auto mode and return to prompting.
- Rewrite into something the classifier can verify: literal paths rather
  than variables filled from earlier output, one purpose per command, and
  no destructive step chained behind a harmless one.
- When the action is genuinely needed, ask the operator. An approval in
  conversation must name the action and its specifics, such as the branch
  of a force push, and covers that one action.
- For recurring needs, the operator can add `permissions` rules or
  `autoMode.environment` entries. A boundary stated only in conversation
  can be lost at compaction; hard limits belong in deny rules.

## Long-Running Work

- Foreground commands default to a 2-minute timeout and may request up to
  10 minutes. At the timeout the command moves to the background instead
  of dying, and the result names its task ID and output file.
- Start builds, long test suites, and launched applications with
  `run_in_background`, keep working, and act on the completion notice.
- Wait for a condition with the Monitor tool and an until-loop, such as
  `until grep -q 'RUN COMPLETE' "$LOG"; do sleep 2; done`. Observed: a
  foreground `Start-Sleep` followed by a check was refused with "To wait
  for a condition, use Monitor with an until-loop ... Do not chain shorter
  sleeps to work around this block." Sleeps inside a script you run are
  unaffected.
- Stop a runaway task with TaskStop. In some sessions it is a deferred tool
  that must be loaded through tool search first.

## Keep State Outside the Conversation

- Use absolute paths in every command.
- Keep durable scratch, such as decompiled sources, downloaded tools,
  validators, and run logs, in the project's ignored `.local/` area, as
  FieldManual's [local operator state][local-state] standard describes.
  The session scratchpad lives under
  `%TEMP%\claude\<project>\<session-id>\scratchpad\`. Observed: when a
  session moved to the background and continued under a new session ID,
  the tools kept in its scratchpad were gone.
- Write hard-won facts down as you learn them: project records for
  decisions, `CLAUDE.md` or `AGENTS.md` for instructions, and auto memory
  for learnings. Compaction summaries keep decisions and error lists but
  lose exact commands.

## Delegate and Relay

A subagent starts with the instruction files, a Git status snapshot, and
its brief, not your conversation. Brief it completely: what to read, the
exact build and test commands, what not to touch, and the report format.
Background subagents report through completion notifications, and an early
notice can be interim. When the final report arrives, relay what matters
to the human; observed: a coordinator that answered a hand-back with "No
response requested." left the operator uninformed. See
[Shared-Checkout Subagents][shared-checkout] for working in one tree.

## Recover After a Forced Restart

Windows Update can restart the machine mid-run. Shutdown stops background
sessions; one that made progress within 48 hours shows as failed and
restarts from its saved conversation when you reply, and every transcript
remains available to `claude --resume`.

After a restart:

1. Reorient as the [session and project boundaries][boundaries] standard
   requires.
2. Check Git before assuming work was lost: `git status`, `git log`,
   `git stash list`, and a fetch. Observed: a resumed session warned that a
   background agent "didn't finish", yet both of its commits were already
   pushed.
3. Rebuild and rerun the checks before trusting partial work.
4. Ask the event log why the machine restarted; see
   [reboot forensics][reboot].

Prevention costs little: commit and push after each completed sub-step,
and set active hours or pause updates before a long unattended run.

## Review Checklist

- Is the shell chosen for the task, with one interpreter per command?
- Are blocked actions rewritten or escalated, not retried?
- Are long operations backgrounded, and conditions awaited with Monitor?
- Is durable scratch inside the project's ignored `.local/` area?
- Were new facts written to records, instructions, or memory?
- Were subagent reports relayed, and partial work checked against Git?

## Further Information

- Anthropic, [Advanced setup: Set up on Windows](https://code.claude.com/docs/en/setup#set-up-on-windows)
- Anthropic, [Tools reference](https://code.claude.com/docs/en/tools-reference)
- Anthropic, [Choose a permission mode](https://code.claude.com/docs/en/permission-modes)
- Anthropic, [Configure permissions](https://code.claude.com/docs/en/permissions)
- Anthropic, [Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing)
- Anthropic, [Background sessions and agent view](https://code.claude.com/docs/en/agent-view)
- Anthropic, [Explore the context window](https://code.claude.com/docs/en/context-window)

[agent-shells]: ../../../../windows/shells/overview.knack.md
[git-agents]: ../../../../windows/git/overview.knack.md
[proc-files]: ../../../../windows/processes-and-files/overview.knack.md
[isolation]: ../../../../sandboxing/windows-agents/overview.knack.md
[local-state]: ../../../../../standards-and-practices/core/local-operator-state.md
[shared-checkout]: ../../../agent-orchestration/shared-checkout/overview.knack.md
[boundaries]: ../../../../../standards-and-practices/core/session-and-project-boundaries.md
[reboot]: ../../../../windows/event-logs/reboots.knack.md
