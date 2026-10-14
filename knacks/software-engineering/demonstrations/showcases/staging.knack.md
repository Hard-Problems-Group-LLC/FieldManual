# Directed Showcases: Staging

Load this companion to the
[directed showcases overview](overview.knack.md) when you
decide where each scene happens, keep scenes from harming one another or the
cast, set up the host for viewing, or capture the result.

Reviewed: 2026-10-13.

## Fixed Seeds, Random Worlds

Seed everything the plugin generates with a fixed value, so that the watcher
sees the rehearsed layout and a recording can be redone. The host's own
world may still differ per run, for example when the showcase starts from a
quick-start world on a random site. Plan for that:

- search for each scene's site with documented fallbacks (the preferred
  window, a wider one, then anywhere);
- when a scene cannot be placed, skip it, log the reason, and drop it from
  the opening card and the numbering; and
- rebuild generated content from the seed plus the obstacles actually
  found, so that the same world reproduces the same layout.

## A Stage Map

Write down where everything goes, with its reach:

| Area | Where | Contents | Reach |
| --- | --- | --- | --- |
| Base | Center, within 16 cells | Every feature, working | Small |
| Range | East of the base | Projectiles at a fixed target | Firing line |
| Pads | Two far corners | Self-destructing devices | Large: blast plus fires |
| Town | One quadrant | A generated settlement | Its parts plus a firebreak |

Keep the map in the showcase's design document and in sync with the code.
It is the first thing a reviewer needs.

## Keep Scenes Clear of Each Other

- **Compute each scene's full reach**, including secondary effects: fires
  it starts, secondary explosions, scattered projectiles, and anything that
  spreads. Add a margin.
- **Measure from what is there.** Keep-away distances run from the parts a
  scene actually occupies, not from a bounding rectangle around them; see
  [site selection](../../procedural-generation/data-first/sites.knack.md).
- **One helper per rule.** Every placement search and every filter that
  enforces "at least this far from the town" must call the same function.
  Two filters that measured one rule from different geometry once made a
  scene silently vanish on some worlds; site selection tells the story.
- **Stop spread at the edges.** Where effects spread cell to cell, as fire
  does, ring sensitive areas with a break of non-spreading ground.

## Protect the Cast

- **Move bystanders clear** before each dangerous scene: everyone within its
  reach plus a margin goes back to a safe area. In one showcase a bystander
  who had wandered into a long-range barrage died, unnoticed by any check
  until a capture showed it.
- **Allow for missing participants.** A scene that needs a volunteer should
  cope with none being available, and its caption should not promise one.
- **Keep the cast fit for the scene.** Fed, rested and healthy participants
  do not wander off mid-scene to eat or sleep.

## Protect the Screen

- **Avoid actions the host rejects.** Trying to remove an indestructible
  feature raised a host error that opened the developer log window over a
  scene. Leave such features alone; they can even add character.
- **Turn off automatic pausing** on threats and events, so that a pop-up
  alert does not freeze the tour.
- **Scrape the log anyway.** A showcase exercises combinations tests may not;
  one showcase surfaced a crash the tests had missed. Check the log after
  every showcase run.

## Props With Side Effects

Demonstration objects live in a world full of background actors, and the
host's own logic treats them like any other objects:

- storage that accepts goods attracts carriers from across the world,
  including the user's own goods;
- workstations, lights, power consumers and machines generate work that
  draws workers to them;
- loose items invite hauling; and
- objects owned by the user can extend the user's territory and attract
  threats to it.

Give props neutral ownership where the host allows it, switch off those that
generate work, mark loose items as off-limits, keep the props out of the
user's zones, and smoke test that nothing travels to or from the stage.

## Viewing Settings

| Setting | Test run | Showcase |
| --- | --- | --- |
| Interface scale | Default | Large, for reading at a distance |
| Sound | Muted | On, at a moderate level |
| Window | Small, windowed | Maximized |
| Automatic pausing | Off | Off |
| Developer tools | On | On when viewers should see debug buttons |
| Run when unfocused | Yes | Yes |

Write the settings into the run's isolated data folder, not the viewer's
own. Maximize only after the showcase logs `READY`: many hosts change
resolution or recreate their window during startup, which undoes an earlier
maximize. The
[desktop automation knack](../../../windows/desktop-automation/overview.knack.md)
covers placement, DPI awareness, and preference files on Windows.

## The Viewer's World

The person watching may also be a user of the host, with saves, settings,
installed plugins and perhaps a session already open.

- Run the showcase in its own data folder; never read or write the viewer's
  saves, settings or plugin list.
- Install the plugin by link into the host's plugin folder only when nothing
  else is there; never replace a folder you did not create.
- Never close, kill or reuse a host instance you did not start. Record the
  process you launched and act only on it.
- On request, relaunch, then confirm that exactly one showcase instance is
  running, and tell the viewer which window it is.
- When the viewer reports something odd, capture the screen and scan the log
  at once. In one session that turned a remark into a reproducible crash.

## Capture

Screen captures are the evidence a showcase worked, and the only evidence an
agent that cannot see the screen will have.

- Arm capture on cues, then take a short burst; crop each frame to the area
  of interest, enlarge with nearest-neighbor scaling, and tile the frames
  into one image for review.
- Make the capture process DPI-aware before its first coordinate call, find
  the window's visible frame, and clamp the capture rectangle to the
  monitor; a maximized window's rectangle extends past the screen. The
  [desktop automation
  knack](../../../windows/desktop-automation/overview.knack.md)
  gives the details and tested code for Windows.
- Check every capture for plausibility (size, not blank, expected content)
  before trusting it.
- Capture only the host's window, store captures in ignored local storage,
  and review them for personal data before sharing.

## Further Information

- FieldManual, [Desktop Automation on a Shared Windows
  Workstation](../../../windows/desktop-automation/overview.knack.md).
- FieldManual, [Data-First Generation: Site
  Selection](../../procedural-generation/data-first/sites.knack.md):
  measuring against occupied parts, and one helper per rule.
- FieldManual, [In-Host Smoke Testing: The
  Launcher](../../testing/in-host-smoke/launcher.knack.md):
  isolated data folders, preferences and process ownership.
- W3C, [Understanding Three Flashes or Below
  Threshold](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html).
