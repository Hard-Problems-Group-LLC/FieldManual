# Shared netstandard2.0 Logic Libraries

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when code must run inside a host that a unit test cannot
start, typically a plugin or extension for a closed application that loads
.NET Framework assemblies, and the project still wants fast automated tests.
It describes splitting the work into a host-independent library, a thin host
adapter, and a modern test project.

Also load the [project-file companion](projects.knack.md)
when writing the three project files, and the
[C# language companion](CSharp.knack.md)
when choosing language features for the library. For building the
host-facing project on Windows, load
[.NET Framework Builds](../framework-builds/overview.knack.md).

## Mental Model

Host-bound code cannot run outside the host. Its types depend on engine
state, native calls, static initializers, or assemblies licensed only for use
inside the product. A unit test that touches them fails to load, crashes, or
quietly tests an imitation of the host.

Split the plugin into three projects:

1. **Core library**: `netstandard2.0`, SDK-style. Pure logic such as rules,
   formulas, schedules, weighted choices, parsers, validators, and text
   builders. It references no host assembly.
2. **Host adapter**: the plugin assembly the host loads, targeting the
   host's framework (for example `net472`), possibly in an old-style project
   file. It reads host state, converts it to core inputs, calls the core, and
   applies the results.
3. **Test project**: a current .NET target such as `net8.0` with xUnit.net.
   It references only the core.

Cover the adapter with in-host smoke tests: scripted runs of the real host
that exercise the plugin and fail on errors (see
[In-Host Smoke Testing](../../software-engineering/testing/in-host-smoke/overview.knack.md)).
Unit tests and smoke tests answer different questions; neither replaces the
other.

`netstandard2.0` is the bridge because it is the newest .NET Standard version
that .NET Framework implements. Microsoft recommends it for code shared
between .NET Framework and other .NET implementations, and recommends .NET
Framework 4.7.2 or later for projects that consume .NET Standard 2.0
libraries. Microsoft's table lists Unity support for .NET Standard 2.0 from
Unity 2018.1.

## What Belongs in the Core

Move logic to the core when it can be expressed over plain inputs:

- numbers, strings, enumerations, and small immutable records;
- values the adapter samples from the host, such as a tick count or a random
  draw; and
- narrow interfaces or delegates for the few queries the logic needs.

Keep host types, handles, singletons, reads and writes of host state, and
anything whose behaviour is known only from running the host in the adapter.

A simple placement test: if a function needs a running host to give a
meaningful answer, it belongs in the adapter; if it needs only data, it
belongs in the core.

Make the core deterministic. Pass time as a value and randomness as an
injected source or a pre-drawn sample so tests can pin both. Validate inputs
at the core boundary and test the edges. A host's random source may return an
endpoint, such as exactly `1.0`, that the core's contract excludes; clamp or
reject it in the adapter and write a test for that boundary.

## Contract-First Workflow

Split the work so the library and the adapter can be written in parallel:

1. Write the core's public types and method signatures first, with XML
   documentation stating inputs, outputs, units, ranges, and failure
   behaviour. Bodies may throw `NotImplementedException`.
2. Build all three projects and commit the contract.
3. Implement the core and its tests on one track while the adapter is
   written against the contract on another. Give parallel builders separate
   worktrees; concurrent builds of one project directory collide in `obj/`.
4. Integrate, run the unit tests, build the plugin, and run the in-host
   smoke test.

Treat a later contract change as its own reviewed commit. Prefer stubs that
throw over stubs that return plausible defaults: a forgotten stub then fails
loudly in the first test or smoke run.

## Testing the Split

- Unit-test the core thoroughly: boundaries, invalid input, and regressions.
- Test the data files the host will load (XML, JSON, tables) from the test
  project by linking them in as fixtures. Such tests catch invalid values and
  misspelt names without starting the host.
- Keep the adapter thin enough that a smoke run reaches every adapter path.
- Prefer passing data into the core over mocking host objects, following
  FieldManual's [test standard](../../../standards-and-practices/core/test-development-and-mock-use.md).
- Because the built core runs anywhere, reviewers who may not build can
  still execute it from PowerShell to settle numeric questions exactly; see
  the [reflection companion](../assembly-inspection/reflection.PowerShell.knack.md).

## Same Binary, Different Runtimes

The test project runs the core on modern .NET; the host runs it on .NET
Framework, Mono, or another implementation. The compiled library is
identical, but the base class library behind it is not. Verified examples:

- `double.ToString()` returns the shortest round-trippable string on .NET
  Core 3.0 and later, but 15 significant digits on .NET Framework, so
  `(0.1 + 0.2).ToString(CultureInfo.InvariantCulture)` yields
  `0.30000000000000004` in a `net8.0` test and `0.3` on .NET Framework.
- `string.GetHashCode()` varied between runs of the same program on .NET 8
  and was stable on .NET Framework; Microsoft documents that it may differ
  across implementations, versions, and processes and must not be persisted.
- .NET 5 and later use ICU for globalization on current Windows versions,
  while .NET Framework uses NLS; culture-sensitive comparison, sorting, and
  casing can differ.

A passing unit test proves the logic, not the host runtime's formatting or
collation. Keep formatting and comparison explicit in the core (see
[Culture-Safe Formatting](../culture-formatting/overview.knack.md)).
When runtime behaviour matters, also run the tests on `net472` on Windows
and keep the smoke test.

## Deployment

The core is a second assembly that ships beside the plugin. A project
reference copies it to the plugin's output by default; keep that, and make
sure packaging includes it. Give it a distinctive assembly name so it cannot
be confused with another plugin's library in the same host process. Before
committing to the pattern, prove with a one-type spike that the host loads a
`netstandard2.0` assembly from the plugin folder.

## Sharp Edges

- `netstandard2.0` defaults to C# 7.3. Raising `LangVersion` is common but
  outside Microsoft's support statement; use only compile-time features and
  polyfills, as the language companion describes.
- Familiar APIs such as `Math.Clamp`, `HashCode`, and
  `Dictionary.GetValueOrDefault` are absent from `netstandard2.0`. The
  compiler catches them, but code copied from modern samples often uses them.
- The `netstandard2.0` reference assemblies carry no nullable annotations, so
  nullable analysis in the core is weaker than in the test project.
- A host can load the adapter yet fail on its first call into the core if the
  core assembly is missing from the deployed folder.
- Logic duplicated "temporarily" in the adapter escapes testing. Move it into
  the core or delete it.

## Review Checklist

- Does the core reference only base-library and portable packages, never a
  host assembly?
- Are time, randomness, and host queries injected?
- Does the contract document units, ranges, and failure behaviour?
- Do tests cover boundaries, invalid input, and the host's data files?
- Is formatting explicit wherever output must be stable?
- Is the core deployed with the plugin and exercised by a smoke run?

## Further Information

- [.NET Standard overview](https://learn.microsoft.com/en-us/dotnet/standard/net-standard)
- [Cross-platform targeting for .NET libraries](https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/cross-platform-targeting)
- [C# language versioning](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-versioning)
- [Globalization and ICU](https://learn.microsoft.com/en-us/dotnet/core/extensions/globalization-icu)
- [Floating-point parsing and formatting improvements in .NET Core 3.0](https://devblogs.microsoft.com/dotnet/floating-point-parsing-and-formatting-improvements-in-net-core-3-0/)
- [`String.GetHashCode` remarks](https://learn.microsoft.com/en-us/dotnet/api/system.string.gethashcode)
- [xUnit.net v3 getting started](https://xunit.net/docs/getting-started/v3/getting-started)
