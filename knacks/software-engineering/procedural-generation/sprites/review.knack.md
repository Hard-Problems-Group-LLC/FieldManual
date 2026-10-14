# Procedural Sprite Generation: Review and Maintenance

Load this companion to the
[procedural sprite generation overview](overview.knack.md)
when you judge a generated sprite, review a change to a generator, or keep
a growing set of generated art consistent.

Reviewed: 2026-10-13.

## What to Look At

A sprite is seen at one or two sizes, on particular backgrounds, next to
particular neighbors. Review it the same way.

**Contact sheets.** Render each new or changed sprite into a sheet with:

- the sprite at full size, beside the existing sprites it will sit next to
  in the host;
- the same row downsampled to the smallest size at which the host displays
  it, such as an inventory icon or a zoomed-out map view;
- the backgrounds it will appear on: the host's typical floor or terrain, a
  light interface panel, a dark one; and
- for animations, every frame in order, and the frames overlaid at reduced
  opacity to show jitter; and
- for sprites drawn in layers by the host, such as a turret's base and its
  rotating top, the layers assembled at the sizes and offsets the host uses.
  Overlaps and gaps between parts show only in the assembly.

Enlarge the sheet with nearest-neighbor scaling for viewing, so that the
real pixels are visible.

**Questions for the sheet.**

- Does the silhouette read at the smallest size, or does it become a blob?
- Is contrast between parts still visible at that size?
- Do outline weight, light direction and palette match the neighbors?
- Does a glow or accent dominate its neighbors, or vanish against the
  background?
- Is the projection consistent with the host's art? A straight top-down
  sprite among three-quarter-view sprites looks wrong unless the difference
  was chosen deliberately and recorded.
- Do animation frames keep the same anchor and size?
- Are there halos, dark fringes or ringing at high-contrast edges?

Iterate on what the sheet shows. Tightening a glow, thickening an outline at
small sizes, or simplifying detail that turns to noise are typical fixes.

## Checking Inside the Host

The host scales, filters, tints, lights and compresses what it draws. A
sprite that passes its contact sheet can still fail in place:

- look at it in the host at normal zoom and at the zoom levels players use;
- check it under the host's lighting and any color tinting it applies, such
  as material or faction colors;
- check edges against the host's backgrounds for color bleeding from
  transparent pixels; and
- check text and labels at the host's smallest font setting.

An agent generating art usually cannot see the host's window. Its report
should list in-host appearance as not verified. Screenshots captured at log
cues during an automated run (see [In-Host Smoke
Testing](../../testing/in-host-smoke/overview.knack.md))
let a person, or an agent able to read images, close that gap. For effects
that change over time, take a burst of captures at the cue, crop each to
the area of interest, enlarge with nearest-neighbor scaling, and tile them
into one image.

## Guarding Existing Sprites

Generators usually regenerate every sprite on every run. That is good for
consistency and dangerous for history: a change to a shared helper made for
one new sprite can quietly alter dozens of old ones. In one project,
generalizing a stripe helper for a larger sprite changed an existing part's
image; the author kept the old behavior for the old sizes so that existing
sprites stayed identical, and checked the output folder after every render.

Practices:

- **Diff the outputs after every render.** Version control shows which
  image files changed. Every changed file must be one you meant to change.
- **Skip unchanged writes.** Compare decoded pixels before writing, so that
  an unchanged sprite leaves no diff (see the
  [Python companion](Python.knack.md)).
- **Version helper behavior deliberately.** When a helper must change for
  new sprites, add a parameter with the old behavior as the default, or a
  new helper, rather than changing what existing callers draw.
- **Snapshot tests.** For a mature set, store a hash of each sprite's pixels
  and fail the build when one changes without its hash being updated in the
  same change.

## Keeping the Art Direction Current

The art-direction document is the contract between everyone who adds art.
When a change introduces a color, a material, a part, a projection choice or
a rule (for example, "robots are drawn straight top-down", or "every
emitter has a two-pixel glow"), update the document in the same change.

A useful structure for the document:

- purpose and tone of the art;
- palette by role, with values, matching the generator's constants;
- light, shading and outline rules per size;
- projection and orientation;
- the part vocabulary with small reference renders;
- naming, folders and frame conventions; and
- display sizes and backgrounds to review against.

Reviewers check that every constant and helper the change adds is
reflected there.

Codify the art direction in three places: the document, for people; a
standing rule in the agents' instructions to read it before generating
anything; and tests that enforce what can be checked mechanically. Useful
tests:

- every item the plugin adds uses the plugin's own art, so that a borrowed
  host sprite is caught (with an explicit list of deliberate exceptions);
- every asset name carries the project's prefix, and a retired prefix
  appears nowhere;
- every texture path referenced in data files or in code exists, including
  paths built in code that a data-file scan cannot see; and
- regenerating produces identical pixels.

## Review Checklist for a Generator Change

- A contact sheet with neighbors, at full and smallest display size, on the
  host's backgrounds, was inspected.
- Only intended image files changed after regenerating the whole set.
- New colors and parts come from role-named constants and shared helpers.
- The art-direction document records every new rule.
- Output is deterministic across two runs.
- In-host appearance was checked, or the change says it was not.

## Further Information

- Pillow, [Image.resize and
  filters](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#filters).
- Unity, [Default texture import
  settings](https://docs.unity3d.com/Manual/texture-type-default.html):
  color dilation at alpha edges as an example of host-side filtering
  concerns.
- FieldManual, [In-Host Smoke
  Testing](../../testing/in-host-smoke/overview.knack.md):
  capturing screenshots at log cues.
