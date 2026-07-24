# Engineering Change Request: Specify and Validate Ubersight Status Contracts

- ECR ID: `FieldManual-ECR-2026-003`
- Request revision: 1
- Source project or origin namespace: FieldManual
- Target project: ubersight
- Target canonical locator:
  `https://github.com/Hard-Problems-Group-LLC/ubersight`
- Target component, version, or revision: Main and background-job status
  protocols in Ubersight 0.1.0 at
  `1ec5d3ccb662f89f7b8c8b8cfd47349894094545`
- Request owner: FieldManual maintainers
- Drafted: 2026-07-24
- Submitted: Not yet submitted
- Submitted-content digest: Not yet recorded
- Source lifecycle: Open
- Target handling status as reported: Not submitted
- Target intake ID or authoritative reference: None
- Sensitivity and reuse classification: Public, reusable integration and
  protocol-correctness guidance
- Related, duplicate, or superseded ECR IDs: None found
- Origin and provenance: FieldManual Ubersight integration review,
  FM-TASK-009

## Submitted Request

Freeze this section after first transport. Preserve a prior revision when a
material change must be resubmitted.

### Problem And Source Impact

Multiple projects publish development status to Ubersight through
`ubersight.status.v1` and `ubersight.background-job-status.v1`. Those names
look like versioned cross-project contracts, but their authoritative
definitions currently exist only across prose examples, Python models,
coercion code, and tests. Ubersight ships no independently consumable schema,
schema-discovery interface, or producer-validation command.

The two readers also apply incompatible validation policy. The main status
loader does not inspect the `schema` value, silently converts unsupported row
states to `pending`, applies truth conversion rather than Boolean type
validation to global flags, and can raise on some malformed object fields.
The background-job loader requires the exact schema but silently converts an
unknown state to `running`. It parses `updated_at` without using it as a
freshness or heartbeat boundary, so telemetry associated with a still-live
PID can remain visibly active after its producer stopped updating it.

The strict main-status writer and the phase-stack renderer do not fully agree
on lifecycle semantics. The writer requires exactly one active phase and,
unless globally complete, an active slice. `--blocked` alone does not waive
that requirement, so without `--complete` a blocked-only current slice cannot
be written; meanwhile global blocked and complete labels are only rendered in
the legacy no-phase-stack path that the current writer refuses to produce.

FieldManual can document the deployed behavior, but consuming projects
should not have to reproduce implementation coercions to determine whether a
status file is valid. Silent conversion of invalid telemetry into ordinary
`pending` or `running` state can give an operator a false view of active work.

### Requested Outcome

Publish and enforce language-neutral, versioned producer contracts for main
status and background-job telemetry. Give producers a network-free way to
discover and validate those contracts, make invalid or unsupported telemetry
visibly distinct from legitimate work state, and align blocked, complete,
and stale semantics across writer, reader, and renderer.

### Acceptance Criteria

- Ubersight tracks and packages machine-readable schemas for
  `ubersight.status.v1` and `ubersight.background-job-status.v1`. They define
  required and optional fields, types, enumerations, numeric constraints,
  unknown-field policy, timestamp rules, and schema-version behavior.
- The maintained prose specifies path and context selection, atomic
  publication, producer ownership, liveness and cleanup, compatibility, and
  privacy rules that cannot be expressed completely in a data schema.
- An installed, network-free, read-only command can export or locate the
  schemas and validate one main-status file or one background-job file. It
  has documented exit codes and machine-readable diagnostics suitable for
  non-Python producers and CI. The diagnostics declare their own schema or
  format version and use documented fields and codes to distinguish at least
  valid, invalid, and unsupported input.
- Current Ubersight writer output and canonical conforming example fixtures
  for both protocols validate against the packaged schemas. Maintained
  documentation draws its conforming examples from, or tests them against,
  those fixtures.
- An unsupported main schema, invalid field type, or invalid row state is
  reported as invalid or unsupported; it is not rendered as legitimate
  `pending` state and does not terminate the dashboard.
- Any legacy missing-schema or single-phase compatibility remains available
  only through an explicit, documented compatibility path whose display or
  diagnostics make that state visible.
- Invalid background-job states are not rendered as `running`. The contract
  defines heartbeat freshness so missing, invalid, or expired timestamps
  cannot remain aggregated as active work merely because a PID is live.
- Malformed, unsupported, or stale producer files are not deleted merely
  because validation failed. Cleanup occurs only under a documented
  ownership and process-identity rule. The contract may separately permit
  documented terminal-state retention and cleanup, including removal after a
  `complete` record has been observed.
- Blocked and complete semantics are representable through the supported
  writer and remain visible when the required phase stack is rendered.
  Active-row requirements and transitions are unambiguous.
- Tests cover installed schema data, schema export and validation, writer and
  documentation conformance, missing and future schemas, invalid types and
  states, malformed lists and Booleans, stale job heartbeats, blocked and
  complete rendering, and the supported compatibility transition.

### Non-Goals

- Redesign the dashboard layout or phase/slice vocabulary.
- Require producers to use Python or the Ubersight source tree.
- Remove currently conforming `v1` producer fields.
- Abruptly remove intentional legacy compatibility without a transition.
- Replace consuming projects' durable project-management records.
- Resolve operator-location collection, network-egress defaults, runtime
  context collisions, or local-file permission policy in this request.

### Constraints And Risks

Ubersight is an alpha package but already has multiple active producers.
Validation changes therefore need a visible compatibility path and a
documented rollout rather than silent reinterpretation. JSON Schema alone
cannot prove atomic replacement, process identity, freshness, ownership, or
sensitive-content policy; the validator and prose contract must cover those
operational rules.

Rejecting invalid status must degrade to an actionable dashboard diagnostic,
not crash the monitoring surface. A stricter contract may expose existing
producer defects that permissive coercion previously hid.

### Evidence At Submission

- Ubersight `README.md`, command documentation, package metadata, source, and
  tests at
  `1ec5d3ccb662f89f7b8c8b8cfd47349894094545`.
- `src/ubersight/dashboard.py`: main status normalization and loading,
  background-job normalization and loading, writer validation, renderer, and
  CLI paths.
- `tests/test_ubersight.py`: current writer, context, rendering,
  background-job, process-liveness, and cleanup expectations.
- The approved target proposal
  `project-management/proposals/approved/ubersight-side-window-dashboard.md`
  introduced the first small status schema and requested schema,
  stale-file, and rendering tests. This ECR is distinct: it requests
  packaged language-neutral contracts, discovery and validation interfaces,
  and correction of the current reader/writer/renderer semantic gaps.
- A 2026-07-24 read-only fixture probe confirmed that an unsupported main
  schema is accepted without a source error and that invalid row state is
  silently normalized.
- Target-side backlog, active and deferred work, bug indexes, and proposal
  indexes, including approved records, showed no duplicate request for these
  packaged contracts and validation interfaces during the source review.

## Source Tracking

After first transport, maintain this section as an append-only history.

### Local Mitigation

FieldManual's Ubersight knack pins its behavior review to the inspected
revision, directs projects to the supported CLI writer and exact state names,
requires atomic publication for independent producers, and warns producers
not to rely on permissive reader coercion. Background-job producers should
test their complete JSON fixtures against the exact deployed version until
Ubersight supplies a standalone validator.

### Transport And Receipt Log

- 2026-07-24 — Drafted locally; not yet submitted.

### Discussion And Amendments

None.

### Target Disposition

Not submitted; no target disposition.

### Source Closure

Open.
