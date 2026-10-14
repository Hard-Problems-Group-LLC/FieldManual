# Reflection over Closed Assemblies from PowerShell

Reviewed: 2026-10-13

Load this companion after the
[closed-assembly inspection overview](overview.knack.md)
when checking declarations in a closed .NET assembly from a script on
Windows, or when validating data files against its types. Examples use
`$env:EXAMPLE_HOST_DIR`, the folder `ExampleHost_Data\Managed`, the assembly
`Host.Game.dll`, and the namespace `Example.Host`.

## Choose the Reflecting Runtime

Windows PowerShell 5.1 (`powershell.exe`) runs on .NET Framework 4.x.
PowerShell 7 (`pwsh`) runs on modern .NET; 7.4 is built on .NET 8, 7.5 on
.NET 9, and 7.6 on .NET 10. Neither is the host's runtime, and they fail in
different places.

In one hands-on check against a Unity-based host's main assembly, Windows
PowerShell loaded the assembly but `GetTypes()` threw
`ReflectionTypeLoadException` for a few dozen types, each with the loader
message "Non-abstract, non-.cctor method in an interface": default interface
members that .NET Framework cannot load. PowerShell 7 loaded every type.
Conversely, types that depend on APIs that exist only in .NET Framework can
fail under PowerShell 7.

Start with the runtime closer to the host, fall back to the other, handle
partial results, and record which one produced the evidence. For pure
metadata without loading code for execution, `MetadataLoadContext` (from the
`System.Reflection.MetadataLoadContext` package) reads assemblies with an
explicit resolver; it suits a small C# console tool better than an
interactive shell.

## Run in a Child Process

.NET Framework cannot unload an individual assembly; the file stays locked
until every application domain that loaded it is unloaded, which for a
script means until the process exits. Run inspection scripts in a fresh
process:

```powershell
$script = '.\tools\inspect-host.ps1'
powershell.exe -NoProfile -File $script -TypeName Example.Host.Building
pwsh -NoProfile -File $script -TypeName Example.Host.Building
```

Never load the project's own plugin output into a long-lived shell; the lock
makes the next build fail to copy its output (MSB3021 or MSB3027).

## Load and Enumerate Safely

```powershell
param([Parameter(Mandatory)] [string] $TypeName)
$ErrorActionPreference = 'Stop'
$managed = Join-Path $env:EXAMPLE_HOST_DIR 'ExampleHost_Data\Managed'
$asm = [Reflection.Assembly]::LoadFrom((Join-Path $managed 'Host.Game.dll'))
$runtime = [Runtime.InteropServices.RuntimeInformation]::FrameworkDescription
"Runtime: $runtime"
"Assembly: $($asm.FullName)"

try {
    $types = $asm.GetTypes()
}
catch [Reflection.ReflectionTypeLoadException] {
    $types = @($_.Exception.Types | Where-Object { $null -ne $_ })
    Write-Warning "Partial load: $($types.Count) types loaded."
    $_.Exception.LoaderExceptions | Select-Object -First 5 |
        ForEach-Object { Write-Warning $_.Message }
}

$type = $asm.GetType($TypeName, $false)
if (-not $type) { throw "Type not found: $TypeName" }
```

`LoadFrom` uses the load-from context, which lets dependencies in the same
folder be found. `GetTypes()` returns nested and non-public types, throws
`ReflectionTypeLoadException` when some types cannot load, and puts `null` in
`Types` for each failure. It also excludes forwarded types; reflect over the
assembly that defines a type, not a facade.

## Query Declarations

```powershell
$flags = [Reflection.BindingFlags] `
    'Public,NonPublic,Instance,Static,DeclaredOnly'

# Fields, including private ones, with their types.
$type.GetFields($flags) |
    Select-Object Name, FieldType, IsPublic, IsStatic, IsInitOnly

# A method's overloads and whether they can be overridden.
$type.GetMethods($flags) | Where-Object Name -eq 'Tick' |
    ForEach-Object { '{0} virtual={1} abstract={2} declaredBy={3}' -f `
        $_, $_.IsVirtual, $_.IsAbstract, $_.DeclaringType }

# The base-class chain.
for ($t = $type; $t; $t = $t.BaseType) { $t.FullName }

# Enumeration names.
[Enum]::GetNames($asm.GetType('Example.Host.DamageKind', $true))

# Attributes, without running attribute constructors.
$type.GetCustomAttributesData() | ForEach-Object { $_.ToString() }
```

Reflection shows declarations, not behaviour. A virtual method's metadata
cannot reveal that its base body throws; decompile it with `ilspycmd -t`.

Avoid `FieldInfo.GetValue` on static fields and other operations that run
type initializers. A host type's static constructor may call engine code
that crashes or hangs outside the host.

## Validate Data Files

Hosts that map XML elements onto fields often skip unknown names. The
pattern below reports every child element that matches no field on the
declared type or its base types:

```powershell
function Get-FieldNameSet([Type] $Type) {
    $set = New-Object 'System.Collections.Generic.HashSet[string]'
    $flags = [Reflection.BindingFlags]'Public,NonPublic,Instance'
    for ($t = $Type; $t; $t = $t.BaseType) {
        foreach ($f in $t.GetFields($flags)) { [void] $set.Add($f.Name) }
    }
    , $set
}

foreach ($file in Get-ChildItem Data -Recurse -Filter *.xml) {
    $doc = New-Object System.Xml.XmlDocument
    $doc.Load($file.FullName)  # honours the XML encoding declaration
    $elements = $doc.DocumentElement.ChildNodes |
        Where-Object NodeType -eq 'Element'
    foreach ($def in $elements) {
        $typeName = "Example.Host.$($def.LocalName)"
        $defType = $asm.GetType($typeName, $false)
        if (-not $defType) {
            "$($file.Name): unknown type $typeName"
            continue
        }
        $fields = Get-FieldNameSet $defType
        $children = $def.ChildNodes | Where-Object NodeType -eq 'Element'
        foreach ($child in $children) {
            if (-not $fields.Contains($child.LocalName)) {
                "$($file.Name): $($def.LocalName) has no field " +
                    "'$($child.LocalName)'"
            }
        }
    }
}
```

The loop over base types is required: `GetFields` with `NonPublic` does not
return a base class's private fields, even with `FlattenHierarchy`, yet a
host's loader may set them. Filtering on element nodes matters too; a
`FirstChild` test fails when a comment comes first.

Adapt the pattern to the host's rules: a `Class` attribute that selects a
subtype, on plain fields as well as list items; alias attributes on fields;
resolution by full type name before short name; case rules; list and
dictionary element syntax; and custom loaders. Unhandled rules show up as
false positives; record each exception in the script rather than deleting
the report. Check each fix against a copy of the data seeded with a known
mistake, so the validator is shown to fail when it should.

Run the validator only after a successful build of anything it loads. A
failed compile leaves the previous DLL in place, and the validator then
reports problems that no longer exist, or misses new ones.

## Execute Pure Library Code

A host-free library, such as the shared `netstandard2.0` core described in
[Shared netstandard2.0 Logic Libraries](../shared-library/overview.knack.md),
can be executed from either PowerShell version. Reviewers who may not build
can use this to settle numeric questions exactly:

```powershell
$built = 'Source\Example.Core\bin\Release\netstandard2.0\Example.Core.dll'
$newest = Get-ChildItem Source\Example.Core -Recurse -Filter *.cs |
    Sort-Object LastWriteTime | Select-Object -Last 1
if ((Get-Item $built).LastWriteTime -lt $newest.LastWriteTime) {
    throw 'Library is older than its sources; rebuild first.'
}
$copy = Join-Path ([IO.Path]::GetTempPath()) "core-$([guid]::NewGuid()).dll"
Copy-Item $built $copy   # keep the build output unlocked
$core = [Reflection.Assembly]::LoadFile($copy)
$calc = $core.GetType('Example.Core.Geometry', $true)
$calc.GetMethod('Area').Invoke($null, @([double] 3, [double] 4))
```

`GetType` with `$true` throws a clear error for a wrong name; without it, a
misspelt namespace returns `$null` and fails later as "You cannot call a
method on a null-valued expression". Calling host code this way is unsafe,
as described above; calling the pure library is not.

## PowerShell Sharp Edges

- PowerShell's XML adapter exposes attributes as properties. On an element
  with a `Name="..."` attribute, `$element.Name` returns the attribute value,
  not the element name, in both PowerShell 5.1 and 7. Use `LocalName`.
- PowerShell unrolls collections returned from functions; the comma in
  `, $set` returns the set itself.
- A type literal such as `[Example.Host.Building]` resolves only after the
  assembly is loaded and only in the current session; prefer
  `$asm.GetType(...)` in scripts.
- `GetCustomAttributes()` runs attribute constructors; prefer
  `GetCustomAttributesData()` when only reading.

## Further Information

- [Differences between Windows PowerShell 5.1 and PowerShell 7](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell)
- [`Assembly.GetTypes`](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.assembly.gettypes)
- [Best practices for assembly loading (.NET Framework)](https://learn.microsoft.com/en-us/dotnet/framework/deployment/best-practices-for-assembly-loading)
- [Load and unload assemblies](https://learn.microsoft.com/en-us/dotnet/standard/assembly/load-unload)
- [Inspect assembly contents using MetadataLoadContext](https://learn.microsoft.com/en-us/dotnet/standard/assembly/inspect-contents-using-metadataloadcontext)
