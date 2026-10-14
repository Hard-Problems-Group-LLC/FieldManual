# .NET Framework Builds on Windows

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when building .NET Framework projects on Windows from a
command line, script, continuous-integration agent, or AI agent, especially
old-style (non-SDK) project files for plugins of closed hosts. It covers
toolchain choice, a repeatable build sequence, determinism, warnings, and
parallel builders.

Load the [MSBuild command-line companion](msbuild.knack.md)
for locating MSBuild and choosing switches, and the
[host-references companion](references.knack.md)
for referencing a closed host's assemblies, Unity module assemblies, and
linked content. For splitting testable logic out of the plugin, see
[Shared netstandard2.0 Logic Libraries](../shared-library/overview.knack.md).
For finding and living with Visual Studio itself, including updates,
developer shells, solutions, and binary logs, see
[Visual Studio from Scripts and Agents](../visual-studio/overview.knack.md).

## Mental Model

There are two families of project file and two MSBuild engines.

**Old-style project files** start with
`<Project ToolsVersion="..." xmlns="http://schemas.microsoft.com/developer/msbuild/2003">`,
list every source file in a `Compile` item, name the framework with
`TargetFrameworkVersion` (for example `v4.7.2`), and import
`Microsoft.CSharp.targets`. Older plugin templates still use them.

**SDK-style project files** start with `<Project Sdk="Microsoft.NET.Sdk">`,
include source files by globbing, name the framework with `TargetFramework`
(for example `net472`, `netstandard2.0`, or `net8.0`), and restore
`PackageReference` items.

**MSBuild.exe** ships with Visual Studio and Visual Studio Build Tools and
runs on .NET Framework. It builds everything Visual Studio builds.

**`dotnet build`** runs the .NET SDK's MSBuild on modern .NET. Some tasks do
not exist there; such builds fail with MSB4803, "The task ... is not
supported on the .NET Core version of MSBuild. Please use the .NET Framework
version of MSBuild." COM references are the documented example. It also
needs .NET Framework reference assemblies from an installed targeting pack or
the `Microsoft.NETFramework.ReferenceAssemblies` package.

Treat Visual Studio's MSBuild.exe as the reference build for .NET Framework
projects. `dotnet build` can succeed on a simple old-style project when a
targeting pack happens to be installed, but that is a property of one
machine, not a contract. Use `dotnet build` and `dotnet test` freely for
SDK-style projects with modern targets, such as a test project.

## Build Sequence

1. Locate MSBuild with `vswhere`. Installation paths differ by Visual Studio
   release and edition; never hard-code one.
2. Provide the host's install location through an environment variable that
   the project reads, and fail fast if it is missing.
3. Build with restore:
   `MSBuild.exe Example.Plugin.csproj -restore -p:Configuration=Release`.
   Use `-restore`, not `-t:Restore;Build`; NuGet documents the combined
   target form as unpredictable.
4. Run the unit tests with `dotnet test` against the test project.
5. Before declaring a change complete, verify a clean compile with
   `-t:Rebuild`, and periodically build from a fresh clone.
6. Deploy the output and run the in-host smoke test.

## Determinism

SDK-style projects are deterministic by default; set
`<Deterministic>true</Deterministic>` explicitly in old-style projects. With
determinism, identical inputs produce identical bytes. Microsoft's list of
inputs includes the compiler version, every referenced assembly, and the
current directory path, so:

- a host update changes the plugin's bytes even when its source does not;
- two checkouts at different paths can produce different outputs; and
- comparing outputs is meaningful only with the same toolchain, host
  assemblies, and paths.

## Warnings Are Signals

Aim for zero warnings and keep it there; a new warning is then visible.
Several MSBuild warnings precede real failures:

- **MSB3245**, "Could not resolve this reference": a host assembly is
  missing, misnamed, or behind an unset environment variable.
- **MSB3277**, "Found conflicts between different versions": two
  dependencies want different versions of one assembly.
- **MSB3027**, "Could not copy ... Exceeded retry count": usually the
  destination is locked, for example by a running host that has loaded the
  previous plugin build.

Compiler warnings carry information too. CS0108, "hides inherited member",
on a plugin field can reveal that the host's base class already manages that
state, and CS0162, "Unreachable code detected", can reveal an experiment's
early return left behind.

Once the build is clean, enforce it in automation with `-warnAsError`.
Suppress a specific code only with a recorded reason. Trust only builds you
saw succeed: a failed compile leaves the previous DLL in place for tests and
deployment to pick up.

## Parallel Builders

Each project writes intermediate files and restore assets
(`project.assets.json` and generated `nuget.g.props` files) under its own
`obj/` directory, and its output under `bin/` or a configured
`OutputPath`. Two builds of the same project directory at the same time,
such as two agents, an IDE background build and a command-line build, or a
build and a test run, write the same files. Results range from
file-in-use failures to mixed, stale output.

Give each parallel builder its own Git worktree, which has its own `obj/`
and `bin/`, or serialize builds. A worktree does not help when `OutputPath`
or a deployment step points at a shared absolute directory; make those
per-worktree as well.

## Sharp Edges

- An unset environment variable in a `HintPath` collapses
  `$(EXAMPLE_HOST_DIR)\Managed\Host.dll` to `\Managed\Host.dll`, which
  resolves against the current drive's root. MSBuild then reports only
  warning MSB3245, followed by a flood of CS0246 errors or, if the reference
  is unused, a successful build. Add a guard target that fails with a clear
  message.
- In an old-style project, every new source file must be added to a
  `Compile` item. A file that is only on disk is silently not compiled.
- Project references are not transitive in .NET Framework projects.
- An old-style project without a top-level import of
  `Microsoft.Common.props` imports `Directory.Build.props` late, so its
  values override the project's own.
- MSBuild treats environment variables as trusted inputs that can redirect
  build logic. Set them deliberately in scripts and agents; do not inherit
  arbitrary values from a shared shell.
- MSBuild reuses worker nodes after a build by default. Pass
  `-nodeReuse:false` in automation that needs a clean process tree.
- MSBuild keeps whitespace inside property and metadata values. Never wrap a
  `HintPath`, `Configuration`, or other value across lines to satisfy a
  line-length rule; exempt project files from such rules.
- Debug and Release builds write to different folders, and `dotnet build`
  defaults to Debug. Name the configuration in every command and deploy from
  the folder that command produced.

## Review Checklist

- Is MSBuild located through `vswhere`, not a hard-coded path?
- Do host paths come from an environment variable, guarded by a target that
  fails clearly?
- Does the scripted build use `-restore`, a named configuration, and a
  documented clean-rebuild check?
- Is the build warning-free, with any suppression justified?
- Is `Deterministic` set in old-style projects?
- Do parallel builders use separate worktrees and output locations?

## Further Information

- [MSBuild command-line reference](https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-command-line-reference)
- [MSB4803](https://learn.microsoft.com/en-us/visualstudio/msbuild/errors/msb4803),
  [MSB3245](https://learn.microsoft.com/en-us/visualstudio/msbuild/errors/msb3245),
  [MSB3277](https://learn.microsoft.com/en-us/visualstudio/msbuild/errors/msb3277),
  and [MSB3027](https://learn.microsoft.com/en-us/visualstudio/msbuild/errors/msb3027)
- [NuGet restore and build in one command](https://learn.microsoft.com/en-us/nuget/reference/msbuild-targets#restoring-and-building-with-one-msbuild-command)
- [C# deterministic compilation](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/code-generation#deterministic)
- [Customize the build by folder](https://learn.microsoft.com/en-us/visualstudio/msbuild/customize-by-directory)
- [Use environment variables in a build](https://learn.microsoft.com/en-us/visualstudio/msbuild/how-to-use-environment-variables-in-a-build)
- [Find MSBuild with vswhere](https://github.com/microsoft/vswhere/wiki/Find-MSBuild)
- [git-worktree](https://git-scm.com/docs/git-worktree)
