# Processes and Files on a Shared Workstation

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when an agent on a Windows workstation starts or stops
programs, runs a second copy of an application, links a development folder
into an application's folder, copies large trees, or cannot delete a file.
The rules matter most when a person uses the same machine at the same
time.

Companions:

- [Processes](ownership.knack.md): launching,
  finding processes by command line, verifying identity, and stopping
  process trees; and
- [Links and copies](links-and-copies.knack.md):
  junctions, symbolic links, safe verification and removal, and
  `robocopy`.

## Mental Model: Own Only What You Start

A workstation holds two kinds of objects: those the agent created during
its task, and everything else. Everything else belongs to the operator:
their running applications and windows, unsaved documents, browser
profiles, game saves, caches, and configuration.

The agent may change or stop only objects it can prove it created, and it
proves ownership with evidence, not names:

- for a process, the process ID **and** its creation time, recorded at
  launch, plus a command line that only this task would use;
- for a file or folder, a path inside the task's own scratch area or a
  path the task created and recorded; and
- for a link, its link type and target, checked immediately before any
  change.

Names are not evidence. `python.exe`, `node.exe`, `git.exe`, and an
application's own executable may each have several instances, some of
them the operator's.

## Processes

- Launch programs so that the process ID and start time are captured, and
  write them to the task's scratch area.
- Find processes by command line through `Win32_Process`, not by image
  name alone.
- Before stopping a process, confirm that its ID and creation time still
  match the record; Windows reuses process IDs.
- Ask a program to close before forcing it, and stop child processes with
  their parent when the program spawns helpers.
- Never use name-based termination such as `taskkill /IM` or
  `Stop-Process -Name` on a shared machine.

## People Share the Desktop

When a person may be using the machine:

- do not close, minimize, move, or kill a window the task did not open;
  it may hold unsaved work;
- avoid stealing focus repeatedly, and do not type into whatever window
  happens to be active;
- announce long-running or noisy work, such as repeated application
  launches, and any extra window, before starting it;
- after each launch or relaunch, count the task's own instances by their
  marker and confirm the expected number, because a background run or an
  earlier attempt is easily left behind; and
- leave the desktop as you found it.

The [desktop automation](../desktop-automation/overview.knack.md)
knack covers windows, screen capture, and readiness in detail.

## Second Instances

To test an application while the operator uses the same application, run
a separate instance with its own data and configuration location. Prefer
the application's documented option for a data or configuration directory.
Overriding `APPDATA` alone works only for programs that read that
variable. Programs that ask Windows for known folders derive AppData,
LocalAppData, Documents, and Desktop from the process's `USERPROFILE`, so
a redirected `USERPROFILE` moves those too, while the profile folder
itself, as registered for the account, stays real. Agent harnesses that
redirect the profile therefore change where every child application keeps
its data; see
[Windows agent isolation](../../sandboxing/windows-agents/overview.knack.md).

Some applications allow a single instance per user and either refuse a
second one or hand the request to the running instance. Never close the
operator's instance to make room; ask.

## Locked Files

Windows refuses to delete or replace a file another process has open
without sharing. Typical holders are a running application using its own
files, a browser using its profile folder, a build output loaded by a
running program, and brief scans by security or indexing software.

When deletion fails with a sharing violation:

1. identify the holder, for example with Resource Monitor's associated
   handles search or the Sysinternals Handle tool, which needs
   administrator rights;
2. if the task started the holder, stop it by recorded ID and retry;
3. otherwise wait, ask the operator to close the program, or defer the
   deletion until after a restart; and
4. never terminate an unknown holder to free a file.

## Links Between Folders

A directory **junction** lets an application see a development folder,
such as a plugin built in a repository, without copying it after every
build. Ordinary users can create junctions to local folders. Directory
**symbolic links** need administrator rights or Developer Mode.

Before creating, replacing, or deleting anything at the link path, check
whether it is already a link and where it points. A real folder at that
path may be the operator's data. Remove a link by removing the link
object, never by deleting recursively through it.

## Copies

`robocopy` is the dependable tool for large trees. Exclude junctions with
`/XJ`, exclude heavy caches and build folders explicitly, set bounded
retries, and read its exit code correctly: values of 8 and above mean
failure. Treat `/MIR` and `/PURGE` as deletions and preview them with `/L`.

## Scratch Files

Keep the task's temporary files in the project's ignored local area, such
as a uniquely named folder under `.local/tmp/`, as FieldManual's
[local operator state](../../../standards-and-practices/core/local-operator-state.md)
standard describes. Remove only what the task created. Do not scatter
files in the user profile, the desktop, or shared temporary folders where
ownership becomes unclear.

## Review Checklist

- Is every process the task will stop identified by recorded ID and
  creation time?
- Does any command select processes or windows by name alone?
- Could a person be using the window or application about to change?
- Was a link's type and target checked immediately before changing it?
- Do copy commands exclude junctions, bound retries, and check exit codes?
- Are all scratch files inside the project's ignored local area?

## Further Information

- Microsoft, [Win32_Process class](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process)
- Microsoft, [taskkill](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/taskkill)
- Microsoft, [Hard links and junctions](https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions)
- Microsoft, [robocopy](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy)
- Microsoft Sysinternals, [Handle](https://learn.microsoft.com/en-us/sysinternals/downloads/handle)
- FieldManual, [session and project boundaries](../../../standards-and-practices/core/session-and-project-boundaries.md)
