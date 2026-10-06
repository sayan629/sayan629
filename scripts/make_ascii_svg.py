"""
Generate a monochrome terminal-style ASCII portrait for Sayan Pal.

- Uses data/source-prepped.png
- Dark GitHub-style terminal background
- High-detail ASCII portrait
- Single light-gray ASCII color
- Slow row-by-row terminal printing animation
- No JavaScript
- STATIC=1 creates a frozen preview
"""

from PIL import Image, ImageEnhance, ImageFilter
import html
import os
import sys


# ============================================================
# PATHS
# ============================================================

HERE = os.path.dirname(
    os.path.abspath(__file__)
)

BASE_DIR = os.path.dirname(HERE)

SRC = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(
        BASE_DIR,
        "data",
        "source-prepped.png"
    )
)

OUT = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.path.join(
        BASE_DIR,
        "avi-ascii.svg"
    )
)


# ============================================================
# ASCII QUALITY
# ============================================================

# More columns = more facial detail.
COLS = int(
    os.environ.get(
        "COLS",
        180
    )
)

ART_W_TARGET = 800

CELL_W = (
    ART_W_TARGET / COLS
)

CELL_H = (
    CELL_W * 15 / 8
)

ROWS = round(
    COLS * 8 / 15
)


# Dark → light density ramp
RAMP = (
    " .`:-=+*cs#%@"
)


# ============================================================
# IMAGE TUNING
# ============================================================

CONTRAST = 1.15

BRIGHTNESS = 1.02

# Slightly lower gamma keeps facial features visible.
GAMMA = 1.05

SHARPEN = True

WHITE_FLOOR = 0.82


# ============================================================
# TERMINAL FRAME
# ============================================================

PAD = 20

TITLEBAR_H = 30

STATUS_H = 30

ART_W = COLS * CELL_W

ART_H = ROWS * CELL_H

CANVAS_W = (
    ART_W + PAD * 2
)

CANVAS_H = (
    TITLEBAR_H
    + ART_H
    + STATUS_H
    + PAD
)


# ============================================================
# COLORS
# ============================================================

BG = "#0d1117"

BG2 = "#111722"

FRAME = "#30363d"

TITLE_TEXT = "#7d8590"

INK = "#c9d1d9"

CURSOR = "#c9d1d9"


# ============================================================
# ANIMATION
# ============================================================

# MUCH slower than the previous version.
#
# Entire portrait takes around 11 seconds.
#
# Change to 14.0 if you want it even slower.

TOTAL_REVEAL_TIME = 11.0

ROW_DUR = (
    TOTAL_REVEAL_TIME / ROWS
)

STAGGER = ROW_DUR


# ============================================================
# CHECK INPUT
# ============================================================

if not os.path.exists(SRC):

    raise FileNotFoundError(
        f"""
Source image not found:

{SRC}

Expected file:

data/source-prepped.png
"""
    )


# ============================================================
# LOAD IMAGE
# ============================================================

im = Image.open(
    SRC
).convert("L")


# Sharpen facial details
if SHARPEN:

    im = im.filter(
        ImageFilter.UnsharpMask(
            radius=2,
            percent=160,
            threshold=2
        )
    )


# Brightness
im = ImageEnhance.Brightness(
    im
).enhance(
    BRIGHTNESS
)


# Contrast
im = ImageEnhance.Contrast(
    im
).enhance(
    CONTRAST
)


# Resize to ASCII grid
im = im.resize(
    (
        COLS,
        ROWS
    ),
    Image.Resampling.LANCZOS
)


px = im.load()


# ============================================================
# STATIC MODE
# ============================================================

STATIC = (
    os.environ.get(
        "STATIC",
        ""
    ) == "1"
)


# ============================================================
# CONVERT PHOTO → ASCII
# ============================================================

rows_txt = []


for y in range(ROWS):

    chars = []

    for x in range(COLS):

        lum = (
            px[x, y] / 255.0
        )


        # Gamma adjustment
        lum = pow(
            lum,
            GAMMA
        )


        # Remove very bright background
        if lum >= WHITE_FLOOR:

            chars.append(" ")

            continue


        index = int(
            (
                1.0 - lum
            )
            * (
                len(RAMP) - 1
            )
            + 0.5
        )


        index = max(
            0,
            min(
                len(RAMP) - 1,
                index
            )
        )


        chars.append(
            RAMP[index]
        )


    rows_txt.append(
        "".join(chars)
    )


# ============================================================
# ART POSITION
# ============================================================

art_top = (
    TITLEBAR_H
    + PAD * 0.35
)


# ============================================================
# SVG
# ============================================================

parts = []


parts.append(
    f'''
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{CANVAS_W}"
    height="{CANVAS_H}"
    viewBox="0 0 {CANVAS_W} {CANVAS_H}"
    font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
'''
)


# ============================================================
# BACKGROUND GRADIENT
# ============================================================

parts.append(
    f'''
<defs>

    <linearGradient
        id="bg"
        x1="0"
        y1="0"
        x2="0"
        y2="1">

        <stop
            offset="0"
            stop-color="{BG2}"
        />

        <stop
            offset="1"
            stop-color="{BG}"
        />

    </linearGradient>

</defs>
'''
)


# ============================================================
# TERMINAL WINDOW
# ============================================================

parts.append(
    f'''
<rect
    width="{CANVAS_W}"
    height="{CANVAS_H}"
    rx="12"
    fill="url(#bg)"
/>

<rect
    x="0.5"
    y="0.5"
    width="{CANVAS_W - 1}"
    height="{CANVAS_H - 1}"
    rx="12"
    fill="none"
    stroke="{FRAME}"
    stroke-width="1"
/>
'''
)


# ============================================================
# TITLE BAR
# ============================================================

parts.append(
    f'''
<line
    x1="0"
    y1="{TITLEBAR_H}"
    x2="{CANVAS_W}"
    y2="{TITLEBAR_H}"
    stroke="{FRAME}"
/>
'''
)


# Terminal buttons
for i, dot_color in enumerate(
    [
        "#ff5f56",
        "#ffbd2e",
        "#27c93f"
    ]
):

    parts.append(
        f'''
<circle
    cx="{PAD + i * 16}"
    cy="{TITLEBAR_H / 2}"
    r="5"
    fill="{dot_color}"
/>
'''
    )


# Terminal title
parts.append(
    f'''
<text
    x="{CANVAS_W / 2}"
    y="{TITLEBAR_H / 2 + 4}"
    fill="{TITLE_TEXT}"
    font-size="12"
    text-anchor="middle">

    sayan@github:~$ ./portrait.sh

</text>
'''
)


# ============================================================
# ASCII PORTRAIT
# ============================================================

font_size = (
    CELL_H * 0.86
)


for row_index, line in enumerate(
    rows_txt
):

    y = (
        art_top
        + row_index * CELL_H
        + CELL_H * 0.74
    )

    row_y = (
        art_top
        + row_index * CELL_H
    )

    delay = (
        row_index
        * STAGGER
    )


    safe = html.escape(
        line
    )


    text = (
        f'<text '
        f'xml:space="preserve" '
        f'x="{PAD}" '
        f'y="{y:.1f}" '
        f'fill="{INK}" '
        f'font-size="{font_size:.1f}" '
        f'textLength="{ART_W}" '
        f'lengthAdjust="spacing">'
        f'{safe}'
        f'</text>'
    )


    # --------------------------------------------------------
    # STATIC
    # --------------------------------------------------------

    if STATIC:

        parts.append(
            text
        )

        continue


    # --------------------------------------------------------
    # ANIMATED ROW
    # --------------------------------------------------------

    parts.append(
        f'''
<clipPath id="row{row_index}">

    <rect
        x="{PAD}"
        y="{row_y:.1f}"
        height="{CELL_H}"
        width="0">

        <animate
            attributeName="width"
            from="0"
            to="{ART_W}"
            begin="{delay:.3f}s"
            dur="{ROW_DUR:.3f}s"
            fill="freeze"
        />

    </rect>

</clipPath>
'''
    )


    parts.append(
        f'''
<g clip-path="url(#row{row_index})">

    {text}

</g>
'''
    )


    # Moving terminal cursor
    parts.append(
        f'''
<rect
    y="{row_y + 1:.1f}"
    width="{CELL_W}"
    height="{CELL_H - 2}"
    fill="{CURSOR}"
    opacity="0">

    <animate
        attributeName="x"
        from="{PAD}"
        to="{PAD + ART_W}"
        begin="{delay:.3f}s"
        dur="{ROW_DUR:.3f}s"
        fill="freeze"
    />

    <set
        attributeName="opacity"
        to="0.85"
        begin="{delay:.3f}s"
    />

    <set
        attributeName="opacity"
        to="0"
        begin="{delay + ROW_DUR:.3f}s"
    />

</rect>
'''
    )


# ============================================================
# STATUS BAR
# ============================================================

status_line_y = (
    TITLEBAR_H
    + ART_H
    + PAD * 0.35
)

status_y = (
    status_line_y
    + 19
)


parts.append(
    f'''
<line
    x1="0"
    y1="{status_line_y:.1f}"
    x2="{CANVAS_W}"
    y2="{status_line_y:.1f}"
    stroke="{FRAME}"
/>

<text
    x="{PAD}"
    y="{status_y:.1f}"
    fill="{TITLE_TEXT}"
    font-size="13">

    sayan@github:~$ whoami

    <tspan fill="{INK}">
        Sayan Pal
    </tspan>

</text>
'''
)


# ============================================================
# BLINKING CURSOR
# ============================================================

status_text = (
    "sayan@github:~$ whoami Sayan Pal "
)

status_chars = len(
    status_text
)


parts.append(
    f'''
<rect
    x="{PAD + status_chars * 13 * 0.6:.1f}"
    y="{status_y - 12:.1f}"
    width="8"
    height="14"
    fill="{INK}">

    <animate
        attributeName="opacity"
        values="1;1;0;0"
        keyTimes="0;0.5;0.51;1"
        dur="1s"
        repeatCount="indefinite"
    />

</rect>
'''
)


# ============================================================
# CLOSE SVG
# ============================================================

parts.append(
    "</svg>"
)


svg = "".join(
    parts
)


# ============================================================
# WRITE
# ============================================================

with open(
    OUT,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        svg
    )


print()
print(
    "======================================"
)
print(
    " ASCII PORTRAIT CREATED"
)
print(
    "======================================"
)
print()
print(
    f"Source    : {SRC}"
)
print(
    f"Output    : {OUT}"
)
print(
    f"Grid      : {COLS} x {ROWS}"
)
print(
    f"Canvas    : {CANVAS_W} x {CANVAS_H}"
)
print(
    f"Animation : {TOTAL_REVEAL_TIME}s"
)
print(
    f"Static    : {STATIC}"
)
print()