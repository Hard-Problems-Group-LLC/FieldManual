# Terminal Knacks

Reviewed: 2026-07-23

These knacks cover terminal UI architecture and interaction, terminal
protocols, emulator behavior, screen libraries, and language-specific APIs.

## Application Design

- [Terminal UI Design](terminal-ui-design.knack/terminal-ui-design.overview.knack.md)
  — architecture, capability boundaries, Unicode cells, lifecycle, remote use,
  accessibility, and verification
- [Terminal UI Automation](terminal-ui-design.knack/terminal-ui-design.api.automation.knack.md)
  — headless frame testing and secure, request-correlated drive/observe
  interfaces
- [POSIX Terminal UI Input](terminal-ui-design.knack/terminal-ui-design.api.input.POSIX.knack.md)
  — semantic input, termios lifecycle, bounded raw adapters, sequence parsing,
  signals, and job control
- [Python Curses Rendering](terminal-ui-design.knack/terminal-ui-design.api.rendering.Python.knack.md)
  — one-owner painting, Unicode, lower-right behavior, colors, cursors,
  diagnostics, and testing
- [Keyboard Navigation](keyboard-navigation.knack.md) — focus, selection,
  activation, component conventions, terminal key variability, and
  accessibility
- [Box Drawing and Shading](box-drawing-and-shading.knack.md) — ASCII, ACS,
  DEC graphics, Unicode, CP437, cell width, and fallbacks
- [Turbo Vision–Style TUIs](turbovision-style-tuis.knack/turbovision-style-tuis.overview.knack.md)
  — a classic menu/status/canvas visual idiom built on the general architecture

## Protocols and Emulator Families

- [ANSI Terminal Control Sequences](ansi.knack.md) — control-sequence grammar
  shared across terminal families
- [VT100 Compatibility](vt100.knack.md) — DEC VT100-era behavior and
  compatibility limits
- [XTerm-Family Emulators](xterms.knack.md) — modern xterm-family behavior and
  extensions

## Libraries and APIs

- [Curses Programming Model](curses.knack.md) — portable curses concepts
- [Curses C API](curses.api.C.knack.md) — portable C calls and lifecycle
- [Curses Python API](curses.api.Python.knack.md) — Python's standard module
  and helpers
- [ncurses](ncurses.knack.md) — implementation and extension boundary
- [ncurses C API](ncurses.api.C.knack.md) — C extensions and companion
  libraries
- [ncurses C++ API](ncurses.api.CPP.knack.md) — the wrapper shipped with
  ncurses

## Load Order

For a full-screen application, begin with Terminal UI Design. Add Keyboard
Navigation and Box Drawing when those concerns are active, then load the
specific protocol, emulator, library, language, or visual-style document.

Load Terminal UI Automation only when tests or an authorized operator need to
drive or observe the interface. An attached automation endpoint is a
consequential control plane and must not be treated as harmless presentation
plumbing.

Keep protocol, implementation, and language-wrapper claims separate. A
terminal bug can sit in the application, screen library, terminfo data,
emulator, transport, locale, width policy, input method, font, or automation
boundary.
