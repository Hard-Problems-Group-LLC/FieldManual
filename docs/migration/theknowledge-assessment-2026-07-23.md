# TheKnowledge Migration Assessment

Date: 2026-07-23

## Purpose

Record what FieldManual retained from its sister project, what it adapted, and
what it deliberately left behind. This is migration provenance, not a live
FieldManual standard.

## Source State

The review examined TheKnowledge at local revision `751a52a` on `trunk`.
That checkout also contained modified tracked records and dozens of untracked
working files. In particular, several consolidated July proposals and the
risk-triggered expert review-board proposal were not committed upstream.

Committed material and working-tree material were therefore classified
separately. Untracked proposals were used as design input and, when retained,
were imported as FieldManual proposals under review rather than represented
as established upstream policy.

The separate
[ECR applicability assessment](theknowledge-ecr-assessment-2026-07-23.md)
records the later request-by-request and lifecycle review.

## Imported Or Adapted

- propose, backlog, execute, clear, and defer lifecycle guidance
- Markdown-first project-management, bug, proposal, review, and decision
  skeletons
- target-neutral, source-owned ECR lifecycle and target-side deconfliction
  for requests crossing project boundaries
- proposal format and append-only decision history
- documentation, testing, mock-use, editing, version-control, local-state,
  project-boundary, environment-selection, and changelog guidance
- clean-template versus framework-live-state separation
- tracked configuration with ignored local overrides
- the declarative, idempotent initialization concepts from current proposals
- selected open proposals that remain relevant without TheKnowledge tooling
- language and technology practices, reorganized outside the core standards
- reusable knacks that do not depend on TheKnowledge executables

## Reimplemented Instead Of Copied

The FieldManual bootstrap takes behavioral lessons from TheKnowledge's
initializer but shares none of its environment-provisioning architecture. It
uses one framework-owned layout declaration and one dependency-free Python
3.9+ installer. It performs only bounded filesystem initialization.

## Deliberately Excluded

- Python environment, pyenv, virtual-environment, pip, and package bootstrap
  machinery
- POSIX and Windows bootstrap wrappers
- shell-profile and user-home mutation
- Git hook installation and commit, pull, push, or feedback helpers
- timeout, quality-gate, entropy, knack-validation, and tool-profile programs
- executable development utilities and language-specific verifiers
- Python package metadata, runtime source, and tests for excluded tooling
- license knacks pending a dedicated legal and currency review
- TheKnowledge's live backlog, bug history, completed tasks, and raw ECR
  intake
- proposals tied specifically to Black, Codex startup workarounds, pyenv,
  direnv, or TheKnowledge's old feedback branch

Executable verification may later be supplied by separate, explicitly adopted
submodules. FieldManual itself remains a documentation framework with one
bootstrap installer.

## Relocated FieldManual Material

FieldManual originally described itself as a non-coding, data-centric manual.
That scope no longer matches its mission.

The useful knowledge-management material was retained as the optional
`knacks/knowledge-management/` profile. It is no longer installed into every
project or presented as the framework's universal default.
