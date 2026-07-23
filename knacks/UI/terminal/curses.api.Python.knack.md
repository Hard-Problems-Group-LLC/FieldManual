# Curses Python API

## When to Load This Knack

Load this knack when writing Python against the standard `curses` module or
diagnosing how Python maps to an underlying curses implementation.

## Mental Model

Python exposes the C model directly:

- module functions manage lifecycle, terminal modes, colors, and windows;
- window objects handle most drawing, refresh, and input;
- `curses.ascii` provides character helpers;
- `curses.panel` adds a stacking model; and
- `curses.textpad` provides a small text-entry helper.

The wrapper does not remove curses' global terminal state, coordinate order,
refresh semantics, locale requirements, or implementation differences.

## Lifecycle

Prefer `curses.wrapper()` for ordinary programs. It initializes curses,
passes the main window to a callable, and restores terminal state when an
exception escapes.

Manual control uses `curses.initscr()` and `curses.endwin()`. Window and pad
creation uses `curses.newwin()` and `curses.newpad()`. Color setup commonly
uses `curses.start_color()` plus default-color policy appropriate to the
implementation.

Set the process locale before initialization when Unicode behavior matters.

## Window Operations

Common methods include:

- `addch()`, `addstr()`, `insstr()`, `hline()`, `vline()`, and `border()`;
- `move()`, `clear()`, `erase()`, `refresh()`, and `noutrefresh()`;
- `subwin()` and `derwin()`; and
- `getch()`, `getkey()`, `get_wch()`, and `instr()`.

For several windows, call `noutrefresh()` on each and then
`curses.doupdate()`.

## Input and Modes

Module-level functions such as `cbreak()`, `raw()`, `echo()`, `noecho()`,
`halfdelay()`, and `nl()` still control global terminal behavior.

Call `window.keypad(True)` to decode multibyte terminal sequences into
logical key codes. Use `get_wch()` when wide-character input matters, and
handle both character and integer key results.

Mouse support depends on terminal negotiation and `mousemask()`. Do not assume
pointer events are available merely because the emulator supports them.

## Attributes and Colors

The module exposes attributes such as `A_BOLD`, `A_REVERSE`, and
`A_UNDERLINE`, along with ACS glyphs and color helpers such as
`color_pair()`, `init_pair()`, and `pair_content()`.

Values such as `LINES`, `COLS`, `COLORS`, and `COLOR_PAIRS` are meaningful
only after the relevant initialization.

## Companion Modules

`curses.ascii` helps classify control characters and raw byte values.

`curses.panel` adds explicit depth ordering. Retain Python references to panel
objects; garbage collection can remove an otherwise active panel. Update the
panel stack, then call `curses.doupdate()`.

`curses.textpad.Textbox` is suitable for small text fields. It is not a full
widget or application framework.

## Sharp Edges

- `curses.error` often carries little context; record dimensions, cursor
  position, and active modes near failures.
- Coordinates are y first, then x.
- Availability differs across operating systems and Python builds.
- Unicode depends on locale, terminfo, emulator, and linked library support.
- The apparent Python defect may be inherited from the C implementation.

## Further Information

- Python `curses` reference:
  <https://docs.python.org/3/library/curses.html>
- Python `curses.panel` reference:
  <https://docs.python.org/3/library/curses.panel.html>
- Python `curses.ascii` reference:
  <https://docs.python.org/3/library/curses.ascii.html>
- Python curses HOWTO:
  <https://docs.python.org/3/howto/curses.html>
- Python curses C API:
  <https://docs.python.org/3/c-api/curses.html>
