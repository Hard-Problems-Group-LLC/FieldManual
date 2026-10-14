# Windows Sandbox: Configuration Files and the `wsb` Command

Reviewed: 2026-10-13. Element names, values, and defaults follow
Microsoft's configuration reference as published on that date; the
command-line section follows Microsoft's preview documentation and was
not exercised for this knack. Read the
[overview](overview.knack.md) first.

## When to Load This Knack

Load this companion when writing or reviewing a `.wsb` file, choosing
which host folders and devices a test guest may reach, writing a logon
command, or automating the Sandbox from a script.

## File Basics

A configuration file is XML with the `.wsb` extension and a single
`<Configuration>` root. Microsoft documents it for Windows 10 build
18342 and later and for Windows 11. Opening the file launches the
Sandbox with those settings:

```powershell
Start-Process -FilePath "$env:SystemRoot\System32\WindowsSandbox.exe" `
  -ArgumentList '"C:\path\to\run-01.wsb"'
```

Rules that follow from the format:

- Escape XML metacharacters in values: `&` as `&amp;`, `<` as `&lt;`.
  A logon command containing `&&` is not valid XML until escaped; a
  driver script avoids the problem.
- Use absolute host paths. The reference says relative paths are not
  supported, although one of its examples suggests otherwise.
- Write the file with a file-writing tool or an XML library, not a
  shell here-document, so backslashes survive.
- Do not treat the launcher's process as the session. Track the session
  processes by name, as the
  [test drivers](test-drivers.knack.md) companion
  shows.

## Elements

| Element | Values | Default | Test guidance |
| --- | --- | --- | --- |
| `VGpu` | `Enable`, `Disable`, `Default` | Enabled on non-Arm64 | `Disable` uses WARP software rendering and shrinks the attack surface; it did not cure the launch defect |
| `Networking` | `Enable`, `Disable`, `Default` | Enabled, through the Hyper-V default switch | Disable unless the test downloads something; networking exposes the internal network |
| `MappedFolders` | `MappedFolder` entries | None | Inputs read-only; one output writable |
| `LogonCommand` | One `Command` | None | Start a driver script, not a pipeline |
| `AudioInput` | `Enable`, `Disable`, `Default` | Enabled | Disable for tests |
| `VideoInput` | `Enable`, `Disable`, `Default` | Disabled | Leave disabled |
| `ProtectedClient` | `Enable`, `Disable`, `Default` | Disabled | Runs the client in an AppContainer; may restrict copy and paste |
| `PrinterRedirection` | `Enable`, `Disable`, `Default` | Disabled | Leave disabled |
| `ClipboardRedirection` | `Enable`, `Disable`, `Default` | Enabled | Disable so results flow only through the output folder |
| `MemoryInMB` | Integer | Up to 4 GB with default settings | Values too small to boot are raised to 2048 |

Microsoft's reference spells the GPU element `vGPU` in one place, while
its own sample files use `VGpu`; the samples are the safer model. The
window size is not configurable.

### Mapped Folders

```xml
<MappedFolder>
  <HostFolder>C:\path\to\run-01\in</HostFolder>
  <SandboxFolder>C:\sbx\in</SandboxFolder>
  <ReadOnly>true</ReadOnly>
</MappedFolder>
```

- `HostFolder` must already exist, or the Sandbox fails to start.
- `SandboxFolder` is created if absent. Without it, the folder appears
  on the guest user's desktop.
- `ReadOnly` defaults to `false`. Set it explicitly every time.
- Folders are mapped before the logon command runs.
- Environment variables in paths work from Windows 11 23H2.
- Changes made through a writable mapping persist on the host after
  the Sandbox closes, and anything in the guest can make them.

Map inputs read-only and give the guest one empty, writable output
folder per run. Microsoft's own sample maps two sibling folders under
one guest parent this way. If a step must modify its inputs, have the
driver copy them to a guest-local work folder first. The run that
established the practices in this fileset used a single read-write
mapping instead; the split layout narrows the blast radius and was not
part of that run.

### Logon Command

The command runs after the guest user signs in, as the container user,
which Microsoft says should be an administrator. Whether it runs
elevated was not recorded; have the driver log it. Its console output
goes nowhere you can read, so the driver must write its own records.
Microsoft recommends a script for anything beyond one simple command.

Patterns:

- A portable Python carried in the inputs:
  `C:\sbx\in\py\python.exe -I -B C:\sbx\in\driver.py`. `-I` ignores
  `PYTHON*` variables and leaves both the user site directory and the
  script's own directory off `sys.path`, so keep the driver in one file;
  `-B` stops attempts to write bytecode into a read-only mapping.
- Windows PowerShell: `powershell.exe -NoProfile -ExecutionPolicy
  Bypass -File C:\sbx\in\driver.ps1`. Client Windows defaults to the
  `Restricted` policy, and a script started at sign-in can fail its
  zone check before the desktop is ready; `Bypass` avoids both.
- `cmd.exe /c C:\sbx\in\driver.cmd` for batch drivers.

A restart started inside the guest keeps its state on Windows 11 22H2
and later. Whether the logon command runs again after such a restart
was not recorded, so make the driver idempotent: if its done marker
exists, exit.

## A Test Template

```xml
<Configuration>
  <VGpu>Disable</VGpu>
  <Networking>Enable</Networking>
  <AudioInput>Disable</AudioInput>
  <VideoInput>Disable</VideoInput>
  <PrinterRedirection>Disable</PrinterRedirection>
  <ClipboardRedirection>Disable</ClipboardRedirection>
  <MemoryInMB>4096</MemoryInMB>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>C:\path\to\run-01\in</HostFolder>
      <SandboxFolder>C:\sbx\in</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
    <MappedFolder>
      <HostFolder>C:\path\to\run-01\out</HostFolder>
      <SandboxFolder>C:\sbx\out</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>C:\sbx\in\py\python.exe -I -B C:\sbx\in\driver.py</Command>
  </LogonCommand>
</Configuration>
```

`Networking` is enabled here because first-use certificate behavior
needs real TLS; disable it for tests that need no network. A minimal
configuration that worked on the observed host contained only
networking, one read-write mapped folder, and a Python logon command.

## The `wsb` Command

Starting with Windows 11 24H2, a newer Windows Sandbox app is delivered
and updated through the Microsoft Store, outside Windows releases, and
it includes a preview command-line tool, `wsb.exe`. Microsoft's
versions page lists 24H2 with a minimum update as the prerequisite.
On the observed host, app package `MicrosoftWindows.WindowsSandbox`
0.8.107.0 shipped `wsb.exe` beside `WindowsSandboxRemoteSession.exe`
and `WindowsSandboxServer.exe`, exposed as an app execution alias.

Find it from the package, not from a profile path:

```powershell
Get-AppxPackage -Name MicrosoftWindows.WindowsSandbox |
  Select-Object Name, Version, InstallLocation
Get-Command wsb.exe -ErrorAction SilentlyContinue
```

Aliases live in the per-user `WindowsApps` folder under the local
application-data directory. Code that builds that path from a redirected
`LOCALAPPDATA` looks in the wrong folder and finds nothing; the `PATH`
expanded at logon normally still lists the real folder, so `wsb` resolves
by name unless `PATH` was rebuilt (observed).

| Command | Purpose | Notes |
| --- | --- | --- |
| `wsb start [--id <id>] [-c <config>]` | Create and start a sandbox | Returns its ID; `-c` takes configuration XML as a string |
| `wsb list` | List the current user's sandboxes | |
| `wsb exec --id <id> -c <command> -r ExistingLogin\|System [-d <dir>]` | Run a command | Returns the exit code only; no standard I/O |
| `wsb share --id <id> -f <host> -s <guest> [-w]` | Map a folder at run time | `-w` allows writes |
| `wsb connect --id <id>` | Open the remote-desktop window | Needed before `ExistingLogin` |
| `wsb ip --id <id>` | Show the guest address | |
| `wsb stop --id <id>` | Stop and release the sandbox | |

`--raw` formats output as JSON on every command. `ExistingLogin` fails
without an active user session, which requires `connect` first.
Because `exec` returns no output, marker files in a shared folder stay
necessary.

Two caveats from the documentation itself: its `start` example passes
`<Networking>Disabled</Networking>`, while the configuration reference
documents `Disable`; and the CLI is labelled a preview. Test the exact
form on the installed version.

Untested idea: since `connect` is what opens the window, `start`
followed by `exec -r System` might run work without the remote-desktop
layer where the launch defect appears. Nobody recorded trying it. If you
do, note the app version and whether the session stayed up. `wsb stop`
is the supported way to end a CLI session; whether it avoids the
lingering VM seen after killing processes is unknown.

## Version Facts to Record

Record these with every run, because Sandbox behavior moves with them:

- Windows build: `[Environment]::OSVersion.Version`;
- Sandbox app version: `Get-AppxPackage MicrosoftWindows.WindowsSandbox`;
- the GPU configuration, when launches are unreliable; and
- the exact `.wsb` used, saved beside the results.

## Further Information

- Microsoft, [Use and configure Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)
- Microsoft, [Windows Sandbox sample configuration files](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-sample-configuration)
- Microsoft, [Windows Sandbox command line](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli)
- Microsoft, [Windows Sandbox versions](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-versions)
- Microsoft, [about_Execution_Policies (5.1)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-5.1)
- Python, [Command line and environment](https://docs.python.org/3/using/cmdline.html)
  for `-I` and `-B`
