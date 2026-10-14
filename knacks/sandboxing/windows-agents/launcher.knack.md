# Project-Local Agent Launchers on Windows

Reviewed: 2026-10-13, against the claude-wrangler specifications at
revision `14dbc3c`, the Claude Code settings and setup documentation, and
the Microsoft Win32 references below. The agent-specific details name
Claude Code; the techniques apply to any coding-agent CLI.

## When to Load This Knack

Load this companion when building, reviewing, or debugging a launcher that
starts a coding agent with project-local state on native Windows. Start
with the [overview](overview.knack.md), which
explains what such a launcher can and cannot isolate. HPG's
[claude-wrangler][cw] is one implementation of these techniques for Claude
Code; its specifications record the reasoning in more depth.

## Shape of a Launcher

- Put all launch logic in one core program, for example a
  standard-library Python script generated into the project, so a project
  keeps launching if the installing tool is later removed.
- Give each shell a thin entry point: a POSIX `sh` script for Git Bash and
  a `.cmd` file for cmd.exe and PowerShell. PowerShell resolves
  `.\bin\agent` to `agent.cmd`. Never also generate `agent.ps1`: PowerShell
  prefers it, and under the Restricted execution policy it then fails
  instead of falling back.
- Write the `.cmd` file with CRLF line endings and ASCII only.
- From Git Bash, hand the core Windows-form paths (`cygpath -w`) and set
  `MSYS_NO_PATHCONV=1` and `MSYS2_ARG_CONV_EXCL='*'` for the launch.
  Otherwise Git Bash rewrites a prompt such as `/review` into
  `C:/Program Files/Git/review`. Remove those variables from the agent's
  environment unless the caller set them.

## Build the Environment in Order

1. **Canonicalize the project path.** Claude Code keys its per-project
   folder and project entries on exact path strings, and a launcher's
   specification adds its secure-storage name. So `c:\work\example-app`,
   `C:\work\example-app`, and an 8.3 short spelling each fork state, with
   a new folder-trust prompt and missing history.
   Upper-case the drive letter and expand short names with
   `GetLongPathNameW`. Do not resolve links, and leave `subst`, mapped,
   and UNC spellings as the caller gave them.
2. **Pin the agent's state.** Export `CLAUDE_CONFIG_DIR` (or `CODEX_HOME`)
   to a folder under the project's ignored `.local/` area at every
   isolation level, including the escape hatch.
3. **Redirect every home variable together**: `HOME`, `USERPROFILE`,
   `HOMEDRIVE` and `HOMEPATH`, `APPDATA`, `LOCALAPPDATA`, and the four
   `XDG_*` folders. At the escape-hatch level, set none of them; never set
   `HOME` alone.
4. **Scrub inherited credentials.** Remove provider keys and tokens (for
   Claude Code, every `ANTHROPIC_*` and `CLAUDE_CODE_OAUTH_*` name, matched
   case-insensitively, and the host-authentication variables). Otherwise
   one key in the operator's shell signs every project into one account.
   Remove a provider switch together with its parameters; observed:
   removing `ANTHROPIC_*` but keeping a gateway switch failed with
   "ANTHROPIC_BASE_URL is missing". Print the names removed, never the
   values, and offer an explicit per-project passthrough. Cloud SDK
   credential chains and settings-file credential helpers cannot be
   scrubbed this way.
5. **Drop a parent session's identity.** A session started from inside
   another agent session inherits its session ID, messaging endpoint, and
   token (for Claude Code, `CLAUDECODE`, `CLAUDE_CODE_SESSION_ID`,
   `CLAUDE_CODE_CHILD_SESSION`, `CLAUDE_PID`, and
   `CLAUDE_CODE_MESSAGING_*`, among others) and behaves as its child.
   Remove them, except for a nested launch of the same project.
6. **Suppress self-update in layers.** The updater writes where `HOME`
   points, not beside the running binary. A launcher's bug record, based
   on reading the code of Claude Code 2.1.296, found that an npm-layout
   install run with the real home would run `npm install -g` and, on
   Windows, first remove the global `claude.exe`. Use all three layers,
   because a cloned repository's `.claude/settings.json` can blank the
   variables before its trust prompt:
   - the environment: `DISABLE_UPDATES=1`, `DISABLE_AUTOUPDATER=1`, and
     `DISABLE_INSTALLATION_CHECKS=1`;
   - `--settings` with an `env` block repeating them, since command-line
     settings outrank project settings; and
   - the same keys in the pinned folder's `settings.json`, for detached
     processes that bypass the launcher.

   Refuse `update`, `upgrade`, and `install` anywhere before the first
   other subcommand, because Claude Code dispatches a subcommand that
   follows leading options. The resulting "Updates are disabled by your
   administrator" message comes from `DISABLE_UPDATES`, not from IT
   policy. Observed in 2.1.296: some subcommands placed after a leading
   `--settings` silently ran the root command instead, so probe each
   subcommand before adding the flag.
7. **Warn once per session** that commands run unsandboxed on native
   Windows and that per-user stores remain shared.

## Run the Pinned Binary

- Start the project's pinned executable by absolute path, never through
  `npx`, a `PATH` lookup, or a global install. Recorded for Codex: with
  the local binary missing, `npx codex` fell through to an unrelated
  registry package named `codex`.
- Keep any managed runtime out of every `*\claude\versions` folder
  reachable from a home: Claude Code's housekeeping prunes old versions
  there whatever the update settings say.
- Keep runtimes out of folders a cloud-sync client uploads; one Claude
  Code release is about 250 MB. Allow up to a minute for a new binary's
  first start while antivirus software scans it.
- A version query can skip startup work. Recorded: `codex --version`
  succeeded while startup itself failed for want of an existing
  `CODEX_HOME`. Smoke-test with an offline startup command, such as a
  login-status query, in an empty scratch home.

## Nested Calls

Hooks, scripts, and background respawns call `claude` again. On Windows
they easily reach the wrong program:

- `CreateProcess`, libuv-based runtimes, and Python argument-list calls
  look only for `.exe` files. They skip a `claude.cmd` shim and run the
  next `claude.exe` on `PATH`, usually the global install. Put the pinned
  executable's folder first on `PATH`, but only while that folder holds
  nothing else, so it cannot shadow other tools.
- cmd.exe re-parses the arguments of every batch file: quotation marks,
  `%`, `^`, `&`, and line breaks. Text from a prompt or a JSON argument
  passed through a `.cmd` file can expand variables, be truncated, or run
  a second command (the BatBadBut class). No batch shim can forward
  arbitrary arguments; programs must call the core with an argument list.
- cmd.exe reads a running batch file by byte offset, so rewriting a shim
  during a session can make it resume mid-file. End the launch line with
  `& call exit /b %%ERRORLEVEL%%` so nothing after it is ever read.

General batch-shim, `PATH`, and PowerShell entry-point rules are in
[Porting CLI Tools: Launchers][porting-launchers].

## Own the Agent's Process

Windows has no `exec`; the launcher must wait for the agent as a child. If
the launcher is killed (a tool timeout, an SDK cancellation, or an editor
that stops only its direct child), the agent would keep running unattended.

- Put the child into a job object with
  `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, and hold the only, non-inheritable
  handle. Add `JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK` so processes the
  agent starts deliberately, such as background sessions, are not killed
  with it.
- Ignore Ctrl+C in the launcher while waiting, and exit with the child's
  code, mapping `0xC000013A` to 130.
- Killing the cmd.exe that runs a `.cmd` shim still leaves the launcher
  running; programmatic callers should kill the process tree or call the
  core directly.

Tested Python code for the job object is in
[Porting CLI Tools: Processes][porting-processes].

## Protect the State Folders

- The pinned configuration folder and the redirected home hold
  transcripts and credentials. A checkout created under a drive root
  inherits Modify for every authenticated user. Give both folders a
  protected DACL granting only the operator, SYSTEM, and Administrators,
  using `SetNamedSecurityInfoW` with a protected DACL, and warn when
  Everyone, Authenticated Users, or Users can write the checkout itself.
- Ignore the whole state tree in Git, and refuse to operate when Git
  tracks files inside it.
- A session can rewrite the launcher or runtime that the next unsandboxed
  launch will trust. On native Windows no sandbox rule prevents it, so
  verify the binary against a recorded size, time, and signature-checked
  manifest before running it.

## Installers and Tests Inside an Isolated Session

- An installer started from an isolated session sees the fake home and
  installs there. Find the real profile from the logon token with
  `OpenProcessToken` and `GetUserProfileDirectoryW`, and refuse a
  user-scoped install into an isolated home unless told explicitly.
  Recognize sibling tools' isolated homes too.
- Refuse an empty `USERPROFILE`; Python's `Path.home()` then returns the
  current directory.
- Test suites for such tools must redirect every home variable, not just
  `HOME`, through an automatic fixture, strip session markers, and offer
  an explicit opt-out marker for tests that need the real home.
- Smoke-test a downloaded agent binary in a scratch environment that
  replaces every home and temporary variable, the configuration variable,
  and `XDG_*`, drops agent variables, removes `PATH` entries under the
  real home, and sets the update-suppression variables.

## Escape Hatch and Records

- Offer a per-invocation flag or variable that runs with the operator's
  real home, keeping the configuration folder pinned. Never make it
  persistent by accident.
- Record in the project's agent instructions which task classes need
  which level, as "task class: requires level N because reason (date)",
  so later sessions do not rediscover the limits.

## Retiring a Launcher

1. Run the uninstaller's dry run first, and expect it to edit
   `.gitignore`; restore that file if the repository must match its
   remote.
2. Sign out (`/logout`) before deleting state, then check Credential
   Manager for an entry tied to the project path:
   `cmdkey /list | Select-String -SimpleMatch claude`.
3. Remove the agent's leftover temporary tree, such as
   `%TEMP%\claude\<project>`.
4. Close browsers started from the redirected home first; their locked
   files otherwise block deletion until a reboot.

## Review Checklist

- Is the project path canonicalized before any variable is exported?
- Is the configuration folder pinned at every level?
- Are all home variables set together, or none?
- Are inherited credentials and parent-session variables removed, with
  names reported and values never printed?
- Is self-update suppressed in the environment, on the command line, and
  in the pinned settings file?
- Do nested calls reach the pinned executable without passing through
  cmd.exe?
- Does killing the launcher end the agent?
- Are the state folders private, ignored, and untracked?

## Further Information

- HPG, [claude-wrangler][cw]; at the reviewed revision, its
  [security ring model][cw-rings],
  [session-state isolation][cw-state], and
  [cross-platform launcher][cw-launcher] specifications
- Anthropic, [Settings files and precedence](https://code.claude.com/docs/en/settings)
- Anthropic, [Advanced setup: disable auto-updates](https://code.claude.com/docs/en/setup#disable-auto-updates)
- Microsoft, [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
  and [JOBOBJECT_BASIC_LIMIT_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)
- Microsoft, [GetLongPathNameW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getlongpathnamew)
- Microsoft, [SetNamedSecurityInfoW](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-setnamedsecurityinfow)
- Microsoft, [GetUserProfileDirectoryW](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-getuserprofiledirectoryw)
- Flatt Security, [BatBadBut: You can't securely execute commands on Windows](https://flatt.tech/research/posts/batbadbut-you-cant-securely-execute-commands-on-windows/)

[porting-launchers]: ../../windows/porting-cli-tools/launchers.knack.md
[porting-processes]: ../../windows/porting-cli-tools/processes.Python.knack.md
[cw]: https://github.com/Hard-Problems-Group-LLC/claude-wrangler
[cw-rings]: https://github.com/Hard-Problems-Group-LLC/claude-wrangler/blob/14dbc3c5d964743c4fd5bb3e58095618dc50e994/docs/specifications/security_ring_model.md
[cw-state]: https://github.com/Hard-Problems-Group-LLC/claude-wrangler/blob/14dbc3c5d964743c4fd5bb3e58095618dc50e994/docs/specifications/session_state_isolation_and_config_dir_pinning.md
[cw-launcher]: https://github.com/Hard-Problems-Group-LLC/claude-wrangler/blob/14dbc3c5d964743c4fd5bb3e58095618dc50e994/docs/specifications/cross_platform_launcher.md
