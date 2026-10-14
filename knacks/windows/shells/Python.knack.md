# Python Tools on Windows for Agents

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when an agent writes or runs Python helper scripts on
Windows: patch scripts, log scanners, image tools, or test utilities. It
covers which interpreter actually runs, console and pipe encodings,
Windows paths in source code, and keeping dependencies inside the project.
Read the [agent shells overview](overview.knack.md) first, and
the [text files companion](text-files.knack.md) for
byte-preserving file edits, which this companion does not repeat.

Project-wide Python policy, such as supported versions, belongs to
FieldManual's [Python standard](../../../standards-and-practices/languages/python/README.md)
and the
[runtime and package environments](../../../standards-and-practices/core/runtime-and-package-environments.md)
standard.

## Which Interpreter Runs

A Windows workstation can expose several commands that look like Python:

- `python` from an installed distribution on `PATH`;
- `python3`, which may resolve to an app execution alias in the user's
  `WindowsApps` folder rather than to the interpreter `python` names; and
- `py`, the launcher, which Python's documentation marks as deprecated
  since 3.14 in favor of the Python Install Manager, which also provides a
  `py` command.

Resolve the command before relying on it, and report the version:

```bash
command -v python python3 py
python -c "import sys; print(sys.executable, sys.version)"
```

```powershell
Get-Command python, python3, py -ErrorAction SilentlyContinue |
    Select-Object Name, Source
```

An unexpected interpreter is an environment surprise, not a detail to work
around silently.

`where python` can list two entries: a real installation first, then a
`WindowsApps\python.exe` alias stub that opens the Store instead of
running code. If `PATH` order changes, the bare name reaches the stub.
Tools that must find Python on their own should:

- test each candidate by its exit code, for example
  `python -c "import sys; sys.exit(sys.version_info < (3, 10))"`, rather
  than by parsing output, so the stub fails cleanly;
- try, in order, an explicit override variable, `py -3`, each absolute
  `python.exe` on `PATH`, and the standard per-user and per-machine
  installation folders; and
- set `PYTHON_MANAGER_AUTOMATIC_INSTALL=false` while probing on machines
  with the Python Install Manager, whose `py` command can install a
  runtime automatically, then restore the caller's value for the real
  child.

For launchers, `python -I -B` runs isolated from `PYTHON*` variables and
the user's site-packages and writes no bytecode. Because `-I` ignores
`PYTHONUTF8` and `PYTHONIOENCODING`, add `-X utf8` when UTF-8 Mode is
needed.

## Standard Streams and Encoding

Python on Windows uses UTF-8 for an interactive console, but for pipes and
files it uses the system's ANSI code page, often Windows-1252, unless told
otherwise. Agent harnesses and Git Bash usually connect Python to pipes, so
`print()` of a character outside that code page either raises
`UnicodeEncodeError: 'charmap' codec can't encode character` or, with a
replacing error handler, prints a substitute such as `?`.

Set one of these for every Python process an agent starts:

```bash
PYTHONIOENCODING=utf-8 python tool.py   # stdio only
PYTHONUTF8=1 python tool.py             # UTF-8 Mode: stdio and open()
python -X utf8 tool.py                  # UTF-8 Mode for one run
```

Python 3.15 enables UTF-8 Mode by default (PEP 686). Until every machine
in scope runs 3.15 or later, set the variable anyway. A tool that cannot
control its environment can protect itself with
`sys.stdout.reconfigure(errors="replace")` before printing.

When output looks wrong, check the file's bytes before blaming the file:
the console or pipe may be the only thing mangling the text. In Git Bash,
`grep -c $'\xe2\x84\xa2' file` counts a UTF-8 trademark sign directly.

## Windows Paths in Source Code

Backslashes in ordinary string literals are escape characters:

- `'C:\Users\dev'` is a syntax error, because `\U` starts a 32-bit Unicode
  escape;
- `'C:\Data'` contains the invalid escape `\D`, which Python 3.12 and
  later report with a `SyntaxWarning`; and
- `'C:\new'` silently contains a newline.

Use `pathlib.Path`, forward slashes, or raw strings such as
`r'C:\work\example-app'`. A raw string cannot end with a single backslash.

## Getting Scripts Onto Disk Intact

Shell here-documents and `python -c` strings pass through Bash or
PowerShell first, which can remove backslashes, end quotes early, or turn
`\n` into a real newline before Python sees the code. Symptoms include
`SyntaxError: unexpected character after line continuation character` and a
script file that was never created. Write Python files with the agent's
file-writing tool. If a backslash must survive a shell layer inside
generated code, build it with `chr(92)`.

## Exact, Atomic Edits

Patch scripts should fail before writing anything when an anchor is
missing or ambiguous:

```python
from pathlib import Path

edits = [
    (Path("src/settings.txt"), "retries = 3", "retries = 5"),
    (Path("src/limits.txt"), "timeout = 30", "timeout = 60"),
]
for path, old, new in edits:
    count = path.read_text(encoding="utf-8").count(old)
    assert count == 1, f"{path}: expected 1 match for {old!r}, found {count}"
# Only now apply the edits, preserving each file's line endings and BOM.
```

Use the byte-preserving `patch_text` helper from the
[text files companion](text-files.knack.md) for the
writes. The two-pass shape matters: a half-applied batch is harder to
recover from than a refused one.

## Dependencies Without Touching the Global Interpreter

When a helper needs a package the interpreter lacks, install it into the
project's ignored local area rather than into the user's or the system's
site-packages:

```bash
python -m pip install --target .local/pylib pillow
PYTHONPATH=.local/pylib python tool.py
```

A virtual environment under `.local/` is the heavier alternative when a
helper needs several packages. Either way, report what was installed and
where; installing into a shared environment needs the operator's
agreement.

- The user site-packages folder lives under `APPDATA`. When a harness
  redirects the profile, `site.getusersitepackages()` points into the
  sandbox, and packages the operator installed "for the user" seem to
  vanish. Check it before reinstalling anything; see
  [Windows agent isolation](../../sandboxing/windows-agents/overview.knack.md).
- A `--target` folder holds binary wheels tagged for one interpreter
  version, such as `cp312`. After a Python upgrade the import fails or the
  wrong binary loads. Record the interpreter version beside the folder and
  reinstall when it changes.
- Do not `Path.resolve()` a virtual environment's interpreter path. On
  POSIX it is a symbolic link to the base interpreter, and running the
  resolved path loses the environment's packages. Use `Path.absolute()`.

Importing a helper as a module writes `__pycache__` beside it. Ignore the
folder in version control, or set `PYTHONDONTWRITEBYTECODE=1` for agent
runs.

## Sharp Edges

- `open()` without `encoding=` uses the locale encoding before Python 3.15
  unless UTF-8 Mode is on.
- Text-mode writes translate `\n` to CRLF on Windows; see the text files
  companion.
- `subprocess` with a list of arguments is safer than a single command
  string, but Windows still joins the list into one command line for the
  child, so programs with unusual parsing, such as batch files, can still
  misread it.
- A script that prints its verdict last should not be piped through a
  tool that keeps only the first lines; capture the whole output and show
  the end.
- Tools being ported from Linux or macOS meet missing modules (`fcntl`,
  `pty`, `termios`, `curses`) and functions (`os.getuid`, `os.fork`); see
  [porting command-line tools](../porting-cli-tools/overview.knack.md).

## Further Information

- Python, [Using Python on Windows](https://docs.python.org/3/using/windows.html)
- Python, [sys.stdout and standard stream encodings](https://docs.python.org/3/library/sys.html#sys.stdout)
- Python, [UTF-8 Mode](https://docs.python.org/3/library/os.html#utf8-mode)
- Python, [PEP 686: Make UTF-8 mode default](https://peps.python.org/pep-0686/)
- Python, [String and bytes literals, including raw strings](https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals)
- Python, [Environment variables: `PYTHONIOENCODING`, `PYTHONUTF8`, `PYTHONDONTWRITEBYTECODE`](https://docs.python.org/3/using/cmdline.html#environment-variables)
- Python, [Command-line options `-I`, `-B`, and `-X utf8`](https://docs.python.org/3/using/cmdline.html)
- pip, [`pip install --target`](https://pip.pypa.io/en/stable/cli/pip_install/)
