# Proving Checks Can Fail

Load this knack when you, or an agent you direct, write or review a new test,
smoke check, validator, assertion or gate; when a bug fix needs a regression
check; or when a report says "all checks pass" and you must decide what that
proves. Load the companions for detail:

- [Vacuous checks](vacuity.knack.md): the ways a
  check passes without observing anything, each with a guard.
- [Sabotage runs](sabotage.knack.md): how to
  break behavior safely, read the result, prove regression checks against
  the old code, and use mutation tools.

Source review: 2026-10-13. The practice is long established; tool links and
the agent-specific advice should be rechecked as tools change.

## Mental Model

A check is evidence only if it could have failed. A green result proves that
the check ran and that its assertion held on that run. It does not prove that
the check looked at the behavior it is named after.

Checks pass vacuously more often than authors expect. In one long project,
deliberate breakage found checks of five kinds that would have passed with
the behavior missing:

- a check whose precondition was absent: every subject had died in an
  earlier scenario, so "each subject reacts" held for an empty set;
- a fixture placed at random, sometimes outside the range under test;
- a check that compared a flag with a list derived from the same flag;
- damage that killed the subject through another path, so the rule under
  test never ran but its outcome appeared anyway; and
- a check that judged the target before the effect had reached it.

Each had been written carefully, reviewed, and seen to pass. None had been
seen to fail.

The remedy is old. Martin Fowler writes in *Refactoring* that he likes "to
see every test fail at least once" when he writes it, and that his favorite
way is "to temporarily inject a fault into the code." Mutation testing
automates the same idea: DeMillo, Lipton and Sayward proposed seeding small
faults, and a test suite that kills the resulting mutants is stronger
evidence than one that merely covers the lines. Later studies found mutant
detection correlated with real-fault detection, and Google runs mutation
analysis on changes during code review.

## Two Practices

**Sabotage runs for new checks.** After writing a check, break the behavior
it guards, briefly and on purpose. Run the check and confirm that it fails,
and fails for the stated reason. Restore the behavior and confirm that it
passes again. Record the sabotage and the observed failure.

**Red-first regression checks.** When fixing a bug, write the check before
the fix, or run it against the code from before the fix. It must fail with
the symptom the bug report describes. Then apply the fix and watch it pass.
A regression check that never saw the bug may test something else.

## Workflow

1. **State the claim.** Write down which behavior the check proves, in one
   sentence: "a projectile that hits a primed device starts its countdown
   within two ticks."
2. **Write the check with guards.** Assert the preconditions it depends on
   (subjects exist and are alive, fixtures are in range, the effect arrived),
   so that a missing precondition fails loudly instead of passing quietly.
3. **Choose a sabotage that targets the claim.** Remove the effect, invert the
   decision, change the constant, or skip the call. Choose what a real bug in
   this behavior would look like.
4. **Build, run and read.** Confirm the sabotaged code was built and is what
   ran. The check must fail, with a message naming the claim. A crash, a
   compile error, or a different check failing is not proof.
5. **Restore and rerun.** The tree must match its state before the sabotage,
   and the check must pass again.
6. **Record the evidence** in the commit message, the change description, or
   the agent's final report: the sabotage, the check that failed, the
   message.

## Why This Matters More With Agents

AI agents write many checks quickly, and they are asked to make checks pass.
A check that passes on its first run is the easiest route to a green report,
and agents rarely volunteer that a check was never seen to fail. Make the
evidence part of the brief: "For each new check, break the behavior it
guards, confirm the check fails, restore, and report the sabotage and the
failure message." Reviewers then verify that the evidence exists and that
the sabotage really targeted the claim.

The [staged verification](../../../AI/agent-orchestration/staged-verification.knack.md) ratchet turns
each defect found in deep review into a cheap check. A sabotage run is how
you know the new check would have caught that defect. In
[adversarial review](../../../AI/agent-orchestration/adversarial-review/overview.knack.md),
test rigor is a review dimension in its own right.

## Sharp Edges

- **Breaking the test instead of the code** proves only that assertions can
  fail. Break the behavior under test.
- **Sabotage that masks another.** When several sabotages share one expensive
  run, one can stop a scenario before another check runs. Choose breaks in
  independent paths and confirm that every targeted check reported.
- **Failing for the wrong reason.** If the sabotage crashes the run, the
  check never judged anything. Read the message.
- **Passing on the old binary.** A sabotage that breaks compilation leaves
  the previous build in place, and a run against it "passes". Confirm the
  build succeeded and the artifact is newer than the sources.
- **Leaving sabotage behind.** Mark sabotaged lines with a unique token,
  search for it before committing, and restore by path.
- **Sabotage in a shared tree.** Other agents may build or test against your
  broken code. Sabotage in a worktree, or when no one else is running checks
  (see [Shared-Checkout
  Subagents](../../../AI/agent-orchestration/shared-checkout/overview.knack.md)).
- **A flaky check proves little either way.** A check that fails at random
  will "catch" any sabotage. Stabilize it first, then prove it.
- **Over-reach.** Not every assertion needs its own sabotage run. Prove the
  checks that carry a claim: new behavior, bug fixes, gates, and anything a
  report will cite.

## Review Checklist

- Each new check states the behavior it proves.
- Preconditions are asserted, not assumed: non-empty sets, live subjects,
  fixtures in range, effects arrived.
- The expected value comes from the specification or an independent
  computation, not from the system under test.
- A sabotage run targeted the claim, the check failed with the expected
  message, and the restored code passed.
- Regression checks were seen to fail on the code before the fix.
- No sabotage marker remains in the tree or the history.
- Agent reports include the sabotage evidence, and a reviewer checked it.

## Further Information

- Martin Fowler, [*Refactoring*, 2nd
  ed.](https://martinfowler.com/books/refactoring.html), chapter 4,
  "Building Tests": seeing each test fail by injecting a fault.
- Richard A. DeMillo, Richard J. Lipton and Frederick G. Sayward, [Hints on
  Test Data Selection: Help for the Practicing
  Programmer](https://doi.org/10.1109/C-M.1978.218136), *Computer* 11(4),
  1978: the origin of mutation testing and the coupling effect.
- Yue Jia and Mark Harman, [An Analysis and Survey of the Development of
  Mutation Testing](https://doi.org/10.1109/TSE.2010.62), *IEEE TSE* 37(5),
  2011.
- René Just et al., [Are Mutants a Valid Substitute for Real Faults in
  Software Testing?](https://doi.org/10.1145/2635868.2635929), FSE 2014.
- Goran Petrović and Marko Ivanković, [State of Mutation Testing at
  Google](https://doi.org/10.1145/3183519.3183521), ICSE-SEIP 2018.
- Earl T. Barr et al., [The Oracle Problem in Software Testing: A
  Survey](https://doi.org/10.1109/TSE.2014.2372785), *IEEE TSE* 41(5), 2015.
- FieldManual, [Test Development and Mock
  Use](../../../../standards-and-practices/core/test-development-and-mock-use.md).
