# In-Host Smoke Testing: The Launcher

Load this companion to the
[in-host smoke testing overview](overview.knack.md) when
you write or review the script that prepares the host, starts it with the
plugin's runner, waits for the result, and turns the host log into an exit
code.

Reviewed: 2026-10-13. Command-line options, configuration file names
and log locations below are placeholders; every host names them
differently. The sketch is Python; any scripting language will do.

## Responsibilities

1. **Preflight.** Find the host through an environment variable or an
   argument, never a hard-coded path. Confirm that the last build succeeded
   and that the plugin binary is newer than every source file; a run
   against a stale binary tests old code. Check for running host instances
   (see "Do Not Disturb" below).
2. **Isolate.** Create a fresh data folder for the run, so that the user's
   settings, saves and plugin list are untouched.
3. **Configure.** Write the host's plugin list and preferences into that
   folder.
4. **Install.** Make the plugin visible to the host, normally with a link
   from the host's plugin folder to the build output.
5. **Launch** with the data-folder override, a log-file path, the runner
   flag and any quick-start option.
6. **Wait** for the runner's `DONE` line, the process's exit, or a timeout.
7. **Scrape** the log for runner results and for errors attributable to the
   plugin.
8. **Report and exit.** Print the results, keep the artifacts, and exit
   non-zero on any failure.

## Isolation

The data folder is where the host keeps its configuration, saves, caches and
logs. Pointing it at a fresh folder per run gives every run the same starting
state and keeps the user's own state out of reach.

- Allocate the folder under the project's disposable workspace, such as
  `.local/tmp/smoke-<timestamp>/`, following FieldManual's
  [Local Operator State](../../../../standards-and-practices/core/local-operator-state.md)
  standard, unless the host requires another location.
- Verify the override took effect. The runner logs the folder it uses; the
  launcher compares it with the folder it created and fails the run if they
  differ, before any scenario runs.
- Clean up only the folder the run created. Keep it on failure if its
  contents help diagnosis.

## Configuration Written for the Run

**Plugin list.** Enable exactly the host's base content, any official
expansions or dependencies the plugin needs, and the plugin itself. Load
order can matter: content that extends earlier content must load after it,
and a wrong order can stop the host from starting at all.

**Preferences.** Typical settings for unattended runs:

| Setting | Test run | Showcase or kept-open run |
| --- | --- | --- |
| Volume | Muted | On, at a moderate level |
| Window | Windowed, small | Maximized once ready |
| Interface scale | Default | Enlarged for viewing |
| Run when unfocused | Yes | Yes |
| Developer mode or console | On | As needed |
| Pause on error | Off | Off |
| Automatic pausing | Never | Never |
| Language | Fixed | Fixed |

Pausing on error or when unfocused turns a failure into a hang. A fixed
language keeps log text and names stable for scraping.

## Do Not Disturb

A person may be playing, or watching a showcase, in a host instance the
launcher did not start. Never close, kill or reuse an instance you did not
start: record the process identifier of the one you launch and act only on
that. Use your own data folder, so that your run never writes to theirs.

## Installing the Plugin

Link the build output into the host's plugin folder rather than copying, so
that every run sees the latest build. Before creating the link, check what
is already there. If the path exists and is not a link to this build, stop
and tell the user. Never replace a folder you did not create.

## Launch and Wait

```python
proc = subprocess.Popen([host_exe, f"-datafolder={data}",
                         "-logfile", str(log), "-plugin-smoke"],
                        cwd=host_dir)
deadline = time.monotonic() + timeout_s
done = None
while time.monotonic() < deadline:
    text = log.read_text(errors="replace") if log.exists() else ""
    done = DONE_RE.search(text)
    if done or proc.poll() is not None:
        break
    time.sleep(1)                     # polling interval, not a fixed wait
if not done:
    kill_process_tree(proc)           # a hung host holds files open
```

- **Timeout.** Size it to several times a normal run, and report it
  distinctly from a failure: a timeout usually means a crash, a hang or a
  modal dialog.
- **Process exit before DONE** is a crash. Report the last lines of the log.
- **Quit the host** after `DONE` unless a person asked to keep it open. The
  runner can request a clean exit itself; the launcher kills the process if
  it lingers.
- **The host's exit code is not a result.** A host commonly exits with 0
  whether or not checks failed, and a killed process may report -1. Derive
  the result from the runner's lines alone.
- **Never read a stale log.** Give each run its own log file, and confirm
  that the previous one is gone or read only content written after launch.
  Deleting a log another process still holds open can fail silently, and
  the `DONE` poll can then match the last run's line (an inferred risk,
  consistent with one observed failure).

## Scraping and Attribution

Read the whole log after the run:

- runner lines: `PASS`, `FAIL`, `INFO`, `TIME`, `DONE` with their counts,
  and the `PLAN` line, so that unreported checks become failures;
- host errors: each error's message and its stack trace, joined into one
  record; and
- attribution: the error is the plugin's when any trace frame belongs to the
  plugin's namespace or assembly, or the message names the plugin.

Report three groups: runner failures, plugin errors, and other host errors.
Fail the run on the first two. Show the third, because a host error with no
trace can still be the plugin's doing.

```python
failed = (not done or int(done["failed"]) > 0 or plugin_errors
          or reported < planned)
sys.exit(1 if failed else 0)
```

## Artifacts

Keep, per run: the full host log, the launcher's summary, the runner's
`INFO` and `TIME` lines, and any screenshots. Name them by run time and
commit so that two runs can be compared. Publish anything worth keeping
before the disposable folder is cleaned.

Measure how long runs take from these artifacts rather than trusting the
documentation. In one project the testing notes said "about three minutes"
while 22 recorded runs took between 35 and 75 seconds.

## Modes for People

- **Keep open.** Run the checks, then leave the host running for a person to
  inspect. Maximize the window and enlarge the interface only after `DONE`,
  because the host may reset its window during startup.
- **Showcase.** Start with the showcase flag instead of the checks, with
  sound on, wait for the runner's `READY` line, then maximize. Scrape the log
  for plugin errors when the person closes the host. Serving a watcher is
  covered in [Directed Showcases:
  Staging](../../demonstrations/showcases/staging.knack.md).

## Screen Capture

Tools that capture screenshots or video of a run should wait for log cues,
not for fixed delays: a `READY` line, a scenario's start marker, or a
specific `INFO` line placed for the purpose. Startup time varies by machine
and by world, and heavy scenes can slow the host's simulation below real
time, so a fixed delay either wastes time or captures the wrong moment.
Capture the host's own window by its handle rather than the whole screen,
so that other windows do not leak into the image.

## Environment Limits

- Hosts that need a graphics device and a desktop session usually cannot run
  on a headless build agent without a virtual display. Run them on a desktop
  machine or a virtual machine with a display, and say so in the project's
  testing notes.
- The user must not interact with the host window during a run; input can
  change camera, selection or time speed.
- Concurrent runs of one host may collide on its install folder, ports or
  single-instance locks. Where the host tolerates it, two runs with separate
  data folders and log files can proceed side by side and sample two
  generated worlds at once; confirm that before relying on it, and
  otherwise serialize. Runs that shared one data folder have ended with
  killed processes.

## Calling It Green

A single passing run on a randomly generated world is weak evidence. Require
two consecutive clean runs before calling a change green, as the
[flakiness companion](flakiness.knack.md)
explains.

## Further Information

- Epic Games, [Gauntlet Automation Framework
  Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/gauntlet-automation-framework-overview-in-unreal-engine):
  launching sessions and parsing their logs.
- Unity, [Player command-line
  arguments](https://docs.unity3d.com/Manual/PlayerCommandLineArguments.html):
  an example of log-file and window overrides on a host's command line.
- Python, [subprocess](https://docs.python.org/3/library/subprocess.html):
  process launch, polling and termination.
- FieldManual, [Local Operator
  State](../../../../standards-and-practices/core/local-operator-state.md):
  disposable run folders and safe cleanup.
- FieldManual, [Desktop Automation on a Shared Windows
  Workstation](../../../windows/desktop-automation/overview.knack.md):
  readiness markers, window placement after startup, preference files and
  captures for hosts on Windows.
