# Directed Showcases: A Showcase Framework

Load this companion to the
[directed showcases overview](overview.knack.md) when a
showcase that began as a developer tool should become something users start
for themselves, or when several plugins for one host want to offer
showcases in a common way.

Reviewed: 2026-10-13. This describes a general shape, not a particular
host's API; menu, data and patching facilities differ by host.

## Why

A good directed showcase is entertaining as well as informative. Started
from a command-line flag it is a developer tool; started from a menu it is a
feature. A small framework lets the plugin, and other plugins for the same
host, declare showcases as data and run them in throwaway worlds without
touching the user's own.

## The Menus

1. **Showcases**, reached from the host's main menu: every plugin that offers
   at least one showcase, each with a preview image, name and count. Find
   them automatically from the showcase definitions loaded.
2. **A plugin's showcases**: each with a title, a short description, an
   estimated running time, and its requirements, such as an expansion or
   another plugin. List showcases whose requirements are unmet, disabled,
   with the reason.
3. **A showcase's details**: a longer description, a preview, any
   compatibility warnings, and **Start** and **Back**.

Back returns one level; Escape closes the whole flow. Use the host's own
dialog style, so the menus look like part of the application.

## Declaring a Showcase

Make the definition data the host already knows how to load, so that any
plugin can add one without code where possible:

| Field | Purpose |
| --- | --- |
| `label`, `description` | Menu text |
| `preview` | Image for the menus |
| `estimatedMinutes` | Shown before starting |
| `requires` | Plugins or expansions that must be present |
| `compatibility` | Other plugins known to interfere: identifier, severity, note |
| `world` | Size and preferences for the throwaway world |
| `worker` | The code that runs it |
| `scenes` | For director-driven showcases, the scene list |
| `narration` | Lines keyed by scene and outcome |

Keep narration in the definition's data, so it can be translated and tested.

## The Code Side

- A **worker** with three members: set up once the world exists, run every
  update, and report when finished. Simple showcases implement it directly.
- A **director** worker that runs declared scenes in order, with the caption
  bar, the skip control, the cue lines for capture, and the release of the
  camera at the end (see [the director](director.knack.md)).
- **Starting** a showcase generates a throwaway world the way the host's own
  quick-start does, remembers which showcase was requested, and starts its
  worker once the world exists. Nothing touches the user's saves unless they
  choose to save.
- **The command line still works.** A flag that names a showcase starts it
  directly, so launchers and capture tooling keep working.

## Other Installed Plugins

A showcase started from a menu runs alongside whatever else the user has
installed. Warn about what the showcase knows, and nothing more:

- **No warning by default.** Warn only when an installed plugin matches an
  entry in the showcase's compatibility list.
- **Concerns, warnings and known incompatibilities** appear on the details
  page with the showcase's note; Start still works.
- **A fatal incompatibility** refuses Start, with the reason. A separate
  "start anyway" action behind a confirmation remains for testing and for
  reproducing the problem.

Generic warnings about every unknown plugin teach users to ignore warnings.

## Hooking Into the Host

A host's main menu may offer no extension point. Adding an entry then needs
a runtime patch through a method-patching library or the host's own
modding facility. Treat that as a deliberate decision under the project's
policy on patching: keep the patch to the one entry, and keep everything
else patch-free. A fallback entry point, such as the plugin's settings page,
needs no patch but is harder to find.

## Packaging

Two shapes work:

- **Inside the first plugin**, under its own namespace and free of that
  plugin's specifics. Quickest to build, but other plugins would depend on
  the first one.
- **A small framework plugin** that every showcase provider depends on. The
  conventional shape for an interface many plugins share, at the cost of a
  separate package and a load-order rule.

A common path is to start inside the first plugin, kept generic, and split
it out when a second plugin wants it.

## Tests

- **Host-free unit tests:** scene sequencing, grouping showcases by
  provider, requirement and compatibility evaluation, narration lookup.
- **Data tests:** every definition's fields, preview images, and narration
  keys for every scene and outcome.
- **In-host smoke checks:** the menu entry exists; each menu level opens and
  lists the expected showcases; a command-line start runs each showcase to
  its end with the cue lines in order and no plugin errors.

## Further Information

- FieldManual, [In-Host Smoke
  Testing](../../testing/in-host-smoke/overview.knack.md):
  the runner and launcher a framework still relies on.
- Epic Games, [Sequencer
  overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-sequencer-movie-tool-overview):
  an engine-level example of data-driven cinematic sequences.
