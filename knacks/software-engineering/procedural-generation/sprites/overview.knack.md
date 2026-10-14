# Procedural Sprite Generation

Load this knack when you generate 2D art from code, such as sprites, icons,
textures or interface glyphs for a game or an application, or when you
review a generator that does. It applies to placeholder art built to play
and test with as much as to art that ships. Companions:

- [Python with Pillow](Python.knack.md):
  canvases, role-named palettes, outlined shapes, glows, downsampling,
  animation frames and deterministic output.
- [Review and maintenance](review.knack.md):
  contact sheets at full and display size, checks inside the host, guarding
  existing sprites against helper changes, and keeping the art-direction
  document current.

Reviewed: 2026-10-13. Library behavior described here was checked with
Pillow 12.3; recheck it on the version you use.

## Mental Model

Treat art as code. The generator script is the source; the image files are
its build products. Everything that makes a set of sprites look like one
family (palette, outline, light, projection, shape vocabulary) lives in
named constants and shared helpers, not in each sprite's drawing code.

An **art-direction document** is the constraint the code implements. It
states, in words a person and an agent can both follow:

- the palette, by role, with each material's light-to-dark ramp;
- the light direction and the shading style (flat bands, gradients, rim
  light);
- outline color and weight at each sprite size;
- the projection: straight top-down, three-quarter, or side-on, matching
  the host's own art;
- the shape vocabulary: which parts recur (panels, bolts, pipes, glows) and
  how they are drawn;
- naming and file layout;
- canvas size per footprint or object kind, with a margin so outlines and
  glows are not clipped at the edge;
- the display sizes at which each kind of sprite must read; and
- when one document also governs text, the voice of labels and
  descriptions.

When a new sprite needs a color, part or rule the document does not cover,
extend the document in the same change. Otherwise the next sprite, or the
next agent, invents a different answer.

## Core Practices

1. **Supersample, then downsample.** Draw at an integer multiple of the
   final size, typically four times, and downsample with a high-quality
   filter such as Lanczos. Many drawing libraries, including Pillow's shape
   primitives, draw hard-edged, aliased shapes; downsampling averages each
   final pixel's coverage into smooth edges.
2. **Name colors by role.** `OUTLINE`, `METAL_LIGHT`, `METAL`, `METAL_DARK`,
   `ACCENT_GLOW`, not `GREY_3` or raw tuples. A role-named palette makes a
   global change one edit and keeps materials consistent across sprites.
3. **Keep outline weights consistent** in final pixels, the same for every
   sprite in a family at a given size, and align outline edges to the
   supersampling grid so that they land on whole final pixels.
4. **Share helper shapes.** One function draws a panel, a bolt, a pipe or a
   glow, everywhere. Shared helpers are what make separate sprites read as
   one set.
5. **Check at full size and at the smallest display size, side by side with
   neighbors.** A sprite that reads well alone at full size can turn to mud
   at the size players see, or clash with the sprites it sits beside.
6. **Generate animation frames as separate files** on the same canvas with
   the same anchor point, unless the host wants a sprite sheet.
7. **Make output deterministic.** Seed every random choice from a stable
   value such as the sprite's name, never from time or process state, so
   that regenerating changes only what the code changed.

## Workflow for a New Sprite

1. Read the art-direction document and look at the neighbors the sprite
   will sit beside.
2. Draw it with the shared helpers and role-named palette, at the
   supersampled size.
3. Render a contact sheet: full size and smallest display size, beside its
   neighbors, on the backgrounds it will appear on.
4. Iterate on what the sheet shows: contrast at small size, outline weight,
   glow strength, silhouette.
5. Regenerate everything and confirm that no other sprite changed unless you
   meant it to.
6. Check it inside the host, or record that you could not.
7. Extend the art-direction document with any new rule.

## Sharp Edges

- **Ringing.** Lanczos overshoots at hard edges. Downsampling a sharp
  dark-to-light edge produced values just beyond both sides in testing: a
  faint dark line on the dark side and a bright one on the light side.
  Usually invisible; on flat high-contrast art, compare with a box filter.
- **Sub-pixel detail vanishes.** A line thinner than one final pixel turns
  into a faint smear across two pixels. Keep every line and gap at least one
  final pixel wide, aligned to the grid.
- **Blurs darken edges.** Blurring a layer whose transparent pixels are
  black pulls black into the soft edge. Fill a glow layer's transparent
  pixels with the glow color at zero alpha before blurring.
- **The host filters again.** Engines scale, filter, mipmap and compress
  textures. Fully transparent pixels can bleed their color into edges when
  filtered; some engines dilate edge color for this reason. Check the sprite
  in the host at its real display size.
- **Compression needs multiples of four.** Block-compressed texture formats
  work on 4-by-4 texel blocks, and Microsoft's Direct3D documentation
  requires block-compressed textures to be multiples of four in every
  dimension. One engine logged that a 410-pixel texture could not be
  compressed. Keep sprite dimensions multiples of four unless the host
  documents otherwise.
- **Helper changes ripple.** Refactoring a shared helper for a new sprite can
  silently change every old sprite that uses it. Diff the outputs after each
  render.
- **Agents cannot see the host.** An agent that generates art usually checks
  only the files it rendered. In-host appearance stays unverified until a
  person, or a screenshot an agent can read, confirms it.
- **Fonts are not deterministic across machines.** Text rendered from a
  system font varies with the font file and the rasterizer version. Bundle
  the font or draw glyphs as shapes.
- **Gamma.** Filters average stored values, which are usually sRGB-encoded,
  not linear light, so blends between saturated colors can come out darker
  than expected. For most sprites this is acceptable; convert to linear light
  before resampling if it shows.

## Review Checklist

- The art-direction document covers every color, part and rule the sprite
  uses, or was extended in the same change.
- Colors come from role-named constants; shapes come from shared helpers.
- Outline weight matches the family at this size and sits on whole pixels.
- A contact sheet at full and smallest display size, with neighbors, was
  inspected.
- Regenerating the whole set changed only the intended files.
- Output is identical across two runs.
- The sprite was seen in the host, or the change says it was not.

## Further Information

- Pillow, [Image.resize and resampling
  filters](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#filters).
- Claude E. Duchon, [Lanczos Filtering in One and Two
  Dimensions](https://doi.org/10.1175/1520-0450%281979%29018%3C1016:LFIOAT%3E2.0.CO;2),
  *Journal of Applied Meteorology* 18(8), 1979.
- Don P. Mitchell and Arun N. Netravali, [Reconstruction Filters in
  Computer Graphics](https://doi.org/10.1145/378456.378514), SIGGRAPH 1988:
  the trade-off between blur and ringing.
- Thomas Porter and Tom Duff, [Compositing Digital
  Images](https://doi.org/10.1145/800031.808606), SIGGRAPH 1984:
  premultiplied alpha.
- Unity, [Default texture import
  settings](https://docs.unity3d.com/Manual/texture-type-default.html): the
  "Alpha Is Transparency" option, which dilates color to avoid edge
  artifacts.
- Microsoft, [Block Compression (Direct3D
  10)](https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression):
  4-by-4 blocks and the multiple-of-four rule.
- W3C, [A Standard Default Color Space for the Internet:
  sRGB](https://www.w3.org/Graphics/Color/sRGB.html).
- Reproducible Builds, [Documentation](https://reproducible-builds.org/docs/):
  removing time and environment from build outputs.
