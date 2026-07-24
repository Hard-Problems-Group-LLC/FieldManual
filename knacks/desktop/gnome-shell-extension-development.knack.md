# GNOME Shell Extension Development

Load this knack when building, packaging, debugging, or iterating on a GNOME
Shell extension.

Source review: 2026-07-23. GNOME Shell APIs and internal actor behavior can
change at every major release; this knack provides a workflow, not a promise
that one implementation works unchanged across releases.

## Mental Model

An enabled extension is loaded into the GNOME Shell process. It is not an
ordinary application with its own process, event loop, or failure boundary.
Blocking an extension callback can stall the desktop shell, and leaked state
can survive an extension disable/enable cycle.

Treat these as separate boundaries:

- **source and package state** — what the project built;
- **installed extension state** — which files exist for the selected UUID;
- **Shell registry state** — whether the running Shell sees and enables it;
- **process state** — modules, registered types, signals, sources, and actors
  already loaded in `gnome-shell`; and
- **visible behavior** — what the active desktop session actually renders.

A success message at one boundary does not prove the next one.

## Declare and Test Version Support

The extension's `metadata.json` declares the Shell versions it supports.
List only major versions that the project actually tests. Review the official
upgrade guide for each new major version and test the built package in that
version's real or nested Shell environment before changing the declaration.

GNOME Shell extensions use ES modules on GNOME 45 and later. Supporting older
Shell families can require a deliberately separate loader or generated
compatibility build. Branch at the narrowest reliable boundary—normally Shell
major version or a documented API capability—not at a distribution name.

Prefer documented GNOME Shell, GJS, GIO, and Clutter APIs. GNOME Shell's
JavaScript UI modules are not a stable third-party application toolkit.
Subclassing private widgets, overriding internal methods, or depending on
actor-tree layout increases the per-release review burden. Isolate any such
dependency and keep a focused live test for it.

## Lifecycle Discipline

Create Shell-facing state from `enable()` and completely release it from
`disable()`:

- disconnect every signal;
- remove timeout, idle, and other GLib sources;
- destroy actors, menus, indicators, and dialogs;
- close or cancel streams, subprocesses, and network activity;
- clear references that would keep objects alive; and
- invalidate every outstanding asynchronous completion.

An enabled flag is not enough to protect asynchronous startup. A completion
from an old enable cycle can observe `true` after a newer cycle begins. Use a
monotonic generation or session token. Capture it before starting work and
accept a completion only while it still matches the active generation.
Dispose of an object immediately if it finishes construction after its
generation became stale.

Keep module top-level code limited to declarations and imports. Do not mutate
Shell state merely by importing a module.

## Reload and Test Strategy

JavaScript modules cannot be unloaded from the running interpreter. A
disable/enable cycle runs lifecycle methods again but does not guarantee a
clean module graph or process-global registry.

Use a tiered loop:

1. Validate metadata, syntax, schemas, translations, and package layout
   without touching the live session.
2. Build into an inspectable staging directory.
3. Install through the project's guarded, documented development path and
   report the exact target UUID directory.
4. Disable and enable for a quick smoke test only when the changed code is
   known to tolerate the retained process.
5. Start a clean Shell process for module entrypoints, type registration,
   metadata, stylesheet, schema, or unexplained stale-state changes.

On Wayland, use a nested development Shell when practical. Current official
guidance uses:

```text
dbus-run-session gnome-shell --devkit --wayland
```

for GNOME 49 and later, with `--nested --wayland` documented for GNOME 48 and
earlier. A nested Shell is convenient but not a security boundary and does not
protect host data.

The main Wayland Shell cannot normally restart while the user remains logged
in; use logout/login when a clean main session is required. On X11, the Shell
can normally be restarted through the Run Command dialog, but X11 does not
provide the same nested Wayland development path.

Treat `gnome-extensions install` as installation, not as proof that the
running process loaded new code. If a project directly replaces a
development UUID directory for faster iteration, that is a project-owned
mutation requiring exact path guards, staging verification, and a clean
release-packaging path. It is not a general hot-reload guarantee.

## Module and GObject Hazards

Cache-busted dynamic imports create new module instances in the same process.
They do not reset process-global state.

`GObject.registerClass()` registers a type name in the process. Re-importing a
development module that registers the same name can fail. Prefer testing in a
clean Shell process. When a deliberately cache-busted development build must
register a class, keep the registered class outside the reloaded module or
use a clearly development-only unique type name. Do not let that workaround
become an unbounded production type-registration scheme.

Pass Shell APIs the concrete types they document. For example, a panel status
area expects the appropriate `PanelMenu.Button` object; a wrapper that merely
owns such a button is not necessarily substitutable.

## Event and Menu Wiring

Use `PanelMenu`, `PopupMenu`, and other Shell-provided UI classes instead of
reimplementing their focus, grab, and accessibility behavior.

When a product adds a controller around Shell UI, keep these states distinct:

- the Shell menu is open or closed;
- the controller requested or authorized a transition;
- Shell dismissed or focused UI through its own policy;
- a menu item is visually enabled;
- it is logically enabled and activatable; and
- low-level events are observed only for diagnostics.

Do not infer the supported event hook from one Shell version. Start with
public signals and documented behavior. If the product must intercept or
override inherited behavior, isolate the smallest hook and retest pointer,
keyboard, focus, menu, and accessibility behavior on every supported Shell
major.

## Helper and Controller I/O

All event-path I/O must be asynchronous and bounded. This includes loopback
sockets, Unix sockets, pipes, D-Bus, subprocesses, and files: their failure
paths can still block.

For stream traffic:

- connect and read asynchronously;
- frame messages explicitly;
- write through a bounded FIFO;
- keep only one output write in flight;
- keep the outgoing byte object alive until completion;
- use a connection generation to reject stale callbacks;
- cancel reads, queued writes, timeouts, and close work during `disable()`;
- disconnect on queue overflow instead of growing without bound; and
- fall back to safe local behavior when the helper is absent.

Use watchdogs only when each side has a defined timeout consequence. A
heartbeat that can fail silently adds traffic without establishing health.

## Accessibility

Visual styling, logical enabled state, focusability, activation, and event
observation are different properties. Make them agree for ordinary controls.
If a development diagnostic intentionally observes a disabled-looking item,
label that as diagnostic behavior and do not present it as normal disabled
semantics.

Use the Shell's accessibility patterns and test keyboard-only navigation,
focus order, names, roles, state, and high-contrast behavior. Accessibility
cannot be recovered reliably after building a parallel custom menu system.

## Debugging Loop

When behavior appears stale or missing:

1. Compare source, staged package, and selected installed files.
2. Confirm the installed directory name exactly matches the extension UUID.
3. Inspect `gnome-extensions show <uuid>` for registry and error state.
4. Follow the active Shell's logs with the platform's user-journal tooling.
5. Confirm `enable()` reached the point that creates the visible actor.
6. Separate a deployment mismatch from module cache, duplicate type
   registration, async startup failure, and Shell-version incompatibility.
7. Reproduce in a clean nested or login session before inventing another
   reload mechanism.

An extension can be reported enabled while its own startup failed before
adding visible UI. Logs are normal verification evidence, not a last resort.

## Review Checklist

- Does metadata list only tested Shell majors?
- Are Shell-facing objects created and destroyed symmetrically?
- Can a stale async completion mutate a newer enable cycle?
- Is all event-path I/O asynchronous and bounded?
- Are private APIs isolated and covered by per-major live tests?
- Does the iteration path distinguish source, stage, install, registry,
  process, and visible state?
- Does a clean-process test cover module or registration changes?
- Do visual, enabled, focus, activation, and accessibility states agree?
- Are the live-session target and mutation authority explicit?

## Further Information

- GJS Guide, extension architecture:
  <https://gjs.guide/extensions/overview/architecture.html>
- GJS Guide, creating and testing extensions:
  <https://gjs.guide/extensions/development/creating.html>
- GJS Guide, debugging and clean-process reloads:
  <https://gjs.guide/extensions/development/debugging.html>
- GJS Guide, updates and breakage:
  <https://gjs.guide/extensions/overview/updates-and-breakage.html>
- GJS Guide, review guidelines:
  <https://gjs.guide/extensions/review-guidelines/review-guidelines.html>
- GJS Guide, popup menus:
  <https://gjs.guide/extensions/topics/popup-menu.html>
- GJS Guide, accessibility:
  <https://gjs.guide/extensions/development/accessibility.html>
- GIO output stream reference:
  <https://docs.gtk.org/gio/class.OutputStream.html>
