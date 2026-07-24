# Terminal Box Drawing and Shading

Reviewed: 2026-07-23

## When to Load This Knack

Load this knack when a character-cell interface uses line art, blocks, or
shading and must distinguish Unicode text, curses ACS, DEC special graphics,
legacy code pages, and plain ASCII.

## Mental Model

“High ASCII” is a historical convenience label, not an encoding. ASCII is a
7-bit standard. A byte above `0x7f` has meaning only under an identified
encoding, while a Unicode code point and a terminal-library drawing constant
are different abstractions again.

Keep four rendering paths distinct:

1. plain ASCII punctuation such as `-`, `|`, `+`, and `#`;
2. curses/terminfo ACS symbols, normally derived from terminal capabilities
   and the DEC alternate character set;
3. Unicode box-drawing, block, and shade characters; and
4. bytes in a named legacy encoding such as IBM CP437.

Similar-looking glyphs do not make those paths interchangeable.

## Choosing a Strategy

- Keep an ASCII fallback when layout meaning matters more than visual fidelity.
- Prefer the active UI library's line-drawing abstraction for its portable
  baseline.
- Use Unicode when the application has a coherent UTF-8 path, a documented
  cell-width policy, and a tested font/emulator matrix.
- Emit CP437 bytes only in a deliberately CP437-compatible environment or
  through an explicit conversion layer.
- Use DEC graphics only through a correctly managed terminal mode or
  capability.

Curses ACS commonly covers single-line forms. Do not assume it provides a
portable double-line family. Unicode is usually the clearer modern route for
double lines, with ASCII as the fallback.

## Unicode and Cell Width

Box-drawing code points are commonly rendered as one cell, but font and width
policy remain runtime facts. Block elements, combining text next to borders,
emoji, and ambiguous-width characters can expose alignment defects.

The renderer should:

- measure according to its declared terminal-width policy;
- avoid splitting width-two content at a border;
- define behavior when a glyph is unsupported or the wrong width;
- test intersections and adjoining text, not only isolated symbols; and
- retain layout meaning if rich line art falls back to ASCII.

Do not use shade density alone to communicate state. Pair it with labels,
spacing, borders, or another non-color cue.

## CP437 and Unicode Double-Line Core

When a legacy import or controlled emulator genuinely needs the classic
double-line set, keep byte and code-point identities explicit.

| Glyph | Meaning | Unicode | CP437 |
| --- | --- | --- | --- |
| `╔` | top-left | `U+2554` | `0xC9` |
| `╗` | top-right | `U+2557` | `0xBB` |
| `╚` | bottom-left | `U+255A` | `0xC8` |
| `╝` | bottom-right | `U+255D` | `0xBC` |
| `═` | horizontal | `U+2550` | `0xCD` |
| `║` | vertical | `U+2551` | `0xBA` |
| `╠` | left tee | `U+2560` | `0xCC` |
| `╣` | right tee | `U+2563` | `0xB9` |
| `╦` | top tee | `U+2566` | `0xCB` |
| `╩` | bottom tee | `U+2569` | `0xCA` |
| `╬` | intersection | `U+256C` | `0xCE` |

CP437 shade bytes map to Unicode characters such as light `░`, medium `▒`,
and dark `▓`, while half and full block elements include `▄`, `▀`, and `█`.
The visible correspondence does not permit writing a CP437 byte directly to a
UTF-8 terminal.

## Capability and Fallback Review

Before selecting a glyph family, identify:

- the bytes or text the application produces;
- the locale and encoding at each transport boundary;
- whether a curses wide-character or narrow-character library is linked;
- the terminfo description and ACS mapping;
- emulator, font, and remote transport;
- the application's width policy; and
- the required ASCII or monochrome fallback.

A small visual sample is useful for human acceptance, but automated tests
should also verify encoded values, frame widths, intersections, clipping, and
fallback selection.

## Sharp Edges

- Never treat bytes above `0x7f` as portable glyph identifiers.
- Do not mix CP437 bytes, DEC mode selectors, ACS constants, and Unicode text
  in one renderer without explicit conversion boundaries.
- Do not assume a glyph that appears in documentation exists in the user's
  font.
- Do not assume Unicode normalization, grapheme segmentation, and terminal
  cell width are the same problem.
- Do not advertise double-line ACS support without checking the actual API and
  terminal capabilities.

## Further Information

- Unicode Box Drawing chart:
  <https://www.unicode.org/charts/PDF/U2500.pdf>
- Unicode CP437 mapping:
  <https://www.unicode.org/Public/MAPPINGS/VENDORS/MICSFT/PC/CP437.TXT>
- Unicode East Asian Width:
  <https://www.unicode.org/reports/tr11/>
- ncurses forms-drawing characters:
  <https://invisible-island.net/ncurses/man/curs_addch.3x.html>
- terminfo alternate-character-set capability:
  <https://invisible-island.net/ncurses/man/terminfo.5.html>
- VT100 compatibility guidance:
  [vt100.knack.md](vt100.knack.md)
