#!/usr/bin/env python3
"""Render a redline film (HTML built from assets/template.html) to MP4 or still frames.

The page must expose window.renderAt(seconds), window.FILM = {duration, width, height},
and start paused when loaded with ?export=1 (the template does all three).

Examples
  export_mp4.py film.html --out film.mp4
  export_mp4.py film.html --out film.mp4 --pad 16:9 --scale 2
  export_mp4.py film.html --stills 0.5,2.1,4.4 --outdir stills

Needs: pip install playwright && playwright install chromium; ffmpeg on PATH.
"""
import argparse, os, pathlib, subprocess, sys


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("html")
    p.add_argument("--out", default="film.mp4")
    p.add_argument("--fps", type=int, default=60)
    p.add_argument("--scale", type=float, default=1.0, help="device scale factor; 2 renders at double resolution")
    p.add_argument("--crf", type=int, default=14, help="x264 quality, lower is better (12-18 is visually lossless)")
    p.add_argument("--pad", default=None, help="letterbox to an aspect ratio such as 16:9, using the film background")
    p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--end", type=float, default=None)
    p.add_argument("--stills", default=None, help="comma-separated times; writes PNGs instead of a video")
    p.add_argument("--outdir", default="stills")
    a = p.parse_args()

    from playwright.sync_api import sync_playwright
    url = pathlib.Path(a.html).resolve().as_uri() + "?export=1"
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 800}, device_scale_factor=a.scale)
        page.goto(url)
        page.wait_for_function("!!(window.FILM && window.renderAt)")
        page.evaluate("document.fonts.ready")
        film = page.evaluate("window.FILM")
        W, H, dur = film["width"], film["height"], film["duration"]
        page.set_viewport_size({"width": W, "height": H})
        page.evaluate("window.renderAt(0)")
        page.wait_for_timeout(300)
        stage = page.locator("#stage")

        def shot(t):
            page.evaluate(f"window.renderAt({t})")
            return stage.screenshot(type="png", animations="disabled")

        if a.stills:
            os.makedirs(a.outdir, exist_ok=True)
            for t in [float(x) for x in a.stills.split(",")]:
                path = os.path.join(a.outdir, f"t{t:06.2f}.png")
                open(path, "wb").write(shot(t))
                print("wrote", path)
            browser.close()
            return

        end = dur if a.end is None else min(a.end, dur)
        n = int(round((end - a.start) * a.fps))
        bg = film.get("background", "#000000").lstrip("#")
        vf = ["scale=trunc(iw/2)*2:trunc(ih/2)*2"]
        if a.pad:
            rw, rh = [float(x) for x in a.pad.split(":")]
            vf.append(f"pad='max(iw,ceil(ih*{rw}/{rh}/2)*2)':'max(ih,ceil(iw*{rh}/{rw}/2)*2)':(ow-iw)/2:(oh-ih)/2:color=0x{bg}")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-",
               "-vf", ",".join(vf), "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf),
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out]
        enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n):
            enc.stdin.write(shot(a.start + i / a.fps))
            if i % a.fps == 0:
                print(f"\rframe {i}/{n}", end="", file=sys.stderr, flush=True)
        enc.stdin.close()
        enc.wait()
        browser.close()
        print(f"\nwrote {a.out}: {n} frames, {end - a.start:.2f}s at {a.fps} fps")


if __name__ == "__main__":
    main()
