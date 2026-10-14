# Agent Shells on Windows

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack when an AI coding agent, or a person supervising one, runs
commands on a Windows workstation through a harness-provided shell. It
covers telling the shells apart, working-directory and state loss between
calls, path forms, quoting through several interpreters, and the habit that
prevents most damage: write a script file, then run it.

Companions:

- [PowerShell](PowerShell.knack.md): Windows PowerShell
  5.1 versus PowerShell 7, encoding defaults, here-strings, native
  arguments, and exit codes;
- [Git Bash](Git-Bash.knack.md): MSYS path conversion,
  `/c/` paths, and calling Windows programs from a POSIX shell;
- [Text files](text-files.knack.md): encodings, byte-order
  marks, line endings, `core.autocrlf`, and byte-preserving edits; and
- [Python](Python.knack.md): which interpreter runs,
  standard-stream encodings, Windows paths in source, and project-local
  dependencies.

## Mental Model

A Windows workstation usually offers several unrelated shells, and an agent
harness may expose more than one of them as separate tools:

| Shell | Executable | Character |
| --- | --- | --- |
| Git Bash | `bash.exe` from Git for Windows | POSIX shell on the MSYS runtime |
| PowerShell 7 | `pwsh.exe` | Cross-platform PowerShell on .NET |
| Windows PowerShell 5.1 | `powershell.exe` | In-box PowerShell on .NET Framework |
| Command Prompt | `cmd.exe` | Legacy batch interpreter |

Each has its own quoting rules, variable syntax, path conventions, default
text encoding, and exit-status model. A command that is correct in one is
often a syntax error, or worse a different valid command, in another.
PowerShell 7 and Windows PowerShell 5.1 install side by side and are not
interchangeable: their encoding defaults and native-argument handling
differ.

Treat every tool call as a fresh, short-lived process unless the harness
documents otherwise. The working directory may be reset between calls, and
shell variables, functions, and `cd` from one call do not survive into the
next. Environment changes made inside a call vanish with it.

Treat the shell as a transport for commands, not as a text editor. Any text
that passes through a command line is reinterpreted by every layer it
crosses.

## Identify the Shell Before Acting

Probe cheaply when the tool name does not settle the question:

| Probe | Git Bash | PowerShell 7 | Windows PowerShell 5.1 |
| --- | --- | --- | --- |
| `echo $MSYSTEM` | `MINGW64` or similar | empty line | empty line |
| `$PSVersionTable.PSEdition` | not a command | `Core` | `Desktop` |
| `$PSVersionTable.PSVersion` | not a command | 7.x | 5.1.x |

A PowerShell process launched from Git Bash, or `powershell.exe` launched
from `pwsh`, is a new interpreter with its own rules. Record which shell a
script targets in its first comment line.

## Working Directory and State

- Use absolute paths in every command. Do not rely on an earlier `cd`.
- Prefer tools that accept a target explicitly, such as `git -C <repo>`,
  over changing directory first.
- Set environment variables in the same call that needs them, for example
  `GIT_SSH_COMMAND=... git fetch` in Bash or `$env:NAME = 'value'; tool`
  in PowerShell.
- In PowerShell, prefer `-LiteralPath` so that `[` and `]` in file names
  are not treated as wildcards.

## Path Forms

The same directory has several spellings:

| Form | Example | Accepted by |
| --- | --- | --- |
| Native | `C:\work\example-app` | Windows programs, PowerShell, cmd |
| Mixed | `C:/work/example-app` | Most Windows APIs, Git, Python, PowerShell |
| MSYS | `/c/work/example-app` | Git Bash and MSYS programs only |

Mixed form is the most portable choice in scripts that several shells or
tools read. Never hand an MSYS path to a native program unless the MSYS
runtime converts it; the Git Bash companion explains when that conversion
happens and when it corrupts arguments instead.

## Quoting Through Layers

An inline command often crosses three or four interpreters: the harness,
the outer shell, an inner interpreter such as `python -c` or
`powershell -Command`, and finally the target program's own argument
parser. Each layer may consume `$`, backslashes, backticks, quotation
marks, and percent signs. The result can be a command that runs
successfully and does the wrong thing.

Non-ASCII text adds a further hazard. Console code pages on many systems
are still legacy single-byte pages, so characters such as an em dash or a
trademark sign can be replaced with a best-fit ASCII character, a question
mark, or mojibake when they cross a pipe. Windows PowerShell 5.1 also reads
UTF-8 files that lack a byte-order mark as the legacy ANSI code page. See
the [text files](text-files.knack.md) companion.

## Write a Script File, Then Run It

For anything longer than a short ASCII one-liner:

1. Write the script with the agent's file-writing tool, which writes the
   exact characters as UTF-8, instead of a shell here-document or `echo`.
2. Put it in the project's ignored local scratch area, such as
   `.local/tmp/`, following FieldManual's
   [local operator state](../../../standards-and-practices/core/local-operator-state.md)
   standard.
3. Run it with an explicit interpreter and no profile:
   `pwsh -NoProfile -File <script>.ps1`, `python <script>.py`, or
   `bash <script>.sh`.
4. Check the exit status, then delete the script unless it is evidence.

A script for Windows PowerShell 5.1 that contains non-ASCII characters must
be saved as UTF-8 with a byte-order mark, or 5.1 misreads it. PowerShell 7
reads BOM-less UTF-8 correctly.

Inline commands remain fine for short, ASCII-only, single-interpreter work
such as `git -C <repo> status --short`.

## Sharp Edges

- `timeout` names two different programs. In Git Bash it is GNU coreutils
  and limits a command's run time; in cmd and PowerShell it is
  `timeout.exe`, which only pauses.
- `&&` and `||` exist in PowerShell 7 but are parse errors in Windows
  PowerShell 5.1.
- A non-zero exit code from a native program does not stop a PowerShell
  script by default; check `$LASTEXITCODE`.
- Some tools report success with a non-zero code. For example, `robocopy`
  uses codes below 8 for success.
- POSIX `find`, `sort`, and `rm` in Git Bash differ from the Windows
  programs of the same or similar names in cmd and PowerShell.
- Recursive deletion near directory junctions needs care; see
  [processes and files](../processes-and-files/links-and-copies.knack.md).
- A search from `/` in Git Bash, or a recursive search of a whole drive,
  can run for many minutes and outlast the harness's time limit. Search
  known roots, and record where tools and packages live once found.
- When a command prints its verdict last, do not cut its output to the
  first lines. Capture all of it, then show the end.

## Review Checklist

- Is the target shell named and verified, not assumed?
- Does every path in the command stand on its own?
- Does any inline command nest more than one interpreter or contain
  non-ASCII text? If so, write a script file instead.
- Was the script written as UTF-8, with a BOM only where Windows PowerShell
  5.1 requires one?
- Does the caller check the exit status in the way the shell defines it?
- Are scratch files inside an ignored project-local folder and removed
  afterwards?

## Further Information

- Microsoft, [Differences between Windows PowerShell 5.1 and PowerShell 7.x](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell)
- Microsoft, [about_Character_Encoding](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding)
- Microsoft, [about_Automatic_Variables](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_automatic_variables)
- Microsoft, [about_Pipeline_Chain_Operators](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipeline_chain_operators)
- Microsoft, [Console code pages](https://learn.microsoft.com/en-us/windows/console/console-code-pages)
- Microsoft, [timeout command](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/timeout)
- MSYS2, [Filesystem paths](https://www.msys2.org/docs/filesystem-paths/)
