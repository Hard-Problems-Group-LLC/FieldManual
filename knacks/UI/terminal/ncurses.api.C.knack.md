# ncurses C API

## When to Load This Knack

Load this knack when C code intentionally depends on ncurses extensions,
wide-character variants, companion libraries, or implementation tools. Use
`curses.api.C.knack.md` for the portable baseline.

## Build Boundary

The main header remains `<curses.h>`. Companion libraries add:

- `<panel.h>` for stacked windows;
- `<menu.h>` for menus; and
- `<form.h>` for forms.

Choose narrow or wide libraries deliberately. Unicode-oriented applications
normally use `libncursesw` and matching `panelw`, `menuw`, and `formw`
libraries where needed.

If source uses ncurses-only calls, state that in build configuration instead
of advertising a generic curses requirement.

## Wide-Character Families

The wide build includes:

- `get_wch()` and `wget_wch()` for input;
- `add_wch()` and `wadd_wch()` for output;
- `setcchar()` and `getcchar()` for complex cells; and
- wide-string functions such as `waddnwstr()` and `get_wstr()`.

Choose the wide model at design time when Unicode is required. Mixing narrow
and wide assumptions later creates subtle rendering and input defects.

## Extensions

### Color

Alongside portable color pairs, supported builds may provide extended-color
functions such as `init_extended_pair()` and `init_extended_color()`. These
are implementation-specific and require capability and version checks.

### Keys and Resize

ncurses adds functions such as `has_key()` and `define_key()`.

Resize handling commonly uses:

- `is_term_resized()` to compare proposed and current dimensions;
- `resize_term()`; and
- `resizeterm()`.

Bring resize handling close to the event loop and window-layout logic.

### Mouse

Mouse support includes event masks, `getmouse()`, `ungetmouse()`, and
implementation-defined protocol interaction. Treat terminal mouse reporting
as negotiated capability, not a universal input source.

## Panels, Menus, and Forms

- Panels add stacking and depth ordering for overlapping windows.
- Menus provide item collections and navigation.
- Forms provide fields, validation, and navigation.

These are separate libraries layered on ncurses. Link selection and order
matter, and their lifecycle objects must remain aligned with the underlying
windows.

## Terminfo Tools

Use:

- `infocmp` to inspect or compare entries;
- `tic` to compile terminfo source;
- `toe` to enumerate entries; and
- `tput` for bounded capability probes.

These tools often establish whether a defect is in capability data rather
than application code.

## Sharp Edges

- Source-compatible curses code may still depend on ncurses behavior.
- Gate extensions with build checks or `NCURSES_VERSION` as appropriate.
- Wide and narrow libraries must not be mixed accidentally.
- Side-library link order can matter.
- Resize, mouse, and extended colors are common portability fault lines.

## Further Information

- ncurses project: <https://invisible-island.net/ncurses/>
- ncurses FAQ:
  <https://invisible-island.net/ncurses/ncurses.faq.html>
- ncurses programming HOWTO:
  <https://invisible-island.net/ncurses/NCURSES-Programming-HOWTO.html>
- ncurses initialization manual:
  <https://invisible-island.net/ncurses/man/curs_initscr.3x.html>
- ncurses input manual:
  <https://invisible-island.net/ncurses/man/curs_getch.3x.html>
- ncurses wide-character output manual:
  <https://invisible-island.net/ncurses/man/curs_add_wch.3x.html>
- ncurses resize manual:
  <https://invisible-island.net/ncurses/man/resizeterm.3x.html>
