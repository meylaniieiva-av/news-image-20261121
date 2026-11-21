#!/usr/bin/env python3
"""news-image-20261121: draws one 1024x1024 image summing up the world news
of Saturday 21 November 2026 and writes it to /output/entry.png.

Pure Python standard library only (no Pillow, no network, no external
assets): a pixel buffer, a 5x7 bitmap font drawn from glyph tables, and a
hand-rolled PNG encoder (zlib is stdlib). The output is deterministic:
two runs on the same machine produce byte-identical files.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (20, 20, 20)
NAVY = (22, 35, 63)
NAVY2 = (30, 48, 84)
RED = (163, 22, 33)
GOLD = (201, 162, 39)
GREY = (90, 88, 82)
LINE = (216, 210, 196)
WHITE = (255, 255, 255)
CREAM = (238, 231, 214)
STEEL = (70, 84, 120)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits ('#' = on). Classic 5x7 cell font.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "00010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10001", "01111"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}
BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per char cell)."""
    return len(text) * 6 * scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    max_chars = max(1, max_w // (6 * scale))
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    """An RGB pixel buffer with rect/line/circle/text drawing."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o:o + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            o = self._off(x0, y)
            self.px[o:o + len(row)] = row

    def rect_outline(self, x0, y0, x1, y1, color, width=2):
        self.rect(x0, y0, x1, y0 + width, color)
        self.rect(x0, y1 - width, x1, y1, color)
        self.rect(x0, y0, x0 + width, y1, color)
        self.rect(x1 - width, y0, x1, y1, color)

    def hline(self, x0, x1, y, color, width=1):
        for t in range(width):
            self.rect(x0, y + t, x1, y + t + 1, color)

    def vline(self, x, y0, y1, color, width=1):
        for t in range(width):
            self.rect(x + t, y0, x + t + 1, y1, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        """Bresenham line with square brush of the given width."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        r = width // 2
        while True:
            self.rect(x - r, y - r, x - r + width, y - r + width, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, width=2):
        """Midpoint circle outline."""
        x, y, d = 0, r, 1 - r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.rect(px - width // 2, py - width // 2,
                          px - width // 2 + width, py - width // 2 + width,
                          color)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def disc(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            dx = int((r * r - (y - cy) ** 2) ** 0.5)
            self.rect(cx - dx, y, cx + dx + 1, y + 1, color)

    def text(self, x, y, s, color, scale):
        """Draw one line of text; returns the pixel width drawn."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == '1':
                        self.rect(cx + col_i * scale, y + row_i * scale,
                                  cx + (col_i + 1) * scale,
                                  y + (row_i + 1) * scale, color)
            cx += 6 * scale
        return cx - x

    def text_centered(self, cx, y, s, color, scale):
        self.text(cx - text_width(s, scale) // 2, y, s, color, scale)

    def text_block(self, x, y, s, color, scale, max_w, leading=None):
        """Draw wrapped text; returns y just below the block."""
        leading = leading or int(7 * scale * 1.35)
        for line in wrap_text(s, scale, max_w):
            self.text(x, y, line, color, scale)
            y += leading
        return y


# ---------------------------------------------------------------- PNG writer
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(canvas, path):
    """Encode the canvas as a deterministic PNG (filter 0, zlib level 9)."""
    w, h = canvas.w, canvas.h
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------------- icons
def draw_globe(c, cx, cy, r, color):
    c.circle(cx, cy, r, color, 3)
    c.line(cx - r, cy, cx + r, cy, color, 2)
    c.circle(cx, cy, int(r * 0.45), color, 2)
    c.line(cx - r + 4, cy - int(r * 0.55), cx + r - 4, cy - int(r * 0.55),
           color, 2)
    c.line(cx - r + 4, cy + int(r * 0.55), cx + r - 4, cy + int(r * 0.55),
           color, 2)


def draw_scales(c, cx, cy, s, color):
    c.vline(cx, cy - s, cy + s, color, 3)
    c.hline(cx - s, cx + s, cy - s + 4, color, 3)
    for sx in (cx - s, cx + s):
        c.line(sx, cy - s + 4, sx - 10, cy + s - 6, color, 2)
        c.line(sx, cy - s + 4, sx + 10, cy + s - 6, color, 2)
        c.hline(sx - 10, sx + 10, cy + s - 6, color, 2)
    c.hline(cx - 14, cx + 14, cy + s, color, 3)


def draw_burst(c, cx, cy, s, color):
    """Explosion / strike burst: radiating spikes from a centre disc."""
    import math
    c.disc(cx, cy, s // 3, color)
    for k in range(8):
        ang = k * math.pi / 4
        x1 = cx + int(math.cos(ang) * s)
        y1 = cy + int(math.sin(ang) * s)
        c.line(cx, cy, x1, y1, color, 3)


def draw_cyclone(c, cx, cy, s, color):
    """Spiral: concentric arcs suggesting a storm swirl."""
    import math
    for k, (r0, a0, a1) in enumerate(((s, 0.3, 4.4), (int(s * 0.62), 2.2, 6.0),
                                     (int(s * 0.3), 4.0, 7.6))):
        steps = 24
        prev = None
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            r = r0 * (0.55 + 0.45 * i / steps)
            p = (cx + int(r * math.cos(a)), cy + int(r * math.sin(a)))
            if prev is not None:
                c.line(prev[0], prev[1], p[0], p[1], color, 2)
            prev = p


def draw_leaf(c, cx, cy, s, color):
    c.circle(cx, cy, s, color, 3)
    c.line(cx - s // 2, cy + s // 2, cx + s // 2, cy - s // 2, color, 3)


def draw_chart(c, cx, cy, s, color):
    pts = [(cx - s, cy + s // 2), (cx - s // 3, cy - s // 4),
           (cx + s // 4, cy + s // 4), (cx + s, cy - s // 2)]
    for a, b in zip(pts, pts[1:]):
        c.line(a[0], a[1], b[0], b[1], color, 3)
    c.line(cx + s, cy - s // 2, cx + s - 10, cy - s // 2, color, 3)
    c.line(cx + s, cy - s // 2, cx + s, cy - s // 2 + 10, color, 3)


def draw_link(c, cx, cy, s, color):
    """Two interlocked rings: a deal / agreement."""
    c.circle(cx - s // 3, cy, s // 2, color, 3)
    c.circle(cx + s // 3, cy, s // 2, color, 3)


# ------------------------------------------------------------------- layout
def main():
    c = Canvas(W, H, PAPER)

    # ---- header band ----
    c.rect(0, 0, W, 150, NAVY)
    c.rect(0, 150, W, 156, GOLD)
    c.text(32, 22, "THE WORLD IN ONE DAY", WHITE, 7)
    c.text(32, 96, "Saturday, 21 November 2026", GOLD, 4)
    draw_globe(c, 930, 75, 46, GOLD)

    # ---- lead story ----
    c.rect(24, 172, 1000, 408, WHITE)
    c.rect_outline(24, 172, 1000, 408, LINE, 2)
    c.rect(24, 172, 36, 408, RED)
    c.text(56, 190, "MARKETS - THE LEAD STORY", RED, 2)
    y = c.text_block(56, 222, "AI sell-off drags world markets into "
                     "correction", INK, 5, 880, leading=52)
    c.text_block(56, y + 10,
                 "The S&P 500 falls 3.7%, the Nasdaq 5.3% and the Nikkei "
                 "5.1% as AI shares plunge worldwide; both US indexes "
                 "close in correction territory.",
                 GREY, 2, 820, leading=20)
    draw_globe(c, 926, 348, 30, NAVY2)

    # ---- four-story grid ----
    stories = [
        ("MEXICO",
         "FBI most-wanted cartel boss caught",
         "Mexican forces seize Fausto Isidro Meza Flores, known as "
         "El Chapo Isidro.",
         draw_burst),
        ("KRYVYI RIH",
         "Russian missile hits Zelensky's hometown",
         "A boy, 7, and a paramedic are killed and 42 people hurt in "
         "Kryvyi Rih, Ukraine.",
         draw_burst),
        ("POLAND",
         "Russian missiles land in Poland",
         "Two missiles and a drone come down in the east; NATO calls "
         "it a grave violation of its airspace.",
         draw_burst),
        ("HEALTH",
         "Daily pill makes pancreatic tumours vanish in trial",
         "Daraxonrasib leaves tumours undetectable in 1 in 12 "
         "patients in an early trial.",
         draw_leaf),
    ]
    gx, gy, gw, gh, gap = 24, 424, 478, 196, 12
    for i, (kicker, head, body, icon) in enumerate(stories):
        x = gx + (i % 2) * (gw + gap)
        y0 = gy + (i // 2) * (gh + gap)
        c.rect(x, y0, x + gw, y0 + gh, WHITE)
        c.rect_outline(x, y0, x + gw, y0 + gh, LINE, 2)
        c.rect(x, y0, x + gw, y0 + 6, NAVY2)
        c.text(x + 18, y0 + 18, kicker, RED, 2)
        y = c.text_block(x + 18, y0 + 46, head, INK, 3, gw - 90,
                         leading=30)
        c.text_block(x + 18, y + 6, body, GREY, 2, gw - 90, leading=20)
        icon(c, x + gw - 34, y0 + gh - 34, 22, NAVY2)

    # ---- bottom strip: climate / deal / markets ----
    c.rect(24, 840, 1000, 952, NAVY)
    strip = [
        ("CLIMATE", "COP31 passes its deadline with no deal", draw_leaf),
        ("BRUSSELS", "UK and EU sign three post-Brexit deals", draw_link),
        ("THE GULF", "Tankers hit near Hormuz as talks stall", draw_chart),
    ]
    sw = (976 - 40) // 3
    for i, (kicker, head, icon) in enumerate(strip):
        x = 24 + 20 + i * sw
        if i:
            c.vline(x - 10, 856, 936, STEEL, 2)
        c.text(x, 852, kicker, GOLD, 2)
        icon(c, x + 16, 908, 13, GOLD)
        c.text_block(x + 40, 886, head, WHITE, 2, sw - 60, leading=20)

    # ---- footer ----
    c.text_centered(512, 968,
                    "All of it happened on one day: Saturday 21 November 2026",
                    INK, 2)
    c.text_centered(512, 996,
                    "Sources: Reuters, AP, CNN, BBC, One Turn - "
                    "21 Nov 2026",
                    GREY, 1)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = save_png(c, path)
    print("wrote", path, size, "bytes")


if __name__ == "__main__":
    main()
