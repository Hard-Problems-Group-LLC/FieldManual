# Sandboxing Knacks

Sandboxing knacks describe practical process-isolation boundaries and their
failure modes.

- [Bubblewrap](bubblewrap.knack.md) covers Linux namespace construction,
  filesystem exposure, user and network choices, and diagnostic techniques.
- [Windows Agent Isolation](windows-agents/overview.knack.md)
  covers what home redirection does and does not isolate for coding agents
  on native Windows, and when to choose a separate account, Windows
  Sandbox, or a virtual machine. Companions:
  [launcher techniques](windows-agents/launcher.knack.md)
  and [verification probes](windows-agents/verification.knack.md).
- Windows Sandbox, a disposable virtual machine for testing on a fresh
  Windows, is under
  [virtualization](../virtualization/windows-sandbox/overview.knack.md).

A sandbox is a declared capability boundary, not a synonym for safety.
Document what remains shared, how identity and credentials are selected, and
which operations require explicit authority to cross the boundary.
