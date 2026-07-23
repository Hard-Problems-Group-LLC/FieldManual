# ANSI Terminal Control Sequences

## When to Load This Knack

Load this knack when reading, writing, or debugging raw terminal control
sequences. It is useful when output is corrupted or when a behavior may belong
to a standard control language, a DEC private mode, or an emulator extension.

## Mental Model

Terminal traffic is a byte stream containing printable text, control bytes,
and control sequences. The phrase "ANSI escapes" often hides several layers:

- ASCII C0 controls such as BEL, BS, CR, and LF;
- ECMA-48 or ISO 6429 control functions such as cursor movement, erase
  operations, and Select Graphic Rendition;
- DEC private modes inherited from VT-series terminals; and
- emulator-specific extensions, especially from xterm-family implementations.

`ESC [ 31 m` is broadly portable as an SGR-style sequence. An alternate-screen
mode such as `ESC [ ? 1049 h` belongs to a private extension layer and has a
different portability promise.

Treat a terminal as a state machine. Cursor position, origin and wrap modes,
scrolling regions, insert behavior, current attributes, and character-set
selection all affect the next bytes.

## Sequence Families

- Single-byte C0 controls such as `BEL`, `BS`, `HT`, `LF`, `CR`, and `ESC`.
- `ESC` sequences, where following bytes select a function.
- `CSI` sequences, commonly represented in seven-bit form as `ESC [`.
- `OSC` strings for commands such as window-title updates.
- `DCS` and related strings for longer structured payloads.

Within a typical `CSI` sequence, parameter bytes contain digits and
semicolons, optional intermediate bytes refine the command, and the final byte
selects the function.

Examples:

- `ESC [ H` or `ESC [ 1 ; 1 H` moves the cursor home.
- `ESC [ 2 J` erases the display.
- `ESC [ 31 m` selects a red foreground in the common palette model.
- `ESC [ 0 m` resets rendition attributes.

## Practical Guidance

Prefer terminfo or a screen library when portability matters. Literal
sequences are reasonable for a known terminal family, a feature with no useful
capability abstraction, or direct protocol diagnosis.

Keep standard and private layers distinct:

- basic movement, erasing, and rendition are commonly ECMA-48 behavior;
- alternate screens, mouse tracking, bracketed paste, titles, hyperlinks, and
  clipboard controls are commonly private extensions.

Be conservative with color. Indexed and direct-color conventions are widely
implemented but do not all share one historical standard. Check the active
terminal description and emulator documentation.

## Sharp Edges

- "ANSI" does not mean every sequence a terminal accepts.
- Some sequences query state, change modes, or affect the host through titles
  and clipboard integration; do not replay unknown control traffic blindly.
- UTF-8 text and terminal control are separate layers.
- A correct sequence can still behave incorrectly when `$TERM` or terminfo
  does not match the emulator.

## Debugging Checklist

- Capture the exact bytes and distinguish literal `ESC` from printable text.
- Classify the sequence as standard, DEC private, or emulator-specific.
- Confirm `$TERM` matches the actual terminal.
- Compare support for the exact control or mode across emulators.
- Diagnose character-set selection separately from cursor-control behavior.

## Further Information

- ECMA-48, Control Functions for Coded Character Sets:
  <https://www.ecma-international.org/wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf>
- DEC VT100 User Guide, programmer information:
  <https://vt100.net/docs/vt100-ug/chapter3.html>
- DEC VT220 Programmer Reference Manual:
  <https://vt100.net/docs/vt220-rm/contents.html>
- XTerm control sequences:
  <https://invisible-island.net/xterm/ctlseqs/ctlseqs.html>
- VTTEST manual:
  <https://invisible-island.net/vttest/manpage/vttest.html>
