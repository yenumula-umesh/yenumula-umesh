from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import urllib.request
import json

# ============================================================
# UMESH YENUMULA — CINEMATIC GITHUB HUD
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_IMAGE = BASE_DIR / "hero.png"
OUTPUT_IMAGE = BASE_DIR / "hero-live.png"

# -------------------------
# PERSONAL INFORMATION
# -------------------------

NAME = "UMESH YENUMULA"
TITLE = "DATA ANALYST  ×  AI ENGINEER"
EDUCATION = "BS IN DATA SCIENCE & APPLICATIONS"
COLLEGE = "IIT MADRAS"

EMAIL = "AVAILABLE VIA GITHUB"

SKILLS = [
    "PYTHON",
    "FLASK",
    "TELETHON",
    "REST APIs",
    "NUMPY",
    "GIT / GITHUB",
    "HTML / CSS",
    "C / C++",
    "SQL / DBMS",
]

GITHUB_USERNAME = "yenumula-umesh"

# ============================================================
# COLORS
# ============================================================

CYAN = (65, 190, 255, 235)
CYAN_SOFT = (65, 190, 255, 125)
CYAN_DIM = (65, 190, 255, 75)

WHITE = (220, 238, 248, 235)
WHITE_DIM = (170, 200, 215, 180)

DARK = (3, 12, 20, 160)
DARK_SOFT = (3, 12, 20, 105)

GREEN = (65, 255, 170, 230)

# ============================================================
# FONT LOADING
# ============================================================

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]

FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]


def find_font(paths):
    for path in paths:
        if Path(path).exists():
            return path
    return None


FONT_REGULAR = find_font(FONT_PATHS)
FONT_BOLD = find_font(FONT_BOLD_PATHS)


def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_REGULAR

    if path:
        return ImageFont.truetype(path, size=size)

    return ImageFont.load_default()


# ============================================================
# HELPERS
# ============================================================

def rounded_hud(draw, box, radius=16, fill=DARK_SOFT,
                outline=CYAN_SOFT, width=1):
    """
    Transparent futuristic HUD panel.
    """
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width
    )


def clipped_panel(draw, box, cut=16, fill=DARK_SOFT,
                  outline=CYAN_SOFT, width=1):
    """
    Futuristic panel with cut corners.
    """
    x1, y1, x2, y2 = box

    points = [
        (x1 + cut, y1),
        (x2 - cut, y1),
        (x2, y1 + cut),
        (x2, y2 - cut),
        (x2 - cut, y2),
        (x1 + cut, y2),
        (x1, y2 - cut),
        (x1, y1 + cut),
    ]

    draw.polygon(points, fill=fill)

    # Border
    draw.line(
        points + [points[0]],
        fill=outline,
        width=width,
        joint="curve"
    )


def line(draw, x1, y1, x2, y2, fill=CYAN_DIM, width=1):
    draw.line((x1, y1, x2, y2), fill=fill, width=width)


def label(draw, x, y, text, size=12, fill=WHITE_DIM):
    draw.text(
        (x, y),
        text.upper(),
        font=font(size),
        fill=fill
    )


def title(draw, x, y, text, size=26, fill=CYAN):
    draw.text(
        (x, y),
        text,
        font=font(size, bold=True),
        fill=fill
    )


def draw_corner_marks(draw, box, length=18):
    x1, y1, x2, y2 = box

    # top left
    line(draw, x1, y1 + length, x1, y1, CYAN_SOFT, 1)
    line(draw, x1, y1, x1 + length, y1, CYAN_SOFT, 1)

    # top right
    line(draw, x2 - length, y1, x2, y1, CYAN_SOFT, 1)
    line(draw, x2, y1, x2, y1 + length, CYAN_SOFT, 1)

    # bottom left
    line(draw, x1, y2 - length, x1, y2, CYAN_SOFT, 1)
    line(draw, x1, y2, x1 + length, y2, CYAN_SOFT, 1)

    # bottom right
    line(draw, x2 - length, y2, x2, y2, CYAN_SOFT, 1)
    line(draw, x2, y2 - length, x2, y2, CYAN_SOFT, 1)


def glow_panel(base, box, blur=8):
    """
    Adds a very subtle cyan glow behind the HUD.
    """
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)

    x1, y1, x2, y2 = box

    gd.rounded_rectangle(
        box,
        radius=15,
        outline=CYAN,
        width=3
    )

    glow = glow.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(glow)


# ============================================================
# LIVE GITHUB INFORMATION
# ============================================================

def get_github_data():
    """
    Gets public GitHub information.
    If API access fails, fallback values are used.
    """

    fallback = {
        "repos": 3,
        "followers": 0,
        "following": 0,
        "public_gists": 0,
    }

    url = f"https://api.github.com/users/{GITHUB_USERNAME}"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "github-profile-hud"
            }
        )

        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))

        return {
            "repos": data.get("public_repos", 0),
            "followers": data.get("followers", 0),
            "following": data.get("following", 0),
            "public_gists": data.get("public_gists", 0),
        }

    except Exception:
        return fallback


# ============================================================
# LOAD IMAGE
# ============================================================

if not INPUT_IMAGE.exists():
    raise FileNotFoundError(
        f"Could not find hero.png at: {INPUT_IMAGE}"
    )

base = Image.open(INPUT_IMAGE).convert("RGBA")

WIDTH, HEIGHT = base.size

# We design around a 1920x768 image.
# Scaling keeps the HUD proportional for other resolutions.

SX = WIDTH / 1920
SY = HEIGHT / 768


def S(x):
    return int(x * SX)


def T(y):
    return int(y * SY)


# ============================================================
# DRAWING LAYER
# ============================================================

overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)


# ============================================================
# LIVE IST TIME
# ============================================================

now = datetime.now(ZoneInfo("Asia/Kolkata"))

current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%d %b %Y").upper()
weekday = now.strftime("%A").upper()


# ============================================================
# GITHUB
# ============================================================

github = get_github_data()


# ============================================================
# 01 — SYSTEM STATUS
# LEFT SIDE
# ============================================================

system_box = (
    S(18),
    T(48),
    S(325),
    T(405),
)

glow_panel(overlay, system_box)

clipped_panel(
    draw,
    system_box,
    cut=S(14),
    fill=DARK_SOFT,
    outline=CYAN_SOFT
)

draw_corner_marks(draw, system_box)

label(
    draw,
    S(38),
    T(72),
    "// SYSTEM STATUS",
    12
)

title(
    draw,
    S(38),
    T(97),
    "OPERATIONAL",
    26
)

# live indicator
draw.ellipse(
    (S(286), T(99), S(296), T(109)),
    fill=GREEN
)

label(
    draw,
    S(38),
    T(136),
    "SYSTEM ONLINE",
    10,
    GREEN
)

# tiny waveform
wave_x = S(38)
wave_y = T(168)

points = []

for i in range(145):
    px = wave_x + S(i)
    py = wave_y + int(
        T(10)
        * ((i % 9) / 8)
        * (1 if i % 2 == 0 else -1)
    )

    points.append((px, py))

if len(points) > 1:
    draw.line(
        points,
        fill=CYAN_SOFT,
        width=1
    )

line(
    draw,
    S(38),
    T(188),
    S(300),
    T(188),
    CYAN_DIM
)

label(
    draw,
    S(38),
    T(207),
    "// LIVE CLOCK",
    10
)

draw.text(
    (S(38), T(230)),
    current_time,
    font=font(22, bold=True),
    fill=WHITE
)

label(
    draw,
    S(38),
    T(263),
    f"{current_date}  //  {weekday}",
    9
)

line(
    draw,
    S(38),
    T(286),
    S(300),
    T(286),
    CYAN_DIM
)

label(
    draw,
    S(38),
    T(305),
    "// PROFILE SIGNAL",
    10
)

label(
    draw,
    S(38),
    T(332),
    f"REPOSITORIES    {github['repos']:02d}",
    10
)

label(
    draw,
    S(38),
    T(352),
    f"FOLLOWERS       {github['followers']:02d}",
    10
)

label(
    draw,
    S(38),
    T(372),
    "NETWORK         ONLINE",
    10
)


# ============================================================
# 02 — MODULES / SKILLS
# LEFT LOWER
# ============================================================

modules_box = (
    S(18),
    T(420),
    S(325),
    T(625),
)

clipped_panel(
    draw,
    modules_box,
    cut=S(14),
    fill=DARK_SOFT,
    outline=CYAN_SOFT
)

draw_corner_marks(draw, modules_box)

label(
    draw,
    S(38),
    T(442),
    "// SKILL MATRIX",
    11
)

skill_y = 470

for i, skill in enumerate(SKILLS[:7]):

    # small technical node
    draw.ellipse(
        (
            S(40),
            T(skill_y + 4),
            S(46),
            T(skill_y + 10)
        ),
        outline=CYAN_SOFT,
        width=1
    )

    draw.text(
        (S(56), T(skill_y)),
        skill,
        font=font(11),
        fill=WHITE
    )

    line(
        draw,
        S(56),
        T(skill_y + 21),
        S(296),
        T(skill_y + 21),
        (65, 190, 255, 40)
    )

    skill_y += 30


# ============================================================
# 03 — SESSION
# CENTER / LOWER
# ============================================================

session_box = (
    S(845),
    T(535),
    S(1115),
    T(705),
)

clipped_panel(
    draw,
    session_box,
    cut=S(16),
    fill=DARK,
    outline=CYAN_SOFT
)

draw_corner_marks(draw, session_box)

label(
    draw,
    S(868),
    T(556),
    "// SESSION",
    10
)

label(
    draw,
    S(868),
    T(582),
    "USER",
    9
)

draw.text(
    (S(940), T(580)),
    "UMESH_YENUMULA",
    font=font(10, bold=True),
    fill=WHITE
)

label(
    draw,
    S(868),
    T(608),
    "IDENTITY",
    9
)

draw.text(
    (S(940), T(606)),
    TITLE,
    font=font(9),
    fill=CYAN
)

label(
    draw,
    S(868),
    T(634),
    "EDUCATION",
    9
)

draw.text(
    (S(940), T(632)),
    "IIT MADRAS",
    font=font(10, bold=True),
    fill=WHITE
)

label(
    draw,
    S(868),
    T(659),
    "LOCAL TIME",
    9
)

draw.text(
    (S(940), T(657)),
    f"{current_time} IST",
    font=font(10, bold=True),
    fill=GREEN
)

# activity bars
for i in range(9):
    height = 4 + ((i * 7) % 15)

    draw.rectangle(
        (
            S(865 + i * 19),
            T(688 - height),
            S(874 + i * 19),
            T(688)
        ),
        fill=CYAN_SOFT
    )


# ============================================================
# 04 — PROFILE / IDENTITY
# UPPER CENTER-RIGHT
# ============================================================

profile_box = (
    S(1195),
    T(28),
    S(1660),
    T(205),
)

clipped_panel(
    draw,
    profile_box,
    cut=S(18),
    fill=DARK_SOFT,
    outline=CYAN_SOFT
)

draw_corner_marks(draw, profile_box)

label(
    draw,
    S(1220),
    T(52),
    "// OPERATOR PROFILE",
    11
)

title(
    draw,
    S(1220),
    T(79),
    NAME,
    25
)

draw.text(
    (S(1220), T(116)),
    TITLE,
    font=font(15, bold=True),
    fill=CYAN
)

line(
    draw,
    S(1220),
    T(148),
    S(1625),
    T(148),
    CYAN_DIM
)

label(
    draw,
    S(1220),
    T(163),
    "BS DATA SCIENCE & APPLICATIONS  //  IIT MADRAS",
    10
)


# ============================================================
# 05 — REAL-TIME FEED
# RIGHT / LOWER
# ============================================================

feed_box = (
    S(1215),
    T(435),
    S(1635),
    T(685),
)

clipped_panel(
    draw,
    feed_box,
    cut=S(16),
    fill=DARK_SOFT,
    outline=CYAN_SOFT
)

draw_corner_marks(draw, feed_box)

label(
    draw,
    S(1240),
    T(457),
    "// REAL-TIME FEED",
    11
)

# feed lines based on actual profile information
feed_items = [
    ("TIME", current_time),
    ("DATE", current_date),
    ("GITHUB", "CONNECTED"),
    ("REPOS", str(github["repos"])),
    ("STATUS", "OPERATIONAL"),
    ("MODE", "LEARNING / BUILDING"),
]

feed_y = 490

for key, value in feed_items:

    label(
        draw,
        S(1240),
        T(feed_y),
        key,
        9
    )

    draw.text(
        (S(1350), T(feed_y)),
        value,
        font=font(9, bold=True),
        fill=WHITE
    )

    line(
        draw,
        S(1240),
        T(feed_y + 19),
        S(1605),
        T(feed_y + 19),
        (65, 190, 255, 35)
    )

    feed_y += 31


# tiny activity graph
graph_x = S(1240)
graph_y = T(668)

graph_points = []

for i in range(95):
    px = graph_x + S(i * 3.6)

    values = [0, 3, -2, 4, 1, -1, 5, -3, 2, 1]
    offset = values[i % len(values)]

    py = graph_y + T(offset)

    graph_points.append((px, py))

draw.line(
    graph_points,
    fill=CYAN_SOFT,
    width=1
)


# ============================================================
# 06 — MOTIVATION
# FAR RIGHT
# ============================================================

motivation_box = (
    S(1665),
    T(50),
    S(1902),
    T(315),
)

clipped_panel(
    draw,
    motivation_box,
    cut=S(16),
    fill=DARK_SOFT,
    outline=CYAN_SOFT
)

draw_corner_marks(draw, motivation_box)

label(
    draw,
    S(1690),
    T(72),
    "// MOTIVATION",
    10
)

draw.text(
    (S(1690), T(115)),
    "DISCIPLINE",
    font=font(19, bold=True),
    fill=WHITE
)

draw.text(
    (S(1737), T(145)),
    "TODAY",
    font=font(19, bold=True),
    fill=WHITE
)

line(
    draw,
    S(1700),
    T(185),
    S(1865),
    T(185),
    CYAN_DIM
)

draw.text(
    (S(1700), T(208)),
    "FREEDOM",
    font=font(19, bold=True),
    fill=WHITE
)

draw.text(
    (S(1730), T(238)),
    "TOMORROW",
    font=font(19, bold=True),
    fill=WHITE
)

# small signal mark
draw.ellipse(
    (
        S(1777),
        T(280),
        S(1787),
        T(290)
    ),
    outline=CYAN_SOFT,
    width=1
)

line(
    draw,
    S(1705),
    T(285),
    S(1760),
    T(285),
    CYAN_DIM
)

line(
    draw,
    S(1805),
    T(285),
    S(1860),
    T(285),
    CYAN_DIM
)


# ============================================================
# 07 — MICRO HUD DETAILS
# ============================================================

# center technical line
line(
    draw,
    S(858),
    T(503),
    S(1050),
    T(503),
    CYAN_DIM
)

label(
    draw,
    S(870),
    T(481),
    "FOCUS  >  EXECUTE  >  SUCCEED",
    9
)

# tiny coordinate readout
label(
    draw,
    S(1750),
    T(332),
    "SYS // PROFILE // ACTIVE",
    8
)

label(
    draw,
    S(35),
    T(698),
    "NODE 01",
    8
)

label(
    draw,
    S(95),
    T(698),
    "SECURE",
    8,
    GREEN
)

# tiny top-right signal
label(
    draw,
    S(1810),
    T(25),
    "LIVE",
    8,
    GREEN
)


# ============================================================
# COMPOSITE
# ============================================================

result = Image.alpha_composite(base, overlay)

# Slight sharpening after compositing
result = result.convert("RGB")

result.save(
    OUTPUT_IMAGE,
    quality=95
)

print("==============================================")
print("HUD GENERATED SUCCESSFULLY")
print(f"Output: {OUTPUT_IMAGE}")
print(f"IST: {current_time}")
print(f"Date: {current_date}")
print(f"GitHub repositories: {github['repos']}")
print("==============================================")
