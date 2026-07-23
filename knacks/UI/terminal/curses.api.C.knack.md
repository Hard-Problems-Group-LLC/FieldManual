# Curses C API

## When to Load This Knack

Load this knack when writing or reviewing C code against the portable curses
interface. Read `curses.knack.md` first for the screen-management model.

## Portability Boundary

The portable API is declared through `<curses.h>`. Real implementations may
provide macros, extensions, and different wide-character support. Keep
ncurses-only calls separate and consult `ncurses.api.C.knack.md` when the
program intentionally depends on them.

## Core State and Types

- `WINDOW` represents a window or pad.
- `SCREEN` represents an explicit terminal screen context.
- `chtype` and `attr_t` carry character and attribute data.
- `cchar_t` supports complex wide-character cells where available.
- `stdscr` is the default full-screen window.
- `curscr` is the library's view of the physical screen.
- `LINES`, `COLS`, `COLORS`, and `COLOR_PAIRS` describe initialized state.

Treat globals as library state, not independent sources of truth.

## Lifecycle

Common single-screen programs use:

1. `initscr()`;
2. mode setup such as `cbreak()`, `noecho()`, and `keypad()`;
3. the application loop; and
4. `endwin()` on every exit path.

Use `newterm()`, `set_term()`, and `delscreen()` when explicit screen objects
are required. `def_prog_mode()`, `def_shell_mode()`, `reset_prog_mode()`, and
`reset_shell_mode()` help when temporarily returning to shell behavior.

## Windows and Pads

- `newwin()`, `delwin()`, `mvwin()`, and `dupwin()` manage windows.
- `subwin()` and `derwin()` create children that can share backing storage.
- `newpad()`, `prefresh()`, and `pnoutrefresh()` support larger off-screen
  surfaces.
- `touchwin()`, `redrawwin()`, `wsyncup()`, and `wsyncdown()` affect repaint
  and synchronization.

Shared storage means a child-window bug may be a parent/child ownership issue,
not merely a repaint issue.

## Drawing and Refresh

Output functions appear in related families:

- `addch()`, `addstr()`, `waddnstr()`, and movement-prefixed forms;
- `printw()` and `wprintw()`;
- `box()`, `border()`, `hline()`, and `vline()`; and
- `erase()`, `clrtoeol()`, and `clrtobot()`.

Separate mutation from display:

- `wrefresh()` stages and flushes one window;
- `wnoutrefresh()` stages without flushing; and
- `doupdate()` flushes all staged changes.

For several windows, prefer a batch of `wnoutrefresh()` calls followed by one
`doupdate()`.

## Input and Terminal Modes

- `getch()`, `wgetch()`, and `ungetch()` form the basic key path.
- `keypad()` enables translation into `KEY_*` codes.
- `cbreak()`, `raw()`, `echo()`, `noecho()`, `halfdelay()`, `nodelay()`, and
  `timeout()` shape line discipline and blocking.
- `meta()` and `notimeout()` influence character and escape handling.

Keep input results in `int` or a wider suitable type; `KEY_*` values do not
fit in an eight-bit `char`.

## Attributes, Colors, and Wide Characters

Attributes include `attron()`, `attroff()`, `standout()`, and window-scoped
`wattr_*` forms. Color setup uses `start_color()`, `init_pair()`,
`pair_content()`, and `COLOR_PAIR()`.

Wide-character implementations add functions such as `setcchar()`,
`wadd_wch()`, and `win_wch()`. Their correctness depends on locale, terminal
capabilities, and the library build.

Prefer window-scoped calls when ownership clarity matters.

## Terminfo Access

Lower-level capability access includes:

- `setupterm()`;
- `tigetstr()`, `tigetnum()`, and `tigetflag()`; and
- `tparm()` and `putp()`.

Use direct terminfo output sparingly. Mixing unmanaged terminal output with
curses repainting can invalidate the screen model.

## Sharp Edges

- Some calls may be macros; do not assume ordinary function semantics.
- Coordinates are row first, then column.
- Drawing without refresh changes only library state.
- Subwindows share storage.
- Raw writes and incomplete teardown corrupt terminal state.
- Wide-character output requires a compatible locale and implementation.

## Further Information

- X/Open `<curses.h>`:
  <https://pubs.opengroup.org/onlinepubs/7908799/xcurses/curses.h.html>
- X/Open terminfo:
  <https://pubs.opengroup.org/onlinepubs/7908799/xcurses/terminfo.html>
- ncurses initialization manual:
  <https://invisible-island.net/ncurses/man/curs_initscr.3x.html>
- ncurses window manual:
  <https://invisible-island.net/ncurses/man/curs_window.3x.html>
- ncurses input manual:
  <https://invisible-island.net/ncurses/man/curs_getch.3x.html>
- ncurses color manual:
  <https://invisible-island.net/ncurses/man/curs_color.3x.html>
