# ncurses

## When to Load This Knack

Load this knack when an application depends on the ncurses implementation,
wide-character libraries, extended colors, resize behavior, companion
libraries, or ncurses terminfo tools.

## Related API Knacks

- `ncurses.api.C.knack.md` covers the C extensions and companion libraries.
- `ncurses.api.CPP.knack.md` covers the shipped C++ wrapper.
- `curses.api.Python.knack.md` covers Python's curses wrapper, which commonly
  uses ncurses on Unix-like systems.

## Mental Model

ncurses is both:

- a curses-compatible screen library; and
- a terminal-capability ecosystem containing terminfo data, compiler and
  query tools, tests, and implementation extensions.

An application may merely link ncurses while using a portable subset, or it
may depend on ncurses-only functions and behavior. Document the boundary.

## What ncurses Adds

- wide-character builds and APIs;
- implementation-specific color, resize, key, and mouse features;
- terminfo management and diagnostic tools;
- panel, menu, and form libraries; and
- portability work across many real Unix-like environments.

Prefer the wide-character family for Unicode-capable applications unless a
specific compatibility requirement prevents it.

## Useful Tools

- `infocmp` inspects and compares terminal descriptions.
- `tic` compiles terminfo source.
- `toe` lists entries.
- `tput` performs small capability queries or emissions.
- `tack` and `vttest` support deeper terminal investigation.

Treat these as diagnostic tools, not evidence that every environment uses the
same implementation or database.

## Sharp Edges

- ncurses is not itself POSIX; X/Open Curses and implementation extensions
  have distinct boundaries.
- BSD, vendor, and embedded curses implementations can differ.
- Wide and narrow libraries are not interchangeable.
- Color claims must agree with terminfo and the built library.
- Resize, mouse, and extended-color behavior expose portability differences
  quickly.

## Debugging Checklist

- Verify the linked library variant.
- Inspect the active terminfo entry.
- Reproduce display and key behavior with reference tools.
- Separate portable calls from ncurses extensions.
- Check the capability database when raw sequences work but ncurses output
  does not.

## Further Information

- ncurses project: <https://invisible-island.net/ncurses/>
- ncurses FAQ:
  <https://invisible-island.net/ncurses/ncurses.faq.html>
- ncurses `initscr` manual:
  <https://invisible-island.net/ncurses/man/curs_initscr.3x.html>
- ncurses `getch` manual:
  <https://invisible-island.net/ncurses/man/curs_getch.3x.html>
- ncurses terminfo manual:
  <https://invisible-island.net/ncurses/man/terminfo.5.html>
- X/Open `<curses.h>`:
  <https://pubs.opengroup.org/onlinepubs/7908799/xcurses/curses.h.html>
- VTTEST project:
  <https://invisible-island.net/vttest/>
