# Procedural Sprite Generation: Python With Pillow

Load this companion to the
[procedural sprite generation overview](overview.knack.md)
when you write or review a sprite generator in Python using Pillow.

Reviewed: 2026-10-13. The sketches were run against Pillow 12.3.
`Image.Resampling` exists from Pillow 9.1; `Image.ANTIALIAS` was removed in
10.0, while `Image.LANCZOS` and similar constants remain available. Check
the installed version with `python -c "import PIL; print(PIL.__version__)"`.

## Canvas and Coordinates

Write drawing code in final-pixel coordinates and convert in one place:

```python
from PIL import Image, ImageDraw, ImageFilter

SS = 4  # supersampling factor

def canvas(size):
    """A transparent canvas SS times the final size."""
    return Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))

def s(*values):
    """Final-pixel coordinates to supersampled ones."""
    return [round(v * SS) for v in values]

def finish(img, size):
    """Downsample to the final size."""
    return img.resize((size, size), Image.Resampling.LANCZOS)
```

Coordinates in whole final pixels land on whole final pixels after the
downsample. Half-pixel coordinates produce deliberate soft edges; use them
on purpose, not by accident.

## Palette by Role

```python
OUTLINE     = (30, 26, 36, 255)
METAL_LIGHT = (178, 182, 190, 255)
METAL       = (140, 144, 152, 255)
METAL_DARK  = (98, 101, 110, 255)
ACCENT      = (250, 170, 255, 255)
GLOW        = (225, 80, 255)          # RGB only; alpha chosen per use
OUTLINE_PX  = 1                       # outline weight in final pixels
```

- One ramp per material, light to dark, named by role.
- Keep glow colors as RGB triples and add alpha where they are used.
- Put the constants at the top of the generator, or in a module every
  generator imports, and mirror them in the art-direction document.

## Drawing

Create the drawing context with mode `"RGBA"` so that translucent fills
blend with what is underneath instead of replacing it. The Pillow
documentation describes this argument as the way "to blend the drawing into
the image."

```python
d = ImageDraw.Draw(img, "RGBA")
```

Pillow's shape primitives draw without anti-aliasing: an ellipse drawn at
final size contains only fully opaque and fully transparent pixels, while
the same ellipse drawn at four times the size and downsampled has smooth
edges. That observation is the reason for the supersampled canvas.

**Outlines as shapes.** Drawing the outline as a filled shape and the body
inset by the outline weight gives an outline of exactly that weight on every
side, for any shape:

```python
def outlined_box(d, x0, y0, x1, y1, fill, weight=OUTLINE_PX):
    d.rectangle(s(x0, y0, x1, y1), fill=OUTLINE)
    d.rectangle(s(x0 + weight, y0 + weight, x1 - weight, y1 - weight),
                fill=fill)

def outlined_ellipse(d, x0, y0, x1, y1, fill, weight=OUTLINE_PX):
    d.ellipse(s(x0, y0, x1, y1), fill=OUTLINE)
    d.ellipse(s(x0 + weight, y0 + weight, x1 - weight, y1 - weight),
              fill=fill)
```

Build a small library of such helpers: panels with a highlight band, bolts,
pipes with end caps, hazard stripes, glows. Every sprite draws from it.

## Glows and Blurs

`Image.filter` blurs each band separately and does not premultiply alpha. A
glow drawn on a layer whose transparent pixels are black therefore picks up
black at its soft edge. In a test, a magenta glow's edge pixel came out as
`(33, 12, 37, 25)` on a black-transparent layer and `(225, 80, 255, 25)` on a
layer whose transparent pixels carried the glow color. Draw glows on their
own layer, filled with the glow color at zero alpha:

```python
def glow(img, box, blur_px, alpha=170):
    """Composite a blurred, colored ellipse over img."""
    layer = Image.new("RGBA", img.size, GLOW + (0,))
    ImageDraw.Draw(layer).ellipse(s(*box), fill=GLOW + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur_px * SS))
    return Image.alpha_composite(img, layer)
```

Scale blur radii by the supersampling factor, as above, so that a glow's
softness is specified in final pixels.

**Masking a layer.** To confine a layer to a shape, multiply its alpha by a
grayscale mask, then composite it, rather than pasting through a combined
mask:

```python
from PIL import ImageChops

layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))  # mask: "L"
img.alpha_composite(layer)
```

## Downsampling

`Image.resize` with a filter other than nearest-neighbor converts `RGBA`
images to premultiplied alpha (`RGBa`) internally and back, so resizing does
not produce the dark fringes that blurring does; this is visible in
Pillow's source for `Image.resize`. Filter choice:

| Filter | Use |
| --- | --- |
| `LANCZOS` | Default for downsampling art; sharpest, slight ringing at hard edges |
| `BOX` | Exact area average for integer factors; no ringing, slightly softer |
| `BICUBIC` | Pillow's default for most modes; less ringing than Lanczos |
| `NEAREST` | Never for downsampling; useful to enlarge previews without blur |

Pillow's documentation rates Lanczos highest for downscaling quality and
slowest. In a quick check, a 4:1 Lanczos downsample of a sharp step from 50
to 200 produced neighboring values of 39 and 211: a little overshoot on each
side. Box filtering produced none. Compare the two on your flattest,
highest-contrast sprites and choose per family, not per sprite.

## Animation Frames

```python
def emitter(size=32, frame=0, frames=4):
    img = canvas(size)
    d = ImageDraw.Draw(img, "RGBA")
    outlined_box(d, 4, 10, 28, 30, METAL)
    pulse = 1 + frame / frames             # frame-dependent parameter
    img = glow(img, (10, 2, 22, 14), blur_px=1.5 * pulse)
    d = ImageDraw.Draw(img, "RGBA")
    outlined_ellipse(d, 12, 4, 20, 12, ACCENT)
    return finish(img, size)

for i in range(4):
    save(emitter(frame=i), f"Things/Emitter/ExampleEmitter_{i}.png")
```

- Derive each frame from one parameter (phase, angle, scale), so that the
  frames form a smooth sequence.
- Keep the canvas size and the anchor point identical across frames, or the
  sprite jitters in the host.
- Name frames with a zero-based index unless the host expects otherwise, and
  check the host's naming rule for animations and rotations.

## Determinism

```python
import random, zlib

def rng_for(name):
    """A generator seeded from the sprite's name, stable across runs."""
    return random.Random(zlib.crc32(name.encode("utf-8")))
```

- Seed from a stable hash of the sprite's name. Python's built-in `hash()`
  of a string is salted per process and differs between runs.
- Give each sprite its own generator, so that adding a random call to one
  sprite does not change the others.
- Avoid time, environment variables, and dictionary or set iteration order
  in drawing decisions.
- Test determinism by rendering twice and comparing pixels:

```python
assert emitter().tobytes() == emitter().tobytes()
```

Compare decoded pixels (`Image.tobytes()`, or a hash of it) rather than PNG
file bytes. Encoder options and the compression library can change the
bytes without changing a pixel.

## Saving

```python
import os

def save(img, rel_path, root=TEXTURES):
    path = os.path.join(root, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with Image.open(path) as old:
            if old.mode == img.mode and old.tobytes() == img.tobytes():
                return False            # unchanged: leave the file alone
    img.save(path)
    return True
```

Skipping unchanged files keeps version-control diffs to the sprites that
really changed, and makes an unexpected change obvious. Find the output
root from the script's own location or an argument, never from an absolute
path.

## Contact Sheets

```python
def contact_sheet(sprites, display_px, background):
    """Full-size row above a display-size row, on a host-like background."""
    full = max(im.width for im in sprites)
    sheet = Image.new("RGBA", (full * len(sprites), full + display_px),
                      background)
    for i, im in enumerate(sprites):
        sheet.alpha_composite(im, (i * full, 0))
        small = im.resize((display_px, display_px), Image.Resampling.LANCZOS)
        sheet.alpha_composite(small, (i * full, full))
    return sheet
```

Enlarge sheets for viewing with `NEAREST`, so that the preview shows real
pixels. The [review companion](review.knack.md)
covers what to look for.

## Further Information

- Pillow, [Image module](https://pillow.readthedocs.io/en/stable/reference/Image.html):
  `new`, `resize`, `alpha_composite`, `filter`.
- Pillow, [ImageDraw](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html):
  shapes, widths, and the blending mode argument.
- Pillow, [ImageFilter](https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html):
  `GaussianBlur` and other filters.
- Pillow, [Concepts: filters](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#filters):
  the resampling filters and their quality and speed ratings.
- Pillow, [Deprecations and
  removals](https://pillow.readthedocs.io/en/stable/deprecations.html):
  the `ANTIALIAS` removal and restored constants.
- Python, [object.\_\_hash\_\_](https://docs.python.org/3/reference/datamodel.html#object.__hash__):
  salted string hashes.
