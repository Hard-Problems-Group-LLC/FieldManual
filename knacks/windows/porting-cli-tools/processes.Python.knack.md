# Porting CLI Tools: Processes, Signals, and Liveness in Python

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when a Python command-line tool that launches,
supervises, stops, or tracks other processes must work on Windows. Read
the [porting overview](overview.knack.md) first. The
code below was run with CPython 3.12 on Windows 11.

## No exec, No fork

POSIX launchers often finish with `exec`, so the launcher becomes the
child and inherits its place: whoever kills the launcher kills the work.
Windows has neither `exec` nor `os.fork`. A launcher on Windows starts a
child and keeps running beside it. If something then terminates the
launcher, such as a tool timeout, an editor stopping a task, or
`taskkill /PID`, the child keeps running, unattended.

In testing, a child started with `subprocess.Popen` survived
`TerminateProcess` of its launcher. The same child placed in a job object
with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` ended with the launcher.

## Tie the Child to the Launcher With a Job Object

```python
import ctypes
import ctypes.wintypes as wt
import subprocess

_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_k32.CreateJobObjectW.restype = wt.HANDLE
_k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wt.LPCWSTR]
_k32.SetInformationJobObject.restype = wt.BOOL
_k32.SetInformationJobObject.argtypes = [wt.HANDLE, ctypes.c_int, ctypes.c_void_p, wt.DWORD]
_k32.AssignProcessToJobObject.restype = wt.BOOL
_k32.AssignProcessToJobObject.argtypes = [wt.HANDLE, wt.HANDLE]

JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x1000
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
JobObjectExtendedLimitInformation = 9


class _Basic(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wt.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wt.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wt.DWORD),
                ("SchedulingClass", wt.DWORD)]


class _Io(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class _Extended(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", _Basic), ("IoInfo", _Io),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t)]


def attach_kill_on_close_job(proc: subprocess.Popen, allow_breakaway: bool = False) -> int:
    """Place proc in a new job that dies with this process; return the handle."""
    job = _k32.CreateJobObjectW(None, None)   # NULL attributes: not inheritable
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    info = _Extended()
    flags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if allow_breakaway:
        flags |= JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK
    info.BasicLimitInformation.LimitFlags = flags
    if not _k32.SetInformationJobObject(job, JobObjectExtendedLimitInformation,
                                        ctypes.byref(info), ctypes.sizeof(info)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not _k32.AssignProcessToJobObject(job, int(proc._handle)):
        raise ctypes.WinError(ctypes.get_last_error())
    return job   # keep it open for the launcher's lifetime; never close it early
```

How it works, per Microsoft's documentation:

- Closing the last handle to a job with `KILL_ON_JOB_CLOSE` terminates
  every process in it. The launcher holds the only handle, so when the
  launcher dies for any reason, the system closes the handle and the child
  goes with it.
- A job created with `NULL` security attributes has a non-inheritable
  handle, so the child cannot keep the job alive by inheriting it.
- Children that the child starts join the job too, so the whole tree goes
  down with the launcher. `allow_breakaway=True` adds
  `SILENT_BREAKAWAY_OK`, which lets the child's own children start outside
  the job; use it only when the child must launch independent, long-lived
  programs.
- `Popen._handle` is a private attribute; pin the Python versions you
  support and test them.

Caveat: a child can start grandchildren between `Popen` returning and the
assignment. When that window matters, start the child suspended through
the Win32 API, or assign the launcher itself to the job before spawning,
because children inherit job membership.

## Ctrl+C and Exit Codes

Console processes attached to the same console all receive Ctrl+C. A
launcher that wants the child to handle Ctrl+C should ignore `SIGINT`
while it waits, then report the child's exit status. A process ended by
Ctrl+C exits with `0xC000013A`, `STATUS_CONTROL_C_EXIT`, which Python
shows as `3221225786`; POSIX-minded callers expect 130, so map it when
the tool's interface promises shell-style codes.

## Signals Do Not Port

| POSIX habit | Windows reality in Python |
| --- | --- |
| `signal.SIGKILL` | Does not exist |
| `os.kill(pid, SIGTERM)` | Immediate `TerminateProcess`; no handler runs |
| `Popen.terminate()` | `TerminateProcess`, same as `kill()` |
| Graceful stop by signal | `CTRL_BREAK_EVENT` only for a child started with `CREATE_NEW_PROCESS_GROUP` and sharing the console |
| `os.getuid`, `pwd`, `grp` | Do not exist |

For a graceful stop that works everywhere, give long-running workers a
stop-request file or a local socket, have them poll it, and keep forced
termination as the last step of a supervisor.

## Liveness and Identity

Windows reuses process IDs quickly, and there is no `/proc`. Record a
process's creation time with its ID, for example
`GetProcessTimes` or `psutil.Process(pid).create_time()`, and compare both
before trusting an ID.

A dependency-free liveness probe:

```python
import ctypes
import ctypes.wintypes as wt

_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_k32.OpenProcess.restype = wt.HANDLE
_k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
_k32.WaitForSingleObject.restype = wt.DWORD
_k32.WaitForSingleObject.argtypes = [wt.HANDLE, wt.DWORD]
_k32.CloseHandle.argtypes = [wt.HANDLE]

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SYNCHRONIZE = 0x00100000
ERROR_ACCESS_DENIED = 5
ERROR_INVALID_PARAMETER = 87
WAIT_TIMEOUT = 0x102


def pid_is_alive(pid: int) -> bool:
    """True if a process with this ID exists; inaccessible counts as alive."""
    handle = _k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE,
                              False, pid)
    if not handle:
        error = ctypes.get_last_error()
        if error == ERROR_INVALID_PARAMETER:
            return False          # no such process
        if error == ERROR_ACCESS_DENIED:
            return True           # exists, owned by someone else
        raise ctypes.WinError(error)
    try:
        return _k32.WaitForSingleObject(handle, 0) == WAIT_TIMEOUT
    finally:
        _k32.CloseHandle(handle)
```

Set `restype` and `argtypes` for every Win32 call. The `ctypes` default
return type is a C `int`, which truncates 64-bit handles. Load the DLL with
`use_last_error=True` and read `ctypes.get_last_error()`, not
`GetLastError`, which other code may already have overwritten.

## Process Trees

- Toolhelp snapshots (`CreateToolhelp32Snapshot`) give image names and
  creator IDs only. Command lines need CIM (`Win32_Process`) or `psutil`.
- A parent ID can be stale: the parent exited and its ID was reused. When
  building a tree, drop any child created before its claimed parent.
- PIDs 0 and 4 are the idle and system processes; skip them.

## Subprocess Hygiene

```python
result = subprocess.run(
    ["git", "-C", repo, "status", "--porcelain"],
    capture_output=True, encoding="utf-8", errors="replace",
    stdin=subprocess.DEVNULL, timeout=60, check=False)
```

- Pass a list, never a command string with `shell=True`, unless a shell
  built-in is really required.
- `text=True` decodes with the locale encoding, often a legacy code page.
  Name the encoding the child actually writes.
- `stdin=subprocess.DEVNULL` stops a background probe from reading, or
  waiting on, the console of an interactive tool.
- Never call a `.cmd` or `.bat` file with untrusted arguments; see
  [launchers](launchers.knack.md).

## Virtual-Environment Interpreters

A virtual environment's `Scripts\python.exe` on Windows is a redirector:
in testing, the running interpreter was the base installation's
`python.exe`, a child of the redirector. Killing the redirector also ended
the interpreter, consistent with the redirector holding it in a job of its
own. Consequences:

- the PID returned by `Popen` is the redirector's, not the interpreter's;
- tools that inspect that PID's command line or memory see the redirector;
  and
- kill and job semantics should be tested with both a base and a
  virtual-environment interpreter.

## Elevation and Interactivity

- Detect elevation with `CheckTokenMembership`, or from PowerShell:

  ```powershell
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  ([Security.Principal.WindowsPrincipal]$id).IsInRole(
      [Security.Principal.WindowsBuiltInRole]::Administrator)
  ```

  Microsoft documents `IsUserAnAdmin` as subject to change and recommends
  `CheckTokenMembership`.
- GitHub-hosted Windows runners run as administrators with User Account
  Control disabled, so continuous integration does not exercise the
  unelevated path. Test it on a real workstation.
- Under Git Bash's terminal, standard streams are pipes, not a console, so
  `sys.stdin.isatty()` is false and interactive prompts fail or hang.
  Require an explicit flag for interactive mode instead of guessing.

## Review Checklist

- Is every long-running child tied to its launcher with a kill-on-close
  job?
- Does Ctrl+C reach the child, and is its exit code mapped as promised?
- Is graceful stop implemented without POSIX signals?
- Do liveness checks use ID plus creation time, and treat "access denied"
  as alive?
- Does every `ctypes` declaration set `restype` and `argtypes`?
- Do probes name their encoding and use `stdin=DEVNULL`?

## Further Information

- Microsoft, [CreateJobObjectW](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-createjobobjectw)
- Microsoft, [JOBOBJECT_BASIC_LIMIT_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)
- Microsoft, [OpenProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess)
- Microsoft, [GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes)
- Microsoft, [IsUserAnAdmin](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-isuseranadmin)
- Python, [subprocess on Windows](https://docs.python.org/3/library/subprocess.html)
- Python, [os.kill and process management](https://docs.python.org/3/library/os.html#os.kill)
- Python, [ctypes: return types](https://docs.python.org/3/library/ctypes.html#return-types)
- Python, [venv: how venvs work](https://docs.python.org/3/library/venv.html)
- GitHub, [GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
