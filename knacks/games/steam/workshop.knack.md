# Mods and the Steam Workshop

Reviewed: 2026-10-13

## When to Load This Knack

Load this companion when developing a mod for a Steam game: making the
game load a development build, studying other mods, enabling a mod in the
player's real profile, or publishing to the Steam Workshop. Read the
[Steam overview](overview.knack.md) first; its evidence labels
(documented, observed, inferred) apply here. Link mechanics are in
[Links and Copies](../../windows/processes-and-files/links-and-copies.knack.md).

## Where Mods Come From

A game usually finds mods in two places and keeps a third thing apart:

1. **A local mods folder** that the game defines: inside the install
   folder, under `Documents`, or under an application-data folder. The
   game's documentation or its own log names it. Do not assume.
2. **Workshop subscriptions**, which Steam downloads into
   `<library>\steamapps\workshop\content\<appid>\<itemid>\` (observed); a
   Steamworks game asks for each folder with
   `ISteamUGC::GetItemInstallInfo` (documented).
3. **The enabled-mod list and load order**, a file or setting in the
   player's data, separate from what is present on disk.

When the same mod is both present locally and subscribed, the game's own
rules decide which copy loads, and a duplicate can produce errors or load
the wrong build. While developing a mod, do not subscribe to its
published item on the same profile unless you know how the game resolves
the pair.

## The Workshop Folder Is Steam's

The client downloads Workshop updates into
`steamapps\workshop\downloads\<appid>` and commits them into `content`
(observed), and Steamworks documents that unsubscribing "will result in
the item being removed after the game quits". Edits made inside an
item's folder can therefore vanish at the next update or unsubscribe.

- Never develop inside the Workshop folder.
- To study another author's mod, read it in place or copy it to an
  ignored scratch folder, and respect its licence; the
  [closed-assembly inspection](../../dotnet/assembly-inspection/overview.knack.md)
  knack covers licence checks before decompiling.
- Steam updates installed items when it launches the game (documented)
  and, on the observed client, as soon as the last instance exited. A
  mod you depend on can change between two runs; note item update times
  from `appworkshop_<appid>.acf` when a failure might be another mod's
  doing.

## Linking a Development Build

Make the game see your work by linking its local mods folder to your
build, rather than copying after every build. A directory junction needs
no elevation; on the observed client the default Steam folder granted
`BUILTIN\Users` full control, so even a mods folder under
`Program Files (x86)` accepted one without elevation (observed). If the
game's folder is protected, do not elevate silently; ask. The guard
below was tested in Windows PowerShell 5.1 and PowerShell 7 against an
absent path, its own link, a link elsewhere, and a real folder:

```powershell
$mods   = Join-Path $game.InstallDir 'Mods'
$link   = Join-Path $mods 'ExampleColonyTools'
$target = Join-Path $repo '.local\stage\ExampleColonyTools'   # staged output
$item   = Get-Item -LiteralPath $link -Force -ErrorAction SilentlyContinue
if (-not $item) {
    New-Item -ItemType Junction -Path $link -Target $target | Out-Null
} elseif (-not $item.LinkType -or ($item.Target -join '') -ne $target) {
    throw "$link exists and is not our link; move it aside first."
}
```

The comparison of `Target` with the intended path is exact; normalize
both if they may differ in case or trailing separators. Choose the link
target with care:

- **Link a staged layout, not the repository root.** A link to the root
  exposes `.git`, ignored local folders, build intermediates, and
  scratch data to the game, which may scan or load them, and to any
  uploader that publishes the folder.
- **The player's game loads the same link.** A link into a working tree
  serves whatever is checked out, including another branch or a
  half-finished build, the next time the player starts their game. Point
  the link at a staging folder that only completed builds update, or at
  a separate worktree, and warn the player before switching what it
  serves.
- **A running game keeps what it loaded.** Rebuilding behind a live
  instance changes nothing in it; test the new build in a new process.
- **Remove links before Steam moves, verifies, or uninstalls the game.**
  Whether those operations follow a junction into its target was not
  tested; treat it as possible. Remove the link object only, as the
  links companion shows.

## Uploading to the Workshop

Steamworks documents two upload routes, both of which take a whole
folder:

- `ISteamUGC::SetItemContent` "sets the folder that will be stored as the
  content for an item", given "the absolute path to a local folder"; a
  game's in-game uploader typically calls it; and
- SteamCMD's `workshop_build_item`, driven by a VDF file whose
  `contentfolder` names the folder and `previewfile` the preview image.

Neither documentation page describes a way to exclude files. A game's
own uploader may filter some files out, or may publish its mod folder as
it stands. Verify what a given uploader includes, from its documentation
or by inspecting an upload's contents, before claiming it excludes
anything. Until then, assume it publishes everything in the folder,
including ignored local folders, logs with user paths, credentials
files, and whatever a link inside the folder reaches.

Development repositories often keep exactly that material in ignored
folders: decompiled references, logs containing user paths, and local
tool state, sometimes hundreds of megabytes of it. Uploading straight
from a development link would, on that assumption, publish all of it.
No such upload was attempted for this knack, so whether any particular
uploader filters it remains unverified (inferred risk). Stage a clean
copy instead:

1. build into an empty staging folder that holds only the files the game
   needs, listed explicitly rather than copied wholesale;
2. inspect the staged tree for secrets, personal paths, and oversized
   files;
3. upload from the staged folder; and
4. note the item ID the upload returns. Some games' uploaders write it
   back into the mod's folder; decide whether that file is tracked in
   version control.

Further Workshop rules (documented):

- items stay hidden until the contributor accepts the Steam Workshop
  Legal Agreement, and Valve asks games to show a terms notice beside
  the submit button;
- upload files as they are, not merged or compressed into archives,
  for efficient transfer; and
- where the game enables branch versions, an item can declare the game
  branches it supports, and players on a branch receive the newest item
  version compatible with it.

## The Player's Real Mod List

Enabling a mod in the player's own profile is a deliberate deployment,
not a side effect of testing:

- do it only when the player asks, while their game is closed;
- back up the list first, with a descriptive suffix, and preserve the
  file's encoding and line endings, as
  [Desktop Automation](../../windows/desktop-automation/overview.knack.md)
  describes for preference files;
- append only your mod's identifier, at the position the game's load
  order needs, and change nothing else;
- identify mods by their unique identifiers, never by display names,
  which can be similar across unrelated mods; and
- after renaming your mod's identifier, sweep every seeded test
  configuration and log-attribution pattern for the old one.

## Game Updates and Mods

A game update can break a mod overnight. Record the game's `buildid`
with every test result (see [Launching](launching.knack.md)),
rerun the mod's tests after the build ID changes, and check the item's
supported game versions before publishing an update.

## Review Checklist

- Is the game's local mods folder taken from the game, not assumed?
- Does the mods-folder link point at a staged build, checked before
  creation, and does the player know it serves your work?
- Is nothing developed or edited inside the Workshop content folder?
- Would an upload include only the staged files, verified rather than
  assumed?
- Is the player's real mod list touched only on request, with a backup
  and a one-line change?
- Are mods identified by unique identifier, not display name?

## Further Information

- Valve, [Steam Workshop](https://partner.steamgames.com/doc/features/workshop)
- Valve, [Steam Workshop Implementation Guide](https://partner.steamgames.com/doc/features/workshop/implementation),
  including item installation and SteamCMD uploads
- Valve, [ISteamUGC](https://partner.steamgames.com/doc/api/ISteamUGC):
  `SetItemContent`, `GetItemInstallInfo`, `UnsubscribeItem`
- Valve, [Steam Workshop Item Versioning](https://partner.steamgames.com/doc/features/workshop/itemversioning)
- FieldManual,
  [Links and Copies](../../windows/processes-and-files/links-and-copies.knack.md)
