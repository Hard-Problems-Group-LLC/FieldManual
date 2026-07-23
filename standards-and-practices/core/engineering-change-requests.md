# Engineering Change Requests

## Purpose

Use an Engineering Change Request, or ECR, when one project needs a durable,
reviewable change from another project. The target may be an upstream
dependency, sibling repository, framework, service, tool, or other separately
owned system.

ECRs are source-project records. They preserve the request while it crosses a
repository boundary; they do not replace the target project's bugs,
proposals, backlog, decisions, or implementation workflow.

## Source-Project Directory Contract

Keep outgoing ECRs in one target-specific lifecycle tree:

```text
ECRs/
  README.md
  _target-template/
    README.md
    request-template.md
    open/
      README.md
    in-progress/
      README.md
    closed/
      README.md
  <target-project>/
    README.md
    request-template.md
    open/
      README.md
    in-progress/
      README.md
    closed/
      README.md
```

`_target-template/` is non-live scaffolding. Copy it to a stable, portable
target slug before filing a request. Replace every `TARGET_PROJECT`
placeholder, remove the scaffold-activation note, and keep one target project
per directory. Do not store live ECRs in the template tree.

FieldManual-consuming projects receive `ECRs/FieldManual/` as a ready target
tree because FieldManual is a known external target. A writable FieldManual
maintenance checkout does not use that self-target for ordinary maintenance;
it uses FieldManual's own project-management workflow and creates target trees
for other projects as needed.

Target slugs should use a stable public project name or an approved opaque
alias. Restrict names to portable letters, digits, dots, underscores, and
hyphens. Resolve case-only or historical-name collisions deliberately instead
of silently merging target trees.

## Ownership And Authority

The source project owns:

- the source ECR ID and revision;
- the submitted request text;
- its local lifecycle location and history;
- local mitigations and source impact; and
- the source-side closure record.

The target project owns:

- acknowledgement and its intake identifier;
- target-side triage and deconfliction;
- bugs, proposals, tasks, decisions, and implementation;
- the authoritative target disposition; and
- target release or delivery claims.

The source may mirror target status only with an authoritative target
reference. Neither project mutates the other's records without separate
authorization.

## Source Lifecycle

The directory and the ECR's `Source lifecycle` field must agree.

### `open/`

The ECR is an editable draft or has been submitted but not acknowledged for
active target handling. Submission does not by itself move a request to
`in-progress/`.

### `in-progress/`

The target has acknowledged, imported, or begun active handling. Record the
target intake ID or other authoritative evidence before moving the source
record here.

`in-progress` describes cross-project handling, not a promise that
implementation has started.

### `closed/`

The source has recorded a dated disposition with rationale and evidence.
Closed outcomes include:

- accepted;
- implemented;
- rejected;
- deferred;
- duplicate;
- superseded;
- withdrawn; and
- no change required.

Closed does not mean successful or implemented. A deferred target disposition
may close the source transport lifecycle while a target-owned proposal
remains deferred.

A source-controlled withdrawal or pre-submission supersession may move
directly from `open/` to `closed/`. Record the source authority and rationale;
an authoritative target reference is required only when the record claims a
target acknowledgement or disposition.

Reopening uses the same ECR ID and an append-only event unless the requested
outcome materially changes. Preserve the earlier closure and explain why the
request returned to active handling.

## Identity And Revisions

Every ECR requires a stable, source-issued, collision-resistant ID. Prefer a
form such as:

```text
<origin-namespace>-ECR-<year>-<sequence>
```

Use an approved opaque origin namespace when the source identity should not be
public. A filename is a human-readable locator, not the identity. Keep the
filename unchanged while moving the record between lifecycle directories.
Prefer a portable filename derived from the ECR ID and short title.

Begin at request revision `1`. Increment the revision when a material change
must be resubmitted, and preserve the prior submitted text or a verifiable
reference to it. Editorial corrections that do not alter the request may be
recorded as dated addenda.

For received records:

- the same ID, revision, and content is a repeated delivery;
- the same ID and revision with different content is an integrity conflict
  and must stop intake; and
- different IDs covering the same topic remain distinct source records and
  may map to one target-owned actionable record.

## Request Record

Each ECR records:

- ECR ID and request revision;
- title;
- source project or approved origin namespace;
- target project and canonical locator;
- target component, version, or revision when relevant;
- request owner;
- drafted and submitted dates;
- submitted-content digest when transport integrity requires it;
- source lifecycle;
- target handling status as reported;
- target intake ID or authoritative reference;
- sensitivity and reuse classification;
- related, duplicate, or superseded ECR IDs; and
- origin and provenance.

The submitted request contains:

- problem and source-project impact;
- requested outcome;
- acceptance criteria;
- non-goals;
- constraints and risks; and
- evidence available at submission.

After first transport, treat those submitted sections as immutable. Put later
information in append-only local-mitigation, transport, discussion,
amendment, and disposition sections. A material change to the requested
outcome requires a preserved new revision or a new ECR.

## Transport

Transmit a copy across repositories; do not remove the source record from its
project. Preserve the ECR ID, revision, and submitted filename in the
transport receipt even when the target uses a different local filename.

Record:

- submission date and method;
- exact revision sent;
- receiving project or authority;
- receipt, intake ID, issue, proposal, or commit reference; and
- later status observations with dates and sources.

Do not require a special feedback branch. Use the projects' normal
version-control and collaboration workflow unless both projects maintain a
specific alternative.

## Existing Project Adoption

FieldManual's bootstrap treats installed ECR files as create-only
project-owned records. A rerun adds a missing `_target-template/` but does not
overwrite an older `ECRs/FieldManual/` README or request template. Existing
projects should compare and reconcile their local skeleton deliberately while
preserving every live ECR.

## Target-Side Intake And Deconfliction

The target keeps received payloads separate from actionable work. When a
durable intake area is useful, prefer:

```text
project-management/
  ecr-intake/
    README.md
    imported/
    disposition-index.md
```

Preserve each received ECR ID, revision, submitted content, and provenance.
The disposition index maps it to the target intake ID, actionable bugs,
proposals or tasks, disposition, date, and authoritative reference.

One target proposal or bug may resolve several ECRs. Preserve every source
record and map duplicates instead of deleting or merging their raw payloads.
If two received records collide on ID or provenance, stop and obtain a
deliberate resolution.

An index is navigation and traceability, not a competing status authority.
The target's normal lifecycle records remain authoritative for target work.

## Privacy And Safety

- Remove credentials, secrets, transcripts, private prompts, host details,
  and unrelated confidential context.
- Include only the evidence needed to evaluate the reusable request.
- Label local workarounds as local; they are not target policy.
- Use opaque source namespaces when identity is unnecessary.
- Do not modify a read-only submodule merely to file its ECR.
- Do not claim target acknowledgement, acceptance, implementation, or release
  without an authoritative target reference.

## Provenance

This standard generalizes TheKnowledge's approved structured ECR lifecycle and
its read-only feedback-directory proposal. It retains per-target
`open`/`in-progress`/`closed` source records, raw-intake separation,
deconfliction, and closure evidence. It intentionally excludes
TheKnowledge's special feedback branch and filename-as-identity convention.
