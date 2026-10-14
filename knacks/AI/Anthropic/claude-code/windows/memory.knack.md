# Claude Code Memory and State on Windows

Reviewed: 2026-10-13, against the Claude Code memory, context-window, and
`.claude` directory documentation and the observed behavior of Claude
Code 2.1.287 on Windows 11. File layouts and limits change between
releases; recheck the cited pages before scripting against them.

## When to Load This Knack

Load this companion when deciding where an agent should keep instructions,
learnings, and scratch files; when context compaction or a session change
loses work; when mining past sessions for lessons; or when moving a
project whose Claude Code state must come along. Start with the
[overview](overview.knack.md). Isolating that state
from the operator's profile is covered in
[Windows Agent Isolation][isolation].

## Where State Lives on Windows

`~/.claude` means `%USERPROFILE%\.claude`, or the folder named by
`CLAUDE_CONFIG_DIR` when that is set. Everything below follows the
variable except the temporary tree.

| State | Location | Lifetime |
| --- | --- | --- |
| Settings, plugins, skills | Configuration folder | Until changed |
| Login | `.credentials.json` in the configuration folder | Until `/logout` |
| Global state and project list | `%USERPROFILE%\.claude.json`; observed inside the configuration folder when the variable is set | Until changed |
| Transcripts | `projects\<project>\<session>.jsonl` | 30 days by default (`cleanupPeriodDays`) |
| Subagent transcripts, large tool output | `projects\<project>\<session>\subagents\` and `tool-results\` | With the parent transcript |
| Auto memory | `projects\<project>\memory\` | Until deleted |
| Background sessions | `jobs\<id>\`, `daemon\` | Until the session is deleted |
| Session scratchpad | `%TEMP%\claude\<project>\<session-id>\scratchpad\` | With the transcript, or sooner if Windows clears `%TEMP%` |

`<project>` is the working-directory path with every character other than
letters and digits replaced by `-`. `CLAUDE_CODE_TMPDIR` moves the
temporary tree. Transcripts and history are plaintext: anything a tool
read or printed, including a credential, is on disk.

## Instructions and Memory

- **Instruction files** hold rules the operator wants every session to
  follow. Claude Code reads `CLAUDE.md`, and since 2.1.277 reads
  `AGENTS.md` directly when no `CLAUDE.md` exists. A `CLAUDE.md` that
  imports `@AGENTS.md` serves several agents from one file; on Windows,
  prefer the import to a symbolic link, which needs Developer Mode or
  administrator rights and arrives as a plain file unless Git's
  `core.symlinks` is on.
- **Auto memory** holds what the agent learned. `MEMORY.md` is an index
  loaded at every session start, up to the first 200 lines or 25 KB. Topic
  files load on demand. All worktrees of one repository share the folder,
  and it never leaves the machine.
- **Project records** hold decisions, open questions, and work state for
  humans and other agents. Memory is not a substitute.

A memory layout that worked well (observed):

- one fact per file, with short frontmatter naming it and its kind;
- a "Why" line quoting the operator's words with the date, and a "How to
  apply" line;
- a one-line index entry per file in `MEMORY.md`;
- a "verified at commit" stamp on facts about code; and
- rewriting a note as soon as it is superseded, rather than appending a
  contradiction.

## Compaction

Claude Code compacts automatically near the context limit, and on request
with `/compact`. Observed: automatic compactions at about 967,000 and
983,000 tokens reduced the context to 11,000 to 26,000 tokens; a manual
compaction while idle avoided paying for an expired prompt cache.

| Survives compaction | Lost or summarized |
| --- | --- |
| System prompt, project-root `CLAUDE.md`, unscoped rules, auto memory, the plan file | Conversation detail, exact commands, tool output |
| Up to five recently changed files, re-read | Nested `CLAUDE.md` files and path-scoped rules until they trigger again |
| Running background commands and subagents | Boundaries the operator stated only in conversation |

Therefore:

- Write each hard-won fact to memory or a record when you learn it, not
  before compaction. Summaries keep error-and-fix lists but drop the exact
  command that worked.
- Ask the operator to turn a conversational boundary ("don't push") into
  a deny rule when it must hold all session.
- A SessionStart hook matching the `compact` source can re-inject
  project context after each compaction.

## Scratch Space

- The scratchpad is keyed by session ID. Observed: moving an interactive
  session to the background continued the conversation under a new
  session ID, and the decompiled sources, decompiler, and validator kept
  in the old scratchpad were gone. Keep anything worth more than a minute
  of work in the project's ignored `.local/` area.
- Subagents and workflow agents write to their parent session's
  scratchpad. Observed: a subagent's `mv` into the scratchpad silently
  replaced a same-named script that an earlier workflow agent had left
  there; it was recovered from that agent's transcript. Prefix scratch
  files with the task's name, and use `mv -n` or check before
  overwriting.
- Background sessions get `CLAUDE_JOB_DIR`; `$CLAUDE_JOB_DIR/tmp` is
  per-session scratch that is removed when the session is deleted.
- Task output files also accumulate under `%TEMP%\claude\<project>\`;
  observed: 46 MB for one project. Clean them when retiring a checkout.
- Disposable test workspaces belong in uniquely named children of
  `.local/tmp/`, per the [local operator state][local-state] standard.

## Transcripts as a Source of Lessons

Past sessions record every command, error, and correction. They are the
best raw material for knacks, memory, and process fixes.

- Mine them before the retention sweep deletes them, or ask the operator
  to raise `cleanupPeriodDays`.
- Treat them as read-only; auto mode blocks writes to transcripts. Copy
  what you need into `.local/` and work on the copy.
- Stream the JSONL with a script into short digests: the opening prompt,
  assistant text, tool calls, failing results, and final reports. Include
  `subagents\` transcripts and saved workflow scripts; the compaction
  summaries are ready-made indexes.
- Generalize as you extract: replace user names, machine names, and paths
  with placeholders, and never copy tokens, keys, or email addresses.
- Record each finding with its lesson, evidence (timestamp and error
  text), and scope, then check whether existing guidance already covers
  it.

## Moving or Copying a Project's State

Claude Code keys state on exact path strings. Observed: after a project
moved to a new folder, the old path was baked into the `projects` keys of
`.claude.json`, the plugin marketplace's install location, every
`history.jsonl` entry, each transcript's `cwd` field, and the
`projects\<project>\` folder name.

- Rewrite those paths with an idempotent script, and verify by comparing
  transcript line counts between the old and new locations.
- Spell the path the same way every time. A launcher reported that a
  lower-case drive letter or an 8.3 short name forks the state, with a
  new folder-trust prompt and missing history.
- When copying a live configuration folder, leave process state behind
  (`daemon`, `sessions`, `jobs`, `session-env`, `shell-snapshots`, and
  lock files) and any browser profile, refuse to run while a session
  recorded under `sessions\` is still alive, and copy memory only into an
  empty target.
- Two folders cloned from one login share its tokens; a refresh in one
  may sign the other out (predicted, not observed). `/login` repairs it.

## Review Checklist

- Are rules in instruction files, learnings in memory, and decisions in
  project records?
- Is each new fact written down when learned?
- Does any durable work depend on the session scratchpad?
- Are hard boundaries deny rules rather than conversation?
- Were transcripts mined, generalized, and stripped of secrets before
  retention removed them?
- After a move, do all path keys use one canonical spelling?

## Further Information

- Anthropic, [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- Anthropic, [Explore the context window: what survives compaction](https://code.claude.com/docs/en/context-window#what-survives-compaction)
- Anthropic, [Explore the .claude directory](https://code.claude.com/docs/en/claude-directory)
- Anthropic, [Authentication: credential management](https://code.claude.com/docs/en/authentication#credential-management)
- Anthropic, [Hooks reference](https://code.claude.com/docs/en/hooks)
- Anthropic, [Background sessions and agent view](https://code.claude.com/docs/en/agent-view)

[isolation]: ../../../../sandboxing/windows-agents/overview.knack.md
[local-state]: ../../../../../standards-and-practices/core/local-operator-state.md
