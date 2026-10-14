# Desktop Automation on a Shared Windows Workstation

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when an agent launches a graphical application on Windows
and must wait for it, place its window, capture screenshots, or present it
to a person: smoke tests of a game or editor, documentation screenshots,
or demonstrations. The
[Win32 from PowerShell companion](Win32.PowerShell.knack.md)
supplies tested code.

Process ownership rules come from
[processes and files](../processes-and-files/overview.knack.md).
For the general boundary between isolated automation and a live user
session, see
[live user-session targeting](../../desktop/live-user-session-targeting.knack.md),
whose concrete selectors are Linux-specific but whose authority model
applies here.

## Mental Model

The desktop is a shared, stateful device that belongs to the person
signed in. Reliable automation on it needs six things, in order:

1. a target window identified by evidence, not by title;
2. a known coordinate system, which on Windows means a known DPI
   awareness;
3. a positive readiness signal from the application;
4. window placement applied after the application finishes its own
   startup changes;
5. a capture checked for plausibility; and
6. cleanup that leaves the desktop as it was.

Fixed sleeps, window titles, and screen coordinates copied from an earlier
run each fail in ordinary conditions.

## Courtesy Rules

- Touch only windows the task opened. Never close, move, or minimize a
  window that may belong to the person at the machine.
- Avoid repeated focus changes. Each launch can pull focus away from what
  the person is typing.
- Announce noisy runs, such as dozens of application launches, and check
  for notification side effects; see
  [background events](../event-logs/background-noise.knack.md).
- Presentation preferences, such as showing demonstration windows
  maximized or at a larger interface scale, belong to the operator. Record
  them in project-owned notes and apply them to windows shown to people;
  the task's own unattended runs can use whatever is fastest.

## DPI Awareness

Windows scales applications that do not declare DPI awareness. For such a
process it also virtualizes many coordinate APIs: `GetWindowRect` and
screen-size queries answer in scaled, 96-DPI units. Screen capture through
`Graphics.CopyFromScreen` copies physical pixels. Mixing the two produces
captures that are cropped to the top-left part of the window or offset
from it. For example, at 225% display scaling an unaware caller sees a
3,840-pixel-wide window as about 1,707 pixels wide.

In testing, both PowerShell editions started DPI-unaware. Before any
coordinate or capture call, make the automation process aware:

- prefer `SetProcessDpiAwarenessContext` with Per Monitor v2, available
  from Windows 10 version 1703;
- fall back to `SetProcessDPIAware`, which gives system awareness and is
  accurate only at the primary display's scale; and
- if the call fails with access denied, awareness was already set; check
  the effective value rather than assuming.

Microsoft recommends declaring awareness in an application manifest rather
than by API call. A script host has no manifest of its own, so the API call
early in the script is the practical choice.

`GetWindowRect` also includes invisible resize borders, so a maximized
window's rectangle is larger than the monitor. For the visible frame, use
`DwmGetWindowAttribute` with `DWMWA_EXTENDED_FRAME_BOUNDS`, which
Microsoft notes is not adjusted for DPI, and clamp the capture rectangle
to the monitor's bounds either way.

## Readiness: Markers, Not Sleeps

Load times vary with cold caches, updates, shader compilation, security
scanning, and the number of plugins. Wait for a positive signal with a
time limit:

- a line the application writes to its log when it reaches the state the
  test needs, such as a main menu or a loaded world;
- the process's main window handle becoming non-zero, after calling
  `Refresh()`, because .NET caches it; and
- failure when the process exits first or the limit expires.

Read only log content written after the launch. Logs may be appended to
across runs, rotated, or truncated at startup, and an old marker must not
satisfy a new wait. Open the log with shared read and write access so the
application can keep writing.

Some launchers start a second process that owns the real window and then
exit. Follow the command line to the process that owns the window.

The same rule applies to moments inside a running session. An application
can run slower than real time under load, so a capture timed by a fixed
delay after launch often misses the event it was meant to show. Have the
application log a cue when the moment begins, wait for that cue, and then
take a short burst of captures.

## Window Placement After Startup

Many applications, games especially, change resolution, toggle full
screen, or recreate their window during startup from their saved
settings. A maximize issued before that point is undone. Sequence:

1. wait for the readiness marker;
2. send `ShowWindowAsync(hwnd, SW_MAXIMIZE)`, where `SW_MAXIMIZE` is 3;
   the asynchronous call does not block if the target is busy; and
3. poll `IsZoomed` with a time limit, and repeat once if the application
   changed its window again.

`Start-Process -WindowStyle Maximized` affects only the first show of the
first window, through the launch's startup information. Applications that
size their own windows override it.

## Preference Files

Applications often store settings in a file that their settings screen
writes; games built with Unity, for example, usually keep persistent data
under `%USERPROFILE%\AppData\LocalLow\<company>\<product>`. Some settings
screens refuse values that the program still
accepts from the file, for example an interface scale above a limit tied
to the current resolution. Editing the file can set such values, but
doing so is unsupported by the vendor:

- edit only while the application is closed, because many applications
  rewrite their settings on exit;
- back up the original file first and restore it afterwards, unless the
  operator wants the change kept;
- preserve the file's encoding, line endings, and structure; see
  [text files](../shells/text-files.knack.md);
  and
- verify the result visually; a value the menu refuses may render badly.

Locate the file from the application's own log or documentation. Under a
harness that redirects the user profile, known-folder lookups follow the
process's `USERPROFILE`, so an application the agent starts may read a
sandbox copy while the operator's instance reads the real file. Decide
which one the task needs, and confirm it from the application's log.

Automation also changes preference files without editing them. A window
maximized by a script can be saved as the application's new resolution,
so the next run starts at a different size. For repeatable runs, give each
run its own data folder and seed it with a known preference file before
launch.

## Captures

`CopyFromScreen` copies whatever is on screen in the rectangle, so the
window must be visible, unobstructed, and on the expected monitor. Check
each capture before trusting it: expected dimensions, not uniformly black
or white, and showing the expected content. Review at full size and at the
downscaled size the audience will see.

Screenshots can show notifications, other windows, and personal data.
Capture only the target window's rectangle, store captures in the
project's ignored local folder, and review them before sharing.

## Review Checklist

- Is the target window found through a process the task launched?
- Is the automation process DPI-aware before its first coordinate call?
- Does every wait have a positive marker, a failure path, and a limit?
- Is placement applied after startup and verified with `IsZoomed`?
- Are preference-file edits backed up, format-preserving, and reverted?
- Were captures checked for size and content, and kept out of version
  control?
- Was every window the task opened closed, and nothing else touched?

## Further Information

- Microsoft, [High DPI desktop application development on Windows](https://learn.microsoft.com/en-us/windows/win32/hidpi/high-dpi-desktop-application-development-on-windows)
- Microsoft, [SetProcessDpiAwarenessContext](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setprocessdpiawarenesscontext)
- Microsoft, [SetProcessDPIAware](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setprocessdpiaware)
- Microsoft, [GetWindowRect](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect)
- Microsoft, [ShowWindowAsync](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindowasync)
- Microsoft, [ShowWindow: `nCmdShow` values](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow)
- .NET, [Process.MainWindowHandle](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.mainwindowhandle)
- .NET, [Graphics.CopyFromScreen](https://learn.microsoft.com/en-us/dotnet/api/system.drawing.graphics.copyfromscreen)
- Unity, [Application.persistentDataPath](https://docs.unity3d.com/ScriptReference/Application-persistentDataPath.html)
