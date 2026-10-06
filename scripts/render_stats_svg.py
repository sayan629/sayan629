#!/usr/bin/env python3

"""
Render GitHub contribution statistics as a terminal-style SVG.

Input:
    data/contributions.json

Output:
    stats.svg

Canvas:
    840 x 880

Designed to sit beside avi-ascii.svg.
"""

import datetime
import json
import os
import sys


# ============================================================
# PATHS
# ============================================================

HERE = os.path.dirname(os.path.abspath(__file__))

SRC = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(HERE, "..", "data", "contributions.json")
)

OUT = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.path.join(HERE, "..", "stats.svg")
)


# ============================================================
# COLORS
# ============================================================

BG = "#0d1117"
BG2 = "#111722"

TILE = "#161b22"
FRAME = "#30363d"

MUTED = "#7d8590"
INK = "#e6edf3"

GREEN = "#39d353"
BAR = "#26a641"

CYAN = "#22d3ee"
GOLD = "#f2cc60"


# ============================================================
# CANVAS
# ============================================================

W = 840
H = 880

PAD = 20

TITLEBAR_H = 30

COLS = 2
ROWS = 3

GAP = 16

TILE_W = (
    W
    - PAD * 2
    - GAP * (COLS - 1)
) / COLS

TILE_H = 150

TILES_TOP = TITLEBAR_H + PAD + 4

CHART_TOP = (
    TILES_TOP
    + ROWS * TILE_H
    + (ROWS - 1) * GAP
    + GAP
)


# ============================================================
# ANIMATION
# ============================================================

TILE_STAGGER = 0.15
SLIDE_DUR = 0.45

COUNT_DUR = 1.2
FRAMES = 16

BAR_START = (
    TILE_STAGGER * COLS * ROWS
    + 0.4
)

BAR_STAGGER = 0.06
BAR_DUR = 0.6


# ============================================================
# DATE HELPERS
# ============================================================

def short(date_string):
    """
    Windows-compatible date formatter.

    Example:
        2026-10-03
        -> Oct 3
    """

    date = datetime.date.fromisoformat(date_string)

    return f"{date.strftime('%b')} {date.day}"


def span(streak):
    """
    Format a streak date range.
    """

    if not streak.get("length"):
        return "—"

    start = streak.get("start", "")
    end = streak.get("end", "")

    if not start or not end:
        return "—"

    return f"{short(start)} – {short(end)}"


# ============================================================
# LOAD DATA
# ============================================================

if not os.path.exists(SRC):
    raise FileNotFoundError(
        f"Contribution data not found:\n{SRC}"
    )


with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)


days = data.get("days", [])


if not days:
    raise RuntimeError(
        "No contribution days found in contributions.json"
    )


# ============================================================
# CALCULATE SAFE FALLBACK STATS
# ============================================================

total_contributions = data.get(
    "total_contributions",
    sum(
        int(day.get("count", 0))
        for day in days
    )
)


active_days = data.get(
    "active_days",
    sum(
        1
        for day in days
        if int(day.get("count", 0)) > 0
    )
)


avg_per_active_day = data.get(
    "avg_per_active_day",
    (
        total_contributions / active_days
        if active_days
        else 0
    )
)


current_streak = data.get(
    "current_streak",
    {
        "length": 0,
        "start": "",
        "end": "",
    }
)


longest_streak = data.get(
    "longest_streak",
    {
        "length": 0,
        "start": "",
        "end": "",
    }
)


best_day = data.get(
    "best_day",
    {
        "count": 0,
        "date": "",
    }
)


monthly = data.get("monthly", [])


# ============================================================
# IF MONTHLY DATA IS MISSING, BUILD IT
# ============================================================

if not monthly:

    monthly_map = {}

    for day in days:

        date = datetime.date.fromisoformat(
            day["date"]
        )

        key = date.strftime("%Y-%m")

        monthly_map[key] = (
            monthly_map.get(key, 0)
            + int(day.get("count", 0))
        )

    monthly = [
        {
            "month": month,
            "total": total,
        }
        for month, total
        in sorted(monthly_map.items())
    ]


# ============================================================
# STAT TILES
# ============================================================

n_days = len(days)


tiles = [

    (
        "current streak",
        current_streak.get("length", 0),
        " days",
        span(current_streak),
        GREEN,
    ),

    (
        "longest streak",
        longest_streak.get("length", 0),
        " days",
        span(longest_streak),
        INK,
    ),

    (
        "contributions",
        total_contributions,
        "",
        "in the last year",
        INK,
    ),

    (
        "active days",
        active_days,
        f" / {n_days}",
        (
            f"{active_days / n_days:.0%} "
            f"of the year"
            if n_days
            else "0% of the year"
        ),
        INK,
    ),

    (
        "best day",
        best_day.get("count", 0),
        "",
        (
            short(best_day["date"])
            if best_day.get("date")
            else "—"
        ),
        GOLD,
    ),

    (
        "avg / active day",
        avg_per_active_day,
        "",
        "contributions",
        INK,
    ),
]


# ============================================================
# NUMBER FORMATTER
# ============================================================

def fmt(value, original):

    if isinstance(original, float):

        return f"{value:,.1f}"

    return f"{int(round(value)):,}"


# ============================================================
# SVG START
# ============================================================

parts = [

    (
        f'<svg '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'width="{W}" '
        f'height="{H}" '
        f'viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, '
        f'SFMono-Regular, Menlo, Consolas, monospace">'
    ),

    """
<style>

.t {
    opacity: 0;
    animation: slideIn 0.45s ease-out both;
}

@keyframes slideIn {

    0% {
        opacity: 0;
        transform: translateY(14px);
    }

    100% {
        opacity: 1;
        transform: translateY(0);
    }

}

.b {

    transform-box: fill-box;
    transform-origin: bottom;
    transform: scaleY(0);

    animation:
        growBar 0.6s ease-out both;

}

@keyframes growBar {

    to {
        transform: scaleY(1);
    }

}

@media (prefers-reduced-motion: reduce) {

    .t,
    .b {

        opacity: 1 !important;
        transform: none !important;
        animation: none !important;

    }

}

</style>
""",

    (
        f'<defs>'
        f'<linearGradient '
        f'id="bg" '
        f'x1="0" y1="0" '
        f'x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/>'
        f'<stop offset="1" stop-color="{BG}"/>'
        f'</linearGradient>'
        f'</defs>'
    ),

    (
        f'<rect '
        f'width="{W}" '
        f'height="{H}" '
        f'rx="12" '
        f'fill="url(#bg)"/>'
    ),

    (
        f'<rect '
        f'x="0.5" '
        f'y="0.5" '
        f'width="{W - 1}" '
        f'height="{H - 1}" '
        f'rx="12" '
        f'fill="none" '
        f'stroke="{FRAME}"/>'
    ),

    (
        f'<line '
        f'x1="0" '
        f'y1="{TITLEBAR_H}" '
        f'x2="{W}" '
        f'y2="{TITLEBAR_H}" '
        f'stroke="{FRAME}"/>'
    ),
]


# ============================================================
# TERMINAL DOTS
# ============================================================

for i, dot in enumerate(
    [
        "#ff5f56",
        "#ffbd2e",
        "#27c93f",
    ]
):

    parts.append(
        f'<circle '
        f'cx="{PAD + i * 16}" '
        f'cy="{TITLEBAR_H / 2}" '
        f'r="5" '
        f'fill="{dot}"/>'
    )


# ============================================================
# TERMINAL TITLE
# ============================================================

parts.append(

    f'<text '
    f'x="{W / 2}" '
    f'y="{TITLEBAR_H / 2 + 4}" '
    f'fill="{MUTED}" '
    f'font-size="12" '
    f'text-anchor="middle">'
    f'sayan@github: ~$ ./stats.sh'
    f'</text>'

)


# ============================================================
# STAT TILES
# ============================================================

for i, (
    label,
    value,
    suffix,
    caption,
    accent,
) in enumerate(tiles):

    col = i % COLS
    row = i // COLS

    x = PAD + col * (
        TILE_W + GAP
    )

    y = (
        TILES_TOP
        + row * (
            TILE_H + GAP
        )
    )

    start = i * TILE_STAGGER

    count_start = (
        start
        + SLIDE_DUR * 0.6
    )


    parts.append(
        f'<g class="t" '
        f'style="animation-delay:{start:.2f}s">'
    )


    # Tile background
    parts.append(

        f'<rect '
        f'x="{x:.1f}" '
        f'y="{y}" '
        f'width="{TILE_W:.1f}" '
        f'height="{TILE_H}" '
        f'rx="10" '
        f'fill="{TILE}" '
        f'stroke="{FRAME}"/>'

    )


    # Label
    parts.append(

        f'<text '
        f'x="{x + 24:.1f}" '
        f'y="{y + 40}" '
        f'fill="{MUTED}" '
        f'font-size="22">'
        f'$ {label}'
        f'</text>'

    )


    # Count-up animation
    num_y = y + 100


    for k in range(
        1,
        FRAMES + 1
    ):

        progress = k / FRAMES

        animated_value = (
            value
            * (
                1
                - (1 - progress) ** 3
            )
        )


        t_on = (
            count_start
            + COUNT_DUR
            * (k - 1)
            / FRAMES
        )

        t_off = (
            count_start
            + COUNT_DUR
            * k
            / FRAMES
        )


        animation = (

            f'<set '
            f'attributeName="opacity" '
            f'to="1" '
            f'begin="{t_on:.3f}s"/>'

        )


        if k < FRAMES:

            animation += (

                f'<set '
                f'attributeName="opacity" '
                f'to="0" '
                f'begin="{t_off:.3f}s"/>'

            )


        parts.append(

            f'<text '
            f'x="{x + 24:.1f}" '
            f'y="{num_y}" '
            f'opacity="0" '
            f'font-size="54" '
            f'font-weight="700" '
            f'fill="{accent}">'

            f'{fmt(animated_value, value)}'

            f'<tspan '
            f'font-size="24" '
            f'font-weight="400" '
            f'fill="{MUTED}">'
            f'{suffix}'
            f'</tspan>'

            f'{animation}'

            f'</text>'

        )


    # Caption
    parts.append(

        f'<text '
        f'x="{x + 24:.1f}" '
        f'y="{y + 132}" '
        f'fill="{MUTED}" '
        f'font-size="20">'
        f'{caption}'
        f'</text>'

    )


    parts.append("</g>")


# ============================================================
# MONTHLY CHART
# ============================================================

chart_x = PAD
chart_w = W - PAD * 2

chart_h = (
    H
    - PAD
    - CHART_TOP
)


parts.append(

    f'<g class="t" '
    f'style="animation-delay:'
    f'{BAR_START - 0.3:.2f}s">'

)

parts.append(

    f'<rect '
    f'x="{chart_x}" '
    f'y="{CHART_TOP}" '
    f'width="{chart_w}" '
    f'height="{chart_h}" '
    f'rx="10" '
    f'fill="{TILE}" '
    f'stroke="{FRAME}"/>'

)

parts.append(

    f'<text '
    f'x="{chart_x + 24}" '
    f'y="{CHART_TOP + 40}" '
    f'fill="{MUTED}" '
    f'font-size="22">'
    f'$ contributions / month'
    f'</text>'

)

parts.append("</g>")


# ============================================================
# CHART AREA
# ============================================================

if monthly:

    plot_top = CHART_TOP + 64

    plot_bot = (
        CHART_TOP
        + chart_h
        - 40
    )

    plot_l = chart_x + 24
    plot_r = (
        chart_x
        + chart_w
        - 24
    )

    slot = (
        plot_r - plot_l
    ) / len(monthly)

    bar_w = slot * 0.62

    peak = max(
        int(m.get("total", 0))
        for m in monthly
    ) or 1


    for i, month in enumerate(monthly):

        total = int(
            month.get("total", 0)
        )

        height = max(
            2,
            (
                plot_bot
                - plot_top
            )
            * total
            / peak
        )


        bx = (
            plot_l
            + i * slot
            + (slot - bar_w) / 2
        )


        fill = (
            GREEN
            if total == peak
            else BAR
        )


        delay = (
            BAR_START
            + i * BAR_STAGGER
        )


        parts.append(

            f'<rect '
            f'class="b" '
            f'x="{bx:.1f}" '
            f'y="{plot_bot - height:.1f}" '
            f'width="{bar_w:.1f}" '
            f'height="{height:.1f}" '
            f'rx="3" '
            f'fill="{fill}" '
            f'style="animation-delay:{delay:.2f}s"/>'

        )


        # Month label
        month_date = datetime.date.fromisoformat(
            month["month"] + "-01"
        )

        month_label = (
            month_date
            .strftime("%b")[0]
        )


        parts.append(

            f'<text '
            f'x="{bx + bar_w / 2:.1f}" '
            f'y="{plot_bot + 28}" '
            f'fill="{MUTED}" '
            f'font-size="18" '
            f'text-anchor="middle">'
            f'{month_label}'
            f'</text>'

        )


        # Peak label
        if total == peak:

            parts.append(

                f'<text '
                f'class="t" '
                f'style="animation-delay:'
                f'{delay + BAR_DUR:.2f}s" '
                f'x="{bx + bar_w / 2:.1f}" '
                f'y="{plot_bot - height - 10:.1f}" '
                f'fill="{INK}" '
                f'font-size="18" '
                f'text-anchor="middle">'
                f'{peak:,}'
                f'</text>'

            )


# ============================================================
# CLOSE SVG
# ============================================================

parts.append("</svg>")


svg = "".join(parts)


# ============================================================
# WRITE
# ============================================================

with open(
    OUT,
    "w",
    encoding="utf-8"
) as f:

    f.write(svg)


print("=" * 50)
print(" STATS SVG CREATED")
print("=" * 50)

print(f"Input : {SRC}")
print(f"Output: {OUT}")
print(f"Size  : {W} x {H}")
print(f"Total : {total_contributions:,}")
print(f"Active: {active_days}")
print(
    f"Average: {avg_per_active_day:.1f}"
)
print(
    f"Monthly records: {len(monthly)}"
)

print("=" * 50)