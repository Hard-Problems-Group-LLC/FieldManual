# Win32 Window Automation From PowerShell

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when a PowerShell script must make itself DPI-aware,
wait for an application to become ready, maximize the application's
window, and capture it. Read the
[desktop automation overview](overview.knack.md) first
for the reasoning. The code below was run in Windows PowerShell 5.1 and
PowerShell 7.6 on Windows 11; the application name, paths, and log marker
are fictional.

## Interop Declarations

`Add-Type` compiles a small C# class with the needed P/Invoke signatures.
Load it once per process, at the top of a script file run with
`-NoProfile -File`; a type cannot be redefined in a session. In code that
may run twice in one session, guard the call with
`if (-not ('Win32Window' -as [type])) { Add-Type ... }`.

```powershell
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class Win32Window
{
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    public static readonly IntPtr PerMonitorAwareV2 = new IntPtr(-4);
    public const int DWMWA_EXTENDED_FRAME_BOUNDS = 9;
    public const int SW_MAXIMIZE = 3;

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetProcessDpiAwarenessContext(IntPtr value);

    [DllImport("user32.dll")]
    public static extern bool SetProcessDPIAware();

    [DllImport("user32.dll")]
    public static extern IntPtr GetThreadDpiAwarenessContext();

    [DllImport("user32.dll")]
    public static extern int GetAwarenessFromDpiAwarenessContext(IntPtr value);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("dwmapi.dll")]
    public static extern int DwmGetWindowAttribute(
        IntPtr hWnd, int attribute, out RECT value, int size);

    [DllImport("user32.dll")]
    public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool IsZoomed(IntPtr hWnd);
}
'@
```

Constants come from Microsoft's headers:
`DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2` is `-4`,
`DWMWA_EXTENDED_FRAME_BOUNDS` is `9`, and `SW_MAXIMIZE` is `3`.

## Become DPI-Aware First

```powershell
function Initialize-DpiAwareness {
    if (-not [Win32Window]::SetProcessDpiAwarenessContext(
            [Win32Window]::PerMonitorAwareV2)) {
        $err = [System.Runtime.InteropServices.Marshal]::GetLastWin32Error()
        if ($err -ne 5) {                      # 5 = ERROR_ACCESS_DENIED
            [void][Win32Window]::SetProcessDPIAware()
        }
    }
    $ctx = [Win32Window]::GetThreadDpiAwarenessContext()
    $awareness = [Win32Window]::GetAwarenessFromDpiAwarenessContext($ctx)
    if ($awareness -lt 1) { throw 'Process is still DPI-unaware.' }
    return $awareness                          # 1 system, 2 per-monitor
}
```

Call it before any coordinate, window, or capture call. Access denied means
awareness was already set for the process; the final check confirms that
the effective awareness is usable. In testing, both PowerShell editions
reported 0 (unaware) before the call and 2 (per-monitor) after it.

## Wait for a Log Marker

```powershell
function Wait-LogMarker {
    param(
        [string]$Path,
        [string]$Pattern,
        [long]$StartOffset = 0,
        [int]$TimeoutSeconds = 180,
        [System.Diagnostics.Process]$Process
    )
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while ([DateTime]::UtcNow -lt $deadline) {
        if ($Process -and $Process.HasExited) {
            throw "Process exited with code $($Process.ExitCode) before it was ready."
        }
        if (Test-Path -LiteralPath $Path) {
            $fs = [System.IO.File]::Open($Path, 'Open', 'Read', 'ReadWrite, Delete')
            try {
                $offset = if ($fs.Length -lt $StartOffset) { 0 } else { $StartOffset }
                [void]$fs.Seek($offset, 'Begin')
                $text = (New-Object System.IO.StreamReader($fs)).ReadToEnd()
                if ($text -match $Pattern) { return $Matches[0] }
            } finally {
                $fs.Dispose()
            }
        }
        Start-Sleep -Milliseconds 500
    }
    throw "Marker '$Pattern' not seen in $Path within $TimeoutSeconds seconds."
}
```

Record the log's length before launching and pass it as `-StartOffset`, so
text from an earlier run cannot satisfy the wait. If the file shrinks, the
application truncated or rotated it, and the function rereads from the
start. The `ReadWrite, Delete` sharing mode lets the application keep
writing and rotating while the script reads.

## Wait for the Main Window

```powershell
function Wait-MainWindow {
    param([System.Diagnostics.Process]$Process, [int]$TimeoutSeconds = 60)
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while ([DateTime]::UtcNow -lt $deadline) {
        $Process.Refresh()                     # MainWindowHandle is cached
        if ($Process.HasExited) { throw 'Process exited before showing a window.' }
        if ($Process.MainWindowHandle -ne [IntPtr]::Zero) {
            return $Process.MainWindowHandle
        }
        Start-Sleep -Milliseconds 250
    }
    throw "No main window within $TimeoutSeconds seconds."
}
```

`MainWindowHandle` is zero for processes without a visible main window,
including hidden windows and launchers whose real window belongs to
another process.

## Maximize and Verify

```powershell
function Set-WindowMaximized {
    param([IntPtr]$Handle, [int]$TimeoutSeconds = 10)
    [void][Win32Window]::ShowWindowAsync($Handle, [Win32Window]::SW_MAXIMIZE)
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while ([DateTime]::UtcNow -lt $deadline) {
        if ([Win32Window]::IsZoomed($Handle)) { return }
        Start-Sleep -Milliseconds 200
    }
    throw 'Window did not report maximized.'
}
```

`ShowWindowAsync` posts the request to the window's own message queue and
returns at once, so a busy application cannot block the script. Run it
only after the readiness marker, because many applications resize their
window during startup.

## Find the Visible Frame

```powershell
function Get-WindowFrame {
    param([IntPtr]$Handle)
    $rect = New-Object Win32Window+RECT
    $size = [System.Runtime.InteropServices.Marshal]::SizeOf([type][Win32Window+RECT])
    $hr = [Win32Window]::DwmGetWindowAttribute(
        $Handle, [Win32Window]::DWMWA_EXTENDED_FRAME_BOUNDS, [ref]$rect, $size)
    if ($hr -ne 0 -and -not [Win32Window]::GetWindowRect($Handle, [ref]$rect)) {
        throw 'Could not read the window rectangle.'
    }
    return $rect
}
```

The DWM frame excludes the invisible resize borders that `GetWindowRect`
includes, and it is reported in physical pixels. With the process
per-monitor aware, both are physical, so a fallback to `GetWindowRect`
differs only by the borders. Without awareness, an earlier test returned
a virtualized `GetWindowRect` of about 1,707 pixels wide for a window the
DWM reported as 3,840.

## Capture the Window

A maximized window's rectangle extends past the monitor's edges: with
`GetWindowRect`, a maximized window on a 3,840 by 2,160 display measured
3,868 by 2,080, and even the DWM frame can exceed the monitor by a pixel.
Clamp the capture to the monitor that holds the window:

```powershell
function Save-WindowCapture {
    param([IntPtr]$Handle, [string]$Path)
    $r = Get-WindowFrame -Handle $Handle
    $frame = [System.Drawing.Rectangle]::FromLTRB($r.Left, $r.Top, $r.Right, $r.Bottom)
    $monitor = [System.Windows.Forms.Screen]::FromHandle($Handle).Bounds
    $area = [System.Drawing.Rectangle]::Intersect($frame, $monitor)
    if ($area.Width -le 0 -or $area.Height -le 0) {
        throw "Window $frame is not on monitor $monitor."
    }
    $bitmap = New-Object System.Drawing.Bitmap $area.Width, $area.Height
    try {
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        try {
            $graphics.CopyFromScreen($area.Left, $area.Top, 0, 0, $bitmap.Size)
        } finally {
            $graphics.Dispose()
        }
        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally {
        $bitmap.Dispose()
    }
}
```

`CopyFromScreen` copies what the screen shows in that rectangle, including
any window or notification on top. Check the saved image's size and
content before using it. To capture only the application's content without
its title bar, use the client rectangle instead (`GetClientRect` with
`ClientToScreen`).

List monitors, their bounds, and their working areas, which exclude the
taskbar:

```powershell
[System.Windows.Forms.Screen]::AllScreens |
    Select-Object DeviceName, Primary, Bounds, WorkingArea
```

Run this only after `Initialize-DpiAwareness`. In testing, `AllScreens`
and `PrimaryScreen` cached the monitor list on first use: queried once
before the awareness call, they kept returning scaled bounds afterwards,
while `Screen.FromHandle` returned physical bounds.

## Putting It Together

```powershell
$null = Initialize-DpiAwareness

$runDir = Join-Path $repo '.local\tmp\demo-run'
$log    = Join-Path $env:LOCALAPPDATA 'ExampleApp\Logs\app.log'
$start  = if (Test-Path -LiteralPath $log) { (Get-Item -LiteralPath $log).Length } else { 0 }

$app = Start-Process -FilePath $exe -PassThru
try {
    Wait-LogMarker -Path $log -Pattern 'Main menu ready' -StartOffset $start `
        -Process $app -TimeoutSeconds 300 | Out-Null
    $hwnd = Wait-MainWindow -Process $app
    Set-WindowMaximized -Handle $hwnd
    Start-Sleep -Milliseconds 500              # let the frame repaint
    Save-WindowCapture -Handle $hwnd -Path (Join-Path $runDir 'main-menu.png')
} finally {
    if (-not $app.HasExited) {
        [void]$app.CloseMainWindow()
        if (-not $app.WaitForExit(15000)) { taskkill /PID $app.Id /T /F | Out-Null }
    }
}
```

The short pause after maximizing is a repaint allowance, not a readiness
wait; the marker has already established readiness. Record the process ID
and start time as the
[processes companion](../processes-and-files/ownership.knack.md)
describes when another step must find the process later.

## Sharp Edges

- `SetLastError` values are meaningful only when the call failed; a stale
  value after success is normal.
- `IsZoomed` reports the window state, not the content. A game that renders
  a smaller back buffer inside a maximized window still needs a visual
  check.
- Exclusive full-screen applications may not produce useful
  `CopyFromScreen` captures; prefer windowed or borderless modes for
  automated capture.
- Monitors with different scale factors give one window different sizes as
  it moves; capture after placement, not before.

## Further Information

- Microsoft, [SetProcessDpiAwarenessContext](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setprocessdpiawarenesscontext)
- Microsoft, [DPI_AWARENESS_CONTEXT values](https://learn.microsoft.com/en-us/windows/win32/hidpi/dpi-awareness-context)
- Microsoft, [SetProcessDPIAware](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setprocessdpiaware)
- Microsoft, [GetWindowRect](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect)
- Microsoft, [DWMWINDOWATTRIBUTE](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute)
- Microsoft, [ShowWindowAsync](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindowasync)
- Microsoft, [ShowWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow)
- Microsoft, [IsZoomed](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-iszoomed)
- .NET, [Process.MainWindowHandle](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process.mainwindowhandle)
- .NET, [Graphics.CopyFromScreen](https://learn.microsoft.com/en-us/dotnet/api/system.drawing.graphics.copyfromscreen)
- .NET, [Screen class](https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.screen)
