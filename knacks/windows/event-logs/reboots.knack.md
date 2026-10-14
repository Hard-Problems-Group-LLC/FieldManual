# Reboot Forensics and Windows Update

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when a Windows workstation restarted or shut down and
you need to know who or what initiated it, whether it was clean, what
Windows Update installed around it, and how to keep it from ending a long
agent run. Read the [event logs overview](overview.knack.md)
first for the query pattern.

## The Events

All of these are in the `System` log. Message texts below were taken from
the provider manifests on a current Windows 11 build and from Microsoft's
troubleshooting article on event 41; confirm them locally with
`(Get-WinEvent -ListProvider <provider>).Events`.

| Provider | ID | Meaning |
| --- | --- | --- |
| `User32` | 1074 | A process initiated a restart or shutdown, with user, reason, and type |
| `EventLog` | 6006 | The event log service stopped: part of a clean shutdown |
| `Microsoft-Windows-Kernel-Power` | 109 | The kernel power manager initiated a shutdown transition |
| `Microsoft-Windows-Kernel-General` | 13 | The operating system is shutting down, with UTC time |
| `Microsoft-Windows-Kernel-General` | 12 | The operating system started, with UTC time |
| `EventLog` | 6005 | The event log service started: early in boot |
| `EventLog` | 6008 | The previous shutdown was unexpected |
| `Microsoft-Windows-Kernel-Power` | 41 | The system rebooted without cleanly shutting down first |

A clean, planned restart usually reads, in order: 1074, then 6006, 109,
and 13, then after boot 12 and 6005. A dirty restart lacks 1074 and 6006
and is followed at the next boot by 41 and 6008.

1074 can precede the actual shutdown by minutes while applications close
or updates are prepared. Servicing can also restart the machine more than
once in a row.

## Read Event 1074

Its event data names the initiator:

| Field | Content |
| --- | --- |
| `param1` | Initiating process, such as `C:\Windows\Explorer.EXE` |
| `param3` | Reason text, such as `Operating System: Service pack (Planned)` |
| `param4` | Reason code in hexadecimal |
| `param5` | Shutdown type, such as `restart` |
| `param7` | Account on whose behalf it ran |

Patterns observed on Windows 11:

- `Explorer.EXE` on behalf of a person's account with reason
  `Other (Planned)`: someone chose Restart from the Start menu.
- An update-orchestrator worker such as `MoUsoCoreWorker.exe` (seen under
  `C:\Windows\uus\`), or `TrustedInstaller.exe`, on behalf of
  `NT AUTHORITY\SYSTEM`, with an `Operating System:` reason: Windows
  servicing restarted the machine.
- `shutdown.exe` with a custom comment: a script or person ran
  `shutdown /r`.

Process names vary between builds; the account and the reason code are
the stable evidence. Reason codes combine flags from Microsoft's shutdown
reason table:

| Code | Decoded | Displayed reason |
| --- | --- | --- |
| `0x80000000` | Planned, major Other | `Other (Planned)` |
| `0x80020003` | Planned, Operating System, Upgrade | `Operating System: Upgrade (Planned)` |
| `0x80020010` | Planned, Operating System, Service pack | `Operating System: Service pack (Planned)` |
| `0x80020012` | Planned, Operating System, Security fix | `Operating System: Security fix (Planned)` |

## Read Events 41 and 6008

Event 41 is written at the boot after an unclean stop. Its event data
narrows the cause:

- non-zero `BugcheckCode`: a stop error; the value is decimal, so convert
  it to hexadecimal before looking it up;
- non-zero `PowerButtonTimestamp`: the power button was held;
- all zero: power loss, a hard hang, or failure to write crash data.
  Microsoft suggests also checking `volmgr` event 46, which reports that
  crash-dump initialization failed.

6008 records when the unexpected shutdown happened. Look at both logs for
anything unusual just before that time.

## What Windows Update Installed

Provider `Microsoft-Windows-WindowsUpdateClient` writes to `System` and to
its own operational log:

| ID | Manifest text, abbreviated |
| --- | --- |
| 44 | Windows Update started downloading an update |
| 43 | Installation Started: Windows has started installing the following update |
| 19 | Installation Successful: Windows successfully installed the following update |
| 20 | Installation Failure: Windows failed to install the following update with error |

The message names the update, often with a KB number. An update's 19 event
can appear after the restart that finished it, so read 43, 1074, the
restart, and 19 together.

## Timeline Recipe

```powershell
param([datetime]$Around = (Get-Date), [int]$Hours = 2)

function New-SystemFilter([string]$Provider, [int[]]$Ids) {
    @{
        LogName      = 'System'
        ProviderName = $Provider
        Id           = $Ids
        StartTime    = $Around.AddHours(-$Hours)
        EndTime      = $Around.AddHours($Hours)
    }
}

$filters = @(
    New-SystemFilter 'User32' 1074
    New-SystemFilter 'EventLog' 6005, 6006, 6008
    New-SystemFilter 'Microsoft-Windows-Kernel-Power' 41, 109
    New-SystemFilter 'Microsoft-Windows-Kernel-General' 12, 13
    New-SystemFilter 'Microsoft-Windows-WindowsUpdateClient' 19, 20, 43, 44
)
Get-WinEvent -FilterHashtable $filters -ErrorAction SilentlyContinue |
    Sort-Object TimeCreated |
    ForEach-Object {
        $first = ($_.Message -split "`r?`n")[0]
        '{0:yyyy-MM-dd HH:mm:ss}  {1,-40} {2,5}  {3}' -f
            $_.TimeCreated, $_.ProviderName, $_.Id, $first
    }
```

Save it as a script file and run it with `pwsh -NoProfile -File`. Pass the
approximate time the session died as `-Around`.

## Protect Long Agent Runs

Windows Update restarts a device outside its **active hours**. By default
active hours run from 8 AM to 5 PM, and current versions allow a range of
up to 18 hours, so some part of every day remains eligible for an
automatic restart. Evening and overnight agent runs fall in exactly that
part under the default setting.

Before a long unattended run, the operator can:

1. install pending updates and restart first, at a convenient time;
2. set active hours to cover the run, under Settings, Windows Update,
   Advanced options, Active hours; and
3. for runs longer than any active-hours window, pause updates under
   Settings, Windows Update. Pauses are limited in length, and once the
   limit is reached updates must be installed before pausing again.

Pausing updates delays security fixes. Keep pauses short and resume them
when the run ends. On organization-managed devices, Group Policy or mobile
device management can override these settings; ask the administrator.

Inside the run, assume a restart can still happen:

- commit and push each verified step to a feature branch; see
  [Git for agents](../git/overview.knack.md);
- write progress notes that a fresh session can resume from; and
- make long steps idempotent so a restarted run can repeat them safely.

## Sharp Edges

- No 1074 does not prove a crash if the log wrapped; check the oldest
  record's time.
- 1074 records intent. Confirm the restart actually happened with 6006,
  13, 12, and 6005.
- Kernel-General messages state UTC; `TimeCreated` is local time. Their
  date text can contain invisible left-to-right marks (U+200E), which
  appear as `?` through a legacy console code page. Parse `TimeCreated`
  or the event data instead of the message.
- Agents cannot see restart notifications on the desktop. Notification
  settings are not a substitute for active hours or a pause.

## Further Information

- Microsoft, [Event ID 41: The system has rebooted without cleanly shutting down first](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/event-id-41-restart)
  (also describes 1074, 6006, and 6008)
- Microsoft, [System shutdown reason codes](https://learn.microsoft.com/en-us/windows/win32/shutdown/system-shutdown-reason-codes)
- Microsoft, [Manage device restarts after updates](https://learn.microsoft.com/en-us/windows/deployment/update/waas-restart)
- Microsoft, [Windows Update: FAQ](https://support.microsoft.com/en-us/windows/windows-update-faq-8a903416-6f45-0718-f5c7-375e92dddeb2)
- Microsoft, [Event ID 20: WUA update installation](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-r2-and-2008/cc735642(v=ws.10))
  (archived; documents the WindowsUpdateClient installation events)
- Microsoft, [Get-WinEvent](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent)
