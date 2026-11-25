"""Generate Hoops for Hunger logo concepts as standalone SVGs (text converted to paths).

Usage: python3 make_logos.py <deutsch.ttf> <barlow-condensed-700.woff2> <barlow-condensed-600.woff2> <outdir> [site]
"""
import math
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

NAVY = "#0b1424"
NAVY2 = "#132544"
ROYAL = "#2357e8"
SKY = "#4cc3ff"
GOLD = "#e8b64c"
CREAM = "#f4f1ea"


class Font:
    def __init__(self, path, space_scale=1.0):
        self.f = TTFont(path)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"]
        self.space_scale = space_scale
        self.cache = {}

    def gname(self, ch):
        return self.cmap.get(ord(ch))

    def adv(self, ch, size):
        g = self.gname(ch)
        if g is None:
            return size * 0.3
        a = self.hmtx[g][0] * size / self.upm
        return a * self.space_scale if ch == " " else a

    def width(self, text, size, track=0.0):
        return sum(self.adv(c, size) for c in text) + track * size * max(len(text) - 1, 0)

    def d(self, ch):
        if ch not in self.cache:
            g = self.gname(ch)
            if g is None:
                self.cache[ch] = ""
            else:
                pen = SVGPathPen(self.gs)
                self.gs[g].draw(pen)
                self.cache[ch] = pen.getCommands()
        return self.cache[ch]

    def glyph(self, ch, size, x, y, rot=0.0, fill=CREAM, dx=0.0):
        d = self.d(ch)
        if not d:
            return ""
        k = size / self.upm
        return (f'<path transform="translate({x:.2f} {y:.2f}) rotate({rot:.3f}) '
                f'translate({dx:.2f} 0) scale({k:.5f} {-k:.5f})" d="{d}" fill="{fill}"/>')

    def text(self, text, size, x, y, anchor="middle", fill=CREAM, track=0.0):
        w = self.width(text, size, track)
        cx = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
        out = []
        for c in text:
            out.append(self.glyph(c, size, cx, y, fill=fill))
            cx += self.adv(c, size) + track * size
        return "".join(out)

    def arc_top(self, text, size, cx, cy, r, fill=CREAM, track=0.0, offset=0.0):
        """Text along the top of a circle, baseline radius r, reading clockwise."""
        w = self.width(text, size, track)
        pos = -w / 2
        out = []
        for c in text:
            a = self.adv(c, size)
            th = (pos + a / 2) / r + offset
            x = cx + r * math.sin(th)
            y = cy - r * math.cos(th)
            out.append(self.glyph(c, size, x, y, math.degrees(th), fill, dx=-a / 2))
            pos += a + track * size
        return "".join(out)

    def arc_bottom(self, text, size, cx, cy, r, fill=CREAM, track=0.0, offset=0.0):
        """Upright text along the bottom of a circle, baseline radius r."""
        w = self.width(text, size, track)
        pos = -w / 2
        out = []
        for c in text:
            a = self.adv(c, size)
            ph = (pos + a / 2) / r + offset
            x = cx + r * math.sin(ph)
            y = cy + r * math.cos(ph)
            out.append(self.glyph(c, size, x, y, -math.degrees(ph), fill, dx=-a / 2))
            pos += a + track * size
        return "".join(out)


def arc_split(font, left, right, size, cx, cy, r, gap_px, where="top", fill=CREAM, track=0.0):
    """Two arc labels with a gap of gap_px (along the arc) centred at the top or bottom."""
    out = []
    for text, side in ((left, -1), (right, 1)):
        half = font.width(text, size, track) / 2
        off = side * (gap_px / 2 + half) / r
        fn = font.arc_top if where == "top" else font.arc_bottom
        out.append(fn(text, size, cx, cy, r, fill, track=track, offset=off))
    return "".join(out)


def star(cx, cy, r, fill=GOLD):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.42
        a = math.pi / 5 * i - math.pi / 2
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'


def wheat(x, y, angle, length, fill=GOLD, flip=False):
    """A wheat sprig growing from (x, y) at `angle` degrees (0 = up)."""
    s = -1 if flip else 1
    parts = [f'<path d="M0 0 Q {6*s:.1f} {-length*0.5:.1f} 0 {-length:.1f}" stroke="{fill}" stroke-width="3" fill="none" stroke-linecap="round"/>']
    n = 6
    for i in range(n):
        t = 0.32 + i * (0.62 / n)
        py = -length * t
        sz = 1 - i * 0.07
        for side in (-1, 1):
            parts.append(
                f'<ellipse cx="0" cy="0" rx="{4.2*sz:.1f}" ry="{9.5*sz:.1f}" fill="{fill}" '
                f'transform="translate({side*5.5*sz + 1.5*s:.1f} {py:.1f}) rotate({side*32})"/>')
    parts.append(f'<ellipse cx="{1.5*s:.1f}" cy="{-length-4:.1f}" rx="3.8" ry="9" fill="{fill}"/>')
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({angle:.1f})">{"".join(parts)}</g>'


def cross_ball(cx, cy, r, ball=GOLD, seam=NAVY, sw=None, uid="b"):
    """Basketball whose straight seams form a cross."""
    sw = sw or max(r * 0.075, 2.5)
    hy = cy - r * 0.3  # crossbar above centre makes a Latin cross
    hw = math.sqrt(r * r - (hy - cy) ** 2)
    return f'''<g>
  <clipPath id="clip-{uid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{ball}"/>
  <g clip-path="url(#clip-{uid})" stroke="{seam}" stroke-width="{sw:.2f}" fill="none" stroke-linecap="round">
    <path d="M{cx} {cy - r} V{cy + r}"/>
    <path d="M{cx - hw:.2f} {hy:.2f} H{cx + hw:.2f}"/>
    <path d="M{cx - r*0.72:.2f} {cy - r*0.72:.2f} Q{cx - r*0.22:.2f} {cy + r*0.05:.2f} {cx - r*0.72:.2f} {cy + r*0.78:.2f}"/>
    <path d="M{cx + r*0.72:.2f} {cy - r*0.72:.2f} Q{cx + r*0.22:.2f} {cy + r*0.05:.2f} {cx + r*0.72:.2f} {cy + r*0.78:.2f}"/>
  </g>
  <circle cx="{cx}" cy="{cy}" r="{r - sw/2:.2f}" fill="none" stroke="{seam}" stroke-width="{sw:.2f}"/>
</g>'''


def luther_rose(cx, cy, r, uid="lr", gap=0.0):
    """Luther rose in the logo palette: gold ring, navy field, sky leaves,
    cream notched petals outlined in navy, sky heart bearing a navy cross.
    `gap` draws a navy halo so the medallion can sit on top of a ring line."""
    sw = max(r * 0.055, 0.9)
    parts = []
    if gap:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r + gap:.2f}" fill="{NAVY}"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.2f}" fill="{NAVY}"/>')
    # leaves between the petals
    for i in range(5):
        a = -90 + 36 + 72 * i
        L = r * 0.80
        parts.append(
            f'<path transform="translate({cx:.2f} {cy:.2f}) rotate({a + 90:.1f})" fill="{SKY}" '
            f'd="M{-L*0.13:.2f} {-L*0.35:.2f} Q0 {-L*0.75:.2f} 0 {-L:.2f} Q0 {-L*0.75:.2f} {L*0.13:.2f} {-L*0.35:.2f} Z"/>')
    # notched petals
    P = r * 0.68
    petal = (f"M0 0 C{-0.58*P:.2f} {-0.12*P:.2f} {-0.66*P:.2f} {-0.86*P:.2f} {-0.26*P:.2f} {-0.97*P:.2f} "
             f"C{-0.12*P:.2f} {-1.0*P:.2f} {-0.03*P:.2f} {-0.93*P:.2f} 0 {-0.84*P:.2f} "
             f"C{0.03*P:.2f} {-0.93*P:.2f} {0.12*P:.2f} {-1.0*P:.2f} {0.26*P:.2f} {-0.97*P:.2f} "
             f"C{0.66*P:.2f} {-0.86*P:.2f} {0.58*P:.2f} {-0.12*P:.2f} 0 0 Z")
    for i in range(5):
        a = 72 * i
        parts.append(f'<path transform="translate({cx:.2f} {cy:.2f}) rotate({a})" d="{petal}" '
                     f'fill="{CREAM}" stroke="{NAVY}" stroke-width="{sw:.2f}" stroke-linejoin="round"/>')
    # heart with cross
    h = r * 0.33
    parts.append(
        f'<path transform="translate({cx:.2f} {cy + h*0.1:.2f}) scale({h/10:.4f})" fill="{SKY}" stroke="{NAVY}" '
        f'stroke-width="{sw / (h/10):.2f}" '
        'd="M0 9 C-3 6.5 -10 2 -10 -3.5 C-10 -7.5 -7 -10 -4.3 -10 C-2.2 -10 -0.7 -8.8 0 -7.2 '
        'C0.7 -8.8 2.2 -10 4.3 -10 C7 -10 10 -7.5 10 -3.5 C10 2 3 6.5 0 9 Z"/>')
    cw = max(h * 0.17, 1.1)
    parts.append(f'<path d="M{cx:.2f} {cy - h*0.6:.2f} V{cy + h*0.62:.2f} M{cx - h*0.38:.2f} {cy - h*0.2:.2f} H{cx + h*0.38:.2f}" '
                 f'stroke="{NAVY}" stroke-width="{cw:.2f}" stroke-linecap="butt"/>')
    # gold ring
    rw = r * 0.11
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r - rw/2:.2f}" fill="none" stroke="{GOLD}" stroke-width="{rw:.2f}"/>')
    return "<g>" + "".join(parts) + "</g>"


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{body}</svg>\n')


def concept_a(dg, bc7, bc6):
    """Refined round badge: blackletter wordmark in the centre, arc text in the ring."""
    c, R = 256, 250
    b = [
        f'<defs><radialGradient id="ga" cx="50%" cy="38%" r="65%"><stop offset="0" stop-color="{NAVY2}"/><stop offset="1" stop-color="{NAVY}"/></radialGradient></defs>',
        f'<circle cx="{c}" cy="{c}" r="{R}" fill="{NAVY}"/>',
        f'<circle cx="{c}" cy="{c}" r="{R-7}" fill="none" stroke="{SKY}" stroke-width="5"/>',
        f'<circle cx="{c}" cy="{c}" r="176" fill="url(#ga)"/>',
        f'<circle cx="{c}" cy="{c}" r="176" fill="none" stroke="{SKY}" stroke-width="3"/>',
        # faint basketball seams inside the centre disc
        f'<g stroke="{SKY}" stroke-opacity="0.13" stroke-width="3" fill="none">'
        f'<path d="M{c} 82 V430"/><path d="M82 {c} H430"/>'
        f'<path d="M150 118 Q205 256 150 394"/><path d="M362 118 Q307 256 362 394"/></g>',
        arc_split(bc7, "ST. JOHN", "LUTHERAN", 31, c, c, 199, 84, "top", CREAM, track=0.16),
        bc7.arc_bottom("3V3 CHALLENGE", 31, c, c, 223, CREAM, track=0.16),
        star(c - 212, c, 9), star(c + 212, c, 9),
        luther_rose(c, c - 210, 27, uid="ra", gap=4),
        dg.text("Hoops", 88, c, 226, fill=CREAM),
        dg.text("for", 38, c, 262, fill=GOLD),
        dg.text("Hunger", 88, c, 332, fill=SKY),
        bc6.text("EST. 2026", 19, c, 378, fill=GOLD, track=0.25),
        star(c - 62, c + 122, 5), star(c + 62, c + 122, 5),
    ]
    return svg(512, 512, "".join(b), "St. John Lutheran Hoops for Hunger 3v3 Challenge")


def concept_b(dg, bc7, bc6, subtitle=True, bg=True):
    """Horizontal lockup: Luther rose emblem + wordmark (+ optional subtitle).
    bg=False gives a transparent version for placing on the site's dark header/footer."""
    pad = 36 if bg else 6
    rx = 98 if bg else 70
    h = 180 if subtitle else 148
    cy = 90 if subtitle else 74
    word_y = 100 if subtitle else 101
    tx = rx + 88
    b = [
        luther_rose(rx, cy, 64, uid="rb"),
        dg.text("Hoops for Hunger", 74, tx, word_y, anchor="start", fill=CREAM),
    ]
    if subtitle:
        b.append(bc7.text("ST. JOHN LUTHERAN  ·  3V3 CHALLENGE", 22, tx + 4, 138, anchor="start", fill=SKY, track=0.14))
    width = tx + dg.width("Hoops for Hunger", 74) + pad
    bg_rect = f'<rect width="{width:.0f}" height="{h}" rx="22" fill="{NAVY}"/>' if bg else ""
    return svg(int(width), h, bg_rect + "".join(b), "Hoops for Hunger, St. John Lutheran 3v3 Challenge")


def concept_c(dg, bc7, bc6):
    """Seal: cross-ball at the centre flanked by wheat, blackletter name around the top."""
    c, R = 256, 250
    b = [
        f'<circle cx="{c}" cy="{c}" r="{R}" fill="{NAVY}"/>',
        f'<circle cx="{c}" cy="{c}" r="{R-8}" fill="none" stroke="{GOLD}" stroke-width="4"/>',
        f'<circle cx="{c}" cy="{c}" r="{R-18}" fill="none" stroke="{GOLD}" stroke-width="1.5" stroke-opacity="0.6"/>',
        dg.arc_top("Hoops for Hunger", 54, c, c, 176, CREAM),
        arc_split(bc7, "ST. JOHN LUTHERAN", "BERLIN, WI", 21, c, c, 212, 92, "bottom", SKY, track=0.14),
        wheat(128, 352, -26, 118), wheat(384, 352, 26, 118, flip=True),
        cross_ball(c, c + 4, 90, uid="cb"),
        luther_rose(c, c + 206, 30, uid="rc", gap=6),
        star(c - 214, c + 4, 8), star(c + 214, c + 4, 8),
    ]
    return svg(512, 512, "".join(b), "Hoops for Hunger seal, St. John Lutheran, Berlin WI")


def icon(dg, bc7, bc6):
    """Square app/favicon mark."""
    b = [f'<rect width="512" height="512" rx="112" fill="{NAVY}"/>', cross_ball(256, 256, 190, uid="ic", sw=17)]
    return svg(512, 512, "".join(b), "Hoops for Hunger icon")


if __name__ == "__main__":
    dg_path, bc7_path, bc6_path, out = sys.argv[1:5]
    mode = sys.argv[5] if len(sys.argv) > 5 else "concepts"
    dg = Font(dg_path, space_scale=0.55)
    bc7 = Font(bc7_path)
    bc6 = Font(bc6_path)
    if mode == "site":
        files = {
            "hfh-badge.svg": concept_a(dg, bc7, bc6),
            "hfh-lockup.svg": concept_b(dg, bc7, bc6, subtitle=True, bg=False),
            "hfh-lockup-compact.svg": concept_b(dg, bc7, bc6, subtitle=False, bg=False),
            "hfh-icon.svg": icon(dg, bc7, bc6),
        }
    else:
        files = {"concept-a-badge.svg": concept_a(dg, bc7, bc6), "concept-b-lockup.svg": concept_b(dg, bc7, bc6),
                 "concept-c-seal.svg": concept_c(dg, bc7, bc6), "icon.svg": icon(dg, bc7, bc6)}
    for name, data in files.items():
        with open(f"{out}/{name}", "w") as fh:
            fh.write(data)
        print("wrote", name)
