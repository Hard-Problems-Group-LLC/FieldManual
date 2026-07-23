# Standards And Practices

FieldManual separates universal operating expectations from guidance that
applies only to a particular implementation choice.

## Structure

- [`core/`](core/README.md): language- and platform-neutral standards for
  workflow, documentation, testing, safety, project state, and change
  governance
- [`languages/`](languages/README.md): language ecosystem practices and
  project-owned verification expectations
- [`technologies/`](technologies/README.md): framework, database,
  infrastructure, and platform guidance
- [`techniques/`](techniques/README.md): implementation-neutral approaches to
  recurring engineering problems
- [`guidelines/`](guidelines/README.md): concise heuristics and antipatterns

Read the core index for every substantive engagement. Load the other branches
only when they apply to the project and task.

## Normative Weight

Core documents provide FieldManual defaults. Language, technology, technique,
and guideline documents add context but do not silently override the core.
A consuming project's explicit instructions and decisions may specialize
FieldManual. Record material exceptions so later agents do not mistake drift
for policy.

FieldManual contains no language-specific verifier programs. Projects choose
and maintain the executable checks that demonstrate compliance, or adopt
separately versioned verifier submodules when those become available.
