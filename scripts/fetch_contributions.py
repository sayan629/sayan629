from pathlib import Path
from datetime import datetime, timezone
import json
import re

import requests
from bs4 import BeautifulSoup


# --------------------------------------------------
# Configuration
# --------------------------------------------------

USERNAME = "sayan629"

URL = f"https://github.com/users/{USERNAME}/contributions"

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "contributions.json"


# --------------------------------------------------
# Fetch GitHub page
# --------------------------------------------------

print()
print("======================================")
print(" FETCHING GITHUB CONTRIBUTIONS")
print("======================================")
print()

headers = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/154.0 Safari/537.36"
    )
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30,
)

response.raise_for_status()

html = response.text

soup = BeautifulSoup(
    html,
    "html.parser",
)


# --------------------------------------------------
# Parse contribution cells
# --------------------------------------------------

cells = soup.select(
    "td.ContributionCalendar-day"
)

if not cells:

    raise RuntimeError(
        "GitHub contribution cells were not found."
    )


print(
    f"Found {len(cells)} contribution cells."
)


# --------------------------------------------------
# Build tooltip lookup
# --------------------------------------------------

tooltip_counts = {}


for tooltip in soup.find_all("tool-tip"):

    target_id = tooltip.get("for")

    if not target_id:
        continue

    text = tooltip.get_text(
        " ",
        strip=True,
    )

    match = re.search(
        r"([\d,]+)\s+contributions?",
        text,
        re.IGNORECASE,
    )

    if match:

        count = int(
            match.group(1)
            .replace(",", "")
        )

    elif re.search(
        r"no contributions",
        text,
        re.IGNORECASE,
    ):

        count = 0

    else:

        continue

    tooltip_counts[target_id] = count


print(
    f"Found {len(tooltip_counts)} contribution tooltips."
)


# --------------------------------------------------
# Extract days
# --------------------------------------------------

contributions = []


for cell in cells:

    date = cell.get("data-date")

    level_raw = cell.get(
        "data-level",
        "0",
    )

    cell_id = cell.get("id")


    if not date:
        continue


    try:

        level = int(level_raw)

    except ValueError:

        level = 0


    count = 0


    if cell_id:

        count = tooltip_counts.get(
            cell_id,
            0,
        )


    contributions.append(
        {
            "date": date,
            "count": count,
            "level": level,
        }
    )


# --------------------------------------------------
# Sort chronologically
# --------------------------------------------------

contributions.sort(
    key=lambda item: item["date"]
)


# --------------------------------------------------
# Statistics
# --------------------------------------------------

total = sum(
    item["count"]
    for item in contributions
)

active = sum(
    1
    for item in contributions
    if item["count"] > 0
)

peak = max(
    (
        item["count"]
        for item in contributions
    ),
    default=0,
)


# --------------------------------------------------
# Output
# --------------------------------------------------

output = {
    "username": USERNAME,
    "source": URL,
    "fetched_at": (
        datetime.now(timezone.utc)
        .isoformat()
    ),
    "total_contributions": total,
    "active_days": active,
    "peak_day": peak,
    "days": contributions,
}


OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)


OUTPUT_FILE.write_text(
    json.dumps(
        output,
        indent=2,
    ),
    encoding="utf-8",
)


# --------------------------------------------------
# Print result
# --------------------------------------------------

print()
print("======================================")
print(" CONTRIBUTIONS FETCHED")
print("======================================")
print()

print(
    f"Days parsed          : {len(contributions)}"
)

print(
    f"Total contributions  : {total:,}"
)

print(
    f"Active days          : {active}"
)

print(
    f"Peak/day             : {peak}"
)

print()
print(
    f"Output: {OUTPUT_FILE}"
)
print()