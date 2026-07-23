# ncurses C++ API

## When to Load This Knack

Load this knack when code uses the C++ wrapper shipped with ncurses, including
headers such as `cursesw.h`, `cursesapp.h`, `cursesp.h`, `cursesf.h`, or
`cursesm.h`.

## Mental Model

The ncurses C++ layer is an older object-oriented wrapper over the C library,
not a separate modern terminal framework. It provides:

- window and pad classes over `WINDOW *`;
- application, panel, menu, and form classes;
- exception wrappers for C error results; and
- inline conveniences and overloads.

The underlying curses lifecycle, terminal state, capabilities, and portability
limits still apply.

## Headers and Libraries

- `cursesw.h` — core window, color-window, and pad wrappers
- `cursesapp.h` — `NCursesApplication`
- `cursesp.h` — panel wrappers
- `cursesm.h` — menu wrappers
- `cursesf.h` — form and field wrappers
- `cursslk.h` — soft-label helpers
- `etip.h` — exception types

Common installations provide `libncurses++` and a wide
`libncurses++w` variant. Match wrapper, core, panel, menu, and form libraries
to the same narrow or wide model.

## Class Families

### Windows and Pads

`NCursesWindow` wraps core window behavior. Related classes provide color
defaults, pads, and framed pads. The programming model remains windows,
cursor position, drawing, and refresh.

### Application

`NCursesApplication` supports a subclass-oriented application structure with
initialization hooks, optional soft labels, and a `run()` body. Use it when
the application accepts framework-style inheritance; prefer a smaller C or
C++ wrapper when it does not.

### Panels

`NCursesPanel` wraps overlapping windows and depth ordering. Keep panel and
window ownership aligned.

### Menus and Forms

Menu classes wrap item collections, navigation, callbacks, and user data.
Form classes wrap fields, field types, validation, and navigation.

### Exceptions

`etip.h` provides types such as `NCursesException`,
`NCursesPanelException`, `NCursesMenuException`, and
`NCursesFormException`. The original failure still comes from the C library;
the wrapper changes how it is surfaced.

## Practical Guidance

Inspect the installed headers for the exact supported release. Online
documentation for this wrapper is much thinner than documentation for the C
API.

Prefer the C API when portability, documentation coverage, and team
familiarity matter more than wrapper structure. Before relying on normal C++
value semantics, inspect constructors, destructors, copy behavior, and
ownership in the actual headers.

## Sharp Edges

- This is not a contemporary cross-platform widget toolkit.
- Header and implementation details are often the primary reference.
- Narrow and wide wrapper libraries are easy to mix incorrectly.
- Older ownership conventions may not match smart-pointer expectations.
- Exceptions do not remove curses' global state and teardown obligations.

## Further Information

Official wrapper-specific material is limited; pair these sources with the
installed headers for the supported release.

- ncurses project: <https://invisible-island.net/ncurses/>
- ncurses release announcements:
  <https://invisible-island.net/ncurses/announce.html>
- ncurses FAQ:
  <https://invisible-island.net/ncurses/ncurses.faq.html>
- ncurses archives:
  <https://invisible-island.net/archives/ncurses/>
- GNU ncurses releases:
  <https://ftp.gnu.org/gnu/ncurses/>
