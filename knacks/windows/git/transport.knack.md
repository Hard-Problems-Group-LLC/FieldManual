# Git Transport for Agents on Windows

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when a Git network operation from an agent hangs,
prompts, or fails on Windows, or before scripting fetch, push, clone, or
submodule updates for unattended use. Read the
[Git for agents overview](overview.knack.md) first. Host
aliases and per-organization keys are covered by
[GitHub SSH and Git identity across organizations](../../authentication/GitHub-SSH-multi-org-sanity.knack.md).

All names below are fictional: the host alias `github-alpha`, the
organization `example-org`, and the repositories `example-app` and
`example-lib`.

## Two SSH Clients

A Windows workstation with Git for Windows usually has two OpenSSH
clients:

| Client | Location | Finds `.ssh\config` in | Uses Windows `ssh-agent` service |
| --- | --- | --- | --- |
| Windows OpenSSH | `C:\Windows\System32\OpenSSH\ssh.exe` | The account's registered profile folder | Yes |
| Git for Windows' bundled SSH | Inside the Git installation | `~/.ssh`, where `~` follows `HOME` | No |

Microsoft's documentation describes the client file as
`%userprofile%\.ssh\config`. In the Win32-OpenSSH source, however, the
home directory comes from the profile path registered for the account's
security identifier under
`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList`, not from
the `USERPROFILE` or `HOME` variables.

Windows OpenSSH is an optional feature; check that the executable exists,
or ask the operator to run `Get-WindowsCapability -Online` from an
elevated prompt. Its `ssh-agent` service is disabled by default; enabling
it needs an administrator and is the operator's decision. Once the
operator has loaded a key with `ssh-add`, Windows OpenSSH uses it without
prompting.

For agents, prefer Windows OpenSSH: keys the operator loaded into the
agent service work without passphrase prompts, and its configuration does
not follow a sandbox's redirected `HOME` or `USERPROFILE`. This has been
observed in practice: under a launcher that redirected both variables,
Git Bash's `ssh` could not see a host alias defined in the real profile's
`.ssh\config`, while `C:\Windows\System32\OpenSSH\ssh.exe` found it.
Confirm the resolved settings with `ssh -G <alias>`.

The same fact cuts the other way: an agent running under such a launcher
still reaches the operator's real SSH configuration and the keys in the
shared `ssh-agent` service. Redirecting the profile does not isolate SSH
credentials. See
[Windows agent isolation](../../sandboxing/windows-agents/overview.knack.md)
and [Claude Code on Windows](../../AI/Anthropic/claude-code/windows/overview.knack.md).

## Select the Client and Forbid Prompts

Set `GIT_SSH_COMMAND` for the command or session. Git runs the value
through a shell, so use forward slashes; backslashes would be consumed.

Bash:

```bash
export GIT_SSH_COMMAND='C:/Windows/System32/OpenSSH/ssh.exe -o BatchMode=yes -o ConnectTimeout=15'
export GIT_TERMINAL_PROMPT=0
git -C /c/work/example-app fetch origin
```

PowerShell:

```powershell
$env:GIT_SSH_COMMAND = 'C:/Windows/System32/OpenSSH/ssh.exe -o BatchMode=yes -o ConnectTimeout=15'
$env:GIT_TERMINAL_PROMPT = '0'
git -C C:\work\example-app fetch origin
```

`core.sshCommand` stores the same value in configuration; the environment
variable overrides it. Changing the operator's global configuration is a
persistent change that needs their agreement.

What the options do:

- `BatchMode=yes` disables password and passphrase prompts and host-key
  confirmation. A missing key, a locked key, or an unknown host now fails
  immediately with an error instead of waiting for input.
- `ConnectTimeout=15` bounds the TCP connection and initial handshake. It
  does not bound a slow transfer; use a time limit for that.
- Do not add `StrictHostKeyChecking=no`. Batch mode makes an unknown host
  key fail, which is the point. Have the operator verify and record the host
  key once, against the provider's published fingerprints.

## Diagnose SSH Without Guessing

```powershell
ssh -G github-alpha                 # resolved settings; no network
Get-Service ssh-agent               # Running, Stopped, or Disabled
ssh-add -l                          # keys the agent service holds
ssh -o BatchMode=yes -T git@github-alpha
```

GitHub answers a successful `ssh -T` with a greeting naming the
authenticated account and explaining that it does not provide shell
access. Read that message, and confirm the account is the intended one,
rather than relying on the exit status. A "Permission denied
(publickey)" result in batch mode means no usable key was offered: check
the alias's `IdentityFile`, `IdentitiesOnly`, and the agent's key list.

"Repository not found" after successful authentication usually means the
owner or repository name is wrong, or the authenticated account cannot see
the repository. Check how sibling repositories from the same organization
spell their remotes with `git remote -v` before guessing names.

## HTTPS Remotes and Invisible Prompts

An HTTPS remote may invoke Git Credential Manager, which can open a browser
or a dialog on the desktop. An agent cannot see or answer it, so the
command hangs until something kills it. Mitigations:

- `GIT_TERMINAL_PROMPT=0` stops Git's own terminal prompts;
- `GCM_INTERACTIVE=never` makes Git Credential Manager fail when it would
  need interaction;
- a time limit around the command; and
- an SSH remote where the operator permits it.

Rewriting a remote URL changes repository configuration. For a one-off
command, rewrite instead:

```bash
git -c url."git@github-alpha:example-org/".insteadOf="https://github.com/example-org/" \
    -C /c/work/example-app fetch origin
```

A common trap is a successful push to an explicit SSH URL followed by a
plain `git fetch origin` when `origin` is still HTTPS: the push works and
the fetch hangs on a credential prompt. After pushing to an explicit URL,
update the tracking ref directly, or fetch through the same URL:

```bash
git push git@github-alpha:example-org/example-app.git feature/x:feature/x
git update-ref refs/remotes/origin/feature/x feature/x
# or
git fetch git@github-alpha:example-org/example-app.git \
    feature/x:refs/remotes/origin/feature/x
```

## Time Limits

Bash in Git for Windows includes GNU `timeout`:

```bash
timeout 120 git -C /c/work/example-app push origin feature/x
status=$?
[ "$status" -eq 124 ] && echo "push timed out; state unknown"
```

Do not pipe the command before reading its status: after
`timeout 120 git push ... 2>&1 | tail -3`, `$?` is `tail`'s status. Use
`${PIPESTATUS[0]}` or `set -o pipefail`.

PowerShell 7 can start Git directly, wait with a limit, and stop the whole
process tree, including `ssh` or `git-remote-https` helpers:

```powershell
function Invoke-GitWithLimit {
    param([string]$Repo, [string[]]$GitArgs, [int]$Seconds = 120)
    $psi = [System.Diagnostics.ProcessStartInfo]::new('git')
    $psi.UseShellExecute = $false
    foreach ($a in @('-C', $Repo) + $GitArgs) { $psi.ArgumentList.Add($a) }
    $p = [System.Diagnostics.Process]::Start($psi)
    if (-not $p.WaitForExit($Seconds * 1000)) {
        taskkill /PID $p.Id /T /F | Out-Null
        throw "git $($GitArgs -join ' ') exceeded $Seconds seconds"
    }
    if ($p.ExitCode -ne 0) { throw "git exited with code $($p.ExitCode)" }
}

Invoke-GitWithLimit -Repo 'C:\work\example-app' -GitArgs @('fetch', 'origin')
```

`ProcessStartInfo.ArgumentList` does not exist in Windows PowerShell 5.1;
there, build the argument string yourself or call the script from `pwsh`.

After a timeout, the remote may or may not have accepted the operation.
Compare `git ls-remote origin <branch>` with the local commit before
retrying a push.

## Submodules Over Host Aliases

`git submodule add` records the URL exactly as typed, and `.gitmodules` is
shared with every collaborator. A personal host alias such as
`git@github-alpha:example-org/example-lib.git` there resolves only on
machines that define the alias. Keep the canonical URL in `.gitmodules`
and map it locally:

```bash
git config --global url."git@github-alpha:example-org/".insteadOf "git@github.com:example-org/"
```

The superproject's `.git/config` holds the operative submodule URL once a
submodule is initialized, and it takes precedence over `.gitmodules`.
After a URL changes in `.gitmodules`, `git submodule sync` copies it into
`.git/config`. Run submodule updates with the same non-interactive settings
and a time limit:

```bash
timeout 300 git -C /c/work/example-app submodule update --init --recursive
```

Run the same update after merging or checking out a branch that adds a
submodule; until then the submodule's folder is empty.

Avoid multiple worktrees of a superproject with submodules; Git documents
that support as incomplete.

## Review Checklist

- Does `GIT_SSH_COMMAND` name Windows OpenSSH with forward slashes and
  `BatchMode=yes`?
- Is the host key already recorded and verified?
- Does `ssh -G` show the intended identity file for the alias?
- Are `GIT_TERMINAL_PROMPT=0` and, for HTTPS, `GCM_INTERACTIVE=never` set?
- Is every network command bounded, and is a timeout treated as unknown
  state?
- Do shared files such as `.gitmodules` contain only canonical URLs?

## Further Information

- Git, [git: `GIT_SSH_COMMAND` and `GIT_TERMINAL_PROMPT`](https://git-scm.com/docs/git)
- Git, [git-config: `core.sshCommand` and `url.<base>.insteadOf`](https://git-scm.com/docs/git-config)
- Git, [gitsubmodules](https://git-scm.com/docs/gitsubmodules)
- OpenBSD, [ssh_config: `BatchMode`, `ConnectTimeout`, `StrictHostKeyChecking`](https://man.openbsd.org/ssh_config)
- Microsoft, [OpenSSH for Windows overview](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_overview)
- Microsoft, [Key-based authentication in OpenSSH for Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)
- Microsoft, [OpenSSH server configuration, including client configuration file order](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh-server-configuration)
- Git Credential Manager, [environment variables](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/environment.md)
- GitHub, [Testing your SSH connection](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection)
- GitHub, [GitHub's SSH key fingerprints](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)
- Unity, [Use Windows OpenSSH with Git](https://docs.unity3d.com/Manual/upm-config-ssh-git-win.html)
  (secondary source for selecting Windows OpenSSH through `core.sshCommand`)
