# Directed Showcases: The Director

Load this companion to the
[directed showcases overview](overview.knack.md) when you
design or review the code that sequences a showcase: its scenes, cues,
camera, captions, narration, skipping and reels.

Reviewed: 2026-10-13. The sketches use C#-like pseudocode with invented
host calls (`Camera.Frame`, `Host.Message`); map them to your host's API.

## The Scene Contract

A scene is a small object with a fixed lifecycle:

| Step | Does | Typical content |
| --- | --- | --- |
| `Setup` | Builds what the scene needs | Spawn the subject, move bystanders clear |
| `Frame` | Points the camera | Position, zoom, selection of the subject |
| `Caption` | Says what is happening | Caption bar text, an opening narration line |
| `Run` | Starts the action | Arm the device, give the order |
| `IsFinished` | Reports completion | A condition on world state |
| `Outcome` | Describes what happened | Survivors, counts, which branch ran |

The director runs scenes in order:

```csharp
void Tick() {
    switch (state) {
    case State.Start:
        scene = scenes[index];
        Cue($"SCENE {index + 1}/{scenes.Count} {scene.Name} START");
        scene.Setup(); scene.Frame(); scene.Caption(); scene.Run();
        startedAt = Now; state = State.Running; break;
    case State.Running:
        if (scene.IsFinished() || Now - startedAt > scene.Budget) {
            var outcome = scene.Outcome();
            Cue($"SCENE {index + 1}/{scenes.Count} {scene.Name} END " +
                $"outcome={outcome}");
            Narrate(scene, outcome);
            holdUntil = Now + scene.Hold; state = State.Hold;
        }
        break;
    case State.Hold:
        if (Now >= holdUntil) {
            index++;
            state = index < scenes.Count ? State.Start : State.Done;
        }
        break;
    case State.Done:
        Cue("DONE"); Camera.Release(); break;
    }
}
```

- **Wait on conditions.** `IsFinished` asks the world: the aftermath has
  ended, the effect has completed, the smoke has settled. A budget stops a
  stuck scene; log it as a warning and move on rather than freezing the
  tour.
- **Hold after the action.** A short pause after each scene lets the watcher
  see the result and read the caption before the camera moves.
- **Keep scenes independent.** Each scene builds or checks its own
  preconditions, so that scenes can be reordered, skipped or replayed.

## The Cue Timeline

Every beat logs one tagged line. External tools, such as screen capture,
recorders and narration players, wait on these lines instead of on time.

```text
[SHOWCASE] READY scenes=8 seed=4242
[SHOWCASE] SCENE 3/8 reactor-shutdown START
[SHOWCASE] BEAT reactor-shutdown countdown
[SHOWCASE] SCENE 3/8 reactor-shutdown END outcome=contained
[SHOWCASE] SKIP corner-demo: no corner clears the town by 88 tiles
[SHOWCASE] DONE
```

- Log `READY` only when the whole stage is built and the first scene can
  start; a launcher maximizes the window and capture tools arm on it.
- Use `BEAT` lines for moments inside a scene that capture should catch,
  such as the instant before a blast.
- Log real time and simulation time at each `END`. Heavy scenes slow the
  simulation; the numbers show where a reel runs long.

## Directing the Camera

- **Frame the subject.** Every scene starts with the camera on its subject
  at a zoom where the subject's details read.
- **Zoom in for small things.** A countdown marker that was clear up close
  turned out to be a few pixels wide at the overview zoom, and watchers
  missed it.
- **Pull back for big things.** Anything with a large radius needs the whole
  radius in frame before it goes off.
- **Frame reactions off-center.** When the scene's point includes a
  reaction, such as two bystanders commenting just outside a blast, place
  them to one side so the main subject keeps the frame.
- **Show the interface.** Selecting the subject makes the host show its
  buttons and inspection text, which explain more than narration can.
- **Do not cut during the action.** Move the camera between beats, not
  during them.
- **Let go at the end.** The director releases the camera and leaves the
  world running; the watcher can explore what was built.

## Captions and Narration

- **A caption bar** names the chapter and its place: "2 of 8: Power for the
  Modern Settlement". Build the numbering from the scenes that will run.
- **The opening card** lists what the tour will show, built from the same
  list. If a scene was skipped during staging, the opening card leaves it
  out and the log says why.
- **Commentary** appears as short messages tied to events. Where the host
  supports it, link each message to its subject, so that a click jumps the
  camera there.
- **Narration reads outcomes.** Key lines by scene and outcome, not by
  script position: "if the subject survived" and "if it did not" each get a
  line. A narrator who describes what actually happened stays credible when
  the simulation surprises everyone.
- **Narration is data.** Keep lines in data files, keyed by scene and
  outcome, so that they can be translated and checked by tests for tone,
  length and missing keys.
- **A through-line helps.** A narrator with a consistent voice, or a framing
  device such as a period public-information film presented in numbered
  reels, ties separate features into one story. Choose it to match the
  project's tone.

## Skipping and Control

Moving content that starts by itself and runs for more than a few seconds
should give the viewer a way to pause, stop or hide it; WCAG's "Pause, Stop,
Hide" criterion states the principle for web content. For a showcase:

- a visible **Skip** control ends the current scene or the tour;
- ending early releases the camera and leaves everything running;
- the host's own volume controls keep working, and narration audio has its
  own volume; and
- effects that flash keep within the general flash thresholds.

## Reels and Chapters

Long tours become hard to show, record and fix as one piece. Divide them
into reels that can run on their own:

- **Self-contained setup.** A reel builds or verifies everything it needs,
  or starts from a known checkpoint, rather than relying on earlier reels.
- **Selectable.** A flag or menu entry starts one reel:
  `-plugin-showcase=reactor` or `-plugin-showcase-reel=3`.
- **Stable names and numbers**, so that recordings, notes and bug reports
  refer to the same reel over time.
- **Title cards per reel**, so that a recording of one reel stands alone.
- **One recording per reel.** Re-record only the reel that changed.

## Testing the Director

- Unit test scene sequencing, numbering, skip handling and outcome-keyed
  narration lookup in host-free code.
- Check narration data: every scene and outcome has a line, and no line
  exceeds the caption bar's width.
- Run the whole showcase, or each reel, under the in-host runner at speed,
  and require the cue lines in order, a `DONE`, and no plugin errors in the
  log.
- Review captures taken at each cue before showing the tour to anyone.

## Further Information

- Epic Games, [Sequencer
  overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-sequencer-movie-tool-overview):
  multi-track cinematic direction in an engine.
- Unity, [Timeline](https://docs.unity3d.com/Packages/com.unity.timeline@1.8/manual/index.html)
  and [Cinemachine](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/index.html):
  sequencing and procedural camera framing.
- W3C, [Understanding Pause, Stop,
  Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)
  and [Understanding Captions
  (Prerecorded)](https://www.w3.org/WAI/WCAG22/Understanding/captions-prerecorded.html).
- FieldManual, [In-Host Smoke Testing: The
  Runner](../../testing/in-host-smoke/runner.knack.md):
  the log protocol the cues extend.
