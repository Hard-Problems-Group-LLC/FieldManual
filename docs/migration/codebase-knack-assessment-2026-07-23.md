# Codebase Knack Assessment

Date: 2026-07-23

## Purpose

Record the repository-wide search for reusable knacks under
`/home/mheck/codebase`, the companion material considered with them, and the
reason each unique family was imported, deferred, or excluded. This is
migration provenance, not a live standard and not a claim that every source
document was authoritative.

## Search Method And Coverage

The review:

- enumerated directories named `knacks` and files whose names end in
  `knack.md`;
- followed parent indexes, ECRs, proposals, incident records, and
  implementation notes when they explained a knack's intent or limitations;
- compared relative paths and content hashes so repeated submodules, clones,
  and obsolete copies did not masquerade as new material;
- inspected the owning repository revision and whether each selected source
  was tracked; and
- left every source checkout unchanged.

Repository metadata, Codex state, dependency trees, caches, and generated
container-storage overlays were excluded from the source scan. Raw traversal
encountered inaccessible overlay, generated-home, and package-manager paths in
container state under several `.codex-home` trees. The pruned source scan
excluded those execution artifacts deliberately; no candidate source tree was
hidden by the failures.

Outside this FieldManual working tree, the scan found:

- 25 knack roots containing 605 regular files;
- 66 distinct relative paths and 123 distinct relative-path/content variants;
- 438 files whose names ended in `knack.md`; and
- no file whose complete basename was literally `knack.md`.

The 605 files divide into 540 files in repeated TheKnowledge trees, 42 files
in project-owned knack trees, and 23 files in another FieldManual checkout.
The other FieldManual copy matched the maintained FieldManual content and
contributed no new family.

Sixteen TheKnowledge roots were present: copies in AutoTomato,
BQMP-pirouette-authserver, BQMP-pirouette-utils, org-recon,
AmazingDNSHammer, Fnirsi_DPS150, NiceBeach, bouncy, claude-wrangler,
codex-wrangler, dufocom, gridbreaker, mdview, mindscraper-code, and
ubersight, plus the canonical TheKnowledge checkout. Those roots contained
five full-tree content variants: some were current, some older or partial,
and some contained locally different index material. In the terminal family,
fifteen held the same current ten-file snapshot and AutoTomato held an older
snapshot. The union added no stock topic absent from the canonical checkout.
FieldManual had already adapted the stock material, so repeated copies were
not overlaid on the maintained versions.

The project-owned roots were:

- `BuildQM/actual/BQMP-pirouette-authserver/knacks`
- `BuildQM/actual/BQMP-pirouette-utils/knacks`
- `BuildQM/actual/org-recon/knacks`
- `HPG/actual/AmazingDNSHammer/knacks`
- `HPG/actual/NiceBeach/knacks`
- `HPG/actual/dufocom/knacks`
- `HPG/actual/mindscraper-code/knacks`
- `HPG/actual/mindscraper_OBSOLETE/knacks`

## Source State

The canonical TheKnowledge checkout was reviewed at
`751a52a0cfcf6c8daf99f8f9657e5a4bb563a3a1`. The principal project
checkouts were reviewed at:

| Project | Revision |
| --- | --- |
| AmazingDNSHammer | `03ddb7fe18614b6bd74fa207dbcd650c758a723e` |
| dufocom | `75bf4094bd02830a8a4531483c354d1eb5741805` |
| BQMP-pirouette-utils | `c5cf9b625966781ff3a26273d6a17c2bd7df0bf7` |
| BQMP-pirouette-authserver | `25ace54a05a9271517fa460e74e7b65db4f93fbd` |
| NiceBeach | `1487a099127e3b77cc19159cc31b5cd62ad02d9f` |
| mindscraper-code | `17743b839b2f74c5317777f0814f8c1b3eeec1f6` |
| org-recon | `d9bbb82b8e2f23a40f49c60ed5daa73118c2781c` |

The VirtualBox source knack in BQMP-pirouette-utils and both Codex app-server
source knacks in org-recon were untracked working-tree files. The
`mindscraper_OBSOLETE` directory was not a Git checkout. Those materials were
treated as design input, not committed upstream authority. Reusable claims
were independently checked against current primary sources before being
restated.

## Family Disposition Ledger

| Source family or companion | Disposition and maintained destination |
| --- | --- |
| Repeated TheKnowledge stock trees and the other FieldManual clone | Already adapted in FieldManual's existing auditing, authentication, debugging, knowledge-management, performance, sandboxing, and terminal protocol/library knacks; no older overlay applied. See the [original TheKnowledge assessment](theknowledge-assessment-2026-07-23.md). |
| AmazingDNSHammer Turbo Vision fileset, import ECR, automation proposal, and implementation | Synthesized into [terminal UI design and automation](../../knacks/UI/terminal/terminal-ui-design.knack/terminal-ui-design.overview.knack.md) plus the [Turbo Vision style overview](../../knacks/UI/terminal/turbovision-style-tuis.knack/turbovision-style-tuis.overview.knack.md). Implementation concerns are retained in FieldManual-ECR-2026-001. |
| dufocom modern text UI, keyboard, box drawing, POSIX input, curses rendering, and xterm input | Synthesized across the [terminal UI family](../../knacks/UI/terminal/README.md); project-specific direct-terminal preferences were not promoted. |
| BQMP-pirouette-utils VirtualBox knack and its incident, bug, guard, tests, and automation notes | Generalized into [safe VM control and VirtualBox automation](../../knacks/virtualization/README.md); host facts and the Python guard remain excluded. |
| BQMP-pirouette-utils Git history knack and import ECR | Corrected and imported as [Git history repair](../../knacks/version-control/purge-large-files-from-git-history.knack.md); source errors are retained in FieldManual-ECR-2026-002. |
| Repeated McCabe metric family in BQMP-pirouette-authserver, AmazingDNSHammer, and NiceBeach | Synthesized as [cyclomatic complexity](../../knacks/software-engineering/code-metrics/cyclomatic-complexity.knack.md). |
| NiceBeach and BQMP-pirouette-authserver Ubersight family, older AmazingDNSHammer copy, and two outside-tree import records | Deferred to the existing Ubersight review; no stock import in this pass. |
| NiceBeach GNOME Shell extension knack and live-session-target ECR | Imported separately as [GNOME Shell extension development](../../knacks/desktop/gnome-shell-extension-development.knack.md) and [live user-session targeting](../../knacks/desktop/live-user-session-targeting.knack.md). |
| Mindscraper browser-automation knack and obsolete duplicate | Rewritten as [browser automation](../../knacks/UI/browser/browser-automation.knack.md); workstation and route facts excluded. |
| org-recon Codex app-server and usage-statistics knacks | Rewritten as the [Codex app-server fileset](../../knacks/AI/OpenAI/README.md) against current official documentation. |
| Mindscraper codex-wrangler, project indexes, and static viewer | Excluded as project-, checkout-, and version-specific navigation or tooling. |
| Repeated license families | Deferred under the existing legal and currency review decision. |

The five filenames ending in `knack.md` outside a `knacks/` root were the
Turbo Vision import record, two copies of the Git history import record, and
two copies of the Ubersight import record. They map to the same three ledger
families and add no fourth content family.

## Imported Or Synthesized

The following unique families contained durable, project-neutral value:

- [Turbo Vision-inspired presentation and broader terminal-UI
  engineering](../../knacks/UI/terminal/README.md), including rendering,
  input, keyboard navigation, box drawing, portability, accessibility, and
  test automation;
- [virtual-machine control invariants and versioned VirtualBox
  operations](../../knacks/virtualization/README.md);
- [safe Git history repair and large-object or secret
  removal](../../knacks/version-control/purge-large-files-from-git-history.knack.md);
- [cyclomatic complexity](../../knacks/software-engineering/code-metrics/cyclomatic-complexity.knack.md)
  as a review and refactoring signal;
- [GNOME Shell extension lifecycle and debugging
  practices](../../knacks/desktop/gnome-shell-extension-development.knack.md);
- [browser-automation design, evidence, and failure
  classification](../../knacks/UI/browser/browser-automation.knack.md);
- [Codex app-server client boundaries and account
  telemetry](../../knacks/AI/OpenAI/README.md); and
- [selecting the intended live desktop user and
  session](../../knacks/desktop/live-user-session-targeting.knack.md) without
  silently escaping an automation or sandbox identity.

These were synthesized rather than copied. Real project names, local paths,
machine facts, private identifiers, implementation scripts, incident
specifics, and source-project policy were removed. Volatile product behavior
is version-gated and dated, and the resulting knacks prefer primary
documentation.

Several source claims required material correction:

- injected TUI input is a consequential control plane, not presentation-only
  access;
- a Unix-domain socket pathname mode is not a portable authentication system,
  and privileged UI automation must not be delegated implicitly;
- terminal cells cannot safely be modeled as one cell per Unicode code point;
- curses lower-right writes and thread behavior require
  implementation-specific qualification;
- raw `/dev/tty` input is a specialized adapter or diagnostic technique, not
  an inherently superior default;
- equal pre- and post-rewrite tip trees prove current-snapshot preservation,
  not that historical objects were unchanged;
- `git push --force-with-lease --mirror` is not a safe generic publication
  recipe;
- VirtualBox registry context, running processes, and writable-medium
  ownership must be reconciled without assuming one project's Python guard;
  and
- complexity counts and useful review thresholds vary by language, tool, and
  project.

Related ECRs, proposals, incident records, tests, and scripts were used to
find these limitations, but were not imported as stock content. Two
source-owned draft requests preserve actionable upstream concerns without
withholding the corrected guidance:

- [harden opt-in TUI
  automation](../../ECRs/AmazingDNSHammer/open/FieldManual-ECR-2026-001-harden-opt-in-tui-automation.md);
  and
- [correct Git history purge
  guidance](../../ECRs/BQMP-pirouette-utils/open/FieldManual-ECR-2026-002-correct-git-history-purge-guidance.md).

Neither request has been submitted or acknowledged.

## Deferred

Ubersight development-observability material remains reserved for the later
Ubersight review already identified in the
[TheKnowledge ECR assessment](theknowledge-ecr-assessment-2026-07-23.md).
It was not silently promoted into stock guidance during this pass.

License knack families remain deferred under the existing legal and currency
review decision. Repetition across checkouts does not make legal guidance
current or generally applicable.

## Excluded

The following material was deliberately not imported:

- `codex-wrangler`, whose absolute paths, generated state, pinned alpha
  versions, and Python manager describe one project rather than a reusable
  practice;
- OrganizationRecon's project-specific status-page and validator contracts;
- Mindscraper routes, workstation browser verdicts, artifact paths, and its
  static knack viewer;
- project-local root and category indexes that only describe their source
  checkout;
- VirtualBox guard scripts, tests, host incident evidence, disk identifiers,
  and recovery facts;
- exact TUI automation protocols and implementation defects from one
  application; and
- obsolete or byte-identical copies that added no distinct guidance.

The reusable boundary lessons from excluded implementation material were
folded into the applicable knacks or were already covered by FieldManual's
runtime, local-state, project-boundary, and version-control standards.

## Result

Every distinct discovered family was imported, mapped to maintained
FieldManual content, deferred through an existing governed review, or
excluded with a reason. The resulting library remains prose-first: no source
project's verifier, environment manager, VM wrapper, browser harness, or
automation server was added to FieldManual.
