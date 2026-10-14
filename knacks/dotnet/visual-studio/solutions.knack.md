# Visual Studio Solutions and Projects

Reviewed: 2026-10-13

Load this companion after the
[Visual Studio overview](overview.knack.md) when creating or
editing solution files, mixing old-style and SDK-style projects, linking
non-code content for IDE users, choosing configurations and output folders,
or keeping Visual Studio's generated files out of version control.
Behaviour marked "observed" was checked with Visual Studio 2022 17.14,
MSBuild 17.14, and the .NET 9 SDK.

## Solution Files

A `.sln` file is text that Visual Studio and `dotnet sln` both maintain.
Observed facts:

- Both tools wrote UTF-8 with a byte-order mark and CRLF line endings.
- Each project is a `Project("{type}") = "Name", "path", "{guid}"` line. C#
  projects, old-style and SDK-style alike, used the type
  `{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}`.
- Solution folders use the type `{2150E333-8FDC-42A3-9474-1A3956D46DE8}`, and
  their **Solution Items** sit in a `ProjectSection(SolutionItems)` that
  names every file. Nothing is globbed; a file added on disk does not appear
  in the solution until its line is added.
- Solution platforms are written `Any CPU`, with a space, while project
  platforms are `AnyCPU`.

These lines cannot be wrapped. Exempt solution and project files from prose
line-length rules and record the exception where the rules live.

Edit with tools when possible:

```powershell
dotnet sln Example.sln add Source\Example.Plugin\Example.Plugin.csproj
dotnet sln Example.sln list
```

`dotnet sln add` handled an old-style project as well as an SDK-style one in
observation. For Solution Items, edit the text and preserve the byte-order
mark and CRLF endings. In PowerShell:

```powershell
$text = [IO.File]::ReadAllText($sln)
# ... edit $text, keeping "`r`n" line breaks ...
[IO.File]::WriteAllText($sln, $text, [Text.UTF8Encoding]::new($true))
```

Reload the solution in an open IDE after an external edit.

MSBuild 17.12 and later also accept the XML `.slnx` format. Keep one solution
format per directory; when both exist, MSBuild requires the file to be named
explicitly. Pass `--format sln` or `--format slnx` to `dotnet new sln` rather
than relying on the SDK's default.

## Configurations and Output Folders

Debug and Release builds write to different folders. Old-style projects set
`OutputPath` per configuration; SDK-style projects default to
`bin\<configuration>\<framework>\`. Defaults differ by tool:

| Tool | Default configuration |
| --- | --- |
| `dotnet build`, `dotnet test` | `Debug` for most projects |
| MSBuild.exe | Whatever the project's own default condition sets |
| Visual Studio | The active solution configuration |

A script that builds Release while the IDE builds Debug leaves two current
outputs. Name the configuration in every command, deploy from the folder
that command produced, and run tests against the same configuration. In
tests, find fixture files through `AppContext.BaseDirectory`, never through
a hard-coded `bin\Debug` path.

Keep every configuration's output outside folders the host scans for
plugins. A host that loads every DLL under its plugin folder would load a
Debug copy nested there as a second plugin.

## Mixed Project Styles

Old-style and SDK-style projects coexist in one solution. In observation,
MSBuild.exe built such a solution with `-restore`, including an old-style
project that referenced an SDK-style library. Points to remember:

- old-style projects list every source file; SDK-style projects glob;
- `Directory.Build.props` reaches old-style projects late unless they
  import `Microsoft.Common.props` at the top (see the
  [project-file companion](../shared-library/projects.knack.md));
- set `LangVersion` per project; and
- build the solution, not individual projects, when references cross
  styles, so restore covers every project.

## Linking Non-Code Content

Let IDE users browse data, documents, and tools that live outside a project
folder by linking them:

```xml
<ItemGroup>
  <None Include="..\Data\**\*.*">
    <Link>Data\%(RecursiveDir)%(Filename)%(Extension)</Link>
    <CopyToOutputDirectory>Never</CopyToOutputDirectory>
  </None>
</ItemGroup>
```

The [host-references companion](../framework-builds/references.knack.md)
explains each piece.

Never wrap a property or metadata value across lines. MSBuild keeps the
whitespace: in observation, a path property wrapped onto its own indented
line no longer named an existing file, and a `Configuration` value wrapped
the same way failed `'$(Configuration)' == 'Release'`. Only message text,
such as an `<Error Text>` attribute, tolerates line breaks.

Visual Studio's project systems can rewrite item lists when files are
added, removed, or renamed through the IDE; Microsoft documents the risk of
wildcards being mishandled for C++ projects. Keep wildcard items in their own
`ItemGroup` and review the project-file diff after IDE file operations.

## Files Visual Studio Creates

- `.vs\` appears beside whichever solution or project file is opened.
  Opening a `.csproj` directly creates a second `.vs\` tree. It can hold
  user options (`.suo`), caches, and index or chat data written by IDE
  extensions, such as AI assistants. Treat it as private.
- `*.csproj.user` and `*.suo` hold per-user settings.
- `bin\` and `obj\` hold build output and intermediate files.

Ignore all of these from the first commit. A `.gitignore` entry does not
untrack files that are already committed; remove them with
`git rm -r --cached <path>`. History still contains them, and removing them
from history is a separate, disruptive operation; see
[Purge Large Files from Git History](../../version-control/purge-large-files-from-git-history.knack.md).

## Review Checklist

- Are solution edits made with `dotnet sln` or with encoding and line endings
  preserved?
- Is every Solution Item listed, and every project in the solution?
- Do commands name their configuration, and do deployment and tests use that
  configuration's output?
- Is no output folder inside a folder the host scans?
- Are project-file values kept on one line?
- Are `.vs\`, `bin\`, `obj\`, and per-user files ignored and untracked?

## Further Information

- [Solution (.sln) file](https://learn.microsoft.com/en-us/visualstudio/extensibility/internals/solution-dot-sln-file)
- [`dotnet sln`](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-sln)
- [MSBuild command-line reference, including `.slnx`](https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-command-line-reference)
- [`dotnet build` configuration default](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-build)
- [Common MSBuild project items](https://learn.microsoft.com/en-us/visualstudio/msbuild/common-msbuild-project-items)
- [.vcxproj files and wildcards](https://learn.microsoft.com/en-us/cpp/build/reference/vcxproj-files-and-wildcards)
