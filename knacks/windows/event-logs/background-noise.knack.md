# Background Events: Notification Noise and Corrected Errors

Reviewed: 2026-10-14

## When to Load This Knack

Load this companion when automated work on a Windows workstation coincides
with unexplained notification sounds, or when recurring warnings in the
`System` log look alarming. Read the
[event logs overview](overview.knack.md) first.

## Baseline Before Diagnosing

Most busy workstations log a steady background of warnings. Before
treating one as the cause of a problem, compare it with the machine's
normal rate:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'; Level = 1, 2, 3; StartTime = (Get-Date).AddDays(-7)
} -ErrorAction SilentlyContinue |
    Group-Object ProviderName, Id -NoElement |
    Sort-Object Count -Descending |
    Select-Object -First 20 Count, Name
```

An event that has appeared at a steady rate for weeks is rarely the
explanation for today's failure. A new event, or a sudden change in rate,
deserves attention.

## Auto HDR Notifications During Automated Game Launches

Auto HDR upgrades the rendering of qualifying DirectX games from standard
to high dynamic range on HDR-capable displays. When it applies to a game,
Windows shows a notification, with the default notification sound, and
records an event:

| Field | Value |
| --- | --- |
| Log | `System` |
| Provider | `Display` |
| ID | `4125` |
| Message | `Good news—%1 has been enhanced for a brighter and more detailed picture. You can turn off Auto HDR any time in Settings.` |

The `%1` placeholder was not filled in on the build where this was
observed, so the message does not name the game. The event was observed on
each launch of a qualifying game. Automated test harnesses that launch a
game repeatedly therefore produce a stream of notifications and sounds,
which distracts anyone sharing the machine and can be mistaken for
warnings.

Confirm the cause by counting the events:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'; ProviderName = 'Display'; Id = 4125
    StartTime = (Get-Date).AddHours(-4)
} -ErrorAction SilentlyContinue |
    Group-Object { $_.TimeCreated.ToString('yyyy-MM-dd HH:00') } -NoElement
```

The same launches can disturb the display itself. Observed once on a
television used as the monitor over HDMI: the set rebooted its own
operating system (it showed its vendor boot logo on power-up rather than
waking from standby) during an automated game launch, while the PC logged
nothing but event 4125. That was one reboot in about a hundred launches,
so the trigger is uncertain: the game's start-up mode change, the HDR
switch, or the refresh rate. After such a reboot, check the desktop's
resolution and refresh rate, because the set may renegotiate a different
mode (an unusual 24 Hz desktop was seen afterwards). On machines that drive
a television, prefer the first remedy below, launch test runs windowed,
and do not leave long unattended runs on a display that has done this.

Remedies, in order of preference; all are the operator's choice:

1. **Turn Auto HDR off for the game under test** in Settings, System,
   Display, Graphics, by expanding that application's entry. A per-app
   setting overrides the system-wide one, so the operator's other games
   keep Auto HDR.
2. **Silence the notification sender** in Settings, System,
   Notifications. The sender appears in that list after it has notified at
   least once.
3. **Use Do Not Disturb** during test runs, manually or with an automatic
   rule such as "when playing a game" or "when using an app in full-screen
   mode".
4. **Turn Auto HDR off system-wide** in the display's HDR settings.

Do not change these settings from an agent without the operator's
agreement; they belong to the person who uses the display.

## WHEA-Logger 17: Corrected Hardware Errors

| Field | Value |
| --- | --- |
| Log | `System` |
| Provider | `Microsoft-Windows-WHEA-Logger` |
| ID | `17` |
| Message | `A corrected hardware error has occurred.` |

The event data typically names the component, for example
`PCI Express Root Port`, the error source, such as Advanced Error
Reporting (PCI Express), and the devices involved by PCI vendor and device
identifiers.

The Windows Hardware Error Architecture (WHEA) records hardware errors in
the system event log. A *corrected* error is one the hardware or firmware
detected and corrected; Microsoft's WHEA definitions describe corrected
platform errors and corrected machine checks as nonfatal. A rare WHEA 17
is usually benign. Watch for:

- a rising rate or bursts of many events in a short period;
- the same device appearing repeatedly;
- uncorrected-error events or stop errors at the same time, such as bug
  check 0x124, `WHEA_UNCORRECTABLE_ERROR`; and
- symptoms on the named device, such as storage or graphics faults.

Count by day and device:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'; ProviderName = 'Microsoft-Windows-WHEA-Logger'; Id = 17
    StartTime = (Get-Date).AddDays(-30)
} -ErrorAction SilentlyContinue |
    Group-Object { $_.TimeCreated.ToString('yyyy-MM-dd') } -NoElement |
    Sort-Object Name
```

Map a `PCI\VEN_xxxx&DEV_yyyy` identifier from the message to a device
name:

```powershell
Get-PnpDevice | Where-Object InstanceId -like 'PCI\VEN_xxxx&DEV_yyyy*' |
    Select-Object FriendlyName, Class, Status
```

Firmware updates, driver updates, and physical inspection are hardware
decisions for whoever maintains the machine, not tasks for an agent.
Record the counts and the device, and report them.

## Windows Sandbox Launches

Windows Sandbox sessions connect through the Remote Desktop client, so its
operational log, `Microsoft-Windows-TerminalServices-RDPClient/Operational`,
records each attempt. The provider's manifest describes event 1024 as an
attempt to connect, 1025 as connected, 1026 as disconnected with a reason
code, and 1027 as connected to a domain with a session. On one observed
host, working launches logged 1027 a few seconds after 1025, while failed
launches logged no 1027 and ended with 1026 within about half a minute.
"Failed to create handle" events in `Microsoft-Windows-VHDMP-Operational`
also appear on good launches, so they are noise for this purpose:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName   = 'Microsoft-Windows-TerminalServices-RDPClient/Operational'
    Id        = 1024, 1025, 1026, 1027
    StartTime = (Get-Date).AddMinutes(-10)
} -ErrorAction SilentlyContinue | Format-Table TimeCreated, Id, Message -Wrap
```

The exact timings, the launch defect, and failure handling belong to the
[Windows Sandbox](../../virtualization/windows-sandbox/overview.knack.md)
knack.

## Sharp Edges

- Not every notification writes an event. Absence of an event does not
  rule out a toast, and a sound may come from an application.
- Display and graphics settings, notification settings, and Do Not Disturb
  are per-user preferences. Changing them affects the person at the
  machine.
- Event text and event IDs for these providers can change between Windows
  builds. Confirm on the machine before relying on them in automation.
- WHEA event data identifies specific hardware. Treat it as machine
  inventory and redact it before sharing outside the team.

## Further Information

- Microsoft Support, [Use Auto HDR for better gaming in Windows](https://support.microsoft.com/en-us/windows/hardware/display-graphics/use-auto-hdr-for-better-gaming-in-windows)
- Microsoft DirectX blog, [Navigating the redesigned graphics settings page](https://devblogs.microsoft.com/directx/navigating-the-redesigned-graphics-settings-page)
  (per-app Auto HDR overrides)
- Microsoft Support, [Notifications and Do Not Disturb in Windows](https://support.microsoft.com/en-us/windows/experience/notifications-and-do-not-disturb-in-windows)
- Microsoft, [Windows Hardware Error Architecture definitions](https://learn.microsoft.com/en-us/windows-hardware/drivers/whea/windows-hardware-error-architecture-definitions)
- Microsoft, [Bug check 0x124: WHEA_UNCORRECTABLE_ERROR](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/bug-check-0x124---whea-uncorrectable-error)
- Microsoft, [Get-PnpDevice](https://learn.microsoft.com/en-us/powershell/module/pnpdevice/get-pnpdevice)
