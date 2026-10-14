# Verifying Windows Agent Isolation

Reviewed: 2026-10-13. Every probe below was run on Windows 11 with
PowerShell 7.6 and Git for Windows 2.55 inside a session whose home
variables were redirected into the project, and again with them pointed
back at the real profile to confirm that each probe can fail.

## When to Load This Knack

Load this companion after setting up or changing an isolation launcher,
after upgrading Windows, the agent, or Git for Windows, before trusting an
isolated session with sensitive work, and before cleaning up a retired
setup. The [overview](overview.knack.md) explains
what each result means; the
[launcher techniques](launcher.knack.md)
explain how to fix a failure.

## Rules for Probes

- Run probes inside the isolated session, through the same tool the agent
  uses, because isolation is a property of the inherited environment.
- Print classifications and names, never credential values. Prefer
  "project", "real profile", or "elsewhere" to full paths, so the output
  is safe to paste into a record.
- Read only, except for one self-removing canary file written into the
  redirected home.
- Find the real profile from the registry, not from the environment you
  are testing.

## Probe the Environment and the Programs

Save as a script and run it with
`pwsh -NoProfile -File isolation-probe.ps1 -ProjectRoot <project-root>`:

```powershell
param([Parameter(Mandatory)] [string] $ProjectRoot)

# The real profile, read from the registry rather than the environment.
$sid  = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$key  = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList\$sid"
$real = (Get-ItemProperty -LiteralPath $key).ProfileImagePath

function Get-Place([string] $Path) {
    if (-not $Path) { return 'empty' }
    if ($Path.StartsWith("$ProjectRoot\", 'OrdinalIgnoreCase')) {
        return 'project'
    }
    if ($Path -eq $real -or
        $Path.StartsWith("$real\", 'OrdinalIgnoreCase')) {
        return 'real profile'
    }
    return 'elsewhere'
}

foreach ($name in 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA',
                  'XDG_CONFIG_HOME', 'TEMP', 'TMP') {
    $value = [Environment]::GetEnvironmentVariable($name)
    '{0,-34} {1}' -f $name, (Get-Place $value)
}
'{0,-34} {1}' -f 'HOMEDRIVE+HOMEPATH',
    (Get-Place ($env:HOMEDRIVE + $env:HOMEPATH))
foreach ($folder in 'UserProfile', 'ApplicationData',
                    'LocalApplicationData', 'MyDocuments') {
    $path = [Environment]::GetFolderPath($folder, 'DoNotVerify')
    '{0,-34} {1}' -f "known folder $folder", (Get-Place $path)
}
'{0,-34} {1}' -f 'PowerShell $PROFILE', (Get-Place $PROFILE)
$pythonHome = & python -c "import os; print(os.path.expanduser('~'))"
'{0,-34} {1}' -f 'Python home', (Get-Place $pythonHome)

# A write canary through Python's idea of home.
$canary = "isolation-canary-$PID"
& python -c "import os, pathlib; pathlib.Path(os.path.expanduser('~'), '$canary').touch()"
'Canary reached real profile: {0}' -f
    (Test-Path -LiteralPath (Join-Path $real $canary))
Remove-Item -LiteralPath (Join-Path $env:USERPROFILE $canary) -ErrorAction Ignore

# Names only; never print values.
$names = Get-ChildItem env: |
    Where-Object Name -match '^(ANTHROPIC_|CLAUDE_CODE_OAUTH|OPENAI_API_KEY)' |
    Select-Object -ExpandProperty Name
'Inherited credential names: {0}' -f ($names -join ', ')
```

Results observed in a correctly isolated session:

| Probe | Expected | Meaning of a different result |
| --- | --- | --- |
| `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, `XDG_CONFIG_HOME`, `HOMEDRIVE+HOMEPATH` | project | Native tools write to the real profile |
| `TEMP`, `TMP` | real profile, unless redirected on purpose | Temporary files and agent scratch leave the project |
| Known folder `UserProfile` | real profile | This one always ignores the variables |
| Known folders `ApplicationData`, `LocalApplicationData`, `MyDocuments` | project | Real when the operator moved the folder to an absolute path |
| PowerShell `$PROFILE`, Python home | project | The variables did not reach the child process |
| Canary reached real profile | False | Python wrote into the real profile |
| Inherited credential names | empty, or only names deliberately passed through | One login is shared across projects |

With the home variables pointed back at the real profile (and the
write canary left out), every line that had read "project" flipped to
"real profile", or to "empty" for the unset `XDG_CONFIG_HOME`, so the
probe can fail.

## Probe SSH and Git

From Git Bash, with a host alias that exists only in the operator's real
SSH configuration (`ssh -G` only parses configuration; it does not
connect):

```bash
alias_name=example-host
win=$(/c/Windows/System32/OpenSSH/ssh.exe -G "$alias_name" |
  awk '/^hostname /{print $2}')
msys=$(ssh -G "$alias_name" | awk '/^hostname /{print $2}')
[ "$win" != "$alias_name" ] && echo "Windows OpenSSH reads the real config"
[ "$msys" != "$alias_name" ] && echo "Git Bash ssh reads a config under HOME"
```

Observed: only the first line printed. Windows OpenSSH keeps the
operator's keys and agent available to the session; Git Bash's `ssh`
sees only what the redirected home holds. Verify commit identity as
[Git for Agents][git-agents] describes before the first commit.

## Probe Agent State

- The agent's configuration variable, such as `CLAUDE_CONFIG_DIR` or
  `CODEX_HOME`, classifies as "project", and the agent's status command
  (`/status` in Claude Code) shows the expected login for this project.
- A session started from inside another agent session carries no session
  ID, messaging endpoint, or token from its parent.
- Credential Manager holds nothing unexpected for the agent; this lists
  target names, never secrets:

  ```powershell
  cmdkey /list | Select-String -SimpleMatch claude
  ```

## Probe Folder Permissions

```powershell
(Get-Acl -LiteralPath $env:CLAUDE_CONFIG_DIR).Access |
    Select-Object IdentityReference, FileSystemRights, IsInherited

@((Get-Acl -LiteralPath <project-root>).Access | Where-Object {
    $_.AccessControlType -eq 'Allow' -and
    $_.IdentityReference -match 'Everyone|Authenticated Users|\\Users$' -and
    $_.FileSystemRights -match 'Write|Modify|FullControl' }).Count
```

Expect only the operator, SYSTEM, and Administrators on the state folder;
inherited entries are fine when the parent is already private, as inside
the profile. Expect 0 broad write grants on a checkout that other local
accounts must not change.

## Inspect the Redirected Home

- List junctions and symbolic links before copying or deleting it. In
  the PowerShell tool, wrap the call so that an access error does not
  read as failure:

  ```powershell
  $links = try {
      Get-ChildItem -LiteralPath $env:USERPROFILE -Recurse -Force -Depth 6 `
          -Attributes ReparsePoint -ErrorAction Stop
  } catch { @() }
  $links | Select-Object FullName, LinkType, Target
  ```

- Look for application state that child programs built, such as browser
  profiles under `AppData\Local`, and close those programs before
  cleanup. Locked files and safe removal are covered in
  [Processes and Files][links].
- Check the size of `%TEMP%\claude\<project>` and similar trees left in
  the real profile.

## Record the Result

Keep a short table in the project's records: probe, expected result,
actual result, date, and the versions of Windows, the agent, PowerShell,
and Git for Windows. Repeat it after each upgrade; isolation regressions
are silent.

## Review Checklist

- Were probes run inside the isolated session, through the agent's tool?
- Did the output avoid credential values and full paths?
- Did every home variable and Python home classify as "project"?
- Was each "real profile" result an accepted, documented exception?
- Was the probe also seen to fail with isolation removed?
- Were links, locked files, and leftover temporary trees checked before
  cleanup?

## Further Information

- Microsoft, [Environment.GetFolderPath](https://learn.microsoft.com/en-us/dotnet/api/system.environment.getfolderpath)
- Microsoft, [SHGetKnownFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath)
- Microsoft, [cmdkey](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmdkey)
- Microsoft, [Get-Acl](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl)
- OpenSSH, [ssh(1) manual: the `-G` option](https://man.openbsd.org/ssh#G)
- FieldManual, [Proving Checks Can Fail][proving]

[git-agents]: ../../windows/git/overview.knack.md
[links]: ../../windows/processes-and-files/links-and-copies.knack.md
[proving]: ../../software-engineering/testing/proving-checks/overview.knack.md
