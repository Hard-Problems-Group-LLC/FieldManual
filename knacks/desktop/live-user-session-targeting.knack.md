# Live User-Session Targeting From Isolated Automation

Load this knack when a project-local agent, sandbox, container, service, or
wrapper needs to inspect or change the operator's real desktop or user
session.

Source review: 2026-07-23.

The concrete selectors in this document describe freedesktop/Linux sessions.
On macOS or Windows, apply the same identity, session, and authority model
through that platform's account database, login/session registry, service
manager, desktop selector, and supported user-configuration APIs. Do not
transpose XDG, D-Bus, systemd, Wayland, or passwd assumptions onto another
platform.

## Mental Model

Process identity, account identity, filesystem home, and live session are
separate facts.

An automation launcher may intentionally redirect `HOME` and XDG variables
into a project-local directory. That protects the operator's ordinary state,
but it also changes where tools read and write configuration, data, caches,
credentials, sockets, and registries. A command can report success after
updating the isolated tree while the visible desktop continues using a
different account home and session bus.

Never “fix” that mismatch by automatically switching to the passwd-database
home or copying the host environment wholesale. Crossing from isolated state
into the operator's live session is a new target and authority boundary.
Detect it, explain it, and require authorization for the exact operation.

Follow FieldManual's
[session and project boundaries](../../standards-and-practices/core/session-and-project-boundaries.md)
and [local operator state](../../standards-and-practices/core/local-operator-state.md)
standards.

## State That Can Select a Different Target

Inspect the variables and services relevant to the tool, including:

- real and effective user and group IDs;
- `HOME`;
- `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`, and
  `XDG_CACHE_HOME`;
- `XDG_RUNTIME_DIR`;
- session-bus selection such as `DBUS_SESSION_BUS_ADDRESS`;
- display selection such as `WAYLAND_DISPLAY` or `DISPLAY`;
- the systemd user manager and its environment;
- desktop-specific registries; and
- project wrapper, container, namespace, or remote-session boundaries.

The XDG Base Directory specification derives default config, data, state, and
cache locations from `HOME` when their explicit variables are absent.
Unsetting one variable can therefore change the target through fallback.

`XDG_RUNTIME_DIR` is different from a persistent home path. It is tied to the
logged-in user, must be private to that user, and contains session-lifetime
objects such as sockets. Do not synthesize a replacement path or point one
user at another user's runtime directory.

## Name the Intended Effect

Classify the operation before resolving a path:

1. **Project-isolated state** — intended only for the current checkout,
   sandbox, test session, or nested desktop.
2. **Live user-session state** — intended to affect the operator's active
   desktop, user service manager, D-Bus session, input/audio stack, or
   user-scoped application state.
3. **System state** — intended to affect multiple users or machine-wide
   configuration.
4. **Read-only diagnosis** — compares candidate targets without mutation.

Do not choose the class from whichever path currently exists. The requested
effect determines the target; the environment is evidence that the selected
process may or may not reach it.

## Resolution Procedure

Use this sequence:

1. Record the project root, process identity, current home and XDG values,
   runtime directory, display, and session-bus identity without printing
   secrets.
2. Determine whether the effective home or XDG path is contained by the
   project or a documented automation-state root.
3. Resolve candidate account and live-session targets through read-only,
   platform-owned interfaces. A passwd home is an account default, not proof
   of which session, display, bus, or user manager is active.
4. Compare the candidate target with what the authoritative desktop or
   service registry reports.
5. If the intended target is outside the active project or isolation
   boundary, stop unless the operator has authorized that exact class of
   mutation in the current task.
6. Print the selected target, selection reason, affected service or path,
   current identity, and whether the operation is read-only or mutating.
7. Invoke the narrow tool with an explicitly constructed environment.
8. Verify the result through the live registry or visible service, not only
   by checking the written file.

Repository containment and path components such as `.codex-home`, `.agents`,
or `.local` can flag likely isolation. They are heuristics, not authority to
select a different home.

## Construct the Environment Narrowly

Do not inherit or discard the whole environment by default.

- Preserve only variables the selected tool needs.
- Set an approved target explicitly where the tool supports a target option.
- Prefer the desktop or service's documented command over editing its private
  files.
- If clearing an isolated XDG variable is required to use a documented
  fallback, show the resulting path before mutation.
- Obtain bus, display, and runtime selection from the intended live session;
  do not guess them from another shell.
- Never forward tokens, agent credentials, SSH agent sockets, package-manager
  config, or unrelated secrets merely to make one desktop command work.
- Do not elevate to root for user-session work unless the platform explicitly
  requires a separate administrative operation.

A clean environment can still target the wrong session. Explicitly setting
the wrong values is not safer than inheriting them.

## Multiple and Remote Sessions

One account can have several local, nested, remote, graphical, or text
sessions. “The user's session” may therefore be ambiguous.

Require an explicit session selector when more than one candidate can receive
the effect. Include enough non-secret evidence for the operator to distinguish
them, such as session type, seat, display, start time, and whether it is local
or remote.

Do not redirect a nested-development operation into the main desktop merely
because both sessions have the same account ID. Do not assume an SSH shell
owns the graphical session it can discover.

## Mutation Safety

A user-scoped target can still contain valuable state. For mutations:

- offer a dry-run or inventory mode;
- require an exact service, UUID, unit, or file target;
- reject empty, root, home-root, project-root, and unresolved targets;
- avoid broad recursive replacement;
- preserve an existing unmanaged file or fail visibly;
- write atomically where the owning format permits it;
- use a backup or owning uninstall mechanism when recovery matters;
- report what changed and how to reverse it; and
- verify both stored state and live effect.

The tool must not turn a target mismatch into a silent fallback. A successful
isolated write and a refused live-session write are different outcomes.

## Diagnostic Patterns

| Symptom | Likely boundary to inspect |
| --- | --- |
| Command succeeds but visible desktop is unchanged | Isolated home/XDG path, wrong display, wrong session bus, or stale host process |
| File exists under the project but application cannot see it | Project-local home selected instead of live account data/config root |
| User service ignores a shell variable | User manager has a different retained environment |
| D-Bus command cannot find a service | Wrong or missing session bus or runtime directory |
| Operation affects a nested desktop, not the main one | Ambiguous display/session selector |
| Running with privilege makes state disappear | Root or another account now owns the home, bus, or runtime target |

## Tool Design Checklist

- Is the intended effect class explicit?
- Does the tool expose inventory/dry-run and an explicit target override?
- Does it identify isolated-home and XDG mismatches without changing them?
- Does it stop for authority before reaching outside the project boundary?
- Does it distinguish account home from active session selection?
- Does it print the resolved target and reason before mutation?
- Does it construct a minimal environment without leaking credentials?
- Does it reject ambiguous multiple sessions?
- Does it verify the authoritative live registry afterward?
- Can an operator recover or uninstall the change?

## Further Information

- XDG Base Directory Specification:
  <https://specifications.freedesktop.org/basedir/latest/>
- D-Bus specification:
  <https://dbus.freedesktop.org/doc/dbus-specification.html>
- systemd user service manager:
  <https://www.freedesktop.org/software/systemd/man/latest/systemd.user.html>
- systemd environment configuration:
  <https://www.freedesktop.org/software/systemd/man/latest/environment.d.html>
- GJS Guide, anatomy and user/system extension locations:
  <https://gjs.guide/extensions/overview/anatomy.html>
- GJS Guide, nested Shell debugging:
  <https://gjs.guide/extensions/development/debugging.html>
