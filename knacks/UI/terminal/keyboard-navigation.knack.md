# Keyboard Navigation for Terminal UIs

Reviewed: 2026-07-23

## When to Load This Knack

Load this knack when designing or reviewing keyboard interaction for terminal
menus, lists, forms, trees, tables, dialogs, editors, dashboards, pickers, or
command palettes.

Use it with the [Terminal UI Design](terminal-ui-design.knack/terminal-ui-design.overview.knack.md)
overview and the applicable input or library companion.

## Mental Model

Keep three states distinct:

- **focus** identifies what receives the next navigation or command event;
- **selection** identifies one or more marked choices; and
- **activation** opens, commits, confirms, or performs an action.

Moving a highlight should not silently execute an expensive or destructive
operation. In a multi-select component, moving focus should not erase the
selection.

WAI-ARIA's composite-widget guidance is a useful cross-interface analogy, not a
terminal protocol: Tab and Shift-Tab move among major components, while arrow
keys navigate inside the focused component. This reduces tab stops and gives
the screen a predictable focus order.

## Default Key Meanings

Use established component behavior over novelty, and document intentional
exceptions.

| Key | Default role |
| --- | --- |
| Tab / Shift-Tab | Move forward or backward among major regions and fields |
| Arrow keys | Move within the focused list, tree, grid, tab set, or menu |
| Home / End | Move to the logical first or last item, column, or line edge |
| Page Up / Page Down | Move by a viewport-sized or other documented large increment |
| Space | Toggle, mark, pause, or select without activation |
| Enter | Activate, open, confirm, submit, or deliberately enter edit mode |
| Escape | Dismiss, cancel, or back out one reversible interaction level |

These are defaults, not permission to overload every component with every key.
Show active bindings in help or a stable command area, and provide an alternate
path for important actions.

## Focus Movement

Make focus order match the visual and reading order.

- Tab should enter a composite at its selected item, remembered focus, or
  documented initial item.
- Arrow keys then move within that composite.
- Tab leaves for the next major region; it should not visit hundreds of list
  rows or table cells.
- Keep the focused item visible after movement and resize.
- When a modal surface opens, move focus into it; when it closes, restore focus
  to the invoking context when that context still exists.
- Make the focus indicator visible without relying on color alone.

Shift-Tab is commonly represented by the terminfo `key_btab` capability and
often by `CSI Z`, but modified-key modes can change it and some terminals do not
report it distinctly. Always provide another way to move backward.

## Focus, Selection, and Activation

Selection may follow focus when the component is single-select, preview is
cheap, and the result is immediately understandable. Keep them separate when:

- multiple items can be selected;
- changing selection performs work;
- preview has significant cost or side effects; or
- movement must not discard a selection set.

A useful multi-select pattern is arrows for focus, Space for toggle, and Enter
for the default action. Modifier-based range selection can be an enhancement,
but it should not be the only usable path because modified navigation keys vary
across terminal environments.

Disabled items should be visibly and textually identified. Whether focus can
reach them depends on the component: reaching one can help explain its presence,
but activation must remain impossible.

## Component Conventions

### Menus and Dialogs

- Up and Down move among menu items; Enter activates; Escape dismisses.
- Tab moves among dialog fields, controls, and button groups.
- Destructive confirmation must be explicit and distinguishable from ordinary
  navigation.
- A default button must not make an accidental Enter destructive.

### Lists and Pickers

- Arrows move focus.
- Home and End jump to the logical extremes.
- Page keys move by a documented large increment while preserving orientation.
- Space toggles a mark in multi-select lists.
- Enter opens or accepts the focused item.

### Trees

- Right expands a collapsed node or moves into it.
- Left collapses an expanded node or moves to its parent.
- Enter activates when activation is distinct from expansion.
- Preserve focus by stable item identity when the tree changes.

### Grids and Tables

- Arrows move by cell or row according to the documented focus model.
- Define Home, End, and page keys at row, column, or viewport scope
  consistently.
- Tab normally leaves the grid; it may move among cells only in an explicit
  cell-editing mode.
- Keep the logical column when paging when practical.

### Text Entry

Text editing has stronger conventions than ordinary navigation. Home and End
normally mean line edges; arrows move the caret; Backspace and Delete edit
text. Do not use printable text as application shortcuts while an editor owns
focus unless a visible mode explicitly says so.

Treat committed input-method text and bounded paste as text events. Do not
split them into command keystrokes.

## Back, Cancel, Interrupt, and Quit

These are different operations:

- **back** moves to a parent view or prior mode;
- **cancel** abandons a reversible in-progress interaction;
- **interrupt** stops current work according to the application's signal
  contract; and
- **quit** exits the application, with confirmation for unsaved or
  consequential state.

Escape is normally back or cancel, one level at a time. A visible `q` command
fits pager-like and viewer-like applications. Ctrl-C should retain a clear
interrupt or emergency-exit meaning. Do not make one ambiguous Escape byte an
undocumented destructive quit.

## Terminal Encoding Boundary

The terminal receives a combination of keyboard layout, operating-system
settings, emulator behavior, active modes, transport, and library decoding.

- Return can arrive as carriage return, line feed, or a keypad Enter event.
- Escape can be a key, an Alt/Meta prefix, or the beginning of a sequence.
- Home, End, and page keys have multiple historical encodings.
- xterm `modifyOtherKeys` and newer keyboard protocols can change modified
  keys, including Shift-Tab.
- AltGr, Option, Command, and function-layer behavior differs by platform.

Prefer semantic events decoded through the terminal library and terminfo.
When parsing directly, follow the
[POSIX Input](terminal-ui-design.knack/terminal-ui-design.api.input.POSIX.knack.md)
companion. Do not make essential navigation depend only on Alt, Option,
function keys, or one modified sequence.

## Accessibility and Discoverability

- Keep all actions reachable from the keyboard.
- Align focus order with reading order.
- Provide text labels for focus, selection, disabled state, errors, and
  progress.
- Do not communicate state only with color, inverse video, animation, or a
  glyph whose name is unclear to assistive technology.
- Avoid high-frequency redraws and cursor motion when content has not changed.
- Offer a plain or linear mode for screen-reader and non-interactive use when
  the application can do so.
- Let users inspect and, for long-lived tools, configure bindings.
- Do not trap Tab, Escape, or interrupt in a mode with no visible way out.

## Verification Checklist

- Exercise every component using only the documented keyboard paths.
- Verify focus remains visible and selection survives focus movement.
- Verify modal focus entry and restoration.
- Test no items, one item, disabled items, long lists, resize, and dynamic
  removal of the focused item.
- Test Enter variants, bare Escape, Alt-prefixed text, Shift-Tab, Home, End,
  page keys, and unknown sequences.
- Test non-US layouts, input methods, paste, compact keyboards, and remote
  transports that matter to the support contract.
- Test monochrome, reduced-decoration, and screen-reader-oriented modes.
- Verify destructive actions require an intentional activation step.

## Further Information

- W3C APG keyboard-interface guidance:
  <https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/>
- ncurses input manual:
  <https://invisible-island.net/ncurses/man/curs_getch.3x.html>
- terminfo key capabilities:
  <https://invisible-island.net/ncurses/man/terminfo.5.html>
- xterm control sequences and modified keys:
  <https://invisible-island.net/xterm/ctlseqs/ctlseqs.html>
- Windows console virtual-terminal input:
  <https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences>
- Apple Terminal keyboard settings:
  <https://support.apple.com/guide/terminal/trmlkbrd/mac>
- Mosh:
  <https://mosh.org/>
