#!/usr/bin/env python3
"""Measure UI screenshots in their native pixels.

Boxes are x0,y0,x1,y1 with exclusive ends. Colors are R,G,B.
Examples:
  measure.py info After.png
  measure.py colors After.png --box 1060,20,2800,140
  measure.py boxes After.png --color 30,30,30 --tol 1 --box 2200,0,2822,140 --min-area 500
  measure.py extent After.png --box 1090,52,1135,108 --bg 42,42,42
  measure.py lines After.png --box 130,700,1060,1000
  measure.py runs After.png --y 80 --x0 1040 --x1 2822
  measure.py corner After.png --x 1060 --y0 20 --y1 70
  measure.py crop After.png --box 1080,40,1500,120 --out tab.png --zoom 2
"""
import argparse, collections, sys
import numpy as np
from PIL import Image


def load(path):
    return np.array(Image.open(path).convert("RGB")).astype(int)


def parse(s, n=None):
    v = [int(float(x)) for x in s.split(",")]
    if n and len(v) != n:
        sys.exit(f"expected {n} comma-separated numbers, got {s}")
    return v


def sub(img, box):
    if not box:
        return img, 0, 0
    x0, y0, x1, y1 = box
    return img[y0:y1, x0:x1], x0, y0


def cmd_info(a):
    im = Image.open(a.img)
    print(f"{a.img}: {im.size[0]}x{im.size[1]} {im.mode}")


def cmd_colors(a):
    r, _, _ = sub(load(a.img), a.box)
    c = collections.Counter(map(tuple, r.reshape(-1, 3).tolist()))
    total = r.shape[0] * r.shape[1]
    for col, n in c.most_common(a.n):
        print(f"rgb{col}  #{col[0]:02x}{col[1]:02x}{col[2]:02x}  {100*n/total:.1f}%")


def cmd_boxes(a):
    from scipy import ndimage
    img = load(a.img)
    m = np.abs(img - np.array(a.color)).max(axis=2) <= a.tol
    if a.box:
        x0, y0, x1, y1 = a.box
        mm = np.zeros_like(m); mm[y0:y1, x0:x1] = m[y0:y1, x0:x1]; m = mm
    lab, _ = ndimage.label(m)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        ys, xs = sl
        area = int((lab[sl] == i + 1).sum())
        if area >= a.min_area:
            out.append((xs.start, ys.start, xs.stop, ys.stop, area))
    for b in sorted(out, key=lambda b: (b[1], b[0])):
        print(f"box {b[0]},{b[1]},{b[2]},{b[3]}  size {b[2]-b[0]}x{b[3]-b[1]}  area {b[4]}")
    if not out:
        print("no regions; try a higher --tol or check the color with `colors`")


def cmd_extent(a):
    r, ox, oy = sub(load(a.img), a.box)
    m = np.abs(r - np.array(a.bg)).max(axis=2) > a.tol
    ys, xs = np.nonzero(m)
    if not len(xs):
        print("nothing differs from the background here"); return
    x0, y0, x1, y1 = xs.min() + ox, ys.min() + oy, xs.max() + ox + 1, ys.max() + oy + 1
    print(f"extent {x0},{y0},{x1},{y1}  size {x1-x0}x{y1-y0}  center {(x0+x1)/2:.1f},{(y0+y1)/2:.1f}")


def cmd_lines(a):
    r, ox, oy = sub(load(a.img), a.box)
    m = r.max(axis=2) > a.th
    rows = np.nonzero(m.any(axis=1))[0]
    if not len(rows):
        print("no text found; lower --th"); return
    groups, s, p = [], rows[0], rows[0]
    for y in rows[1:]:
        if y > p + a.gap:
            groups.append((s, p)); s = y
        p = y
    groups.append((s, p))
    prev = None
    for y0, y1 in groups:
        xs = np.nonzero(m[y0:y1 + 1].any(axis=0))[0]
        pitch = f"  pitch {y0 - prev}" if prev is not None else ""
        print(f"line y {y0+oy}-{y1+oy+1} (h {y1-y0+1})  x {xs.min()+ox}-{xs.max()+ox+1}{pitch}")
        prev = y0


def cmd_runs(a):
    img = load(a.img)
    row = [tuple(c) for c in img[a.y, a.x0:a.x1].tolist()]
    start, ref = a.x0, row[0]
    for i, c in enumerate(row[1:], 1):
        if max(abs(c[k] - ref[k]) for k in range(3)) > a.tol:
            if a.x0 + i - start >= a.min:
                print(f"x {start}-{a.x0+i}  rgb{ref}")
            start, ref = a.x0 + i, c
    print(f"x {start}-{a.x1}  rgb{ref}")


def cmd_corner(a):
    img = load(a.img)
    bg = img[a.y0, max(0, a.x - 20)]
    for y in range(a.y0, a.y1):
        r = img[y, a.x:a.x + 80]
        idx = np.nonzero(np.abs(r - bg).max(axis=1) > 8)[0]
        print(f"y {y}: first edge pixel at x {a.x + idx.min() if len(idx) else 'none'}")


def cmd_crop(a):
    im = Image.open(a.img).convert("RGB").crop(tuple(a.box))
    if a.zoom != 1:
        im = im.resize((im.width * a.zoom, im.height * a.zoom), Image.NEAREST)
    im.save(a.out)
    print(f"saved {a.out} ({im.width}x{im.height})")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    box = lambda q, req=False: q.add_argument("--box", type=lambda v: parse(v, 4), required=req)
    q = s.add_parser("info"); q.add_argument("img"); q.set_defaults(f=cmd_info)
    q = s.add_parser("colors"); q.add_argument("img"); box(q); q.add_argument("-n", type=int, default=8); q.set_defaults(f=cmd_colors)
    q = s.add_parser("boxes"); q.add_argument("img"); q.add_argument("--color", type=lambda v: parse(v, 3), required=True)
    q.add_argument("--tol", type=int, default=2); box(q); q.add_argument("--min-area", type=int, default=50); q.set_defaults(f=cmd_boxes)
    q = s.add_parser("extent"); q.add_argument("img"); box(q, True); q.add_argument("--bg", type=lambda v: parse(v, 3), required=True)
    q.add_argument("--tol", type=int, default=8); q.set_defaults(f=cmd_extent)
    q = s.add_parser("lines"); q.add_argument("img"); box(q, True); q.add_argument("--th", type=int, default=60)
    q.add_argument("--gap", type=int, default=6); q.set_defaults(f=cmd_lines)
    q = s.add_parser("runs"); q.add_argument("img"); q.add_argument("--y", type=int, required=True)
    q.add_argument("--x0", type=int, default=0); q.add_argument("--x1", type=int, required=True)
    q.add_argument("--tol", type=int, default=6); q.add_argument("--min", type=int, default=3); q.set_defaults(f=cmd_runs)
    q = s.add_parser("corner"); q.add_argument("img"); q.add_argument("--x", type=int, required=True)
    q.add_argument("--y0", type=int, required=True); q.add_argument("--y1", type=int, required=True); q.set_defaults(f=cmd_corner)
    q = s.add_parser("crop"); q.add_argument("img"); box(q, True); q.add_argument("--out", required=True)
    q.add_argument("--zoom", type=int, default=1); q.set_defaults(f=cmd_crop)
    a = p.parse_args(); a.f(a)


if __name__ == "__main__":
    main()
