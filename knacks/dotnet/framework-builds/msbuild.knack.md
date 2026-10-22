# MSBuild Command Line for .NET Framework Projects

Reviewed: 2026-10-14

Load this companion after the
[.NET Framework builds overview](overview.knack.md) when
scripting builds with Visual Studio's MSBuild.exe. Examples use PowerShell
and the neutral names `Example.sln` and `Example.Plugin.csproj`.

## Locate MSBuild

`vswhere.exe` is installed with Visual Studio 2017 Update 2 and later at
`%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe`. The
vswhere project documents this query:

```powershell
$vswhere = Join-Path ${env:ProgramFiles(x86)} `
    'Microsoft Visual Studio\Installer\vswhere.exe'
$msbuild = & $vswhere -latest -requires Microsoft.Component.MSBuild `
    -find 'MSBuild\**\Bin\MSBuild.exe' | Select-Object -First 1
if (-not $msbuild) { throw 'MSBuild not found; install Visual Studio.' }
& $msbuild -version
```

By default the query covers the Community, Professional, and Enterprise
editions; add `-products *` to include Build Tools. The resulting path has
this shape, where the release and edition segments vary:

```text
<Program Files>\Microsoft Visual Studio\<release>\<edition>\
    MSBuild\Current\Bin\MSBuild.exe
```

Record the MSBuild version in build logs, because it determines the
compiler and therefore the C# language versions available.

A Developer PowerShell or Developer Command Prompt for Visual Studio puts
MSBuild on `PATH` and is an acceptable alternative for interactive work.

## Switches Worth Knowing

Every switch accepts `-switch` or `/switch`, and switches are not
case-sensitive.

| Switch | Effect |
| --- | --- |
| `-restore`, `-r` | Run the `Restore` target before the requested targets. |
| `-target:`, `-t:` | Run named targets, such as `Rebuild` or `Clean`, instead of the defaults. |
| `-property:`, `-p:` | Set global properties, such as `Configuration=Release`. |
| `-maxCpuCount`, `-m` | Build projects in parallel processes; without it MSBuild uses one. |
| `-verbosity:`, `-v:` | `q`, `m`, `n` (default), `d`, or `diag`. |
| `-nologo` | Omit the banner. |
| `-warnAsError`, `-err` | Fail the build on warnings, or on listed codes. |
| `-noWarn:` | Demote listed warning codes to messages. |
| `-binaryLogger`, `-bl` | Write a structured `.binlog` of the whole build. |
| `-nodeReuse:false` | Do not leave worker nodes running after the build. |
| `-getProperty:` | Print evaluated property values without building. |
| `-preprocess`, `-pp` | Write the project with all imports inlined, without building. |

The .NET CLI passes these switches through `dotnet build` and
`dotnet msbuild`, so the same diagnostics work for SDK-style projects.

## Recipes

Release build with restore:

```powershell
& $msbuild Example.Plugin.csproj -restore -p:Configuration=Release `
    -nologo -v:m
if ($LASTEXITCODE -ne 0) { throw "Build failed: $LASTEXITCODE" }
```

Clean verification of every source file and reference:

```powershell
& $msbuild Example.sln -restore -t:Rebuild -p:Configuration=Release -m
```

Strict automation build:

```powershell
& $msbuild Example.sln -restore -p:Configuration=Release -m `
    -warnAsError -nodeReuse:false -bl:artifacts\build.binlog
```

Property inspection, for example to see where an environment variable or
`Directory.Build.props` value ends up:

```powershell
& $msbuild Example.Plugin.csproj -getProperty:HostManaged,LangVersion
& $msbuild Example.Plugin.csproj -pp:artifacts\preprocessed.xml
```

Unit tests for the SDK-style test project:

```powershell
dotnet test Tests\Example.Core.Tests\Example.Core.Tests.csproj -c Release
```

Keep `artifacts\` and similar log locations ignored by version control.
Binary logs embed project and imported files, task command lines, and the
environment variables that influence the build. MSBuild documents that this
reduces but does not eliminate the risk of leaking sensitive values, so
review a log before sharing it outside the team.

## Restore Rules

- Use `-restore` with the build rather than `-t:Restore;Build`. NuGet runs
  restore and build evaluations with different global properties, and the
  combined form is documented as unpredictable.
- An old-style project that references an SDK-style project needs restore
  even if it has no packages of its own, because the referenced project
  needs its `project.assets.json`.
- `packages.config` projects restore through MSBuild 16.5 or later with
  `-t:restore -p:RestorePackagesConfig=true`; `dotnet` does not support that
  format.

## PowerShell Quoting

PowerShell can split or reinterpret arguments that contain semicolons,
commas, or `$`. Quote lists of properties or targets:

```powershell
& $msbuild Example.sln '-p:Configuration=Release;Platform=Any CPU'
```

Inside a quoted argument, PowerShell expands `$name` in double quotes but not
in single quotes. Prefer single quotes for literal MSBuild syntax such as
`$(Configuration)`.

## Validate Data Files in the Build

A host plugin often ships data files (XML definitions, configuration) that
the host binds to the plugin's types by name when it loads them. A typo in
a type name compiles cleanly and fails only inside the host, sometimes
silently. If a validator can check the files against the host's assembly
and the assembly just built, run it as part of every build:

```xml
<!-- After Build: check the data files against the DLL just built.
     Skip once with -p:SkipDataValidation=true. -->
<Target Name="ValidateData"
        AfterTargets="Build"
        Condition="'$(SkipDataValidation)' != 'true' And '$(OS)' == 'Windows_NT'">
  <Exec Command="powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File &quot;$(MSBuildProjectDirectory)\..\Tools\validate-data.ps1&quot; -Assembly &quot;$(TargetPath)&quot;"
        IgnoreExitCode="true">
    <Output TaskParameter="ExitCode" PropertyName="ValidateDataExitCode" />
  </Exec>
  <Error Condition="'$(ValidateDataExitCode)' != '0'"
         Text="Data validation failed; see the errors above." />
</Target>
```

- Pass `$(TargetPath)` so each configuration checks its own output, not a
  stale Release DLL left by an earlier build.
- Print each problem in the canonical diagnostic form,
  `<file>: error <CODE>: <message>`. `Exec` recognises that form, so the
  problem appears in the build's error list and an IDE's error window
  with its file. Print nothing else on success, or a one-line summary.
- `IgnoreExitCode` plus an `Error` task gives one clear failure message
  instead of `MSB3073`, and still fails the build.
- Keep the step cheap (seconds), offer an opt-out property for quick
  iterations, and use Windows PowerShell 5.1 when the validator reflects
  over .NET Framework assemblies (see
  [assembly inspection](../assembly-inspection/overview.knack.md)).
- Prove it: break one data file on purpose, confirm the build fails with
  the expected error, then restore the file.

## Exit Codes and Logs

Check `$LASTEXITCODE` after each native command; PowerShell does not stop on
a failing executable by default. When a build fails, keep the summary short
in chat or tickets and attach the binary log or a filtered warnings list
instead of a full diagnostic log.

## Troubleshooting

| Symptom | Likely cause | First check |
| --- | --- | --- |
| MSB3245, then many CS0246 | Host reference not resolved | `-getProperty` on the path property; environment variable set? |
| MSB4803 under `dotnet build` | Task exists only in .NET Framework MSBuild | Build with MSBuild.exe |
| MSB3027 or MSB3021 copying output | Destination locked | Close the host or the process that loaded the DLL |
| CS1069 naming another assembly | Type forwarded from a facade | Reference the named assembly |
| Restore assets missing | Restore skipped | Add `-restore` |
| Output differs between runs | Non-deterministic inputs | Toolchain, references, paths |

## Further Information

- [MSBuild command-line reference](https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-command-line-reference)
- [Find MSBuild with vswhere](https://github.com/microsoft/vswhere/wiki/Find-MSBuild)
- [NuGet pack and restore as MSBuild targets](https://learn.microsoft.com/en-us/nuget/reference/msbuild-targets)
- [Exec task](https://learn.microsoft.com/en-us/visualstudio/msbuild/exec-task)
- [MSBuild and Visual Studio format for diagnostic messages](https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-diagnostic-format-for-tasks)
- [Target build order (`AfterTargets`)](https://learn.microsoft.com/en-us/visualstudio/msbuild/target-build-order)
- [MSBuild binary log documentation](https://github.com/dotnet/msbuild/blob/main/documentation/wiki/Binary-Log.md)
- [Resolve errors for missing assembly references (CS0012, CS1069)](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-messages/assembly-references)
