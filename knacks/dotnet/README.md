# .NET Knacks

Reviewed: 2026-10-13

These knacks cover building, testing, and verifying .NET code that runs
inside a host the project does not control, such as a plugin or extension
for a closed application, with emphasis on .NET Framework hosts on Windows.
They separate host-independent logic from host-bound code, describe the
Windows build toolchain and Visual Studio, show how to verify a closed
host's behaviour before relying on it, and keep machine-readable text
stable across cultures and runtimes.

## Contents

- [Shared netstandard2.0 Logic Libraries](shared-library/overview.knack.md)
  — a testable core shared by a .NET Framework plugin and a modern xUnit.net
  test project, contract-first parallel work, and runtime differences
  between tests and host
  - [Project files](shared-library/projects.knack.md)
    — library, test, and plugin project shapes, polyfill, fixtures,
    multi-targeted tests, and shared settings
  - [C# language features on netstandard2.0](shared-library/CSharp.knack.md)
    — the `LangVersion` decision, compiler-required types, runtime-only
    features, nullable analysis, and missing APIs
- [.NET Framework Builds on Windows](framework-builds/overview.knack.md)
  — MSBuild.exe versus `dotnet build`, a repeatable build sequence,
  determinism, warnings, and parallel builders
  - [MSBuild command line](framework-builds/msbuild.knack.md)
    — locating MSBuild with `vswhere`, switches, recipes, restore rules, and
    troubleshooting
  - [Host assembly references](framework-builds/references.knack.md)
    — environment-variable paths, guard targets, `Private=false`, Unity
    module assemblies, and linked content
- [Visual Studio from Scripts and Agents](visual-studio/overview.knack.md)
  — instances and versions, locating with `vswhere`, choosing MSBuild,
  updates that change the toolchain, developer shells, and working beside
  the IDE
  - [Discovery and developer shells](visual-studio/discovery.PowerShell.knack.md)
    — `vswhere` queries, MSBuild binaries, version records, Developer
    PowerShell, and `VsDevCmd.bat`
  - [Installer](visual-studio/installer.knack.md)
    — unattended updates, exit codes, rollback, Microsoft Update delivery,
    and `.vsconfig` files
  - [Solutions and projects](visual-studio/solutions.knack.md)
    — solution-file format and editing, configurations and output folders,
    mixed project styles, linked content, and `.vs` hygiene
  - [Diagnostics](visual-studio/diagnostics.knack.md)
    — binary logs, IDE build logs, stale-output checks, and file locks
    beside an open IDE
- [Closed-Assembly Inspection](assembly-inspection/overview.knack.md)
  — licence caveats, evidence levels, reading before calling, and reading
  decompiled code
  - [ilspycmd](assembly-inspection/ilspycmd.knack.md)
    — pinned installation, type and project decompilation, searching, and
    output hygiene
  - [Reflection from PowerShell](assembly-inspection/reflection.PowerShell.knack.md)
    — Windows PowerShell versus PowerShell 7, safe enumeration, declaration
    queries, and data-file validation
- [Culture-Safe Formatting](culture-formatting/overview.knack.md)
  — machine versus human text, invariant formatting and parsing, ordinal
  comparison, plugin etiquette, and culture testing
  - [Numbers and dates in C#](culture-formatting/CSharp.knack.md)
    — invariant APIs on netstandard2.0, `NumberStyles`, floating-point text
    across runtimes, and stable-text techniques

## Load Order

For a new host plugin, start with Shared netstandard2.0 Logic Libraries,
then .NET Framework Builds on Windows, and Visual Studio from Scripts and
Agents when scripts or agents drive the toolchain. Load Closed-Assembly
Inspection before calling, overriding, or depending on host members, and
Culture-Safe Formatting whenever code writes or reads numbers, dates, or
identifiers as text. Add each companion when the work reaches its concrete
project file, command, or API.

In-host smoke testing of the adapter layer is covered by
[In-Host Smoke Testing](../software-engineering/testing/in-host-smoke/overview.knack.md).

## Boundaries

- The decompilation licence section flags a legal question without
  answering it; consult the licensor or qualified counsel.
- Observations recorded in these knacks name the runtimes and tool versions
  they were made with. Re-check them when those change.
- Consuming projects own their supported .NET, Visual Studio, and host
  versions and their build and test commands, as the
  [language standards](../../standards-and-practices/languages/README.md)
  describe.
