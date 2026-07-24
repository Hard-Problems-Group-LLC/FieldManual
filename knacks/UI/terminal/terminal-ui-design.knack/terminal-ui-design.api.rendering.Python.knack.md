# Python Curses Rendering for Terminal UIs

Reviewed: 2026-07-23

## When to Load This Knack

Load this companion when a Python full-screen UI uses `curses` as its physical
renderer. Read the general [Curses Python API](../curses.api.Python.knack.md)
for call families and the
[terminal UI design overview](terminal-ui-design.overview.knack.md) for
architecture and Unicode cell rules.

## Position

Keep application state, controller transitions, and intended-frame rendering
independent of `curses`. The Python adapter should do only terminal lifecycle,
capability and attribute mapping, input normalization, cursor policy, and
painting.

This lets unit tests verify state and layout without an initialized terminal.
It also prevents an input or rendering workaround from becoming an application
architecture.

## Lifecycle and Ownership

Use `curses.wrapper()` for the ordinary lifecycle. It initializes the screen,
configures common modes and keypad handling, initializes colors when
available, and restores the terminal when the callable returns or raises.
Still define signal, job-control, and forced-termination behavior according to
the parent overview.

Confine all `curses` calls—including input, resize bookkeeping, painting, and
cursor changes—to one owner thread. Background workers and automation
interfaces should enqueue semantic events or results without touching curses.

An optional threaded ncurses build has coarse locking facilities, but Python
applications should not assume their linked library provides or uses them.

## Intended Frame and Unicode

Represent styles by semantic names such as `status`, `focused`, `disabled`, or
`error`. Map those names to color pairs and attributes only after curses is
initialized.

Do not build a frame with `enumerate(text)` and assume every code point advances
one column. The renderer needs an explicit grapheme and terminal-width policy,
continuation cells for width-two content, and defined clipping. Exercise that
policy against the linked curses library and supported terminals.

Reject or visibly replace control characters that are not intentional UI
controls. Keep a plain-ASCII structural fallback.

## Painting

It is reasonable to rebuild the intended frame from authoritative state after
each meaningful transition. Let curses optimize the physical update:

- update each affected window's virtual contents;
- use `noutrefresh()` to stage multiple windows; and
- call `curses.doupdate()` once for the frame.

Avoid writes outside the measured geometry. Handle failures with enough
context—window dimensions, coordinates, text width, style, and active
modes—to distinguish clipping from a capability or lifecycle failure.

### Lower-Right Corner

Python documents that writing with `addch()` or `addstr()` at a window's
lower-right corner can raise `curses.error` after the character or string has
been printed. Do not report this as “the corner cannot be painted.”

Possible policies include:

- reserve the corner and leave it blank;
- catch only the documented lower-right error after ensuring the intended cell
  was written; or
- use an insertion operation for a single fitting cell because it does not
  advance the cursor.

Insertion shifts the remainder of the line and discards its rightmost content,
so use it only with that behavior understood. Test the chosen policy on the
linked curses implementations and with width-two edge cases.

## Colors, Styles, and Cursor

Query color support and available pairs. In an eight-color compatibility
palette, semantic “bright” styles may be approximated with bold, but terminals
do not guarantee that `A_BOLD` means a bright foreground. Attributes such as
dim, underline, reverse, and cursor visibility are also capabilities, not
certainties.

Provide a monochrome mapping and never use color or shade as the only signal.

Hide the hardware cursor only while the interface renders its own focus marker
and no text caret is active. For text entry, deliberately set visibility and
position after painting. Restore the previous state when leaving that mode and
on teardown.

## Input and Resize Coordination

Use keypad decoding and prefer `get_wch()` when Unicode text matters. Normalize
characters and implementation-specific integer constants into semantic events
at the adapter boundary.

A bounded wait can keep the owner loop responsive to resize, injected events,
and background results. Poll those sources fairly; checking a secondary queue
only when terminal input is idle can starve it under sustained typing.

On `KEY_RESIZE`, refresh geometry and rerender without treating resize as a
command, printable character, or reason to dismiss an overlay. Depending on
the environment and library, explicit resize bookkeeping may still be needed.

## Diagnostics and Testing

- Send diagnostics to a separate access-controlled sink, never into stdout or
  stderr while they refer to the owned terminal.
- Unit-test the controller and intended renderer as ordinary pure code.
- Put curses behind a small adapter interface and test painter decisions with
  a recording fake instead of bypassing constructors or patching library
  internals.
- Test attribute mapping after real initialization.
- Use a PTY integration test for lifecycle, input, resize, and teardown.
- Perform a small real-terminal matrix for the supported emulator, locale,
  color, and remote combinations.
- Verify that exceptions and Ctrl-C leave a usable terminal.

## Sharp Edges

- A visible screen does not prove the input path works.
- Catching every `curses.error` can hide genuine geometry and lifecycle bugs.
- Library constants and capabilities vary across implementations.
- Full intended-frame rendering does not require brute-force physical output.
- A fake painter cannot validate terminfo, the linked library, or emulator
  behavior.

## Further Information

- Python `curses` reference:
  <https://docs.python.org/3/library/curses.html>
- Python curses HOWTO:
  <https://docs.python.org/3/howto/curses.html>
- ncurses character-output manual:
  <https://invisible-island.net/ncurses/man/curs_addch.3x.html>
- ncurses insertion manual:
  <https://invisible-island.net/ncurses/man/curs_insch.3x.html>
- ncurses cursor and low-level mode manual:
  <https://invisible-island.net/ncurses/man/curs_kernel.3x.html>
- ncurses color manual:
  <https://invisible-island.net/ncurses/man/curs_color.3x.html>
- ncurses threading notes:
  <https://invisible-island.net/ncurses/man/curs_threads.3x.html>
