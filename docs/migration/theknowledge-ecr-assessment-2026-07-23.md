# TheKnowledge ECR Applicability Assessment

Date: 2026-07-23

## Purpose

Determine which Engineering Change Request practices and requests reviewed in
TheKnowledge also apply to FieldManual. This is migration provenance, not a
claim that an external target accepted a FieldManual request.

## Source State

The review examined TheKnowledge revision
`751a52a0cfcf6c8daf99f8f9657e5a4bb563a3a1` on `trunk`.

The canonical ECR specification, starter templates, original directory
request, and approved structured-lifecycle proposal were tracked and clean.
The raw intake contained 50 substantive records: 18 tracked and 32 untracked.
The disposition index and deconfliction map had tracked modifications, while
the July intake report and consolidated proposals were untracked.

July classifications are therefore reviewed working-state evidence, not
committed source authority. Raw ECRs were not copied verbatim because several
contain unnecessary client identity, organization details, local mitigations,
or workstation paths.

## Applicable And Implemented

- Per-target ECR directories were generalized into the target-neutral
  [ECR standard](../../standards-and-practices/core/engineering-change-requests.md),
  live tree, and consumer skeletons.
- The `open` / `in-progress` / `closed` lifecycle was adopted with sharper
  acknowledgement, disposition, reopening, and source-versus-target
  authority rules.
- Raw intake deconfliction became target-side guidance that keeps received
  payloads separate from bugs, proposals, tasks, and decisions.
- Coding, documentation, mock use, pragmatic editing, changelog preservation,
  and project-boundary ECRs were already represented in FieldManual core
  standards; no duplicate ECR was created.
- Reusable local-state, managed-ignore, bootstrap-context, and starter-mode
  requirements are reflected in FieldManual configuration, manifest,
  bootstrap, and safety documentation. Python environment machinery remains
  excluded.
- Unexpected tool environment or validation scope became an explicit
  interrupt rule in
  [runtime and package environments](../../standards-and-practices/core/runtime-and-package-environments.md).

## Applicable But Not Approved Policy

Several source ECR groups were already represented by FieldManual proposals
that remain under review:

- [large-file and history
  safety](../../project-management/proposals/under-review/large-file-and-history-safety.md)
- [automation target
  safety](../../project-management/proposals/under-review/automation-target-safety.md)
- [operator tool
  contracts](../../project-management/proposals/under-review/operator-tool-contract.md)
- [project-owned overlays and record
  paths](../../project-management/proposals/under-review/project-owned-overlays-and-record-paths.md)
- [roadmap and frontend
  guidance](../../project-management/proposals/under-review/reusable-roadmap-and-frontend-guidance.md)
- [superseded proposal
  lifecycle](../../project-management/proposals/under-review/superseded-proposal-lifecycle.md)

The ECR assessment does not approve those proposals.

## External-Target Findings Reserved For Later

One raw request actually targets `mdview`: support for viewing TOML. The
untracked July inspection reports that `mdview` already displays arbitrary
non-Markdown files through its generic plain-text path. FieldManual did not
create or close an `ECRs/mdview/` record based solely on that uncommitted
report. Verify the authoritative `mdview` behavior when that target is
reviewed.

The Ubersight-related raw records do not request changes from Ubersight. They
ask the standards framework to add optional Ubersight integration guidance
and a development-observability knack. That content may be evaluated later,
but it must not be misfiled as `ECRs/ubersight/`.

Other outward requests in the source inbox target tools and behavior that
FieldManual does not currently use. They were not imported merely because
they existed in TheKnowledge.

## Not Applicable

FieldManual did not import ECRs tied to:

- pyenv, virtual environments, pip installation, or Python package runtime
  policy;
- hook installers, commit helpers, entropy or quality-gate wrappers;
- multi-script bootstrap and updater machinery; or
- TheKnowledge's special feedback branch and helper.

The general safety lessons were considered, but those executable systems are
outside FieldManual's nearly scriptless architecture.

## Result

FieldManual now uses one source-owned ECR contract for its own requests to
other projects and for requests created by consuming projects. The ready
`ECRs/FieldManual/` target serves consumers; `_target-template/` supplies the
same structure for any other real target. No mdview or Ubersight ECR was filed
during this assessment.
