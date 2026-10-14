# Proving Checks Can Fail: Vacuous Checks

Load this companion to the
[overview](overview.knack.md) when writing or
reviewing a check, or when a sabotage run reveals that a check passed without
observing anything. Each pattern below gives the symptom, a neutral example,
the reason it passes, the guard, and the sabotage that exposes it.

Source review: 2026-10-13.

## 1. Absent Precondition

**Symptom.** The check iterates over subjects, asserts something about each,
and passes because there are none.

**Example.** A smoke suite runs scenarios in sequence on one simulated world.
A late scenario checks that "every worker stops work when the alarm sounds."
An earlier explosion scenario killed every worker, so the loop body never
runs and the check passes.

**Why it passes.** A universal claim over an empty set is true. Loops,
`all()`, and "no failures found" summaries all report success on nothing.
Defensive code does the same for a single subject: a check written as
`if (worker == null) return;`, or `worker?.Stopped ?? true`, accepts a
missing worker as a pass. In one suite two such checks passed with their
behavior removed, because an earlier blast had killed every subject.

**Guard.**

- Assert the precondition before acting: the subjects exist, are alive, are
  in the expected state, and number at least the minimum the claim needs.
- Create fresh fixtures inside the scenario rather than inheriting them from
  earlier ones.
- Count what was judged and fail on zero:
  `assert judged >= 3, f"only {judged} workers judged"`.

**Exposed by** removing the behavior. The check stays green, which is the
finding.

Property-based testing tools guard the same gap. Hypothesis has a
`filter_too_much` health check and raises `Unsatisfiable` when assumptions
reject too many generated examples; QuickCheck reports when it gives up after
discarding too many test cases.

## 2. Fixture Outside the Range Under Test

**Symptom.** The check passes or fails depending on where a randomly placed
fixture landed.

**Example.** A check that an area effect pulls a bystander places the
bystander at a random free cell "near" the effect. Sometimes the cell is
outside the effect radius. A companion check that "items beyond the radius
are untouched" passes trivially when nothing was placed beyond it.

**Why it passes.** The fixture never entered, or never left, the region the
claim is about. Convenience helpers hide this: a "place near" helper that
picked a random free cell within ten cells put a subject outside a ten-cell
range on some runs, and a sabotage that inverted the rule under test still
passed.

**Guard.**

- Place fixtures exactly, at distances chosen from the specification:
  inside, on the boundary, and outside.
- When placement must search for a free cell, assert the resulting distance
  before acting and log it.
- When placement is random, log the seed and the positions so that a failure
  can be replayed.

**Exposed by** shrinking the effect's range. A correct check fails for the
fixture now outside it.

## 3. Tautological Oracle

**Symptom.** The expected value is computed from the system under test, so
the check compares the system with itself.

**Example.** `armed = devices.Where(d => d.IsArmed)`, followed by
`Assert.All(armed, d => Assert.True(d.IsArmed))`. The check holds whatever
the arming logic does.

**Why it passes.** The oracle and the observation share a source. Barr and
colleagues call deciding the correct output the *oracle problem*; a
tautology sidesteps it rather than solving it.

**Guard.**

- Derive the expected value from the specification or from an independent
  computation: a constant, a hand-worked case, a brute-force reference, or a
  different code path.
- Check transitions, not states: unarmed while deploying, armed once the
  countdown starts, and the transition at the specified moment.
- Review every check whose expected value mentions the subject's own fields.

**Exposed by** breaking the flag's logic, for example by never setting it.
A tautological check stays green.

## 4. Outcome Through Another Path

**Symptom.** The expected outcome appears, but something other than the rule
under test produced it.

**Example.** A check that "a device destroyed by damage detonates" applies
heavy damage and asserts that the device is gone and an explosion occurred.
The damage was enough to destroy the device outright, and a neighboring
device's blast supplied the explosion. The detonation rule never ran.

**Why it passes.** The assertion names an outcome shared by several causes.
Overkill is a common way in: inducing a precondition with overwhelming
force. Shooting the wheels off a machine with enormous damage spilled into
its body and destroyed it outright, so a check of what the machine does
when it loses its wheels passed whether or not that rule worked.

**Guard.**

- Assert a marker unique to the rule: its own event, log line, counter or
  side effect.
- Induce preconditions precisely: exactly the damage, state or count the
  rule needs, not a margin that reaches the outcome by another route.
- Shut the other paths: use damage below the lethal threshold, remove
  neighbors that could produce the same outcome, or make the subject immune
  to the other causes.
- Record the cause where the system can report it, and assert on the cause.

**Exposed by** disabling the rule. If the outcome still appears, the check
is attributing another path's work to the rule.

## 5. Judging Before the Effect Arrives

**Symptom.** The check inspects the target in the same step that starts the
effect, before the effect has propagated.

**Example.** An expanding blast wave reaches cells over several ticks. The
check asserts "the bystander outside the radius is unharmed" immediately
after triggering, before the wave would have reached even the bystanders
inside the radius.

**Why it passes.** Nothing has happened yet, so every "unchanged" assertion
holds. The mirrored mistake, asserting a change too early, fails at random
instead.

The same error at the other end of the window: judging after the effect has
ended lets later events decide the result. A check that a creature seized by
a pull "is released from its previous behavior" ran after the pull, when the
final explosion had set the creature fleeing by another route, and so judged
the explosion rather than the pull.

**Guard.**

- Wait on a completion signal, or advance time by a bounded budget and poll
  for the condition.
- Before judging bystanders, assert that the effect reached something it
  should have reached: an inside target was harmed, so the wave has passed.
- Judge only inside the observation window the claim is about: while the
  pull runs, during the countdown. Record extremes over the window, such as
  the farthest distance reached, rather than the state at its end.
- Prefer conditions to fixed waits. Luo and colleagues found asynchronous
  waits to be the most common root cause of flaky tests.

**Exposed by** removing the effect's distance limit, so that it harms
everything. A check that judges too early still passes.

## Other Patterns

- **Fixtures that interfere.** Fixtures spawned on the same cell, or close
  enough to affect one another, can produce the expected outcome between
  themselves. Seven devices spawned on one cell destroyed one another's
  contents, and a check passed for the wrong reason. Guard: give every
  fixture its own space, and assert changes against a count taken before
  the action rather than an absolute total.
- **A measure that cannot discriminate.** A check that counts samples above
  a threshold cannot tell fast pulses from slow ones; counting upward
  crossings can. Guard: name the two cases the check must tell apart, and
  confirm that each produces a different result.
- **Assertion never reached.** An exception is caught and logged, an early
  return skips the assertion, or the test is never discovered or registered.
  Guard: count assertions or checks executed, and compare with a declared
  plan.
- **Skipped as passed.** A runner reports skipped or ignored checks in the
  same color as passes. Guard: fail the run, or report prominently, when the
  executed count is below the plan.
- **Mock instead of system.** The check asserts what a mock was told to
  return. Guard: keep real-path coverage for important behavior, as
  FieldManual's
  [test standard](../../../../standards-and-practices/core/test-development-and-mock-use.md)
  requires.
- **Fakes that encode an assumption.** A fake random source in a unit test
  produced values in `[0, 1)`, and the code under test rejected `1.0`; the
  host's real generator can return exactly `1.0`. Guard: check each fake's
  range and behavior against the real component's documentation or source.
- **Log scanning as the test.** Broken behavior rarely logs an error. In one
  project eight of nine sabotage runs logged no error at all, and the ninth
  logged one only because the sabotage code itself did. A suite that only
  scanned logs would have passed all nine. Guard: assert behavior; treat a
  clean log as a separate, additional check.
- **Log scraping that cannot fail.** A launcher counts `PASS` lines but
  treats a crash, or a missing `FAIL` line, as success. Guard: require an
  end-of-run summary line with counts, and treat its absence as failure.
- **Tolerance wider than the effect.** A threshold so loose that the
  unaffected value also satisfies it. One containment check, "residents stay
  in the settlement", used a box covering half the map, so only a
  resident's death could fail it. Guard: size the bound to the drift you
  want to catch (here, each resident within a short distance of its own
  home), and confirm that a baseline outside it fails.

## Guard Summary

| Guard | Defeats |
| --- | --- |
| Precondition assertions and judged counts | Absent preconditions, unreached assertions |
| Exact fixture placement, logged seeds | Fixtures outside the range |
| Independent oracle, transition checks | Tautologies |
| Rule-specific markers, closed alternative paths | Outcomes through another path |
| Completion signals, "effect arrived" assertions | Judging too early |
| Declared plan and a summary line | Skipped checks, crashes read as passes |

## Further Information

- Earl T. Barr et al., [The Oracle Problem in Software Testing: A
  Survey](https://doi.org/10.1109/TSE.2014.2372785), *IEEE TSE* 41(5), 2015.
- Qingzhou Luo et al., [An Empirical Analysis of Flaky
  Tests](https://doi.org/10.1145/2635868.2635920), FSE 2014: asynchronous
  waits, concurrency and test-order dependency as leading causes.
- Hypothesis, [API reference: health checks and
  `Unsatisfiable`](https://hypothesis.readthedocs.io/en/latest/reference/api.html).
- Koen Claessen and John Hughes, [QuickCheck: A Lightweight Tool for Random
  Testing of Haskell Programs](https://doi.org/10.1145/351240.351266), ICFP
  2000.
- Test Anything Protocol, [TAP version 14
  specification](https://testanything.org/tap-version-14-specification.html):
  a declared plan that lets a harness detect missing results.
