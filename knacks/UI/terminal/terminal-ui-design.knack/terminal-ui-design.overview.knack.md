# Terminal UI Design

Reviewed: 2026-07-23

## When to Load This Knack

Load this knack when designing, reviewing, or debugging a full-screen
character-cell interface. It covers application architecture, terminal
capabilities, rendering ownership, Unicode, lifecycle safety, remote use, and
the boundary between a UI model and a terminal library.

For a particular layer, also load the applicable
[input](terminal-ui-design.api.input.POSIX.knack.md),
[Python rendering](terminal-ui-design.api.rendering.Python.knack.md), or
[automation](terminal-ui-design.api.automation.knack.md) companion and the
relevant protocol or library knack from the parent directory.

## Mental Model

A terminal UI is a stateful renderer for a character-cell device, not a stream
of decorative `print` calls. Treat these as distinct systems:

1. the application model and durable domain operations;
2. interaction state such as focus, selection, modes, scroll position, and
   open overlays;
3. a layout and rendering model that describes the intended frame;
4. an adapter that maps the frame to the active terminal library and
   capabilities; and
5. a single event loop that owns terminal input, painting, resize, suspension,
   and teardown.

This split keeps domain behavior testable without a terminal, confines
terminal-specific failures, and lets headless tests inspect the same intended
frame that an attached session paints.

## Architecture

Keep the following boundaries explicit.

### Domain and Controller

The domain layer should not import the terminal library. A controller maps
semantic events such as `move-down`, `activate`, `cancel`, or `text-input` to
state transitions. Do not let raw escape sequences or implementation-specific
numeric key codes escape the terminal adapter.

Focus, selection, and activation are separate concepts. A focused item receives
navigation; selected items are marked; activation performs an operation. See
[Keyboard Navigation](../keyboard-navigation.knack.md) for interaction
defaults.

### Pure Layout and Rendering

Prefer a deterministic function from application and interaction state plus
geometry to an intended frame and a small semantic summary. Rendering should
not read from the terminal, perform domain mutations, or depend on elapsed time
that has not been supplied explicitly.

The semantic summary exists for diagnostics and testing. It should expose
meaning needed to verify the interface, not duplicate secrets or the entire
domain model.

### Terminal Adapter

The adapter owns capability lookup, color and attribute mapping, cursor
visibility, physical screen updates, and conversion between library events and
semantic events. Keep direct control sequences out of higher layers.

Use a library and its capability database for the portable core. Use raw
ECMA-48, DEC, or xterm-family sequences only when the feature is understood,
negotiated where possible, restored on exit, and verified on every supported
terminal family.

### One Terminal Owner

Use one thread or serialized execution context for all calls that read from or
write through a curses-like screen library. Other workers may produce domain
events or background results, but they should communicate through bounded
queues. The terminal owner decides when to consume those results and when to
paint.

Optional ncurses threading builds and coarse locks do not make arbitrary
concurrent screen access safe. Use them only under an implementation-specific
design with explicit evidence.

## Model Cells, Not Characters

A Unicode string is not a row of one-column cells. Combining marks, grapheme
clusters, variation selectors, emoji sequences, and East Asian wide characters
break the assumption that one code point equals one displayed cell.

A reusable frame model should define:

- the text or grapheme represented at a cell;
- its measured terminal width;
- continuation cells for width-two content;
- semantic style, not a raw library attribute;
- clipping behavior at both edges; and
- policy for controls, invalid text, ambiguous-width characters, and a cluster
  that does not fit.

Grapheme segmentation and display-width calculation are separate problems, and
real terminals can still disagree. Choose a documented width policy, keep a
plain-ASCII fallback for critical structure, and test the actual emulators and
fonts in scope.

See [Box Drawing and Shading](../box-drawing-and-shading.knack.md) for the
differences among Unicode line art, DEC graphics, curses ACS, and legacy code
pages.

## Capability and Rendering Strategy

Prefer, in order:

1. a maintained UI or screen library that owns diffing, modes, and teardown;
2. its wide-character interface and terminal capability database;
3. capability-backed low-level operations when the high-level API is
   insufficient;
4. well-defined standard or widely implemented control sequences; and
5. emulator-specific behavior only behind detection, configuration, or a
   deliberately narrow support contract.

The order is a risk guide, not a requirement to use curses. A suitable modern
framework may provide a higher-level widget and event model. What matters is
that the project states its portability boundary instead of quietly assuming
one emulator.

Render from authoritative state. It is often simplest to rebuild the intended
frame after each meaningful transition, while the screen library computes a
minimal physical update. For multiple windows, stage their updates and perform
one final flush. Avoid multiple writers and never allow ordinary logs or
subprocess output to interleave with a full-screen display.

## Lifecycle and Failure Safety

Treat terminal state as a resource:

- initialize through the library's supported lifecycle;
- record which modes the application enables;
- handle resize as a geometry change, not an ordinary text or command event;
- restore cursor, keypad, paste, mouse, screen, and terminal modes on normal
  exit and exceptions;
- define behavior for interrupt, termination, hangup, and broken output; and
- on POSIX, handle stop and continue so shell job control does not leave the
  terminal damaged.

A crash-safe wrapper is useful, but it cannot repair every signal, forced
termination, or external writer. Keep an operator recovery procedure simple,
and make failures observable without printing through the owned screen.

## Interaction and Accessibility

Polish comes from predictable state and restraint:

- keep focus visible and movement spatially consistent;
- preserve stable headers, footers, landmarks, and help;
- degrade deliberately at small geometries;
- never encode meaning with color, shade, or cursor shape alone;
- provide a monochrome and reduced-decoration path;
- expose current bindings and important state as text;
- avoid repaint churn that makes screen readers unusable; and
- provide a plain or linear output mode when the full-screen presentation is
  not accessible or stdout is not interactive.

Treat input-method text, pasted text, and command keys as different event
classes. Do not interpret committed non-ASCII text as a sequence of shortcuts.

## Local, Remote, and Cross-Platform Use

Correct `$TERM`, matching terminfo data, locale, font, and a real TTY or PTY are
part of the runtime contract.

Over SSH, verify PTY allocation, the remote terminal description, locale
forwarding, resize, latency, and output volume. The ncurses inline `TERMINFO`
technique works only when compatible ncurses is present and SSH client/server
configuration explicitly permits that environment variable.

Mosh requires a UTF-8-clean path and uses prediction to improve interaction.
Test the interface under Mosh rather than assuming SSH results transfer,
especially for unusual modes and high-churn screens.

On Windows, detect or enable the required virtual-terminal input and output
modes and retain a defined fallback. Do not equate one successful terminal
emulator with support for every Windows console environment.

## Verification Checklist

- Test controller transitions and layout without initializing a terminal.
- Test narrow, short, wide, empty, and large content.
- Test combining and width-two text at clipping boundaries.
- Test colorless and reduced-decoration modes.
- Test resize during overlays, editing, and background updates.
- Test interrupt, exception, stop/continue, normal quit, and output failure.
- Test redirected streams and missing TTY/terminfo cases.
- Test real supported emulators locally and through supported remote
  transports.
- Capture diagnostics through a separate, access-controlled sink.

## Sharp Edges

- `ANSI`, `VT100-compatible`, and `xterm-compatible` are not interchangeable
  support claims.
- UTF-8 transport does not guarantee correct grapheme width or font rendering.
- Repainting the intended frame is different from emitting every cell on every
  update.
- Mixing library-managed output with ad hoc control traffic eventually exposes
  malformed or interleaved sequences.
- A UI framework does not remove the need to restore modes and define signal
  behavior.

## Further Information

- ECMA-48 control functions:
  <https://ecma-international.org/publications-and-standards/standards/ecma-48/>
- ncurses introduction:
  <https://invisible-island.net/ncurses/ncurses-intro.html>
- ncurses FAQ:
  <https://invisible-island.net/ncurses/ncurses.faq.html>
- terminfo manual:
  <https://invisible-island.net/ncurses/man/terminfo.5.html>
- xterm control sequences:
  <https://invisible-island.net/xterm/ctlseqs/ctlseqs.html>
- Unicode text segmentation:
  <https://www.unicode.org/reports/tr29/>
- Unicode East Asian Width:
  <https://www.unicode.org/reports/tr11/>
- Windows console virtual-terminal sequences:
  <https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences>
- Mosh:
  <https://mosh.org/>
- OpenSSH client configuration:
  <https://man.openbsd.org/ssh_config>
