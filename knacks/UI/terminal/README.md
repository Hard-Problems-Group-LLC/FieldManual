# Terminal Knacks

These knacks cover terminal protocols, emulator behavior, terminal libraries,
and language-specific APIs.

Start with the layer being changed or diagnosed:

- `ansi.knack.md` — control-sequence grammar shared across terminal families
- `vt100.knack.md` — DEC VT100-era behavior and compatibility limits
- `xterms.knack.md` — modern xterm-family emulator behavior
- `curses.knack.md` — the portable curses programming model
- `curses.api.C.knack.md` — the portable curses C API
- `curses.api.Python.knack.md` — Python's `curses` module and helpers
- `ncurses.knack.md` — the ncurses implementation and extension boundary
- `ncurses.api.C.knack.md` — ncurses C extensions and companion libraries
- `ncurses.api.CPP.knack.md` — the C++ wrapper shipped with ncurses

Keep protocol, implementation, and language-wrapper claims separate. A
terminal bug can sit in the application, screen library, terminfo data,
emulator, transport, locale, or font.
