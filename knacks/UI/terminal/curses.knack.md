# Curses Programming Model

## When to Load This Knack

Load this knack when building or debugging a full-screen terminal application
and the portable curses model matters more than raw escape sequences.

## Related API Knacks

- `curses.api.C.knack.md` covers the portable C API.
- `curses.api.Python.knack.md` covers Python's `curses` module.
- `ncurses.knack.md` covers the most common implementation and its
  extensions.

## Mental Model

Curses is a screen-management abstraction:

- the application updates windows and pads;
- the library compares desired state with its terminal state model; and
- the library emits terminal-specific controls to reconcile them.

Think in three layers:

1. application intent, such as drawing a border or reading a function key;
2. curses calls, windows, pads, and refresh behavior; and
3. terminal capabilities selected through terminfo or equivalent data.

Many apparent curses bugs are mismatched `$TERM` or terminfo behavior.

## Core Pattern

Initialization and teardown:

- initialize with `initscr` or `newterm`;
- configure input and echo modes;
- draw into windows or pads;
- refresh the virtual screen; and
- restore terminal state on every exit path.

Input:

- `keypad` enables decoding of multibyte key sequences into logical keys.
- `cbreak`, `raw`, `echo`, timeouts, and blocking modes affect what input
  calls observe.

Output:

- drawing normally changes library-managed state;
- `refresh` updates one window and the display;
- `noutrefresh` stages changes; and
- `doupdate` flushes a batch efficiently.

## Good Uses

- portable full-screen text interfaces;
- cursor and region updates;
- abstract key decoding;
- colors and text attributes supported by the implementation; and
- incremental repaint.

Curses cannot correct a false terminal description.

## Sharp Edges

- Raw output can invalidate curses' model of the screen.
- Subwindows may share backing storage with parents.
- Teardown failures can leave the terminal in raw or no-echo mode.
- Curses standardization is not identical to POSIX, and implementations vary.
- Unicode behavior depends on locale, wide-character support, and terminfo.

## Debugging Checklist

- Confirm `$TERM` and inspect terminfo.
- Check initialization and teardown symmetry.
- Inspect `cbreak`, `raw`, `echo`, `keypad`, and timeout settings.
- Look for missing `refresh` or `doupdate` calls.
- Minimize raw writes while curses owns the terminal.
- Separate portable behavior from implementation extensions.

## Further Information

- X/Open `<curses.h>`:
  <https://pubs.opengroup.org/onlinepubs/7908799/xcurses/curses.h.html>
- X/Open terminfo:
  <https://pubs.opengroup.org/onlinepubs/7908799/xcurses/terminfo.html>
- ncurses `initscr` manual:
  <https://invisible-island.net/ncurses/man/curs_initscr.3x.html>
- ncurses terminfo manual:
  <https://invisible-island.net/ncurses/man/terminfo.5.html>
- ncurses FAQ:
  <https://invisible-island.net/ncurses/ncurses.faq.html>
