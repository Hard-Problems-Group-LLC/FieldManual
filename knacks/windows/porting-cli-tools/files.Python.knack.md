# Porting CLI Tools: Files, Locks, and Paths in Python

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when a Python tool that writes state files, replaces
its own executables, takes file locks, or checks path containment must
work on Windows. Read the
[porting overview](overview.knack.md) first. Behavior
marked as tested was run with CPython 3.12 on Windows 11 and NTFS.

## Replacing Files That Others Read

The usual atomic-write pattern still applies: write a temporary file in
the same directory, flush it, then `os.replace` it over the target. Two
Windows differences break naive ports:

- `os.replace` fails with `PermissionError` (Windows error 5) while
  another process has the target open without delete sharing, which is
  how ordinary `open()` calls in Python and most programs open files. A
  reader polling a status file makes the writer fail intermittently.
- A directory cannot be opened for `fsync`: `os.open` on a directory
  raises `PermissionError`. Skip the directory flush on Windows rather
  than failing.

```python
import os
import time
from pathlib import Path

_DELAYS = (0.01, 0.02, 0.05, 0.1, 0.2, 0.25, 0.4)   # about one second


def write_text_atomic(path: Path, text: str) -> None:
    """Replace path with text (UTF-8, LF), retrying while readers hold it."""
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        for delay in _DELAYS + (None,):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                if delay is None:
                    raise
                time.sleep(delay)
    finally:
        if tmp.exists():
            tmp.unlink()
    if os.name != "nt":
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
```

Readers should retry briefly too, because a read can land in the instant
the file is being replaced. Write with `newline="\n"` for files that
POSIX tools or Python read; `Path.write_text` without `newline` writes
CRLF on Windows.

## Replacing a Running Executable

A running program's `.exe` cannot be deleted or overwritten; the attempt
fails with Windows error 5. It can be renamed. In testing, renaming a
running executable and copying a new one into its old name both
succeeded. An updater should:

1. rename the old file aside, for example to `tool.exe.old-<token>`;
2. put the new file in place under the original name;
3. delete leftover `.old-*` files on a later run, ignoring failures for
   ones still in use; and
4. retry Windows errors 5 and 32 with backoff for up to about a minute,
   because security software briefly holds newly written executables.

The C runtime's `open` can report a sharing violation as plain `EACCES`
with no Windows error code attached, so test for both forms.

## File Locks

`fcntl` does not exist on Windows. `msvcrt.locking` locks byte ranges:

- in testing, a second process could not even read a locked byte; its
  `open().read()` failed with `PermissionError`;
- a second lock attempt on a locked range failed with `PermissionError`,
  errno 13 (`EACCES`); and
- `LK_LOCK` retries for about ten seconds before failing, while `LK_NBLCK`
  fails at once.

Design locks for those semantics: lock one byte of a dedicated lock file
that holds no data, never read that file for diagnostics, and keep the
diagnostic information in a separate file. Treat "the filesystem does not
support locking" as its own outcome on network and unusual filesystems,
distinct from contention.

## File Identity

Python 3.12 changed `os.stat` on Windows: `st_ino` can now carry up to
128 bits on file systems that use 128-bit file identifiers, such as ReFS,
and `st_dev` up to 64 bits. Values stored by one Python version may not
match those computed by another. For change detection, stamp files with
size and `st_mtime_ns`; when true identity matters, use the 128-bit file
ID consistently.

## Case-Insensitive Paths

NTFS paths are case-insensitive by default. `PureWindowsPath` comparisons,
`relative_to`, and `is_relative_to` ignore case, but plain string
comparisons and `PurePosixPath` do not. A containment check written and
tested on Linux, such as "this path is not inside the protected folder",
can pass for `Protected\x` while Windows resolves it to `protected\x`.
Compare `os.path.normcase` results or casefolded path components, and
test with case variants.

## Path Length

`MAX_PATH` is 260 characters. Long paths need both the `LongPathsEnabled`
system setting and a `longPathAware` application manifest, so a tool
cannot assume either. Failures surface as Windows error 206, "The filename
or extension is too long", often from a deep staging folder or a test
framework's temporary directory. Keep staging names short, warn when a
path approaches about 240 characters, and give test runners a short base
temporary folder, such as pytest's `--basetemp`.

## Links and Version Switching

Symbolic links need administrator rights or Developer Mode, and Windows
has no atomic exchange of two directories like Linux's `renameat2` with
`RENAME_EXCHANGE`. To switch between installed versions:

- keep each version in its own folder;
- record the active one in a small pointer file written atomically; and
- make migrations that would need an atomic exchange refuse to run
  rather than approximate it.

Never follow links or junctions during discovery or cleanup. Older Python
versions differ in how `Path.resolve()` treats dangling links on Windows,
and a followed junction can lead a cleanup outside its tree; see
[links and copies](../processes-and-files/links-and-copies.knack.md).

## Where State Lives

POSIX runtime locations do not port: there is no `XDG_RUNTIME_DIR`,
`/run/user/<uid>`, or `/tmp/<tool>-<uid>`. Keep project-specific state in
the project's ignored local folder, such as `.local/<tool>/`, and use
`%LOCALAPPDATA%\<tool>` only for state shared across projects. Temporary
folders under `%TEMP%` are not cleaned automatically and accumulate large
leftovers from test runs; create uniquely named folders under
`.local/tmp/` and remove what each run created.

## Review Checklist

- Do atomic writes retry `PermissionError`, clean up the temporary file,
  and skip directory `fsync` on Windows?
- Are LF line endings explicit where POSIX tools read the file?
- Does self-update rename the running executable aside instead of
  overwriting it?
- Are locks taken on a dedicated file that nothing reads?
- Are path containment checks case-insensitive on Windows?
- Do staging and test paths stay well below 260 characters?

## Further Information

- Python, [os.replace](https://docs.python.org/3/library/os.html#os.replace)
- Python, [msvcrt.locking](https://docs.python.org/3/library/msvcrt.html#msvcrt.locking)
- Python, [What's New in Python 3.12: `os.stat` on Windows](https://docs.python.org/3/whatsnew/3.12.html)
- Python, [pathlib: pure paths and case](https://docs.python.org/3/library/pathlib.html)
- Microsoft, [Maximum path length limitation](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation)
- Microsoft, [LockFileEx](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex)
- Microsoft, [Creating symbolic links](https://learn.microsoft.com/en-us/windows/win32/fileio/creating-symbolic-links)
