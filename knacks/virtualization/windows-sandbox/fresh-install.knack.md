# Windows Sandbox: What a Fresh Windows Lacks

Reviewed: 2026-10-13. Each claim carries one of three labels:
**observed** on Windows 11 build 26300, in a Windows Sandbox guest
unless the entry names the host; **documented** by the vendor; or
**unknown** because nobody has recorded it yet. Measure unknowns with
the inventory script below before relying on them. Read the
[overview](overview.knack.md) first.

## When to Load This Knack

Load this companion when an installer, bootstrap script, or tool must
work on a newly installed Windows, whether in Windows Sandbox, a new
virtual machine, or a new workstation, and when a failure appears only
on such a machine. Most lessons apply beyond the Sandbox; Sandbox-only
facts are marked.

## Inventory at a Glance

| Item | On a fresh Windows | Label | Typical failure |
| --- | --- | --- | --- |
| Public root certificates | Roots not shipped with Windows arrive only on first use through Windows TLS | Observed, documented | Python: "unable to get local issuer certificate" |
| Python | Absent | Observed | `python` not found; on a normal Windows, a Store alias may answer instead |
| Git | Absent | Observed | `git` not found |
| WinGet, Microsoft Store | Absent in the Sandbox | Documented | `winget` not found |
| Inbox Store apps such as Notepad and Terminal | Absent in the Sandbox from Windows 11 24H2 | Documented | Scripts that open them fail |
| PowerShell | Windows PowerShell 5.1 only; PowerShell 7 is a separate product | Documented | `pwsh` not found |
| Execution policy | `Restricted` on clients unless set | Documented; guest value unknown | `.ps1` files refuse to run |
| Universal C runtime | Part of Windows 10 and later | Documented | None |
| Visual C++ runtime (`vcruntime140.dll`, `msvcp140.dll`) | Not part of Windows | Documented; guest unknown | A DLL "was not found" at start |
| .NET Framework | 4.8.1 included from Windows 11 22H2; 3.5 must be enabled | Documented | Old apps ask for 3.5 |
| .NET 5 and later | Not included | Documented | Framework-dependent apps fail; `dotnet` not found |
| Long paths | Opt-in by policy or registry | Documented; guest unknown | Failures past 260 characters |
| Microsoft Defender | Unknown in the guest | Unknown | Record its state before blaming it |
| Enterprise roots, proxy, mapped drives, credentials | Not in a pristine guest | By design | TLS-inspecting proxies break every client |

## Root Certificates Arrive on Demand

### Mechanism

Windows ships with a set of trusted roots and adds others when needed.
When a Windows component builds a certificate chain to a root it does
not hold, the Automatic Root Certificates Update component asks Windows
Update whether Microsoft trusts that root and, if so, installs it
(documented). A fresh Windows has never made that request for most
hosts. Automatic updating can be disabled by policy, and it needs
`ctldl.windowsupdate.com` over HTTP; with either missing, the root never
arrives.

### Symptom

Python's `ssl` module verifies with OpenSSL. Its default context loads
the certificates in the Windows `ROOT` and `CA` stores when the context
is built, and verification never asks Windows to fetch anything. On one
fresh guest, a public download host whose chain ended at GlobalSign
Root CA failed:

```text
urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED]
certificate verify failed: unable to get local issuer certificate
(_ssl.c:...)>
```

One Windows PowerShell request to the same host made Windows fetch the
root, after which Python verified the host (observed). The connection
to the documented mechanism is an inference; to confirm it, look for
CAPI2 event 4097 in the guest's `Application` log, "Successful auto
update of third-party root certificate", naming the root.

### Which Clients Trigger the Fetch

| Client | Behavior on a missing root |
| --- | --- |
| Windows PowerShell `Invoke-WebRequest` | Triggers the fetch (observed) |
| Inbox `curl.exe` | Reports Schannel in `curl -V` (observed on the host); expected to trigger it, not verified |
| .NET on Windows | Uses the Windows chain engine; expected to trigger it, not verified |
| Python `ssl` with the default context | Does not trigger it (observed) |
| Python with `truststore` | Delegates verification to Windows CryptoAPI; expected to trigger it, not verified |
| pip 24.2 and later | Uses the system store through `truststore` in addition to `certifi` (documented) |
| Bundled CA files such as `certifi` | Ignore the Windows store entirely; no fetch, and no enterprise roots |
| Git for Windows | Depends on `http.sslBackend`: `schannel` uses Windows, `openssl` uses a CA file |

### Manual Fix

From Windows PowerShell 5.1, before the failing tool runs:

```powershell
Invoke-WebRequest -UseBasicParsing -Method Head `
  -Uri https://downloads.example.com/
```

The request may fail at the HTTP level and still deliver the root; the
TLS handshake is what matters.

### Automated Fix in Python

Retry once per host, only for the missing-issuer failure, only on
Windows, and only while Python uses the Windows store:

```python
"""Retry HTTPS once after Windows itself fetches a missing root."""
import ctypes
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

MISSING_ISSUER = "unable to get local issuer certificate"
FETCH_SCRIPT = (
    "$ProgressPreference = 'SilentlyContinue'; "
    "[Net.ServicePointManager]::SecurityProtocol = "
    "[Net.ServicePointManager]::SecurityProtocol -bor "
    "[Net.SecurityProtocolType]::Tls12; "
    "try { Invoke-WebRequest -UseBasicParsing -Method Head -TimeoutSec 30 "
    "-Uri $env:ROOT_FETCH_URL | Out-Null } catch { }; exit 0")
_tried_hosts = set()


def windows_powershell():
    """Return powershell.exe from the system directory, never from PATH."""
    buffer = ctypes.create_unicode_buffer(32768)
    length = ctypes.windll.kernel32.GetSystemDirectoryW(buffer, len(buffer))
    if not length or length >= len(buffer):
        return None
    path = os.path.join(buffer.value, "WindowsPowerShell", "v1.0",
                        "powershell.exe")
    return path if os.path.isfile(path) else None


def let_windows_fetch_root(url):
    """Make one Windows TLS request to url; True if PowerShell ran."""
    exe = windows_powershell()
    if exe is None:
        return False
    env = dict(os.environ, ROOT_FETCH_URL=url)  # never in command text
    try:
        done = subprocess.run(
            [exe, "-NoLogo", "-NoProfile", "-NonInteractive",
             "-Command", FETCH_SCRIPT],
            env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, timeout=90,
            creationflags=subprocess.CREATE_NO_WINDOW)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return done.returncode == 0


def is_missing_issuer(exc):
    """True for the certificate failure that a root fetch can cure."""
    reason = getattr(exc, "reason", exc)
    return (isinstance(reason, ssl.SSLCertVerificationError)
            and MISSING_ISSUER in str(reason))


def urlopen_fresh_windows(url, timeout=60):
    """urlopen that lets Windows fetch a missing root, then retries once."""
    try:
        return urllib.request.urlopen(
            url, timeout=timeout, context=ssl.create_default_context())
    except (urllib.error.URLError, ssl.SSLError) as exc:
        host = urllib.parse.urlsplit(url).hostname
        if (sys.platform != "win32" or not is_missing_issuer(exc)
                or os.environ.get("SSL_CERT_FILE") or host in _tried_hosts):
            raise
        _tried_hosts.add(host)
        if not let_windows_fetch_root(url):
            raise
    # A new context reads the Windows store again, including the new root.
    return urllib.request.urlopen(
        url, timeout=timeout, context=ssl.create_default_context())
```

Why each detail matters:

- **New context.** The old `SSLContext` keeps its copy of the store;
  only a context built after the fetch sees the new root.
- **System directory.** A `powershell.exe` planted on `PATH` or in the
  working directory is never run.
- **URL in the environment.** The URL is never parsed as PowerShell
  code, and the script contains no double quotes for Windows
  command-line quoting to split.
- **`-UseBasicParsing`.** Since the December 2025 security update for
  CVE-2025-54100, `Invoke-WebRequest` in Windows PowerShell 5.1 prompts
  before parsing a page unless this switch is present. An unattended
  request would stall or fail on that prompt.
- **`exit 0`.** A caught request error still makes `-Command` exit 1,
  which would read as "PowerShell could not run" and skip the retry.
- **TLS 1.2.** Current Windows 11 reports `SystemDefault`; adding
  `Tls12` is harmless insurance on older configurations.
- **Once per host.** A second failure means Windows could not supply
  the root, for example behind a TLS-inspecting proxy, with automatic
  root updates disabled, or with the update endpoint blocked. Report
  that instead of looping.

Applied to a local server whose private root Windows cannot fetch, the
helper detected the real error, ran the real PowerShell request once,
retried once, and re-raised the original error.

### Verifying Without a Fresh Guest

The Sandbox may not cooperate, and a used host already holds most
roots. Verify on the host by forcing one missing-issuer failure through
a test seam, then letting the real PowerShell request and the retry run
against a real host. Add a Windows-only unit test that runs the real
PowerShell script against a closed local port, to prove that a failed
request still exits 0. Record that the fresh-guest check remains open
until a guest run confirms it.

### Related TLS Sharp Edges

- `SSL_CERT_FILE` and tool-specific CA-bundle options replace the system
  store; they do not extend it. A root fetched by Windows does not help
  a client that uses a bundle.
- Python 3.13 adds `VERIFY_X509_STRICT` and `VERIFY_X509_PARTIAL_CHAIN`
  to the default context. Some certificates that other clients accept,
  including some TLS-inspection roots, can fail the stricter checks.
- A pristine guest lacks enterprise roots and proxy settings that the
  host received from policy. A corporate network can therefore break
  every client in the guest, which no root fetch can fix.

## Installers and Scripts on a Fresh Windows

- **Interpreters.** Check with `Get-Command` and run the found binary
  with `--version`. On a normal Windows, `python.exe` and `python3.exe`
  app execution aliases can open the Store instead of running Python.
  Whether those aliases exist in a Sandbox guest is unknown. Carry a
  portable interpreter, such as Python's NuGet package, in the inputs.
- **WinGet.** The Sandbox includes neither WinGet nor the Store.
  Microsoft documents bootstrapping it with the `Microsoft.WinGet.Client`
  module and `Repair-WinGetPackageManager`, which needs the network and
  the PowerShell Gallery. On a newly installed full Windows, WinGet
  registers asynchronously after the first sign-in and may be missing
  for a while. Offline installers in the inputs are more predictable.
- **Execution policy.** Start scripts with
  `-ExecutionPolicy Bypass -File`, or accept that `Restricted` blocks
  them. Group Policy settings override the command line.
- **Web requests.** Always pass `-UseBasicParsing` to
  `Invoke-WebRequest` in Windows PowerShell 5.1.
- **Native runtimes.** Install the Visual C++ Redistributable from the
  inputs with `vc_redist.x64.exe /install /quiet /norestart`, or ship an
  application-local copy where its license allows. Check the
  `HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64` `Version`
  value before installing; the package refuses to install over a newer
  version.
- **.NET.** Publish self-contained, or install the matching runtime; a
  framework-dependent app fails without one.
- **Restarts.** Installers that return 3010 want a restart. A restart
  inside the guest keeps state; whether the logon command runs again is
  unknown, so drivers must be idempotent.

## Inventory Script

Run it at the start of a guest run and after each step under test. It
needs only Windows PowerShell 5.1 and prints JSON.

```powershell
# Record what this Windows has, before and after a step.
# Runs under Windows PowerShell 5.1 and prints JSON.
function Probe([scriptblock] $Block) {
    try { & $Block } catch { 'error: ' + $_.Exception.Message }
}
function Get-RegValue([string] $Key, [string] $Name) {
    Probe { (Get-ItemProperty -LiteralPath $Key -ErrorAction Stop).$Name }
}
$me = [Security.Principal.WindowsPrincipal](
    [Security.Principal.WindowsIdentity]::GetCurrent())
$admin = [Security.Principal.WindowsBuiltInRole]::Administrator
$apps = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps'
$vc = 'HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64'
$ndp = 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full'
$fs = 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem'
[ordered]@{
    Time       = (Get-Date).ToString('o')
    OsVersion  = [Environment]::OSVersion.Version.ToString()
    PowerShell = $PSVersionTable.PSVersion.ToString()
    Policy     = Probe { Get-ExecutionPolicy -List |
                 ForEach-Object { "$($_.Scope)=$($_.ExecutionPolicy)" } }
    User       = [Environment]::UserName
    Elevated   = $me.IsInRole($admin)
    Commands   = foreach ($n in 'python', 'py', 'git', 'winget', 'pwsh',
                                'dotnet', 'curl.exe') {
        $c = Get-Command $n -ErrorAction SilentlyContinue |
             Select-Object -First 1
        if ($c) { "$n=$($c.Source)" } else { "$n=missing" }
    }
    Aliases    = Probe { (Get-ChildItem $apps -ErrorAction Stop).Name }
    VcRedistX64 = Get-RegValue $vc Version
    NetFx4Release = Get-RegValue $ndp Release
    LongPaths  = Get-RegValue $fs LongPathsEnabled
    RootCount  = @(Get-ChildItem Cert:\LocalMachine\Root).Count
    Proxy      = Probe { (netsh.exe winhttp show proxy) -join ' ' }
    Defender   = Probe { Get-MpComputerStatus -ErrorAction Stop |
                 Select-Object AMServiceEnabled, RealTimeProtectionEnabled }
    RootsFetched = Probe { Get-WinEvent -ErrorAction Stop -FilterHashtable @{
        LogName = 'Application'; ProviderName = 'Microsoft-Windows-CAPI2'
        Id = 4097 } | ForEach-Object Message }
} | ConvertTo-Json -Depth 4
exit 0
```

The output names the guest user and local paths; that is fine inside a
disposable guest, but review it before publishing results.

## Review Checklist

- Does every assumption about a fresh Windows carry a label, and are
  the unknowns measured rather than guessed?
- Does network code on Windows survive a missing root, either through a
  Windows verifier or a guarded fetch-and-retry?
- Does the retry rebuild the TLS context, run once per host, and stay
  out of the way when a CA bundle is configured?
- Are `Invoke-WebRequest` calls in Windows PowerShell 5.1 using
  `-UseBasicParsing`?
- Do installers and scripts bring or bootstrap their own interpreters
  and runtimes instead of assuming WinGet, Python, Git, or PowerShell 7?

## Further Information

- Microsoft, [Event ID 5: Automatic Root Certificates Update Configuration](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc734126(v=ws.10))
  (archived; describes the on-demand root fetch)
- Microsoft, [Certificates and trust management in Windows](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-trust)
  and [Configure trusted roots and disallowed certificates](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/configure-trusted-roots-disallowed-certificates)
- Python, [ssl: `load_default_certs` and `create_default_context`](https://docs.python.org/3/library/ssl.html)
- Python, [Using Python on Windows](https://docs.python.org/3/using/windows.html)
- truststore, [documentation](https://truststore.readthedocs.io/en/latest/);
  pip, [HTTPS certificates](https://pip.pypa.io/en/stable/topics/https-certificates/)
- Git, [git-config](https://git-scm.com/docs/git-config), for
  `http.sslBackend` and `http.schannelUseSSLCAInfo`
- Microsoft, [Invoke-WebRequest (5.1)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest?view=powershell-5.1)
  and [KB5074596: preventing script execution from web content](https://support.microsoft.com/KB/5074596)
- Microsoft, [about_Execution_Policies (5.1)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-5.1)
  and [What is Windows PowerShell?](https://learn.microsoft.com/en-us/powershell/scripting/what-is-windows-powershell)
- Microsoft, [Use WinGet: Install WinGet on Windows Sandbox](https://learn.microsoft.com/en-us/windows/package-manager/winget/)
- Microsoft, [Universal CRT deployment](https://learn.microsoft.com/en-us/cpp/windows/universal-crt-deployment),
  [Latest supported Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist),
  and [Redistribute Visual C++ files](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files)
- Microsoft, [.NET Framework and Windows versions](https://learn.microsoft.com/en-us/dotnet/framework/install/versions-and-dependencies)
  and [Install .NET on Windows](https://learn.microsoft.com/en-us/dotnet/core/install/windows)
- Microsoft, [Install Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-install),
  for the 24H2 note on inbox Store apps
- FieldManual, [.NET knacks](../../dotnet/README.md) and
  [Agent Shells: Python](../../windows/shells/Python.knack.md)
