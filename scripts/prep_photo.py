from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "source-prepped.png"


# --------------------------------------------------
# Get input image
# --------------------------------------------------

if len(sys.argv) < 2:
    print("Usage:")
    print("  python scripts/prep_photo.py assets/source-photo.JPG")
    sys.exit(1)

input_file = Path(sys.argv[1])

if not input_file.is_absolute():
    input_file = BASE_DIR / input_file

if not input_file.exists():
    print(f"Error: File not found: {input_file}")
    sys.exit(1)

print(f"Input : {input_file}")
print("Removing background...")


# --------------------------------------------------
# Remove background
# --------------------------------------------------

input_image = Image.open(input_file).convert("RGBA")

removed = remove(input_image)


# --------------------------------------------------
# Composite on white background
# --------------------------------------------------

white_background = Image.new(
    "RGBA",
    removed.size,
    (255, 255, 255, 255)
)

white_background.alpha_composite(removed)

rgb_image = white_background.convert("RGB")


# --------------------------------------------------
# Convert to OpenCV
# --------------------------------------------------

image = np.array(rgb_image)

gray = cv2.cvtColor(
    image,
    cv2.COLOR_RGB2GRAY
)


# --------------------------------------------------
# Improve local contrast using CLAHE
# --------------------------------------------------

clahe = cv2.createCLAHE(
    clipLimit=2.0,
    tileGridSize=(8, 8)
)

enhanced = clahe.apply(gray)


# --------------------------------------------------
# Slightly increase contrast
# --------------------------------------------------

enhanced = cv2.normalize(
    enhanced,
    None,
    alpha=0,
    beta=255,
    norm_type=cv2.NORM_MINMAX
)


# --------------------------------------------------
# Save result
# --------------------------------------------------

success = cv2.imwrite(
    str(OUTPUT_FILE),
    enhanced
)

if not success:
    print("Error: Could not save output image.")
    sys.exit(1)

print()
print("Done!")
print(f"Output: {OUTPUT_FILE}")