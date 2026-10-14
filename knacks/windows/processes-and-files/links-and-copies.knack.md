# Links and Copies: Junctions, Symbolic Links, and robocopy

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion before creating, replacing, or removing a link on
Windows, before copying or mirroring a large tree, and when a deletion
fails because a file is in use. Read the
[processes and files overview](overview.knack.md)
first. Paths below are fictional: `C:\work\example-plugin` is a
repository's build output, and `%LOCALAPPDATA%\ExampleApp\Plugins` is an
application's plugin folder.

## Link Types

| Type | Links | Create without elevation | Notes |
| --- | --- | --- | --- |
| Directory junction | Directory to directory | Yes | Local volumes only, including other local drives; not network shares |
| Directory symbolic link | Directory to directory | Only with Developer Mode | May be relative |
| File symbolic link | File to file | Only with Developer Mode | May be relative |
| Hard link | Another name for the same file | Yes | Files only, same volume |

Microsoft's `New-Item` documentation states that creating a symbolic link
requires elevation unless Developer Mode is enabled, and its
`mklink` documentation lists `/D` for directory symbolic links, `/H` for
hard links, and `/J` for junctions. Junctions are therefore the usual
choice for linking a development folder into an application folder from
an unelevated agent.

## Create a Junction

PowerShell:

```powershell
$link   = Join-Path $env:LOCALAPPDATA 'ExampleApp\Plugins\ExamplePlugin'
$target = 'C:\work\example-plugin\build'
New-Item -ItemType Junction -Path $link -Target $target
```

cmd:

```text
mklink /J "%LOCALAPPDATA%\ExampleApp\Plugins\ExamplePlugin" "C:\work\example-plugin\build"
```

Use absolute targets for junctions. Record what was created, so a later
cleanup removes only that.

Under a harness that redirects the user profile, `%LOCALAPPDATA%` and
known-folder lookups follow the redirected `USERPROFILE`, so the agent's
view of the plugin folder can differ from the one the operator's
application uses. Confirm which folder the target application instance
reads, for example from its log, before creating the link.

## Verify Before Changing Anything

Check the path immediately before creating, replacing, or deleting:

```powershell
$item = Get-Item -LiteralPath $link -Force -ErrorAction SilentlyContinue
if (-not $item) {
    'absent'
} elseif ($item.LinkType) {
    '{0} -> {1}' -f $item.LinkType, ($item.Target -join ', ')
} else {
    'real directory or file: do not touch without the operator'
}
```

`LinkType` and `Target` are available in Windows PowerShell 5.1 and
PowerShell 7; PowerShell 7 also exposes .NET's `LinkTarget`. Linked items
show `l` in the `Mode` column. In cmd, `dir /AL` lists links with their
targets.

To survey a tree for links before copying or deleting it, list reparse
points with a bounded depth:

```powershell
Get-ChildItem -LiteralPath $root -Recurse -Force -Depth 6 `
    -Attributes ReparsePoint -ErrorAction SilentlyContinue |
    Select-Object FullName, LinkType, Target
```

Act on the result:

| Found | Action |
| --- | --- |
| Nothing | Create the link |
| A link to the expected target | Nothing to do |
| A link to another target | Stop; it may be the operator's setup |
| A real directory or file | Stop; it may hold the operator's data |

## Remove a Link, Not Its Target

Remove the link object itself:

```text
rmdir "%LOCALAPPDATA%\ExampleApp\Plugins\ExamplePlugin"
```

`rmdir` without `/S` removes a junction or directory symbolic link and
leaves the target's contents alone. From PowerShell,
`[System.IO.Directory]::Delete($link)` without the recursive flag does the
same. Confirm afterwards that the link path is gone and the target still
exists.

Never point a recursive delete at a link or at a tree that contains links.
Tools do not agree on whether recursion stops at a junction, and there are
reports of POSIX-layer `rm -rf` and some PowerShell versions deleting a
junction target's contents. Remove each link on its own first, verify,
then delete the remaining tree.

PowerShell 7.4 and later can replace an existing junction with
`New-Item -ItemType Junction -Force`; earlier versions fail with a "not
empty" error. Verify the old link's target before replacing it either way.

## Git Bash and Links

MSYS `ln -s` creates a deep copy by default rather than a link, which
silently diverges from the source after the next build. Create links with
Windows tools. See the
[Git Bash companion](../shells/Git-Bash.knack.md).

## Copy Trees With robocopy

In cmd syntax, where `^` continues a line:

```text
robocopy C:\work\example-app D:\backup\example-app /E /XJ ^
    /XD .git node_modules bin obj .local ^
    /R:2 /W:2 /NP /LOG:C:\work\example-app\.local\tmp\robocopy.log
```

- `/E` copies subdirectories, including empty ones.
- `/XJ` excludes junction points, which robocopy otherwise includes by
  default. Without it, a junction can pull a whole other tree into the
  copy, or a junction that points at an ancestor can make the copy
  recurse into itself.
- `/XD` excludes directories by name or path. List caches, dependency
  folders, build outputs, and the project's local scratch area explicitly.
- `/R:2 /W:2` bounds retries. The defaults are one million retries with
  30 seconds between them, which turns one locked file into an apparent
  hang. For trees that are known to contain files in use, such as a user
  profile or an application data folder, `/R:0 /W:0` skips locked files at
  once; read the log for the skipped list.
- Exclude browser profile folders and similar caches from profile-like
  copies; they are large, constantly locked while the browser runs, and
  rarely what the copy is for.
- `/LOG:` writes a record. `/L` lists what would happen without copying,
  deleting, or changing timestamps.

`/MIR` is `/E` plus `/PURGE`: it deletes destination files that are absent
from the source. A swapped source and destination, or a wrong destination,
destroys data. Run with `/L` first and read the log.

## robocopy Exit Codes

| Code | Meaning |
| --- | --- |
| 0 | Nothing copied; nothing failed |
| 1 | Files copied successfully |
| 2, 3, 5, 6, 7 | Extra or mismatched files noted; no failure |
| 8 and above | At least one failure |

In PowerShell, test `$LASTEXITCODE -ge 8`, not `-ne 0`. Under PowerShell
7.4's `$PSNativeCommandUseErrorActionPreference = $true`, disable that
preference around `robocopy` calls.

From Git Bash, robocopy's switches are mangled by MSYS path conversion; in
one test `/E` became `E:/` and `/XJ` became `C:/Program Files/Git/XJ`. Run
robocopy from PowerShell or cmd, or prefix the command with
`MSYS_NO_PATHCONV=1`.

## Files in Use

A sharing violation means another process has the file open. Browser
profiles, an application's own data files, and loaded build outputs are
typical. Test for a lock without changing anything by asking for exclusive
access and releasing it at once:

```powershell
try {
    [System.IO.File]::Open($path, 'Open', 'ReadWrite', 'None').Dispose()
    'not locked'
} catch [System.IO.IOException] {
    'locked by another process'
} catch [System.UnauthorizedAccessException] {
    'access denied: read-only, protected, or in use'
}
```

Identify the holder before acting; the Sysinternals Handle tool lists
processes holding a path and needs administrator rights. Without it,
list the likely owners' main processes; Chromium-based browsers, for
example, mark their helper processes with a `--type=` argument, so the
main browser process is the one without it.

Stop the holder only if the task started it and its identity is verified;
see the [processes companion](ownership.knack.md).
Otherwise wait, ask the operator, or defer the change until after a
restart.

Two habits avoid creating locks in the first place:

- to inspect a build output from a long-lived process, such as loading an
  assembly into a PowerShell session, copy the file to the scratch area
  and load the copy; and
- to update a running executable, rename it aside and put the new file in
  its place; a running `.exe` cannot be deleted or overwritten but can be
  renamed. See
  [porting files](../porting-cli-tools/files.Python.knack.md).

## Review Checklist

- Was the path's link type and target checked immediately before the
  change?
- Is the link a junction with an absolute target, unless symbolic-link
  semantics are required and permitted?
- Does removal use `rmdir` without `/S` or a non-recursive delete?
- Does every `robocopy` call use `/XJ`, explicit exclusions, bounded
  retries, a log, and an exit-code test of 8 or above?
- Was any `/MIR` or `/PURGE` previewed with `/L`?

## Further Information

- Microsoft, [Hard links and junctions](https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions)
- Microsoft, [Creating symbolic links](https://learn.microsoft.com/en-us/windows/win32/fileio/creating-symbolic-links)
- Microsoft, [CreateSymbolicLinkW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createsymboliclinkw)
  (unprivileged creation requires Developer Mode)
- Microsoft, [mklink](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mklink)
- Microsoft, [New-Item: `ItemType` and `Force`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-item)
- Microsoft, [about_FileSystem_Provider: `LinkType`](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_filesystem_provider)
- Microsoft, [robocopy](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy)
- Microsoft, [about_Preference_Variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables)
- Microsoft Sysinternals, [Handle](https://learn.microsoft.com/en-us/sysinternals/downloads/handle)
- MSYS2, [Symlinks](https://www.msys2.org/docs/symlinks/)
