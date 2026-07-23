# Decision Log

Record durable decisions here with newest entries at the top.

For each entry, include:

- date
- decision
- status when relevant
- rationale
- related files, proposals, or backlog items

## Decisions

### FM-DEC-006 — Use One Target-Neutral ECR Contract

- Date: 2026-07-23
- Status: active
- Decision: Keep outgoing ECRs as source-owned records under
  `ECRs/<target-project>/{open,in-progress,closed}`. Install a ready
  FieldManual target for consumers and a non-live target template for every
  other project.
- Rationale: FieldManual itself and its consumers need the same identity,
  transport, authority, lifecycle, and closure rules without assuming every
  target is an upstream dependency or introducing a special feedback branch.
- Related work: FM-TASK-006,
  `standards-and-practices/core/engineering-change-requests.md`, and
  `docs/migration/theknowledge-ecr-assessment-2026-07-23.md`

### FM-DEC-005 — Defer License Knacks

- Date: 2026-07-23
- Status: active
- Decision: Do not import license guidance during the initial migration.
- Rationale: legal and compatibility guidance requires a dedicated currency
  and expert review before republication.
- Related work: FM-TASK-003 and `knacks/README.md`

### FM-DEC-004 — Preserve Proposal Status

- Date: 2026-07-23
- Status: active
- Decision: Import selected current source material as FieldManual proposals
  under review, not as approved standards.
- Rationale: several of the strongest source proposals were untracked working
  material, and operator direction to migrate useful content does not silently
  approve each proposed contract.
- Related work: `project-management/proposals/under-review/`

### FM-DEC-003 — Separate Clean Templates From Live State

- Date: 2026-07-23
- Status: active
- Decision: Keep reusable skeletons under `templates/` and FieldManual's own
  active records under `project-management/`.
- Rationale: consuming projects need clean starters, while framework
  maintenance needs durable live governance records.
- Related work: `FieldManual-layout.toml`

### FM-DEC-002 — Use An Explicit Two-Root Contract

- Date: 2026-07-23
- Status: active
- Decision: Require both project and framework roots in tracked and local TOML
  configuration.
- Rationale: the framework/project distinction must not depend on the ambient
  working directory. Equal roots identify self-maintenance; otherwise the
  framework is nested inside the project.
- Related work: `docs/configuration.md`

### FM-DEC-001 — Keep FieldManual Nearly Scriptless

- Date: 2026-07-23
- Status: active
- Decision: Keep language-neutral core standards and optional
  language/technology documentation in FieldManual, but no language-specific
  verification programs.
- Rationale: consuming projects own executable toolchains; reusable verifier
  suites can become separately versioned submodules.
- Related work: `README.md` and FM-TASK-005
