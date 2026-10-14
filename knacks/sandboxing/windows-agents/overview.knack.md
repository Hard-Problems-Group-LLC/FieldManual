# Windows Agent Isolation

Reviewed: 2026-10-13. The observations below come from Claude Code 2.1.287
on Windows 11 with Git for Windows 2.55 and PowerShell 7.6. Isolation
behavior depends on Windows, agent, and tool versions; repeat the
[verification](verification.knack.md) after any
upgrade.

## When to Load This Knack

Load this knack when a coding agent such as Claude Code or Codex runs on
native Windows and you must decide what it can reach: keeping its state
and its tools' configuration out of the operator's profile, separating
projects or clients, or choosing between home redirection, a separate
account, Windows Sandbox, and a virtual machine.

Companions:

- [Launcher techniques](launcher.knack.md):
  building a project-local launcher that pins agent state, redirects every
  home variable, scrubs credentials, and owns the agent's process; and
- [Verification](verification.knack.md):
  probes that show what an isolated session actually reaches.

## Threat Model

Two different risks motivate isolation:

1. **State blast radius.** Tools write wherever the environment says home
   is: configuration, caches, self-updaters, and logins. A bad update or a
   stray write into the real profile can break every project on the
   machine at once. Home redirection addresses this.
2. **Action blast radius.** A command the agent runs can read, change, or
   send anything the Windows account can. A prompt injection, a mistaken
   cleanup, or an over-broad script acts with the operator's rights. Only
   an operating-system boundary addresses this: the agent's own sandbox, a
   separate account, Windows Sandbox, or a virtual machine.

Home redirection is a state boundary, never a security boundary. Say which
one a setup provides.

## Three Independent Axes

| Axis | Mechanism | Separates |
| --- | --- | --- |
| Agent state | The agent's own variable: `CLAUDE_CONFIG_DIR`, `CODEX_HOME` | Logins, transcripts, history, and settings per project |
| Tool state | Redirecting every home variable | Global configuration and caches of the tools the agent runs |
| Execution | Sandbox, account, or virtual machine | What commands can touch |

Pin agent state at every level of home isolation, so that raising or
lowering it never forks a login or session history.

## Why `HOME` Is Not Enough

Windows programs find "home" in different places:

| Consumer | Where it looks | Basis |
| --- | --- | --- |
| Git Bash and other MSYS programs, including Git Bash's `ssh` | `HOME` | Observed |
| Python 3.8 and later, `os.path.expanduser` | `USERPROFILE`, then `HOMEDRIVE` plus `HOMEPATH`; never `HOME` | Python documentation |
| Node.js `os.homedir()` | `USERPROFILE`, then the profile path | Node.js documentation |
| PowerShell `$HOME` and `$PROFILE`; PowerShell 7's user module path | `USERPROFILE` and the Documents folder | Observed |
| Windows PowerShell 5.1's user module path | The real profile's Documents folder | Observed |
| Known-folder APIs for the profile itself (`SHGetKnownFolderPath` with `FOLDERID_Profile`, .NET `UserProfile`) | The account's registered profile path, ignoring the variables | Observed |
| Known-folder APIs for AppData, Local AppData, Documents, and Desktop | Registry values relative to `%USERPROFILE%`, expanded with the calling process's environment | Observed |
| Windows OpenSSH | The profile path registered for the account under `HKLM\...\ProfileList`, ignoring `HOME` and `USERPROFILE` | Source code; observed |
| Temporary files | `TMP`, then `TEMP`, then `USERPROFILE` | Microsoft documentation |

Redirecting `HOME` alone moves only the MSYS tools and splits programs
that read both kinds of variable across two homes. Redirect the set
together, from one path:

- `HOME` and `USERPROFILE`;
- `HOMEDRIVE` and `HOMEPATH`, split from the same path;
- `APPDATA` as `<home>\AppData\Roaming` and `LOCALAPPDATA` as
  `<home>\AppData\Local`; and
- `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `XDG_STATE_HOME`, and
  `XDG_DATA_HOME` beneath the same home.

Decide about `TMP` and `TEMP` deliberately. Left alone, temporary files,
agent scratch space, and task output land in the real profile; observed:
46 MB for one project. Never leave `USERPROFILE` empty: Python's
`Path.home()` then falls back to the current directory.

## What Still Reaches the Real Profile

With every home variable redirected, these remain shared:

- **Credential Manager**, including Git Credential Manager, and any agent
  login kept there. Claude Code documents its Windows login as a file in
  its configuration folder; a launcher's authors warn that an entry keyed
  to that folder may also appear in Credential Manager and outlive the
  checkout.
- **The registry** under `HKCU`, including `HKCU\SOFTWARE\Policies`.
- **The profile folder itself.** Code that asks Windows for the profile
  (`FOLDERID_Profile`, `GetUserProfileDirectoryW`) gets the real one.
  Folders the operator moved to absolute locations, such as a synced
  Documents folder, also stay real; inherited `PSModulePath` entries may
  name real-profile folders too. Conversely, every lookup relative to
  `USERPROFILE`, including the known-folder APIs for AppData and
  Documents, lands in the fake home and misses real data, such as a game's
  logs under `AppData\LocalLow` written by a copy started outside the
  agent. Derive such paths from the real profile, or pass them explicitly.
- **Windows OpenSSH** keys, configuration, and the `ssh-agent` service.
  Observed: Git Bash's `ssh` failed to resolve a host alias while Windows
  OpenSSH resolved it, because only the latter read the real `.ssh`
  folder. See [Git transport][git-transport].
- **Credentials in the environment**, such as API keys inherited from the
  operator's shell, and cloud SDK credential chains.
- **Machine-wide state:** program folders, `HKLM`, services, and managed
  agent settings under `C:\Program Files`.
- **Everything else the account can reach:** every readable file, and the
  operator's other processes and windows.

## What Redirection Hides

Per-user locations that follow the redirect lose what the operator
installed there. A known folder whose redirected directory does not exist
fails: observed, `SHGetKnownFolderPath` for Documents returned
`0x80070002` and .NET `GetFolderPath(MyDocuments)` an empty string. Create
the standard folders in the redirected home, or expect tools that ask for
them to fail.

App execution aliases live in `%LOCALAPPDATA%\Microsoft\WindowsApps`.
Code that builds that path from the redirected variable finds nothing,
although `PATH`, expanded at logon, normally still lists the real folder,
so an alias such as Windows Sandbox's `wsb.exe` still resolves by name
(observed) unless the launcher rebuilt `PATH`. Locate such tools by name or
from their package, as [Windows Sandbox][wsb-cli] shows. User
site-packages and PowerShell 7 user modules vanish the same way; see
[Agent Shells: Python][python].

## What Leaks Into the Redirected Home

Programs the agent starts build real application state in the redirected
home. Observed in one project:

- a browser opened by a tool wrote a full profile under
  `<home>\AppData\Local\Google\Chrome\User Data`; with .NET first-run
  files, NuGet, and another browser's cache, `AppData\Local` reached about
  140 MB;
- a junction appeared under `INetCache`; and
- a browser left running held 834 files locked, so deleting the redirected
  home failed with "Permission denied" until a reboot.

Exclude the redirected home from searches, copies, and project moves;
close child browsers before cleanup; and read
[Processes and Files][proc-files] before removing anything with links in
it.

## Choose a Stronger Boundary When Needed

| Boundary | Separates | Still shared or exposed |
| --- | --- | --- |
| Home redirection | Agent and tool state | Everything in the shared list above |
| The agent's own sandbox | Writes and network for its commands | Varies: Claude Code has none on native Windows (use WSL2); Codex documents native Windows sandbox modes |
| WSL2 | A Linux user space where Linux sandboxes work | Windows drives under `/mnt`, and Windows programs started through interop |
| A separate standard Windows account | Profile, `HKCU`, Credential Manager, SSH keys | Machine-wide state, and files other local accounts can write |
| [Windows Sandbox][wsb] | A disposable Windows | Mapped folders, and the network unless disabled |
| A virtual machine | Everything not explicitly shared | Shared folders and the network; see [virtual-machine control][vm] |

For client work, use a separate account or a virtual machine. At minimum,
keep checkouts where only you can write: a folder created under a drive
root such as `C:\work` inherits Modify for every authenticated user.

## Review Checklist

- Is the setup described honestly as a state boundary, an execution
  boundary, or both?
- Is the agent's configuration variable pinned at every isolation level?
- Are all home variables redirected together from one path?
- Is each still-shared store (Credential Manager, registry, the profile
  folder, SSH, temporary files, environment credentials) acceptable for
  this work?
- Are browser profiles and junctions in the redirected home excluded from
  searches and copies?
- Does work that needs containment run in WSL2, a separate account,
  Windows Sandbox, or a virtual machine?

## Further Information

- Anthropic, [Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing):
  "On native Windows, Claude Code runs commands unsandboxed."
- Anthropic, [Authentication: credential management](https://code.claude.com/docs/en/authentication#credential-management)
- OpenAI, [Codex Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)
  and [environment variables](https://learn.chatgpt.com/docs/config-file/environment-variables)
- Python, [os.path.expanduser](https://docs.python.org/3/library/os.path.html#os.path.expanduser)
- Node.js, [os.homedir()](https://nodejs.org/api/os.html#oshomedir)
- Microsoft, [SHGetKnownFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath)
- Microsoft, [GetTempPath2W](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-gettemppath2w)
- Microsoft, [Key-based authentication in OpenSSH for Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)
- PowerShell team, [Win32-OpenSSH home-directory lookup in `pwd.c`](https://github.com/PowerShell/openssh-portable/blob/latestw_all/contrib/win32/win32compat/pwd.c)
- Microsoft, [Credential Manager in Windows](https://support.microsoft.com/en-us/windows/credential-manager-in-windows-1b5c916a-6a16-889f-8581-fc16e8165ac0)
- Microsoft, [Windows Sandbox](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/)
- FieldManual, [Bubblewrap](../bubblewrap.knack.md), the Linux
  counterpart, and
  [Claude Code on native Windows](../../AI/Anthropic/claude-code/windows/overview.knack.md)

[git-transport]: ../../windows/git/transport.knack.md
[proc-files]: ../../windows/processes-and-files/links-and-copies.knack.md
[wsb]: ../../virtualization/windows-sandbox/overview.knack.md
[wsb-cli]: ../../virtualization/windows-sandbox/configuration.knack.md#the-wsb-command
[python]: ../../windows/shells/Python.knack.md
[vm]: ../../virtualization/virtual-machine-control.knack.md
