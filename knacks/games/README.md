# Game Knacks

Reviewed: 2026-10-13

These knacks cover developing, testing, and automating against games and
game tools on a workstation that a person also plays on: finding installed
games, launching them for tests, keeping test runs away from the player's
saves and settings, and building mods. Store clients, engines, and games
change often; check each knack's review date and its cited documentation
before relying on version-specific details.

## Topics

- [Steam](steam/overview.knack.md) — working against games and
  tools installed through Steam on Windows, beside the player who owns the
  machine: the three owners of a Steam install, launch paths, version
  drift, and a review checklist
  - [Install layout](steam/install-layout.knack.md) —
    the Steam root, library folders, app manifests and build IDs, Workshop
    folders, client logs, and the KeyValues (VDF) text format, with tested
    lookup sketches
  - [Launching](steam/launching.knack.md) — `steam://`
    URLs versus direct launches, `steam_appid.txt` and the
    restart-through-Steam check, launch options, play sessions, and
    updates that arrive mid-project
  - [Coexisting with the player](steam/sharing-with-player.knack.md)
    — the player's instance, per-run data folders, Steam Cloud, multiple
    instances, the overlay, and notifications
  - [Mods and Workshop](steam/workshop.knack.md)
    — local mods versus Workshop subscriptions, linking a development
    folder, staging clean uploads, and the player's mod list

## Load Order

Load the Steam overview first, then the companion for the task at hand.
Before launching or stopping a game, also load
[Processes and Files](../windows/processes-and-files/overview.knack.md);
before driving its window, load
[Desktop Automation](../windows/desktop-automation/overview.knack.md).

## Related Knacks

- [In-host smoke testing](../software-engineering/testing/in-host-smoke/overview.knack.md)
  — a test runner inside a mod or plugin, an isolated data folder, and a
  launcher that scrapes the host log
- [Closed-assembly inspection](../dotnet/assembly-inspection/overview.knack.md)
  — reading a game's managed assemblies, with licence checks first
- [Agent shells on Windows](../windows/shells/overview.knack.md)
  — quoting paths such as `Program Files (x86)` through shell layers
- [Safe virtual-machine control](../virtualization/virtual-machine-control.knack.md)
  — when a test needs a machine of its own

A game installed on a person's workstation is theirs, and so are its
saves, settings, mod list, and play sessions. Treat a test run as a guest
in their installation.
