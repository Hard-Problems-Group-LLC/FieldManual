# Engineering Change Request: Harden Opt-In TUI Automation

- ECR ID: `FieldManual-ECR-2026-001`
- Request revision: 1
- Source project or origin namespace: FieldManual
- Target project: AmazingDNSHammer
- Target canonical locator:
  `https://github.com/Hard-Problems-Group-LLC/AmazingDNSHammer`
- Target component, version, or revision: TUI automation guidance and
  implementation at `03ddb7fe18614b6bd74fa207dbcd650c758a723e`
- Request owner: FieldManual maintainers
- Drafted: 2026-07-23
- Submitted: Not yet submitted
- Submitted-content digest: Not yet recorded
- Source lifecycle: Open
- Target handling status as reported: Not submitted
- Target intake ID or authoritative reference: None
- Sensitivity and reuse classification: Public, reusable engineering and
  security guidance; no private runtime data
- Related, duplicate, or superseded ECR IDs: None
- Origin and provenance: FieldManual codebase knack assessment,
  FM-TASK-007

## Submitted Request

Freeze this section after first transport. Preserve a prior revision when a
material change must be resubmitted.

### Problem And Source Impact

AmazingDNSHammer's explicit `--automation-socket PATH` opt-in is the correct
default-deny shape: an ordinary run does not expose the automation socket.
The reusable automation documentation and implementation nevertheless
describe injected input as presentation-only and contain correctness and
boundary weaknesses once that mode is enabled.

Injected keys can invoke every consequential action reachable through the
TUI. A privileged process that transfers its control socket to the invoking
user delegates that authority to any process acting as that user. Pathname
socket modes are not a portable authentication mechanism.

Implementation review also found unbounded line input, unsafe stale-path
removal, completion acknowledgements that can race unrelated redraws, no
final publication for an exit-producing key, starvation between real and
injected input, modifier state that is recorded but not applied,
implementation-specific numeric key codes, and a one-code-point-per-cell
frame model that cannot represent general terminal text.

These issues can make tests unreliable or expose more authority than the
operator intended. They are reasons to harden the valuable automation
facility, not to remove it.

### Requested Outcome

Retain the explicit opt-in automation facility and revise its threat model,
protocol, implementation, and tests so enabled automation is a bounded,
authenticated drive-and-observe control plane.

### Acceptance Criteria

- A normal invocation creates no automation listener, socket path, server
  thread, discovery record, or capture artifact; automation requires an
  explicit option such as the existing `--automation-socket PATH`.
- Startup and shutdown make the enabled mode and protected endpoint lifecycle
  observable without logging screen contents or secrets.
- Attached automation is refused for an elevated process by default. Any
  supported privileged mode has a separately reviewed authorization design
  and does not delegate authority merely through `SUDO_UID`.
- A local endpoint uses a private application-owned directory, validates
  existing objects before removal, authenticates peers, bounds clients and
  messages, and cleans up only its own endpoint.
- Each injected event uses a request identity whose completion is correlated
  with that event and its resulting state, including no-op, rejected,
  timeout, cancellation, and exit paths.
- Real and injected input have a documented fair ordering. Semantic key names
  are mapped to runtime library constants by the attached adapter.
- Frame representation accounts for grapheme and terminal-cell width, or
  explicitly restricts the supported character repertoire.
- Automated tests cover disabled startup, malformed and oversized input,
  unauthorized peers, endpoint collision, final-frame publication,
  correlation under redraw, fairness, modifier handling, and cleanup.

### Non-Goals

- Remove TUI automation.
- Require one transport, serialization format, or programming language.
- Replace domain-level authorization with transport authentication.
- Make FieldManual's conceptual harness contract an AmazingDNSHammer wire
  protocol.

### Constraints And Risks

Compatibility for current test clients may require a versioned protocol or a
transition period. “Local” and “same user” must not be treated as equivalent
to “authorized controller.” Screen and semantic snapshots may contain
sensitive data even when no persistent capture was requested.

### Evidence At Submission

- AmazingDNSHammer Turbo Vision knack fileset and approved curses-automation
  proposal at the target revision.
- AmazingDNSHammer TUI automation implementation reviewed during
  FieldManual's 2026-07-23 repository-wide knack assessment.
- Linux `unix(7)` portability warning for pathname-socket permissions.
- FieldManual's generalized terminal UI automation knack, which preserves the
  test architecture while correcting the reusable boundary model.

## Source Tracking

After first transport, maintain this section as an append-only history.

### Local Mitigation

FieldManual imported the reusable controller, renderer, framebuffer,
drive-and-observe, and testing patterns. Its stock guidance requires explicit
opt-in, correlated completion, bounded input, authorization, and
privilege-aware operation; it does not copy the target's wire protocol or
implementation.

### Transport And Receipt Log

- 2026-07-23 — Drafted locally; not yet submitted.

### Discussion And Amendments

None.

### Target Disposition

No target disposition has been reported.

### Source Closure

Open.
