# Visual Studio Installer from the Command Line

Reviewed: 2026-10-13

Load this companion after the
[Visual Studio overview](overview.knack.md) when a script must
update, modify, repair, roll back, or describe a Visual Studio instance, or
when a build broke after an update. Installer operations change shared
machine state. Run them only when the operator asked for them, never as a
side effect of a build, and never while another session is using the
instance.

This companion is drawn from Microsoft's documentation; its commands were
not executed while it was written, because each would have modified the
instance under test.

## The Installer

The installed Visual Studio Installer lives at:

```text
%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\setup.exe
```

Microsoft notes that it must be started from a different working directory
than its own folder. Edition bootstrappers, such as `vs_community.exe` or
`vs_buildtools.exe`, install new instances; `setup.exe` maintains existing
ones. The first argument is a command; options use two dashes and are not
case-sensitive.

| Command | Purpose |
| --- | --- |
| `update` | Update an instance to the latest release on its channel. |
| `updateall` | Update every installed instance in turn. |
| `modify` | Add or remove workloads and components. |
| `repair` | Repair an instance. |
| `rollback` | Return an instance to its previously installed update. |
| `export` | Write the instance's configuration to a `.vsconfig` file. |
| `uninstall` | Remove an instance. |

`--installPath` is required for `update` and `modify` and recommended for the
others, so the command acts on the intended instance. Take the path from
`vswhere`.

## Unattended Updates

```powershell
$setup = Join-Path ${env:ProgramFiles(x86)} `
    'Microsoft Visual Studio\Installer\setup.exe'
Push-Location $env:TEMP   # not the installer's own folder
try {
    $p = Start-Process $setup -Wait -PassThru -ArgumentList @(
        'update', '--installPath', "`"$vsPath`"", '--passive', '--norestart')
    "Installer exit code: $($p.ExitCode)"
}
finally { Pop-Location }
```

- `--passive` shows progress without prompts; `--quiet` shows nothing. Both
  require administrator rights regardless of the standard-user policy.
- `--norestart` must accompany `--passive` or `--quiet` and delays a
  required reboot.
- `--force` closes running Visual Studio processes and can lose work; avoid
  it in shared sessions.
- The installer's `--wait` switch is for bootstrappers only; with
  `setup.exe`, wait on the process instead, as above.

## Exit Codes

| Code | Meaning |
| --- | --- |
| 0 | Success |
| 740 | Elevation required |
| 1001 | Installer process already running |
| 1003 | Visual Studio is in use |
| 1618 | Another installation is running |
| 1641 | Success, and a reboot was started |
| 3010 | Success, but a reboot is required before use |
| 5007 | Blocked: the computer does not meet requirements |
| 8006 | Visual Studio processes are running |

Treat 3010 as "not ready": until the reboot, `vswhere` without `-all` may not
return the instance, and builds may use a partly updated toolchain. Logs are
written to `%TEMP%` as files beginning `dd_bootstrapper`, `dd_client`, and
`dd_setup`.

## Rollback

From Visual Studio 2022, an instance can return to its previous update unless
policy disables rollback:

```powershell
& $setup rollback --installPath "$vsPath"
```

Use it when an update demonstrably broke a build, after recording both
versions. Plan a forward fix too; the rolled-back release will be offered
again.

## Updates You Did Not Start

- Microsoft Update can deliver monthly Visual Studio security updates to
  Community edition on unmanaged machines that enable "Receive updates for
  other Microsoft products" in Windows Update's advanced options. The update
  applies once Visual Studio is closed, typically during idle time.
- Organizations can deploy administrator updates through their update
  management systems.
- The installer itself may update before it updates a product.

Any of these can coincide with a Windows restart. After a restart, re-run
the version record from the discovery companion before trusting comparisons
with earlier builds.

## Record the Required Configuration

Export the workloads and components an instance has, and keep the file with
the project so that another machine can be brought to the same state:

```powershell
& $setup export --installPath "$vsPath" --config "$PWD\.vsconfig"
```

A `.vsconfig` file is JSON with a `components` array and optional
`extensions`. Apply it to an existing instance with `modify --config`; to add
components, `update` is not enough. When a `.vsconfig` file sits in a
solution's root, Visual Studio detects missing components on opening the
solution and offers to install them. Trim an exported file to what the
project needs before committing it.

## Review Checklist

- Did the operator request the installer operation?
- Is the instance chosen by `--installPath` from `vswhere`?
- Are exit codes checked, with 3010 treated as incomplete?
- Are versions recorded before and after?
- Does the project keep a trimmed `.vsconfig` describing what it needs?

## Further Information

- [Use command-line parameters to install Visual Studio](https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio)
- [Command-line parameter examples](https://learn.microsoft.com/en-us/visualstudio/install/command-line-parameter-examples)
- [Import or export installation configurations](https://learn.microsoft.com/en-us/visualstudio/install/import-export-installation-configurations)
- [Update Visual Studio](https://learn.microsoft.com/en-us/visualstudio/install/update-visual-studio)
- [Visual Studio security updates through Microsoft Update](https://devblogs.microsoft.com/visualstudio/automatically-install-visual-studio-security-updates-through-microsoft-update/)
- [Workload and component IDs](https://learn.microsoft.com/en-us/visualstudio/install/workload-and-component-ids)
