# Knack Authoring Guide

Knacks are meant to be loaded whole for a concrete task, then summarized when
active context must shrink. That model drives their size, naming, sourcing,
and maintenance.

## Size Guidance

An overview should usually stay near 1,250 words. That is enough to explain a
mental model, practical workflow, sharp edges, and references without turning
the document into a full manual.

An API reference may approach 2,500 words. Split large APIs by stable
subsystem when doing so makes selection and loading clearer.

Treat 5,000 words as a practical maximum for one knack file. Prefer a
well-linked fileset over a document that is difficult to load, review, or
refresh.

These are design targets, not automated gates. A shorter knack is preferable
when it solves the task without losing essential context.

## Naming and Layout

Use `<topic>.knack.md` when one document is sufficient.

For a larger fileset:

- use `<topic>.overview.knack.md` as the conceptual entry point;
- begin API companions with `<topic>.api`;
- append a stable language tag when the API is language-specific, such as
  `.C`, `.CPP`, or `.Python`; and
- insert stable subsystem tokens between `.api` and the language tag when an
  API needs further division.

Examples:

- `ansi.knack.md`
- `curses.api.C.knack.md`
- `curses.api.Python.knack.md`
- `renderer.api.layout.CPP.knack.md`

When a fileset needs its own container, use a directory named
`<topic>.knack/`.

## Reusable and Project-Owned Material

Stock FieldManual knacks must be reusable. Use fictional neutral examples and
avoid:

- consuming-project names;
- real client, employer, or operator identities;
- local absolute paths;
- claims tied to one workstation or checkout;
- credentials, network identifiers, or private infrastructure facts; and
- policy that only makes sense for one repository.

Project-specific material belongs in the `knacks/` tree owned by that project.
Its location establishes ownership and applicability. Do not move those
details into stock prose merely by calling them "project-local."

When stock and project-owned guidance both apply, read both. Project-owned
policy may strengthen or narrow stock guidance, but contradictions should be
recorded and resolved rather than silently guessed away.

## Recommended Structure

Most knacks benefit from these sections:

1. when to load the knack;
2. mental model;
3. practical workflow or operating pattern;
4. sharp edges and failure modes;
5. a diagnostic or review checklist; and
6. further information.

API companions should also describe important types, lifecycle rules, call
families, portability boundaries, and error behavior.

## Sources and Currency

Prefer primary and durable sources:

- standards-body publications;
- official product or language documentation;
- vendor reference manuals;
- canonical project repositories; and
- peer-reviewed research when the knack relies on empirical claims.

Include enough authoritative references for a reader to verify the material;
do not add weak links merely to meet a quota. Use direct links to the
supporting document.

Add a review date when guidance depends on changing product behavior,
security advice, law, regulation, or version support. Legal, compliance, and
security-sensitive guidance needs proportionally stronger currency review and
should state when expert judgment is required.

Follow FieldManual's
[documentation standard](../standards-and-practices/core/documentation.md)
for source-of-truth and evidence discipline.

## Manual Review

FieldManual does not provide a knack validator or validation cache. Before a
knack lands, review:

- filename and topic placement;
- scope and load trigger;
- Markdown structure and relative links;
- word count and split opportunities;
- unsupported certainty or stale version claims;
- high-entropy or secret-like content;
- real names, local paths, and project-specific leakage; and
- authority and currency of references.

Treat hygiene findings as maintenance work unless they expose a broader
correctness, privacy, legal, or security problem.
