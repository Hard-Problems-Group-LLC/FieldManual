# XTerm-Family Emulators

## When to Load This Knack

Load this knack when working with a terminal emulator that follows xterm
behavior directly or loosely. It is especially relevant to alternate screens,
mouse tracking, bracketed paste, focus events, titles, hyperlinks, and
clipboard controls.

## Mental Model

XTerm is both a program and a reference implementation for many conventions
layered on older DEC behavior. An xterm-family environment combines:

- VT100 and VT220 semantics;
- private control sequences and modes;
- terminfo or termcap descriptions;
- emulator configuration; and
- features such as mouse protocols, clipboard helpers, and UTF-8 rendering.

"Xterm-compatible" is not binary. Emulators may support the same sequence
families with different scrollback, resize, security, or edge-case behavior.

## Common Feature Families

### Alternate Screen

Private modes such as `1047`, `1048`, and `1049` control alternate-screen and
cursor-save behavior. Editors and pagers commonly use them. Scrollback
behavior is emulator policy, not a universal guarantee.

### Bracketed Paste

Mode `2004` marks pasted text so a shell or full-screen application can
distinguish it from typing. This reduces accidental execution and preserves
multiline input behavior when the application handles it correctly.

### Mouse and Focus Reporting

XTerm defines several mouse modes and encodings, including SGR mouse
reporting. Focus events are also negotiated. Bugs may arise from mode
selection rather than from raw input decoding.

### Operating-System Commands

`OSC` strings commonly set titles and may support hyperlinks, clipboard
operations, and other host-facing features. Treat them as powerful,
non-portable input rather than harmless styling.

## Terminfo Matters

Applications should use the terminal description selected by `$TERM`, not
guess capabilities from an emulator name or window title.

- Prefer an entry matching the actual capability set.
- Do not force an older `xterm-color`-style entry merely because basic output
  seems to work.
- A bad terminal description can make correct emulator support look broken.

## Sharp Edges

- Support for titles does not imply equivalent mouse, focus, clipboard, or
  alternate-screen behavior.
- Scrollback behavior is not standardized.
- Host-facing controls can create security and operator-experience risks in
  mixed-trust environments.
- A terminal profile name may not identify the actual emulator.

## Debugging Checklist

- Identify the actual emulator and version.
- Inspect `$TERM` and the selected terminfo entry.
- Identify the exact private mode or control family.
- Compare with xterm when a reference implementation is useful.
- Use `vttest` for baseline display and keyboard behavior.

## Further Information

- XTerm FAQ:
  <https://invisible-island.net/xterm/xterm.faq.html>
- XTerm control sequences:
  <https://invisible-island.net/xterm/ctlseqs/ctlseqs.html>
- XTerm control-sequence documents:
  <https://invisible-island.net/xterm/ctlseqs/>
- VTTEST project:
  <https://invisible-island.net/vttest/>
- VTTEST manual:
  <https://invisible-island.net/vttest/manpage/vttest.html>
- DEC VT220 Programmer Reference Manual:
  <https://vt100.net/docs/vt220-rm/contents.html>
