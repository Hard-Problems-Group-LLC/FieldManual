# Visual Studio from Scripts and Agents

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when a script, build agent, or AI agent on Windows must find,
use, update, or work beside Visual Studio 2022 or Visual Studio Build Tools:
building with its MSBuild, opening a developer shell, recording toolchain
versions, editing solutions, or explaining why a build changed after an
update.

Companions:

- [Discovery and developer shells](discovery.PowerShell.knack.md)
  for `vswhere`, MSBuild selection, and developer-shell environments;
- [Installer](installer.knack.md) for updates, rollback,
  exit codes, and `.vsconfig` files;
- [Solutions and projects](solutions.knack.md) for
  solution files, mixed project styles, and linked content; and
- [Diagnostics](diagnostics.knack.md) for binary logs and
  coexisting with an open IDE.

The build sequence itself, including MSBuild.exe versus `dotnet build`, is
in [.NET Framework Builds on Windows](../framework-builds/overview.knack.md).

## Mental Model

The Visual Studio Installer manages **instances**. Each instance has an
installation path, a product (Community, Professional, Enterprise, or Build
Tools), a channel, and a set of workloads and components. Several instances
can live side by side, including different editions and major versions.
Visual Studio 2022 is major version 17 and installs under
`Microsoft Visual Studio\2022\<edition>`; Visual Studio 2026 is version 18 and
installs under `Microsoft Visual Studio\18\<edition>`.

An instance carries a whole toolchain: MSBuild, the C# compiler and
analyzers, .NET Framework targeting packs, and often a .NET SDK. The IDE and
command-line builds share it. Updating the instance changes all of these at
once.

Several version numbers describe one instance. On one machine checked for
this knack they were:

| Quantity | Source | Value |
| --- | --- | --- |
| Product display version | `vswhere -property catalog_productDisplayVersion` | `17.14.42` |
| Installation version | `vswhere -property installationVersion` | `17.14.37806.7` |
| MSBuild version | `MSBuild.exe -version` | `17.14.60.43110` |
| Developer-prompt marker | `%VSCMD_VER%` | `17.0` |

Record the first three; they answer different questions.

Scripts never need the IDE. They call MSBuild.exe by path, or start a
developer shell when they need other tools from `PATH`.

## Locate, Never Assume

Find instances with `vswhere.exe`, which ships with the installer under
`%ProgramFiles(x86)%\Microsoft Visual Studio\Installer`. Its defaults
matter:

- Only Community, Professional, and Enterprise are searched; add
  `-products *` to include Build Tools.
- Only complete instances are searched: no errors and no reboot required.
  An instance in the middle of an update or waiting for a restart silently
  disappears from results. When a script reports "not found", rerun with
  `-all` and read `isComplete` and `isRebootRequired`.
- `-latest` returns the newest version, last installed.

The query documented by the vswhere project,
`-find MSBuild\**\Bin\MSBuild.exe`, returns the 32-bit MSBuild. The 64-bit
MSBuild is `MSBuild\Current\Bin\amd64\MSBuild.exe`; developer shells put it
first on `PATH`, and Microsoft notes that from Visual Studio 2022 `msbuild`
in those shells defaults to 64-bit. Pick one deliberately and log its path.

Never use `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe`. It
is the MSBuild 4.x that ships with .NET Framework itself. It rejected an
SDK-style project with MSB4041 and treated a `ToolsVersion="15.0"` project as
4.0. A developer prompt's `PATH` contains it after Visual Studio's MSBuild,
so `where msbuild` lists both.

## Updates Change the Toolchain Under You

An instance can be updated by the installer's own notifications, by an
administrator's managed updates, or, for Community edition on an unmanaged
machine that enables "Receive updates for other Microsoft products", through
Microsoft Update alongside Windows updates. Microsoft Update never
force-closes Visual Studio; the update applies once it is closed. In
practice an instance can move to a new servicing release across a Windows
Update restart without anyone opening the installer. In the case behind
this knack, the MSBuild path stayed the same, so path-based scripts kept
working while the compiler and MSBuild changed underneath them.

Therefore:

1. Record the product display version, MSBuild version, and .NET SDK
   version with every build log or status report.
2. After any restart or update, re-read them before comparing results with
   earlier runs.
3. After a version change, run a clean rebuild and the full test suite
   before trusting incremental output.
4. When a build or analyzer result changes without a source change, compare
   versions first.
5. Use `-version` ranges in `vswhere` queries when a project must stay on one
   major version, and expect paths to change between major versions.

The installer companion covers rollback and exit codes, including 3010,
"reboot required".

## When an Agent Needs a Developer Shell

- **Not needed** for MSBuild alone; call it by full path.
- **Needed** for tools found through `PATH` or environment variables, such
  as `csc`, `ildasm`, `signtool`, and the C++ tools, and for builds that read
  `VSINSTALLDIR`, `INCLUDE`, or `LIB`.

A developer shell changes only the current process. Many agent tools start a
fresh shell for each command, so initialize the environment and run the
build in the same command or script. Always pass an explicit installation
path: `Launch-VsDevShell.ps1` falls back to an interactive list when it
cannot locate an instance, which stalls an unattended run.

## Working Beside the IDE

An open solution is not idle. Visual Studio runs design-time builds when it
loads a project and when project files change; these run MSBuild targets but
do not modify build outputs. Real IDE builds, debugging sessions, and test
runs use the same `bin/` and `obj/` folders as scripts, and MSBuild keeps
worker nodes alive after builds by default. Before a scripted clean rebuild,
stop IDE builds and debugging or close the solution, or build in a separate
worktree. The diagnostics companion has details.

## Sharp Edges

- The installer owns instance state. Prefer its `repair` and `modify`
  commands over hand edits under the installation path when a toolchain
  misbehaves.
- `VSCMD_VER` showed `17.0` in the instance checked, although Microsoft's
  example shows a full version. Use it only as a marker that the environment
  is initialized.
- Initializing a developer prompt printed "'vswhere.exe' is not recognized"
  from an internal script. The initialization still succeeded; judge success
  by exit code and by the tools found, not by console noise.
- Build Tools instances have no IDE; documentation about IDE menus does not
  apply to them.

## Review Checklist

- Is every Visual Studio path discovered with `vswhere`, including
  `-products *` where Build Tools may be the only instance?
- Does "not found" handling check incomplete and reboot-pending instances?
- Is the MSBuild binary (32-bit, 64-bit, never .NET Framework's) chosen
  deliberately and logged?
- Are product, MSBuild, and SDK versions recorded and re-checked after
  restarts?
- Do developer-shell steps pass an explicit instance and run in one process?
- Are IDE builds stopped, or a separate worktree used, during scripted
  rebuilds?

## Further Information

- [vswhere wiki: Find MSBuild](https://github.com/microsoft/vswhere/wiki/Find-MSBuild)
- [Tools for detecting and managing Visual Studio instances](https://learn.microsoft.com/en-us/visualstudio/install/tools-for-managing-visual-studio-instances)
- [Developer Command Prompt and Developer PowerShell](https://learn.microsoft.com/en-us/visualstudio/ide/reference/command-prompt-powershell)
- [Use command-line parameters to install Visual Studio](https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio)
- [Visual Studio security updates through Microsoft Update](https://devblogs.microsoft.com/visualstudio/automatically-install-visual-studio-security-updates-through-microsoft-update/)
- [Design-time builds](https://github.com/dotnet/project-system/blob/main/docs/design-time-builds.md)
- [MSBuild command-line reference](https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-command-line-reference)
