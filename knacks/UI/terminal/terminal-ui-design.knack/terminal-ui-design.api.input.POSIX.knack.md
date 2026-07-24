# POSIX Terminal UI Input

Reviewed: 2026-07-23

## When to Load This Knack

Load this companion when implementing or diagnosing input for a full-screen
terminal UI on POSIX systems. Also load the parent
[design overview](terminal-ui-design.overview.knack.md) and, when decoding
emulator behavior directly, the [xterm-family](../xterms.knack.md) and
[VT100](../vt100.knack.md) knacks.

## Default Boundary

Prefer the input facility of the selected terminal UI or screen library. It can
combine terminfo capabilities, keypad modes, resize handling, mouse events, and
implementation-specific decoding more safely than a small home-grown parser.

Use direct reads from the controlling terminal only when:

- inherited standard input is redirected but an explicitly interactive
  controlling terminal is part of the supported contract;
- the application intentionally owns a raw protocol feature the library does
  not expose; or
- a bounded diagnostic needs to distinguish transport bytes from library
  decoding.

Direct input is not inherently more reliable than curses input. It transfers
decoding, Unicode, modes, signals, and restoration obligations into the
application.

## One Input Owner

Exactly one component should read the terminal. Do not let a curses reader and
a direct file-descriptor reader race for the same byte stream.

Convert library codes or input bytes at the boundary into semantic events:

- navigation and command events;
- committed text;
- paste as a bounded text event;
- mouse or focus events when supported;
- resize;
- interrupt, end-of-input, and transport failure.

Keep implementation-specific numeric key codes inside the adapter. They are not
a stable serialized vocabulary.

## Direct Controlling-Terminal Adapter

When direct POSIX input is justified:

1. Open the controlling terminal deliberately and fail or fall back according
   to the documented non-interactive behavior.
2. Save its complete termios state before changing modes.
3. Prefer cbreak-like behavior when signals such as interrupt should retain
   their terminal-driver meaning; use raw mode only when the application
   intentionally owns those bytes.
4. Wait with a bounded polling primitive so resize, cancellation, and
   background results remain responsive.
5. Read bounded chunks and feed an incremental decoder and terminal-sequence
   state machine.
6. Restore the exact saved state on normal exit, exceptions, interruption, and
   suspension.

An application using both a direct input adapter and a screen library must
coordinate their mode expectations. Changing termios behind a library's back
can invalidate the library's saved state.

## Text and Escape Parsing

Do not parse one byte as one character. UTF-8 input may span reads; combining
sequences and input methods may produce multiple code points for one user
action. Separate committed text from command recognition, and never reinterpret
ordinary non-ASCII text as shortcuts.

`ESC` is ambiguous: it may be a bare Escape key, an Alt/Meta prefix, or the
start of a control sequence. Use a documented, configurable bounded delay and
retain incomplete input across reads. Test the latency tradeoff over remote
connections.

Common xterm-family examples include:

- Page Up: `CSI 5 ~`
- Page Down: `CSI 6 ~`
- Home: `CSI H`, `SS3 H`, `CSI 1 ~`, or `CSI 7 ~`
- End: `CSI F`, `SS3 F`, `CSI 4 ~`, or `CSI 8 ~`

These are examples, not a complete portable key table. Application cursor
mode, emulator settings, modified-key protocols, and terminfo can change what
arrives. Prefer terminfo/library decoding; when a raw parser is necessary,
normalize only explicitly supported sequences and expose unknown sequences in
redacted diagnostics.

Bracketed paste, mouse reporting, focus reporting, and newer keyboard protocols
need explicit negotiation and bounded parsers. Paste contents are untrusted
text, not a sequence of commands.

## Resize, Signals, and Job Control

- Treat resize as an out-of-band geometry event and coalesce repeated notices.
- Define interrupt behavior rather than accidentally swallowing or duplicating
  it.
- On stop, restore shell-facing modes before the process suspends.
- On continue, reacquire geometry, re-enable application modes, and redraw from
  authoritative state.
- Handle hangup, EOF, failed reads, and a lost controlling terminal.
- Do not perform unsafe terminal-library work directly inside a signal handler;
  communicate the event to the owner loop.

## Diagnostics and Testing

- Record the terminal identity, input mode, and redacted byte representation
  for an unrecognized sequence.
- Compare raw bytes with library-decoded events in an isolated diagnostic, not
  with two concurrent production readers.
- Test bare Escape, Alt-prefixed text, Shift-Tab, Enter variants, navigation,
  UTF-8 split across reads, paste, resize, and unknown sequences.
- Test redirected stdin, no controlling terminal, PTYs, SSH, Mosh, stop and
  continue, interrupt, and abrupt disconnect.
- Keep critical navigation available without Alt, function keys, or modified
  sequences.

## Sharp Edges

- `/dev/tty` can be unavailable in containers, services, detached processes,
  and unusual launch environments.
- Cbreak preserves configured special-character handling; it does not promise
  one universal signal policy.
- A short Escape delay improves key decoding but makes a bare Escape key feel
  slower.
- `$TERM` describes a terminal contract, not necessarily the exact emulator.
- A small navigation parser should not be advertised as a general terminal
  protocol implementation.

## Further Information

- POSIX general terminal interface:
  <https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap11.html>
- terminfo manual:
  <https://invisible-island.net/ncurses/man/terminfo.5.html>
- ncurses input manual:
  <https://invisible-island.net/ncurses/man/curs_getch.3x.html>
- xterm control sequences and keyboard modes:
  <https://invisible-island.net/xterm/ctlseqs/ctlseqs.html>
- Python `termios`:
  <https://docs.python.org/3/library/termios.html>
- Python `tty`:
  <https://docs.python.org/3/library/tty.html>
- Python `selectors`:
  <https://docs.python.org/3/library/selectors.html>
