# Claude Code Tools on Windows

Reviewed: 2026-10-13, against the Claude Code tools reference and the
observed behavior of Claude Code 2.1.287 on Windows 11 with Git for
Windows 2.55 and PowerShell 7.6. Limits and messages change between
releases; recheck the [tools reference][tools-ref] before relying on a
number.

## When to Load This Knack

Load this companion when a Claude Code tool call on Windows fails,
truncates, hangs, or is refused, or before scripting work that crosses
quoting, encoding, or time limits. Start with the
[overview](overview.knack.md). General Windows shell
behavior is in [Agent Shells][agent-shells] and its
[Git Bash][git-bash], [PowerShell][pwsh], and [text files][text-files]
companions; this file covers what the Claude Code harness adds.

## Bash Tool

The Bash tool runs each command in a separate Git Bash process.

- **Working directory.** A `cd` carries over only while it stays inside
  the project or an added working directory. A `cd` elsewhere is undone,
  and the result ends with `Shell cwd was reset to <dir>`. Subagents never
  carry a `cd` over. Use absolute paths, or tools that take a target, such
  as `git -C <repo>`.
- **Environment.** An `export` lasts for one command. Set variables in the
  command that needs them, or have the operator set `CLAUDE_ENV_FILE` or a
  SessionStart hook for values every command needs.
- **Startup files.** Aliases and functions are captured from the shell
  startup file at session start. Under a redirected `HOME`, that is the
  redirected home's file, if any.
- **Searches.** Never run `find /` or `grep -r /` in Git Bash; observed: a
  search for a Python package walked every mounted drive past the time
  limit and had to be stopped. Record where tools live instead.

## PowerShell Tool

- Claude Code prefers `pwsh.exe` and falls back to Windows PowerShell 5.1.
  It does not load profiles and starts PowerShell with
  `-ExecutionPolicy Bypass` at process scope, which Group Policy still
  overrides.
- Since 2.1.214, `>` writes UTF-8 even on 5.1, text piped to native
  programs is UTF-8, and a child that waits on standard input receives
  end-of-file instead of hanging.
- Exit code 1 from `grep`, `findstr`, and `git grep` means no match, and
  `robocopy` codes 0 to 7 are success; the tool does not report these as
  failures.
- Observed: a cmdlet that writes an error record exits 1 even with
  `-ErrorAction SilentlyContinue`. `Get-Process` for a program that is not
  running and `Get-WinEvent` with no matching events both looked like
  failures with empty output. Make the outcome explicit:

  ```powershell
  $events = try {
      Get-WinEvent -FilterHashtable $filter -ErrorAction Stop
  } catch { @() }
  "matching events: $($events.Count)"
  ```

- PowerShell `-match` ignores case; use `-cmatch` when case matters, and
  exclude your own log lines from error counts. The [PowerShell][pwsh]
  companion covers text matching and exit status in full.

## Scripts Instead of Inline Text

Inline commands cross the harness, the shell, and often a second
interpreter. Observed failures:

- Long Bash here-documents containing Python triple-quoted strings failed
  nine times across six agents with "unexpected EOF while looking for
  matching `''", even with a quoted delimiter such as `<<'PYEOF'`. The
  script file was never created.
- Backslashes collapsed: `'\\'` arrived as `'\'`, giving a Python
  `SyntaxError`, and a `\n` inside a string literal became a real newline
  in edited C# source.

Write the script with the Write tool, which stores exactly the characters
given as UTF-8, into the project's ignored `.local/` area, then run it with
an explicit interpreter. Inside Python, `chr(92)` sidesteps a backslash
that must survive another layer. Before a scripted replacement, assert
that each search string occurs exactly once, and write nothing if any
assertion fails.

## Encodings

- Python's standard output in Git Bash uses the ANSI code page when piped.
  Observed: non-ASCII text printed as replacement characters or raised
  `UnicodeEncodeError: 'charmap' codec can't encode character`. Set
  `PYTHONIOENCODING=utf-8` or `PYTHONUTF8=1` per command, and judge a file
  by its bytes, not by how the console renders it; see the
  [Python][python] companion.
- Edit refuses a file that is not valid UTF-8 unless it begins with a
  UTF-16LE byte-order mark, and NotebookEdit refuses any non-UTF-8
  notebook. Write can replace such a file but saves UTF-8, losing the
  original encoding. Change legacy-encoded
  files with a byte-preserving script.
- Line endings are a repository property; see the
  [text files][text-files] companion before scripted edits in a
  repository that mixes CRLF and LF.

## Time Limits and Background Work

| Situation | Default | Notes |
| --- | --- | --- |
| Foreground Bash or PowerShell | 2 minutes | Claude may request up to 10; `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` change both |
| Foreground timeout reached | Moves to background | Not stopped, unless the command starts with `sleep` |
| Background command, interactive local session | No limit | Runs until it exits or is stopped |
| Background command, unattended session | 30 minutes | Up to 2 hours with an explicit `timeout` |
| Monitor watch | 5 minutes | At most 30; requires Git Bash on Windows |

- A command moved to the background reports its task ID and output file.
  Read the file; do not rerun the command.
- A user message arriving mid-command also moves it to the background;
  observed text: "so that a message that arrived while it was running can
  reach you; it was not interrupted."
- Observed: an HTTPS `git fetch` waiting on an invisible credential prompt
  ran into the 2-minute limit. Make network commands fail fast as
  [Git for Agents][git-agents] describes.
- Stop with TaskStop by task ID. If the call fails with a missing
  parameter, the tool was deferred; load it through tool search and retry.
- A `cd` inside a command that moved to the background never carries over.

## Output Limits

| Result | What reaches Claude |
| --- | --- |
| Success, up to about 30,000 characters | Inline |
| Success, larger | A file path in the session's `tool-results` folder plus a 2,000-character preview |
| Failure | A head-and-tail excerpt of about 10,000 characters, with no file path |

Consequences:

- Search a saved result file with Grep or Read instead of rerunning the
  command.
- For verbose builds and test runs, redirect output to a log under
  `.local/` and search the log, because a failing command's middle is
  otherwise lost.
- Do not cut a script's output with `Select-Object -First N` or `head`
  when its verdict comes last. Capture the output, then show the tail.
- `BASH_MAX_OUTPUT_LENGTH` and the `bashOutputMaxChars` setting change
  these limits; the operator sets them.

## File Tools

- **Read before writing.** Edit and Write need a current read of an
  existing file, with relaxations that vary by model and version. After
  changing a file through a shell command, read it again before Edit;
  observed messages include "File has been modified since read" and "the
  edit applied cleanly, but the file contains other changes not in your
  context."
- **Images.** Read renders PNG and JPEG for the model, downscaling large
  images. To check many generated images or screenshots, tile them into
  one contact sheet and read that; crop a region when detail matters.
- **PDFs.** Page-range reads need `pdftoppm` on `PATH`. Observed: Git for
  Windows 2.55 ships `pdftotext` but not `pdftoppm`, so
  `pdftotext -layout file.pdf -` was the working fallback.
- **Large files.** One read returns at most about 25,000 tokens and
  refuses a whole file over 256 KB; page with `offset` and `limit`, or
  search first.
- **Searches.** Glob and Grep from the repository root also walk ignored
  folders. Observed: the first `**/*` search in a project with a
  redirected home returned a browser-profile file. Scope searches to
  source folders.

## Removal Guards

Claude Code refuses or escalates deletions it cannot verify:

- `rm` or `rmdir` aimed at a critical path, including the home directory,
  its 8.3 short name, drive roots, and the working directory, is never
  approved by an allow rule; depending on the mode it asks a human or is
  denied.
- `Remove-Item` on a bare `*` or a target ending in `\*`, and `cmd /c rd`
  or `del` aimed at system paths, are denied in every mode.
- In auto mode, `rm -rf "$DIR"` whose variable came only from earlier
  output is blocked. Write the literal path, or guard globs with
  `"${DIR:?}"`.

Before deleting near links, read [Links and copies][links].

## Questions to the Operator

Read AskUserQuestion results literally. Observed: a result marked as
rejected still carried three chosen answers plus a request to clarify, and
a free-text answer replaced every offered option. Act on what the
operator wrote, not on the option you recommended.

## Review Checklist

- Does every command use absolute paths and set its own environment?
- Was anything longer than a short ASCII one-liner written as a script
  file first?
- Is Python output encoding set when non-ASCII text crosses a pipe?
- Are slow commands backgrounded, and their output files read, not
  rerun?
- Is verbose output captured to a log that survives a failing exit?
- Was each file re-read after a shell edit and before Edit?
- Are deletions literal, scoped, and clear of links?

## Further Information

- Anthropic, [Tools reference][tools-ref]: Bash, PowerShell, Monitor,
  Read, Edit, and Write behavior
- Anthropic, [Choose a permission mode: critical paths](https://code.claude.com/docs/en/permission-modes#critical-paths)
- Anthropic, [Environment variables](https://code.claude.com/docs/en/env-vars)
- Python, [PYTHONIOENCODING](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONIOENCODING)
  and [Python UTF-8 Mode](https://docs.python.org/3/library/os.html#utf8-mode)
- Microsoft, [about_Comparison_Operators](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_comparison_operators)

[tools-ref]: https://code.claude.com/docs/en/tools-reference
[agent-shells]: ../../../../windows/shells/overview.knack.md
[git-bash]: ../../../../windows/shells/Git-Bash.knack.md
[pwsh]: ../../../../windows/shells/PowerShell.knack.md
[text-files]: ../../../../windows/shells/text-files.knack.md
[python]: ../../../../windows/shells/Python.knack.md
[git-agents]: ../../../../windows/git/overview.knack.md
[links]: ../../../../windows/processes-and-files/links-and-copies.knack.md
