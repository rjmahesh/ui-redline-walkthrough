#!/usr/bin/env python3
"""Cut icons out of screenshots into one transparent sprite plus a JSON map.

Usage: extract_icons.py spec.json [--out sprite.png]

spec.json:
{
  "images": {"before": "Before.png", "after": "After.png"},
  "icons": [
    {"name": "close",  "img": "after",  "box": [2722, 64, 2754, 96], "mode": "white",  "bg": [30, 30, 30]},
    {"name": "app",    "img": "after",  "box": [1093, 62, 1131, 98], "mode": "color",  "bg": [42, 42, 42]},
    {"name": "tabbar", "img": "after",  "box": [1500, 40, 2290, 120], "mode": "opaque"}
  ]
}

Modes
  white   light monochrome glyph on a flat background; alpha from luminance (cleanest)
  color   multicolor icon on a flat background; alpha from distance to the background
  opaque  keep pixels as they are, background included

Writes sprite.png and sprite.json ({"W", "H", "m": {name: [x, y, w, h]}}).
In CSS: background-image the sprite, background-position -x 0, element size w x h.
Scale an icon by multiplying width, height, background-position and background-size together.
"""
import argparse, json, os
import numpy as np
from PIL import Image


def white(r, bg):
    bgl = float(np.mean(bg))
    lum = r.mean(axis=2)
    fg = r.reshape(-1, 3)[lum.argmax()]
    a = np.clip((lum - bgl) / max(1.0, fg.mean() - bgl), 0, 1)
    out = np.zeros(r.shape[:2] + (4,))
    out[..., :3] = fg
    out[..., 3] = a * 255
    return out


def color(r, bg, d=70.0):
    bgv = np.array(bg, float)
    a = np.clip(np.abs(r - bgv).max(axis=2) / d, 0, 1)
    c = bgv + (r - bgv) / np.maximum(a[..., None], 1e-3)
    out = np.zeros(r.shape[:2] + (4,))
    out[..., :3] = np.where(a[..., None] > 0, np.clip(c, 0, 255), 0)
    out[..., 3] = a * 255
    return out


def opaque(r, bg=None):
    out = np.zeros(r.shape[:2] + (4,))
    out[..., :3] = r
    out[..., 3] = 255
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("spec")
    p.add_argument("--out", default="sprite.png")
    a = p.parse_args()
    spec = json.load(open(a.spec))
    base = os.path.dirname(os.path.abspath(a.spec))
    imgs = {k: np.array(Image.open(os.path.join(base, v)).convert("RGB")).astype(float) for k, v in spec["images"].items()}
    modes = {"white": white, "color": color, "opaque": opaque}
    tiles = []
    for ic in spec["icons"]:
        x0, y0, x1, y1 = ic["box"]
        r = imgs[ic["img"]][y0:y1, x0:x1]
        tiles.append((ic["name"], Image.fromarray(modes[ic.get("mode", "white")](r, ic.get("bg", [0, 0, 0])).astype(np.uint8), "RGBA")))
    W = sum(t.width for _, t in tiles) + 2 * len(tiles)
    H = max(t.height for _, t in tiles)
    sheet = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m, x = {}, 0
    for name, t in tiles:
        sheet.paste(t, (x, 0)); m[name] = [x, 0, t.width, t.height]; x += t.width + 2
    sheet.save(a.out, optimize=True)
    js = os.path.splitext(a.out)[0] + ".json"
    json.dump({"W": W, "H": H, "m": m}, open(js, "w"), indent=1)
    print(f"wrote {a.out} ({W}x{H}) and {js} with {len(m)} icons")


if __name__ == "__main__":
    main()
