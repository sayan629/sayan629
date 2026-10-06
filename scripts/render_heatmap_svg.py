from pathlib import Path
from datetime import datetime
import json
import math


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "contributions.json"
OUTPUT_FILE = BASE_DIR / "contrib-heatmap.svg"


# --------------------------------------------------
# Configuration
# --------------------------------------------------

WIDTH = 860
HEIGHT = 250

CELL = 11
GAP = 3

LEFT = 48
TOP = 64

# GitHub-inspired green scale
LEVEL_COLORS = [
    "#ebedf0",
    "#9be9a8",
    "#40c463",
    "#30a14e",
    "#216e39",
]

TEXT = "#111111"
MUTED = "#666666"
BORDER = "#111111"


# --------------------------------------------------
# Load data
# --------------------------------------------------

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Missing contribution data: {INPUT_FILE}"
    )


data = json.loads(
    INPUT_FILE.read_text(
        encoding="utf-8"
    )
)


days = data["days"]


# --------------------------------------------------
# Organize by date
# --------------------------------------------------

by_date = {
    item["date"]: item
    for item in days
}


# --------------------------------------------------
# Find latest date
# --------------------------------------------------

latest_date = max(
    datetime.strptime(
        item["date"],
        "%Y-%m-%d"
    )
    for item in days
)


# --------------------------------------------------
# Find Sunday starting point
# --------------------------------------------------

# GitHub contribution calendars are arranged
# Sunday -> Saturday.

latest_date_str = latest_date.strftime(
    "%Y-%m-%d"
)


# We render the most recent 53 weeks.
# Find the Sunday that starts the final week.

latest_weekday = latest_date.weekday()

# Python:
# Monday = 0
# Sunday = 6

days_from_sunday = (
    latest_weekday + 1
) % 7


start_date = (
    latest_date
    .toordinal()
    - (52 * 7)
    - days_from_sunday
)


from datetime import date, timedelta

start_date = date.fromordinal(
    start_date
)


# --------------------------------------------------
# Generate calendar cells
# --------------------------------------------------

weeks = []

current = start_date

for week_index in range(53):

    week = []

    for day_index in range(7):

        current_date = (
            start_date
            + timedelta(
                days=week_index * 7
                + day_index
            )
        )

        date_string = current_date.isoformat()

        item = by_date.get(
            date_string,
            {
                "date": date_string,
                "count": 0,
                "level": 0,
            }
        )

        week.append(item)

    weeks.append(week)


# --------------------------------------------------
# Calculate statistics
# --------------------------------------------------

visible_days = [
    cell
    for week in weeks
    for cell in week
]


total = sum(
    cell["count"]
    for cell in visible_days
)


active_days = sum(
    1
    for cell in visible_days
    if cell["count"] > 0
)


max_count = max(
    (
        cell["count"]
        for cell in visible_days
    ),
    default=0,
)


# --------------------------------------------------
# SVG
# --------------------------------------------------

svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">
'''
)


# --------------------------------------------------
# Animation
# --------------------------------------------------

svg.append(
    """
<style>

.heat-cell {
    opacity: 0;
    transform-box: fill-box;
    transform-origin: center;
    animation:
        cellReveal
        0.45s
        ease-out
        forwards;
}

@keyframes cellReveal {

    0% {
        opacity: 0;
        transform: scale(0.65);
    }

    100% {
        opacity: 1;
        transform: scale(1);
    }

}

.title {
    opacity: 0;
    animation:
        fadeIn
        0.5s
        ease-out
        0.1s
        forwards;
}

.subtitle {
    opacity: 0;
    animation:
        fadeIn
        0.5s
        ease-out
        0.25s
        forwards;
}

.footer {
    opacity: 0;
    animation:
        fadeIn
        0.5s
        ease-out
        1.1s
        forwards;
}

@keyframes fadeIn {

    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }

}

</style>
"""
)


# --------------------------------------------------
# Background
# --------------------------------------------------

svg.append(
    f'''
<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="12"
    fill="#ffffff"
    stroke="{BORDER}"
    stroke-width="2"
/>
'''
)


# --------------------------------------------------
# Header
# --------------------------------------------------

svg.append(
    f'''
<text
    class="title"
    x="28"
    y="29"
    font-family="Consolas, Monaco, monospace"
    font-size="15"
    font-weight="700"
    fill="{TEXT}">
    $ ./contributions.sh
</text>

<text
    class="subtitle"
    x="28"
    y="48"
    font-family="Consolas, Monaco, monospace"
    font-size="11"
    fill="{MUTED}">
    github.com/{data["username"]} · last 12 months
</text>
'''
)


# --------------------------------------------------
# Month labels
# --------------------------------------------------

month_positions = {}

for week_index in range(53):

    date_for_week = (
        start_date
        + timedelta(
            days=week_index * 7
        )
    )

    month_key = (
        date_for_week.year,
        date_for_week.month
    )

    if month_key not in month_positions:

        month_positions[month_key] = (
            week_index
        )


for (
    year,
    month
), week_index in month_positions.items():

    if week_index == 0:
        continue

    month_name = datetime(
        year,
        month,
        1
    ).strftime("%b")

    x = (
        LEFT
        + week_index
        * (CELL + GAP)
    )

    svg.append(
        f'''
<text
    x="{x}"
    y="56"
    font-family="Consolas, Monaco, monospace"
    font-size="10"
    fill="{MUTED}">
    {month_name}
</text>
'''
    )


# --------------------------------------------------
# Weekday labels
# --------------------------------------------------

weekday_labels = {
    1: "Mon",
    3: "Wed",
    5: "Fri",
}


for day_index, label in weekday_labels.items():

    y = (
        TOP
        + day_index
        * (CELL + GAP)
        + 9
    )

    svg.append(
        f'''
<text
    x="10"
    y="{y}"
    font-family="Consolas, Monaco, monospace"
    font-size="9"
    fill="{MUTED}">
    {label}
</text>
'''
    )


# --------------------------------------------------
# Heatmap cells
# --------------------------------------------------

for week_index, week in enumerate(weeks):

    for day_index, item in enumerate(week):

        x = (
            LEFT
            + week_index
            * (CELL + GAP)
        )

        y = (
            TOP
            + day_index
            * (CELL + GAP)
        )

        level = int(
            item.get(
                "level",
                0
            )
        )

        level = max(
            0,
            min(
                4,
                level
            )
        )

        fill = LEVEL_COLORS[level]

        delay = (
            0.35
            + (
                week_index * 7
                + day_index
            )
            * 0.008
        )

        tooltip = (
            f'{item["count"]} contributions '
            f'on {item["date"]}'
        )

        svg.append(
            f'''
<rect
    class="heat-cell"
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="2"
    fill="{fill}"
    style="animation-delay:{delay:.3f}s;">
    <title>{tooltip}</title>
</rect>
'''
        )


# --------------------------------------------------
# Legend
# --------------------------------------------------

legend_y = 172

svg.append(
    f'''
<text
    x="{LEFT}"
    y="{legend_y + 22}"
    font-family="Consolas, Monaco, monospace"
    font-size="10"
    fill="{MUTED}">
    Less
</text>
'''
)


for index, color in enumerate(
    LEVEL_COLORS
):

    x = (
        LEFT
        + 28
        + index * 18
    )

    svg.append(
        f'''
<rect
    x="{x}"
    y="{legend_y + 12}"
    width="12"
    height="12"
    rx="2"
    fill="{color}"
/>
'''
    )


svg.append(
    f'''
<text
    x="{LEFT + 28 + 5 * 18 + 4}"
    y="{legend_y + 22}"
    font-family="Consolas, Monaco, monospace"
    font-size="10"
    fill="{MUTED}">
    More
</text>
'''
)


# --------------------------------------------------
# Stats
# --------------------------------------------------

stats_text = (
    f"12-month window  ·  "
    f"{total:,} contributions  ·  "
    f"{active_days} active days  ·  "
    f"peak {max_count}"
)


svg.append(
    f'''
<text
    class="footer"
    x="{LEFT}"
    y="222"
    font-family="Consolas, Monaco, monospace"
    font-size="11"
    fill="{TEXT}">
    {stats_text}
</text>
'''
)


# --------------------------------------------------
# Close SVG
# --------------------------------------------------

svg.append("</svg>")


# --------------------------------------------------
# Save
# --------------------------------------------------

OUTPUT_FILE.write_text(
    "\n".join(svg),
    encoding="utf-8",
)


print()
print("======================================")
print(" CONTRIBUTION HEATMAP CREATED")
print("======================================")
print()

print(f"User          : {data['username']}")
print(f"Total         : {total:,}")
print(f"Active days   : {active_days}")
print(f"Peak/day      : {max_count}")
print(f"Output        : {OUTPUT_FILE}")

print()