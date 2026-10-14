# Visual Studio Discovery and Developer Shells

Reviewed: 2026-10-13

Load this companion after the
[Visual Studio overview](overview.knack.md) when a PowerShell
script must find a Visual Studio instance, choose its MSBuild, record
versions, or initialize a developer-shell environment. The snippets were run
under Windows PowerShell 5.1 and PowerShell 7.6 against a Visual Studio 2022
Community instance.

## Find Instances with vswhere

```powershell
$ErrorActionPreference = 'Stop'
$vswhere = Join-Path ${env:ProgramFiles(x86)} `
    'Microsoft Visual Studio\Installer\vswhere.exe'
if (-not (Test-Path $vswhere)) { throw 'vswhere.exe not found.' }

# Every instance, including Build Tools and incomplete instances.
$json = & $vswhere -all -products * -format json -utf8 | Out-String
$instances = $json | ConvertFrom-Json
$instances |
    Select-Object displayName, installationPath, installationVersion,
        isComplete, isRebootRequired,
        @{ n = 'displayVersion'; e = { $_.catalog.productDisplayVersion } }
```

Assign the result of `ConvertFrom-Json` before piping it on. Windows
PowerShell 5.1 emits the parsed array as one object, so piping
`ConvertFrom-Json` straight into `Select-Object` produced empty columns there,
while PowerShell 7 enumerated it.

Useful options, from `vswhere -?`:

| Option | Effect |
| --- | --- |
| `-all` | Include incomplete instances, such as those needing a reboot. |
| `-products *` | Include every product, not only Community, Professional, and Enterprise. |
| `-requires <id>` | Require workload or component IDs; all must be present unless `-requiresAny`. |
| `-version <range>` | Restrict versions, for example `[17.0,18.0)` for Visual Studio 2022. |
| `-latest` | Newest version, last installed. |
| `-path <dir>` | The instance that owns a path. |
| `-property <name>` | Print one property; nested names use `.`, `/`, or `_`. |
| `-find <pattern>` | Return matching files under the installation path. |
| `-include packages` | Add installed packages to JSON or XML output. |
| `-utf8` | Write UTF-8, recommended for JSON. |
| `-prerelease`, `-legacy` | Include previews, or Visual Studio 2015 and older. |

Component IDs present on the checked instance included
`Microsoft.Component.MSBuild`,
`Microsoft.VisualStudio.Workload.ManagedDesktop`,
`Microsoft.Net.Component.4.7.2.TargetingPack`, and
`Microsoft.NetCore.Component.SDK`. Require the targeting pack a project
needs, not only MSBuild:

```powershell
$vsPath = & $vswhere -latest -products * -version '[17.0,18.0)' `
    -requires Microsoft.Component.MSBuild `
    -requires Microsoft.Net.Component.4.7.2.TargetingPack `
    -property installationPath
if (-not $vsPath) {
    throw 'No complete Visual Studio 2022 instance with MSBuild and the ' +
        '4.7.2 targeting pack. Check vswhere -all for pending reboots.'
}
```

## Choose MSBuild

```powershell
$msbuild = Join-Path $vsPath 'MSBuild\Current\Bin\amd64\MSBuild.exe'
```

| Binary | Process |
| --- | --- |
| `MSBuild\Current\Bin\MSBuild.exe` | 32-bit; returned by the documented `-find` query |
| `MSBuild\Current\Bin\amd64\MSBuild.exe` | 64-bit; first on `PATH` in a developer shell |
| `dotnet msbuild` | 64-bit, from the .NET SDK, not Visual Studio |

A property function confirmed each: `$([System.Environment]::Is64BitProcess)`
returned `False`, `True`, and `True` respectively. All three reported the
same MSBuild version on the checked machine. Avoid the .NET Framework's own
`MSBuild.exe` under `C:\Windows\Microsoft.NET\`.

## Record Versions

```powershell
[pscustomobject]@{
    VisualStudio = & $vswhere -path $vsPath `
        -property catalog_productDisplayVersion
    Instance     = & $vswhere -path $vsPath -property installationVersion
    MSBuild      = & $msbuild -version -nologo | Select-Object -Last 1
    DotNetSdk    = dotnet --version
}
```

Write this record into build logs, test reports, and status files, and
compare it after every restart. `dotnet --version` reports the SDK selected
for the current directory, which a `global.json` can pin.

## Developer PowerShell

`Launch-VsDevShell.ps1` in `Common7\Tools` loads the
`Microsoft.VisualStudio.DevShell.dll` module and calls `Enter-VsDevShell`.
For unattended use, always name the instance:

```powershell
& (Join-Path $vsPath 'Common7\Tools\Launch-VsDevShell.ps1') `
    -VsInstallationPath $vsPath -SkipAutomaticLocation `
    -Arch amd64 -HostArch amd64 | Out-Null
```

- `-VsInstallationPath`, `-VsInstanceId`, or `-Latest` select the instance.
  Without them the script tries its own location, then the latest instance,
  then shows an interactive list, which stalls an agent. `-List` is always
  interactive.
- `-SkipAutomaticLocation` keeps the current directory. Without it the shell
  can move to the configured Visual Studio project location.
- `-Arch` and `-HostArch` need Visual Studio 2022 version 17.1 or later. The
  default for both is x86.
- The script requires an execution policy that allows it to run.

## Developer Command Prompt

`VsDevCmd.bat` in the same folder initializes `cmd.exe`. Substitute the
installation path that `vswhere` returned:

```bat
call "<installationPath>\Common7\Tools\VsDevCmd.bat" -no_logo ^
    -arch=amd64 -host_arch=amd64 -startdir=none
```

Its `-help` lists the options. `-startdir=none` keeps the current directory
and is the default unless `VSCMD_START_DIR` is set; `-test` runs smoke checks
in an already initialized prompt. Microsoft recommends checking `VSCMD_VER`
to detect an initialized prompt.

To use the prompt's environment from PowerShell, run the batch file and
`set` in one `cmd.exe` process and copy the variables back:

```powershell
$devCmd = Join-Path $vsPath 'Common7\Tools\VsDevCmd.bat'
$devArgs = '-no_logo -arch=amd64 -host_arch=amd64 -startdir=none'
$lines = cmd.exe /d /c "`"$devCmd`" $devArgs && set"
if ($LASTEXITCODE -ne 0) { throw "VsDevCmd failed: $LASTEXITCODE" }
foreach ($line in $lines) {
    if ($line -match '^([^=]+)=(.*)$') {
        Set-Item -Path "Env:$($Matches[1])" -Value $Matches[2]
    }
}
```

After this, `msbuild` and `csc` resolved from Visual Studio's folders in both
PowerShell versions.

## From Git Bash

Git Bash rewrites arguments that start with `/`, so `cmd /c` and switches
such as `/nologo` can arrive mangled. Write the commands to a `.cmd` file and
run it with a full Windows path, use `cmd //c`, or pass MSBuild switches in
their `-switch` form. Convert paths with `cygpath -w` before handing them to
Windows programs.

## Further Information

- [vswhere repository and wiki](https://github.com/microsoft/vswhere/wiki)
- [Find MSBuild with vswhere](https://github.com/microsoft/vswhere/wiki/Find-MSBuild)
- [Developer Command Prompt and Developer PowerShell](https://learn.microsoft.com/en-us/visualstudio/ide/reference/command-prompt-powershell)
- [Visual Studio workload and component IDs](https://learn.microsoft.com/en-us/visualstudio/install/workload-and-component-ids)
- [`global.json` overview](https://learn.microsoft.com/en-us/dotnet/core/tools/global-json)
