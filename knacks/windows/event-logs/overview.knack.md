# Windows Event Logs: What Just Happened

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when something happened on a Windows workstation and
nobody saw why: the machine restarted, an agent session died mid-task, a
notification sound played, an application closed, or hardware reported an
error. It explains how to ask the event logs precise questions from
PowerShell.

Companions:

- [Reboot forensics](reboots.knack.md): who or
  what restarted the machine, what Windows Update installed, and how to
  protect long agent runs; and
- [Background events](background-noise.knack.md):
  recurring events that are noisy or alarming but usually benign, such as
  Auto HDR notifications and corrected hardware errors.

## Mental Model

Windows records events in named logs. The classic logs are `System`,
`Application`, `Security`, and `Setup`; many components also write to
their own logs under Applications and Services Logs, such as
`Microsoft-Windows-WindowsUpdateClient/Operational`.

An event is identified by its **provider** and its **event ID**. IDs are
only meaningful within a provider: event 41 from
`Microsoft-Windows-Kernel-Power` and event 41 from another provider are
unrelated. Always filter on both.

Each event also has a level (1 critical, 2 error, 3 warning, 4
information), a creation time, structured event data, and a message
rendered from the provider's manifest on the local machine. Logs are
circular by default, so old events disappear as new ones arrive; capture
evidence early.

Reading most of `System` and `Application` works without elevation.
`Security` and some operational logs need an administrator.

## The Query Pattern

Use `Get-WinEvent -FilterHashtable`. The filter runs inside the event log
service, which is much faster than retrieving everything and piping it to
`Where-Object`.

```powershell
$since = (Get-Date).AddHours(-2)
Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    Level     = 1, 2, 3
    StartTime = $since
} -ErrorAction SilentlyContinue |
    Select-Object TimeCreated, ProviderName, Id, LevelDisplayName,
        @{ n = 'Message'; e = { ($_.Message -split "`r?`n")[0] } } |
    Format-Table -AutoSize -Wrap
```

Useful keys: `LogName`, `ProviderName`, `Id`, `Level`, `StartTime`,
`EndTime`, `Data`, and `SuppressHashFilter`, which excludes matches.
Wildcards work only in `LogName` and `ProviderName` values. Results arrive
newest first; `-MaxEvents` limits the count and `-Oldest` reverses the
order.

To build a timeline across sources, pass several hash tables and sort:

```powershell
$since = (Get-Date).AddHours(-6)
$filters = @(
    @{ LogName = 'System'; ProviderName = 'User32'; Id = 1074 }
    @{ LogName = 'System'; ProviderName = 'EventLog'; Id = 6005, 6006, 6008 }
    @{ LogName = 'System'; Id = 41, 109
       ProviderName = 'Microsoft-Windows-Kernel-Power' }
) | ForEach-Object { $_.StartTime = $since; $_ }
Get-WinEvent -FilterHashtable $filters -ErrorAction SilentlyContinue |
    Sort-Object TimeCreated |
    Format-Table TimeCreated, ProviderName, Id, Message -Wrap
```

## Find the Right IDs

The provider manifests installed on the machine are the authoritative
catalogue of what that build can log:

```powershell
(Get-WinEvent -ListProvider Microsoft-Windows-Kernel-Power).Events |
    Select-Object Id, Description
Get-WinEvent -ListProvider *Update* | Select-Object Name, LogLinks
(Get-WinEvent -ListLog System).ProviderNames
```

Microsoft documents some events individually, but many are documented only
by their manifest text. Prefer the local manifest over a remembered ID.

## Read Structured Event Data

Messages are for people; event data is for code. Read named fields through
the event's XML:

```powershell
$e = Get-WinEvent -FilterHashtable @{
    LogName = 'System'; ProviderName = 'Microsoft-Windows-Kernel-Power'; Id = 41
} -MaxEvents 1 -ErrorAction SilentlyContinue
if ($e) {
    ([xml]$e.ToXml()).Event.EventData.Data |
        ForEach-Object { '{0} = {1}' -f $_.Name, $_.'#text' }
}
```

`$e.Properties` gives the same values by position.

## Without PowerShell

`wevtutil` queries the same service with XPath:

```text
wevtutil qe System /q:"*[System[(EventID=1074)]]" /c:5 /rd:true /f:text
```

From Git Bash, Windows-style switches such as `/q:` are rewritten as paths
unless conversion is disabled, for example with `MSYS_NO_PATHCONV=1`; see
the [Git Bash companion](../shells/Git-Bash.knack.md).
Event Viewer (`eventvwr.msc`) can build the same filters interactively and
export them as XML for `Get-WinEvent -FilterXml`.

## Sharp Edges

- When nothing matches, `Get-WinEvent` writes the error "No events were
  found that match the specified selection criteria." Treat that as an
  empty result, not a failure. `-ErrorAction SilentlyContinue` hides the
  message but still leaves `$?` false, so a harness that runs
  `pwsh -Command` reports exit code 1 when the query is the last
  statement. Wrap the query instead:

  ```powershell
  $events = try {
      Get-WinEvent -FilterHashtable $filter -ErrorAction Stop
  } catch [System.Exception] {
      if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') { @() }
      else { throw }
  }
  "events: $(@($events).Count)"
  ```
- `TimeCreated` is local time. Some messages, such as the Kernel-General
  start and shutdown messages, state UTC system time. Convert to one zone
  before reading a timeline.
- A message can contain an unresolved `%1` placeholder when the provider's
  message resources do not supply the insertion. Read the event data
  instead.
- The `*-EventLog` cmdlets, including `Get-EventLog`, are absent from
  PowerShell 7; use `Get-WinEvent`.
- An absent event proves little when the log has wrapped. Check the oldest
  record's time with `Get-WinEvent -LogName System -Oldest -MaxEvents 1`.
- Event logs can contain user names, computer names, paths, and command
  lines. Redact them before pasting evidence into tickets or shared
  documents.

## Review Checklist

- Is every filter scoped by log, provider, ID, and time window?
- Were empty results distinguished from errors and from wrapped logs?
- Are times in a single, stated time zone?
- Was the event's meaning checked against the local manifest or a
  Microsoft reference, not only against memory?
- Was sensitive detail removed before the evidence left the machine?

## Further Information

- Microsoft, [Get-WinEvent](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent)
- Microsoft, [Creating Get-WinEvent queries with FilterHashtable](https://learn.microsoft.com/en-us/powershell/scripting/samples/creating-get-winevent-queries-with-filterhashtable)
- Microsoft, [wevtutil](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil)
- Microsoft, [Differences between Windows PowerShell 5.1 and PowerShell 7.x](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell)
