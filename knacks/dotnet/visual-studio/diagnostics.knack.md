# Build Diagnostics and Working Beside the IDE

Reviewed: 2026-10-13

Load this companion after the
[Visual Studio overview](overview.knack.md) when a build fails
or changes unexpectedly, when an IDE build must be inspected, or when
scripts and an open Visual Studio contend for the same outputs.

## Binary Logs

A binary log records the whole build. Microsoft lists its contents as
diagnostic-level messages, the full text of every imported project file,
final property values and reassignments, items and metadata, and task
inputs and outputs.

```powershell
& $msbuild Example.sln -restore -p:Configuration=Release `
    '-bl:artifacts\build-{}.binlog'
```

- `-bl` writes `msbuild.binlog`; `-bl:<name>.binlog` names it, and `{}` in
  the name becomes a unique timestamp-and-process stamp.
- `dotnet build -bl` writes the same format for SDK-style builds.
- Open logs in the MSBuild Structured Log Viewer.
- Replay a log through any logger by passing it to MSBuild instead of a
  project: `MSBuild.exe artifacts\build.binlog -v:diag`. In observation the
  replay reproduced the original build's output lines.
- Binary logging adds overhead on large builds; enable it when diagnosing.
- Logs embed project files and the environment variables that influence the
  build. Review one before sharing it outside the team.

## Logs from Visual Studio Builds

The IDE's own builds and its design-time builds are not started from a
script. To capture them, start Visual Studio from a shell with:

```powershell
$env:MSBUILDDEBUGENGINE = '1'
$env:MSBUILDDEBUGPATH = "$PWD\artifacts\vs-logs"
& (Join-Path $vsPath 'Common7\IDE\devenv.exe') Example.sln
```

MSBuild then writes binary logs and debugging data for every invocation in
that environment. Remove the variables afterwards; the logs grow quickly.

## Other Quick Diagnostics

| Question | Command |
| --- | --- |
| What value does a property end with? | `-getProperty:Name1,Name2` |
| Which items exist? | `-getItem:Compile` |
| Which file set a property? | `-pp:preprocessed.xml`, then search |
| Which targets ran and in which order? | the binary log |
| Where did the time go? | `-clp:PerformanceSummary` |
| Which project configurations were built? | `-detailedSummary` |

## Trust Only Builds You Saw Succeed

- Check the exit code of every build. The console summary lines
  (`0 Warning(s)`, `0 Error(s)`) belong to the default console logger; the
  terminal logger formats output differently, so do not parse text when an
  exit code will do.
- A failed compile leaves the previous DLL in place. Anything that runs
  afterwards, such as tests, a reflection validator, or an in-host smoke
  test, then exercises old code and can pass or fail for the wrong reason.
  Before trusting such a run, confirm the build succeeded and that the DLL's
  timestamp is newer than every source file it compiles.
- Keep the log of a known clean build as a baseline. After restoring files
  from a deliberate break or an experiment, rebuild with `-t:Rebuild` and
  search the new log for warnings; a forgotten early return, for example,
  leaves CS0162 "Unreachable code detected".
- Compiler warnings can describe the host. CS0108, "hides inherited member",
  on a field named like the base class's field showed that the base already
  managed that state.

## Working Beside an Open IDE

What an open solution does:

- **Design-time builds** run when Visual Studio loads a project, when
  project or `Directory.*` files change, and when configurations switch.
  They run MSBuild targets for IntelliSense and package resolution but do not
  compile or modify outputs. Their results are cached under `.vs\`.
- **IDE builds, debugging, and test runs** write and load the same `bin\`
  and `obj\` files that scripts use.
- **MSBuild worker nodes** stay alive after builds by default, in the IDE and
  on the command line.

What goes wrong: a script's copy step fails with MSB3021 or MSB3027 because a
debugger, test host, or the host application holds the DLL; or the IDE and
a script build the same project at once and leave mixed output.

What to do:

- Stop IDE builds, debugging, and test runs, or close the solution, before
  a scripted clean rebuild.
- Give agents their own worktree so their `bin\` and `obj\` are separate.
- Pass `-nodeReuse:false` in scripts. To stop the IDE leaving nodes behind,
  start it with `MSBUILDDISABLENODEREUSE=1` set, which MSBuild documents for
  exactly this case.
- Look for holders before blaming the build:

```powershell
$names = 'devenv', 'MSBuild', 'testhost', 'vstest.console'
$running = @(Get-Process -Name $names -ErrorAction SilentlyContinue)
$running | Select-Object Name, Id, StartTime
```

With `SilentlyContinue`, `Get-Process` hides the error for a name with no
process but still records it, so a `-Command` invocation whose last
statement is that call exits with code 1 in both PowerShell versions. The
array form above ended with exit code 0. Judge by the array's contents, not
by the exit code of a bare `Get-Process`.

- When a reflection script or a reviewer must load a built DLL, copy it to a
  scratch folder and load the copy, so the build output stays unlocked.

## Review Checklist

- Is a binary log captured for any build being diagnosed, and reviewed before
  sharing?
- Are builds judged by exit code, with stale-output checks before dependent
  runs?
- Is a clean-build baseline kept and compared after experiments?
- Are IDE activity and scripted builds kept apart?
- Is node reuse disabled where locked task or output files have appeared?

## Further Information

- [Obtaining build logs with MSBuild](https://learn.microsoft.com/en-us/visualstudio/msbuild/obtaining-build-logs-with-msbuild)
- [MSBuild command-line reference](https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-command-line-reference)
- [MSBuild binary log documentation](https://github.com/dotnet/msbuild/blob/main/documentation/wiki/Binary-Log.md)
- [MSBuild environment variables](https://github.com/dotnet/msbuild/blob/main/documentation/wiki/MSBuild-Environment-Variables.md)
- [Design-time builds](https://github.com/dotnet/project-system/blob/main/docs/design-time-builds.md)
- [MSBuild Structured Log Viewer](https://msbuildlog.com/)
- [MSB3021](https://learn.microsoft.com/en-us/visualstudio/msbuild/errors/msb3021)
  and [MSB3027](https://learn.microsoft.com/en-us/visualstudio/msbuild/errors/msb3027)
