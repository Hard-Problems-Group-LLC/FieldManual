# ilspycmd

Reviewed: 2026-10-13

Load this companion after the
[closed-assembly inspection overview](overview.knack.md)
when decompiling .NET assemblies from a command line. `ilspycmd` is the
command-line front end of ILSpy, distributed as a .NET tool. Read the
overview's licence section before decompiling third-party code. Examples use
PowerShell, the ignored folder `.local\`, and the host assembly
`Host.Game.dll` under `$env:EXAMPLE_HOST_DIR`.

## Install a Pinned Version Locally

Install into a tool path inside an ignored folder rather than globally, and
pin the version:

```powershell
dotnet tool install ilspycmd --version <pinned-version> `
    --tool-path .local\tools
.\.local\tools\ilspycmd.exe --version
```

Pin because each release targets a particular .NET runtime. On nuget.org,
the 9.1.0 release targets .NET 8, while the 10.0.0 and 11.1.0 releases target
.NET 10. With only a .NET 9 SDK installed, installing the 11.1.0 release
failed with a misleading message:

```text
The settings file in the tool's NuGet package is invalid: Settings file
'DotnetToolSettings.xml' was not found in the package.
```

`--allow-roll-forward`, available from the .NET 9 SDK, did not change that
result; it lets an installed tool run on a newer runtime, not let an older
SDK install a tool built for a newer framework. Check the target framework on
the package's nuget.org page and pick the newest release that the installed
SDK supports, or install a newer SDK.

For a team, a local tool manifest records the version in the repository
without committing binaries:

```powershell
dotnet new tool-manifest
dotnet tool install ilspycmd --version <pinned-version>
dotnet tool restore
dotnet ilspycmd --version
```

`dotnet tool` warns that a `--tool-path` directory must be trusted, because
tools there run directly. Keep it inside the project's private local area.

## Core Commands

Options vary by release; run `ilspycmd --help` for the pinned version.

List entities by kind (`c` classes, `i` interfaces, `s` structs, `d`
delegates, `e` enums):

```powershell
Set-Alias ilspycmd .\.local\tools\ilspycmd.exe   # tool-path install
$refs = Join-Path $env:EXAMPLE_HOST_DIR 'ExampleHost_Data\Managed'
$dll = Join-Path $refs 'Host.Game.dll'
$out = Join-Path .local\decompiled (Get-Item $dll).VersionInfo.FileVersion
ilspycmd -l c $dll | Select-String 'Building'
```

Decompile one type to the console or a file:

```powershell
New-Item -ItemType Directory -Force $out | Out-Null
ilspycmd -t Example.Host.Building -r $refs $dll |
    Set-Content (Join-Path $out 'Building.cs')
```

Decompile the whole assembly as a project, one file per type, with
namespace folders:

```powershell
ilspycmd -p --nested-directories -o (Join-Path $out 'Host.Game') `
    -r $refs --disable-updatecheck $dll
```

`-p` requires `-o`. A whole-assembly decompile of a large game assembly took
minutes in practice; run it once per host version and search the result.

Show IL when the C# rendering is unclear:

```powershell
ilspycmd -il -t Example.Host.Building $dll
```

## Useful Options

| Option | Purpose |
| --- | --- |
| `-o`, `--outputdir` | Output directory; required with `-p`. |
| `-p`, `--project` | Emit a compilable-style project. |
| `-t`, `--type` | Decompile one fully qualified type. |
| `-l`, `--list` | List classes, interfaces, structs, delegates, or enums. |
| `-r`, `--referencepath` | Directory of dependencies, for better resolution. |
| `-il`, `--ilcode` | Show IL instead of C#. |
| `-lv`, `--languageversion` | Choose the C# version used for output. |
| `--nested-directories` | Use namespace folders in project output. |
| `--disable-updatecheck` | Skip the online update check in automation. |
| `-genpdb`, `-usepdb` | Generate a PDB, or use names from an existing PDB. |

Newer releases add options such as `-m` for a single member and
`--list-resources`; confirm them in the pinned release's help.

## Searching the Output

Use a fast search tool over the decompiled tree:

```powershell
$tree = Join-Path $out 'Host.Game'
rg -n 'override void Tick\(' $tree
rg -n 'NotImplementedException' (Join-Path $tree 'Example\Host')
rg -n --fixed-strings 'Could not find' $tree
```

Search for:

- overrides of a virtual method, to see how the host's own subclasses use
  it;
- callers of a method, to learn the order of operations;
- literal log and exception messages seen at run time; and
- `NotImplementedException` or empty bodies in base classes.

## Output Hygiene

- Put output under a folder named for the host assembly's file version, as
  the examples do, so evidence and host version stay together.
- Confirm that the folder is ignored: `git check-ignore -v <path>`.
- Delete output for host versions no longer supported.
- Do not feed whole decompiled files into issues, reviews, or prompts; quote
  the minimum.

## Sharp Edges

- Different `ilspycmd` releases render the same IL differently. Note the
  release with any quoted excerpt.
- Missing `-r` references can degrade output and produce warnings about
  unresolved types.
- Decompiled projects rarely compile cleanly and must not be used as a build
  input.
- The update check contacts the network unless disabled.

## Further Information

- [ILSpy repository](https://github.com/icsharpcode/ILSpy)
- [ilspycmd README and help](https://github.com/icsharpcode/ILSpy/blob/master/ICSharpCode.ILSpyCmd/README.md)
- [ilspycmd on NuGet, with versions and target frameworks](https://www.nuget.org/packages/ilspycmd)
- [`dotnet tool install`](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-tool-install)
- [.NET tools and local tool manifests](https://learn.microsoft.com/en-us/dotnet/core/tools/global-tools)
