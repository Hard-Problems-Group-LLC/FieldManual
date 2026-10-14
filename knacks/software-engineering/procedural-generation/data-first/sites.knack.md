# Data-First Generation: Site Selection

Load this companion to the
[data-first generation overview](overview.knack.md)
when a generated plan must be placed in an existing world: choosing where a
settlement, base or room fits, scoring candidate sites, rejecting unsafe
ones, and explaining why a search found nothing.

Reviewed: 2026-10-13. Sketches are Python and were checked against a
brute-force sum on random grids.

## The Problem

The world is a grid of cells. The plan occupies some of them, its *parts*,
relative to an origin. Site selection chooses an origin that:

- avoids hard blockers (impassable or protected cells, map edges, features
  that must not be touched) under every part;
- keeps keep-away distances from hazards and from other content; and
- minimizes a cost, such as the work to clear the ground, the roughness of
  the terrain, or the distance from where the player is likely to look.

Checking each candidate cell by cell costs the plan's area per candidate.
With thousands of candidates and large plans this is slow enough to stall a
frame. Summed-area tables make each rectangle sum constant-time.

## Summed-Area Tables

Crow introduced summed-area tables for texture mapping in 1984; Viola and
Jones popularized the same structure as the *integral image*. For a grid
`g`, the table `S` holds the sum of every cell above and to the left:

```text
S[y][x] = sum of g[j][i] for all j < y and i < x
sum over box [x0, x1) x [y0, y1) =
    S[y1][x1] - S[y0][x1] - S[y1][x0] + S[y0][x0]
```

```python
def summed_area(grid):
    """Return an (h+1) x (w+1) table; row 0 and column 0 are zeros."""
    h, w = len(grid), len(grid[0])
    s = [[0] * (w + 1) for _ in range(h + 1)]
    for y in range(h):
        row = 0
        for x in range(w):
            row += grid[y][x]
            s[y + 1][x + 1] = s[y][x + 1] + row
    return s

def box_sum(s, x0, y0, x1, y1):
    """Sum of cells with x0 <= x < x1 and y0 <= y < y1."""
    return s[y1][x1] - s[y0][x1] - s[y1][x0] + s[y0][x0]
```

- **Pad by one.** The extra zero row and column remove every edge case.
- **Build once per grid**, in time proportional to its area; each query is
  then four lookups.
- **One table per layer.** Keep a cost table, and a count table for each
  kind of hard blocker, so that "any blocker under this part" is
  `box_sum(...) > 0`.
- **Use integers.** Integer sums are exact; floating-point sums of large
  grids lose precision in the subtraction. Check the integer width against
  the largest possible total.

Test the table against a brute-force sum on many random grids and boxes.
The brute force is an independent oracle, short enough to trust by reading.

## Measure Against the Parts

Score and reject using the cells the plan actually occupies, not its
bounding rectangle:

```python
def site_cost(origin, parts, cost_sat, blocker_sat):
    ox, oy = origin
    total = 0
    for (x0, y0, x1, y1) in parts:            # plan-local boxes
        box = (ox + x0, oy + y0, ox + x1, oy + y1)
        if box_sum(blocker_sat, *box) > 0:
            return None, "blocked"
        total += box_sum(cost_sat, *box)
    return total, "ok"
```

A plan with an irregular outline, such as an L-shaped settlement, scattered
buildings or a ring of pens, leaves much of its bounding box empty. Rules
measured against the box treat that empty space as occupied. In one project
a single fixed obstacle in an empty corner of a settlement's bounding box
rejected every candidate site on some maps. Two agents building the planner
and its host-side caller in parallel each found the same flaw independently.

The cost per candidate becomes proportional to the number of parts, not
their area. Describe the parts as a short list of boxes; merge adjacent
cells into boxes when the plan is built.

## Keep-Away Distances

To keep every part at least `d` cells from a hazard, either grow each part's
box by `d` before the blocker query, or grow the hazard cells by `d` into a
separate blocker layer before building its table. Growing a box gives a
square (Chebyshev) margin. For a Euclidean rule, follow the box test with an
exact distance check on the few candidates that pass, or dilate the hazard
layer with a disc.

Use one helper for each safety rule. If the site search, a demonstration
placer and a test each measure "at least `d` from the settlement" their own
way, they will disagree near the boundary. In one project the site search
measured from the parts while a demonstration's placement filter measured
from the bounding box plus a margin, and a demonstration silently
disappeared on some maps. A single public function, called from every
place that enforces the rule, fixed it.

## Choosing Among Candidates

- **Enumerate deterministically**: a fixed stride over the allowed window,
  in a fixed order.
- **Break ties by position** after cost, so that equal costs never depend on
  iteration order.
- **Prefer a window first.** Search where the result should appear, such as
  near the player's view, then widen in documented steps to larger windows
  and finally the whole map.
- **Reject, then rank.** Apply hard rejections first and rank only the
  survivors.
- **Keep the top few**, not only the best, when a later step (unit drops,
  a host refusal) may still fail on the chosen site.

## Explanation Functions

Every search that can fail needs a function that explains the failure:

```python
from collections import Counter

def explain(candidates, parts, layers):
    tally = Counter()
    for origin in candidates:
        tally[first_rejection(origin, parts, layers) or "accepted"] += 1
    return tally
```

```text
site search (window 1 of 3): 0 of 1,152 accepted;
  water 610, steep 288, map edge 196, fixed obstacle 58
```

- Name each rejection by the rule that fired first, in a fixed rule order,
  so that tallies are comparable.
- Log the tally whenever the search fails or falls back to a wider window.
- Assert on tallies in unit tests: on a fixture grid, the expected reasons
  and counts appear.
- Count a site skipped for lack of room separately from a pass, so that a
  test suite cannot report green when nothing was built.

## Testing Site Selection

- Synthetic grids with known answers: an open field (any site), a single
  blocker in an empty corner of the bounding box (still accepted), a
  blocker under a part (rejected), a narrow corridor (one site).
- Property tests: every accepted site, checked cell by cell without the
  tables, has no blocker under any part and meets every distance.
- Determinism: the same grid and seed choose the same site.
- Performance: a timing check on the largest supported grid and plan, with
  a generous budget.

## Further Information

- Franklin C. Crow, [Summed-Area Tables for Texture
  Mapping](https://doi.org/10.1145/800031.808600), SIGGRAPH 1984.
- Paul Viola and Michael Jones, [Rapid Object Detection Using a Boosted
  Cascade of Simple Features](https://doi.org/10.1109/CVPR.2001.990517),
  CVPR 2001: the integral image.
- Wikipedia, [Summed-area
  table](https://en.wikipedia.org/wiki/Summed-area_table): a short
  derivation with diagrams.
- Julian Togelius et al., [Search-Based Procedural Content Generation: A
  Taxonomy and Survey](https://doi.org/10.1109/TCIAIG.2011.2148116), *IEEE
  TCIAIG* 3(3), 2011.
- FieldManual, [In-Host Smoke Testing:
  Flakiness](../../testing/in-host-smoke/flakiness.knack.md):
  explanation functions in smoke diagnostics.
