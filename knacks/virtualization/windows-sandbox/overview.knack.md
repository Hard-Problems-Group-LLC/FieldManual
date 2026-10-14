# Windows Sandbox: Testing on a Fresh Windows

Reviewed: 2026-10-13. Field observations come from a Windows 11 host
(build 26300) with the Store-delivered Windows Sandbox app 0.8.107.0.
Sandbox behavior changes with Windows and app updates; recheck the cited
Microsoft pages and the upstream issue tracker before relying on
version-specific details.

## When to Load This Knack

Load this knack before using Windows Sandbox to test software on a
never-used Windows: an installer, a bootstrap or prerequisite script, a
first-run path, or a tool whose updater must never touch a real profile.
Load it also when a Sandbox launch fails or hangs, or when an agent must
drive the Sandbox unattended.

Companions:

- [Configuration and the `wsb` command](configuration.knack.md):
  `.wsb` elements, safe defaults for tests, logon commands, and the
  Windows 11 24H2 command-line interface;
- [Test drivers](test-drivers.knack.md): a
  self-closing guest driver, marker files, a host runner, timeouts, and
  evidence collection; and
- [What a fresh Windows lacks](fresh-install.knack.md):
  root certificates fetched on demand, missing runtimes and tools,
  PowerShell defaults, and an inventory script.

## Mental Model

Windows Sandbox is a disposable virtual machine that Windows builds from
the host's own installation. Microsoft describes it as pristine on every
launch: host software is absent, and closing it discards everything.

Consequences:

- The guest runs the host's Windows build. It answers "what happens on a
  clean install of this build," not "what happens on an older or
  different edition."
- Writes to a writable mapped folder land on the host and persist after
  the Sandbox closes. Everything else is discarded.
- Only one Sandbox runs at a time.
- The Sandbox window is a Remote Desktop client connected to the guest.
  Launch failures therefore appear in the host's RDP client event log.
- The guest user is `WDAGUtilityAccount`; the configured logon command
  runs as that user after sign-in.
- Networking, clipboard redirection, and audio input are on by default.
- Restarts started inside the guest keep its state on Windows 11 22H2
  and later; only closing the Sandbox discards it.

The Sandbox is an execution boundary for disposable work. It does not
replace unit tests or host runs with redirected profiles; see
[Windows agent isolation](../../sandboxing/windows-agents/overview.knack.md)
for choosing between home redirection, a separate account, the Sandbox,
and a virtual machine.

## What It Is For

Use the Sandbox when the question needs a Windows that has never been
used:

- behavior that depends on first use, such as the certificate store
  before any Windows TLS request, or a missing runtime;
- an installer's or bootstrap script's assumptions about what is
  already present; and
- a vendor updater, cleanup routine, or other housekeeping that must
  never run against a real profile.

Prefer a [virtual machine](../virtual-machine-control.knack.md)
with a checkpoint for repeated fresh-Windows runs, for other Windows
versions or editions, for state that must persist between runs, or on a
host affected by the launch defect below. It costs a one-time install,
and enabling a hypervisor feature is the operator's decision.

## The One-Good-Launch-per-Boot Defect

On hosts with both an integrated and a discrete GPU, the Sandbox may
give only one working launch per boot. Later launches show a black
window and then "The connection to the Windows Sandbox environment was
lost. Do you want to reconnect?" in a loop. Reconnecting does not help.

Upstream reports, both open and without a Microsoft response as of the
review date:

- [microsoft/Windows-Sandbox#103](https://github.com/microsoft/Windows-Sandbox/issues/103),
  "Starting Windows Sandbox a second time yields 'The connection to the
  Windows Sandbox environment was lost…'": the first launch after a
  restart works; several commenters report hybrid-GPU hosts.
- [microsoft/Windows-Sandbox#128](https://github.com/microsoft/Windows-Sandbox/issues/128),
  "The connection to the Windows Sandbox environment was disconnected…":
  app 0.8.107.0; the reporter estimates 90 percent of launches fail.

On the observed host, about 2 of 15 launches before a restart reached
logon. After a restart, the first launch of a bare configuration (one
empty mapped folder, one `cmd /c echo`) worked and the next two failed.
Disabling the virtual GPU changed nothing; pending updates, free disk
space, and leftover VMs were ruled out. Reported workarounds (pinning
the Sandbox app to one GPU under Settings > System > Display > Graphics,
disabling the integrated GPU, or restarting the Hyper-V Host Compute
Service) help some people some of the time. Changing GPU settings is the
operator's call.

Practical rule: restart, then spend the first launch on the real test,
not on a smoke test. Dry-run the driver on the host first, and plan a
fallback that verifies the fix on the host by forcing the failure.

Recognize a failed launch within half a minute from
`Microsoft-Windows-TerminalServices-RDPClient/Operational`. On the
observed host, every launch logged 1024 and 1025; working launches then
logged 1027 ("Connected to domain … with session 1") about three seconds
later, while failed launches logged no 1027 and ended with 1026 "RDP
ClientActiveX has been disconnected (Reason= 3)" 23 to 30 seconds after
1025. Reason 3 is
documented as a server-side disconnection, not an error code, so timing
and the missing 1027 are the signal.

```powershell
Get-WinEvent -FilterHashtable @{
  LogName   = 'Microsoft-Windows-TerminalServices-RDPClient/Operational'
  StartTime = (Get-Date).AddMinutes(-10); Id = 1024, 1025, 1026, 1027 } |
  Sort-Object TimeCreated | Format-Table TimeCreated, Id, Message -Wrap
```

## Workflow

1. **Enable once.** An administrator enables the optional feature
   `Containers-DisposableClientVM` and restarts. It needs Pro,
   Enterprise, or Education, hardware virtualization, and nested
   virtualization when the host is itself a VM. Log it as a request for
   the operator.
2. **Stage inputs.** Build one scratch folder holding only what the
   guest needs: a portable runtime, offline installers, and the code
   under test without `.git`, virtual environments, or local state. Never
   map a real checkout, profile folders, or anything holding credentials.
3. **Configure.** Write a `.wsb` that maps inputs read-only and one
   output folder writable, decides networking deliberately, and runs the
   driver as its logon command.
4. **Drive.** The guest driver writes a start marker, runs each step
   with a timeout, records exit codes and output, writes a done marker,
   and shuts the guest down.
5. **Launch and watch.** Confirm no Sandbox is running, launch the
   `.wsb`, poll the output folder, and check the RDP client log.
6. **Collect and wait.** Copy results out, then wait until the Sandbox
   processes have exited before the next launch.

## Sharp Edges

- Never force-kill `WindowsSandboxRemoteSession`, `WindowsSandboxServer`,
  or `vmmemWindowsSandbox`. The VM then lingers for minutes, and only
  one Sandbox can run at a time. Let the driver shut the guest down, or
  ask the operator to close the window.
- A writable mapping is a host write. Anything in the guest, including a
  misbehaving installer, can change or delete its contents.
- Write `.wsb` and driver files with a file-writing tool, not a shell
  here-document: backslash sequences in Windows paths can be rewritten
  (the `\b` in one `C:\sbx\bisect` path became a backspace). See
  [Git Bash here-documents](../../windows/shells/Git-Bash.knack.md).
- A `HostFolder` that does not exist stops the Sandbox from starting.
- `wsb.exe` is a per-user app execution alias. An agent that builds its
  path from a redirected `LOCALAPPDATA`, or whose `PATH` was rebuilt, may
  not find it; by name through the logon `PATH` it resolves.
- The guest has no Microsoft Store and no WinGet, and on Windows 11 24H2
  and later inbox Store apps such as Notepad and Terminal are absent.
- `Microsoft-Windows-VHDMP-Operational` "failed to create handle" events
  also appear on working launches; they are noise.

## Review Checklist

- Does the question need a never-used Windows, or would a unit test, a
  redirected-profile host run, or a VM answer it better?
- Was the host restarted, and is the first launch reserved for the real
  test?
- Are inputs read-only, is exactly one output folder writable, and is
  nothing secret mapped?
- Does the driver write start and done markers and shut the guest down?
- Does the runner check the RDP client log and wait for the Sandbox
  processes to exit without killing them?
- Are unverified fresh-Windows assumptions recorded as unknowns?

## Further Information

- Microsoft, [Windows Sandbox overview](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/)
- Microsoft, [Install Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-install)
- Microsoft, [Windows Sandbox architecture](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-architecture)
- Microsoft, [Use and configure Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)
- Microsoft, [Windows Sandbox versions](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-versions)
- Microsoft, [IMsTscAxEvents::OnDisconnected](https://learn.microsoft.com/en-us/windows/win32/termserv/imstscaxevents-ondisconnected),
  for the meaning of disconnect reason 3
- Upstream issue tracker:
  [microsoft/Windows-Sandbox issues](https://github.com/microsoft/Windows-Sandbox/issues)
- FieldManual: [Event Logs](../../windows/event-logs/overview.knack.md),
  [Processes and Files](../../windows/processes-and-files/overview.knack.md),
  and [VirtualBox Control](../virtualbox-control.knack/virtualbox-control.overview.knack.md)
