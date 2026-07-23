# Documentation

## Purpose

Treat documentation as part of the delivered system. It should help a future
reader understand what exists, why it exists, how to use it safely, and where
the authoritative rules live.

## Default Form

Use Markdown for maintained prose unless a machine-consumed format or an
established platform convention requires something else.

Each maintained document should make its purpose and scope clear near the
beginning. Add ownership, status, or a review date when the content is
volatile, normative, or operationally important.

## Source-of-Truth Discipline

- Give each normative rule one canonical home.
- Link to canonical material instead of copying it into multiple documents.
- Mark generated indexes and summaries as derived.
- Record deliberate exceptions near the affected rule or in a decision log.
- Update documentation in the same change as the behavior or contract it
  describes.

## Source Documentation

Document public interfaces, durable contracts, invariants, significant side
effects, failure behavior, and non-obvious lifecycle constraints.

Do not require comments or docstrings for every private helper merely to
satisfy a quota. Names and structure should explain straightforward code.
Comments should explain intent, tradeoffs, hazards, and reasons that are not
obvious from the implementation.

## Evidence and References

- Prefer primary, authoritative, and durable sources.
- Link directly to the material that supports a claim.
- Distinguish sourced fact, project policy, inference, and analogy.
- Add a review date to guidance that depends on changing products, standards,
  laws, or versions.
- If sources disagree, state the uncertainty and identify the project's
  chosen operating default.

## Maintenance Review

Review documentation for:

- agreement with current behavior;
- clear authority and audience;
- working internal links after moves;
- examples that use safe, generic values;
- absence of secrets or unnecessary identifying information;
- obsolete instructions and duplicated rules; and
- readable structure and concise prose.

Executable documentation checks belong to consuming projects or future
verifier submodules.
