# Shared Library Project Files

Reviewed: 2026-10-13

Load this companion after the
[shared-library overview](overview.knack.md) when
writing or reviewing the three project files. Examples use the neutral names
`Example.Core`, `Example.Plugin`, and `Example.Core.Tests`, and the
environment variable `EXAMPLE_HOST_DIR`. Version numbers shown as `x.y.z`
are placeholders; the consuming project pins reviewed versions.

## Layout

```text
Example.sln
Directory.Build.props            optional shared settings (see below)
Source/
  Example.Core/                  netstandard2.0, SDK-style
  Example.Plugin/                net472, old-style or SDK-style
Tests/
  Example.Core.Tests/            net8.0 or later, xUnit.net
Data/                            files the host loads at run time
```

## Core Library

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <AssemblyName>Example.Core</AssemblyName>
    <!-- netstandard2.0 defaults to C# 7.3. Pin a number every supported
         build machine understands; see the language companion. -->
    <LangVersion>12.0</LangVersion>
    <Nullable>enable</Nullable>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
  <ItemGroup>
    <InternalsVisibleTo Include="Example.Core.Tests" />
  </ItemGroup>
</Project>
```

- A numeric `LangVersion` keeps the build identical across machines.
  Microsoft advises against `latest`, whose meaning follows whichever compiler
  is installed.
- SDK-style projects are deterministic by default.
- The .NET SDK turns the `InternalsVisibleTo` item into an assembly attribute
  for a `netstandard2.0` target, so tests can reach `internal` members without
  widening the public contract.
- Reference only packages that support `netstandard2.0`. Each package
  dependency is another assembly that must reach the host's plugin folder;
  confirm that the plugin's build output contains it.

## Polyfill File

Records and `init` accessors need a type that `netstandard2.0` lacks:

```csharp
// Example.Core/IsExternalInit.cs
namespace System.Runtime.CompilerServices
{
    /// <summary>
    /// Compiler support type absent from netstandard2.0. Records and init
    /// accessors refer to it.
    /// </summary>
    internal static class IsExternalInit
    {
    }
}
```

The compiler matches this type by full name and prefers a definition in the
project being compiled. Keep it `internal` so it never collides with the real
type in .NET 5 and later or with another library's copy. The language
companion lists the other compiler-required types.

## Test Project

xUnit.net v3 supports .NET 8 or later and .NET Framework 4.7.2 or later, the
latter officially on Windows only. Its test projects are executables. The
v2 `xunit` package is marked deprecated on NuGet and receives security fixes
only. Generate new test projects from the current template rather than
copying a package list:

```text
dotnet new install xunit.v3.templates
dotnet new xunit3 --output Tests/Example.Core.Tests
```

The template offers a choice between Microsoft Testing Platform and VSTest
for `dotnet test`; VSTest remains `dotnet test`'s default unless a
`global.json` selects the other runner (.NET 10 SDK and later). With VSTest,
the project needs `Microsoft.NET.Test.Sdk` and `xunit.runner.visualstudio`.
Without the test SDK the project still builds, but `dotnet test` cannot run
it. One project saw `dotnet test` report no tests and succeed; in a check
for this knack (xUnit.net 2.7, .NET 9 SDK) it aborted with exit code 1
because package assemblies were missing from the output. Guard against the
silent case in automation by checking that the reported test count is above
a known minimum. Then add the core reference:

```xml
<ItemGroup>
  <ProjectReference
      Include="..\..\Source\Example.Core\Example.Core.csproj" />
</ItemGroup>
```

Do not reference the plugin project or any host assembly from the tests.

## Data Fixtures

Link the host's data files into the test output instead of copying them into
the test tree. The files stay single-sourced and tests do not depend on the
working directory:

```xml
<ItemGroup>
  <None Include="..\..\Data\**\*.xml">
    <Link>Fixtures\Data\%(RecursiveDir)%(Filename)%(Extension)</Link>
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </None>
</ItemGroup>
```

```csharp
string root = Path.Combine(AppContext.BaseDirectory, "Fixtures", "Data");
```

Useful fixture tests check that every file parses, that identifiers are
unique, that numeric fields fall in documented ranges, and that values fixed
by earlier defects stay fixed. Element names can also be checked against the
host's real fields by reflection outside the test run; see
[Closed-Assembly Inspection](../assembly-inspection/overview.knack.md).

## Running Tests on .NET Framework Too

When a behaviour depends on the runtime, multi-target the tests on Windows:

```xml
<TargetFrameworks>net8.0;net472</TargetFrameworks>
```

`dotnet test` then runs both targets. Building `net472` needs the .NET
Framework reference assemblies, from an installed targeting pack or the
`Microsoft.NETFramework.ReferenceAssemblies` package. This narrows the gap
to a .NET Framework host but does not close it; a Mono-based host has its
own base library.

## Plugin Reference to the Core

```xml
<ItemGroup>
  <ProjectReference Include="..\Example.Core\Example.Core.csproj" />
</ItemGroup>
```

An old-style project can reference the SDK-style core with MSBuild 17
(Visual Studio 2022). Build with `-restore`, because the core needs its
restore assets before it compiles. The core's DLL is copied to the plugin
output by default; ship both. Host references, by contrast, use
`Private=false`; see the
[host-references companion](../framework-builds/references.knack.md).

Project references are not transitive in .NET Framework projects. If the
core references a third project, the plugin cannot compile against that
project's types without its own reference.

## Shared Settings

A `Directory.Build.props` at the repository root can hold settings common to
all three projects, such as `Nullable` and `TreatWarningsAsErrors`. Two
cautions:

- Set `LangVersion` per project. The plugin and the core may need different
  values, and neither should change by accident.
- An old-style project that lacks the top-level import of
  `Microsoft.Common.props` still receives `Directory.Build.props`, but late:
  the common targets import it after the project body, so its values
  override the project's own instead of acting as defaults. Check with
  `MSBuild.exe Example.Plugin.csproj -getProperty:Name` or `-pp`.

## Review Checklist

- Does the core target only `netstandard2.0` and reference no host assembly?
- Is `LangVersion` numeric, with polyfills internal and in the right
  namespace?
- Was the test project generated from the current xUnit.net template, with
  pinned versions and a discovery path that `dotnet test` can use?
- Are data files linked as fixtures rather than copied?
- Does the plugin output contain the core and every core dependency?
- Do shared settings in `Directory.Build.props` take effect as intended in
  the old-style project?

## Further Information

- [Common MSBuild project items](https://learn.microsoft.com/en-us/visualstudio/msbuild/common-msbuild-project-items)
- [Customize the build by folder](https://learn.microsoft.com/en-us/visualstudio/msbuild/customize-by-directory)
- [Init-only setters specification](https://github.com/dotnet/csharplang/blob/main/proposals/csharp-9.0/init.md)
- [xUnit.net v3 getting started](https://xunit.net/docs/getting-started/v3/getting-started)
- [Deprecated `xunit` v2 package](https://www.nuget.org/packages/xunit)
- [`Microsoft.NETFramework.ReferenceAssemblies`](https://www.nuget.org/packages/Microsoft.NETFramework.ReferenceAssemblies)
- [NuGet restore target](https://learn.microsoft.com/en-us/nuget/reference/msbuild-targets#restore-target)
