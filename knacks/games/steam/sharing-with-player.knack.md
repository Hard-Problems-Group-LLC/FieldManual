# Coexisting With the Player

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion before running a Steam game for tests, captures, or
demonstrations on a machine whose owner also plays it, especially while
they might be playing. Read the [Steam overview](overview.knack.md)
first; its evidence labels (documented, observed, inferred) apply here.
General rules for shared workstations live in
[Processes and Files](../../windows/processes-and-files/overview.knack.md)
and
[Desktop Automation](../../windows/desktop-automation/overview.knack.md);
this companion adds what Steam and games change.

## What the Player Owns

- their running game, its window, and any unsaved progress in it;
- saves, settings, enabled-mod lists, and logs, wherever the game keeps
  them: the install folder, `%USERPROFILE%\Documents`, `%APPDATA%`,
  `%LOCALAPPDATA%`, or `%USERPROFILE%\AppData\LocalLow\<company>\<product>`
  for many Unity games;
- cloud copies of those saves on Valve's servers and their other
  machines;
- launch options, update settings, beta branch, and overlay settings in
  the client; and
- their play status, play time, achievements, and statistics.

A test may read these when the task needs it. It changes them only with
the player's explicit agreement, after a backup.

## Before Every Launch

Find every running process whose image lies in the game's install folder,
and mark the ones that carry your run marker. Helper processes, such as a
crash handler, also live there. A process whose path you cannot read is
not yours. Tested in Windows PowerShell 5.1 and PowerShell 7:

```powershell
function Get-GameInstance {
    param(
        [Parameter(Mandatory)][string] $InstallDir,
        [Parameter(Mandatory)][string] $ImageName,
        [string] $Marker
    )
    $prefix = $InstallDir.TrimEnd('\') + '\'
    Get-CimInstance Win32_Process | Where-Object {
        if ($_.ExecutablePath) {
            $_.ExecutablePath.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)
        } else {
            $_.Name -eq $ImageName            # unreadable path: count it
        }
    } | ForEach-Object {
        [pscustomobject]@{
            ProcessId = $_.ProcessId
            Created   = $_.CreationDate
            Mine      = [bool]($Marker -and $_.CommandLine -and
                $_.CommandLine.IndexOf($Marker, [StringComparison]::OrdinalIgnoreCase) -ge 0)
            Image     = if ($_.ExecutablePath) { $_.ExecutablePath } else { $_.Name }
        }
    }
}
```

Then:

- if an instance that is not yours is running, the player is probably
  playing or has the game open. Do not launch something that competes
  with them for the screen, sound, or input; ask, or wait;
- if a run of yours from earlier is still alive, account for it before
  starting another; a background run left over is a common surprise;
- announce any window you are about to open while a person is at the
  machine; and
- after each launch, count your instances by marker and confirm the
  expected number.

Never stop a process you cannot prove is yours, and never stop the
game by image name: `Stop-Process -Name` and `taskkill /IM` end the
player's game too.

## Isolate Every Run

Give each run its own data, configuration, and log location, using the
game's own option for it, and create that folder fresh under the
project's ignored `.local\tmp\`, as FieldManual's
[local operator state](../../../standards-and-practices/core/local-operator-state.md)
standard describes. Folders left in `%TEMP%` by earlier runs accumulated,
some holding autosaves of several megabytes each (observed).

- **Verify the override.** Read the folder the game reports in its log,
  or check that files appeared where you pointed it, before trusting the
  run. Games commonly ignore an option they do not recognize, so a
  misspelled one can send the run's writes to the player's folders.
- **Write the run's configuration**, such as its mod list and
  preferences, into the run folder; never edit the player's to get a
  test going.
- **Give logs their own path.** Unity players accept `-logFile <path>`
  (documented). For one Unity game, a launch from the client rotated the
  default `Player.log` to `Player-prev.log`, while runs started with
  `-logFile` wrote only their own file and left the player's logs
  untouched (observed). Do not read the player's logs as test evidence,
  or let tests overwrite them.
- **Clean up** only the folders the run created, keeping a failed run's
  folder while it is needed for diagnosis.

When a game has no data-folder option, stop and ask. Alternatives each
have costs: backing up and restoring the player's folders with their
consent risks a cloud upload at the wrong moment; running a Steamworks
game under another Windows account fails against the player's client,
because Steamworks requires the client under the same operating-system
user (documented); and a
[virtual machine](../../virtualization/virtual-machine-control.knack.md)
needs its own client and a licence for the game.

## Steam Cloud

Steam Auto-Cloud synchronizes the folders and file patterns the game's
developer configured, such as a subfolder of `AppData\LocalLow`, "when
the application launches and exits" (documented). On the observed
client, each of 39 consecutive exits of directly launched test instances
was followed within the same second by a cloud pass over the player's
default save folder (observed). Runs whose data went to their own folder
added nothing to it.

- Anything a test writes into the player's default save folder can
  reach Valve's servers and the player's other machines at the next
  exit. Never write test data there.
- Never delete or rename files in that folder; a deletion can propagate
  as well (inferred).
- Steam placed a small marker file, `steam_autocloud.vdf`, holding the
  account ID, in the synchronized folder (observed). Keep it out of test
  fixtures and published output.

## Multiple Instances

The client tracked several direct-launched instances of one app at once,
each with its own data folder (observed). Whether a game allows a second
instance is the game's choice: some refuse, some hand off to the first.
Never close the player's instance to make room. Resources shared by all
instances include:

- the install folder and its local mods folder, so a changed mods-folder
  link affects the player's next start;
- network ports and other single-instance locks the game takes; and
- Steam's view of the app: while any instance runs, the app counts as
  running, which holds its updates (see
  [Launching](launching.knack.md)).

## Overlay and Notifications

The overlay hooks into games launched from Steam and, for games run
outside it, loads when the game calls `SteamAPI_Init` (documented); the
overlay log showed it injected into direct launches (observed). Its
default key is Shift+Tab (documented), so automation must not send that
chord to the game window.

The overlay shows notification pop-ups in a corner of the game window;
Steamworks lets a game choose the corner (documented, as
`ISteamUtils::SetOverlayNotificationPosition`). Such pop-ups, for example
for messages from friends, can appear in screen captures (inferred).
Capture the game's window rather than the screen, check every capture
before use, and never change the player's overlay or notification
settings to tidy a capture. Windows itself adds notifications on game
launches; see
[background events](../../windows/event-logs/background-noise.knack.md).

## Play Sessions and the Player's Account

A direct launch that initializes Steamworks is a play session on the
player's account (see
[Launching](launching.knack.md)): it moves `LastPlayed`
(observed), adds play time and may show the player as in game to friends
(inferred), and anything the game does through Steamworks, such as
unlocking achievements or posting leaderboard scores, acts for the player
(inferred). Tell the player that test runs will appear as their play
sessions, and keep test paths away from irreversible account changes.

## Sharing the Session

- Agree with the player which instances are yours and which window you
  will open next.
- Warn them before changing what their game loads, such as switching
  the branch behind a mods-folder link.
- A showcase or kept-open instance defers their updates; close it when
  the demonstration ends, unless they asked otherwise.
- Leave the desktop as you found it.

## Review Checklist

- Was the player's instance looked for before launching, by path and
  marker rather than by name?
- Does every run use a fresh data and log location that the game was
  proven to use?
- Could any test write to, or delete from, a cloud-synchronized folder?
- Are captures taken by window, and checked for notifications and
  personal data?
- Could the test unlock, post, or change anything on the player's
  account?
- Does the player know which instances and windows are yours?

## Further Information

- Valve, [Steam Cloud: Steam Auto-Cloud](https://partner.steamgames.com/doc/features/cloud#steam_auto-cloud)
- Valve, [Steam Overlay](https://partner.steamgames.com/doc/features/overlay)
- Valve, [ISteamUtils::SetOverlayNotificationPosition](https://partner.steamgames.com/doc/api/ISteamUtils#SetOverlayNotificationPosition)
- Valve, [SteamAPI_Init](https://partner.steamgames.com/doc/api/steam_api#SteamAPI_Init)
- Unity, [Log files](https://docs.unity3d.com/Manual/log-files.html) and
  [Player command-line arguments](https://docs.unity3d.com/Manual/PlayerCommandLineArguments.html)
- Microsoft, [Win32_Process class](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-process)
- FieldManual,
  [in-host smoke testing: the launcher](../../software-engineering/testing/in-host-smoke/launcher.knack.md)
