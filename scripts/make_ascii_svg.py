from pathlib import Path

from PIL import Image, ImageOps, ImageEnhance


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "source-prepped.png"
OUTPUT_FILE = BASE_DIR / "avi-ascii.svg"


# --------------------------------------------------
# ASCII configuration
# --------------------------------------------------

# Bright -> dark
# Very sparse first, very dense last.
RAMP = " .:-=+*#%@"

TARGET_WIDTH = 110

CHAR_WIDTH = 7
CHAR_HEIGHT = 14

FONT_SIZE = 10

# Strict monochrome
TEXT_COLOR = "#111111"

# Pure white background
BACKGROUND = "#ffffff"


# --------------------------------------------------
# Load image
# --------------------------------------------------

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input image not found: {INPUT_FILE}"
    )

image = Image.open(INPUT_FILE).convert("L")


# --------------------------------------------------
# Increase contrast
# --------------------------------------------------

# Make the difference between face highlights
# and shadows much stronger.

image = ImageOps.autocontrast(
    image,
    cutoff=2
)

contrast = ImageEnhance.Contrast(image)

image = contrast.enhance(2.2)


# --------------------------------------------------
# Resize while preserving aspect ratio
# --------------------------------------------------

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


# --------------------------------------------------
# Slight threshold enhancement
# --------------------------------------------------

# Keep white areas very clean.
pixels = list(image.getdata())

processed_pixels = []

for value in pixels:

    # Push very bright pixels toward pure white.
    if value > 225:
        value = 255

    # Push very dark pixels toward black.
    elif value < 35:
        value = 0

    processed_pixels.append(value)


# --------------------------------------------------
# Convert pixels to ASCII
# --------------------------------------------------

rows = []

for y in range(target_height):

    row = []

    for x in range(TARGET_WIDTH):

        brightness = processed_pixels[
            y * TARGET_WIDTH + x
        ]

        # White -> sparse
        # Black -> dense

        index = int(
            (255 - brightness)
            / 255
            * (len(RAMP) - 1)
        )

        row.append(RAMP[index])

    rows.append("".join(row))


# --------------------------------------------------
# SVG dimensions
# --------------------------------------------------

svg_width = TARGET_WIDTH * CHAR_WIDTH
svg_height = target_height * CHAR_HEIGHT


# --------------------------------------------------
# SVG
# --------------------------------------------------

svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{svg_width}" '
    f'height="{svg_height}" '
    f'viewBox="0 0 {svg_width} {svg_height}">'
)


# --------------------------------------------------
# Animation CSS
# --------------------------------------------------

svg.append("""
<style>

.ascii-row {

    opacity: 0;

    transform: translateX(-18px);

    animation:
        asciiReveal
        0.38s
        cubic-bezier(.2,.8,.2,1)
        forwards;
}


@keyframes asciiReveal {

    0% {

        opacity: 0;

        transform:
            translateX(-18px);

    }

    100% {

        opacity: 1;

        transform:
            translateX(0);

    }

}

</style>
""")


# --------------------------------------------------
# White background
# --------------------------------------------------

svg.append(
    f'<rect '
    f'width="100%" '
    f'height="100%" '
    f'fill="{BACKGROUND}"/>'
)


# --------------------------------------------------
# ASCII rows
# --------------------------------------------------

for row_index, row in enumerate(rows):

    y = (row_index + 1) * CHAR_HEIGHT

    delay = row_index * 0.025

    escaped = (
        row
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    svg.append(
        f'<text '
        f'class="ascii-row" '
        f'x="0" '
        f'y="{y}" '
        f'font-family="Consolas, '
        f'Monaco, monospace" '
        f'font-size="{FONT_SIZE}px" '
        f'font-weight="600" '
        f'fill="{TEXT_COLOR}" '
        f'style="'
        f'animation-delay:{delay:.3f}s;'
        f'white-space:pre;">'
        f'{escaped}'
        f'</text>'
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
    encoding="utf-8"
)


print()
print("======================================")
print(" MONOCHROME ASCII SVG CREATED")
print("======================================")
print()
print(f"Input : {INPUT_FILE}")
print(f"Output: {OUTPUT_FILE}")
print()
print(f"Grid  : {TARGET_WIDTH} x {target_height}")
print("Color : Monochrome")
print("Mode  : High Contrast")
print("Animation: Row-by-row")