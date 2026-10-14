# Anthropic Knacks

Reviewed: 2026-10-13

Load these documents only when the task uses the named Anthropic product
surface. Do not transfer behavior between Claude Code, the Claude apps,
the Claude API, and the Agent SDK merely because they share an account or
a model.

## Claude Code on Windows

- [Overview](claude-code/windows/overview.knack.md) —
  what the harness gives an agent on native Windows, choosing the Bash or
  PowerShell tool, permission modes and the auto-mode classifier,
  long-running work, durable state, delegation, and recovery after a
  forced restart
- [Tools](claude-code/windows/tools.knack.md) —
  working directory, scripts instead of inline text, encodings, time
  limits, background work, output limits, file tools, and removal guards
- [Subagents and workflows](claude-code/windows/subagents.knack.md) —
  what delegated agents inherit, interim and final reports, worktree
  isolation and its command guard, and dynamic workflows
- [Memory and state](claude-code/windows/memory.knack.md) —
  where state lives, instruction files and auto memory, compaction, scratch
  space, transcripts as a source of lessons, and moving a project's state

Claude Code changes quickly. Each knack records its review date and the
version its observations come from; recheck the official documentation
before relying on a version-sensitive detail.

## Related Knacks

- [Windows agent isolation](../../sandboxing/windows-agents/overview.knack.md)
  — keeping any coding agent's state and tools out of the operator's
  Windows profile, and what home redirection cannot isolate
- [Windows knacks](../../windows/README.md) — shells, Git, processes,
  event logs, and desktop automation for agents on Windows
- [Agent orchestration](../agent-orchestration/README.md) —
  product-neutral patterns for multi-agent work
