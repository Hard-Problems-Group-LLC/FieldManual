# Time And Uncertainty Model

Status: Draft

## Purpose

Define how the repository represents exact dates, ranges, fuzzy recollection,
relative timing constraints, and confidence.

## Questions To Settle

- What time shapes are allowed?
- How should approximate memory be encoded?
- How should relative constraints be represented?
- How should confidence or certainty be expressed?
- What normalized fields are needed for sorting and viewer rendering?
- How are contradictions or unresolved ambiguities recorded?

## Initial Direction

The model should preserve uncertainty honestly and avoid false precision.
Sorting and rendering may require a best-known normalized representation, but
that should not erase the original uncertainty.
