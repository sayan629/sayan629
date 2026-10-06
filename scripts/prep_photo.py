"""
Prepare Sayan Pal's portrait for high-quality ASCII conversion.

Pipeline:
    1. Load the source photo.
    2. Remove the background using rembg.
    3. Smooth photographic texture while preserving facial edges.
    4. Improve contrast.
    5. Strengthen fine facial details.
    6. Composite the subject onto white.
    7. Crop tightly around the subject.
    8. Save grayscale source-prepped.png.

Input:
    assets/source-photo.JPG

Output:
    data/source-prepped.png
"""

import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


# ============================================================
# PROJECT PATHS
# ============================================================

HERE = os.path.dirname(
    os.path.abspath(__file__)
)

BASE_DIR = os.path.dirname(HERE)


DEFAULT_INPUT = os.path.join(
    BASE_DIR,
    "assets",
    "source-photo.JPG"
)


DEFAULT_OUTPUT = os.path.join(
    BASE_DIR,
    "data",
    "source-prepped.png"
)


INPUT = (
    sys.argv[1]
    if len(sys.argv) > 1
    else DEFAULT_INPUT
)


OUTPUT = (
    sys.argv[2]
    if len(sys.argv) > 2
    else DEFAULT_OUTPUT
)


# ============================================================
# SETTINGS
# ============================================================

# Strength of facial line enhancement.
LINE_WEIGHT = 0.55

# Background feathering.
FEATHER = 0.8

# Extra contrast.
CONTRAST = 1.15

# Slight brightness adjustment.
BRIGHTNESS = 1.02


# ============================================================
# CHECK INPUT
# ============================================================

if not os.path.exists(INPUT):

    raise FileNotFoundError(
        f"""
Source photo not found:

{INPUT}

Expected:

assets/source-photo.JPG
"""
    )


print()
print(
    "======================================"
)
print(
    " PREPARING PORTRAIT"
)
print(
    "======================================"
)
print()

print(
    f"Input : {INPUT}"
)

print(
    f"Output: {OUTPUT}"
)

print()


# ============================================================
# 1. LOAD PHOTO
# ============================================================

image = Image.open(
    INPUT
).convert(
    "RGBA"
)


# ============================================================
# 2. REMOVE BACKGROUND
# ============================================================

print(
    "Removing background..."
)

cutout = remove(
    image
)


# RGB image
rgb = np.array(
    cutout.convert(
        "RGB"
    )
)


# Alpha mask
alpha = np.array(
    cutout.getchannel(
        "A"
    )
)


# ============================================================
# 3. GRAYSCALE
# ============================================================

gray = cv2.cvtColor(
    rgb,
    cv2.COLOR_RGB2GRAY
)


# ============================================================
# 4. REMOVE PHOTO NOISE
# ============================================================

print(
    "Cleaning photographic texture..."
)


smooth = gray.copy()


# Bilateral filtering keeps facial edges.
for _ in range(2):

    smooth = cv2.bilateralFilter(
        smooth,
        9,
        35,
        9
    )


# ============================================================
# 5. SUBJECT MASK
# ============================================================

subject_pixels = (
    alpha > 128
)


if not np.any(
    subject_pixels
):

    raise RuntimeError(
        "Background removal produced an empty subject mask."
    )


# ============================================================
# 6. CONTRAST / TONE
# ============================================================

print(
    "Improving facial contrast..."
)


values = smooth[
    subject_pixels
]


low, high = np.percentile(
    values,
    [
        2,
        96
    ]
)


if high <= low:

    high = low + 1


tone = (
    smooth.astype(
        np.float32
    )
    - low
) / (
    high - low
)


tone = np.clip(
    tone,
    0,
    1
)


# Contrast
tone = (
    tone - 0.5
) * CONTRAST + 0.5


# Brightness
tone = (
    tone * BRIGHTNESS
)


tone = np.clip(
    tone,
    0,
    1
)


# ============================================================
# 7. FACIAL DETAIL EXTRACTION
# ============================================================

print(
    "Enhancing eyes, hair and facial lines..."
)


fine = cv2.GaussianBlur(
    smooth,
    (0, 0),
    1.3
).astype(
    np.float32
)


coarse = cv2.GaussianBlur(
    smooth,
    (0, 0),
    5.0
).astype(
    np.float32
)


# Dark line structure
detail = (
    coarse - fine
)


detail = np.clip(
    detail / 35.0,
    0,
    1
)


# Apply only to subject
processed = (
    tone
    - LINE_WEIGHT * detail
)


processed = np.clip(
    processed,
    0,
    1
)


# ============================================================
# 8. CONVERT TO 8-BIT
# ============================================================

processed = (
    processed * 255
).astype(
    np.uint8
)


# ============================================================
# 9. SOFT SUBJECT MASK
# ============================================================

mask = (
    alpha.astype(
        np.float32
    )
    / 255.0
)


mask = cv2.GaussianBlur(
    mask,
    (0, 0),
    FEATHER
)


# ============================================================
# 10. COMPOSITE ON WHITE
# ============================================================

white = np.full_like(
    processed,
    255,
    dtype=np.float32
)


processed_float = (
    processed.astype(
        np.float32
    )
)


composited = (
    processed_float * mask
    + white * (
        1.0 - mask
    )
)


composited = np.clip(
    composited,
    0,
    255
).astype(
    np.uint8
)


# ============================================================
# 11. FIND SUBJECT BOUNDING BOX
# ============================================================

ys, xs = np.where(
    alpha > 20
)


if len(xs) == 0:

    raise RuntimeError(
        "Could not determine subject boundaries."
    )


min_x = xs.min()
max_x = xs.max()

min_y = ys.min()
max_y = ys.max()


subject_width = (
    max_x - min_x
)

subject_height = (
    max_y - min_y
)


# ============================================================
# 12. SQUARE CROP
# ============================================================

padding = 50


side = max(
    subject_width,
    subject_height
) + padding * 2


center_x = (
    min_x + max_x
) // 2


center_y = (
    min_y + max_y
) // 2


# Keep the face slightly above center.
center_y -= int(
    subject_height * 0.04
)


canvas = np.full(
    (
        side,
        side
    ),
    255,
    dtype=np.uint8
)


# Crop coordinates
x0 = (
    center_x
    - side // 2
)

y0 = (
    center_y
    - side // 2
)

x1 = (
    x0 + side
)

y1 = (
    y0 + side
)


# Source bounds
sx0 = max(
    x0,
    0
)

sy0 = max(
    y0,
    0
)

sx1 = min(
    x1,
    composited.shape[1]
)

sy1 = min(
    y1,
    composited.shape[0]
)


# Destination bounds
dx0 = (
    sx0 - x0
)

dy0 = (
    sy0 - y0
)

dx1 = (
    dx0
    + (sx1 - sx0)
)

dy1 = (
    dy0
    + (sy1 - sy0)
)


canvas[
    dy0:dy1,
    dx0:dx1
] = composited[
    sy0:sy1,
    sx0:sx1
]


# ============================================================
# 13. FINAL LIGHT CONTRAST
# ============================================================

# Keep the background pure white while preserving facial details.
canvas = cv2.normalize(
    canvas,
    None,
    0,
    255,
    cv2.NORM_MINMAX
)


# ============================================================
# 14. SAVE
# ============================================================

os.makedirs(
    os.path.dirname(
        OUTPUT
    ),
    exist_ok=True
)


Image.fromarray(
    canvas,
    mode="L"
).save(
    OUTPUT
)


# ============================================================
# DONE
# ============================================================

print()

print(
    "======================================"
)

print(
    " PORTRAIT PREPARATION COMPLETE"
)

print(
    "======================================"
)

print()

print(
    f"Input : {INPUT}"
)

print(
    f"Output: {OUTPUT}"
)

print(
    f"Size  : {canvas.shape[1]} x {canvas.shape[0]}"
)

print(
    "Mode  : Grayscale"
)

print(
    "Background: Removed"
)

print(
    "Facial details: Enhanced"
)

print()