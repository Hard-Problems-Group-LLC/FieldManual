# Steam: Working Beside the Player

Reviewed: 2026-10-13

## When to Load This Knack

Load this knack before building, testing, decompiling against, automating,
or modding a game or tool installed through Steam on a Windows
workstation, especially one whose owner also plays on it. It also applies
when you run your own Steamworks title outside the Steam client during
development. Companions:

- [Install layout](install-layout.knack.md): finding the Steam
  root, libraries, app manifests, build IDs, Workshop folders, and client
  logs, and reading the KeyValues (VDF) text format;
- [Launching](launching.knack.md): `steam://` URLs versus direct
  launches, `steam_appid.txt`, launch options, play sessions, and updates;
- [Coexisting with the player](sharing-with-player.knack.md):
  the player's instance, isolated data folders, Steam Cloud, and the
  overlay; and
- [Mods and Workshop](workshop.knack.md): local mods,
  Workshop subscriptions, development links, and clean uploads.

Examples use a fictional game, *Example Colony*, installed in
`steamapps\common\Example Colony` with executable `ExampleColony.exe` and
placeholder app ID `9876540`. The ID did not belong to any store app on
the review date; substitute the real one.

### Evidence Labels

Valve documents Steamworks for game developers, not the client's files,
registry values, or logs. This fileset therefore marks claims:

- **documented**: stated in the linked Steamworks or Steam Support
  documentation, or on the Valve Developer Community wiki;
- **observed**: seen on a Windows 11 workstation with the Steam client
  current in October 2026; undocumented, and liable to change; and
- **inferred**: reasoned from the above, not tested.

## Mental Model: Three Owners

A Steam installation holds objects with three different owners.

1. **The Steam client** owns the install and library folders, app and
   Workshop manifests, the Workshop content folder, update scheduling, and
   cloud synchronization. It rewrites these files on its own schedule.
   Read them; never edit them.
2. **The player** owns their running game, saves, settings, enabled mod
   list, launch options, cloud saves, play status and play time, and the
   Steam account itself.
3. **You** own your development folder, the links you created, your run
   folders, and the instances you launched, proved by process ID,
   creation time, and a command-line marker, as
   [Processes and Files](../../windows/processes-and-files/overview.knack.md)
   describes.

The boundary that surprises people: a test instance launched directly
from the game folder still attaches to the player's signed-in client when
the game initializes Steamworks. Steam then treats the run as the player
playing: it tracks the process, loads the overlay, records play time, and
synchronizes the player's cloud files when the run exits (documented in
part, observed in full; see the companions).

## Workflow

1. **Locate.** Resolve the game folder from the registry, the library
   list, and the app manifest, or from an environment variable the
   project declares. Never hard-code a library path.
2. **Pin the version.** Read `buildid` and `StateFlags` from the app
   manifest. Proceed only when `StateFlags` is exactly 4, meaning fully
   installed with nothing pending (observed), and record the build ID with
   every baseline: test results, decompiled references, validator data.
3. **Isolate.** Give each run its own data, configuration, and log
   location through the game's own option, and verify the game used it.
   If the game has no such option, stop and ask the player.
4. **Check for the player.** Find running instances by image path and
   command line. If the player is playing, do not compete with them;
   never close their instance.
5. **Install your work.** Link the game's local mods folder to a staged
   build output with a directory junction, after checking what is already
   at that path.
6. **Launch directly** with the install folder as working directory, a
   unique marker in the command line, and every argument the game needs.
   Record the process ID and creation time.
7. **Wait on evidence**, such as a log marker, the process exit, or a
   timeout, as
   [In-Host Smoke Testing](../../software-engineering/testing/in-host-smoke/overview.knack.md)
   describes.
8. **Stop only your instances**, then let the client finish its exit
   work: cloud synchronization and any held updates.
9. **Re-read the build ID** at the end of a session; if it changed,
   the session spans two versions.

## Two Launch Paths

| Aspect | Through Steam (`steam://run`, Play) | Direct (`ExampleColony.exe`) |
| --- | --- | --- |
| Process started by | The Steam client; you get no process ID | You; you hold its ID |
| Developer's and player's launch options | Applied | Not applied (observed) |
| Pending game and Workshop updates | Installed first (documented) | Not installed first (inferred) |
| Second, isolated instance | No route to one; a running Steamworks game is handed the URL's parameters (documented) | Yes, if the game permits it |
| Play session, overlay, cloud sync at exit | Yes | Yes, once the game initializes Steamworks (observed) |

Automated tests normally launch directly. Use a Steam launch when the test
is about the Steam launch itself, and then expect the player-facing
effects in the table.

## Sharp Edges

- **The game changes under you.** Automatic updates, a beta branch the
  player selects, and Workshop updates arrive between runs. A build ID
  recorded yesterday proves nothing about today.
- **Your runs hold the player's updates.** While any tracked instance
  runs, Steam marks the app as running; queued Workshop updates started
  within a second of the last instance exiting (observed). Back-to-back
  runs can straddle an update, and a showcase left open defers the
  player's updates.
- **Paths contain spaces and parentheses.** The default library is under
  `C:\Program Files (x86)\Steam`, and install folder names often contain
  spaces and punctuation. Quote every path through every shell layer.
- **The default install folder is writable by all local users**
  (observed: `BUILTIN\Users` has full control), so junctions need no
  elevation. It also means game files there are not tamper-proof; never
  treat them as a trusted input.
- **A junction serves whatever is checked out.** When the player's real
  game loads your mod from your working tree, a branch switch or a
  half-finished build reaches their next session.
- **A running game keeps the code it loaded.** Test a new build in a new
  process; an old instance keeps logging the old build's errors.
- **The process you launched may not be the one that runs.** Some games
  restart themselves, for example after a mod-list change; the new
  process carries the same arguments and a new ID (observed). Find
  instances by marker, not only by the first ID.
- **Steam closed is a different environment.** Steamworks initialization
  fails without a running client (documented). What a given game then
  does is game-specific; test it explicitly before relying on it.
- **Uploads include more than you think.** A Workshop upload takes a
  folder; no exclusion mechanism is documented. Stage a clean copy.
- **Steam's files identify the player.** Manifests, logs, and cloud
  markers hold account IDs, user names, and save names. Redact them
  before quoting any of it in a repository, issue, or knack.

## Review Checklist

- Is the game located without hard-coded library paths?
- Is the build ID recorded with every result and baseline, and
  `StateFlags` checked before the session?
- Does every run use its own data, configuration, and log location, and
  is that verified from the game's own output?
- Was the player's instance checked for, and left alone?
- Does every stop command name a recorded process ID and creation time?
- Are arguments the game needs passed explicitly, given that a direct
  launch skips Steam's launch options?
- Does the mods-folder link point at a staged output, checked before
  creation?
- Would a Workshop upload include only the files intended?
- Is any Steam-derived text free of account IDs, user names, and paths?

## Further Information

- Valve, [Steamworks API Overview: Initialization and Shutdown](https://partner.steamgames.com/doc/sdk/api#initialization_and_shutdown)
- Valve, [steam_api.h reference](https://partner.steamgames.com/doc/api/steam_api)
- Valve, [Steam Cloud](https://partner.steamgames.com/doc/features/cloud)
- Valve, [Steam Workshop Implementation Guide](https://partner.steamgames.com/doc/features/workshop/implementation)
- Valve, [Steam Overlay](https://partner.steamgames.com/doc/features/overlay)
- Valve, [Uploading to Steam](https://partner.steamgames.com/doc/sdk/uploading),
  which covers launch options
- Valve Developer Community,
  [Steam browser protocol](https://developer.valvesoftware.com/wiki/Steam_browser_protocol)
  and [KeyValues](https://developer.valvesoftware.com/wiki/KeyValues)
- FieldManual,
  [local operator state](../../../standards-and-practices/core/local-operator-state.md)
