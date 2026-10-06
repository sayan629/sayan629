from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "info-card.svg"


# --------------------------------------------------
# Card configuration
# --------------------------------------------------

WIDTH = 490
HEIGHT = 520

BG = "#ffffff"
TEXT = "#111111"
MUTED = "#666666"
BORDER = "#111111"


# --------------------------------------------------
# Profile data
# --------------------------------------------------

lines = [
    ("$ whoami", "command"),
    ("Sayan Pal", "title"),
    ("", "space"),

    ("$ education", "command"),
    ("MCA @ KIIT", "normal"),
    ("", "space"),

    ("$ focus", "command"),
    ("AI / ML / Software Development", "normal"),
    ("", "space"),

    ("$ stack", "command"),
    ("Python     JavaScript     Java", "normal"),
    ("React      Next.js        FastAPI", "normal"),
    ("Node.js    MongoDB        Docker", "normal"),
    ("Git        LangChain      LangGraph", "normal"),
    ("", "space"),

    ("$ projects", "command"),
    ("OryntisAI", "normal"),
    ("Prepzy", "normal"),
    ("AiPaperPilot", "normal"),
    ("Agentic AI Calendar", "normal"),
    ("", "space"),

    ("$ status", "command"),
    ("Building intelligent systems.", "normal"),
    ("Always learning. Always shipping.", "normal"),
]


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

.card-line {
    opacity: 0;
    transform: translateY(8px);
    animation:
        lineReveal
        0.45s
        ease-out
        forwards;
}

@keyframes lineReveal {

    0% {
        opacity: 0;
        transform: translateY(8px);
    }

    100% {
        opacity: 1;
        transform: translateY(0);
    }

}

.cursor {
    animation: blink 1s steps(1) infinite;
}

@keyframes blink {

    0%, 50% {
        opacity: 1;
    }

    51%, 100% {
        opacity: 0;
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
    x="0"
    y="0"
    width="{WIDTH}"
    height="{HEIGHT}"
    rx="12"
    fill="{BG}"
    stroke="{BORDER}"
    stroke-width="2"
/>
'''
)


# --------------------------------------------------
# Terminal header
# --------------------------------------------------

svg.append(
    '''
<rect
    x="0"
    y="0"
    width="490"
    height="42"
    rx="12"
    fill="#111111"
/>

<circle cx="20" cy="21" r="6" fill="#ffffff"/>
<circle cx="40" cy="21" r="6" fill="#ffffff"/>
<circle cx="60" cy="21" r="6" fill="#ffffff"/>

<text
    x="245"
    y="27"
    text-anchor="middle"
    font-family="Consolas, Monaco, monospace"
    font-size="13"
    fill="#ffffff">
    sayan@github ~
</text>
'''
)


# --------------------------------------------------
# Content
# --------------------------------------------------

y = 76
line_height = 20

animation_index = 0

for text, kind in lines:

    if kind == "space":
        y += 10
        continue

    escaped = (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    delay = animation_index * 0.08

    if kind == "command":

        font_size = 14
        weight = "600"
        fill = TEXT

    elif kind == "title":

        font_size = 25
        weight = "700"
        fill = TEXT

    else:

        font_size = 13
        weight = "400"
        fill = MUTED

    svg.append(
        f'''
<text
    class="card-line"
    x="28"
    y="{y}"
    font-family="Consolas, Monaco, monospace"
    font-size="{font_size}px"
    font-weight="{weight}"
    fill="{fill}"
    style="animation-delay:{delay:.2f}s;">
    {escaped}
</text>
'''
    )

    y += line_height
    animation_index += 1


# --------------------------------------------------
# Cursor
# --------------------------------------------------

svg.append(
    f'''
<text
    class="cursor"
    x="28"
    y="{HEIGHT - 20}"
    font-family="Consolas, Monaco, monospace"
    font-size="14"
    font-weight="700"
    fill="{TEXT}">
    █
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
    encoding="utf-8"
)


print()
print("======================================")
print(" INFO CARD SVG CREATED")
print("======================================")
print()
print(f"Output: {OUTPUT_FILE}")
print(f"Size  : {WIDTH} x {HEIGHT}")
print("Style : Terminal / Monochrome")
print("Animation: Line-by-line")
print()