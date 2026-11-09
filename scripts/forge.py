#!/usr/bin/env python3
"""forge.py: generates the SVG assets for the GitHub profile README.

Concept: "Data Grimoire x Mission Control". Occult sigils, tarot arcana and
alchemical tables, rendered as a starship HUD.

Usage:
    python3 scripts/forge.py

Edit the DATA section below, run the script, commit `assets/`.
Standard library only. GitHub renders the SVGs as <img>, so CSS animations
and SMIL work, JavaScript and web fonts do not.
"""
from __future__ import annotations

import math
import random
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

# ════════════════════════════════════════════════════════════════════ DATA ══

IDENTITY = {
    "name": "ŠTĚPÁN REŠL",
    "prompt": "> whoami --verbose",
    "facts": [
        "Microsoft MVP · Data Platform (Power BI & Fabric)",
        "Managing Partner & Lead Technical Consultant",
        "DataBrothers · Prague",
        "Co-organizer · Czech Fabric User Group",
        "Co-author · Exam Ref DP-600",
    ],
    "motto": [
        "“Don't say something cannot be done, or someone",
        "who doesn't know will come and do it.”",
    ],
    "hud_left": "SYS ▸ honesty 90% · humor 75% · caffeine nominal",
    "hud_right": "50.0755°N 14.4378°E · PRAGUE · CREW 4/4",
}

# Incantation ring around the sigil
RUNES = (
    "let Source = Lakehouse.Contents() in Source ✦ "
    "EVALUATE SUMMARIZECOLUMNS() ✦ "
    'spark.read.format("delta") ✦ '
    "SELECT * FROM gold ✦ "
    "CALCULATE([Truth], REMOVEFILTERS(Doubt)) ✦ "
)

# (label, color key, orbit radius, period s, phase 0..1, kind)
FAMILIARS = [
    ("V.I.K.I.", "violet", 84, 34, 0.10, "orb"),
    ("T.A.R.S.", "cyan", 114, 52, 0.55, "slab"),
    ("GERTY", "gold", 140, 76, 0.30, "smile"),
]

# (roman, title, line1, line2, symbol)
ARCANA = [
    ("I", "THE MAGICIAN", "Power Query · M", "custom functions", "magician"),
    ("II", "THE HIGH PRIESTESS", "DAX · Semantic", "Models", "priestess"),
    ("VII", "THE CHARIOT", "Orchestration", "Airflow · Pipelines", "chariot"),
    ("X", "WHEEL OF FORTUNE", "PySpark · Python", "Notebooks", "wheel"),
    ("XVII", "THE STAR", "Microsoft Fabric", "Lakehouse · OneLake", "star"),
    ("XIX", "THE SUN", "Power BI", "SVG visuals · UX", "sun"),
]

# (number, symbol, name, glyph, category)
ELEMENTS = [
    (1, "Py", "Python", "☿", "lang"),
    (2, "M", "Power Query M", "♄", "lang"),
    (3, "Dx", "DAX", "♃", "lang"),
    (4, "Sq", "SQL", "△", "lang"),
    (5, "Ps", "PowerShell", "▽", "lang"),
    (6, "Sv", "SVG", "✧", "lang"),
    (7, "Fb", "Microsoft Fabric", "☉", "platform"),
    (8, "Bi", "Power BI", "♀", "platform"),
    (9, "Lh", "Lakehouse · Delta", "⊕", "platform"),
    (10, "Sk", "PySpark", "♂", "engine"),
    (11, "Af", "Airflow", "≋", "engine"),
    (12, "Ag", "AI Agents", "☽", "engine"),
]
ELEMENT_CLASSES = {
    "lang": ("gold", "LANGUAGES & SCRIPTS"),
    "platform": ("violet", "PLATFORMS"),
    "engine": ("cyan", "ENGINES & FAMILIARS"),
}

# Talks per year, counted from sessionize.com/stepan-resl
TRANSMISSIONS = {2019: 1, 2020: 5, 2021: 6, 2022: 3, 2023: 8, 2024: 10, 2025: 7, 2026: 8}
LATEST_SIGNALS = [
    ("FabFest 2026", "Birmingham"),
    ("dataMinds Connect 2026", "Mechelen"),
    ("Data Saturday Holland", "Utrecht"),
    ("Power BI Next Step 2026", "Odense"),
    ("Data Point Prague 2026", "Prague"),
    ("DataGrillen 2026", "Lingen"),
    ("SQLDay 2026", "Wrocław"),
    ("SQLBits 2025", "London"),
]

# (file slug, mission no, tag, title, description lines, footer)
MISSIONS = [
    ("m-custom-functions", 1, "REPO · POWER QUERY M", "M Custom Functions",
     ["Library of mostly pure M functions", "for everyday Power Query work."],
     "github.com/tirnovar/m-custom-functions"),
    ("power-bi-rest-api-pq", 2, "REPO · POWER QUERY M", "Power BI REST API · PQ",
     ["Custom Power Query functions for", "calling the Power BI REST API."],
     "github.com/tirnovar/Power_BI_REST_API_PQ"),
    ("power-bi-admin-connector", 3, "REPO · CONNECTOR", "Power BI Admin REST API",
     ["Power Query connector for the", "Power BI Admin REST API."],
     "github.com/tirnovar/Power-BI-Admin-REST-API-Connector"),
    ("fabric-usage-metrics", 4, "REPO · PYSPARK NOTEBOOK", "Fabric Usage Metrics",
     ["Report usage metrics across many", "Fabric workspaces at once."],
     "github.com/tirnovar/Fabric-Multi-Workspace-Usage-Metric-Of-Reports"),
    ("m-game", 5, "TRAINING · PUBLIC", "M-Game",
     ["Public Power Query training.", "Learn M by playing."],
     "mgame.datameerkat.com"),
    ("dp-600", 6, "BOOK · MICROSOFT PRESS", "Exam Ref DP-600",
     ["Implementing Analytics Solutions", "Using Microsoft Fabric."],
     "amazon.com/dp/0135336023"),
]

# Off-duty dossier: (label, icon) and the audio channel
OFF_DUTY = [
    ("SAILOR", "sail"),
    ("TRAVELER", "plane"),
    ("GAMER", "gamepad"),
    ("GEEK", "robot"),
    ("FOODIE", "plate"),
    ("RED WINE", "wine"),
]
GENRES = "METAL · ROCK · ELECTRO-SWING · POP · …"

# Dossier: intro banner and credential tiles (file slug, role, title, icon)
DOSSIER_INTRO = (
    "I make data platforms behave.",
    "Mostly Microsoft Fabric · Power BI · Power Query · Python,",
    "and SVG whenever a report needs to look like it means it.",
)
CREDENTIALS = [
    ("mvp", "MICROSOFT MVP", "Data Platform", "medal"),
    ("databrothers", "MANAGING PARTNER", "DataBrothers", "briefcase"),
    ("datameerkat", "BLOG", "Data Meerkat", "quill"),
    ("user-group", "CO-ORGANIZER", "Czech Fabric UG", "network"),
    ("dp-600", "CO-AUTHOR", "Exam Ref DP-600", "book"),
]
AI_CREW = "V.I.K.I. · T.A.R.S. · GERTY"

# (file slug, label, color key)
COMMS = [
    ("linkedin", "LINKEDIN", "gold"),
    ("bluesky", "BLUESKY", "cyan"),
    ("x", "X", "ink"),
    ("mastodon", "MASTODON", "violet"),
    ("sessionize", "SESSIONIZE", "gold"),
    ("datameerkat", "DATA MEERKAT", "cyan"),
]

# ═══════════════════════════════════════════════════════════════ PALETTE ══

C = {
    "void": "#07061A",
    "deep": "#0E0B24",
    "panel": "#15112F",
    "gold": "#E8C66A",
    "gold_d": "#A8822F",
    "violet": "#9B7BFF",
    "cyan": "#5FE3D0",
    "ink": "#ECE6FF",
    "dim": "#8E88B8",
    "faint": "#3B3568",
    "hud": "#5E579A",
}
SERIF = "Cinzel, 'Cormorant Garamond', 'Trajan Pro', Georgia, 'Times New Roman', serif"
MONO = "'JetBrains Mono', 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
TEXT_VS = "︎"  # force text (not emoji) presentation for planet glyphs
MONO_W = 0.602  # average advance of a monospace glyph, in em

BASE_CSS = f"""
.serif{{font-family:{SERIF}}}
.mono{{font-family:{MONO}}}
@keyframes twinkle{{0%,100%{{opacity:.12}}50%{{opacity:.95}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes spinr{{to{{transform:rotate(-360deg)}}}}
@keyframes fadeup{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@keyframes fadein{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes pulse{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}
.tw{{animation:twinkle 5s ease-in-out infinite}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""


def esc(s: str) -> str:
    return escape(s, quote=True)


def f(n: float) -> str:
    """Compact number formatting for coordinates."""
    s = f"{n:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def svg(w: int, h: int, title: str, body: str, css: str = "", defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">\n'
        f"<title>{esc(title)}</title>\n"
        f"<defs><style>{BASE_CSS}{css}</style>{defs}</defs>\n"
        f"{body}\n</svg>\n"
    )


def write(rel: str, content: str) -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✦ {path.relative_to(ROOT)}  ({len(content.encode()) / 1024:.1f} kB)", flush=True)


# ═════════════════════════════════════════════════════════════ PRIMITIVES ══

def starfield(w: int, h: int, n: int, seed: int) -> str:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(4, w - 4), rnd.uniform(4, h - 4)
        r = rnd.choice([0.5, 0.6, 0.8, 1.0, 1.2, 1.6])
        col = C[rnd.choice(["ink", "ink", "ink", "gold", "violet", "cyan"])]
        if rnd.random() < 0.45:
            d, dur = rnd.uniform(0, 7), rnd.uniform(3, 8)
            out.append(
                f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="{col}" class="tw" '
                f'style="animation-delay:-{f(d)}s;animation-duration:{f(dur)}s"/>'
            )
        else:
            out.append(
                f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="{col}" '
                f'opacity="{f(rnd.uniform(0.12, 0.5))}"/>'
            )
    return "\n".join(out)


def backdrop(w: int, h: int, gid: str = "bg", cx: str = "70%", cy: str = "45%") -> tuple[str, str]:
    defs = (
        f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="90%">'
        f'<stop offset="0" stop-color="#1B1440"/>'
        f'<stop offset=".45" stop-color="{C["deep"]}"/>'
        f'<stop offset="1" stop-color="{C["void"]}"/></radialGradient>'
    )
    body = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" '
        f'fill="url(#{gid})" stroke="{C["faint"]}"/>'
    )
    return defs, body


def corners(w: int, h: int, inset: int = 10, size: int = 16) -> str:
    i, s = inset, size
    paths = [
        f"M{i} {i + s}V{i}H{i + s}",
        f"M{w - i - s} {i}H{w - i}V{i + s}",
        f"M{i} {h - i - s}V{h - i}H{i + s}",
        f"M{w - i - s} {h - i}H{w - i}V{h - i - s}",
    ]
    return "".join(
        f'<path d="{p}" fill="none" stroke="{C["cyan"]}" stroke-width="1.4" opacity=".55"/>'
        for p in paths
    )


def glow_filter(fid: str = "glow", sd: float = 2.4) -> str:
    return (
        f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feGaussianBlur stdDeviation="{sd}" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )


def polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def star_points(cx: float, cy: float, n: int, r_out: float, r_in: float, rot: float = -90) -> str:
    pts = []
    for k in range(2 * n):
        r = r_out if k % 2 == 0 else r_in
        x, y = polar(cx, cy, r, rot + k * 180 / n)
        pts.append(f"{f(x)},{f(y)}")
    return " ".join(pts)


# ═══════════════════════════════════════════════════════════════════ HERO ══

def hero() -> str:
    W, H = 900, 420
    cx, cy = 700, 210
    R_DIAL, R_RUNE, R_SIGIL = 182, 162, 150

    bg_defs, bg = backdrop(W, H, cx="76%", cy="50%")
    defs = bg_defs + glow_filter() + glow_filter("softglow", 6)
    defs += (
        f'<radialGradient id="halo"><stop offset="0" stop-color="{C["gold"]}" stop-opacity=".55"/>'
        f'<stop offset=".35" stop-color="#E88A3A" stop-opacity=".16"/>'
        f'<stop offset="1" stop-color="{C["violet"]}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="disk" x1="0" x2="1">'
        f'<stop offset="0" stop-color="#FFB45E" stop-opacity=".15"/>'
        f'<stop offset=".5" stop-color="#FFEAB0"/>'
        f'<stop offset="1" stop-color="#FFB45E" stop-opacity=".15"/></linearGradient>'
        f'<linearGradient id="trail" x1="1" x2="0"><stop offset="0" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<path id="runepath" d="M{cx - R_RUNE} {cy}a{R_RUNE} {R_RUNE} 0 1 1 {2 * R_RUNE} 0'
        f'a{R_RUNE} {R_RUNE} 0 1 1 {-2 * R_RUNE} 0"/>'
    )

    # typing effect for the prompt (SMIL, plays once)
    prompt = IDENTITY["prompt"]
    px, py, pfs = 48, 70, 13
    cw = pfs * MONO_W
    n = len(prompt)
    widths = ";".join(f(cw * k + (2 if k else 0)) for k in range(n + 1))
    cursor_xs = ";".join(f(px + cw * k + 2) for k in range(n + 1))
    t_type = round(n * 0.07, 2)
    defs += (
        f'<clipPath id="typeclip"><rect x="{px - 2}" y="{py - 15}" width="{f(cw * n + 4)}" height="22">'
        f'<animate attributeName="width" values="{widths}" dur="{t_type}s" begin=".4s" '
        f'calcMode="discrete" fill="freeze"/></rect></clipPath>'
    )

    css = f"""
.name{{animation:fadeup 1s ease-out {t_type + 0.5}s both}}
.fact{{animation:fadeup .7s ease-out both}}
.motto{{animation:fadein 1.6s ease-out {t_type + 2.4}s both}}
.disk{{animation:pulse 6s ease-in-out infinite}}
@keyframes shoot{{0%{{transform:translate(0,0);opacity:0}}1.5%{{opacity:1}}9%{{transform:translate(-300px,150px);opacity:0}}100%{{transform:translate(-300px,150px);opacity:0}}}}
.shoot{{animation:shoot 11s linear 3s infinite;opacity:0}}
"""

    b = [bg, starfield(W, H, 110, seed=7), corners(W, H)]

    # shooting star
    b.append(
        f'<g class="shoot"><line x1="560" y1="40" x2="620" y2="10" stroke="url(#trail)" '
        f'stroke-width="1.4" stroke-linecap="round"/></g>'
    )

    # ── dial (mission control) ──
    ticks = []
    for k in range(72):
        deg = k * 5
        long_ = k % 6 == 0
        r1 = R_DIAL - (12 if long_ else 6)
        x1, y1 = polar(cx, cy, r1, deg)
        x2, y2 = polar(cx, cy, R_DIAL, deg)
        ticks.append(
            f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" '
            f'stroke="{C["cyan"]}" stroke-width="{1.2 if long_ else 0.8}" '
            f'opacity="{0.55 if long_ else 0.28}"/>'
        )
    b.append(
        f'<g style="transform-origin:{cx}px {cy}px;animation:spinr 300s linear infinite">'
        + "".join(ticks)
        + "</g>"
    )

    # ── incantation ring ──
    ring_len = 2 * math.pi * R_RUNE - 6
    b.append(
        f'<g style="transform-origin:{cx}px {cy}px;animation:spin 150s linear infinite">'
        f'<text class="mono" font-size="9.5" fill="{C["gold"]}" opacity=".6" letter-spacing=".6">'
        f'<textPath href="#runepath" textLength="{f(ring_len)}" lengthAdjust="spacing">'
        f"{esc(RUNES)}</textPath></text></g>"
    )

    # ── sigil: heptagram of the seven classical planets ──
    verts = [polar(cx, cy, R_SIGIL, -90 + k * 360 / 7) for k in range(7)]
    order = [(k * 3) % 7 for k in range(8)]
    d = "M" + "L".join(f"{f(verts[i][0])} {f(verts[i][1])}" for i in order) + "Z"
    planets = ["☉", "☽", "☿", "♀", "♂", "♃", "♄"]
    sig = [
        f'<circle cx="{cx}" cy="{cy}" r="{R_SIGIL}" fill="none" stroke="{C["gold"]}" opacity=".38"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{R_SIGIL - 5}" fill="none" stroke="{C["gold"]}" '
        f'stroke-width=".6" opacity=".2"/>',
        f'<path d="{d}" fill="none" stroke="{C["gold"]}" stroke-width="1" opacity=".42" '
        f'stroke-linejoin="round"/>',
    ]
    for (vx, vy), p in zip(verts, planets):
        sig.append(
            f'<circle cx="{f(vx)}" cy="{f(vy)}" r="9.5" fill="{C["deep"]}" '
            f'stroke="{C["gold"]}" stroke-width=".9" opacity=".95"/>'
            f'<text x="{f(vx)}" y="{f(vy + 4)}" text-anchor="middle" font-size="11" '
            f'fill="{C["gold"]}" class="serif">{p}{TEXT_VS}</text>'
        )
    b.append(
        f'<g style="transform-origin:{cx}px {cy}px;animation:spinr 200s linear infinite">'
        + "".join(sig)
        + "</g>"
    )

    # ── orbits ──
    for _, col, r, *_ in FAMILIARS:
        b.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C[col]}" '
            f'stroke-width=".8" stroke-dasharray="1 5" opacity=".45"/>'
        )

    # ── Gargantua: the commander's core ──
    rx, ry = 58, 11
    b.append(
        f'<circle cx="{cx}" cy="{cy}" r="74" fill="url(#halo)"/>'
        f'<ellipse class="disk" cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" '
        f'stroke="url(#disk)" stroke-width="3.2" filter="url(#glow)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="31" fill="none" stroke="#FFD98A" stroke-width="1.2" '
        f'opacity=".55" filter="url(#glow)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="25" fill="#000" stroke="#FFE7A8" stroke-width="1.3"/>'
        f'<path class="disk" d="M{cx - rx} {cy}A{rx} {ry} 0 0 0 {cx + rx} {cy}" fill="none" '
        f'stroke="url(#disk)" stroke-width="3.6" filter="url(#glow)"/>'
        f'<text x="{cx}" y="{cy + 46}" text-anchor="middle" class="mono" font-size="8.5" '
        f'letter-spacing="2" fill="{C["gold"]}" opacity=".75">CMDR</text>'
    )

    # ── familiars (orbit with upright labels via counter-rotation) ──
    for label, col, r, dur, phase, kind in FAMILIARS:
        x, y = cx + r, cy
        delay = f(-dur * phase)
        color = C[col]
        if kind == "orb":
            body = (
                f'<circle cx="{x}" cy="{y}" r="12" fill="none" stroke="{color}" opacity=".45"/>'
                f'<circle cx="{x}" cy="{y}" r="6.5" fill="{color}" filter="url(#glow)"/>'
                f'<circle cx="{x}" cy="{y}" r="2.2" fill="#fff" opacity=".85"/>'
            )
        elif kind == "slab":
            segs = "".join(
                f'<line x1="{x - 4.5}" y1="{y - 9 + k * 4.5}" x2="{x + 4.5}" y2="{y - 9 + k * 4.5}" '
                f'stroke="{color}" stroke-width=".7" opacity=".7"/>'
                for k in range(1, 4)
            )
            body = (
                f'<rect x="{x - 5}" y="{y - 10}" width="10" height="20" rx="1" fill="{C["panel"]}" '
                f'stroke="{color}" stroke-width="1.3" filter="url(#glow)"/>{segs}'
            )
        else:  # smile
            body = (
                f'<circle cx="{x}" cy="{y}" r="8.5" fill="{color}" filter="url(#glow)"/>'
                f'<circle cx="{x - 3}" cy="{y - 2}" r="1.1" fill="{C["void"]}"/>'
                f'<circle cx="{x + 3}" cy="{y - 2}" r="1.1" fill="{C["void"]}"/>'
                f'<path d="M{x - 4} {y + 2}Q{x} {y + 6} {x + 4} {y + 2}" fill="none" '
                f'stroke="{C["void"]}" stroke-width="1.2" stroke-linecap="round"/>'
            )
        b.append(
            f'<g style="transform-origin:{cx}px {cy}px;animation:spin {dur}s linear {delay}s infinite">'
            f'<g style="transform-origin:{x}px {y}px;animation:spinr {dur}s linear {delay}s infinite">'
            f"{body}"
            f'<text x="{x}" y="{y + 25}" text-anchor="middle" class="mono" font-size="9.5" '
            f'letter-spacing="1" fill="{color}">{esc(label)}</text>'
            f"</g></g>"
        )

    # ── left column: identity ──
    b.append(
        f'<text x="48" y="28" class="mono" font-size="9.5" letter-spacing="2" fill="{C["cyan"]}" '
        f'opacity=".75">◉ SIGNAL LOCKED · GRIMOIRE//ENDURANCE</text>'
    )
    b.append(
        f'<g clip-path="url(#typeclip)"><text x="{px}" y="{py}" class="mono" font-size="{pfs}" '
        f'fill="{C["cyan"]}">{esc(prompt)}</text></g>'
        f'<rect class="blink" x="{f(px + cw * n + 2)}" y="{py - 11}" width="7" height="14" '
        f'fill="{C["cyan"]}" opacity=".85">'
        f'<animate attributeName="x" values="{cursor_xs}" dur="{t_type}s" begin=".4s" '
        f'calcMode="discrete" fill="freeze"/></rect>'
    )
    b.append(
        f'<text class="serif name" x="46" y="136" font-size="46" letter-spacing="5" '
        f'fill="{C["gold"]}" filter="url(#glow)">{esc(IDENTITY["name"])}</text>'
        f'<line class="name" x1="49" y1="156" x2="160" y2="156" stroke="{C["violet"]}" '
        f'stroke-width="1.2" opacity=".7"/>'
        f'<circle class="name" cx="166" cy="156" r="2" fill="{C["violet"]}"/>'
    )
    for i, fact in enumerate(IDENTITY["facts"]):
        y = 194 + i * 26
        delay = t_type + 1.0 + i * 0.18
        b.append(
            f'<g class="fact" style="animation-delay:{f(delay)}s">'
            f'<text x="49" y="{y}" font-size="11" fill="{C["gold"]}" class="serif">✦</text>'
            f'<text x="68" y="{y}" class="mono" font-size="12.5" fill="{C["ink"]}">{esc(fact)}</text></g>'
        )
    for i, line in enumerate(IDENTITY["motto"]):
        b.append(
            f'<text class="serif motto" x="49" y="{350 + i * 19}" font-size="14.5" '
            f'font-style="italic" fill="{C["dim"]}">{esc(line)}</text>'
        )

    # ── HUD footer ──
    b.append(
        f'<line x1="40" y1="392" x2="460" y2="392" stroke="{C["faint"]}" stroke-dasharray="2 4"/>'
        f'<text x="48" y="408" class="mono" font-size="9.5" letter-spacing="1" fill="{C["hud"]}">'
        f'{esc(IDENTITY["hud_left"])}</text>'
        f'<text x="{W - 24}" y="408" text-anchor="end" class="mono" font-size="9.5" '
        f'letter-spacing="1" fill="{C["hud"]}">{esc(IDENTITY["hud_right"])}</text>'
    )

    return svg(W, H, "Štěpán Rešl: Data Grimoire × Mission Control", "\n".join(b), css, defs)


# ═════════════════════════════════════════════════════════════════ ARCANA ══

def sym_magician(x: float, y: float) -> str:
    g = C["gold"]
    return (
        f'<g transform="translate({f(x)} {f(y)})" fill="none" stroke="{g}" stroke-width="1.6" '
        f'stroke-linecap="round">'
        f'<path d="M0 -20C6 -32 24 -32 24 -20C24 -8 6 -8 0 -20C-6 -32 -24 -32 -24 -20'
        f'C-24 -8 -6 -8 0 -20Z" filter="url(#glow)"/>'
        f'<line x1="0" y1="0" x2="0" y2="30" stroke-width="2.4"/>'
        f'<circle cx="0" cy="-1" r="2.6" fill="{g}"/>'
        f'<g style="animation:pulse 2.4s ease-in-out infinite">'
        f'<line x1="-7" y1="-3" x2="-12" y2="-6"/><line x1="7" y1="-3" x2="12" y2="-6"/>'
        f'<line x1="-6" y1="4" x2="-11" y2="6"/><line x1="6" y1="4" x2="11" y2="6"/></g>'
        f"</g>"
    )


def sym_priestess(x: float, y: float) -> str:
    g, p = C["gold"], C["panel"]
    return (
        f'<g transform="translate({f(x)} {f(y)})">'
        f'<rect x="-36" y="-24" width="8" height="54" fill="none" stroke="{g}" stroke-width="1.2"/>'
        f'<rect x="28" y="-24" width="8" height="54" fill="{g}" opacity=".85"/>'
        f'<text x="-32" y="-29" text-anchor="middle" font-size="8" fill="{g}" class="serif">B</text>'
        f'<text x="32" y="-29" text-anchor="middle" font-size="8" fill="{g}" class="serif">J</text>'
        f'<g filter="url(#glow)"><circle cx="0" cy="0" r="17" fill="{g}"/>'
        f'<circle cx="8" cy="-5" r="15" fill="{p}"/></g>'
        f'<circle cx="0" cy="0" r="23" fill="none" stroke="{g}" stroke-width=".6" '
        f'stroke-dasharray="2 3" style="animation:spin 40s linear infinite;transform-origin:0px 0px"/>'
        f"</g>"
    )


def sym_chariot(x: float, y: float) -> str:
    g, c, p = C["gold"], C["cyan"], C["panel"]
    nodes = [(-26, 0), (0, -20), (0, 20), (26, 0)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    s = [f'<g transform="translate({f(x)} {f(y)})">']
    for a, bb in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[bb]
        s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{g}" stroke-width="1.2" opacity=".7"/>')
    for i, (nx, ny) in enumerate(nodes):
        delay = [0, 0.6, 0.6, 1.2][i]
        s.append(
            f'<circle cx="{nx}" cy="{ny}" r="5.5" fill="{p}" stroke="{g}" stroke-width="1.4" '
            f'style="animation:pulse 2.4s ease-in-out {delay}s infinite"/>'
        )
    for path, begin in (("M-26 0L0 -20L26 0", "0s"), ("M-26 0L0 20L26 0", "1.2s")):
        s.append(
            f'<circle r="2.3" fill="{c}" filter="url(#glow)">'
            f'<animateMotion dur="2.4s" begin="{begin}" repeatCount="indefinite" path="{path}"/></circle>'
        )
    s.append(f'<text x="0" y="40" text-anchor="middle" class="mono" font-size="7" fill="{g}" opacity=".7">DAG</text>')
    s.append("</g>")
    return "".join(s)


def sym_wheel(x: float, y: float) -> str:
    g = C["gold"]
    spokes = "".join(
        f'<line x1="{f(polar(0, 0, 7, a)[0])}" y1="{f(polar(0, 0, 7, a)[1])}" '
        f'x2="{f(polar(0, 0, 21, a)[0])}" y2="{f(polar(0, 0, 21, a)[1])}"/>'
        for a in range(0, 360, 45)
    )
    letters = "".join(
        f'<text x="{f(polar(0, 0, 25.5, a)[0])}" y="{f(polar(0, 0, 25.5, a)[1] + 2.5)}" '
        f'text-anchor="middle" font-size="7" fill="{g}" stroke="none" class="serif">{ch}</text>'
        for a, ch in zip((-90, 0, 90, 180), "TARO")
    )
    return (
        f'<g transform="translate({f(x)} {f(y)})">'
        f'<g style="animation:spin 24s linear infinite;transform-origin:0px 0px" fill="none" '
        f'stroke="{g}" stroke-width="1.3">'
        f'<circle r="30" stroke-width="1.6" filter="url(#glow)"/><circle r="21"/>'
        f'<circle r="7" fill="{g}"/>{spokes}{letters}</g></g>'
    )


def sym_star(x: float, y: float) -> str:
    g, c = C["gold"], C["cyan"]
    small = []
    for k in range(7):
        sx, sy = polar(0, 0, 33, -90 + 25 + k * (310 / 6))
        if sy > 18:
            continue
        small.append(
            f'<polygon points="{star_points(sx, sy, 4, 3.8, 1.2)}" fill="{g}" class="tw" '
            f'style="animation-delay:-{k * 0.7:.1f}s"/>'
        )
    return (
        f'<g transform="translate({f(x)} {f(y)})">'
        f'<polygon points="{star_points(0, -4, 8, 22, 8)}" fill="{g}" filter="url(#glow)" '
        f'style="animation:spin 60s linear infinite;transform-origin:0px -4px"/>'
        + "".join(small)
        + f'<path d="M-26 26q6.5 -5 13 0t13 0t13 0t13 0" fill="none" stroke="{c}" stroke-width="1.2" opacity=".8"/>'
        f'<path d="M-20 32q5 -4 10 0t10 0t10 0t10 0" fill="none" stroke="{c}" stroke-width="1" opacity=".5"/>'
        f"</g>"
    )


def sym_sun(x: float, y: float) -> str:
    g = C["gold"]
    rays = "".join(
        f'<line x1="{f(polar(0, 0, 18, a)[0])}" y1="{f(polar(0, 0, 18, a)[1])}" '
        f'x2="{f(polar(0, 0, 30 if i % 2 == 0 else 24, a)[0])}" '
        f'y2="{f(polar(0, 0, 30 if i % 2 == 0 else 24, a)[1])}"/>'
        for i, a in enumerate(range(0, 360, 22))
    )
    return (
        f'<g transform="translate({f(x)} {f(y)})">'
        f'<g style="animation:spin 36s linear infinite;transform-origin:0px 0px" stroke="{g}" '
        f'stroke-width="1.6" stroke-linecap="round">{rays}</g>'
        f'<circle r="13" fill="{g}" filter="url(#glow)"/>'
        f'<circle r="13" fill="none" stroke="#fff" stroke-width=".6" opacity=".6"/>'
        f"</g>"
    )


SYMBOLS = {
    "magician": sym_magician,
    "priestess": sym_priestess,
    "chariot": sym_chariot,
    "wheel": sym_wheel,
    "star": sym_star,
    "sun": sym_sun,
}


def arcana() -> str:
    W, H = 900, 268
    cw, ch, gap = 128, 228, 18
    x0 = (W - (len(ARCANA) * cw + (len(ARCANA) - 1) * gap)) / 2
    y0 = 20

    defs = glow_filter("glow", 2)
    defs += (
        '<linearGradient id="sheen" x1="0" x2="1">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".13"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    )
    css = """
@keyframes sweep{0%{transform:translateX(0)}22%{transform:translateX(330px)}100%{transform:translateX(330px)}}
@keyframes edge{0%,100%{stroke-opacity:.45}50%{stroke-opacity:1}}
.edge{animation:edge 6s ease-in-out infinite}
.sheen{animation:sweep 9s ease-in-out infinite}
.card{animation:float 7s ease-in-out infinite}
"""
    b = [starfield(W, H, 40, seed=21)]
    for i, (roman, title, l1, l2, sym) in enumerate(ARCANA):
        x = x0 + i * (cw + gap)
        mx = x + cw / 2
        defs += f'<clipPath id="cc{i}"><rect x="{f(x)}" y="{y0}" width="{cw}" height="{ch}" rx="10"/></clipPath>'
        title_fs = 11 if len(title) <= 13 else 9
        title_attrs = ""
        est = len(title) * title_fs * 0.78
        if est > cw - 16:
            title_attrs = f' textLength="{cw - 18}" lengthAdjust="spacingAndGlyphs"'
        b.append(
            f'<g class="card" style="animation-delay:-{i * 1.1:.1f}s">'
            f'<rect x="{f(x)}" y="{y0}" width="{cw}" height="{ch}" rx="10" fill="{C["panel"]}" '
            f'stroke="{C["gold_d"]}" stroke-width="1.3" class="edge" style="animation-delay:{i * 0.8:.1f}s"/>'
            f'<rect x="{f(x + 6)}" y="{y0 + 6}" width="{cw - 12}" height="{ch - 12}" rx="6" fill="none" '
            f'stroke="{C["gold"]}" stroke-width=".6" opacity=".35"/>'
            f'<text x="{f(mx)}" y="{y0 + 32}" text-anchor="middle" class="serif" font-size="15" '
            f'letter-spacing="2" fill="{C["gold"]}">{roman}</text>'
            f'<line x1="{f(mx - 14)}" y1="{y0 + 42}" x2="{f(mx + 14)}" y2="{y0 + 42}" '
            f'stroke="{C["gold"]}" stroke-width=".7" opacity=".5"/>'
            + SYMBOLS[sym](mx, y0 + 98)
            + f'<line x1="{f(x + 18)}" y1="{y0 + 152}" x2="{f(x + cw - 18)}" y2="{y0 + 152}" '
            f'stroke="{C["gold"]}" stroke-width=".6" opacity=".35"/>'
            f'<text x="{f(mx)}" y="{y0 + 172}" text-anchor="middle" class="serif" '
            f'font-size="{title_fs}" letter-spacing="1.4" fill="{C["gold"]}"{title_attrs}>{esc(title)}</text>'
            f'<text x="{f(mx)}" y="{y0 + 194}" text-anchor="middle" class="mono" font-size="9.5" '
            f'fill="{C["ink"]}">{esc(l1)}</text>'
            f'<text x="{f(mx)}" y="{y0 + 209}" text-anchor="middle" class="mono" font-size="9.5" '
            f'fill="{C["dim"]}">{esc(l2)}</text>'
            f'<g clip-path="url(#cc{i})"><rect class="sheen" x="{f(x - 150)}" y="{y0}" width="70" '
            f'height="{ch}" fill="url(#sheen)" style="animation-delay:{i * 0.35:.2f}s"/></g>'
            f"</g>"
        )
    return svg(W, H, "Arcana Major: the disciplines", "\n".join(b), css, defs)


# ═══════════════════════════════════════════════════════════════ ELEMENTS ══

def elements() -> str:
    W, H = 900, 262
    cols, tw, th, gap = 6, 132, 86, 12
    x0 = (W - (cols * tw + (cols - 1) * gap)) / 2
    y0 = 16

    bg_defs, bg = backdrop(W, H, cx="50%", cy="0%")
    defs = bg_defs + (
        f'<linearGradient id="scan" x1="0" x2="1"><stop offset="0" stop-color="{C["cyan"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{C["cyan"]}" stop-opacity=".22"/></linearGradient>'
    )
    css = f"""
@keyframes scan{{from{{transform:translateX(0)}}to{{transform:translateX({W + 60}px)}}}}
.scan{{animation:scan 7s linear infinite}}
.tile{{animation:pulse 7s ease-in-out infinite}}
"""
    b = [bg, starfield(W, H, 30, seed=3)]
    for i, (num, sym, name, glyph, cat) in enumerate(ELEMENTS):
        col = C[ELEMENT_CLASSES[cat][0]]
        r, c = divmod(i, cols)
        x, y = x0 + c * (tw + gap), y0 + r * (th + gap)
        b.append(
            f'<rect x="{f(x)}" y="{y}" width="{tw}" height="{th}" rx="7" fill="{C["panel"]}" '
            f'stroke="{col}" stroke-opacity=".55"/>'
            f'<rect class="tile" x="{f(x)}" y="{y}" width="3" height="{th}" rx="1.5" fill="{col}" '
            f'style="animation-delay:{(c * 0.35 + r * 0.2):.2f}s"/>'
            f'<text x="{f(x + 12)}" y="{y + 18}" class="mono" font-size="10" fill="{C["dim"]}">{num:02d}</text>'
            f'<text x="{f(x + tw - 12)}" y="{y + 20}" text-anchor="end" class="serif" font-size="14" '
            f'fill="{col}" opacity=".85">{glyph}{TEXT_VS}</text>'
            f'<text x="{f(x + 12)}" y="{y + 56}" class="serif" font-size="30" font-weight="600" '
            f'fill="{col}">{esc(sym)}</text>'
            f'<text x="{f(x + 12)}" y="{y + 75}" class="mono" font-size="9.5" fill="{C["ink"]}" '
            f'opacity=".85">{esc(name)}</text>'
        )
    b.append(
        f'<rect class="scan" x="-60" y="8" width="60" height="{2 * th + gap + 16}" fill="url(#scan)"/>'
    )
    ly = y0 + 2 * th + gap + 34
    lx = x0
    for key in ("lang", "platform", "engine"):
        ck, label = ELEMENT_CLASSES[key]
        b.append(
            f'<rect x="{f(lx)}" y="{ly - 8}" width="9" height="9" rx="2" fill="{C[ck]}"/>'
            f'<text x="{f(lx + 16)}" y="{ly}" class="mono" font-size="9.5" letter-spacing="1.5" '
            f'fill="{C["dim"]}">{esc(label)}</text>'
        )
        lx += 16 + len(label) * 9.5 * MONO_W + len(label) * 1.5 + 36
    b.append(
        f'<text x="{f(W - x0)}" y="{ly}" text-anchor="end" class="mono" font-size="9.5" '
        f'letter-spacing="1" fill="{C["hud"]}">ATOMIC WEIGHT: UNKNOWN · HALF-LIFE: UNTIL NEXT RELEASE</text>'
    )
    return svg(W, H, "Table of Arcane Elements: the tech stack", "\n".join(b), css, defs)


# ══════════════════════════════════════════════════════════ TRANSMISSIONS ══

def transmissions() -> str:
    W, H = 900, 300
    bg_defs, bg = backdrop(W, H, cx="25%", cy="40%")
    defs = bg_defs + glow_filter("glow", 2.2) + (
        f'<radialGradient id="sg"><stop offset="0" stop-color="{C["gold"]}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{C["gold"]}" stop-opacity="0"/></radialGradient>'
    )
    css = """
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
.constellation{stroke-dasharray:1;stroke-dashoffset:0;animation:draw 3.2s ease-out .4s both}
.pt{animation:fadein .6s ease-out both}
"""
    b = [bg, starfield(W, H, 70, seed=11), corners(W, H)]

    total = sum(TRANSMISSIONS.values())
    first = min(TRANSMISSIONS)
    b.append(
        f'<text x="34" y="36" class="mono" font-size="11" letter-spacing="2" fill="{C["cyan"]}">'
        f"TRANSMISSION LOG ▸ {total} BROADCASTS SINCE {first}</text>"
        f'<text x="34" y="54" class="mono" font-size="9.5" fill="{C["hud"]}">'
        f"source: sessionize.com/stepan-resl · conferences, user groups, podcasts</text>"
    )

    years = sorted(TRANSMISSIONS)
    vmax = max(TRANSMISSIONS.values())
    gx0, gx1, base, top = 70, 530, 244, 92
    step = (gx1 - gx0) / (len(years) - 1)

    def ypos(v: float) -> float:
        return base - (base - top) * v / vmax

    for v in (0, vmax // 2, vmax):
        yy = ypos(v)
        b.append(
            f'<line x1="{gx0 - 20}" y1="{f(yy)}" x2="{gx1 + 20}" y2="{f(yy)}" stroke="{C["faint"]}" '
            f'stroke-dasharray="2 5"/>'
            f'<text x="{gx0 - 26}" y="{f(yy + 3)}" text-anchor="end" class="mono" font-size="8.5" '
            f'fill="{C["hud"]}">{v}</text>'
        )

    pts = [(gx0 + i * step, ypos(TRANSMISSIONS[y])) for i, y in enumerate(years)]
    d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts)
    b.append(
        f'<path class="constellation" pathLength="1" d="{d}" fill="none" stroke="{C["violet"]}" '
        f'stroke-width="1.2" opacity=".75"/>'
    )
    for i, ((x, y), yr) in enumerate(zip(pts, years)):
        v = TRANSMISSIONS[yr]
        r = 2.2 + v * 0.32
        delay = 0.4 + 3.2 * i / (len(years) - 1)
        last = i == len(years) - 1
        b.append(
            f'<g class="pt" style="animation-delay:{f(delay)}s">'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 4)}" fill="url(#sg)"/>'
            f'<polygon points="{star_points(x, y, 4, r * 2.2, r * 0.5)}" fill="{C["gold"]}" opacity=".9"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 0.8)}" fill="#FFF6DA" filter="url(#glow)"/>'
            f'<text x="{f(x)}" y="{f(y - r * 2.2 - 8)}" text-anchor="middle" class="mono" font-size="9.5" '
            f'fill="{C["gold"]}">×{v}</text>'
            f'<text x="{f(x)}" y="{base + 24}" text-anchor="middle" class="mono" font-size="10" '
            f'fill="{C["ink"] if last else C["dim"]}">{yr}</text>'
            + (
                f'<circle cx="{f(x)}" cy="{f(y)}" r="8" fill="none" stroke="{C["cyan"]}" stroke-width="1.2">'
                f'<animate attributeName="r" values="8;22" dur="2.2s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values=".9;0" dur="2.2s" repeatCount="indefinite"/></circle>'
                if last else ""
            )
            + "</g>"
        )
    b.append(
        f'<line x1="{gx0 - 20}" y1="{base + 8}" x2="{gx1 + 20}" y2="{base + 8}" stroke="{C["faint"]}"/>'
    )

    # latest signals panel
    px, py, pw, ph = 590, 22, 286, 256
    b.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="{C["panel"]}" '
        f'fill-opacity=".75" stroke="{C["faint"]}"/>'
        f'<text x="{px + 18}" y="{py + 26}" class="mono" font-size="10" letter-spacing="2.5" '
        f'fill="{C["cyan"]}">LATEST SIGNALS</text>'
        f'<line x1="{px + 18}" y1="{py + 36}" x2="{px + pw - 18}" y2="{py + 36}" stroke="{C["faint"]}"/>'
    )
    for i, (event, city) in enumerate(LATEST_SIGNALS):
        y = py + 60 + i * 25
        b.append(
            f'<circle cx="{px + 22}" cy="{y - 4}" r="2.6" fill="{C["gold"] if i else C["cyan"]}" '
            f'style="animation:pulse 2.6s ease-in-out {i * 0.3:.1f}s infinite"/>'
            f'<text x="{px + 34}" y="{y}" class="mono" font-size="10.5" fill="{C["ink"]}">'
            f'{esc(event)}<tspan fill="{C["dim"]}"> · {esc(city)}</tspan></text>'
        )
    return svg(W, H, f"Transmission log: {total} talks since {first}", "\n".join(b), css, defs)


# ═══════════════════════════════════════════════════════════════ MISSIONS ══

def mission_card(slug: str, no: int, tag: str, title: str, desc: list[str], foot: str) -> str:
    W, H = 430, 150
    roman = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"][no]
    bg_defs, bg = backdrop(W, H, gid="bg", cx="10%", cy="50%")
    defs = bg_defs + glow_filter("glow", 2)
    sx, sy = 58, 75
    css = """
.engage{animation:pulse 2.2s ease-in-out infinite}
"""
    title_fs = 18
    est = len(title) * title_fs * 0.62
    tl = f' textLength="300" lengthAdjust="spacingAndGlyphs"' if est > 300 else ""
    b = [
        bg,
        starfield(W, H, 18, seed=100 + no),
        corners(W, H, inset=8, size=12),
        f'<g style="transform-origin:{sx}px {sy}px;animation:spin 30s linear infinite">'
        f'<circle cx="{sx}" cy="{sy}" r="37" fill="none" stroke="{C["cyan"]}" stroke-width="1" '
        f'stroke-dasharray="2 5" opacity=".7"/>'
        f'<polygon points="{star_points(sx, sy, 7, 37, 31)}" fill="none" stroke="{C["gold"]}" '
        f'stroke-width=".6" opacity=".35"/></g>',
        f'<circle cx="{sx}" cy="{sy}" r="27" fill="{C["panel"]}" stroke="{C["gold"]}" stroke-width="1.4" '
        f'filter="url(#glow)"/>',
        f'<text x="{sx}" y="{sy + 7}" text-anchor="middle" class="serif" font-size="20" '
        f'fill="{C["gold"]}">{roman}</text>',
        f'<text x="112" y="36" class="mono" font-size="9.5" letter-spacing="1.5" fill="{C["cyan"]}">'
        f"MISSION {no:03d} · {esc(tag)}</text>",
        f'<text x="112" y="64" class="serif" font-size="{title_fs}" font-weight="600" '
        f'fill="{C["gold"]}"{tl}>{esc(title)}</text>',
    ]
    for i, line in enumerate(desc):
        b.append(
            f'<text x="112" y="{88 + i * 16}" class="mono" font-size="10.5" fill="{C["ink"]}" '
            f'opacity=".8">{esc(line)}</text>'
        )
    max_foot = 38  # leaves room for ENGAGE at 9px mono
    if len(foot) > max_foot:
        foot = foot[: max_foot - 1].rstrip("-_/") + "…"
    b.append(
        f'<text x="112" y="132" class="mono" font-size="9" fill="{C["hud"]}">{esc(foot)}</text>'
        f'<text class="engage mono" x="{W - 22}" y="132" text-anchor="end" font-size="10" '
        f'letter-spacing="2" fill="{C["gold"]}">ENGAGE ›</text>'
    )
    return svg(W, H, f"Mission {no}: {title}", "\n".join(b), css, defs)


# ══════════════════════════════════════════════════════════════════ COMMS ══

def comm_button(label: str, color_key: str, idx: int) -> str:
    W, H = 150, 40
    col = C[color_key]
    css = """
@keyframes bar{0%,100%{transform:scaleY(.35)}50%{transform:scaleY(1)}}
.bar{transform-box:fill-box;transform-origin:bottom;animation:bar 1.4s ease-in-out infinite}
"""
    bars = "".join(
        f'<rect class="bar" x="{16 + k * 4.5}" y="13" width="2.6" height="14" rx="1" fill="{col}" '
        f'style="animation-delay:-{(k * 0.25 + idx * 0.17):.2f}s"/>'
        for k in range(3)
    )
    body = (
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{(H - 2) / 2}" fill="{C["panel"]}" '
        f'stroke="{col}" stroke-opacity=".7"/>'
        f"{bars}"
        f'<text x="{(W + 30) / 2}" y="24.5" text-anchor="middle" class="mono" font-size="11" '
        f'letter-spacing="1.6" fill="{C["ink"]}">{esc(label)}</text>'
    )
    return svg(W, H, label, body, css)


# ════════════════════════════════════════════════════════════════ DOSSIER ══

def dossier_intro() -> str:
    W, H = 900, 116
    bg_defs, bg = backdrop(W, H, cx="50%", cy="0%")
    defs = bg_defs + glow_filter("glow", 2)
    headline, line1, line2 = DOSSIER_INTRO
    css = """
.hl{animation:fadeup 1s ease-out .2s both}
.sub{animation:fadein 1.4s ease-out .9s both}
"""
    body = (
        bg + starfield(W, H, 40, seed=9) + corners(W, H)
        + f'<text class="serif hl" x="{W / 2}" y="50" text-anchor="middle" font-size="27" letter-spacing="2" '
        f'fill="{C["gold"]}" filter="url(#glow)">{esc(headline)}</text>'
        f'<text class="mono sub" x="{W / 2}" y="78" text-anchor="middle" font-size="12" fill="{C["ink"]}">'
        f"{esc(line1)}</text>"
        f'<text class="mono sub" x="{W / 2}" y="96" text-anchor="middle" font-size="12" fill="{C["dim"]}">'
        f"{esc(line2)}</text>"
    )
    return svg(W, H, " ".join(DOSSIER_INTRO), body, css, defs)


def cred_icon(kind: str) -> str:
    g, c = C["gold"], C["cyan"]
    if kind == "medal":
        return (
            f'<path d="M-5 2L-9 16L-4 13L-1 17M5 2L9 16L4 13L1 17" stroke="{c}"/>'
            f'<circle cx="0" cy="-6" r="10" fill="{g}" fill-opacity=".18"/>'
            f'<polygon points="{star_points(0, -6, 5, 6, 2.6)}" fill="{g}" stroke="none" '
            f'style="animation:pulse 2.6s ease-in-out infinite"/>'
        )
    if kind == "briefcase":
        return (
            f'<path d="M-5 -7V-11H5V-7"/>'
            f'<rect x="-15" y="-7" width="30" height="20" rx="3" fill="{g}" fill-opacity=".15"/>'
            f'<path d="M-15 1H15"/><rect x="-3" y="-1" width="6" height="4" rx="1" fill="{c}" stroke="none"/>'
        )
    if kind == "quill":
        return (
            f'<path d="M13 -16C0 -14 -9 -3 -10 12C-2 9 9 0 13 -16Z" fill="{g}" fill-opacity=".18"/>'
            f'<path d="M10 -12L-10 12"/>'
            f'<path d="M-14 15H8" stroke="{c}" stroke-dasharray="22" '
            f'style="animation:write 3s ease-in-out infinite"/>'
        )
    if kind == "network":
        pts = [polar(0, 0, 14, -90 + k * 72) for k in range(5)]
        lines = "".join(f'<line x1="0" y1="0" x2="{f(x)}" y2="{f(y)}" opacity=".7"/>' for x, y in pts)
        ring = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"
        nodes = "".join(
            f'<circle cx="{f(x)}" cy="{f(y)}" r="3" fill="{C["panel"]}" '
            f'style="animation:pulse 2.5s ease-in-out {k * 0.5:.1f}s infinite"/>'
            for k, (x, y) in enumerate(pts)
        )
        return (
            f'{lines}<path d="{ring}" opacity=".35"/>{nodes}'
            f'<circle r="4.5" fill="{c}" stroke="none"/>'
        )
    if kind == "book":
        return (
            f'<path d="M0 -8C-5 -12 -12 -12 -16 -10V12C-12 10 -5 10 0 14C5 10 12 10 16 12V-10'
            f'C12 -12 5 -12 0 -8Z" fill="{g}" fill-opacity=".15"/>'
            f'<path d="M0 -8V14"/>'
            f'<path d="M-12 -4C-9 -5 -6 -5 -4 -4M-12 1C-9 0 -6 0 -4 1M4 -4C6 -5 9 -5 12 -4" '
            f'stroke-width="1" opacity=".7"/>'
        )
    raise ValueError(kind)


def credential(role: str, title: str, kind: str, idx: int) -> str:
    W, H = 176, 156
    bg_defs, bg = backdrop(W, H, cx="50%", cy="30%")
    css = """
@keyframes write{0%{stroke-dashoffset:22}60%,100%{stroke-dashoffset:0}}
.open{animation:pulse 2.4s ease-in-out infinite}
"""
    cx, cy = W / 2, 54
    direction = "spin" if idx % 2 == 0 else "spinr"
    body = (
        bg + starfield(W, H, 14, seed=200 + idx) + corners(W, H, inset=8, size=11)
        + f'<g style="transform-origin:{f(cx)}px {cy}px;animation:{direction} {26 + idx * 4}s linear infinite">'
        f'<circle cx="{f(cx)}" cy="{cy}" r="34" fill="none" stroke="{C["cyan"]}" stroke-width=".9" '
        f'stroke-dasharray="2 5" opacity=".6"/></g>'
        f'<circle cx="{f(cx)}" cy="{cy}" r="28" fill="{C["panel"]}" stroke="{C["gold_d"]}" stroke-width="1.2"/>'
        f'<g transform="translate({f(cx)} {cy})" fill="none" stroke="{C["gold"]}" stroke-width="1.6" '
        f'stroke-linecap="round" stroke-linejoin="round">{cred_icon(kind)}</g>'
        f'<text x="{f(cx)}" y="{cy + 54}" text-anchor="middle" class="mono" font-size="9" '
        f'letter-spacing="1.5" fill="{C["cyan"]}">{esc(role)}</text>'
        f'<text x="{f(cx)}" y="{cy + 75}" text-anchor="middle" class="serif" font-size="15" '
        f'font-weight="600" fill="{C["gold"]}">{esc(title)}</text>'
        f'<text class="mono open" x="{f(cx)}" y="{H - 12}" text-anchor="middle" font-size="8.5" '
        f'letter-spacing="2" fill="{C["hud"]}" style="animation-delay:{idx * 0.4:.1f}s">OPEN ›</text>'
    )
    return svg(W, H, f"{role}: {title}", body, css, bg_defs)


# ═══════════════════════════════════════════════════════════════ OFF-DUTY ══

def icon(kind: str) -> str:
    """Line-art icons drawn around (0, 0), roughly 40 px across."""
    g, v = C["gold"], C["void"]
    if kind == "sail":
        return (
            f'<g style="animation:rock 4s ease-in-out infinite;transform-origin:0px 12px">'
            f'<path d="M-16 6H16L11 13H-11Z" fill="{g}" fill-opacity=".25"/>'
            f'<line x1="0" y1="6" x2="0" y2="-18"/>'
            f'<path d="M2 -16V3H15Z" fill="{g}" fill-opacity=".85"/>'
            f'<path d="M-2 -11V3H-12Z"/></g>'
            f'<path d="M-18 17q4.5 -3 9 0t9 0t9 0t9 0" stroke="{C["cyan"]}" stroke-width="1.2" opacity=".8"/>'
        )
    if kind == "plane":
        return (
            f'<g style="animation:float 3.2s ease-in-out infinite">'
            f'<path d="M0 -18C2 -18 3 -15 3 -12V-3L17 5V8L3 4V11L8 15V17L0 15L-8 17V15L-3 11V4'
            f'L-17 8V5L-3 -3V-12C-3 -15 -2 -18 0 -18Z" fill="{g}" fill-opacity=".2"/></g>'
        )
    if kind == "gamepad":
        return (
            f'<path d="M-13 -7H13C18 -7 21 -1 20 6C19 12 15 14 12 10L8 5H-8L-12 10'
            f'C-15 14 -19 12 -20 6C-21 -1 -18 -7 -13 -7Z" fill="{g}" fill-opacity=".15"/>'
            f'<path d="M-11 -4V4M-15 0H-7" stroke-width="2"/>'
            f'<circle cx="9" cy="-2" r="1.9" fill="{C["cyan"]}" stroke="none" class="blink"/>'
            f'<circle cx="13" cy="2" r="1.9" fill="{g}" stroke="none"/>'
        )
    if kind == "robot":
        return (
            f'<line x1="0" y1="-10" x2="0" y2="-16"/>'
            f'<circle cx="0" cy="-17.5" r="2" fill="{C["cyan"]}" stroke="none" '
            f'style="animation:pulse 1.6s ease-in-out infinite"/>'
            f'<rect x="-13" y="-10" width="26" height="21" rx="5" fill="{g}" fill-opacity=".15"/>'
            f'<rect x="-17" y="-4" width="4" height="8" rx="1.5"/><rect x="13" y="-4" width="4" height="8" rx="1.5"/>'
            f'<g fill="{C["cyan"]}" stroke="none" style="animation:blinkeye 4s steps(1) infinite">'
            f'<circle cx="-5" cy="-1" r="2.6"/><circle cx="5" cy="-1" r="2.6"/></g>'
            f'<path d="M-5 5.5H5" stroke-width="1.4"/>'
        )
    if kind == "plate":
        return (
            f'<circle r="13" fill="{g}" fill-opacity=".12"/><circle r="8.5" opacity=".6"/>'
            f'<path d="M-21 -12V-3M-23.5 -12V-5C-23.5 -2 -18.5 -2 -18.5 -5V-12M-21 -3V13"/>'
            f'<path d="M21 13V-12C24.5 -9 24.5 -1 21 1"/>'
        )
    if kind == "wine":
        return (
            f'<path d="M-8.2 -9H8.2C7.4 -3 4.4 -.6 0 -.6C-4.4 -.6 -7.4 -3 -8.2 -9Z" fill="#B0283F" '
            f'stroke="none" style="animation:slosh 3.4s ease-in-out infinite;transform-origin:0px -4px"/>'
            f'<path d="M-9 -17H9C9 -5 5 0 0 0C-5 0 -9 -5 -9 -17Z"/>'
            f'<line x1="0" y1="0" x2="0" y2="13"/><line x1="-7" y1="13.5" x2="7" y2="13.5"/>'
        )
    raise ValueError(kind)


def off_duty() -> str:
    W, H = 900, 210
    bg_defs, bg = backdrop(W, H, cx="20%", cy="50%")
    defs = bg_defs + glow_filter("glow", 1.6) + (
        f'<linearGradient id="eq" x1="0" y1="1" x2="0" y2="0" gradientUnits="objectBoundingBox">'
        f'<stop offset="0" stop-color="{C["violet"]}"/><stop offset="1" stop-color="{C["cyan"]}"/>'
        f"</linearGradient>"
    )
    css = """
@keyframes rock{0%,100%{transform:rotate(-5deg)}50%{transform:rotate(5deg)}}
@keyframes slosh{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(4deg)}}
@keyframes blinkeye{0%,92%{opacity:1}93%,97%{opacity:0}98%,100%{opacity:1}}
@keyframes eq{0%,100%{transform:scaleY(.15)}50%{transform:scaleY(1)}}
.eq{transform-box:fill-box;transform-origin:bottom;animation:eq 1s ease-in-out infinite}
@keyframes lbl{0%,100%{opacity:.7}50%{opacity:1}}
.lbl{animation:lbl 5s ease-in-out infinite}
"""
    b = [bg, starfield(W, H, 45, seed=77), corners(W, H)]
    b.append(
        f'<text x="34" y="34" class="mono" font-size="11" letter-spacing="1.5" fill="{C["cyan"]}">'
        f"&gt; crew.dossier --off-duty</text>"
        f'<text x="{W - 34}" y="34" text-anchor="end" class="mono" font-size="9.5" letter-spacing="1.5" '
        f'fill="{C["hud"]}">STATUS: SHORE LEAVE · COMMS OPEN</text>'
    )

    # badges
    cy = 104
    for i, (label, kind) in enumerate(OFF_DUTY):
        x = 82 + i * 90
        direction = "spin" if i % 2 == 0 else "spinr"
        b.append(
            f'<g style="transform-origin:{x}px {cy}px;animation:{direction} {24 + i * 3}s linear infinite">'
            f'<circle cx="{x}" cy="{cy}" r="36" fill="none" stroke="{C["cyan"]}" stroke-width=".9" '
            f'stroke-dasharray="2 5" opacity=".6"/></g>'
            f'<circle cx="{x}" cy="{cy}" r="30" fill="{C["panel"]}" stroke="{C["gold_d"]}" stroke-width="1.2"/>'
            f'<g transform="translate({x} {cy})" fill="none" stroke="{C["gold"]}" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round">{icon(kind)}</g>'
            f'<text class="mono lbl" x="{x}" y="{cy + 56}" text-anchor="middle" font-size="9.5" '
            f'letter-spacing="1.8" fill="{C["ink"]}" style="animation-delay:{i * 0.6:.1f}s">{label}</text>'
        )

    # audio channel
    px, py, pw, ph = 600, 52, 268, 128
    b.append(
        f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="{C["panel"]}" '
        f'fill-opacity=".75" stroke="{C["faint"]}"/>'
        f'<text x="{px + 16}" y="{py + 22}" class="mono" font-size="10" letter-spacing="2.5" '
        f'fill="{C["cyan"]}">AUDIO CHANNEL</text>'
        f'<circle cx="{px + pw - 54}" cy="{py + 18.5}" r="3" fill="#FF5A6E" class="blink"/>'
        f'<text x="{px + pw - 16}" y="{py + 22}" text-anchor="end" class="mono" font-size="9" '
        f'letter-spacing="1.5" fill="{C["dim"]}">LIVE</text>'
    )
    rnd = random.Random(5)
    n_bars, bw, gap = 24, 6, 4
    bx0 = px + (pw - (n_bars * bw + (n_bars - 1) * gap)) / 2
    base, bh = py + 92, 52
    for k in range(n_bars):
        dur = rnd.uniform(0.55, 1.4)
        delay = rnd.uniform(0, 1.4)
        b.append(
            f'<rect class="eq" x="{f(bx0 + k * (bw + gap))}" y="{base - bh}" width="{bw}" height="{bh}" '
            f'rx="1.5" fill="url(#eq)" style="animation-duration:{f(dur)}s;animation-delay:-{f(delay)}s"/>'
        )
    b.append(
        f'<line x1="{px + 16}" y1="{base + 2}" x2="{px + pw - 16}" y2="{base + 2}" stroke="{C["faint"]}"/>'
        f'<text x="{px + pw / 2}" y="{py + ph - 14}" text-anchor="middle" class="mono" font-size="10" '
        f'fill="{C["ink"]}">{esc(GENRES)}</text>'
    )

    b.append(
        f'<text x="34" y="{H - 16}" class="mono" font-size="9.5" letter-spacing="1" fill="{C["hud"]}">'
        f"AI CREW ON WATCH ▸ {esc(AI_CREW)}</text>"
    )
    return svg(W, H, "Off-duty: sailor, traveler, gamer, geek, foodie, red wine lover; "
                     "music: metal, rock, electro-swing, pop", "\n".join(b), css, defs)


# ═══════════════════════════════════════════════════════ DIVIDER / FOOTER ══

def divider() -> str:
    W, H = 900, 30
    cx, cy = W / 2, H / 2
    defs = (
        f'<linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{C["gold"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{C["gold"]}" stop-opacity=".7"/></linearGradient>'
        f'<linearGradient id="r" x1="1" x2="0"><stop offset="0" stop-color="{C["gold"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{C["gold"]}" stop-opacity=".7"/></linearGradient>'
    )
    verts = [polar(cx, cy, 11, -90 + k * 360 / 7) for k in range(7)]
    d = "M" + "L".join(f"{f(verts[(k * 3) % 7][0])} {f(verts[(k * 3) % 7][1])}" for k in range(8)) + "Z"
    body = (
        f'<line x1="40" y1="{cy}" x2="{cx - 30}" y2="{cy}" stroke="url(#l)"/>'
        f'<line x1="{cx + 30}" y1="{cy}" x2="{W - 40}" y2="{cy}" stroke="url(#r)"/>'
        f'<circle cx="{cx - 22}" cy="{cy}" r="1.6" fill="{C["gold"]}" class="tw"/>'
        f'<circle cx="{cx + 22}" cy="{cy}" r="1.6" fill="{C["gold"]}" class="tw" style="animation-delay:-2.5s"/>'
        f'<g style="transform-origin:{f(cx)}px {f(cy)}px;animation:spin 40s linear infinite">'
        f'<circle cx="{f(cx)}" cy="{f(cy)}" r="11" fill="none" stroke="{C["gold"]}" stroke-width=".8" opacity=".7"/>'
        f'<path d="{d}" fill="none" stroke="{C["gold"]}" stroke-width=".8"/></g>'
    )
    return svg(W, H, "divider", body, "", defs)


def footer() -> str:
    W, H = 900, 120
    bg_defs, bg = backdrop(W, H, cx="50%", cy="100%")
    body = (
        bg + starfield(W, H, 60, seed=42) + corners(W, H)
        + f'<text x="{W / 2}" y="44" text-anchor="middle" class="mono" font-size="11" letter-spacing="3" '
        f'fill="{C["dim"]}">END OF TRANSMISSION</text>'
        f'<rect class="blink" x="{W / 2 + 98}" y="34" width="7" height="12" fill="{C["cyan"]}"/>'
        f'<text x="{W / 2}" y="78" text-anchor="middle" class="serif" font-size="20" font-style="italic" '
        f'letter-spacing="1" fill="{C["gold"]}">Per data ad astra.</text>'
        f'<text x="{W / 2}" y="102" text-anchor="middle" class="mono" font-size="9" letter-spacing="1" '
        f'fill="{C["hud"]}">forged by scripts/forge.py · zero JavaScript was harmed</text>'
    )
    return svg(W, H, "End of transmission. Per data ad astra.", body, "", bg_defs)


# ═══════════════════════════════════════════════════════════════════ MAIN ══

def main() -> None:
    jobs: list[tuple[str, callable]] = [
        ("hero.svg", hero),
        ("arcana.svg", arcana),
        ("elements.svg", elements),
        ("transmissions.svg", transmissions),
        ("off-duty.svg", off_duty),
        ("dossier.svg", dossier_intro),
        ("divider.svg", divider),
        ("footer.svg", footer),
    ]
    jobs += [(f"missions/{m[0]}.svg", lambda m=m: mission_card(*m)) for m in MISSIONS]
    jobs += [
        (f"dossier/{slug}.svg", lambda r=role, t=title, k=kind, i=i: credential(r, t, k, i))
        for i, (slug, role, title, kind) in enumerate(CREDENTIALS)
    ]
    jobs += [
        (f"comms/{slug}.svg", lambda lab=lab, col=col, i=i: comm_button(lab, col, i))
        for i, (slug, lab, col) in enumerate(COMMS)
    ]
    print(f"Forging {len(jobs)} assets into {OUT.relative_to(ROOT)}/", flush=True)
    for k, (rel, fn) in enumerate(jobs, 1):
        print(f"[{k:2d}/{len(jobs)}]", end="", flush=True)
        write(rel, fn())
    print("Done. Per data ad astra.", flush=True)


if __name__ == "__main__":
    main()
