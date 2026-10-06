from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(HERE)

# Your processed portrait
SRC = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(BASE_DIR, "data", "source-prepped.png")
)

OUT = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.path.join(BASE_DIR, "avi-ascii.svg")
)

# ============================================================
# ASCII DETAIL
# ============================================================

COLS = int(os.environ.get("COLS", 180))

ART_W_TARGET = 800

CELL_W = ART_W_TARGET / COLS
CELL_H = CELL_W * 15 / 8

ROWS = round(
    COLS * 8 / 15
)

RAMP = " .`:-=+*cs#%@"

# ============================================================
# IMAGE TUNING
# ============================================================

CONTRAST = 1.05
BRIGHTNESS = 1.0

GAMMA = 1.18

SHARPEN = False

WHITE_FLOOR = 0.80

# ============================================================
# TERMINAL DESIGN
# ============================================================

PAD = 20

TITLEBAR_H = 30
STATUS_H = 30

ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H

CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0d1117"
BG2 = "#111722"

FRAME = "#30363d"

TITLE_TEXT = "#7d8590"

INK = "#c9d1d9"

CURSOR = "#c9d1d9"

# ============================================================
# SLOW ANIMATION
# ============================================================

ROW_DUR = 5.8 / ROWS

STAGGER = ROW_DUR

# ============================================================
# LOAD YOUR PHOTO
# ============================================================

print()
print("======================================")
print(" CREATING ASCII PORTRAIT")
print("======================================")
print()

print("Source :", SRC)
print("Output :", OUT)
print()


if not os.path.exists(SRC):
    raise FileNotFoundError(
        f"Photo not found: {SRC}"
    )


im = Image.open(SRC).convert("L")


# ============================================================
# IMAGE PROCESSING
# ============================================================

if SHARPEN:

    im = im.filter(
        ImageFilter.UnsharpMask(
            radius=2,
            percent=140,
            threshold=2
        )
    )


im = ImageEnhance.Brightness(
    im
).enhance(BRIGHTNESS)


im = ImageEnhance.Contrast(
    im
).enhance(CONTRAST)


# ============================================================
# RESIZE TO ASCII GRID
# ============================================================

im = im.resize(
    (
        COLS,
        ROWS
    ),
    Image.Resampling.LANCZOS
)


px = im.load()


# ============================================================
# STATIC PREVIEW OPTION
# ============================================================

STATIC = bool(
    os.environ.get("STATIC")
)


# ============================================================
# CONVERT PHOTO → ASCII
# ============================================================

rows_txt = []


for y in range(ROWS):

    chars = []

    for x in range(COLS):

        lum = px[x, y] / 255.0

        lum = pow(
            lum,
            GAMMA
        )

        # Remove very bright background
        if lum >= WHITE_FLOOR:

            chars.append(" ")

            continue


        idx = int(
            (1.0 - lum)
            * (len(RAMP) - 1)
            + 0.5
        )


        idx = max(
            0,
            min(
                len(RAMP) - 1,
                idx
            )
        )


        chars.append(
            RAMP[idx]
        )


    rows_txt.append(
        "".join(chars)
    )


# ============================================================
# SVG
# ============================================================

art_top = (
    TITLEBAR_H
    + PAD * 0.35
)


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
# TERMINAL TITLE BAR
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


for i, dotcol in enumerate(
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
    fill="{dotcol}"
/>
'''
    )


parts.append(
    f'''
<text
    x="{CANVAS_W / 2}"
    y="{TITLEBAR_H / 2 + 4}"
    fill="{TITLE_TEXT}"
    font-size="12"
    text-anchor="middle">

    sayan@github: ~$ ./portrait.sh

</text>
'''
)


# ============================================================
# ASCII PORTRAIT
# ============================================================

font_size = (
    CELL_H * 0.86
)


for ry, line in enumerate(
    rows_txt
):

    y = (
        art_top
        + ry * CELL_H
        + CELL_H * 0.74
    )

    row_y = (
        art_top
        + ry * CELL_H
    )


    delay = (
        ry * STAGGER
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


    if STATIC:

        parts.append(
            text
        )

        continue


    # ---------------------------------------
    # ROW CLIP / TYPING EFFECT
    # ---------------------------------------

    parts.append(
        f'''
<clipPath id="r{ry}">

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
            dur="{ROW_DUR:.2f}s"
            fill="freeze"
        />

    </rect>

</clipPath>
'''
    )


    parts.append(
        f'''
<g clip-path="url(#r{ry})">

    {text}

</g>
'''
    )


    # Cursor follows the typing edge
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
        dur="{ROW_DUR:.2f}s"
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
# TERMINAL STATUS BAR
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

status_chars = len(
    "sayan@github:~$ whoami Sayan Pal "
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


parts.append(
    "</svg>"
)


# ============================================================
# SAVE
# ============================================================

svg = "".join(
    parts
)


with open(
    OUT,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        svg
    )


print(
    "Created:",
    OUT
)

print(
    "Size:",
    CANVAS_W,
    "x",
    CANVAS_H
)

print(
    "ASCII grid:",
    COLS,
    "x",
    ROWS
)

print(
    "Animation:",
    "~6 seconds"
)

print()