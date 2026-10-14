# Windows Knacks

Reviewed: 2026-10-13

These knacks cover working on a Windows workstation as, or alongside, an AI
coding agent: shells and text encoding, Git transport, identity and
history, process and file ownership, event-log forensics, desktop
automation, and porting command-line tools to Windows. They assume
Windows 10 or 11 with PowerShell and Git for Windows. Product behavior
changes with Windows, PowerShell, Python, and Git releases; check each
knack's review date and its cited documentation before relying on
version-specific details.

## Topics

- [Agent Shells](shells/overview.knack.md) —
  telling Git Bash, PowerShell 7, and Windows PowerShell 5.1 apart,
  working-directory loss, path forms, quoting through layers, and writing
  scripts instead of inline here-documents
  - [PowerShell](shells/PowerShell.knack.md)
    — 5.1 versus 7, encoding defaults, here-strings, text matching, XML
    and reflection, native arguments, and exit status
  - [Git Bash](shells/Git-Bash.knack.md) —
    MSYS path conversion, `cygpath`, calling Windows programs, pipelines,
    terminals, and time limits
  - [Text files](shells/text-files.knack.md)
    — encodings, byte-order marks, line endings, `core.autocrlf`, and
    byte-preserving edits
  - [Python](shells/Python.knack.md) — finding
    the right interpreter, standard-stream encodings, Windows paths in
    source, exact edits, and project-local dependencies
- [Git for Agents](git/overview.knack.md)
  — fail-fast operation, identity under a redirected home, worktrees for
  parallel writers, and commit cadence
  - [Transport](git/transport.knack.md)
    — Windows OpenSSH, `GIT_SSH_COMMAND`, batch mode, HTTPS credential
    prompts, time limits, and submodules over host aliases
  - [History](git/history.knack.md) —
    merging from fresh refs, moving repositories, reconciling branches,
    provenance, rewrites, shared ignore files, and safe checks on untrusted
    repositories
- [Event Logs](event-logs/overview.knack.md) —
  `Get-WinEvent` queries for "what just happened"
  - [Reboot forensics](event-logs/reboots.knack.md)
    — restart and shutdown events, Windows Update installation events, and
    protecting long agent runs
  - [Background events](event-logs/background-noise.knack.md)
    — Auto HDR notifications during automated launches, corrected hardware
    errors, and Windows Sandbox launch events
- [Processes and Files](processes-and-files/overview.knack.md)
  — owning only what you start, second instances, locked files, links,
  copies, and scratch space
  - [Processes](processes-and-files/ownership.knack.md)
    — launching, finding by command line, verifying identity, and stopping
    process trees
  - [Links and copies](processes-and-files/links-and-copies.knack.md)
    — junctions, symbolic links, safe removal, files in use, and
    `robocopy`
- [Desktop Automation](desktop-automation/overview.knack.md)
  — sharing a desktop with a person, DPI awareness, readiness markers,
  window placement, preference files, and captures
  - [Win32 from PowerShell](desktop-automation/Win32.PowerShell.knack.md)
    — tested interop for DPI awareness, waiting, maximizing, and capture
- [Porting CLI Tools](porting-cli-tools/overview.knack.md)
  — what does not port from Linux and macOS, and a porting workflow
  - [Processes in Python](porting-cli-tools/processes.Python.knack.md)
    — job objects instead of `exec`, Ctrl+C, signals, liveness, process
    trees, and elevation
  - [Files in Python](porting-cli-tools/files.Python.knack.md)
    — atomic writes beside readers, replacing running executables, locks,
    file identity, case, path length, and state locations
  - [Launchers](porting-cli-tools/launchers.knack.md)
    — batch shims and argument injection, PowerShell entry points, `PATH`,
    and DLL placement

## Load Order

Start with Agent Shells for any agent work on Windows; most other failures
begin as a quoting, path, or encoding mistake. Add Git for Agents before
network Git work, history surgery, or parallel agents; Processes and Files
before starting or stopping programs or touching links; and Desktop
Automation before driving a graphical application. Load Event Logs when
something already happened and needs an explanation, and Porting CLI Tools
when making a tool run natively on Windows.

## Related Knacks and Standards

- [GitHub SSH and Git identity across organizations](../authentication/GitHub-SSH-multi-org-sanity.knack.md)
- [Windows agent isolation](../sandboxing/windows-agents/overview.knack.md):
  redirected homes and profiles for agent harnesses
- [Windows Sandbox](../virtualization/windows-sandbox/overview.knack.md):
  disposable Windows environments, including fresh-install certificates
- [Claude Code on Windows](../AI/Anthropic/claude-code/windows/overview.knack.md)
- [Steam](../games/steam/overview.knack.md): launching and
  isolating games for automated tests
- [Live user-session targeting](../desktop/live-user-session-targeting.knack.md),
  the Linux counterpart for crossing from isolated automation into a
  person's session
- [Staged verification for multi-agent work](../AI/agent-orchestration/staged-verification.knack.md)
- FieldManual's [local operator state](../../standards-and-practices/core/local-operator-state.md),
  [session and project boundaries](../../standards-and-practices/core/session-and-project-boundaries.md),
  and [version-control safety](../../standards-and-practices/core/version-control-safety.md)
  standards

A Windows workstation usually has a person on it. Treat their windows,
processes, files, and settings as theirs, and change them only with
evidence of ownership or explicit permission.
