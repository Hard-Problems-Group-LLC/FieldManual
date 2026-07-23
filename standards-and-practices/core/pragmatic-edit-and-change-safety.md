# Pragmatic Edit and Change Safety

## Purpose

Choose an edit method based on the shape and risk of the change. Safety comes
from bounded scope, preservation of unrelated work, reviewable results, and
appropriate validation.

## Before Editing

- Confirm the active project and intended target.
- Inspect existing state and applicable instructions.
- Identify user-owned or concurrent changes that must be preserved.
- Resolve ambiguous destinations before writing.
- For destructive, privileged, or cross-project actions, obtain the required
  explicit authority first.

## Choosing an Edit Method

Prefer a patch-style edit for a small, localized manual change.

Whole-file records, generated material, and explicit mechanical
transformations may use a named-file rewrite, formatter, generator, or
codemod when that makes the affected scope clearer and safer.

Any mechanical transformation should have:

- an explicit file set or narrow discovery rule;
- deterministic behavior where practical;
- a way to review the resulting change; and
- a recovery path if it stops partway through.

Avoid broad shell transformations whose affected paths or escaping behavior
are difficult to review.

## Destructive and Generated Changes

- Prefer recoverable actions where practical.
- Never use an unresolved variable, broad wildcard, repository root, user
  home, or filesystem root as a destructive target.
- Validate exact targets before deletion or replacement.
- Preserve the authoritative source for generated output.
- Do not hand-edit generated output without also changing its source, unless
  the exception is explicit and temporary.

## After Editing

Inspect the complete change set, including unexpected files and metadata.
Validate in proportion to risk and document any checks that could not run.

If an edit mechanism repeatedly fails, stop retrying blindly. Record the
failure, change strategy, or ask for direction.
