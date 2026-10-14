# Directed Showcases

Load this knack when you build a scripted demonstration of software for a
person to watch, such as a feature tour of a plugin inside a host
application, a demonstration for stakeholders, or a recorded reel, or when a
demonstration shown to someone went wrong. Companions:

- [The director](director.knack.md): scenes, the cue
  timeline, camera direction, captions and narration, skipping, and reels
  that replay individually.
- [Staging](staging.knack.md): fixed seeds, keeping
  scenes clear of each other's hazards with shared geometry, protecting the
  cast and the screen, props with side effects, viewing settings, isolation
  of the viewer's data, and capture.
- [A showcase framework](framework.knack.md): turning
  a developer tool into a feature users can start from a menu.

The runner, its command-line flag, the isolated data folder and the log
protocol are shared with automated testing; see
[In-Host Smoke Testing](../../testing/in-host-smoke/overview.knack.md).

Reviewed: 2026-10-13.

## Mental Model

A showcase and a smoke test use the same machinery for different
audiences:

| | Smoke test | Showcase |
| --- | --- | --- |
| Audience | A launcher script | A person |
| Success | `DONE failed=0` | The watcher follows and enjoys each feature |
| World | Random each run; scenarios destroy freely | Fixed seed; staged and safe |
| Pace | As fast as the host allows | Real time, one thing at a time |
| Settings | Muted, small window | Sound, large interface, maximized |
| Output | Result lines | The screen, plus cues for capture and narration |

Make the showcase a mode of the test runner, started by its own flag, with a
fixed seed for everything the plugin generates, so that the watcher sees a
known, rehearsed layout. Keep it separate from the smoke test, which is
allowed to destroy everything.

**The watcher's reactions are the acceptance test.** A showcase can pass
every automated check and still fail: a warning marker a few pixels wide at
the viewing zoom, a bystander killed off-screen, a caption announcing a
scene that never runs, a camera pointed at empty ground while the action
happens elsewhere. Usability practice relies on watching people use a
system while they say what they think; do the same with a showcase. Watch
someone watch it, and note where they are confused, look away, or ask
"what just happened?". Treat each such moment as a defect, and record what
the watcher asks for as requirements.

## From Timer to Director

First showcases are often a timer: build everything, start demonstration A
after five seconds and B after twenty-five, and move the camera now and
then. Watchers find that hard to follow. Several things happen at once, the
camera is elsewhere when something important happens, and actions finish
early or late, because heavy scenes slow the host's simulation below real
time.

A director runs **one scene at a time**. Each scene sets up, frames the
camera, says what is happening, runs, and waits for the action to finish
(an aftermath ending, an effect completing, smoke settling) rather than a
fixed delay. Then the next scene begins. Engines with built-in cinematic
tools, such as Unreal's Sequencer and Unity's Timeline with Cinemachine,
embody the same idea; a plugin inside a closed host usually builds a small
director of its own.

## Core Practices

1. **One feature at a time**, with a caption naming it and a camera move
   that frames it.
2. **A cue at every beat.** The showcase logs a line when it is ready and
   when each scene starts and ends. Capture tooling and narration wait on
   those cues, never on fixed sleeps.
3. **Captions match what runs.** Build the opening card, chapter numbering
   and narration from the scenes that will actually run, and log every scene
   skipped and why.
4. **Stage with shared geometry.** Keep each scene clear of every other
   scene's reach, measured by one helper that every placement and filter
   calls. Two filters that measured the same rule from different geometry
   once dropped a scene silently.
5. **Protect the cast and the screen.** Move bystanders clear before
   anything dangerous, and avoid actions the host rejects with an error
   window.
6. **Tame the props.** Demonstration objects can draw the host's background
   actors, and the user's own resources, from far away. Switch off what
   would.
7. **Viewing settings are not test settings.** Large interface scale, sound
   on, and a maximized window applied after the host's own startup
   resolution change.
8. **Isolate the viewer's world.** Use a separate data folder, never touch
   their saves, settings or installs, and never close an instance you did
   not start.
9. **Reels replay individually.** Each chapter can run on its own, so one
   can be re-shown, recorded or fixed without the rest.
10. **The watcher stays in control.** Offer a way to skip or end the tour,
    leave the world running at the end, keep sound adjustable, and keep
    flashing effects within safe limits.

## A Natural Next Step

A showcase built for development is often worth offering to users. A
showcase framework in the plugin can list every showcase from a menu, with
descriptions, running times, requirements, and warnings about other
installed plugins known to interfere, and start each in a throwaway world.
The [framework companion](framework.knack.md)
describes the shape.

## Sharp Edges

- **Silent drops.** A scene that cannot be staged disappears unless the
  showcase logs it and the captions adapt.
- **Fixed delays.** Load and heavy effects stretch real time; a capture or a
  narration line timed by a delay lands on the wrong moment.
- **Props with side effects.** Storage that attracts the user's goods,
  workstations that summon workers across the world, and devices that extend
  the user's territory and attract threats all change the world around the
  demonstration.
- **Error windows.** A rejected action can open the host's debug log on top
  of the scene.
- **Everything at once.** A busy screen hides each feature behind the
  others.
- **Flashing.** Explosions and strobing effects can exceed safe flash
  limits; viewers with photosensitive conditions are at risk.
- **Invisible to agents.** An agent building a showcase usually cannot see
  the screen; captures at cues are its only evidence.
- **Private data in captures.** Recordings show whatever is on screen.
  Capture the host's window only, and review before sharing.

## Review Checklist

- The showcase is a separate mode with a fixed seed and its own settings.
- Scenes run one at a time and wait on conditions, not delays.
- Every beat logs a cue; capture and narration use the cues.
- Opening captions and numbering come from the scenes that will run;
  skips are logged and announced.
- One helper enforces each staging rule wherever it applies.
- Bystanders are moved clear; props cannot draw actors or goods away.
- The viewer's data, installs and running instances are untouched.
- Each reel runs on its own.
- The watcher can skip, the world stays running at the end, and effects
  respect flash limits.
- A person watched it, and their reactions were recorded and acted on.

## Further Information

- FieldManual, [In-Host Smoke
  Testing](../../testing/in-host-smoke/overview.knack.md):
  the shared runner, flags and log protocol.
- FieldManual, [Desktop Automation on a Shared Windows
  Workstation](../../../windows/desktop-automation/overview.knack.md):
  readiness markers, window placement, DPI awareness and captures.
- Jakob Nielsen, [Thinking Aloud: The #1 Usability
  Tool](https://www.nngroup.com/articles/thinking-aloud-the-1-usability-tool/),
  Nielsen Norman Group, 2012.
- W3C, WCAG 2.2 Understanding documents: [Pause, Stop,
  Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html),
  [Audio Control](https://www.w3.org/WAI/WCAG22/Understanding/audio-control.html)
  and [Three Flashes or Below
  Threshold](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html).
- Epic Games, [Sequencer
  overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-sequencer-movie-tool-overview),
  and Unity, [Cinemachine](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/index.html):
  cinematic direction built into engines.
