# Windows Sandbox: Self-Closing Test Drivers

Reviewed: 2026-10-13. The driver below ran on a host under CPython 3.12,
where its shutdown guard held. The runner was parse-checked under
Windows PowerShell 5.1 and PowerShell 7.6, and its launch-state function
was checked against a real RDP client log. Neither was run against a
guest for this review. Read the [overview](overview.knack.md)
and the
[configuration companion](configuration.knack.md)
first.

## When to Load This Knack

Load this companion when a Sandbox run must happen without a person
watching: an agent launches it, the guest does the work and closes
itself, and the host decides from files and logs what happened.

## Shape of a Run

1. The host stages an input folder and an empty output folder, then
   checks that no Sandbox is running.
2. The host launches the `.wsb` and notes the time.
3. The guest signs in and runs the logon command, which starts the
   driver.
4. The driver writes `started`, runs each step with a timeout, records
   results after every step, writes `done`, and shuts the guest down.
5. The host polls for the markers, watches the RDP client log for a
   failed launch, collects results, and waits for the Sandbox processes
   to exit.

Every handoff is a file in the writable mapping, because the logon
command's console is invisible and the preview `wsb exec` returns no
output.

## Marker Contract

| File in the output folder | Written | Its absence means |
| --- | --- | --- |
| `started` | First thing the driver does | The launch failed, logon never finished, or the logon command could not start the driver |
| `<step>.out.txt`, `<step>.err.txt` | Around each step | The step never began |
| `results.json` | After each step, rewritten whole | No step finished |
| `done` | In a `finally` block, pass or fail | The driver hung, crashed hard, or the guest died |

Create the output folder empty for every run, with a new name per run,
so stale markers can never be mistaken for fresh ones. "Never started"
must be distinguishable from "started and failed."

## Guest Driver

A Python driver, run by a portable interpreter carried in the inputs:

```python
"""Self-closing Windows Sandbox driver: run steps, record, shut down."""
import json
import os
import pathlib
import subprocess
import sys
import time

IN = pathlib.Path(os.environ.get("SBX_IN", r"C:\sbx\in"))     # read-only
OUT = pathlib.Path(os.environ.get("SBX_OUT", r"C:\sbx\out"))  # writable
STEP_TIMEOUT_SECONDS = 900
# Shut down only inside Windows Sandbox, so a dry run never stops a host.
IN_SANDBOX = os.environ.get("USERNAME", "").lower() == "wdagutilityaccount"
PS = [r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
      "-NoLogo", "-NoProfile", "-NonInteractive",
      "-ExecutionPolicy", "Bypass", "-File"]
STEPS = [
    ("01-inventory", PS + [str(IN / "inventory.ps1")]),
    ("02-install", [sys.executable, "-I", str(IN / "app" / "install.py")]),
    ("03-inventory-after", PS + [str(IN / "inventory.ps1")]),
]


def write_atomic(path, text):
    """Write text so the host never reads a half-written file."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def run_step(name, argv):
    """Run one step with output in files, never pipes; return a record."""
    began = time.monotonic()
    with open(OUT / (name + ".out.txt"), "wb") as out, \
            open(OUT / (name + ".err.txt"), "wb") as err:
        try:
            code = subprocess.run(argv, stdin=subprocess.DEVNULL,
                                  stdout=out, stderr=err,
                                  timeout=STEP_TIMEOUT_SECONDS).returncode
        except subprocess.TimeoutExpired:
            code = "timeout"
        except OSError as exc:
            err.write(repr(exc).encode("utf-8"))
            code = "could-not-start"
    return {"step": name, "exit": code,
            "seconds": round(time.monotonic() - began, 1)}


def main():
    """Mark the start, run every step, then mark done and shut down."""
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "done").exists():
        return  # A restart re-ran the logon command; do nothing twice.
    write_atomic(OUT / "started", time.strftime("%Y-%m-%dT%H:%M:%S"))
    results = []
    try:
        for name, argv in STEPS:
            results.append(run_step(name, argv))
            write_atomic(OUT / "results.json", json.dumps(results, indent=2))
    except Exception as exc:  # Record anything, then still finish.
        results.append({"step": "driver", "exit": "exception",
                        "error": repr(exc)})
        write_atomic(OUT / "results.json", json.dumps(results, indent=2))
    finally:
        write_atomic(OUT / "done", time.strftime("%Y-%m-%dT%H:%M:%S"))
        if IN_SANDBOX:
            subprocess.run(["shutdown", "/s", "/t", "5"], check=False)


if __name__ == "__main__":
    main()
```

Design points:

- **Files, not pipes.** A step's output goes straight to files. On a
  timeout, Python kills the direct child, but a grandchild holding an
  inherited pipe could keep the driver waiting; files avoid that.
- **Per-step timeouts.** A hung installer becomes a recorded `timeout`,
  and the driver moves on to `done`.
- **Atomic writes.** `os.replace` gives a reader a whole file or the
  previous one. On Windows, replacing a file that another process holds
  open can fail, so the host tests markers for existence and reads
  `results.json` only after `done`.
- **Guarded shutdown.** The driver shuts down only when it runs as
  `WDAGUtilityAccount`, the guest user, so a dry run on a host records
  everything and exits. Never replace the guard with a command-line
  flag that a hurried rerun could omit.
- **Idempotence.** Restarts inside the guest keep state; an existing
  `done` marker stops a second pass.
- **Full paths.** The driver names Windows PowerShell by path and runs
  the code under test with the same isolated interpreter.

The inventory step is the script in
[What a fresh Windows lacks](fresh-install.knack.md);
running it before and after the step under test shows what the step
changed. A PowerShell or batch driver can follow the same contract.

## Host Runner

```powershell
param(
    [Parameter(Mandatory)] [string] $WsbFile,
    [Parameter(Mandatory)] [string] $OutFolder,  # host side of C:\sbx\out
    [int] $StartMinutes = 5,
    [int] $RunMinutes = 60
)
$SessionNames = 'WindowsSandboxRemoteSession', 'WindowsSandboxServer',
                'vmmemWindowsSandbox'

function Get-SandboxProcess {
    Get-Process -Name $SessionNames -ErrorAction SilentlyContinue
}

function Get-LaunchState([datetime] $Since) {
    $log = 'Microsoft-Windows-TerminalServices-RDPClient/Operational'
    $ids = @(Get-WinEvent -ErrorAction SilentlyContinue -FilterHashtable @{
        LogName = $log; StartTime = $Since; Id = 1024, 1025, 1026, 1027 } |
        ForEach-Object Id)
    if ($ids -contains 1027) { 'LoggedOn' }   # observed, not documented
    elseif ($ids -contains 1026) { 'Lost' }   # Reason= 3 without 1027
    elseif ($ids -contains 1025) { 'Connected' }
    else { 'Starting' }
}

function Wait-Until([scriptblock] $Condition, [datetime] $Deadline) {
    while (-not (& $Condition)) {
        if ((Get-Date) -gt $Deadline) { return $false }
        Start-Sleep -Seconds 5
    }
    $true
}

if (Get-SandboxProcess) { throw 'A sandbox is running or still exiting.' }
New-Item -ItemType Directory -Force -Path $OutFolder | Out-Null
if (Get-ChildItem -LiteralPath $OutFolder) { throw "Not empty: $OutFolder" }

$launched = Get-Date
Start-Process -FilePath "$env:SystemRoot\System32\WindowsSandbox.exe" `
    -ArgumentList ('"{0}"' -f $WsbFile)

$started = Join-Path $OutFolder 'started'
$null = Wait-Until {
    (Test-Path $started) -or (Get-LaunchState $launched) -eq 'Lost'
} $launched.AddMinutes($StartMinutes)
if (-not (Test-Path $started)) {
    return "LaunchFailed ($(Get-LaunchState $launched)): ask the " +
           'operator to close the window, then wait for exit.'
}
$done = Join-Path $OutFolder 'done'
$runBy = (Get-Date).AddMinutes($RunMinutes)
if (-not (Wait-Until { Test-Path $done } $runBy)) {
    return 'TimedOut: no done marker. Ask the operator to close it.'
}
$exitBy = (Get-Date).AddMinutes(5)
if (-not (Wait-Until { -not (Get-SandboxProcess) } $exitBy)) {
    return 'DoneButStillRunning: keep waiting; never kill the processes.'
}
'Completed'
```

Reading the RDP client log needed no elevation on the observed host.
Other Remote Desktop use on the same host writes to the same log; keep
the query window tight. On that host, Sandbox launches logged event 1024
with an empty server name in parentheses, which distinguishes them from
ordinary connections.

## Reading the Outcome

| Outcome | Likely cause | Next action |
| --- | --- | --- |
| `Completed` | The driver finished | Read `results.json`; judge each step by its exit code and output |
| `LaunchFailed (Lost)` | The launch defect | Ask the operator to close the window; the next good launch probably needs a restart |
| `LaunchFailed (LoggedOn)` | The guest signed in, but the driver never started | Check the logon command path, quoting, XML escaping, and the input mapping |
| `LaunchFailed (Starting)` or `(Connected)` | Slow or stuck start | Look at the window before deciding; do not relaunch while processes exist |
| `TimedOut` | A step outlived its budget, or the guest died | Read the partial `results.json`; raise step timeouts only with evidence |
| `DoneButStillRunning` | The guest is still shutting down | Wait longer; never kill the processes |

## Timeouts

- **Start.** A working launch reached sign-in within seconds on the
  observed host; a failed one showed within 30 seconds. Five minutes
  allows for a cold disk and the logon command.
- **Steps.** Give each step its own guest-side limit. The host's run
  deadline must exceed the sum of the step limits plus start and
  shutdown time, or the host gives up on a healthy run.
- **Exit.** Wait for all three session processes to disappear before
  any relaunch. How long a clean shutdown takes was not measured; allow
  minutes, not seconds.

Polling every five seconds is cheap. Avoid fixed sleeps that assume a
duration; wait for an observable transition, as the
[virtual-machine control](../virtual-machine-control.knack.md)
knack's closed loop describes.

## Never Force-Kill the Sandbox

Stopping `WindowsSandboxRemoteSession`, `WindowsSandboxServer`, or
`vmmemWindowsSandbox` with `Stop-Process` or `taskkill` leaves the VM
lingering for minutes, and only one Sandbox can run at a time. The supported
endings are the guest shutting itself down, a person closing the window,
and, for sessions started by the CLI, `wsb stop`. When a run is stuck,
report it and ask the operator to close the window. Then wait for the
processes to exit. See
[Processes and Files](../../windows/processes-and-files/overview.knack.md)
for the general rule of stopping only what you own.

## Collecting Evidence

- Everything under the writable mapping survives. Copy it to the run's
  permanent record before the next run, together with the `.wsb`, the
  Windows build, and the Sandbox app version.
- Export guest event logs in a final driver step, for example
  `wevtutil epl Application C:\sbx\out\Application.evtx`. CAPI2 event
  4097 in that log names root certificates Windows fetched.
- To prove what a step changed, list files, sizes, and hashes under the
  guest profile areas the software touches before and after the step,
  and compare. The guest profile is `C:\Users\WDAGUtilityAccount`.
- Record unknowns as unknowns. A step that did not run proves nothing
  about the behavior it was meant to show.

## Spending the One Good Launch

- Dry-run the driver on the host with scratch input and output folders;
  the shutdown guard keeps the host running.
- Validate the `.wsb` by reading it back, checking every `HostFolder`
  exists, and confirming XML well-formedness, for example with
  `[xml](Get-Content -Raw run-01.wsb)`.
- Restart the host if launches have been failing, then launch the real
  test first.
- If the Sandbox will not cooperate, verify the fix on the host by
  forcing the failure condition through a test seam, and record that
  the fresh-guest check remains open.

## Review Checklist

- Is the output folder new and empty for this run?
- Does the driver write `started` first and `done` in a `finally`
  block, with atomic writes?
- Does each step have its own timeout, with output to files?
- Is shutdown guarded so a host dry run cannot stop the host?
- Does the runner distinguish a failed launch, a broken logon command,
  a timeout, and a slow shutdown?
- Does the runner never kill Sandbox processes and always wait for them
  to exit?

## Further Information

- Microsoft, [Use and configure Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)
- Microsoft, [Windows Sandbox command line](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli)
- Microsoft, [Get-WinEvent](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent)
- Microsoft, [wevtutil](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil)
- Python, [subprocess](https://docs.python.org/3/library/subprocess.html)
  and [os.replace](https://docs.python.org/3/library/os.html#os.replace)
- FieldManual, [Event Logs](../../windows/event-logs/overview.knack.md)
