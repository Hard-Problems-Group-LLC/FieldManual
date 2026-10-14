# Referencing a Closed Host's Assemblies

Reviewed: 2026-10-13

Load this companion after the
[.NET Framework builds overview](overview.knack.md) when
a project compiles against assemblies that belong to an installed host
application, including Unity-based hosts, or when linking non-code content
into a project. Examples use the environment variable `EXAMPLE_HOST_DIR`,
the managed-assembly folder `ExampleHost_Data\Managed`, and the host
assembly `Host.Game.dll`. A real host's layout will differ.

## Reference Through an Environment Variable

Each developer and build agent installs the host in a different place. Keep
the location out of the project file:

```xml
<PropertyGroup>
  <!-- Set EXAMPLE_HOST_DIR to the host's install folder. -->
  <HostManaged>$(EXAMPLE_HOST_DIR)\ExampleHost_Data\Managed</HostManaged>
</PropertyGroup>
<ItemGroup>
  <Reference Include="Host.Game">
    <HintPath>$(HostManaged)\Host.Game.dll</HintPath>
    <Private>false</Private>
  </Reference>
</ItemGroup>
<Target Name="CheckHostAssemblies"
        BeforeTargets="ResolveAssemblyReferences"
        Condition="!Exists('$(HostManaged)\Host.Game.dll')">
  <Error Text="Host assemblies not found under '$(HostManaged)'.
Set EXAMPLE_HOST_DIR to the host's install folder." />
</Target>
```

MSBuild exposes every environment variable whose name is a valid property
name as a property; a property defined in the project with the same name
wins. Document the variable in the project's build instructions and set it
in each automation definition.

The guard target matters. Without it, an unset variable leaves a
root-relative `HintPath`; MSBuild reports warning MSB3245 and the compiler
follows with errors about unknown types, which hides the cause. If the
reference is unused, the build even succeeds.

Only the message text above is wrapped. Keep `HintPath`, property, and other
values on one line: MSBuild keeps the whitespace of a wrapped value, so a
wrapped path names no file.

Keep every configuration's `OutputPath` outside folders the host scans for
plugins. A host that loads every DLL beneath its plugin folder would load a
nested Debug build as a second copy of the plugin.

## Why `Private=false`

`Private` controls whether a reference is copied to the output folder, the
**Copy Local** setting in Visual Studio. Set it to `false` explicitly for
every host assembly, rather than relying on defaults:

- the host already loads its own copy, and a second copy beside the plugin
  invites version confusion;
- host binaries are usually licensed for use with the product, not for
  redistribution in a plugin package; and
- a smaller output makes packaging mistakes easier to see.

Keep the default copying for the plugin's own dependencies, such as a
shared logic library, because the host does not have them.

## Unity Module Assemblies

Unity splits its engine API across module assemblies such as
`UnityEngine.CoreModule.dll`, `UnityEngine.IMGUIModule.dll`, and
`UnityEngine.TextRenderingModule.dll`. In the Unity-based host examined,
`UnityEngine.dll` forwarded types to those modules, and referencing only
`UnityEngine.dll` produced CS1069:

```text
error CS1069: The type name 'GUI' could not be found in the namespace
'UnityEngine'. This type has been forwarded to assembly
'UnityEngine.IMGUIModule, ...' Consider adding a reference to that assembly.
```

The error names the module to add. Other ways to find the owner before
writing code:

- the Unity Scripting API module pages, for example
  `UnityEngine.IMGUIModule` lists `GUI`, `Event`, and `EventType`, and
  `UnityEngine.TextRenderingModule` lists `TextAnchor`;
- reflection over the module assemblies in the host's managed folder,
  remembering that `Assembly.GetTypes()` excludes forwarded types, so the
  facade itself shows nothing useful; and
- `ilspycmd -l c` or `-l e` against a module to list its classes or enums.

Reference each module the plugin uses, all with `Private=false`, and keep a
short comment naming the types that justify each reference. Unity labels
some modules, such as the text-rendering module, as legacy; hosts can still
depend on them.

## SDK-Style Plugin Projects

An SDK-style `net472` plugin uses the same `Reference` items. Two
differences matter:

- it globs source files, so a stray file in the directory compiles; and
- without an installed targeting pack it needs the
  `Microsoft.NETFramework.ReferenceAssemblies` package to build, including
  under `dotnet build`.

## Link Non-Code Content

Hosts often load data, textures, or documents from folders beside the
plugin. Link them into the project so IDE users can browse the whole tree
without moving files:

```xml
<ItemGroup>
  <None Include="..\Data\**\*.*">
    <Link>Data\%(RecursiveDir)%(Filename)%(Extension)</Link>
    <CopyToOutputDirectory>Never</CopyToOutputDirectory>
  </None>
</ItemGroup>
```

`Link` sets the path shown in Solution Explorer for a file outside the
project's folder. `%(RecursiveDir)` preserves the subfolders matched by
`**`. `CopyToOutputDirectory` set to `Never` keeps browsing separate from
deployment; use `PreserveNewest` only when the build output really is the
deployment layout. A test project can link the same files as fixtures.

## Host Constants and Versions

- A `const` in a host assembly is copied into the plugin at compile time. If
  a host update changes the value, the plugin keeps the old one until it is
  rebuilt. Prefer reading `static readonly` fields or properties when the
  value may change.
- Compile against the host version the plugin supports. A host update can
  remove or change members the plugin calls; the failure appears at run time
  as `MissingMethodException`, `MissingFieldException`, or
  `TypeLoadException`, not at build time. Record the host version used for
  each release and rebuild after host updates.

## Review Checklist

- Do all host paths derive from one environment-backed property?
- Does a guard target fail with an actionable message?
- Is `Private=false` explicit on every host reference?
- Is every referenced Unity module justified, and none missing?
- Is linked content excluded from build output unless deliberately deployed?
- Is the supported host version recorded?

## Further Information

- [Common MSBuild project items](https://learn.microsoft.com/en-us/visualstudio/msbuild/common-msbuild-project-items)
- [Use environment variables in a build](https://learn.microsoft.com/en-us/visualstudio/msbuild/how-to-use-environment-variables-in-a-build)
- [MSB3245](https://learn.microsoft.com/en-us/visualstudio/msbuild/errors/msb3245)
- [Missing assembly reference errors, including CS1069](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-messages/assembly-references)
- [`Assembly.GetTypes` and forwarded types](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly.gettypes)
- [Unity `UnityEngine.IMGUIModule`](https://docs.unity3d.com/ScriptReference/UnityEngine.IMGUIModule.html)
- [Unity `UnityEngine.TextRenderingModule`](https://docs.unity3d.com/ScriptReference/UnityEngine.TextRenderingModule.html)
- [`Microsoft.NETFramework.ReferenceAssemblies`](https://www.nuget.org/packages/Microsoft.NETFramework.ReferenceAssemblies)
- [C# constants and other assemblies](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/constants)
