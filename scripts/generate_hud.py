from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from pathlib import Path
import textwrap


# ============================================================
# UMESH YENUMULA — GITHUB PROFILE HUD
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_IMAGE = ROOT / "hero.png"
OUTPUT_IMAGE = ROOT / "hero-live.png"


# ============================================================
# YOUR PROFILE INFORMATION
# ============================================================

NAME = "UMESH YENUMULA"
TITLE = "DATA ANALYST  ×  AI ENGINEER"

EDUCATION = "BS IN DATA SCIENCE & APPLICATIONS"
COLLEGE = "IIT MADRAS"

EMAIL = "YOUR_EMAIL@example.com"

SKILLS = [
    "PYTHON",
    "FLASK",
    "TELETHON",
    "REST APIs",
    "NUMPY",
    "GIT / GITHUB",
    "HTML / CSS",
    "C / C++",
]


# ============================================================
# LOAD IMAGE
# ============================================================

if not INPUT_IMAGE.exists():
    raise FileNotFoundError(
        "hero.png was not found. Put hero.png in the repository root."
    )

image = Image.open(INPUT_IMAGE).convert("RGBA")

width, height = image.size


# ============================================================
# DRAWING
# ============================================================

draw = ImageDraw.Draw(image, "RGBA")


# ------------------------------------------------------------
# FONT SETUP
# ------------------------------------------------------------

font_paths = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

if Path(bold_path).exists():
    FONT_BOLD = bold_path
else:
    FONT_BOLD = None

if Path(regular_path).exists():
    FONT_REGULAR = regular_path
else:
    FONT_REGULAR = None


def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REGULAR

    if path:
        return ImageFont.truetype(path, size)

    return ImageFont.load_default()


# ============================================================
# HUD PANEL
# ============================================================

panel_x = int(width * 0.60)
panel_y = int(height * 0.08)

panel_width = int(width * 0.36)
panel_height = int(height * 0.82)

# Dark transparent futuristic panel
draw.rounded_rectangle(
    (
        panel_x,
        panel_y,
        panel_x + panel_width,
        panel_y + panel_height,
    ),
    radius=24,
    fill=(5, 10, 18, 190),
    outline=(80, 210, 255, 180),
    width=2,
)


# ============================================================
# HEADER
# ============================================================

x = panel_x + 32
y = panel_y + 28

# Status indicator
draw.ellipse(
    (x, y + 7, x + 13, y + 20),
    fill=(80, 255, 170, 255),
)

draw.text(
    (x + 24, y),
    "SYSTEM OPERATIONAL",
    font=font(22, bold=True),
    fill=(120, 255, 190, 255),
)

y += 58


# ============================================================
# NAME
# ============================================================

draw.text(
    (x, y),
    NAME,
    font=font(34, bold=True),
    fill=(240, 248, 255, 255),
)

y += 48

draw.text(
    (x, y),
    TITLE,
    font=font(19, bold=True),
    fill=(80, 215, 255, 255),
)

y += 58


# ============================================================
# SEPARATOR
# ============================================================

draw.line(
    (x, y, panel_x + panel_width - 32, y),
    fill=(80, 210, 255, 120),
    width=2,
)

y += 28


# ============================================================
# EDUCATION
# ============================================================

draw.text(
    (x, y),
    "EDUCATION",
    font=font(16, bold=True),
    fill=(120, 180, 210, 255),
)

y += 28

draw.text(
    (x, y),
    COLLEGE,
    font=font(23, bold=True),
    fill=(240, 248, 255, 255),
)

y += 34

draw.text(
    (x, y),
    EDUCATION,
    font=font(15),
    fill=(190, 205, 220, 255),
)

y += 50


# ============================================================
# LIVE CLOCK
# ============================================================

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%d %b %Y").upper()

draw.text(
    (x, y),
    "LOCAL TIME",
    font=font(15, bold=True),
    fill=(120, 180, 210, 255),
)

draw.text(
    (x + 155, y),
    current_time,
    font=font(21, bold=True),
    fill=(100, 240, 255, 255),
)

y += 34

draw.text(
    (x, y),
    "DATE",
    font=font(15, bold=True),
    fill=(120, 180, 210, 255),
)

draw.text(
    (x + 155, y),
    current_date,
    font=font(19, bold=True),
    fill=(230, 240, 250, 255),
)

y += 52


# ============================================================
# SKILLS
# ============================================================

draw.text(
    (x, y),
    "ACTIVE LOADOUT",
    font=font(16, bold=True),
    fill=(120, 180, 210, 255),
)

y += 32


# Create two-column skill layout
column_gap = 18
column_width = (panel_width - 64 - column_gap) // 2

for index, skill in enumerate(SKILLS):

    column = index % 2
    row = index // 2

    skill_x = x + column * (column_width + column_gap)
    skill_y = y + row * 38

    draw.rounded_rectangle(
        (
            skill_x,
            skill_y,
            skill_x + column_width,
            skill_y + 29,
        ),
        radius=8,
        fill=(20, 35, 48, 190),
        outline=(60, 150, 180, 100),
        width=1,
    )

    draw.text(
        (skill_x + 10, skill_y + 5),
        skill,
        font=font(13, bold=True),
        fill=(210, 230, 240, 255),
    )


y += ((len(SKILLS) + 1) // 2) * 38 + 20


# ============================================================
# CONTACT
# ============================================================

draw.line(
    (x, y, panel_x + panel_width - 32, y),
    fill=(80, 210, 255, 100),
    width=1,
)

y += 20

draw.text(
    (x, y),
    "CONTACT",
    font=font(15, bold=True),
    fill=(120, 180, 210, 255),
)

y += 27

draw.text(
    (x, y),
    EMAIL,
    font=font(15),
    fill=(220, 235, 245, 255),
)


# ============================================================
# SMALL HUD CORNERS
# ============================================================

corner_size = 18

# top-left
draw.line(
    (panel_x, panel_y + corner_size, panel_x, panel_y),
    fill=(100, 220, 255, 220),
    width=3,
)

draw.line(
    (panel_x, panel_y, panel_x + corner_size, panel_y),
    fill=(100, 220, 255, 220),
    width=3,
)

# bottom-right
bx = panel_x + panel_width
by = panel_y + panel_height

draw.line(
    (bx - corner_size, by, bx, by),
    fill=(100, 220, 255, 220),
    width=3,
)

draw.line(
    (bx, by - corner_size, bx, by),
    fill=(100, 220, 255, 220),
    width=3,
)


# ============================================================
# SAVE
# ============================================================

image.convert("RGB").save(
    OUTPUT_IMAGE,
    "PNG",
    optimize=True,
)

print(f"Generated: {OUTPUT_IMAGE}")
