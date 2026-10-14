# PowerShell for Agents: 5.1 Versus 7

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when an agent writes, runs, or debugs PowerShell on
Windows, or calls native programs from PowerShell. Read the
[agent shells overview](overview.knack.md) first. The claims
below were checked against the Microsoft Learn pages listed at the end;
recheck them when a new PowerShell release changes defaults.

## Two Products, One Name

| Property | Windows PowerShell 5.1 | PowerShell 7 |
| --- | --- | --- |
| Executable | `powershell.exe` | `pwsh.exe` |
| `$PSVersionTable.PSEdition` | `Desktop` | `Core` |
| Runtime | .NET Framework | .NET |
| First positional argument | `-Command` | `-File` |
| `&&` and `\|\|` | Parse error | Pipeline chain operators |
| Default file encoding | Inconsistent; see below | UTF-8 without BOM |

Both install side by side. A script tested in one is not tested in the
other. Name the target in the script's first comment and launch it
explicitly:

```powershell
pwsh -NoProfile -NonInteractive -File .\.local\tmp\task.ps1
powershell -NoProfile -NonInteractive -File .\.local\tmp\task.ps1
```

`-NoProfile` keeps the operator's profile from changing behavior.
`-NonInteractive` turns a would-be prompt into an error instead of a hang.
When execution policy blocks a local script, `-ExecutionPolicy Bypass` on
the command line applies to that process; do not change machine or user
policy to get one script to run.

## Encoding Defaults

| Operation | Windows PowerShell 5.1 | PowerShell 7 |
| --- | --- | --- |
| `>`, `>>`, `Out-File` | UTF-16LE with BOM | UTF-8, no BOM |
| `Set-Content` or `Add-Content`, new file | ANSI code page | UTF-8, no BOM |
| `-Encoding UTF8` | UTF-8 with BOM | UTF-8, no BOM |
| `-Encoding utf8NoBOM` | Not available | UTF-8, no BOM |
| `Get-Content`, file without BOM | ANSI code page | UTF-8 |
| Script source without BOM | ANSI code page | UTF-8 |
| `$OutputEncoding` (pipe to native) | ASCII | UTF-8, no BOM |

Consequences:

- In 5.1, `git diff > patch.txt` produces a UTF-16LE file that `git apply`
  and most POSIX tools cannot read.
- In 5.1, `-Encoding UTF8` adds a BOM, which can break shell scripts,
  JSON consumers, and tools that compare bytes.
- `Out-File -Append` and `>>` do not match an existing file's encoding.
- A non-ASCII string piped from 5.1 into a native program's standard input
  becomes question marks unless `$OutputEncoding` is changed.

Write BOM-less UTF-8 the same way in both editions through .NET:

```powershell
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($path, $text, $utf8)
```

`[System.IO.File]::ReadAllText($path)` detects a BOM and otherwise assumes
UTF-8, which is usually what a repository file needs.

Reading a native program's output is a separate setting: PowerShell decodes
it with `[Console]::OutputEncoding`, which follows the console code page.
When a tool writes UTF-8, set
`[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false`
before calling it, or have the tool write to a file and read the bytes.

## Strings and Here-Strings

- Single quotes are literal. Double quotes expand `$name`, `$(expr)`, and
  backtick escapes. Prefer single quotes unless expansion is intended.
- In a double-quoted string, `"$env:HOME:"` fails because the colon is
  read as a scope qualifier; write `"${env:HOME}:"`.
- The escape character is the backtick, not the backslash. Backslashes in
  Windows paths need no escaping.
- Smart quotes count as quotation marks, so pasted typographic quotes can
  silently end a string.

A here-string starts with `@'` or `@"` as the last characters on a line and
ends with `'@` or `"@` as the first characters of a line:

```powershell
$body = @'
Literal text; $nothing expands here.
'@
```

The closing marker must start at column 0. Indenting it to match the
surrounding code is a parse error. Use the single-quoted form for file
content, and avoid here-strings inside a `-Command` argument passed from
another shell: write a script file instead.

## Matching Text

PowerShell's string operators are case-insensitive unless the operator
starts with `c`. `'PASS: finished without error' -match '\bError\b'` is
true, so a log scan that counts "Error" lines also counts success messages
that mention an error. For such scans:

- use `-cmatch`, `-clike`, `-ceq`, or `-creplace` when case matters;
- give `Select-String` the `-CaseSensitive` switch, because it is also
  case-insensitive by default;
- use `Select-String -SimpleMatch` for literal markers that contain regex
  characters, such as `[TEST] DONE`; and
- exclude the script's own status lines before counting.

Broad patterns also over-match: `Could not (find|load)` catches benign
lines from dependencies, and a product name matches every path that
contains it. Anchor patterns to the source you care about.

## XML, Binary Files, and .NET Framework Assemblies

- PowerShell's XML adapter maps element and attribute names to
  properties, so `$node.Name` returns a `Name` attribute or child element
  when one exists. Use `$node.LocalName` for the element's own tag name.
- To search a binary file for ASCII strings, decode it as Latin-1
  (`[Text.Encoding]::GetEncoding(28591)`), which maps every byte to one
  character, then apply a regular expression.
- For reflection over .NET Framework or Mono-era assemblies, neither
  edition is reliably better: Windows PowerShell 5.1 runs on .NET
  Framework, yet in one observed case it failed to load types that
  PowerShell 7 loaded. Try both, record which produced the evidence, and
  follow the
  [reflection companion](../../dotnet/assembly-inspection/reflection.PowerShell.knack.md).
  Run inspection scripts in a child process with `-NoProfile -File`, and
  load a copy of a build output so the original stays unlocked.

## Calling Native Programs

PowerShell parses arguments first and then builds a Windows command line
for the program.

- PowerShell 7.3 and later preserve embedded quotes and empty arguments
  (`$PSNativeCommandArgumentPassing`, default `Windows`). Windows
  PowerShell 5.1 uses the older `Legacy` rules, which drop or mangle them.
  In `Windows` mode, batch files and script hosts such as `cmd.exe` still
  receive `Legacy` handling.
- The stop-parsing token `--%` passes the rest of the line verbatim,
  expanding only `%NAME%` variables. It ends at a newline or pipe.
- `Start-Process -ArgumentList` joins its arguments into one command line;
  arguments containing spaces need their own embedded quotation marks.
- Batch files receive raw command lines through `cmd.exe`; never pass
  untrusted input to them as arguments.

When an argument list is complicated, put the values in a file or
environment variable and let the program read them.

## Exit Status and Errors

- `$LASTEXITCODE` holds the last native program's exit code.
  `$?` is `$false` after a native program exits non-zero.
- `$ErrorActionPreference = 'Stop'` does not stop on a native program's
  non-zero exit by default. PowerShell 7.4 added
  `$PSNativeCommandUseErrorActionPreference`; it defaults to `$false`.
- PowerShell 7 does not treat native standard-error output as failure;
  Windows PowerShell 5.1 wraps redirected standard-error lines as error
  records, which can trip `Stop` handling.
- `pwsh -File` exits 1 on an unhandled exception, the `exit` value when
  given, and 0 otherwise.

A defensive pattern for scripts that call native tools:

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Native {
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Exe exited with code $LASTEXITCODE"
    }
}

Invoke-Native git @('-C', $repo, 'status', '--short')
```

Adjust the success test for tools such as `robocopy` whose informational
codes are non-zero.

## Useful Idioms

- Test for a command: `Get-Command git -ErrorAction SilentlyContinue`.
- Absolute path of the script's folder: `$PSScriptRoot`.
- Temporary drive in PowerShell 7: `Temp:\` maps to the user's temporary
  folder, but prefer the project's ignored local folder for agent work.
- Literal file paths: `Get-Item -LiteralPath 'a[1].txt'`.
- Hash of a file for before-and-after checks:
  `Get-FileHash -Algorithm SHA256 -LiteralPath $path`.

## Sharp Edges

- `Get-WinEvent` and `Get-Process -Name` write an error when nothing
  matches, while `Get-CimInstance -Filter` returns nothing silently. Treat
  "no results" deliberately rather than as a generic failure.
- `pwsh -Command` collapses a native program's exit code to 0 or 1; use
  `-File`, or end the command string with `exit $LASTEXITCODE`.
- Under `-Command`, the process exits 1 when the last command set `$?` to
  `$false`, even if `-ErrorAction SilentlyContinue` hid the error. A check
  such as `Get-Process -Name example-app -ErrorAction SilentlyContinue`
  that finds nothing therefore looks like a failed tool call. End with an
  explicit result, for example
  `@(Get-Process -Name example-app -ErrorAction SilentlyContinue).Count`.
  The same happens after a `try` whose `catch` block is empty: in testing,
  both editions exited 1. End helper scripts with `exit 0` or
  `exit $LASTEXITCODE`.
- When a one-off command must cross another shell intact,
  `pwsh -EncodedCommand` takes Base64 of UTF-16LE text and sidesteps the
  outer shell's quoting. A script file is still easier to review.
- Parentheses, subexpressions, and array expressions reset `$?` in 5.1 but
  not in 7.
- Profiles, modules, and execution policy differ between editions because
  each has its own module path and profile files.
- `Remove-Item` on a folder with children prompts unless `-Recurse` is
  given, and `-Confirm:$false` does not suppress that prompt; under
  `-NonInteractive` the prompt becomes an error.
- Since the December 2025 security update for CVE-2025-54100,
  `Invoke-WebRequest` in Windows PowerShell 5.1 shows a confirmation
  prompt before parsing a page unless `-UseBasicParsing` is given. An
  unattended call stalls on the prompt, or fails under `-NonInteractive`.
  Pass `-UseBasicParsing` in every 5.1 script; PowerShell 7 always parses
  this way and is unaffected.

## Further Information

- Microsoft, [Differences between Windows PowerShell 5.1 and PowerShell 7.x](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell)
- Microsoft, [about_Character_Encoding](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding)
- Microsoft, [about_Quoting_Rules](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_quoting_rules)
- Microsoft, [about_Comparison_Operators](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_comparison_operators)
- Microsoft, [Select-String](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/select-string)
- Microsoft, [about_Parsing](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_parsing)
- Microsoft, [about_Preference_Variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_preference_variables)
- Microsoft, [about_Automatic_Variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables)
- Microsoft, [about_Pwsh](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pwsh)
- Microsoft, [about_Execution_Policies](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)
- Microsoft, [Remove-Item](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/remove-item)
- Microsoft, [Invoke-WebRequest (5.1)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest?view=powershell-5.1)
  and [KB5074596: preventing script execution from web content](https://support.microsoft.com/KB/5074596)
