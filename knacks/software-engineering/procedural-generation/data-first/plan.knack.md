# Data-First Generation: Plan Model and Invariants

Load this companion to the
[data-first generation overview](overview.knack.md)
when you design the plan's data types, make generation deterministic, write
invariant tests, write the host-side executor, or adapt a plan to obstacles.

Reviewed: 2026-10-13. Sketches are Python; the same shapes work in any
language with value types and collections.

## Plan Types

Keep the plan plain: values, identifiers and collections, with no host
types.

| Type | Holds | Notes |
| --- | --- | --- |
| `Cell` | `x`, `y` | Plan-local integer coordinates |
| `Box` | `x0`, `y0`, `x1`, `y1` | Half-open: `x0 <= x < x1`; say so once |
| `Footprint` | set of cells, or a box plus a rotation | What a placement occupies |
| `Placement` | data id, cell, rotation, material, owner, tags | One host object |
| `Unit` | name, footprint, placements, required flag | Stands or falls as a whole |
| `Terrain` | cells, terrain id | Floors, paths, cleared ground |
| `Roof` | cells | Only over enclosed rooms |
| `Label` | text, cell | Signs, map labels, names |
| `Plan` | units, terrain, roofs, labels, origin, seed | The whole result |

Conventions to fix early:

- **One coordinate system.** Plans use local coordinates with the origin at a
  stated corner. The executor applies the site offset and any rotation.
- **Half-open boxes.** State the convention once and use it everywhere,
  including in site selection. Off-by-one disagreements between planner and
  executor are common and tedious.
- **Identifiers, not objects.** A placement names the host's data identifier
  as a string. The executor resolves it, and a test checks that it exists.
- **Units as the unit of failure.** A building, a room with its contents, or
  a fenced pen is one unit. Obstacle handling and execution treat it whole.

## Determinism

The same parameters, seed and environment snapshot must yield the same
plan. Sources of hidden variation:

- **Shared or global random generators.** Pass an explicit generator into
  every stage. Derive a sub-seed per stage, for example from a stable hash
  of the seed and the stage name, so that changing one stage does not
  reshuffle the others.
- **Runtime generator changes.** Python guarantees only that `random()`
  reproduces its sequence for a given seed under a compatible seeder; most
  other algorithms and seeding functions may change between Python versions.
  .NET warns that `Random` may produce different sequences on different .NET
  versions. If plans must reproduce across runtime versions, ship a small
  generator of your own (for example SplitMix64 or PCG) and test its output
  against fixed vectors.
- **Unordered collections.** Hash sets, dictionaries keyed by objects, and
  directory listings have no stable order. Sort before iterating whenever
  order affects the result.
- **Salted hashes.** Python salts `str` and `bytes` hashes per process, so
  `hash(name)` differs between runs. Use a stable hash such as CRC-32 or a
  cryptographic digest for seeds.
- **Floating point.** Keep geometry in integers. Where floats are
  unavoidable, round at well-defined points.
- **Time and environment.** No wall-clock time, locale-dependent formatting,
  or machine-specific paths in the planner.

Test determinism directly: generate twice from the same inputs, serialize
both plans canonically, and compare.

## Look Before Testing

Render the plan as text before writing invariants. A few lines of code that
print one character per cell (`#` wall, `+` door, `.` floor, letters for
furniture) show overlaps, gaps and mis-rotations at once, and suggest which
invariants matter. Extract the list of data identifiers from a generated
plan rather than writing it from memory.

```text
##########   ######
#..b..b..#   #.cc.#
#........+...+....#
#..t..t..#   ######
####+#####
```

## Invariant Tests

Write each invariant as a function that returns its violations, then run it
over many seeds and every supported size. Report the failing seed.

```python
def overlaps(plan):
    seen, bad = {}, []
    for unit in plan.units:
        for p in unit.placements:
            for c in p.cells():
                if c in seen and not stackable(seen[c], p):
                    bad.append((c, seen[c].data_id, p.data_id))
                seen.setdefault(c, p)
    return bad

def test_no_overlaps():
    for seed in range(500):
        for size in SIZES:
            plan = make_plan(size, seed)
            assert not overlaps(plan), (seed, size, overlaps(plan)[:3])
```

The invariants:

- **No overlaps**, except where the host allows stacking.
- **Capacity.** Items only where the cell allows them: storage capacity,
  one object per cell, floor or support requirements, no items on walls or
  doors.
- **Reachability.** A flood fill (breadth-first search) from the entrance
  over passable cells reaches every room, every door, and every cell an
  actor must stand on to use a placement.
- **Distances between hazards.** Explosive storage, fire sources and similar
  hazards keep their minimum distances from each other and from occupied
  rooms, measured with the metric the host uses (Euclidean, Chebyshev or
  Manhattan).
- **Determinism**, as above.
- **Data identifiers exist.** Every identifier appears in the host's data.
  When the host's data files are available on the test machine, load them
  and check, including inherited or abstract definitions. When they are
  absent, skip with a visible message; never pass silently.
- **Bounds, roofs and labels.** Everything inside the plan's extent; roofs
  only over enclosed rooms and within the host's support limits; labels
  unique and placed on visible cells.

```python
from collections import deque

def reachable(passable, start):
    """Cells reachable from start by 4-neighbour steps over passable cells."""
    h, w = len(passable), len(passable[0])
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (0 <= nx < w and 0 <= ny < h and passable[ny][nx]
                    and (nx, ny) not in seen):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen
```

Prove the invariant tests can fail: break the planner (overlap two units,
wall off a room, misspell an identifier) and watch each test catch it, as
[Proving Checks Can
Fail](../../testing/proving-checks/overview.knack.md)
describes.

## Obstacles: Drop Whole Units

A site chosen in a live world can still hold fixed obstacles: rock, water,
indestructible features. When a unit's footprint meets one:

- **drop the whole unit**, not individual cells or items, because a
  building with a missing wall or a pen with a gap is worse than no
  building;
- **never drop a required unit**; reject the site instead, and let site
  selection try the next candidate;
- **re-run the invariants** on the adapted plan, because dropping a unit can
  disconnect paths or orphan a label; and
- **record each drop** with the unit, the obstacle, and its position.

Obstacles that do no harm can stay. A feature that cannot be removed, in
empty ground between units, may even add character; the rule is about
collisions with units, not about every obstacle inside the site.

## Executor Contract

The executor is the only code that touches the host:

1. **Validate** the plan against the live world: the site is still clear,
   identifiers resolve, the plan's invariants hold.
2. **Apply in dependency order**: clear the ground, lay terrain, build
   structure, roof, furnish, add contents, add actors, add labels. Complete
   each unit before starting the next.
3. **Report every placement** as placed, or skipped with the host's reason.
4. **Never repair the plan silently.** If the host refuses something, report
   it; the report shows which host rule the planner needs to learn.
5. **Return the executed plan**: the plan as actually built, after dropped
   units and refusals.

Test what was actually built. In one project the in-host check compared the
world with the full plan, while the executor had dropped buildings around an
obstacle, so the check was judging buildings that were never meant to exist.
The executor now returns the executed plan, and the smoke check uses it.

## Further Information

- Python, [random: notes on
  reproducibility](https://docs.python.org/3/library/random.html#notes-on-reproducibility).
- Python, [object.\_\_hash\_\_](https://docs.python.org/3/reference/datamodel.html#object.__hash__):
  per-process salting of `str` and `bytes` hashes.
- Microsoft, [Supplemental API remarks for
  System.Random](https://learn.microsoft.com/en-us/dotnet/fundamentals/runtime-libraries/system-random):
  sequences may differ across .NET versions.
- Amit Patel, Red Blob Games, [Introduction to the A\*
  Algorithm](https://www.redblobgames.com/pathfinding/a-star/introduction.html):
  breadth-first search on grids, with interactive diagrams.
- Koen Claessen and John Hughes, [QuickCheck: A Lightweight Tool for Random
  Testing of Haskell Programs](https://doi.org/10.1145/351240.351266), ICFP
  2000.
- Noor Shaker, Julian Togelius and Mark J. Nelson, [*Procedural Content
  Generation in Games*, chapter 3](https://www.pcgbook.com/chapter03.pdf):
  constructive generation of dungeons and levels.
