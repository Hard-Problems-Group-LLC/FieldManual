# UI Complexity

## Guideline

Prefer small, coherent groups of choices that users can scan and distinguish.
When a visible group becomes difficult to compare, regroup it by task,
object, frequency, or workflow stage.

Do not enforce a universal item-count limit. Counts such as seven, nine, or
four are useful prompts for review, not laws of interface design.

## Evaluation Questions

- Are the choices familiar and clearly labeled?
- Can users distinguish them without remembering earlier screens?
- Are frequent and critical actions easy to find?
- Would grouping reduce search effort without hiding important choices?
- Does an added hierarchy create more navigation cost than it removes?
- Do keyboard, screen-reader, zoomed, narrow, and touch layouts remain
  understandable?
- What do usability observation and task-completion evidence show?

## Recommended Default

Start with the smallest set that supports the task. When a group approaches
roughly seven to nine peer items, review it deliberately, especially if the
items are unfamiliar or visually dense. Smaller groups may already be too
complex, while familiar, well-structured collections may remain usable above
that range.

Prefer meaningful grouping, search, filtering, or progressive disclosure over
mechanically adding submenus. Validate important information architecture
with representative users.

## Evidence and Caveat

Miller's “seven plus or minus two” concerns information-processing limits and
chunking; it is not a direct UI component limit. Later research argues for a
smaller core working-memory capacity. These findings support managing
cognitive load, but they do not determine one correct menu size.

Reviewed: 2026-07-23.

- George A. Miller, [The Magical Number Seven, Plus or Minus Two](https://doi.org/10.1037/h0043158)
- Nelson Cowan, [The Magical Number 4 in Short-Term Memory](https://doi.org/10.1017/S0140525X01003922)
- W3C, [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
