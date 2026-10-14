# Porting CLI Tools: Launchers, Batch Shims, and PATH

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when a command-line tool needs Windows entry points:
`.cmd` or `.bat` shims, PowerShell scripts, installers that edit `PATH`,
or tests that drive cmd and PowerShell. Read the
[porting overview](overview.knack.md) first.

## Programs Call Executables; Batch Files Are for People

When a program starts a `.bat` or `.cmd` file, Windows runs it through
`cmd.exe`, which parses the command line again with its own rules for
`"`, `%`, `^`, `&`, `|`, and `!`. Language runtimes quote arguments for
the C runtime's rules, not cmd's. The resulting command-injection class
was named BatBadBut in 2024 and affected many runtimes, including Rust
(CVE-2024-24576), Node.js, Python, Go, and Java. The Rust advisory states
that, because of cmd's complexity, no escaping was found that is correct
in all cases; Rust now refuses arguments it cannot escape safely. Python's
`subprocess` documentation warns that batch files may be run in a shell
regardless of how arguments are passed.

In a test with CPython 3.12, passing the single list element
`"& echo INJECTED` to a two-line `.cmd` shim that forwarded `%*` to Python
ran `echo INJECTED` as a separate command. The same element passed
directly to `python.exe` arrived intact.

Rules:

- Programs, tests, and other tools call the real executable with an
  argument list, by full path including the `.exe` extension, so a
  same-named batch file on `PATH` cannot be picked instead.
- Never pass untrusted text, including prompts, file names, or model
  output, to a batch file.
- Ship a real executable entry point. Python projects get one from
  console-script entry points: pip writes a small `.exe` launcher that
  records the absolute path of its interpreter, so a copied launcher still
  works from another folder.
- Keep `.cmd` shims for people typing at a prompt, and document that they
  cannot forward arbitrary arguments verbatim.

## Writing a Batch File Safely Anyway

When a human-facing batch file is still worth shipping:

- Store it with CRLF line endings and ASCII text, and pin both in
  `.gitattributes` with `*.cmd text eol=crlf` and `*.bat text eol=crlf`.
  cmd's label and `goto` handling has been reported to misbehave with
  LF-only files; a short test passing proves little about a long file.
- Start with `@echo off` and `setlocal`, and carry results out with
  `endlocal & set "RESULT=%RESULT%"`.
- Set `set "NoDefaultCurrentDirectoryInExePath=1"` so cmd stops searching
  the current folder for programs. Microsoft documents that the
  variable's presence, not its value, removes the current folder from
  cmd's executable search.
- Name programs with explicit `.exe` and full paths. A bare name can
  resolve to another shim, such as a version manager's `.bat`, which then
  takes over the run.
- Do not start programs with `call`. In testing, `call` doubled carets
  inside quoted arguments and expanded `%` a second time.
- Keep `%*` out of parenthesized blocks, and read `PATH` with delayed
  expansion (`!PATH!`): quoted entries such as `(x86)` folders break
  parenthesized `for` lists, and entries containing `!` need delayed
  expansion turned off again. These are reported pitfalls rather than
  documented rules.
- cmd limits command lines and expansions to 8,191 characters and ignores
  inherited variables longer than that, so a long `PATH` can vanish inside
  cmd.
- `for /f` decodes command output in the console code page and mangles
  non-ASCII paths. Decide by exit codes, not by parsed output.
- `%~dp0` has been reported to name the caller's folder when cmd finds the
  script on `PATH` through a quoted bare name. Resolving it inside a
  `call`ed subroutine of the same file gives the script's real folder.
- cmd reads a running batch file by byte offset, so a script that is
  replaced while it runs, for example by its own updater, continues at the
  old offset in the new content. End the launch line so the script exits
  immediately afterwards.
- Killing the `cmd.exe` that runs a batch file leaves the program it
  started running, and Ctrl+C prompts "Terminate batch job (Y/N)?". Stop
  the whole tree with `taskkill /T`, or call the real executable.

## PowerShell Entry Points

- In testing, `.\bin\tool` ran `bin\tool.cmd` when no `tool.ps1` existed,
  and ran `tool.ps1` once one appeared beside it. A `.ps1` is subject to
  execution policy; a `.cmd` is not. Never generate a `.ps1` with the same
  base name as a shipped `.cmd`.
- With `-Command`, a script whose last statement is a `try` with an empty
  `catch` still exits 1, because `$?` stays false. This happened in both
  Windows PowerShell 5.1 and PowerShell 7. End helper scripts with an
  explicit `exit 0` or `exit $LASTEXITCODE`.
- Windows PowerShell 5.1 still uses legacy native-argument quoting; see
  the [PowerShell companion](../shells/PowerShell.knack.md).

## Driving cmd and PowerShell From Tests

```python
def run_powershell(shell: str, script: str, *args: str) -> list[str]:
    """Build an argv that runs script with args and returns its exit code."""
    quoted = " ".join("'" + a.replace("'", "''") + "'" for a in (script,) + args)
    return [shell, "-NoLogo", "-NoProfile", "-NonInteractive",
            "-Command", f"& {quoted}; exit $LASTEXITCODE"]


def run_cmd(script: str, args: str) -> str:
    """Build a command line for cmd.exe; /d skips AutoRun, /s strips outer quotes."""
    return f'cmd.exe /d /s /c ""{script}" {args}"'
```

Pass the cmd line to `subprocess.run` as a string, not a list: Python's
list quoting would escape the inner quotation marks with backslashes,
which cmd does not understand. `args` must already be safe for cmd.

Run each entry point under every shell it claims to support: cmd,
Windows PowerShell 5.1, PowerShell 7, and Git Bash. Each one parses
differently.

From Git Bash, a launcher can set `MSYS_NO_PATHCONV=1` and
`MSYS2_ARG_CONV_EXCL='*'` for its own native calls, but should remove them
from the environment of the child it finally starts, so commands run in
that session keep normal MSYS behavior. See the
[Git Bash companion](../shells/Git-Bash.knack.md).

## PATH and the Environment

- Do not edit `PATH` with `setx`. Microsoft documents that `setx`
  truncates values at 1,024 characters and replaces variable references
  with their expanded values. Use
  `[Environment]::SetEnvironmentVariable('Path', $newValue, 'User')`, or
  print that command for the user, and tell them to open a new terminal:
  already-running shells keep their old environment.
- Installers that update `PATH`, including per-user package managers,
  change only the stored value. Re-detect tools by full path in the same
  session, and tell the user to restart terminals.
- Environment variable names are case-insensitive on Windows, and Python's
  `os.environ` upper-cases keys. A hand-built child environment dictionary
  can still hold both `Path` and `PATH`, which leaves the child with an
  ambiguous block. Normalize names case-insensitively before spawning.

## DLLs Beside Executables

For ordinary desktop programs, Windows searches the folder the program was
loaded from before the system folder when resolving DLLs. A stray DLL next
to an executable can therefore replace a system library. Keep a verified
binary's folder free of anything else, and never place executables in a
shared folder that collects DLLs.

## Review Checklist

- Do programs and tests call `.exe` files by full path with argument
  lists?
- Do batch files receive only trusted, documented arguments?
- Are `.cmd` and `.bat` files CRLF and ASCII, pinned in
  `.gitattributes`?
- Does every PowerShell helper end with an explicit exit code?
- Does the installer avoid `setx` and explain that new terminals are
  needed?
- Is the entry point tested under cmd, both PowerShell editions, and Git
  Bash?

## Further Information

- Rust, [Security advisory for the standard library (CVE-2024-24576)](https://blog.rust-lang.org/2024/04/09/cve-2024-24576/)
- Flatt Security, [BatBadBut: You can't securely execute commands on Windows](https://flatt.tech/research/posts/batbadbut-you-cant-securely-execute-commands-on-windows/)
- Python, [subprocess: Windows batch file warning](https://docs.python.org/3/library/subprocess.html)
- Microsoft, [cmd](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd)
- Microsoft, [Command prompt line string limitation](https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/command-line-string-limitation)
- Microsoft, [NeedCurrentDirectoryForExePathW](https://learn.microsoft.com/en-us/windows/win32/api/processenv/nf-processenv-needcurrentdirectoryforexepathw)
- Microsoft, [setx](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setx)
- Microsoft, [Dynamic-link library search order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order)
- Microsoft, [about_Command_Precedence](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_command_precedence)
- Python, [os.environ](https://docs.python.org/3/library/os.html#os.environ)
