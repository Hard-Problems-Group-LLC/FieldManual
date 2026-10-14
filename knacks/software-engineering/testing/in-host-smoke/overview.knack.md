# In-Host Smoke Testing

Load this knack when you build a plugin, mod, extension or script for a
closed host application, such as a game, a design tool or an editor, whose
APIs only work inside the running host, and you need automated evidence that
the plugin loads, works against the real host, and logs no errors.
Companions:

- [Runner](runner.knack.md): the test runner inside
  the plugin, its log protocol, simulated time, scenario hygiene, error
  attribution, timing lines, and a showcase mode.
- [Launcher](launcher.knack.md): the script that
  isolates, configures and starts the host, waits for the result, scrapes the
  log, and drives screen capture.
- [Flakiness](flakiness.knack.md): random worlds,
  interfering actors, diagnostics and explanation functions, environment
  scaled thresholds, and the two-clean-runs rule.

Reviewed: 2026-10-13. Host command-line options, log formats and data
folders are product-specific; confirm each against your host's
documentation and behavior.

## Mental Model

A closed host cannot be loaded into a unit-test process. Its types need its
runtime, its world, and often a graphics device. Evidence therefore comes in
three layers, cheapest first:

1. **Unit tests of host-free logic.** Move every decision that does not need
   the host into a library that does not reference it: calculations, plans,
   state machines, selection rules. Test it in seconds.
2. **Static validation of data files.** Check the plugin's definition files
   against the host's schema or types without launching the host: unknown
   fields, bad references, missing assets.
3. **The in-host smoke run.** Launch the real host with the plugin. A runner
   inside the plugin drives scenarios and logs structured results. A
   launcher outside reads the log and returns an exit code.

The layers do not substitute for one another. A clean build and a clean
static validation can still be followed by a host that refuses to start
(content loaded in the wrong order) or reports configuration errors that
only its own loader checks.

McConnell's description of the daily smoke test still fits the third layer:
it should "exercise the entire system from end to end," it "does not have to
be exhaustive," and it "must evolve as the system evolves."

The split between an in-host runner and an external launcher mirrors engines
that support automation directly. Unreal's Gauntlet framework launches
sessions and parses their logs, and leaves the in-game side to "whatever
makes the most sense," including "just some command-line parameters that the
game interprets." A host without any test framework usually still offers
what the pattern needs: command-line arguments the plugin can read, a log
file, and a way to point the host at another data folder.

## The Parts

- **A runner inside the plugin**, dormant unless a command-line flag such as
  `-plugin-smoke` is present.
- **An isolated data folder per run**, so that the user's own settings, saves
  and plugin list are never read or changed.
- **Host preferences written for the run**: muted, windowed, developer mode
  on, no pausing when unfocused or on errors.
- **Structured log lines with a tag**: `[SMOKE] PASS name`,
  `[SMOKE] FAIL name: detail`, and a final
  `[SMOKE] DONE passed=n failed=m`.
- **A launcher** that waits for `DONE` with a timeout, scrapes the host log,
  attributes errors to the plugin by stack trace, and exits non-zero on any
  failure.
- **Simulated time**: the runner ticks the host's update loop many times
  inside one frame, and triggers per-frame engine work by hand where ticking
  alone skips it.
- **Scenario hygiene**: each scenario builds its own fixtures, asserts its
  preconditions, and tears down what it built; destructive scenarios run
  last.
- **A final error sweep** of the host's in-process log queue, for hosts whose
  log file does not record severity.
- **Flake control** for hosts that generate a different world each run.
- **A showcase mode**: the same runner builds a demonstration for people to
  watch instead of running checks.

## Adding a Check

1. Move what you can into host-free code and unit test it there.
2. Write the scenario: build fixtures in a cleared area, assert the
   preconditions, act, advance time within a tick budget while polling for
   the expected condition, assert, and tear down.
3. Log `PASS` or `FAIL` with measured and expected values in the detail.
4. Prove the check can fail with a sabotage run (see [Proving Checks Can
   Fail](../proving-checks/overview.knack.md)).
5. Run the whole suite until it passes twice in a row.
6. Add a timing line if the scenario exercises something expensive.

## Sharp Edges

- **The user's data is one wrong argument away.** If the data-folder override
  is misspelled or ignored, the run uses the user's real settings and saves.
  The runner should log the folder it actually uses, and the launcher should
  refuse to continue when it is the default.
- **Missing DONE is a failure.** A crash, hang or modal dialog stops the run
  silently. The launcher's timeout, not the absence of `FAIL` lines, decides.
- **The first line of an error lies about its owner.** Host errors usually
  begin inside host code. Attribute by stack trace.
- **The log file may drop severity.** Some hosts write errors and
  information identically to the file. Read the host's in-process log queue
  as the final check.
- **A clean log is not a pass.** In one project eight of nine runs with
  deliberately broken behavior logged no error at all. Only assertions
  catch broken behavior; log scanning is an extra check.
- **The host's exit code says nothing.** Hosts often exit with 0 whatever
  the checks found. Decide from the runner's lines.
- **Scenarios leak into one another.** An earlier explosion kills the
  subjects a later check needs, and a later check then passes vacuously.
  Build fresh fixtures, tear down, and run destructive scenarios last.
- **The host is busy too.** Background workers move test items, and
  scheduled events arrive mid-check. Neutralize them for the run.
- **Random worlds cause flakes.** A check that passes on one generated world
  fails on another. Diagnose, scale thresholds to the environment, and
  require two clean runs.
- **Pauses stall runs.** Hosts that pause when unfocused or on error leave the
  runner waiting forever. Set the preferences, and keep the timeout.
- **Fixed waits waste minutes.** Wait on log cues and conditions, not
  sleeps, in the launcher and in screen-capture tooling.

## Review Checklist

- Host-free logic is unit tested outside the host; data files are validated
  statically.
- The runner is inert without its flag, and logs its data folder.
- Each run uses a fresh isolated data folder with written preferences and an
  explicit plugin list.
- Every scenario asserts preconditions, logs measured values, tears down, and
  has been seen to fail under sabotage.
- Destructive scenarios run last.
- The launcher fails on timeout, on a missing `DONE`, on any `FAIL`, and on
  any error attributed to the plugin by stack trace.
- The in-process log queue is checked at the end of the run.
- A change is called green only after two consecutive clean runs.

## Further Information

- Steve McConnell, [Daily Build and Smoke
  Test](https://stevemcconnell.com/articles/daily-build-and-smoke-test/),
  *IEEE Software* 13(4), 1996.
- Epic Games, [Gauntlet Automation Framework
  Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/gauntlet-automation-framework-overview-in-unreal-engine):
  session launching, log parsing, and game-interpreted command-line
  parameters.
- Unity, [Player command-line
  arguments](https://docs.unity3d.com/Manual/PlayerCommandLineArguments.html):
  `-logFile`, windowing and batch-mode options, as an example of host
  launch controls.
- Test Anything Protocol, [TAP version 14
  specification](https://testanything.org/tap-version-14-specification.html):
  a line-oriented result protocol worth borrowing from.
- Martin Fowler, [Eradicating Non-Determinism in
  Tests](https://martinfowler.com/articles/nonDeterminism.html).
- FieldManual, [Test Development and Mock
  Use](../../../../standards-and-practices/core/test-development-and-mock-use.md)
  and [Staged Verification for Multi-Agent
  Work](../../../AI/agent-orchestration/staged-verification.knack.md).
