# Measuring the screenshots

The video is only as convincing as its measurements. Spend the time here; it is far cheaper than fixing alignment after the user spots it.

## Coordinates

Use the screenshot's native pixels as the world coordinate system, even on a 2x retina capture. Set the template's world size to the screenshot size and place every element at its measured pixel position. Fonts, borders and radii are then measured in the same units: a 2x screenshot of 14px text measures about 28px, and you set 28px.

Open the image first and check its real size (`python scripts/measure.py info After.png`). Displayed previews are often scaled, so never read coordinates off a preview by eye.

## The measuring tool

`scripts/measure.py` has these commands. All boxes are `x0,y0,x1,y1` with exclusive ends.

| Command | Use it for |
| --- | --- |
| `info IMG` | Image size and mode |
| `colors IMG --box B` | The most common colors in a region: surface, border and text colors |
| `boxes IMG --color R,G,B [--tol N] [--box B] [--min-area N]` | Every connected region of one color: panels, buttons, pills, cards |
| `extent IMG --box B --bg R,G,B [--tol N]` | Bounding box of anything that differs from the background: text runs, icons |
| `lines IMG --box B [--th N]` | Rows of text inside a region, with their x extents: line positions and spacing |
| `runs IMG --y Y --x0 A --x1 B` | Color runs along one row: borders, dividers, gaps between buttons |
| `corner IMG --x X --y0 A --y1 B` | Where a rounded corner starts on each row, to estimate radius |
| `crop IMG --box B --out F [--zoom N]` | A zoomed crop to look at with your own eyes |

Measure, then look. Crop and view every element you build at least once.

## Raster or live DOM

Keep as a raster crop:
- Rich content that never changes during the video: slides, charts, documents, avatars, logos.
- Areas outside the redesign that only provide context, such as a sidebar.

Rebuild as live DOM:
- Anything that moves, resizes, morphs, appears or disappears.
- Any text the user may want to change (titles, chat copy, tab names, sources), or that must truncate with an ellipsis.
- Buttons whose label or shape changes.

When you compose a context raster (for example a chat column), paste the pieces you keep onto a blank background with PIL and leave holes for live text, rather than shipping the full screenshot with stale content in it.

## Icons

`scripts/extract_icons.py spec.json` cuts icons into one sprite with a JSON map. Modes:

- `white`: light monochrome icon on a known flat background. Alpha is recovered from luminance, so the icon composites cleanly on any surface. Use this for most UI glyphs.
- `color`: multicolor icon on a known flat background. Alpha is estimated from distance to the background.
- `opaque`: keep the background. Use only when the element always sits on that exact background.

Measure each icon's background color with `colors` first; one wrong value leaves a halo.

## Alignment traps

- **Before and after may be captured at different UI scales.** Compare the size of a shared element (a button, a line of text) between the two shots before reusing coordinates.
- **Shared centerlines across panels.** Headers in neighboring panels (a sidebar logo, a chat title, a canvas toolbar) should sit on one centerline. Measure all of them and align to one value, usually the logo's center.
- **Shared bottoms.** A prompt bar and the bottom of an adjacent canvas should end on the same line, in the before state too.
- **Panel insets.** If a redesign tightens padding to make an alignment work, change the panel's outer inset and its inner padding together, then re-derive every child position from the new values.
- **Text boxes versus glyphs.** Measured text extents are glyph ink, not the CSS box. Set `line-height` explicitly and offset `top` so the cap height lands on the measured pixels.
