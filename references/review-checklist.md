# Review checklist

Go through this before every delivery. Each item comes from a correction users actually asked for.

## Pacing
- Does each change land in about 2 to 3 seconds? First cuts are nearly always too slow.
- Does the final state hold for at least 2 seconds after the camera settles?

## Framing
- The background behind the window is dark gray, not pure black, so the window edge reads.
- The window border matches the app's own divider lines in color and thickness.
- The opening shot shows the whole app; the closing shot pulls back out to show the whole redesigned app.

## Alignment
- Headers across panels (logo, page or chat title, toolbar or tabs) share one vertical center.
- Neighboring panels end on the same bottom line, in the before state as well as the after.
- Icons and labels inside each button are centered on the button, not just near it.
- After a padding change, every child moved with its container.
- Spacing between stacked blocks (content and the list below it, a response and the card under it) looks deliberate; widen or tighten to match the design's rhythm.

## Content
- Every visible string is relevant to the content shown: chat transcripts, page titles, file names, artifact names and sibling tabs all describe the same work.
- Leftover content from the screenshots is gone: stray chips, unrelated messages, old file names.
- The three dots, chevrons and badges sit where they belong relative to text that changed length.
- Truncated text truncates with an ellipsis at the right width.
- Placeholder data (sources, numbers, names) is called out to the user. Nothing invented is presented as real.

## Ink and notes
- Every note's wording matches what the user asked for exactly.
- No mark or note covers the thing it points at or content the viewer needs during the morph.
- Each removed control has a callout showing where it went.
- Marks fade before the morph starts; callout notes clear before the beat ends.

## Technical
- Every element is a function of time; seeking to any frame matches playback.
- Stills at each beat's mark and after each morph look right (render them with `export_mp4.py --stills` and look).
- Fonts load before export; the export script waits for them, but a missing font file shows as a fallback face in the stills.
