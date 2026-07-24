# Turbo Vision–Style Terminal UIs

Reviewed: 2026-07-23

## When to Load This Knack

Load this knack when a full-screen, keyboard-driven terminal interface should
use the visual and interaction idiom associated with Borland Turbo Vision:
strong menu and status bands, a contrasting content canvas, visible hotkeys,
focus bars, cell-level focus, compact dialogs, and restrained character-cell
decoration.

This is a style and composition guide, not a claim of source, widget, or binary
compatibility with Turbo Vision. Read the general
[Terminal UI Design](../terminal-ui-design.knack/terminal-ui-design.overview.knack.md),
[Keyboard Navigation](../keyboard-navigation.knack.md), and applicable
rendering companion first.

## Architecture Before Appearance

Keep the domain, controller, pure intended-frame renderer, and physical
terminal painter separate. A style should be a palette and layout policy over
semantic UI state, not raw color constants scattered through domain code.

Define semantic styles such as:

- application and menu bars;
- content canvas;
- title and column heading;
- focused row;
- focused cell;
- hotkey;
- disabled or secondary text;
- dialog and dialog focus; and
- warning or error.

The painter maps those styles to the capabilities available at runtime.
Headless tests can assert the semantic style and text at a position without
initializing curses.

## Visual Vocabulary

A recognizable compatibility palette often uses:

- a gray or light neutral menu/status background;
- a blue content area;
- yellow or high-contrast headings;
- a cyan or contrasting full-row focus bar;
- a distinct cell at the row-and-column intersection;
- red or otherwise contrasting hotkey letters; and
- line art for dialogs, separators, and scrollbars.

Treat those as design intent. In an eight-color terminal, “light” colors may
need an attribute-based approximation, and bold does not universally mean a
bright foreground. Define a coherent monochrome mapping with reverse,
underline, weight, spacing, and labels; never make color the only state cue.

Use [Box Drawing and Shading](../box-drawing-and-shading.knack.md) to choose
among ASCII, ACS, Unicode, and a deliberately controlled legacy repertoire.

## Composition Patterns

### Stable Bands and Canvas

Use stable menu, status, or command bands around a clearly bounded content
region. Keep important context—current view, mode, dirty state, and available
commands—in predictable positions. Do not let long content silently overwrite
frame rows.

At small geometries, reduce decoration and optional columns before corrupting
the frame. Below the usable minimum, show a plain explanation of the required
geometry and retain a safe exit path.

### Bracketed Hotkeys

Bracketed command labels make keys discoverable, for example `[S]ave`. Style
the key separately and dim or otherwise mark unavailable commands, while
retaining a textual disabled cue for accessibility.

Parse labels structurally rather than by casually searching for brackets.
Escaped brackets, a bracket used as the hotkey itself, localization, and
width-two text all need defined behavior.

### Row and Cell Focus

For tables, a full-row focus bar gives strong vertical orientation. Restyle the
single focused cell so the row-and-column intersection is unambiguous. Keep
focus visible after scroll, resize, filtering, and data refresh.

Do not confuse focus with selection. A multi-select table still needs a
separate selected-state treatment.

### Scrollbar

When a scrollbar adds useful orientation:

- reserve its own column;
- distinguish track, endpoints, and thumb;
- size the thumb from viewport extent relative to total extent;
- position it from viewport offset, not merely focused-row index;
- handle empty, fully visible, and very small ranges; and
- provide textual position information when glyphs or geometry cannot support
  the bar.

### Editing and Confirmation

Mode indicators, explicit save or apply actions, undo, and dirty-exit guards
can fit this style well, but they are application policies rather than Turbo
Vision requirements. Choose them from domain risk and user expectations.

If editing can be locked, explain the lock visibly and keep safe recovery
actions available. Saving must report its real outcome; never treat an
attempted save as a successful state transition.

## Cursor and Painter Discipline

If the interface draws its own row/cell focus, hide the terminal cursor while
no text caret is needed. Show and place the real cursor deliberately for text
entry, then restore the prior policy.

The Python-specific lower-right error behavior, color mapping, one-owner rule,
and test strategy live in
[Python Curses Rendering](../terminal-ui-design.knack/terminal-ui-design.api.rendering.Python.knack.md).
Do not duplicate them in the style implementation.

## Automation and Verification

The pure frame makes visual states inspectable without screenshots. Test:

- menu, content, status, and footer boundaries;
- enabled and disabled hotkeys;
- row focus and cell focus independently;
- scrollbar size and position across viewport ranges;
- dialog stacking and focus restoration;
- monochrome and reduced-decoration mappings;
- too-small geometry and recovery;
- Unicode width and ASCII fallback; and
- text-caret visibility during editing.

For drive/observe testing, follow
[Terminal UI Automation](../terminal-ui-design.knack/terminal-ui-design.api.automation.knack.md).
An attached automation endpoint is a consequential control plane, even when
the visible interface is styled as a simple terminal application.

## Sharp Edges

- Visual resemblance is not compatibility with the original framework.
- CP437 appearance does not justify emitting CP437 bytes to a UTF-8 terminal.
- Dense borders, shade, and saturated color can reduce readability.
- A continuously blinking or misplaced hardware cursor undermines an otherwise
  stable frame.
- A decorative scrollbar that does not represent viewport state is misleading.
- Locking, save, and undo policies must come from the domain, not nostalgia.

## Further Information

- Modern Turbo Vision project:
  <https://github.com/magiblot/tvision>
- Python `curses` reference:
  <https://docs.python.org/3/library/curses.html>
- ncurses manual:
  <https://invisible-island.net/ncurses/man/ncurses.3x.html>
- terminfo manual:
  <https://invisible-island.net/ncurses/man/terminfo.5.html>
- Unicode Box Drawing chart:
  <https://www.unicode.org/charts/PDF/U2500.pdf>
