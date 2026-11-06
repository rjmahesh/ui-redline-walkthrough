# Choreography

## Contents
- Beat structure
- Ordering
- Timing defaults
- Camera
- Ink marks
- Handwritten notes
- Morph patterns
- Cursor demonstrations

## Beat structure

A film is a list of beats played back to back:

1. **Context** (about 1.4s): the full app window, framed, then a push-in to the area being redesigned.
2. **One beat per improvement** (about 2 to 3s each), each with up to three phases:
   - *Mark*: ink draws on the problem (circle, strike, underline, arrow) and a note writes itself in nearby empty space.
   - *Morph*: the marks fade and the UI changes into the fixed state.
   - *Callout* (optional): a second, smaller mark and note point at a consequence, such as where a removed control went or a new affordance.
3. **After** (about 3.4s): the clean redesign, then a pull-back out to the full window, then a hold.

Every beat starts from the finished state of all earlier beats, so the film never jumps.

## Ordering

Group improvements by screen region and finish one region before moving to the next. For a typical app panel: everything in the title bar and header first (title placement, primary action, toolbar consolidation, tabs), then the content area (side rails, the content itself), then anything below it (footers, citations, metadata). Within a region, go in the order the viewer's eye travels, usually left to right.

When one change depends on another (actions can fold into a header only after the header exists), order them so each beat's starting state makes sense on its own.

## Timing defaults

Times are seconds within a beat at `SPEED = 1`. These defaults come from real review rounds where every first cut was asked to go faster; start here rather than slower.

| Moment | Start | Duration |
| --- | --- | --- |
| First mark draws on | 0.12 | 0.18 to 0.24 |
| Second mark (arrow) | 0.35 to 0.55 | 0.14 |
| Note writes on | 0.35 to 0.5 | 0.1 + 0.008 per character |
| Marks fade | about 0.95 | 0.14 |
| Morph | 1.0 | 0.35 to 0.5 |
| Callout mark + note | morph end + 0.15 | 0.18, then the note |
| Notes fade | beat end minus 0.4 | 0.14 |

A mark-and-morph beat lasts about 2.0 to 2.4s; with a callout or a cursor demo, 2.6 to 2.9s. Use the template's global `SPEED` to scale everything when the user asks for "faster" or "slower" (1.25 for 25% faster).

Easing: `eio` (cubic in-out) for UI morphs and camera moves, `eo` (cubic out) for things appearing. Stagger groups of similar elements by 0.08 to 0.12 of the morph progress, or about 0.05s per row for lists.

## Camera

- Context framing: fit the whole window at about 90% of frame width, centered, on the dark gray background.
- Focus framing: fit the redesigned panel with about 40px of margin on the tighter axis.
- Interpolate scale in log space and the center linearly, with `eio`.
- Keep the camera still during beats except for a slow breathing scale of about plus or minus 0.4% over 12 seconds, driven by film time so it never jumps between beats.
- Never move the camera during a mark or morph. Move it only in the context and after beats.

## Ink marks

- Color: a saturated red such as `#FF4B3A`. Stroke about 0.35% of frame width at the focused zoom (6px world units for a 1800px frame showing a panel at roughly 1:1). Round caps and joins.
- Hand-drawn feel: jitter control points slightly and draw a smooth curve through them. Ellipses loop about 1.1 turns and widen a little as they close, so the end overshoots the start.
- Boil: keep three slightly different variants of each stroke and cycle them at 12 fps. It reads as live ink without being distracting.
- Draw on with a stroke dash offset, sequentially through a mark's strokes (an arrow's shaft, then each head stroke).
- Shapes and when to use them: `ell` to circle a thing (set `sq` below 1 for a rounded rectangle around rows or rails), `line` for strike-throughs and underlines, `arrow` from a note to its subject or from a problem to where it goes.
- Give each mark its own `seed` so no two look alike.
- Marks must not cover the thing they mark. Circle around it with a few pixels of clearance.

## Handwritten notes

- A handwriting face such as Caveat at weight 600, sized at about 2.5% of frame width (46px in an 1800px frame), in the ink color.
- Lowercase, under about 7 words, said the way a designer would scribble it: "pull the title into the panel", "publish, not export", "more room for the canvas".
- Write the change and, when it helps, the reason, on a second line: "collapse the previews" / "give the slide room".
- Place notes in empty space near the subject, never over it and never over content the viewer needs to read during the morph. Empty bands above content and wide empty toolbar areas are good spots.
- Reveal left to right with a clip that widens as the note writes on.
- Use the user's exact wording whenever they supply it, character for character.

## Morph patterns

These cover most redesigns. Each is a function of a 0 to 1 progress value.

- **Move into a container**: the container's box grows (often upward) to wrap the element while the element slides and rescales into its new slot. Fade the old frame's border out and the new surface color in.
- **Relabel a button**: reshape the box (position, width, radius, color) with `eio`, and swap the label at the midpoint, fading opacity as `|p - 0.5| * 2` so the word changes while it is invisible.
- **Fold a row into a header**: every row button flies to its header slot along its own path, staggered. Crossfade each label out in the first 30% and the header icon in after 55%. The row's space then collapses and the content below moves up.
- **Something appears in a new home**: fade and scale from 0.9 to 1. Then add a callout so the viewer sees where it went.
- **Collapse a side rail**: fade the rail out while it slides 30px toward the edge, fade in the compact indicator, and grow the main content into the freed space (a few percent bigger reads well).
- **Tabs**: the active item gains its pill background and truncates (animate `max-width` with `text-overflow: ellipsis`), a version badge fades in, then sibling tabs slide in from the right with a short stagger. Fade the last tab out with a mask if the bar is full.
- **List under content**: content slides up to make room, rows fade and rise 14px each with 0.12s stagger.

## Cursor demonstrations

Use a cursor only when the change is about an interaction (hover to expand, click to open). Fade it in away from the target, travel along a gentle arc with `eio`, pause on the target, show the reaction, then leave and fade. A classic arrow pointer with a light drop shadow reads on any surface.
