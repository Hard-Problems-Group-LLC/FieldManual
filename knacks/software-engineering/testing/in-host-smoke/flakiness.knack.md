# In-Host Smoke Testing: Flakiness

Load this companion to the
[in-host smoke testing overview](overview.knack.md) when
a smoke check passes on one run and fails on the next, or before trusting a
suite that runs on a world the host generates afresh each time.

Reviewed: 2026-10-13.

## Where Nondeterminism Comes From

A unit test controls its inputs. An in-host check shares a living world:

- **Generated worlds.** Terrain, obstacles, resources and starting actors
  differ per run unless the seed is fixed, and many hosts' quick-start modes
  do not expose the seed.
- **Background actors.** Workers haul the items a check placed, creatures
  wander into a test area, automated defenses fire at test targets.
- **Scheduled events.** Raids, weather, disasters and timed story events
  arrive mid-check.
- **Needs and moods.** A test actor gets hungry or tired and abandons the
  task the check is waiting for.
- **Order effects.** Earlier scenarios leave damage, fires, debris or dead
  actors behind.
- **Timing.** Work deferred to rendered frames, or spread across frames,
  completes at different tick counts on different machines.

Martin Fowler's catalogue of non-determinism in tests (lack of isolation,
asynchronous behavior, remote services, time, resource leaks) applies, and
Luo and colleagues found asynchronous waits, concurrency and test-order
dependency to be the most common causes of flaky tests in the projects they
studied. Each of those has an in-host form above.

## Neutralize the World

Remove the sources you do not need before the checks start:

- **Silence the event scheduler** for the run, so that no raid or disaster
  lands mid-check. In one project, an unscheduled raid drew fire from a
  test turret and consumed the ammunition a later check counted.
- **Quiet the stage** before sensitive scenarios: put out fires, remove
  hostiles, and move or immobilize bystanders.
- **Satisfy needs** of actors a check depends on: fed, rested, healthy, so
  that they do not abandon the task.
- **Account for every carrier.** When counting items, count those in actors'
  hands and inventories, those in transit, and those consumed, not only the
  ones on the ground.
- **Stage on cleared ground** away from the generated world's features, and
  verify the ground is clear rather than assuming it.
- **Pin random parameters** that a check does not test. If a countdown is
  drawn from a range, hold it at the value the check needs for the run,
  through the plugin's data or a test hook, and restore it afterward.
- **Set state just before the check.** Randomness inside the system under
  test also causes flakes. In one suite a device's fuel lasted a random
  duration and ran out during earlier scenarios about one run in twenty;
  refueling it immediately before its check fixed the flake. The failure
  had first been put down to a person's mistake; accept no explanation for
  a failure, from anyone, without evidence.
- **Pin defaults that change.** When a new setting ships with a default
  that alters behavior, set older scenarios to the value they were written
  for, so that their geometry and timing stay what they test.
- **Fall back in stages, then skip loudly.** When a generated world leaves
  no room for a scenario, widen the search in documented steps (the
  preferred area, then a larger window, then the whole world). If nothing
  fits, log the skip with an explanation tally and count it separately
  from passes; never let it pass silently.

## Measure What You Mean

Many flakes come from measuring a proxy at the wrong moment:

- **Extremes over instants.** "The actor ran at least 8 tiles past the
  boundary before the pull started" is a property of the whole interval; the
  actor's position at the instant of measurement is not. In one suite a
  creature that had fled far enough was twice seen wandering back before the
  instant of measurement. Track the maximum distance reached instead.
- **Windows over points.** Assert that an event happened within a tick
  window, such as 120 to 151 ticks, derived from the specification and the
  host's polling interval, not at an exact tick.
- **Causes over outcomes.** Assert the marker unique to the rule, not an
  outcome other paths can produce (see the
  [vacuous checks](../proving-checks/vacuity.knack.md)
  patterns).
- **Only what the claim needs.** Over-strict checks flake too. A check that
  a production queue stopped at its target also demanded that an unrelated
  stock of materials stay untouched; background workers moved the stock,
  and the check failed. Assert the claim (nothing more was produced), not
  incidental state.

## Statistical Behavior

When the plugin makes random choices, such as how each actor reacts, test
the distribution and the stability rather than one outcome:

- make the choice a deterministic function of a seed and stable
  identifiers, so that the check can compute every expected choice in
  advance;
- pick a seed, logged, that yields at least a few of each outcome, so that
  every branch is exercised; and
- assert that each subject acts on its expected choice and that no choice
  changes during the run.

A choice computed as a hash of stable identifiers and a stored seed also
lets unit tests check the split of outcomes, and spares saved games from
storing derived state.

## Scale Thresholds to the Environment

A fixed threshold that holds on a roomy world fails on a cramped one. Derive
thresholds from what the environment allows: expect "at least 80 percent of
the placeable cells" rather than "at least 200 cells"; expect power output
relative to the generators actually built. A check that expected at least a
hundred fires after a blast failed on a barren world that produced 35; it
now counts against the cells in range where the host says a fire can
start. Log the denominator, so that a failure shows whether the
environment or the code fell short. Do not loosen a threshold until it can
no longer fail; a sabotage run should still trip it.

## Diagnostics and Explanation Functions

When a map-dependent check fails, the log must say why without a rerun:

- **Dump the inputs the check depended on**: positions, counts, terrain
  under the fixtures, nearby actors, the world identity or seed.
- **Write explanation functions** for decisions the plugin makes, and log
  their output on failure. An explanation function returns a tally of why
  candidates were accepted or rejected:

  ```text
  [SMOKE] INFO site-search: 0 of 1,152 candidates accepted;
          rejected: water 610, steep 288, map edge 196, fixed obstacle 58
  ```

  The same function serves unit tests and the plugin's own diagnostics. See
  [data-first generation](../../procedural-generation/data-first/overview.knack.md)
  for its use in site selection.
- **Name the environment in the failure**: "failed on a cramped world" and
  "failed on every world" lead to different fixes.
- **Log measurements in passing runs too.** An `INFO` line with the measured
  value on every run, not only on failure, lets you compare a failing run
  with dozens of passing ones. In one suite, comparing a flee distance
  across about thirty saved runs showed one creature type reaching the
  target distance and then wandering back.
- **Keep every run's output**, named by time and commit, and correlate
  failures across runs by counting: which checks fail together, on which
  kinds of world, with which obstacles nearby.
- **Trace temporarily.** For a failure the diagnostics cannot explain, add
  a per-tick trace of the subject's state to the runner output for a few
  runs, and remove it before committing.

## Triage

1. **Read the diagnostics** of the failing run. Decide whether the code, the
   check, or the environment is at fault.
2. **Rerun once.** A pass does not close the case; it confirms flakiness.
3. **Find the source** in the list above. Most in-host flakes trace to an
   interfering actor, a scheduled event, a measurement at the wrong moment,
   or a threshold that ignores the environment.
4. **Fix the cause**, not the symptom. Extra retries or longer waits without
   a reason only hide it.
5. **Prove the fixed check still fails** under sabotage.
6. **Require two consecutive clean runs** of the whole suite before calling
   the fix done.
7. **Register** a flake you cannot yet fix, with its observed rate, as
   [staged verification](../../../AI/agent-orchestration/staged-verification.knack.md)
   describes, and treat a rise in that rate as a regression.

## Why Two Clean Runs

One clean run on a generated world says the change works on that world. A
second run on a different world catches the commonest map-dependent
failures cheaply. Two runs are not proof: a flake that occurs one run in
ten passes twice in a row more often than not, and in one project the
generated-world flakes ran at roughly one run in ten to thirty. Track
failure rates over time for anything that has ever flaked, and investigate
a check whose rate rises.

## Fixing the Seed

If the host lets you choose the world seed, use a small fixed set of seeds
for routine runs and a random one occasionally, and log every seed. Fixed
seeds make failures reproducible; random seeds find the worlds the fixed set
missed. If the host does not expose the seed, log enough of the world's
identity (name, size, terrain summary) to recognize a recurrence.

## Further Information

- Martin Fowler, [Eradicating Non-Determinism in
  Tests](https://martinfowler.com/articles/nonDeterminism.html).
- Qingzhou Luo et al., [An Empirical Analysis of Flaky
  Tests](https://doi.org/10.1145/2635868.2635920), FSE 2014.
- Google Testing Blog, [Flaky Tests at Google and How We Mitigate
  Them](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html).
- FieldManual, [Staged Verification for Multi-Agent
  Work](../../../AI/agent-orchestration/staged-verification.knack.md): the
  flaky-check registry.
