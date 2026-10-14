# Porting Command-Line Tools to Windows

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when a command-line tool written for Linux or macOS,
especially in Python, must run natively on Windows: not under WSL, and not
only inside Git Bash. It gives the mental model, an inventory of features
that do not port, and a porting workflow. Companions:

- [Processes](processes.Python.knack.md): job
  objects instead of `exec`, Ctrl+C, signals, liveness, process trees,
  subprocess hygiene, and elevation;
- [Files](files.Python.knack.md): atomic writes
  beside readers, replacing running executables, locks, file identity,
  case-insensitive paths, path length, and state locations; and
- [Launchers](launchers.knack.md): batch shims and
  their argument-injection hazard, PowerShell entry points, `PATH`, and
  DLL placement.

Day-to-day agent work on Windows is covered by
[agent shells](../shells/overview.knack.md) and
its [Python companion](../shells/Python.knack.md).

## Mental Model

Windows is not a Unix with different path separators. A port meets four
kinds of difference:

1. **Process model.** No `fork`, no `exec`, no POSIX signals, no `/proc`,
   no user IDs. A launcher lives beside its child, not in place of it.
2. **File semantics.** Open files block renames and deletes; running
   executables cannot be overwritten; locks are mandatory byte ranges;
   paths are case-insensitive and length-limited by default.
3. **Consoles and encodings.** Legacy code pages for pipes, CRLF defaults,
   and terminals that are pipes rather than consoles.
4. **Entry points.** `cmd.exe` re-parses batch-file arguments, PowerShell
   has its own resolution and exit rules, and `PATH` lives in the
   registry.

Most porting failures are not exotic. They are POSIX assumptions evaluated
early, for example a default computed at import time, which make every
command fail before it starts.

## What Does Not Port

| POSIX feature | Windows replacement |
| --- | --- |
| `exec` into the real program | Child process in a kill-on-close job object |
| `os.fork`, daemonizing | `subprocess` plus a supervisor |
| `SIGTERM` handlers, `SIGKILL` | Stop-request file or socket; `TerminateProcess` as last resort |
| `/proc/<pid>` liveness and command lines | `OpenProcess`, process creation time, CIM or `psutil` |
| `os.getuid`, `pwd`, `grp`, `os.sysconf` | Absent; use `getpass.getuser()` or Windows APIs |
| `fcntl.flock` | `msvcrt.locking` on a dedicated lock file |
| `pty`, `termios`, `curses` | Absent from python.org builds; ConPTY, a third-party `windows-curses`, or a plain-output mode |
| `XDG_RUNTIME_DIR`, `/run/user/<uid>` | Project `.local/<tool>/` or `%LOCALAPPDATA%\<tool>` |
| Atomic rename over an open file | `os.replace` with retries |
| Symlink switching, `RENAME_EXCHANGE` | Version folders plus an atomic pointer file |
| Shell scripts as entry points | Real executables or Python entry points; `.cmd` only for people |
| Executable bit and shebang | File extension and launcher; keep the bit in Git for other platforms |

In a test with CPython 3.12 on Windows, `os.getuid`, `os.fork`,
`os.sysconf`, and `signal.SIGKILL` were absent, and importing `fcntl`,
`pty`, `termios`, `curses`, `resource`, `pwd`, and `grp` failed.

## Porting Workflow

1. **Inventory before editing.** Search for `os.getuid`, `os.fork`,
   `os.sysconf`, `signal.`, `/proc`, `/tmp`, `/run`, `fcntl`, `pty`,
   `termios`, `curses`, `shell=True`, `#!/bin/`, `os.rename`, symlink
   creation, and calls to Unix-only programs. Each hit is a design
   decision, not a find-and-replace.
2. **Make platform defaults lazy.** Compute paths and identities only on
   the code path that needs them, and guard optional calls with
   `hasattr` or `sys.platform`. One eager `os.getuid()` in `main()` before
   command dispatch makes every subcommand crash on Windows, including
   ones that never needed a user ID.
3. **Replace mechanisms, not syntax.** Swap signals for stop files, `exec`
   for jobs, symlink switching for pointer files. Emulating the POSIX API
   usually leaks.
4. **Fix encodings and line endings at the edges.** Name the encoding of
   every subprocess pipe and file, write LF where POSIX tools read, and
   handle `UnicodeEncodeError` on redirected output, for example with
   `sys.stdout.reconfigure(errors="replace")` or UTF-8 Mode.
5. **Test on real Windows.** WSL and Git Bash hide most differences. Run
   the entry points from cmd, Windows PowerShell 5.1, PowerShell 7, and
   Git Bash, and run the suite from a short base path.
6. **Test the unelevated path.** Hosted Windows CI runners run as
   administrators, so permission failures appear first on workstations.

## Companion Tools That Do Not Run on Windows

When a tool must exchange files with a companion that does not run on
Windows yet, write the file protocol with a small, dependency-free mirror:
pin it to an upstream revision, write atomically, and test it against the
upstream's own reader when that reader can be imported, skipping the test
otherwise. Do not vendor the whole companion to get one file format.

## Review Checklist

- Does importing every module and running `--help` work on Windows?
- Are all Unix-only calls behind lazy, guarded code paths?
- Is each long-running child tied to its launcher?
- Do state files survive concurrent readers?
- Do entry points avoid passing arguments through batch files?
- Has the tool run from every supported shell, unelevated, on a real
  Windows host?

## Further Information

- Python, [os module availability notes](https://docs.python.org/3/library/os.html)
- Python, [signal on Windows](https://docs.python.org/3/library/signal.html)
- Python, [curses availability](https://docs.python.org/3/library/curses.html)
- Python, [Using Python on Windows](https://docs.python.org/3/using/windows.html)
- Microsoft, [Job objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
- Microsoft, [Creating a pseudoconsole session (ConPTY)](https://learn.microsoft.com/en-us/windows/console/creating-a-pseudoconsole-session)
- GitHub, [GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
