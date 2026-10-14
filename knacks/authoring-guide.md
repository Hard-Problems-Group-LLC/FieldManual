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

A knack's full path should state its purpose and scope once, with no
component repeated. Paths grow long quickly, and every repeated word costs
every reader, link, and listing.

Use `<topic>.knack.md` when one document is sufficient:

- `knacks/UI/terminal/ansi.knack.md`
- `knacks/sandboxing/bubblewrap.knack.md`

For a larger fileset, make a directory named for the topic and name each
file inside for its own part only:

- `overview.knack.md` is the conceptual entry point and links its
  companions;
- each companion is `<part>.knack.md`, for a stable subsystem or concern;
  and
- a language-specific companion appends a stable language tag:
  `<part>.<Language>.knack.md`, or `<Language>.knack.md` when the language
  is the whole subject. Tags include `C`, `CPP`, `CSharp`, `PowerShell`,
  and `Python`.

Examples:

- `knacks/windows/shells/overview.knack.md`
- `knacks/windows/shells/PowerShell.knack.md`
- `knacks/dotnet/assembly-inspection/reflection.PowerShell.knack.md`
- `knacks/games/steam/install-layout.knack.md`

The directory is the topic. Do not repeat it, or any other path component,
in the names beneath it: `windows/shells/PowerShell.knack.md`, not
`windows/shells.knack/shells.api.PowerShell.knack.md` or
`windows/windows-shells/PowerShell.knack.md`. A fileset directory is
recognised by its `overview.knack.md`; an area directory by its
`README.md`. The `.knack` marker appears only in file names, never
in directory names.

When a part outgrows one file, because it has deep details, special cases,
or techniques worth their own documents, promote it to a subdirectory named
for the part. Its main document becomes that directory's
`overview.knack.md`, and the new files sit beside it:

- `knacks/windows/shells/PowerShell/overview.knack.md`
- `knacks/windows/shells/PowerShell/remoting.knack.md`

A part with a single file stays a file; do not make a directory for one
document. A single-document knack that gains companions is promoted the same
way (`shells.knack.md` becomes `shells/overview.knack.md`). Promotion
changes the path, so rewrite the links that point to it. Every fileset
directory, at any depth, therefore has the same entry point, and no name
repeats a component of its path.

### Choosing Names

- Because a topic appears once in its path, name it for clarity: say what
  the knack covers, using no word the path already supplies
  (`windows/desktop-automation/`, not `windows/desktop/` or
  `windows/windows-desktop-automation/`).
- Keep part names to a word or two (`transport`, `install-layout`).
- Aim for full paths under `knacks/` of about 70 characters or fewer.
- When several topics share a qualifier, such as a platform, product, or
  tool, give them a subarea directory instead of a shared prefix
  (`AI/Anthropic/claude-code/windows/`). Split an area into subareas once
  it holds more topics than a reader can scan at a glance, roughly eight.
- File a knack where a reader would look for its subject, not where its
  author found it. A testing technique belongs under testing even when it
  was learned while orchestrating agents; Windows Sandbox, a disposable
  virtual machine, belongs under virtualization.
- Give every area directory a `README.md` that indexes its contents, so a
  reader can descend from `knacks/README.md` to any file; a fileset's
  overview indexes its companions.

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
