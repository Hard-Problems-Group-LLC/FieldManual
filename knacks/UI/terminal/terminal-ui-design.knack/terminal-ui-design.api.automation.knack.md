# Terminal UI Automation and Drive/Observe Interfaces

Reviewed: 2026-07-23

## When to Load This Knack

Load this knack when tests, CI, or an authorized operator need to drive and
observe a terminal UI without relying on image capture or manual keystrokes.
Read the [terminal UI design overview](terminal-ui-design.overview.knack.md)
first.

## Position

Separate a pure controller and renderer from the terminal painter. Tests can
then submit semantic input events and inspect both:

- a frame describing text, cell width, semantic style, cursor, and geometry;
  and
- a deliberately small semantic view describing focus, modes, enabled actions,
  and other observable UI meaning.

This makes headless state and layout verification fast and deterministic. An
attached drive interface is a different and substantially riskier facility:
it can cause every action available through the UI.

## Threat Model

Treat external UI automation as a consequential control plane.

“It only injects keys” is not a security boundary. Keys can save files, approve
changes, invoke subprocesses, delete data, or exercise the privileges of the
hosting process. Observation can disclose every secret visible in the UI.

Defaults:

- expose no automation endpoint, listener, worker, or control artifact unless
  the operator passes an explicit per-process opt-in such as `--automation`;
- prefer in-process headless testing over an externally reachable endpoint;
- authenticate every external controller and authorize the requested
  capability;
- refuse attached automation when the application is elevated by default;
- do not transfer a privileged application's control endpoint to an
  unprivileged user merely because that user invoked elevation; and
- require a recorded, application-specific threat review before enabling an
  elevated or otherwise consequential attached mode.

Privilege separation is preferable when automation must coexist with privileged
work: keep rendering and automation unprivileged, and require the normal
authenticated privileged boundary for each consequential domain operation.

## Reusable Architecture

Keep four interfaces independent:

1. semantic input events;
2. controller transitions;
3. pure frame and semantic rendering; and
4. an attached painter that is the only component allowed to call the terminal
   library.

Headless tests call the same controller and renderer but omit the painter.
Attached automation sends commands to a bounded queue; the terminal owner
consumes both real and injected events fairly. No automation worker calls
curses or another stateful screen library.

The frame representation must follow the Unicode cell-width rules in the
overview. A matrix of one code point per cell is only valid for a deliberately
single-cell character repertoire.

## End-to-End Harness Flow

Build the harness in layers so most failures are reproducible without a
terminal and the remaining terminal boundary stays small.

1. **Define the contract.** The application supplies an initial state, a
   transition from state plus semantic event to new state and outcome, and a
   pure renderer from state plus geometry to frame plus semantic summary.
2. **Exercise transitions directly.** Unit tests cover navigation, modes,
   validation, cancellation, and consequential domain outcomes without a
   painter, endpoint, timing, or thread.
3. **Run complete headless sessions.** A harness accepts correlated semantic
   events, applies them through the real controller, renders after each
   completion—including exit—and returns the associated immutable snapshot.
   Assert meaning on the semantic summary and structure on selected frame
   cells.
4. **Check the physical adapter in a PTY.** Start the actual terminal entry
   point under a pseudo-terminal. Verify initialization, decoded input, resize,
   emitted updates, interrupt, failure teardown, and restored terminal modes.
   A PTY is not a full emulator; use it to test the process boundary, not to
   claim visual compatibility.
5. **Perform a small real-terminal matrix.** On supported terminal families,
   confirm width, color and monochrome mappings, cursor behavior, resize,
   paste, suspend/continue, and clean exit.
6. **Enable attached drive/observe only when needed.** Use it to reproduce a
   defect requiring the real painter or to let an authorized operator and test
   driver inspect the same session. Apply the authentication, authorization,
   privilege, and data controls below.

The conceptual contract can remain language-neutral:

```text
transition(state, semantic_event) -> state, outcome
render(state, geometry) -> frame, semantic_summary
submit(request_id, semantic_event) -> completion(request_id, outcome, frame_sequence)
observe(frame_sequence) -> immutable frame, semantic_summary
paint(frame) -> terminal update
```

`submit` and `observe` are conceptual interfaces, not a required wire protocol.
Headless tests can call them in-process.

### Neutral Scenario

Consider a three-item picker containing `Amber`, `Blue`, and `Cedar`.

- Start at `24x80`; assert the semantic focus is `Amber` and the frame marks
  that row with the focused style.
- Submit `move-down` with request `nav-1`; require completion for `nav-1`, then
  assert focus is `Blue` in the associated snapshot.
- Submit `toggle-selection` with request `select-1`; assert that `Blue` is
  selected while focus remains distinct.
- Change geometry to `10x32`; assert focus stays visible and the renderer uses
  its compact layout without losing the selection.
- Submit `cancel` or `quit`; require a final published state and successful
  terminal restoration rather than a timeout caused by exiting before render.

Run that scenario first as direct controller tests, then through the headless
harness. Use the PTY and real-terminal levels only for the parts they uniquely
cover.

## Command Completion and Snapshots

Correlate completion with the specific submitted command, not merely with “the
next frame.”

For each accepted command:

- assign or validate a unique request identifier;
- enqueue one semantic event with its completion token;
- let the UI owner apply that event in order;
- publish the resulting semantic state and intended frame, including the final
  state when the event exits the UI; and
- acknowledge that token with its outcome and associated frame sequence.

An unrelated timer, resize, real keystroke, or background redraw must not
satisfy the wait. A valid no-op should complete explicitly even when its
visible frame is unchanged. Timeouts must report indeterminate or failed
completion, never success.

Use monotonic frame sequences for observation and change detection, but do not
mistake them for command correlation. Define whether snapshots are immutable
copies and make frame plus semantic data atomic from a reader's perspective.

## Queueing and Fairness

- Bound command and background-result queues.
- Define ordering among real input, injected input, resize, and background
  completion.
- Prevent a continuous real-input stream from starving automation, and prevent
  automation from making the local session unusable.
- Apply backpressure or reject work rather than allowing unbounded memory
  growth.
- Permit cancellation and orderly shutdown without abandoning a waiting
  request.
- Make one controller authoritative; do not let multiple clients race modifier
  state or modes.

Model modifiers and chords as explicit semantic events only when the
application truly supports them. Do not advertise modifier operations that are
recorded but never consumed.

## Endpoint and Protocol Safety

The transport is an implementation choice, not the security model. If a
pathname-based local IPC endpoint is used:

- place it in an application-owned directory with mode `0700`;
- create the directory and endpoint without following attacker-controlled
  links;
- do not unlink an existing object unless its identity and ownership have been
  verified;
- authenticate the peer using a portable application credential or a
  deliberately platform-specific peer-credential mechanism;
- do not rely only on the endpoint file's mode—POSIX does not define pathname
  socket permission enforcement, and implementations differ; and
- remove only the endpoint created by the current instance.

Tie endpoint lifetime to the explicit automation mode:

1. parse `--automation` or an equivalently conspicuous opt-in;
2. complete privilege and configuration checks before creating the endpoint;
3. report that automation is active and where its protected endpoint lives;
4. accept controllers only for that process lifetime; and
5. close the listener and remove the verified endpoint during every orderly
   exit path.

Without the opt-in, starting the utility must not create the listener, socket
path, server thread, discovery record, or capture directory. Avoid enabling
the control plane through an inherited environment variable or surprising
ambient configuration. A test can and should assert both startup modes.

For every protocol:

- bound message length, nesting, collection sizes, geometry, text, and capture
  size;
- require the expected top-level type and reject unknown fields or versions
  according to a documented compatibility policy;
- use timeouts for framing, idle connections, command completion, and writes;
- limit clients and outstanding requests;
- return structured errors without terminating the server loop; and
- record security-relevant enablement, connection, rejection, and shutdown
  events without logging screen contents or secrets.

## Observation and Capture

Frame and semantic data are potentially sensitive. Define:

- which fields are exposed;
- who may observe them;
- whether captures are enabled separately from live observation;
- an application-owned fixed capture location;
- restrictive creation permissions, retention, cleanup, and sharing rules; and
- redaction before persistence, with tests for the application's data classes.

An untracked directory prevents accidental version control; it does not provide
confidentiality. Avoid duplicating sensitive domain values in the semantic
summary merely to make assertions convenient.

Text and structured snapshots are useful because they are diffable and do not
require OCR. They still need the same privacy review as screenshots.

## Verification Strategy

- Unit-test controller transitions and rendering directly, with no endpoint.
- Assert semantic outcomes and structural cells separately.
- Test Unicode width, clipping, styles, cursor policy, and small geometry.
- Test command correlation against unrelated redraws and real input.
- Test no-op, rejected, timed-out, cancelled, and exit-producing commands.
- Test fairness and bounded-queue behavior under sustained load.
- Test malformed, oversized, truncated, and wrong-type protocol messages.
- Test endpoint collision, stale objects, symlinks, cleanup, and peer rejection.
- Test that elevated attached automation is refused by default.
- Compare an attached painter's intended operations with the same headless
  frame, then perform a small real-terminal acceptance test.

## Sharp Edges

- A pure renderer reduces test cost but does not test the terminal emulator or
  physical painter.
- A terminal recording can contain credentials, tokens, hostnames, customer
  data, and command output.
- “Same user” is not equivalent to “same authorized process.”
- A default-off interface can still be dangerous whenever it is enabled.
- Local transport does not remove authentication, input-validation, or
  lifecycle requirements.

## Further Information

- Linux Unix-domain socket permissions and portability warning:
  <https://man7.org/linux/man-pages/man7/unix.7.html>
- XDG base-directory runtime requirements:
  <https://specifications.freedesktop.org/basedir-spec/latest/>
- OWASP input-validation guidance:
  <https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html>
- OWASP logging guidance:
  <https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html>
- CWE-306, Missing Authentication for Critical Function:
  <https://cwe.mitre.org/data/definitions/306.html>
- JSON data-interchange format:
  <https://www.rfc-editor.org/rfc/rfc8259>
