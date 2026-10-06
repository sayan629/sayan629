#!/usr/bin/env python3
"""
Render data/contributions.json as a GitHub-style contribution heatmap SVG.

Source:
    data/contributions.json

Output:
    contrib-heatmap.svg

No third-party stats API is used.
The contribution data comes from the public GitHub contributions page
via fetch_contributions.py.
"""

import datetime
import json
import os
import html


HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")


# ---------------------------------------------------------------------
# COLORS
# ---------------------------------------------------------------------

PALETTE = [
    "#161b22",  # 0
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4
    "#69f0a0",  # 5
]

BG = "#0a0e14"
BG2 = "#0d1420"
FRAME = "#1f6feb"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"


# ---------------------------------------------------------------------
# DIMENSIONS
# ---------------------------------------------------------------------

CELL = 12
GAP = 3
STEP = CELL + GAP

PAD = 22
LEFT_LABEL_W = 30
TOP_LABEL_H = 20
TITLEBAR_H = 30

STATS_H = 88


# ---------------------------------------------------------------------
# ANIMATION
# ---------------------------------------------------------------------

COL_T = 0.018
ROW_T = 0.045
CELL_DUR = 0.42


# ---------------------------------------------------------------------
# CONTRIBUTION LEVEL
# ---------------------------------------------------------------------

def level_for(count):
    """
    Convert contribution count into a GitHub-style visual level.
    """

    if count <= 0:
        return 0

    if count <= 5:
        return 1

    if count <= 15:
        return 2

    if count <= 30:
        return 3

    if count <= 50:
        return 4

    return 5


# ---------------------------------------------------------------------
# BUILD 53-WEEK STYLE GRID
# ---------------------------------------------------------------------

def build_grid(days):
    """
    Convert daily contribution records into Sunday -> Saturday columns.

    Each column contains exactly 7 rows.
    """

    if not days:
        return []

    first = datetime.date.fromisoformat(days[0]["date"])

    # Python:
    # Monday = 0
    # Sunday = 6
    #
    # We want:
    # Sunday = 0
    # Monday = 1
    # ...
    # Saturday = 6
    lead_pad = (first.weekday() + 1) % 7

    grid = []

    column = [None] * lead_pad

    for item in days:

        date = datetime.date.fromisoformat(item["date"])

        weekday = (date.weekday() + 1) % 7

        while len(column) < weekday:
            column.append(None)

        count = int(item.get("count", 0))

        column.append(
            (
                item["date"],
                count,
                level_for(count),
            )
        )

        if len(column) == 7:
            grid.append(column)
            column = []

    if column:
        while len(column) < 7:
            column.append(None)

        grid.append(column)

    return grid


# ---------------------------------------------------------------------
# MONTH LABELS
# ---------------------------------------------------------------------

def build_month_labels(grid):
    """
    Generate month labels based on the first visible day of each month.
    """

    labels = []
    seen = set()

    for column_index, column in enumerate(grid):

        for cell in column:

            if cell is None:
                continue

            date = datetime.date.fromisoformat(cell[0])

            key = (date.year, date.month)

            if key not in seen:

                seen.add(key)

                labels.append(
                    (
                        column_index,
                        date.strftime("%b"),
                    )
                )

            break

    return labels


# ---------------------------------------------------------------------
# SVG ESCAPE
# ---------------------------------------------------------------------

def esc(value):
    return html.escape(str(value), quote=True)


# ---------------------------------------------------------------------
# RENDER
# ---------------------------------------------------------------------

def render(data):

    days = data.get("days", [])

    if not days:
        raise RuntimeError(
            "No contribution days found in data/contributions.json"
        )

    grid = build_grid(days)

    if not grid:
        raise RuntimeError("Unable to construct contribution grid.")

    n_cols = len(grid)

    art_w = n_cols * STEP
    art_h = 7 * STEP

    canvas_w = (
        PAD
        + LEFT_LABEL_W
        + art_w
        + PAD
    )

    canvas_h = (
        TITLEBAR_H
        + TOP_LABEL_H
        + art_h
        + STATS_H
        + PAD
    )

    month_labels = build_month_labels(grid)

    # -----------------------------------------------------------------
    # CSS
    # -----------------------------------------------------------------

    css = f"""
@keyframes cell {{
    0% {{
        opacity: 0;
        transform: translateY(-7px);
    }}

    65% {{
        opacity: 1;
        transform: translateY(1px);
    }}

    100% {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.c {{
    opacity: 0;
    transform-box: fill-box;
    transform-origin: center;
    animation:
        cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both;
}}
""".strip()

    # -----------------------------------------------------------------
    # SVG START
    # -----------------------------------------------------------------

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{canvas_w}" height="{canvas_h}" '
            f'viewBox="0 0 {canvas_w} {canvas_h}" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
        ),

        f"<style>{css}</style>",

        "<defs>",

        (
            f'<linearGradient id="hbg" '
            f'x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG2}"/>'
            f'<stop offset="1" stop-color="{BG}"/>'
            f"</linearGradient>"
        ),

        "</defs>",

        (
            f'<rect width="{canvas_w}" height="{canvas_h}" '
            f'rx="12" fill="url(#hbg)"/>'
        ),

        (
            f'<rect x="0.5" y="0.5" '
            f'width="{canvas_w - 1}" '
            f'height="{canvas_h - 1}" '
            f'rx="12" fill="none" '
            f'stroke="{FRAME}" '
            f'stroke-width="1" '
            f'stroke-opacity="0.55"/>'
        ),

        (
            f'<line x1="0" y1="{TITLEBAR_H}" '
            f'x2="{canvas_w}" y2="{TITLEBAR_H}" '
            f'stroke="{FRAME}" '
            f'stroke-opacity="0.35"/>'
        ),
    ]

    # -----------------------------------------------------------------
    # TERMINAL DOTS
    # -----------------------------------------------------------------

    for i, dot_color in enumerate(
        ["#ff5f56", "#ffbd2e", "#27c93f"]
    ):
        parts.append(
            f'<circle '
            f'cx="{PAD + i * 16}" '
            f'cy="{TITLEBAR_H / 2}" '
            f'r="5" '
            f'fill="{dot_color}"/>'
        )

    # -----------------------------------------------------------------
    # TERMINAL TITLE
    # -----------------------------------------------------------------

    parts.append(
        f'<text '
        f'x="{canvas_w / 2}" '
        f'y="{TITLEBAR_H / 2 + 4}" '
        f'fill="{MUTED}" '
        f'font-size="12" '
        f'text-anchor="middle">'
        f'sayan@github: ~/contributions --graph'
        f'</text>'
    )

    # -----------------------------------------------------------------
    # GRID POSITION
    # -----------------------------------------------------------------

    grid_top = TITLEBAR_H + TOP_LABEL_H
    grid_left = PAD + LEFT_LABEL_W

    # -----------------------------------------------------------------
    # MONTH LABELS
    # -----------------------------------------------------------------

    for column_index, label in month_labels:

        x = grid_left + column_index * STEP

        parts.append(
            f'<text '
            f'x="{x}" '
            f'y="{TITLEBAR_H + 14}" '
            f'fill="{MUTED}" '
            f'font-size="10">'
            f'{esc(label)}'
            f'</text>'
        )

    # -----------------------------------------------------------------
    # WEEKDAY LABELS
    # -----------------------------------------------------------------

    for row_index, weekday_name in [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri"),
    ]:

        y = (
            grid_top
            + row_index * STEP
            + CELL * 0.78
        )

        parts.append(
            f'<text '
            f'x="{PAD}" '
            f'y="{y:.1f}" '
            f'fill="{MUTED}" '
            f'font-size="9">'
            f'{weekday_name}'
            f'</text>'
        )

    # -----------------------------------------------------------------
    # CONTRIBUTION BOXES
    # -----------------------------------------------------------------

    for column_index, column in enumerate(grid):

        gx = grid_left + column_index * STEP

        for row_index, cell in enumerate(column):

            if cell is None:
                continue

            date_s, count, level = cell

            gy = grid_top + row_index * STEP

            # Diagonal cascade:
            #
            # left -> right
            # top -> bottom
            delay = (
                column_index * COL_T
                + row_index * ROW_T
            )

            plural = "" if count == 1 else "s"

            parts.append(
                f'<rect '
                f'class="c" '
                f'x="{gx}" '
                f'y="{gy}" '
                f'width="{CELL}" '
                f'height="{CELL}" '
                f'rx="2.5" '
                f'fill="{PALETTE[level]}" '
                f'style="animation-delay:{delay:.3f}s">'
                f'<title>'
                f'{esc(date_s)}: '
                f'{count} contribution{plural}'
                f'</title>'
                f'</rect>'
            )

    # -----------------------------------------------------------------
    # LEGEND
    # -----------------------------------------------------------------

    leg_y = grid_top + art_h + 6

    legend_width = (
        len(PALETTE) * (CELL - 1)
        + 70
    )

    leg_x = (
        canvas_w
        - PAD
        - legend_width
    )

    parts.append(
        f'<text '
        f'x="{leg_x}" '
        f'y="{leg_y + CELL * 0.8:.1f}" '
        f'fill="{MUTED}" '
        f'font-size="10" '
        f'text-anchor="end">'
        f'Less'
        f'</text>'
    )

    lx = leg_x + 8

    for color in PALETTE:

        parts.append(
            f'<rect '
            f'x="{lx}" '
            f'y="{leg_y}" '
            f'width="{CELL - 1}" '
            f'height="{CELL - 1}" '
            f'rx="2.2" '
            f'fill="{color}"/>'
        )

        lx += CELL

    parts.append(
        f'<text '
        f'x="{lx + 4}" '
        f'y="{leg_y + CELL * 0.8:.1f}" '
        f'fill="{MUTED}" '
        f'font-size="10">'
        f'More'
        f'</text>'
    )

    # -----------------------------------------------------------------
    # STATS SEPARATOR
    # -----------------------------------------------------------------

    sep_y = leg_y + CELL + 14

    parts.append(
        f'<line '
        f'x1="0" '
        f'y1="{sep_y}" '
        f'x2="{canvas_w}" '
        f'y2="{sep_y}" '
        f'stroke="{FRAME}" '
        f'stroke-opacity="0.25"/>'
    )

    # -----------------------------------------------------------------
    # STATS
    # -----------------------------------------------------------------

    current_streak = data.get(
        "current_streak",
        {"length": 0}
    )

    longest_streak = data.get(
        "longest_streak",
        {"length": 0}
    )

    total = int(
        data.get(
            "total_contributions",
            sum(d["count"] for d in days)
        )
    )

    best_day = data.get(
        "best_day",
        {"count": 0, "date": "-"}
    )

    date_range = data.get(
        "range",
        {
            "start": days[0]["date"],
            "end": days[-1]["date"],
        }
    )

    cs = int(current_streak.get("length", 0))
    ls = int(longest_streak.get("length", 0))

    best_count = int(best_day.get("count", 0))
    best_date = best_day.get("date", "-")

    ly = sep_y + 24

    # Total contributions
    parts.append(
        f'<text '
        f'x="{PAD}" '
        f'y="{ly}" '
        f'font-size="13" '
        f'fill="{GREEN}">'
        f'<tspan font-weight="700">'
        f'{total:,}'
        f'</tspan>'
        f'<tspan fill="{MUTED}">'
        f' contributions in the last year'
        f'</tspan>'
        f'</text>'
    )

    # Date range
    parts.append(
        f'<text '
        f'x="{canvas_w - PAD}" '
        f'y="{ly}" '
        f'font-size="12" '
        f'fill="{MUTED}" '
        f'text-anchor="end">'
        f'{esc(date_range["start"])}'
        f' &#8594; '
        f'{esc(date_range["end"])}'
        f'</text>'
    )

    ly += 24

    # Streaks
    parts.append(
        f'<text '
        f'x="{PAD}" '
        f'y="{ly}" '
        f'font-size="13" '
        f'fill="{MUTED}">'
        f'current streak '
        f'<tspan fill="{ACCENT}" font-weight="700">'
        f'{cs} days'
        f'</tspan>'
        f'<tspan fill="{MUTED}">'
        f'   &#183;   longest '
        f'</tspan>'
        f'<tspan fill="{ACCENT}" font-weight="700">'
        f'{ls} days'
        f'</tspan>'
        f'</text>'
    )

    # Best day
    parts.append(
        f'<text '
        f'x="{canvas_w - PAD}" '
        f'y="{ly}" '
        f'font-size="12" '
        f'fill="{MUTED}" '
        f'text-anchor="end">'
        f'best day '
        f'<tspan fill="{GOLD}" font-weight="700">'
        f'{best_count}'
        f'</tspan>'
        f' on '
        f'{esc(best_date)}'
        f'</text>'
    )

    parts.append("</svg>")

    return "".join(parts)


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

if __name__ == "__main__":

    if not os.path.exists(IN_PATH):
        raise FileNotFoundError(
            f"Missing contribution data: {IN_PATH}"
        )

    with open(
        IN_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    svg = render(data)

    with open(
        OUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(svg)

    print("=" * 50)
    print(" CONTRIBUTION HEATMAP CREATED")
    print("=" * 50)
    print(f"Input  : {IN_PATH}")
    print(f"Output : {OUT_PATH}")
    print(f"Days   : {len(data.get('days', []))}")
    print(
        f"Total  : "
        f"{data.get('total_contributions', 0):,}"
    )
    print("=" * 50)