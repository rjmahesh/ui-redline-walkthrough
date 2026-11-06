---
name: ui-redline-walkthrough
description: Turn before/after screenshots of a product UI into a polished animated redline walkthrough video. Hand-drawn red ink circles, arrows and handwritten notes mark each problem on the real interface, then the UI morphs into the fix one step at a time, ending on the clean redesigned state, exported as MP4. Use this whenever someone wants to animate a UI redesign, show before-and-after design changes, make a design review or changelog clip, a "redline" or annotated design walkthrough, or a launch video of UI improvements, even if they only say "animate these two screenshots" or "show what changed".
---

# UI redline walkthrough

Build a short video that walks a viewer through a UI redesign the way a designer would mark up a printout: red ink calls out a problem, the interface changes to fix it, the ink moves on. Every frame shows the real product, rebuilt from the screenshots, so the viewer never wonders whether the after state is real.

The output is a single self-contained HTML file that animates as a pure function of time, plus an MP4 rendered from it frame by frame.

## What you need from the user

- A **before** and an **after** screenshot of the same screen, same zoom level. Small content differences between them are fine; ask which version of the content to use.
- A numbered list of the improvements to show, ideally with a one-line reason each.

If either is missing, ask for it before anything else.

## Workflow

Follow these steps in order. Each step names the reference file to read when you reach it; read it then, not before.

### 1. Intake: ask before building

Read `references/intake.md` and ask the user its questions in one message. Many of them have defaults listed; offer those so a quick reply settles everything. Do not start building until the answers are in. Users of this skill tend to be designers with strong opinions about framing, copy and pacing, and every answer you get up front saves a revision round later.

### 2. Measure the screenshots

Read `references/measuring.md`. Work in the screenshot's own pixel coordinates (the "world"). Use `scripts/measure.py` to pull exact boxes, colors, text extents and corner radii, and `scripts/extract_icons.py` to cut icons out with clean transparency. Decide for each element whether it stays a raster crop (static, complex content such as a chart or slide) or becomes live DOM (anything that moves, changes, truncates, or whose text the user may edit).

### 3. Plan the beats

Read `references/choreography.md`. Write the beat list before any code: one beat per improvement, grouped by screen region, bracketed by a context push-in and a pull-out. Each beat has a mark phase (ink and note), a morph phase, and an optional callout phase. Share the beat list with the user only if they asked to see the plan; otherwise build.

### 4. Build from the template

Copy `assets/template.html` and edit it. It contains a working demo (a generic app window whose title moves into a panel and whose Export button becomes Publish) so you can see every engine feature in use. Replace the demo UI markup, CSS and `renderUI(P)` with the real product, then rewrite `BEATS`. The engine section is marked; leave it alone unless you need a new mark shape.

Ground rules that keep the result exportable:

- Everything is computed from the time `t`. No CSS transitions, no `setTimeout`, no `Math.random()` at render time. The export script seeks to arbitrary frames and they must match playback.
- UI state lives in numeric progress values (`P.k1`, `P.k2`...) that run 0 to 1. Each beat sets its own value and inherits the finished values of every earlier beat, so each beat starts exactly where the last one ended.
- Place everything in world coordinates. The camera scales the whole world, so ink and notes stay pinned to the UI they mark.

### 5. Check your own work

Run `python scripts/export_mp4.py film.html --stills 0.5,2,4.5,...` with one time inside each beat's mark phase and one after each morph, then look at every still. Check alignment, overlaps, ink placement and that text reads cleanly. Fix what you find before showing the user anything. Then read `references/review-checklist.md` and go through it; it lists the corrections users of this kind of video ask for most often.

### 6. Review with the user

Share the HTML (it autoplays and loops in a browser) and say in a line or two what you made and anything you assumed, such as placeholder copy. Apply feedback in place: pacing changes go through the global `SPEED` setting or the beat durations, layout changes through the measured coordinates.

### 7. Export

```bash
python scripts/export_mp4.py film.html --out film.mp4            # native size, 60 fps
python scripts/export_mp4.py film.html --out film.mp4 --pad 16:9  # letterbox for social or slides
```

Requires Python with Playwright (`pip install playwright && playwright install chromium`) and ffmpeg. The script renders every frame through headless Chromium and encodes H.264 at high quality. See `--help` for frame rate, scale and quality flags.

## Principles worth keeping

- **Fidelity first.** Rebuild the product precisely from measurements and real icon crops. A redline only persuades if the viewer believes both states are real.
- **One change per beat.** Mark, then morph, then move on. Never show two unrelated changes at once.
- **Finish a region before leaving it.** Do all the header changes, then all the canvas changes, so the camera and the viewer's eye travel as little as possible.
- **Short, plain notes.** Handwritten notes say what changes and why in a few words, lowercase, like a designer's margin note.
- **Brisk pacing.** Viewers read faster than you expect. Start at roughly 2 to 3 seconds per beat; slowing down is a rarer request than speeding up.
- **Never invent data.** If the UI shows sources, figures or names that must change, use content the user supplies, or clearly flag your placeholders when you deliver.
