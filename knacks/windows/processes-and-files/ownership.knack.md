# Processes: Launch, Find, Verify, Stop

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when an agent starts programs on Windows and must later
find or stop exactly those programs, without touching the operator's. Read
the [processes and files overview](overview.knack.md)
first. Examples use PowerShell; the names `example-app.exe` and
`run-42` are fictional.

## Identity Is ID Plus Creation Time

Microsoft's `Win32_Process` documentation warns that process IDs are reused
after a process ends, so an ID alone can later name an unrelated program.
The same applies to `ParentProcessId`: the parent may have exited and its
ID been reused. Pair every recorded ID with the process creation time, and
compare both before acting.

## Launch and Record

```powershell
$runDir = Join-Path $repo '.local\tmp\run-42'
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$p = Start-Process -FilePath $exe -PassThru -WorkingDirectory $runDir `
    -ArgumentList @('--data-dir', "`"$runDir\data`"", '--log', "`"$runDir\app.log`"")

[pscustomobject]@{
    Id        = $p.Id
    StartTime = $p.StartTime.ToString('o')
    Exe       = $exe
    Marker    = $runDir
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runDir 'process.json')
```

`Start-Process -ArgumentList` joins its values into one command line, so
values containing spaces need their own quotation marks, as above. A unique
folder in the command line, such as the run directory, later identifies the
process unambiguously.

## Find by Command Line

`Win32_Process` exposes the full command line, creation time, and parent
in both Windows PowerShell 5.1 and PowerShell 7:

```powershell
Get-CimInstance Win32_Process -Filter "Name = 'example-app.exe'" |
    Where-Object { $_.CommandLine -like '*\.local\tmp\run-42*' } |
    Select-Object ProcessId, ParentProcessId, CreationDate, CommandLine
```

- Filter by `Name` in WQL and by command line in PowerShell. WQL string
  literals need escaped backslashes, which makes path matching in the
  filter error-prone.
- `CommandLine` may be empty for processes the caller lacks rights to
  inspect, such as elevated ones. Treat an empty command line as "not
  proven mine".
- PowerShell 7 also adds a `CommandLine` property to `Get-Process`
  results on Windows.

## Verify Before Stopping

```powershell
function Get-RecordedProcess {
    param([string]$RecordPath)
    $rec = Get-Content -Raw -LiteralPath $RecordPath | ConvertFrom-Json
    $cim = Get-CimInstance Win32_Process -Filter "ProcessId = $($rec.Id)"
    if (-not $cim) { return $null }                      # already gone
    $recorded = [datetime]$rec.StartTime   # string in 5.1, DateTime in 7
    $delta = [math]::Abs(($cim.CreationDate - $recorded).TotalSeconds)
    if ($delta -gt 1) { return $null }                   # ID was reused
    if ($cim.CommandLine -notlike "*$($rec.Marker)*") { return $null }
    return $cim
}
```

A `$null` result means "do not touch": the process ended, or the ID now
belongs to something else.

When no record exists, for example after an interrupted session, fall back
to the marker: list processes whose command line contains the run's unique
folder, and if several match, act on the newest `CreationDate` only after
confirming the others are stale copies of the same run. Never fall back to
the image name.

## Stop Gently, Then Firmly

1. **Ask it to close.** For a program with a window,
   `(Get-Process -Id $id).CloseMainWindow()` sends a close request, as if
   the user clicked the close button. The program may save state, or may
   show a prompt that never gets answered.
2. **Wait with a limit.** `(Get-Process -Id $id).WaitForExit(15000)`
   returns `$false` if it is still running after 15 seconds.
3. **Force the tree.** `taskkill /PID $id /T /F` ends the process and the
   child processes it started. `Stop-Process -Id $id` ends one process
   without asking it to save anything.

`taskkill` without `/F` asks rather than forces. From Git Bash, write
`taskkill //PID 1234 //T //F` or disable MSYS path conversion; otherwise
`/PID` can be rewritten into a file path. See the
[Git Bash companion](../shells/Git-Bash.knack.md).

## Child Processes

Programs often start helpers: shells, compilers, crash reporters,
`conhost.exe`, or SSH clients. List them through the parent ID, guarding
against reuse by requiring that each child started after its parent:

```powershell
$parent = Get-RecordedProcess -RecordPath (Join-Path $runDir 'process.json')
if ($parent) {
    Get-CimInstance Win32_Process -Filter "ParentProcessId = $($parent.ProcessId)" |
        Where-Object { $_.CreationDate -ge $parent.CreationDate } |
        Select-Object ProcessId, Name, CreationDate
}
```

`taskkill /T` stops the tree as it exists at that moment. A helper that was
re-parented or detached earlier is not part of the tree; check for it by
command line afterwards.

Two launch patterns leave orphans behind:

- Killing the `cmd.exe` that runs a `.cmd` or `.bat` shim does not stop
  the program the shim started. Stop the tree, or launch the real
  executable directly.
- A launcher written in Python or another runtime keeps running beside
  its child, because Windows has no `exec`. Killing the launcher leaves the
  child running unless the launcher placed it in a kill-on-close job
  object; see
  [porting processes](../porting-cli-tools/processes.Python.knack.md).

## What Not to Do

- `taskkill /IM example-app.exe /F` and `Stop-Process -Name example-app`
  stop every instance, including the operator's.
- Window-title filters such as `taskkill /FI "WINDOWTITLE eq ..."` are
  name-based in disguise.
- Killing `explorer.exe`, a browser, an editor, or a terminal to free a
  file or reset state affects the person using the machine.
- Running agent work elevated to see more processes expands what a mistake
  can damage. Stay unelevated unless the operator decides otherwise.

## Waiting for Readiness

A process existing is not the same as a program being ready. Wait for a
positive signal the program emits, such as a line in its log file, with a
time limit. The
[desktop automation](../desktop-automation/overview.knack.md)
knack gives a polling pattern.

## Review Checklist

- Was the ID and creation time recorded at launch?
- Does the command line contain a marker unique to this run?
- Is every stop preceded by a fresh identity check?
- Is a graceful close tried before forcing, with a time limit?
- Are helpers found by parent and creation time, then checked by command
  line after the tree is stopped?
- Is any selection made by image name or window title alone?

## Further Information

- Microsoft, [Win32_Process class](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process)
- Microsoft, [Get-CimInstance](https://learn.microsoft.com/en-us/powershell/module/cimcmdlets/get-ciminstance)
- Microsoft, [Start-Process](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/start-process)
- Microsoft, [Stop-Process](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/stop-process)
- Microsoft, [taskkill](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/taskkill)
- .NET, [Process.CloseMainWindow](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.closemainwindow)
- .NET, [Process.WaitForExit](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.waitforexit)
