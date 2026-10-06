#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public contributions
endpoint and write data/contributions.json.

No token.
No authentication.
No GraphQL.
"""

from datetime import datetime, timezone
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup


# ============================================================
# YOUR GITHUB PROFILE
# ============================================================

USERNAME = os.environ.get(
    "GH_PROFILE_USER",
    "sayan629"
)

URL = (
    f"https://github.com/users/"
    f"{USERNAME}/contributions"
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "contributions.json"
)


# ============================================================
# FETCH CONTRIBUTIONS
# ============================================================

def fetch_days():

    print()
    print("======================================")
    print(" FETCHING GITHUB CONTRIBUTIONS")
    print("======================================")
    print()

    print(
        f"GitHub user : {USERNAME}"
    )

    print(
        f"Source      : {URL}"
    )

    print()


    response = requests.get(
        URL,
        headers={
            "User-Agent":
                "sayan629-profile-readme-bot/1.0"
        },
        timeout=30
    )


    response.raise_for_status()


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    # --------------------------------------------------------
    # Contribution cells
    # --------------------------------------------------------

    cells = soup.select(
        "td.ContributionCalendar-day"
    )


    if not cells:

        print(
            "No contribution cells found.",
            file=sys.stderr
        )

        print(
            "GitHub markup may have changed.",
            file=sys.stderr
        )

        sys.exit(1)


    print(
        f"Found {len(cells)} contribution cells."
    )


    # --------------------------------------------------------
    # First map tooltip IDs → contribution counts
    # --------------------------------------------------------

    tooltip_counts = {}


    for tooltip in soup.find_all(
        "tool-tip"
    ):

        target_id = tooltip.get(
            "for"
        )


        if not target_id:
            continue


        text = tooltip.get_text(
            " ",
            strip=True
        )


        # Example:
        #
        # 4 contributions on October 1, 2026
        #
        match = re.search(
            r"([\d,]+)\s+contributions?",
            text,
            re.IGNORECASE
        )


        if match:

            count = int(
                match.group(1)
                .replace(",", "")
            )


        elif re.search(
            r"no contributions",
            text,
            re.IGNORECASE
        ):

            count = 0


        else:

            continue


        tooltip_counts[
            target_id
        ] = count


    print(
        f"Found {len(tooltip_counts)} contribution tooltips."
    )


    # --------------------------------------------------------
    # Combine cells + tooltips
    # --------------------------------------------------------

    days = []


    for td in cells:

        date = td.get(
            "data-date"
        )


        if not date:
            continue


        td_id = td.get(
            "id"
        )


        count = 0


        if td_id:

            count = tooltip_counts.get(
                td_id,
                0
            )


        try:

            level = int(
                td.get(
                    "data-level",
                    0
                )
            )

        except ValueError:

            level = 0


        days.append(
            {
                "date": date,
                "count": count,
                "level": level
            }
        )


    days.sort(
        key=lambda d: d["date"]
    )


    return days


# ============================================================
# CURRENT STREAK
# ============================================================

def compute_current_streak(days):

    if not days:
        return 0, None, None


    idx = len(days) - 1


    # Today may not be complete yet.
    if days[idx]["count"] == 0:

        idx -= 1


    streak = 0

    end_idx = idx


    while (
        idx >= 0
        and days[idx]["count"] > 0
    ):

        streak += 1

        idx -= 1


    start_idx = idx + 1


    if streak == 0:

        return 0, None, None


    return (
        streak,
        days[start_idx]["date"],
        days[end_idx]["date"]
    )


# ============================================================
# LONGEST STREAK
# ============================================================

def compute_longest_streak(days):

    longest = 0

    run = 0

    longest_start = None

    longest_end = None

    run_start_idx = None


    for i, day in enumerate(days):

        if day["count"] > 0:

            if run == 0:

                run_start_idx = i


            run += 1


            if run > longest:

                longest = run

                longest_start = (
                    days[run_start_idx]["date"]
                )

                longest_end = (
                    days[i]["date"]
                )


        else:

            run = 0


    return (
        longest,
        longest_start,
        longest_end
    )


# ============================================================
# BUILD JSON DATA
# ============================================================

def build_data(days):

    total = sum(
        day["count"]
        for day in days
    )


    active_days = sum(
        1
        for day in days
        if day["count"] > 0
    )


    best = max(
        days,
        key=lambda day: day["count"]
    )


    current_len, current_start, current_end = (
        compute_current_streak(days)
    )


    longest_len, longest_start, longest_end = (
        compute_longest_streak(days)
    )


    # --------------------------------------------------------
    # Monthly totals
    # --------------------------------------------------------

    monthly = {}


    for day in days:

        month = day["date"][:7]

        monthly[month] = (
            monthly.get(month, 0)
            + day["count"]
        )


    monthly_list = [

        {
            "month": month,
            "total": total
        }

        for month, total
        in sorted(monthly.items())

    ]


    # --------------------------------------------------------
    # Final JSON
    # --------------------------------------------------------

    return {

        "username":
            USERNAME,

        "source":
            URL,

        "generated_at":
            datetime.now(
                timezone.utc
            ).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),

        "range": {

            "start":
                days[0]["date"],

            "end":
                days[-1]["date"]

        },

        "total_contributions":
            total,

        "active_days":
            active_days,

        "avg_per_active_day":
            round(
                total / active_days,
                1
            )
            if active_days
            else 0,

        "current_streak": {

            "length":
                current_len,

            "start":
                current_start,

            "end":
                current_end

        },

        "longest_streak": {

            "length":
                longest_len,

            "start":
                longest_start,

            "end":
                longest_end

        },

        "best_day": {

            "date":
                best["date"],

            "count":
                best["count"]

        },

        "monthly":
            monthly_list,

        "days":
            days

    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    days = fetch_days()


    data = build_data(
        days
    )


    os.makedirs(
        os.path.dirname(
            OUT_PATH
        ),
        exist_ok=True
    )


    with open(
        OUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


    print()
    print("======================================")
    print(" CONTRIBUTIONS FETCHED")
    print("======================================")
    print()

    print(
        f"User             : {data['username']}"
    )

    print(
        f"Days             : {len(days)}"
    )

    print(
        f"Total            : "
        f"{data['total_contributions']:,}"
    )

    print(
        f"Active days      : "
        f"{data['active_days']}"
    )

    print(
        f"Average/active   : "
        f"{data['avg_per_active_day']}"
    )

    print(
        f"Current streak   : "
        f"{data['current_streak']['length']}"
    )

    print(
        f"Longest streak   : "
        f"{data['longest_streak']['length']}"
    )

    print(
        f"Best day         : "
        f"{data['best_day']['count']}"
    )

    print()

    print(
        f"Output: {OUT_PATH}"
    )

    print()