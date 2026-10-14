# Proving Checks Can Fail: Sabotage Runs

Load this companion to the
[overview](overview.knack.md) when you are about to
break code on purpose to prove a check, prove a regression check against the
code before a fix, or decide whether a mutation-testing tool can do the work.

Source review: 2026-10-13. Mutation tools change quickly; check each tool's
current documentation for supported languages and options.

## Choosing the Sabotage

Ask what bug the check exists to catch, and introduce that bug. The standard
mutation operators make a useful menu:

| Sabotage | Typical form | Good for checks of |
| --- | --- | --- |
| Remove the effect | Comment out the call that applies it | Effects, side effects |
| Invert the decision | `if (ready)` becomes `if (!ready)` | Branches, gates |
| Short-circuit | `return` before the work, or return a constant | Calculations, pipelines |
| Change a constant | Radius 5 becomes 2; delay 120 becomes 0 | Ranges, timing |
| Disable a guard | Drop a precondition test | Safety rules, validation |
| Redraw a value | Re-roll a stored random choice on every call | Persistence, determinism |
| Swap two values | Exchange arguments or thresholds | Ordering, mapping |

Prefer the sabotage closest to a plausible real defect. A check of "a
stored choice never changes" is proved by re-rolling the choice on every
call, not by deleting the feature, because deleting the feature also fails
many unrelated checks and proves less about this one.

## Doing It Safely

1. **Isolate.** Sabotage in your own worktree or on a throwaway branch, or at
   a moment when no other agent builds or tests from the same tree. Other
   writers must never run against your broken code.
2. **Save.** If the files to break also hold uncommitted work, copy them
   aside first. `git restore` would discard that work along with the break.
3. **Mark.** Put a unique token on every sabotaged line, for example
   `// SABOTAGE-CHECK`. One search then finds every break.
4. **Build, and confirm the build.** Check the build's exit status, and check
   that the built artifact is newer than every source file, or rebuild from
   clean. In one project a sabotage edit broke compilation; the build failed
   quietly, the smoke run loaded the previous binary, and the sabotage
   "passed".
5. **Run.** Run the narrowest command that includes the target check.
6. **Restore.** Use `git restore -- <path>` for only the files you broke, or
   copy the saved files back, then confirm that the diff against the saved
   state is empty. Never restore the whole tree in a shared checkout.
7. **Search before committing.** Search the tree and the staged diff for the
   token. Treat a hit as a release blocker.
8. **Rerun green.** The restored code must pass. In environments with known
   flakiness, require two consecutive clean runs.

Never commit a sabotage, even to a private branch that "will be squashed".
Branches outlive intentions.

## A Sabotage Harness

When sabotage runs become routine, replace hand edits with a small script:

- a registry of named breaks, each a file, the exact original text, and its
  replacement;
- `apply <name>` replaces the text exactly once and fails if the original is
  absent or appears more than once, so a stale registry cannot break the
  wrong line;
- `save` and `restore` copy the affected files aside and back; and
- a run script that builds, confirms the build, runs the suite, and prints
  the summary and the targeted checks' lines.

Named breaks make results comparable between runs and let a reviewer rerun
any of them. Keep the harness and its registry out of the shipped product.

## Batching Expensive Runs

When each run is expensive, such as an in-host smoke run that takes minutes,
several sabotages can share one run if they cannot mask one another:

- choose breaks in independent code paths and independent scenarios;
- avoid any break that crashes the runner or ends a scenario early, because
  every later check in that scenario then goes unjudged;
- confirm afterward that every targeted check reported a result, using the
  run's summary counts; and
- if one break hides another, split them into separate runs.

A run that breaks one behavior on its own sometimes exposes a second,
unrelated weakness. In one case, a run that broke only one feature's
reaction also showed that a blast check had judged its target before the
blast wave arrived. Read every failure in a sabotage run, not only the one
you expected.

## Reading the Result

A sabotage run proves a check only when:

- the sabotaged code is what ran, as the build check above confirms;
- the targeted check failed;
- its message names the claim and shows measured and expected values; and
- the failure arises from the assertion, not from a crash, a timeout, a
  compile error, or a missing fixture.

Do not expect the log to show the break. Behavioral sabotage almost never
produces an error message; the assertions must catch it.

Record each result:

```text
Sabotage: stored reaction re-rolled on every query (ReactionTable.Get)
Target:   "each subject keeps its first reaction"
Result:   FAIL: subject 7 reaction changed from Hesitate to Flee at tick 30
Restored: yes; rerun PASS (2 of 2 clean runs)
```

If the targeted check stayed green, the check is vacuous or tests something
else. Use the [vacuous checks](vacuity.knack.md)
patterns to find out which, fix the check, and sabotage again.

## Red-First Regression Checks

A regression check for a bug must fail on the code that has the bug. Two
ways to arrange it:

- **Check first.** Write the check, run it on the unfixed code, see it fail
  with the reported symptom, then fix.
- **Check against the old code.** If the fix already exists, run the new
  check against the parent of the fix:

  ```sh
  git worktree add --detach ../example-repo-before <fix-commit>^
  # copy the new check into ../example-repo-before, build and run it there
  git worktree remove --force ../example-repo-before
  ```

  The check must fail there and pass on the fixed code.
- **Swap the old files in briefly.** For files you own,
  `git restore --source=<fix>^ -- <path>` writes the pre-fix version in
  place through Git's own filters, and `git stash push -- <paths>` stashes
  only the named paths. A new untracked file is not stashed; move it
  aside. Avoid `git show <fix>^:<path> > <path>`: it bypasses line-ending
  conversion, and on Windows PowerShell 5.1 the redirection writes UTF-16
  (see [Git history for agents](../../../windows/git/history.knack.md)).
  Restore and confirm the diff before anything else runs.

The failure must match the bug report, and the scenario must reproduce the
report's conditions. In one project, two regression checks first passed on
the old code. One spawned all its fixtures on a single cell, where they
interfered with one another. The other targeted a crash reported from a
live session (a null reference deep inside the host when a certain
projectile landed near a creature) but used a kind of projectile that
creatures do not react to. Once it fired the reported kind among creatures,
it failed on the old code with the reported exception and passed on the
fixed code. A first draft of the fix called a base-class method that the
host implemented as "not implemented", and the same scenario caught that
too.

## Mutation-Testing Tools

Where a tool exists for the language and test runner, automated mutation
testing does the same job at scale. It generates mutants, runs the suite on
each, and reports survivors, which are changes that no check noticed.

- [PIT](https://pitest.org/): the JVM.
- [Stryker](https://stryker-mutator.io/): JavaScript and TypeScript, C#, and
  Scala.
- [mutmut](https://github.com/boxed/mutmut): Python.
- [cargo-mutants](https://mutants.rs/): Rust.

Google reports running diff-based mutation analysis during code review. It
mutates only changed lines with statement coverage, skips lines it judges
uninteresting ("arid"), and limits the number of mutants per review so that
the survivors shown are actionable. Copy the scoping: mutate the change, not
the whole code base.

Hand-made sabotage remains necessary where tools cannot reach: checks that
run inside a closed host application, smoke tests driven by a launcher,
validators of data files, generated-content invariants, and gates in an
agent workflow. Those are also the checks most often written once and
trusted forever.

For a static validator, sabotage the input rather than the code: keep a
control copy of the data with one seeded mistake per rule (an unknown
field, a bad enumeration value, a dangling reference, a missing asset), and
require the validator to report every one. Add a seeded mistake whenever the
validator gains a rule.

## Briefing Agents

Put the requirement and its evidence format in the brief:

```text
For each new or changed check:
1. State the claim it proves in one sentence.
2. Break the behavior it guards (not the check). Mark it SABOTAGE-CHECK.
3. Build; confirm the build succeeded and the artifact is newer than the
   sources. Run; the check must fail with a message naming the claim.
4. Restore, confirm the diff is empty, rebuild, rerun; it must pass.
5. Report: sabotage, target check, failure message, restore confirmation.
Never commit a sabotage. Never sabotage in a tree other agents are using.
```

Reviewers then check that every new check has an entry, that each sabotage
targets the stated claim, and that no token remains.

## Further Information

- Martin Fowler, [*Refactoring*, 2nd
  ed.](https://martinfowler.com/books/refactoring.html), chapter 4: injecting
  a fault to see a test fail.
- Yue Jia and Mark Harman, [An Analysis and Survey of the Development of
  Mutation Testing](https://doi.org/10.1109/TSE.2010.62), *IEEE TSE* 37(5),
  2011: mutation operators and their history.
- Goran Petrović and Marko Ivanković, [State of Mutation Testing at
  Google](https://doi.org/10.1145/3183519.3183521), ICSE-SEIP 2018; Goran
  Petrović et al., [Practical Mutation Testing at Scale: A View from
  Google](https://doi.org/10.1109/TSE.2021.3107634), *IEEE TSE*, 2022.
- Git, [git-worktree](https://git-scm.com/docs/git-worktree) and
  [git-restore](https://git-scm.com/docs/git-restore).
- FieldManual, [Shared-Checkout
  Subagents](../../../AI/agent-orchestration/shared-checkout/overview.knack.md).
