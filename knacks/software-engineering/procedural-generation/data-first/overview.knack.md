# Data-First Generation

Load this knack when code must generate complex structured content inside a
host application, such as a town, a level, a base, a dungeon or a floor plan,
and the content must satisfy rules that are hard to check by looking at it.
Companions:

- [Plan model and invariants](plan.knack.md): the
  plan's data types, determinism, the executor contract, invariant tests,
  and dropping whole units around obstacles.
- [Site selection](sites.knack.md):
  scoring candidate sites over a cost grid with summed-area tables, hard
  rejections measured against the occupied parts, and explanation functions.

Reviewed: 2026-10-13.

## Mental Model

Split generation into two programs:

1. **A planner** in a host-free library. It takes parameters, a seed and a
   snapshot of the environment, and returns a *plan*: plain data describing
   every cell, box, footprint, placement, roof and label, in plan-local
   coordinates. It calls no host API.
2. **An executor** in the host. It validates the plan against the live world,
   applies it in dependency order, and reports what it did.

This is the "functional core, imperative shell" arrangement applied to
content. The planner holds the decisions and can be tested exhaustively in
milliseconds. The executor holds the host calls and stays thin enough to
review line by line.

Benefits that compound:

- **Testable invariants.** No overlaps, reachable rooms, safe distances and
  valid data references are checked on thousands of plans without starting
  the host.
- **Determinism.** The same inputs give the same plan, so a bad layout seen
  once can be regenerated and debugged.
- **Reuse.** One planner serves several sizes and quality tiers, a preview,
  and a test fixture.
- **Diagnosis.** When a generated result looks wrong in the host, compare
  the executor's report with the plan; the fault is on one side or the
  other.
- **Executable by reviewers.** Anyone can load the built library and compute
  a plan exactly, including read-only reviewers who may not build or launch
  the host. Disputes about geometry are then settled with numbers.

The procedural content generation literature distinguishes constructive
methods, which build content in one pass, from generate-and-test methods,
which generate candidates and reject those that fail. A data-first planner
supports both: invariant checks can serve as the test step at generation
time as well as in the unit suite.

## Operating Pattern

1. **Define the plan schema** before the generator: the types, the
   coordinate convention, and which host data identifiers a plan may name.
2. **Write the invariants** as functions over a plan, then as unit tests
   that run them across many seeds and sizes.
3. **Write the planner**, deterministic for a given seed and environment
   snapshot.
4. **Choose the site** by scoring candidates over a cost grid from the live
   world (see the [site-selection
   companion](sites.knack.md)).
5. **Adapt the plan to the site**: drop whole units that collide with fixed
   obstacles, and record each drop with its reason.
6. **Execute** in dependency order: clear, terrain, structure, roofs,
   furnishings, contents, actors, labels.
7. **Report** each placement as placed or skipped with a reason, and log a
   summary.
8. **Smoke test in the host**: compare the executor's report with the plan,
   and check the properties only the host can judge, such as whether the
   host treats each room as enclosed.

## Invariants Worth Testing

- No two placements occupy the same cell unless the host allows stacking.
- Items are placed only where the cell can hold them: storage capacity,
  one-object-per-cell rules, floor and support requirements.
- Every room, door and required cell is reachable from the entrance by
  flood fill over passable cells.
- Hazards keep their minimum distances from each other and from occupied
  spaces, measured the way the host measures distance.
- The same seed and inputs produce an identical plan.
- Every referenced data identifier exists, checked against the host's own
  data files when they are available.
- Everything lies inside the site; roofs lie over enclosed rooms and within
  the host's support limits; labels are unique and on visible cells.

## Explanation Functions

Generation fails in ways that are tedious to reconstruct: no site was
acceptable, a unit was dropped, a placement was skipped. Give each decision
an explanation function that returns a tally of reasons rather than a bare
result:

```text
site search: 0 of 1,152 accepted; water 610, steep 288,
             map edge 196, fixed obstacle 58
```

Log the tally whenever a decision fails, and assert on it in unit tests. The
same output serves players' bug reports, smoke diagnostics and reviewers.

## Sharp Edges

- **Bounding boxes over-reject.** Hard rules measured against a plan's
  bounding rectangle treat empty space as occupied. In one project a single
  fixed obstacle in an empty corner of a settlement's bounding box rejected
  every candidate site on some maps. Measure against the parts actually
  occupied.
- **The host has rules the plan does not model.** Terrain that refuses a
  building, placement restrictions, support rules for roofs. The executor
  must report each refusal, not silently repair it; the report then shows
  which rule to add to the planner.
- **Hidden nondeterminism.** Hash-ordered sets, unsorted directory listings,
  wall-clock time, and runtime random generators whose sequences may change
  between versions all break reproducibility.
- **Partial execution.** A host error midway leaves half a structure. Order
  execution so that each unit completes before the next starts, and make the
  report say exactly where execution stopped.
- **Side effects of placed content.** Generated storage, jobs, lights or
  power can attract the player's own actors and items from far away. Plan
  ownership and scope explicitly, and smoke test the interaction.
- **Plans coupled to host types.** A planner that references host types
  cannot be tested outside the host. Use identifiers and plain values;
  convert in the executor.

## Review Checklist

- The planner references no host type and runs in unit tests.
- Every invariant above that applies is a test run across many seeds and
  sizes, and each was seen to fail under sabotage.
- Determinism is tested by generating twice and comparing serialized plans.
- Data identifiers are checked against the host's data files where
  available, and the test says clearly when it skips that check.
- Site rules are measured against occupied parts, not bounding boxes.
- Dropped units, skipped placements and rejected sites are logged with
  reasons.
- The executor's report is compared with the plan in an in-host smoke check.

## Further Information

- Noor Shaker, Julian Togelius and Mark J. Nelson, [*Procedural Content
  Generation in Games*](https://www.pcgbook.com/), Springer, 2016; see
  [chapter 3, constructive generation](https://www.pcgbook.com/chapter03.pdf).
- Julian Togelius et al., [Search-Based Procedural Content Generation: A
  Taxonomy and Survey](https://doi.org/10.1109/TCIAIG.2011.2148116), *IEEE
  TCIAIG* 3(3), 2011: constructive versus generate-and-test.
- Gary Bernhardt, [Functional Core, Imperative
  Shell](https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell),
  Destroy All Software screencast.
- Koen Claessen and John Hughes, [QuickCheck: A Lightweight Tool for Random
  Testing of Haskell Programs](https://doi.org/10.1145/351240.351266), ICFP
  2000: properties checked over many generated inputs.
- FieldManual, [In-Host Smoke
  Testing](../../testing/in-host-smoke/overview.knack.md).
