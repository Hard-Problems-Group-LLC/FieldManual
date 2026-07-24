# Completed Tasks

Record completed work with newest entries at the top. Use dated bullets and
include concise outcomes, owners, ISO 8601 completion timestamps, validation
evidence, important decisions or risk acceptances, and follow-up records.

## Completed

- FM-TASK-009 — Added maintained Ubersight development-observability
  guidance and filed an applicable source-owned ECR. Owner: FieldManual
  maintainers; execution by an AI assistant under repository-operator
  direction. Created and started: 2026-07-24T00:48:02-07:00. Completed:
  2026-07-24T01:11:17-07:00.
  - Outcome: added a reusable Ubersight knack and discovery category; added
    the complete `ECRs/ubersight/` lifecycle tree and
    `FieldManual-ECR-2026-003` requesting packaged, discoverable, validated
    status contracts; and recorded follow-ups to the earlier migration
    assessments without changing their historical dispositions.
  - Research: reviewed the clean authoritative Ubersight 0.1.0 checkout at
    `1ec5d3ccb662f89f7b8c8b8cfd47349894094545`, its approved originating
    proposal, source, tests, security and command documentation, and three
    independently discovered producer-knack variants.
  - Validation: three independent target-content reviews; exercised the
    actual CLI status writer, main-status rendering, and background-job
    loading against the reviewed revision; passed a bootstrap dry run, 282
    local Markdown links, three unique and lifecycle-consistent ECRs,
    whitespace, secret-signature, symlink, and oversized-file checks.
  - Decisions: no new architecture decision required.
  - Risk decisions: the new ECR remains explicitly unsubmitted. Current
    permissive status parsing, phase-stack flag visibility, network and
    operator-context observation, location-memory sensitivity, and runtime
    context limits are documented rather than represented as solved.

- FM-TASK-008 — Established `.local/tmp/` as the default project-local
  temporary workspace. Owner: FieldManual maintainers; execution by an AI
  assistant under repository-operator direction. Created and started:
  2026-07-23T19:22:43-07:00. Completed:
  2026-07-23T19:29:32-07:00.
  - Outcome: made the entire `.local/` tree a mandatory effective ignore;
    added unique-run, ownership, confinement, retention, sensitivity, and
    cleanup guidance; propagated the rule through managed AGENTS instructions
    and the core test standard; and declared `.local/tmp/` as a private
    bootstrap directory.
  - Validation: compiled the bootstrap with Python 3.9 and the system Python;
    completed a clean-consumer dry run, installation, and idempotent rerun;
    verified both local directories at mode `0700`, the effective `.local/`
    ignore, exact managed-footer parity, 271 local Markdown links, and clean
    whitespace.
  - Decisions: no new architecture decision required.
  - Risk decisions: none.

- FM-TASK-007 — Inventoried and deduplicated reusable knack material
  throughout `~/codebase`. Owner: FieldManual maintainers; execution by an AI
  assistant under repository-operator direction. Created: 2026-07-23.
  Started: 2026-07-23T17:01:26-07:00. Completed:
  2026-07-23T17:39:37-07:00.
  - Outcome: assessed 25 knack roots containing 605 regular files and 123
    relative-path/content variants; added 17 maintained knack documents and
    15 category indexes covering terminal UI and Turbo Vision design, TUI and
    VM test automation, VirtualBox, Git history repair, complexity, browser
    automation, GNOME and live sessions, and Codex app-server integration.
  - Provenance: recorded exact source revisions, untracked-source status,
    duplicate and subset variants, companion records, corrections, imports,
    exclusions, and deferred Ubersight and license material in the codebase
    knack assessment.
  - ECRs: created two unsubmitted source-owned drafts for AmazingDNSHammer's
    opt-in TUI automation concerns and BQMP-pirouette-utils' Git history-purge
    errors while retaining corrected, actionable stock guidance.
  - Validation: three independent content and integration reviews; reproduced
    all inventory counts; checked 270 local Markdown links; verified all 17
    new knacks at 744–1,679 words with current source-review dates; checked
    VirtualBox 7.2.13 command syntax; compiled the installer with Python 3.9
    and the system Python; completed a clean consumer dry run, installation,
    and idempotent rerun; and passed ECR structure, UTF-8, newline, whitespace,
    secret, project-leakage, symlink, binary, and repository-hygiene checks.
  - Decisions: no new architecture decision required.
  - Risk decisions: none. The outgoing ECRs remain explicitly unsubmitted;
    Ubersight and license guidance remain governed deferred work.

- FM-TASK-004 — Added a current, language-specific Go engineering profile.
  Owner: FieldManual maintainers; execution by an AI assistant under
  repository-operator direction. Created: 2026-07-23. Started:
  2026-07-23T16:31:11-07:00. Completed:
  2026-07-23T16:55:28-07:00.
  - Outcome: added integrated guidance for code and API design, testing and
    debugging, modules and builds, security, tool installation and
    maintenance, dependency graphs, clean onboarding, and administrator
    operations; linked the profile from the language index.
  - Research: synthesized current Go project documentation and community wiki
    guidance with the living Google and Uber style guides and original
    guidance from widely used Go tools. The profile records a 2026-07-23
    source review and a time-resilient version policy.
  - Validation: two independent Go-content reviews; Python 3.9 compilation
    and warning-clean bootstrap dry run; clean consuming-project installation
    and idempotent rerun; 45/45 manifest templates; exact ECR live/template
    parity; 163 local Markdown links; whitespace, secret, binary, newline, and
    repository-hygiene checks.
  - Decisions: no new architecture decision required.
  - Risk decisions: none.

- FM-TASK-006 — Standardized target-neutral Engineering Change Requests for
  FieldManual and consuming projects. Owner: FieldManual maintainers;
  execution by an AI assistant under repository-operator direction. Started:
  2026-07-23; exact time not recorded. Completed:
  2026-07-23T16:23:19-07:00.
  - Outcome: added one source-owned ECR standard, target-neutral request
    format, reusable `_target-template/`, ready consumer `FieldManual/`
    target, target-side intake/deconfliction guidance, and an explicit
    environment-surprise interrupt rule.
  - Assessment: mapped applicable TheKnowledge ECRs to implemented standards
    or existing under-review proposals, excluded tooling-specific requests,
    and reserved mdview and Ubersight evaluation for later work without
    creating premature target records.
  - Validation: 45/45 manifest templates, exact live/template ECR parity,
    Python 3.9 clean-consumer dry run and installation, idempotent rerun,
    arbitrary-target activation, request-field checks, local links, Markdown
    hygiene, and independent implementation review.
  - Decisions: FM-DEC-006.
  - Risk decisions: none.

- FM-TASK-001 — Rebuilt FieldManual as a language-neutral, nearly scriptless
  standards framework. Owner: FieldManual maintainers; execution by an AI
  assistant under repository-operator direction. Started: 2026-07-23; the
  original record did not capture a time. Completed:
  2026-07-23T15:35:18-07:00.
  - Outcome: added the two-root configuration, explicit filesystem manifest,
    conservative Python 3.9+ bootstrap, clean project skeletons, core and
    optional standards trees, reusable knacks, live project management, and
    seven imported proposals that remain under review.
  - Validation: Python 3.9 compilation and execution; standard and fallback
    TOML parsing; clean-project dry run, installation, permissions, and
    idempotent rerun; template-manifest coverage; local-link and proposal
    structure checks; symlink and concurrent-create safety cases; and two
    independent repository reviews.
  - Decisions: FM-DEC-001 through FM-DEC-005.
  - Risk decisions: none. Documented portable-fallback and managed-file
    concurrency limits remain explicit rather than being represented as
    solved.
  - Follow-up: FM-TASK-002 through FM-TASK-005.
