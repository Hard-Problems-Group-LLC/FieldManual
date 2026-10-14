# Git Bash for Agents

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when an agent runs commands through the Bash shell that
ships with Git for Windows, especially when those commands call Windows
programs or pass Windows paths. Read the
[agent shells overview](overview.knack.md) first.

## Mental Model

Git Bash is a POSIX shell running on the MSYS2 runtime. Programs under
`/usr/bin` are MSYS programs that understand POSIX paths. Everything else,
including `git.exe`, `python.exe`, `pwsh.exe`, `cmd.exe`, and the programs in
`C:\Windows\System32`, is a native Windows program that only understands
Windows paths and Windows command-line quoting.

When Bash starts a native program, the MSYS runtime rewrites arguments and
some environment variables that look like POSIX paths into Windows paths.
That conversion is helpful for real paths and destructive for arguments
that merely resemble paths.

`$MSYSTEM` is set in this environment, for example to `MINGW64`, and
`uname -s` reports a `MINGW` or `MSYS` system name.

## Path Spellings

| POSIX form in Git Bash | Windows meaning |
| --- | --- |
| `/c/work/example-app` | `C:\work\example-app` |
| `/tmp/scratch` | A folder under the user's temporary directory |
| `/usr/bin` | The `usr\bin` folder of the Git installation |
| `~` | Whatever `$HOME` currently is |

Convert explicitly with `cygpath` instead of guessing:

```bash
cygpath -w /c/work/example-app    # C:\work\example-app
cygpath -m /c/work/example-app    # C:/work/example-app
cygpath -u 'C:\work\example-app'  # /c/work/example-app
```

Agent harnesses sometimes redirect `HOME` to a sandbox folder. In that case
`~` and every tool that reads `$HOME`, including Git's global
configuration and the MSYS `ssh`, see the sandbox rather than the
operator's profile. See [Git for agents](../git/overview.knack.md).

## Automatic Argument Conversion

Arguments passed to a native program are converted when they look like
POSIX paths:

```bash
python -c 'import sys; print(sys.argv[1:])' /tmp/out /c/src
# ['C:/Users/<user>/AppData/Local/Temp/out', 'C:/src']
```

Windows-style switches can be mistaken for paths. In one test,
`cmd //c echo /PID 123` received `"C:/Program Files/Git/PID" 123`, so a
command such as `taskkill /PID 123` fails or targets nothing. Options:

- double the leading slash: `taskkill //PID 123 //T`,
  `tasklist //FI "IMAGENAME eq example-app.exe"`, or `cmd //c ...`;
- disable conversion for one command with Git for Windows'
  `MSYS_NO_PATHCONV=1`, for example `MSYS_NO_PATHCONV=1 taskkill /PID 123`;
- exclude prefixes with MSYS2's `MSYS2_ARG_CONV_EXCL`, such as
  `MSYS2_ARG_CONV_EXCL='--prefix='`; or
- run the command from PowerShell instead.

Conversion also applies to options such as `--dir=/foo`. Path-list
environment variables are converted, and `:` separators become `;`.

## Calling PowerShell and cmd From Bash

Two quoting systems stack. Bash removes its own quotes and expands `$` in
double quotes; PowerShell then parses the remaining text and expands `$`
again. A safe pattern hands PowerShell a script file rather than inline
code:

```bash
pwsh -NoProfile -NonInteractive -File "$(cygpath -w "$script")" -Name demo
```

Environment variables set on the command line reach the Windows child,
which is the simplest way to hand it a Windows path:

```bash
EXAMPLE_HOME='C:\Program Files (x86)\ExampleApp' \
    pwsh -NoProfile -File "$(cygpath -w "$script")"
```

For cmd, `cmd //c "..."` works for simple commands, but `cmd` has its own
rules for `%`, `^`, `&`, and `|`. Prefer a `.cmd` file written with the
agent's file tool, or avoid cmd.

## Here-Documents

- An unquoted delimiter (`<<EOF`) expands `$name`, `$(...)`, and
  backticks, and processes backslash escapes. A quoted delimiter
  (`<<'EOF'`) passes the body literally.
- The harness has already passed the whole command through its own
  encoding and quoting layers before Bash sees it. Non-ASCII characters and
  backslash sequences can be altered before the here-document exists.
- Bash writes LF line endings. A file that the repository stores with CRLF
  becomes mixed or rewritten; see the
  [text files](text-files.knack.md) companion.

Use a here-document for short ASCII content only. Write anything else with
the agent's file-writing tool.

## Line Endings in Pipes

Native Windows programs usually end output lines with CRLF. When that
output is piped into MSYS tools, a trailing carriage return can defeat
`grep -x`, string comparison, and `diff`. Normalize with `tr -d '\r'`
before comparing. `cat -A file` shows a carriage return as `^M` before the
`$` that marks each line end, which also exposes literal newlines and tabs
introduced by a mangled scripted edit.

## Links

MSYS `ln -s` creates a deep copy of the target by default, not a Windows
symbolic link. Native links require `MSYS=winsymlinks:nativestrict` plus
administrator rights or Developer Mode. For links an application must
follow, create a junction or symbolic link with Windows tools; see
[links and copies](../processes-and-files/links-and-copies.knack.md).

## Time Limits

Git Bash includes GNU coreutils `timeout`, which limits how long a command
may run:

```bash
timeout 120 git -C /c/work/example-app fetch origin
echo "exit: $?"   # 124 means the limit was reached
```

After a timeout, check for helper processes, such as `ssh` or
`git-remote-https`, that may still be running. The Windows `timeout.exe`
seen from cmd and PowerShell is a pause command and does not do this.

In a pipeline, `$?` reports only the last command. After
`timeout 30 git ls-remote origin 2>&1 | tail -2`, `$?` is `tail`'s status
and hides Git's failure. Read `${PIPESTATUS[0]}` immediately after the
pipeline, or run scripts with `set -o pipefail`.

## Paths With Spaces in Pipelines

`xargs` splits its input on blanks, so a path such as
`/c/Program Files (x86)/ExampleApp/app.log` arrives as three arguments.
Use null-separated lists instead:

```bash
find "$root" -name '*.log' -print0 | xargs -0 grep -l 'ERROR'
grep -rlZ 'ExampleSetting' "$root" | xargs -0 ls -l
```

Or read paths one per line with `while IFS= read -r p; do ...; done`.

## Scripts

Start Bash scripts with:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

Quote every expansion, and use `"$(cygpath -w "$p")"` at the boundary
where a path leaves Bash for a native program.

Scripts meant to run on other systems too should survive two portable
traps:

- an exported `CDPATH` can redirect `cd` and make it print the new
  directory, which corrupts `$(cd ... && pwd)`; write
  `CDPATH= cd -- "$(dirname -- "$0")"`; and
- Bash before 4.4, still the default on macOS, treats an empty
  `"${args[@]}"` as unset under `set -u`; write `${args[@]+"${args[@]}"}`.

A launcher written for Git Bash may export `MSYS_NO_PATHCONV=1` and
`MSYS2_ARG_CONV_EXCL='*'` for its own native calls. Remove both from the
environment of the program it finally starts, so commands run inside that
program keep normal conversion; see
[launchers](../porting-cli-tools/launchers.knack.md).

## Terminals

Git Bash's terminal, mintty, connects native Windows programs to pipes
rather than to a Windows console. Native programs then see
`isatty()` as false, may buffer output, and cannot run full-screen text
interfaces. Run curses-style tools in Windows Terminal or the classic
console host instead, for example in a side pane:

```text
wt -w 0 split-pane -V -s 0.3 -d . example-tui.exe
```

Python's own `curses` module is absent from python.org builds for Windows;
see [porting command-line tools](../porting-cli-tools/overview.knack.md).

## Sharp Edges

- `rm -rf` is an MSYS program. Do not point it at a tree that contains
  junctions until each junction has been removed on its own; see
  [links and copies](../processes-and-files/links-and-copies.knack.md).
- `find`, `sort`, `ps`, and `kill` are POSIX tools here. MSYS process IDs
  need not match Windows process IDs, so use Windows tools to inspect and
  stop native processes; see
  [processes](../processes-and-files/ownership.knack.md).
- A path containing spaces must be quoted at both the Bash layer and,
  where a second interpreter is involved, at that layer too.
- Environment variables set with `export` persist only for the current
  call when each tool call is a new process.
- `find /` searches the Git installation and `/proc`, where
  `/proc/registry`, `/proc/registry32`, and `/proc/registry64` expose the
  Windows registry as files. It can run far past a harness's time limit.
  Search a known root instead.

## Further Information

- MSYS2, [Filesystem paths and automatic conversion](https://www.msys2.org/docs/filesystem-paths/)
- MSYS2, [Symlinks](https://www.msys2.org/docs/symlinks/)
- Git for Windows, [release notes, including `MSYS_NO_PATHCONV`](https://github.com/git-for-windows/build-extra/blob/main/ReleaseNotes.md)
- GNU, [timeout invocation](https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html)
- Microsoft, [taskkill](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/taskkill)
- Microsoft, [Windows Terminal command-line arguments](https://learn.microsoft.com/en-us/windows/terminal/command-line-arguments)
