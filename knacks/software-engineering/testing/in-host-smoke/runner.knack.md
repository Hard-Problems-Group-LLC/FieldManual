# In-Host Smoke Testing: The Runner

Load this companion to the
[in-host smoke testing overview](overview.knack.md) when
you write or review the test runner that lives inside the plugin.

Reviewed: 2026-10-13. The sketches use C#-like pseudocode with invented
host calls (`Host.TickOnce`, `Host.Log`); map them to your host's real API.

## Activation

The runner ships inside the plugin and does nothing unless the host was
started with its flag:

```csharp
static void OnPluginLoaded() {
    var args = Environment.GetCommandLineArgs();
    if (args.Contains("-plugin-smoke"))
        Runner.Schedule(Mode.Checks);
    else if (args.Contains("-plugin-showcase"))
        Runner.Schedule(Mode.Showcase);
    // Otherwise: no runner, no hooks, no cost.
}
```

- Read the flag once, at load. Never let a saved setting or a user-visible
  option start the runner.
- Wait for the host to be ready: world loaded, first frame drawn, plugin
  initialization finished. Start from a known state, such as a fresh
  quick-start world, rather than whatever the host restored.
- Log the environment first: plugin version, host version, data folder in
  use, world seed or identity, the list of loaded plugins, and anything in
  the world at the start that could interfere, such as hostile actors or
  active hazards.

## Log Protocol

Every runner line carries a tag that nothing else in the log uses:

```text
[SMOKE] START host=<version> plugin=<version> data=<folder> world=<id>
[SMOKE] PLAN 42
[SMOKE] PASS reactor-output
[SMOKE] FAIL pull-radius: 2 of 11 items beyond 1.5 tiles (max 3.2)
[SMOKE] INFO pull-radius: seed=1234 origin=(40,52)
[SMOKE] TIME pathfind-long 38ms
[SMOKE] DONE passed=41 failed=1
```

Rules:

- **Stable, unique names.** Names are the join key between runs, sabotage
  records and flake registries. Keep them short, lowercase and hyphenated.
- **Failures explain themselves.** Give measured and expected values and the
  entity or position involved, and say where things went: "missing: crate 7
  (not destroyed; carried by a worker)" or "not connected to any power
  network". A bare `FAIL` costs a rerun to diagnose.
- **A plan line.** Declaring the number of checks lets the launcher detect
  checks that never reported, the same job TAP's plan line does.
- **DONE always prints.** Wrap the run in `try`/`finally`, so that an
  exception in one scenario becomes a `FAIL` and the summary still appears.
  The launcher treats a missing `DONE` as failure regardless.
- **One line per result.** Multiline details break scraping; put extra
  context on `INFO` lines that follow.
- **Print "never" for events that never happened.** Arithmetic on a `-1`
  sentinel produces numbers such as "started -29034 ticks after the hit"
  that look like timing bugs and send diagnosis the wrong way.

## Scenario Structure

```csharp
void ScenarioPullGathersItems() {
    var site = Stage.ClearArea(center, radius: 15);       // known ground
    var items = Stage.PlaceExactly(itemDef, RingAround(site.Center, 4..9));
    Require(items.Count == 11, "11 items placed");        // precondition
    Require(items.All(i => Dist(i, site.Center) > 3), "items start outside");

    var effect = Spawn(effectDef, site.Center);
    bool done = Ticks.Until(() => effect.Finished, budget: 600);

    Check("pull-finishes", done, $"not finished after 600 ticks");
    var far = items.Where(i => i.Exists && Dist(i, site.Center) > 1.5);
    Check("pull-gathers", !far.Any(), $"{far.Count()} beyond 1.5");
    Stage.TearDown(site);                                 // remove all built
}
```

- **Build fixtures, never inherit them.** A scenario that relies on objects
  left by an earlier one breaks, or passes vacuously, when that scenario
  changes.
- **Require preconditions.** A failed precondition logs `FAIL` with the
  reason; it must not silently skip the check.
- **Place exactly.** Choose positions from the specification: inside, on and
  beyond each boundary. Search for free cells only near those positions, and
  assert the result. Give every fixture its own cell; fixtures stacked on
  one cell can interact and produce the expected result between themselves.
- **Count changes, not totals.** In a world shared with earlier scenarios,
  take a count before acting and assert the difference.
- **Drive real paths.** Trigger behavior the way the host would: fire a real
  projectile at the target rather than calling its damage method, so that a
  target the host cannot actually hit fails the check.
- **Wait on conditions with a budget.** Poll a condition while advancing
  time, and fail when the budget runs out.
- **Tear down** what the scenario built, and restore any global setting it
  changed: time speed, weather, event scheduling, selection, camera. Fence
  each scenario's area and check for leftovers by type afterward; debris
  such as spent projectiles from one scenario can contaminate the next.
- **Share seams with developer controls.** A test hook that triggers a
  behavior directly can double as a developer-mode button, so that manual
  and automated checks exercise the same code.
- **Survive a lost fixture.** Before using a fixture built earlier in the
  scenario, confirm it still exists. If it has vanished, fail that one check
  with diagnostics, rebuild the fixture, and continue. In one suite an
  unguarded null reference aborted the runner after 57 checks and skipped
  about 70 more.
- **Derive expected values from the model.** Where a host-free library
  predicts a result (a cost, a duration, a count), have the in-host check
  compare the host's actual result with the library's prediction. Drift
  between them is a defect in one or the other. In one case the in-host code
  repaired one injury at a time, rounding each injury's steps up, while the
  library summed the injuries first and predicted fewer steps. Call the same
  pure functions the code uses, state the slack allowed, and expect a new
  check's first failures to be the checker's own arithmetic as often as the
  code's.

## Simulating Time

Hosts with an update loop usually expose a tick or step function. Calling it
repeatedly inside one frame advances the world far faster than real time,
and deterministically with respect to frame rate:

```csharp
static bool Until(Func<bool> condition, int budget) {
    for (int i = 0; i < budget; i++) {
        if (condition()) return true;
        Host.TickOnce();          // one simulation step, no rendering
    }
    return condition();
}
```

- **Measure in ticks, not seconds.** A tick count is the same on every
  machine; elapsed wall time is not.
- **Some work only happens per frame.** Engines often defer work to the
  rendering frame: cache rebuilds, visibility and path-grid updates, deferred
  destruction, effects, user-interface state. Ticking alone skips it. Call
  the specific update by hand when the check depends on it, or yield one real
  frame and continue. In one suite, newly built consumers reported "not
  connected to any power network" however long the check waited, because
  the host rebuilt its networks once per rendered frame; calling that
  rebuild explicitly fixed the check, and waiting longer did not.
- **Inspect lazily resolved state before ticking.** Some hosts queue work
  and resolve it on the next tick: marked-for-removal buffers, pending
  collapses, deferred spawns. A check that ticks first finds the buffer
  already empty, and the evidence gone. Read or snapshot such state before
  the tick that resolves it.
- **Keep frames responsive.** Thousands of ticks in one frame freeze the
  window, and the host or operating system may report it as hung. Split long
  waits across frames, with a few hundred ticks each.
- **Fixed steps keep results comparable.** If the host lets you choose the
  step, use a fixed one. Glenn Fiedler's "Fix Your Timestep!" explains how a
  fixed delta time decouples simulation from frame rate and makes runs far
  more repeatable, though floating-point differences can remain.

## Ordering and Isolation

- **Order scenarios from least to most destructive.** Explosions, deletions,
  world-wide effects and anything that kills actors run last. Luo and
  colleagues found test-order dependency among the leading causes of flaky
  tests.
- **Remove bystanders before destructive scenarios.** Objects from earlier
  scenarios can be damaged, triggered or set off by a later blast. Remove them
  without side effects, using the host's silent-removal option where one
  exists, rather than destroying them in a way that runs their own effects.
- **Stage destructive scenarios** on cleared ground away from everything
  else, with actors moved away or made safe.

## Error Attribution

The host logs its own errors, and the plugin's errors often surface inside
host code. Attribute by the whole stack trace, not the first line:

- an error is the plugin's if any frame in its trace belongs to the plugin's
  namespace or assembly, or the message names the plugin;
- errors with no trace are listed separately for a person to judge;
- warnings that mention the plugin count too, if the project treats them as
  defects; and
- the runner's own lines are excluded first. A substring filter for the
  plugin's prefix also matches the runner's `FAIL` lines when they are
  logged as warnings, and counts each failure a second time.

A clean log is an additional check, never the test itself: broken behavior
usually logs nothing.

When the host's log file records errors and information identically,
severity cannot be recovered from the file. Many hosts also keep an
in-process message queue or log buffer, such as the one behind a developer
console, with severity attached; look for it in the host's API or reference
source. As the final check before `DONE`, read that queue for the run's time
window and fail on any error, or any warning about the plugin:

```text
[SMOKE] FAIL host-log-clean: 2 errors logged during run (first: ...)
```

## Timing Lines

Wrap expensive operations, such as a large generation step, a long path
search, a blast over a crowded area, or a save and reload, in a timer and
log a `TIME` line with the workload beside it:

```text
[SMOKE] TIME blast-aftermath 355ms (88 secondaries, 105 fires)
```

Identical code took between about 0.35 and 6.3 seconds in one suite,
because each generated world produced between 32 and nearly 2,000 fires.
Without the workload the numbers are noise. Avoid asserting on wall-clock
time; if a limit is needed, make it generous and relative to the workload.
Discard the first measurement of anything that loads or compiles on first
use. The lines are cheap performance checks: compared across runs, a
regression that doubles a cost per unit of work shows up without a
profiler.

## Showcase Mode

The same runner, under a second flag, builds a demonstration for people
rather than running checks:

- it builds a representative scene with every feature working, at a pace a
  person can follow;
- it logs `[SHOWCASE] READY` when the scene is complete, so that launchers and
  capture tools can wait for it;
- it skips assertions, or keeps only sanity checks that log warnings; and
- the launcher gives it sound, a maximized window and a readable interface
  scale, while test runs stay muted and small.

Showcase code exercises the plugin's public behavior in combinations tests
may not, and a showcase has found defects the tests had missed. Scrape its
log for plugin errors too. Keep its fixtures separate from the test
scenarios so that tuning a demonstration never weakens a check, but share
the helpers that enforce safety rules. Directing, staging, captions and
capture for showcases are covered in [Directed
Showcases](../../demonstrations/showcases/overview.knack.md).

## Further Information

- Test Anything Protocol, [TAP version 14
  specification](https://testanything.org/tap-version-14-specification.html):
  plans, `ok` and `not ok` lines, and `Bail out!`.
- Glenn Fiedler, [Fix Your
  Timestep!](https://gafferongames.com/post/fix_your_timestep/): fixed
  steps and accumulators.
- Qingzhou Luo et al., [An Empirical Analysis of Flaky
  Tests](https://doi.org/10.1145/2635868.2635920), FSE 2014.
- FieldManual, [Proving Checks Can
  Fail: Vacuous
  Checks](../proving-checks/vacuity.knack.md).
