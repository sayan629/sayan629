from pathlib import Path

from PIL import Image, ImageOps, ImageEnhance

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "source-prepped.png"
OUTPUT_FILE = BASE_DIR / "avi-ascii.svg"

RAMP = " .:-=+*#%@"

# KEEPING YOUR EXISTING SIZE
TARGET_WIDTH = 110

CHAR_WIDTH = 7
CHAR_HEIGHT = 14

FONT_SIZE = 10

# Dark terminal theme
TEXT_COLOR = "#e6edf3"
BACKGROUND = "#0d1117"


if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input image not found: {INPUT_FILE}"
    )


image = Image.open(INPUT_FILE).convert("L")

image = ImageOps.autocontrast(
    image,
    cutoff=2
)

contrast = ImageEnhance.Contrast(image)
image = contrast.enhance(2.2)


width, height = image.size

aspect_ratio = height / width

target_height = max(
    1,
    round(
        TARGET_WIDTH
        * aspect_ratio
        * CHAR_WIDTH
        / CHAR_HEIGHT
    )
)


image = image.resize(
    (TARGET_WIDTH, target_height),
    Image.Resampling.LANCZOS
)


pixels = list(image.getdata())

processed_pixels = []

for value in pixels:

    if value > 225:
        value = 255

    elif value < 35:
        value = 0

    processed_pixels.append(value)


rows = []

for y in range(target_height):

    row = []

    for x in range(TARGET_WIDTH):

        brightness = processed_pixels[
            y * TARGET_WIDTH + x
        ]

        index = int(
            (255 - brightness)
            / 255
            * (len(RAMP) - 1)
        )

        row.append(
            RAMP[index]
        )

    rows.append(
        "".join(row)
    )


svg_width = TARGET_WIDTH * CHAR_WIDTH
svg_height = target_height * CHAR_HEIGHT


svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{svg_width}"
    height="{svg_height}"
    viewBox="0 0 {svg_width} {svg_height}">
'''
)


# ---------------------------------------
# SLOW TERMINAL ANIMATION
# ---------------------------------------

svg.append(
    """
<style>

.ascii-row {

    opacity: 0;

    transform:
        translateX(-10px);

    animation:
        asciiReveal
        0.75s
        cubic-bezier(.2,.8,.2,1)
        forwards;
}


@keyframes asciiReveal {

    0% {

        opacity: 0;

        transform:
            translateX(-10px);
    }

    100% {

        opacity: 1;

        transform:
            translateX(0);
    }

}

</style>
"""
)


# ---------------------------------------
# DARK BACKGROUND
# ---------------------------------------

svg.append(
    f'''
<rect
    width="100%"
    height="100%"
    fill="{BACKGROUND}"
/>
'''
)


# ---------------------------------------
# ASCII ROWS
# ---------------------------------------

for row_index, row in enumerate(rows):

    y = (
        row_index + 1
    ) * CHAR_HEIGHT

    # SLOWER ROW-BY-ROW STAGGER
    delay = row_index * 0.055

    escaped = (
        row
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    svg.append(
        f'''
<text
    class="ascii-row"
    x="0"
    y="{y}"
    font-family="Consolas, Monaco, monospace"
    font-size="{FONT_SIZE}px"
    font-weight="600"
    fill="{TEXT_COLOR}"
    style="animation-delay:{delay:.3f}s;
           white-space:pre;">
    {escaped}</text>
'''
    )


svg.append("</svg>")


OUTPUT_FILE.write_text(
    "\n".join(svg),
    encoding="utf-8"
)


print()
print("======================================")
print(" DARK ASCII SVG CREATED")
print("======================================")
print()

print(f"Input : {INPUT_FILE}")
print(f"Output: {OUTPUT_FILE}")

print()

print(f"Grid  : {TARGET_WIDTH} x {target_height}")

print("Theme : Dark Terminal")

print("Text  : #e6edf3")

print("Background : #0d1117")

print("Animation : Slow row-by-row")

print()