# Launching Steam Games for Development and Tests

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion before a script or agent starts a Steam game or tool,
whether through the Steam client or by running its executable, and when a
result may depend on which build was installed. Read the
[Steam overview](overview.knack.md) first; its evidence labels
(documented, observed, inferred) apply here. Process ownership, waiting,
and stopping are covered in
[Processes](../../windows/processes-and-files/ownership.knack.md);
this companion covers what Steam adds.

## Launching Through Steam

The Valve Developer Community wiki lists the `steam://` URL commands; the
page itself warns that some no longer work and others are missing:

| Command | Effect |
| --- | --- |
| `steam://run/<appid>` | Runs the app, installing it if necessary |
| `steam://run/<appid>//<args>/` | The same, passing `<args>` as launch parameters |
| `steam://rungameid/<id>` | Like `run`, also for mods and non-Steam shortcuts |
| `steam://launch/<appid>/dialog` | Uses the player's preferred launch option, or asks |
| `steam://validate/<appid>` | Validates the app's installed files |
| `steam.exe -applaunch <appid> [args]` | Command-line form of a launch |

Every `steam://` command starts the Steam client if it is not running
(documented). Consequences for automation:

- **No process handle.** The URL goes to the client, and the client
  starts the game. Your launcher must find the game process afterwards,
  and cannot tell it from a player's launch made at the same moment.
- **Not a second instance.** Steamworks documents that a `steam://run`
  URL with parameters, executed while the game is running, is delivered
  to the running game as a `NewUrlLaunchParameters_t` callback. Do not
  rely on a Steam launch to start an isolated test instance beside the
  player's game.
- **Arguments may need a person.** Steamworks exposes URL arguments
  through `ISteamApps::GetLaunchCommandLine` and calls that route
  preferable to an operating-system command line, "which can be a
  security risk". Players have reported, since 2024, a client prompt
  asking them to confirm a launch with custom options (community reports,
  not Valve documentation). Do not build unattended runs on it.
- **Updates come first.** When the client launches a game, it first
  installs updated depots and updates installed Workshop items
  (documented). A Steam launch can therefore change the build you are
  about to test.

## Launching Directly

A direct launch runs the executable from the install folder. Steamworks
looks for `steam_appid.txt` in the **current working directory**
(documented), so set the working directory to the install folder, not to
your repository:

```powershell
$game = Get-SteamApp -AppId 9876540     # see the install-layout companion
if (-not $game -or $game.StateFlags -ne 4) { throw 'Example Colony is not ready.' }
$run = Join-Path $repo ".local\tmp\colony-$(Get-Date -Format yyyyMMdd-HHmmss)"
New-Item -ItemType Directory -Path $run | Out-Null
$exe = Join-Path $game.InstallDir 'ExampleColony.exe'
$p = Start-Process -FilePath $exe -WorkingDirectory $game.InstallDir -PassThru `
    -ArgumentList @("-datafolder=`"$run\data`"", '-logfile', "`"$run\game.log`"")
[pscustomobject]@{
    Id = $p.Id; StartTime = $p.StartTime.ToString('o')
    BuildId = $game.BuildId; Run = $run
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $run 'launch.json')
```

`-datafolder` and `-logfile` stand for whatever options the game really
offers. The run folder in the command line is the marker that identifies
this instance later. `Start-Process` joins the argument list without
quoting, so paths carry their own quotation marks. In Windows PowerShell
5.1 and PowerShell 7, this pattern delivered intact arguments to a test
program whose working directory and run folder both contained spaces and
parentheses. Each game parses its own command line, so confirm what it
received from its log or from Steam's `gameprocess_log.txt`, which
records the full command line.

## `steam_appid.txt` and the Restart Check

Steamworks offers `SteamAPI_RestartAppIfNecessary(appid)`. It "checks if
your executable was launched through Steam and relaunches it through
Steam if it wasn't"; when it returns true it starts the client if
required and relaunches the game, and the game should quit at once. If
`steam_appid.txt` is present, it returns false regardless, which
"allows you to develop and test without launching your game through the
Steam client" (all documented). Valve tells developers not to ship the
file.

- **A third-party game.** Some shipped games include `steam_appid.txt`
  anyway (observed); a direct launch from their folder then runs in
  place. A game without it that calls the check will exit and relaunch
  through Steam: your process ends within moments, and the new one
  carries Steam's launch options instead of your arguments (inferred
  from the documented behavior). Detect this by watching for a quick
  exit and a new process without your marker. Do not add the file to a
  game the player owns without their agreement; it changes their
  installation.
- **Your own Steamworks title.** Keep `steam_appid.txt` beside the
  development executable and out of every depot you upload, as Valve
  instructs.
- **A DRM-wrapped executable.** Valve's DRM documentation does not say
  how a wrapped executable behaves when started directly. Test it.

## Attaching to the Player's Client

`SteamAPI_Init` needs a running Steam client under the same operating
system user, and fails when the client is not running, the app ID cannot
be determined, or the user lacks a license (documented). When it
succeeds, a direct launch joins the player's session:

- the client logged the launched process as a tracked process of the app,
  under the same ID that `Start-Process` returned (observed);
- the overlay loads when the game calls `SteamAPI_Init` (documented for
  games run outside the client, for example in a debugger), and the
  overlay log recorded the injection (observed);
- the app manifest's `LastPlayed` moved and the content log showed the
  app as running (observed);
- Steam Cloud synchronized at exit (see
  [Coexisting with the player](sharing-with-player.knack.md));
  and
- presence, achievements, statistics, and leaderboards act as the
  signed-in player (inferred from the shared client; not tested). Keep
  test paths away from anything that unlocks, uploads, or posts.

**With Steam closed**, initialization fails (documented), and what a
given game does next is its own choice: quit, start the client through
the restart check, or run without Steam features such as Workshop
content. This was not tested for this knack. Test it explicitly and
record the result before relying on it, and do not start or stop the
player's client to find out without asking them.

## Launch Options

A Steam launch applies two sets of arguments that a direct launch does
not:

1. **The developer's launch options.** Steamworks apps define at least
   one launch option, "the path and optionally, any arguments required
   to launch the game" (documented), and can define different ones per
   operating system.
2. **The player's launch options**, typed into the game's Properties in
   the client.

Comparing `gameprocess_log.txt` entries showed a Steam launch carrying a
developer-defined argument that every direct launch lacked (observed).
Before trusting a direct launch, read a Steam launch's command line from
that log, pass any argument the game needs yourself, and decide whether
the player's options matter to your test. Never edit the player's launch
options to suit a test.

## Games That Restart Themselves

Some games restart in place, for example after a mod-list or language
change. The process log showed a new process for the same app, with the
same arguments re-quoted and without the helper processes Steam had
started alongside the first, about two minutes after a launch (observed;
the trigger was inferred). A launcher waiting on the first process would
see it exit while the game carries on (inferred). Seed the configuration
a restart would apply before launching, and find instances by marker
rather than trusting the first ID alone.

## Updates and Version Drift

- **Documented.** Players must download each game update before they
  can launch again. `ISteamApps::GetAppBuildId` "may change at any time
  based on backend updates to the game". Choosing a branch on the game's
  Game Versions & Betas tab starts a download that replaces the
  installed build.
- **Observed.** While any tracked instance ran, the client marked the app
  running and logged no update activity for it. Within a second of the
  last instance exiting, its scheduler logged an automatic update
  "not played for 1 seconds" and downloaded and committed queued Workshop
  updates. The manifest's `AutoUpdateBehavior` and
  `AllowOtherDownloadsWhileRunning` keys appear to hold the player's
  update preferences; their values are undocumented.
- **Inferred.** A direct launch while an update is queued runs the old
  build, and a session of back-to-back runs can straddle an update.

Practice:

1. Read `buildid` and `StateFlags` at the start and end of every session,
   and store the build ID with each result, decompiled reference, and
   validation baseline, as
   [Closed-Assembly Inspection](../../dotnet/assembly-inspection/overview.knack.md)
   asks for host versions.
2. When the build ID changes, rerun the baselines before comparing
   results across the change.
3. Do not change the player's update settings or branch to stabilize a
   test. Ask, or accept the drift and record it.
4. When a beta branch is announced, treat a trial on it as planned work,
   not a side effect of the player's choice.

## Reading the Process Log

`<root>\logs\gameprocess_log.txt` answers "what did Steam see": each
tracked process ID, its full command line, and its exit code. Use it to
confirm quoting, to spot launches you did not make, and to compare Steam
launches with direct ones. Do not use it for timing: overlapping
instances' exits were logged together (observed). It contains user paths;
redact before quoting.

## Review Checklist

- Does the launcher start the executable directly, with the install
  folder as working directory, when the test needs a process it owns?
- Is every argument the game needs passed explicitly?
- Does the launcher detect an immediate exit followed by a relaunch?
- Is the build ID recorded at launch and checked again at the end?
- Is anything in the test able to unlock achievements, post scores, or
  change presence on the player's account?
- Was behavior with Steam closed tested, rather than assumed?

## Further Information

- Valve, [Steamworks API Overview: Initialization and Shutdown](https://partner.steamgames.com/doc/sdk/api#initialization_and_shutdown)
- Valve, [SteamAPI_RestartAppIfNecessary](https://partner.steamgames.com/doc/api/steam_api#SteamAPI_RestartAppIfNecessary)
  and [SteamAPI_Init](https://partner.steamgames.com/doc/api/steam_api#SteamAPI_Init)
- Valve, [ISteamApps](https://partner.steamgames.com/doc/api/isteamapps):
  `GetAppBuildId`, `GetLaunchCommandLine`, `NewUrlLaunchParameters_t`
- Valve, [Uploading to Steam](https://partner.steamgames.com/doc/sdk/uploading):
  launch options
- Valve, [Branches (Betas)](https://partner.steamgames.com/doc/store/application/branches)
- Valve, [Updating Your Game: Best Practices](https://partner.steamgames.com/doc/store/updates)
- Valve, [Steam Workshop Implementation Guide: Item Installation](https://partner.steamgames.com/doc/features/workshop/implementation)
- Valve, [Steam Overlay](https://partner.steamgames.com/doc/features/overlay)
- Valve, [Steam DRM](https://partner.steamgames.com/doc/features/drm)
- Valve Developer Community,
  [Steam browser protocol](https://developer.valvesoftware.com/wiki/Steam_browser_protocol)
  and [Command line options (Steam)](https://developer.valvesoftware.com/wiki/Command_line_options_(Steam))
- Steam Community discussion,
  [launch-option warning reports](https://steamcommunity.com/discussions/forum/1/4362372817693649390)
  (player reports, not Valve documentation)
