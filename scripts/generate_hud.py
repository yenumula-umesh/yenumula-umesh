from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import urllib.request
import json

# ============================================================
# UMESH YENUMULA — CINEMATIC GITHUB HUD
# Time/date intentionally NOT rendered into the image.
# GitHub numbers are refreshed whenever this workflow runs.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_IMAGE = BASE_DIR / "hero.png"
OUTPUT_IMAGE = BASE_DIR / "hero-live.png"

NAME = "UMESH YENUMULA"
TITLE = "DATA ANALYST  ×  AI ENGINEER"
EDUCATION = "BS IN DATA SCIENCE & APPLICATIONS"
COLLEGE = "IIT MADRAS"
GITHUB_USERNAME = "yenumula-umesh"

SKILLS = [
    "PYTHON", "FLASK", "TELETHON", "REST APIs", "NUMPY",
    "GIT / GITHUB", "HTML / CSS", "C / C++", "SQL / DBMS"
]

# Visual palette — restrained so it blends with the original image.
CYAN = (65, 205, 255, 235)
CYAN_SOFT = (65, 205, 255, 125)
CYAN_DIM = (65, 205, 255, 55)
VIOLET_SOFT = (145, 100, 255, 115)
WHITE = (225, 241, 248, 235)
WHITE_DIM = (170, 202, 218, 175)
GREEN = (70, 255, 170, 235)
DARK = (3, 11, 20, 150)
DARK_DEEP = (3, 10, 18, 180)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]
BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]


def find_font(paths):
    for p in paths:
        if Path(p).exists():
            return p
    return None


REGULAR = find_font(FONT_PATHS)
BOLD = find_font(BOLD_PATHS)


def f(size, bold=False):
    path = BOLD if bold else REGULAR
    return ImageFont.truetype(path, size) if path else ImageFont.load_default()


def scaled(box, sx, sy):
    return tuple(int(v * (sx if i % 2 == 0 else sy)) for i, v in enumerate(box))


def draw_line(d, x1, y1, x2, y2, fill=CYAN_DIM, width=1):
    d.line((x1, y1, x2, y2), fill=fill, width=width)


def hud_panel(d, box, cut=14, fill=DARK, outline=CYAN_SOFT):
    x1, y1, x2, y2 = box
    pts = [
        (x1 + cut, y1), (x2 - cut, y1), (x2, y1 + cut),
        (x2, y2 - cut), (x2 - cut, y2), (x1 + cut, y2),
        (x1, y2 - cut), (x1, y1 + cut)
    ]
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=outline, width=1, joint="curve")


def corner_marks(d, box, length=16):
    x1, y1, x2, y2 = box
    c = CYAN_SOFT
    draw_line(d, x1, y1 + length, x1, y1, c)
    draw_line(d, x1, y1, x1 + length, y1, c)
    draw_line(d, x2 - length, y1, x2, y1, c)
    draw_line(d, x2, y1, x2, y1 + length, c)
    draw_line(d, x1, y2 - length, x1, y2, c)
    draw_line(d, x1, y2, x1 + length, y2, c)
    draw_line(d, x2 - length, y2, x2, y2, c)
    draw_line(d, x2, y2 - length, x2, y2, c)


def glow(base, box):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle(box, radius=14, outline=CYAN, width=3)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(8)))


def label(d, x, y, text, size=10, fill=WHITE_DIM):
    d.text((x, y), text.upper(), font=f(size), fill=fill)


def text(d, x, y, value, size=12, fill=WHITE, bold=False):
    d.text((x, y), value, font=f(size, bold), fill=fill)


def github_data():
    fallback = {"repos": 0, "followers": 0}
    url = f"https://api.github.com/users/{GITHUB_USERNAME}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "umesh-profile-hud"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode("utf-8"))
        return {
            "repos": int(data.get("public_repos", 0)),
            "followers": int(data.get("followers", 0)),
        }
    except Exception:
        return fallback


if not INPUT_IMAGE.exists():
    raise FileNotFoundError(f"Could not find hero.png at {INPUT_IMAGE}")

base = Image.open(INPUT_IMAGE).convert("RGBA")
W, H = base.size
sx, sy = W / 1920, H / 768
S = lambda x: int(x * sx)
T = lambda y: int(y * sy)

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
gh = github_data()

# ------------------------------------------------------------
# LEFT — SYSTEM STATUS (NO CLOCK)
# ------------------------------------------------------------
system = scaled((18, 48, 325, 355), sx, sy)
glow(layer, system)
hud_panel(d, system, S(14))
corner_marks(d, system)
label(d, S(38), T(70), "// SYSTEM STATUS", 11)
text(d, S(38), T(96), "OPERATIONAL", 25, GREEN, True)
d.ellipse((S(286), T(99), S(296), T(109)), fill=GREEN)
label(d, S(38), T(133), "SYSTEM ONLINE", 9, GREEN)

# visual signal strip
points = []
for i in range(150):
    x = S(38) + S(i)
    pattern = [0, -3, 2, -1, 5, -2, 1, 0, 3, -1]
    y = T(166) + T(pattern[i % len(pattern)])
    points.append((x, y))
d.line(points, fill=CYAN_SOFT, width=1)

draw_line(d, S(38), T(188), S(300), T(188))
label(d, S(38), T(206), "// PROFILE SIGNAL", 9)
label(d, S(38), T(237), f"REPOSITORIES    {gh['repos']:02d}", 10, WHITE)
label(d, S(38), T(264), f"FOLLOWERS       {gh['followers']:02d}", 10, WHITE)
label(d, S(38), T(291), "GITHUB          CONNECTED", 10, GREEN)
label(d, S(38), T(318), "NETWORK         ONLINE", 10, GREEN)

# ------------------------------------------------------------
# LEFT LOWER — SKILL MATRIX
# ------------------------------------------------------------
skills_box = scaled((18, 372, 325, 625), sx, sy)
hud_panel(d, skills_box, S(14))
corner_marks(d, skills_box)
label(d, S(38), T(394), "// SKILL MATRIX", 11)

# Two-column matrix: cleaner and more compact.
for i, skill in enumerate(SKILLS):
    col = i % 2
    row = i // 2
    x = S(40 + col * 126)
    y = T(428 + row * 39)
    d.ellipse((x, y + T(4), x + S(7), y + T(11)), outline=CYAN_SOFT, width=1)
    text(d, x + S(14), y, skill, 9, WHITE)
    draw_line(d, x + S(14), y + T(22), x + S(113), y + T(22), CYAN_DIM)

# small active-module footer
label(d, S(40), T(588), "MODULES", 8)
text(d, S(102), T(586), "09 ACTIVE", 9, CYAN, True)

# ------------------------------------------------------------
# UPPER CENTER-RIGHT — OPERATOR PROFILE
# ------------------------------------------------------------
profile = scaled((900, 28, 1645, 185), sx, sy)
hud_panel(d, profile, S(18))
corner_marks(d, profile)
label(d, S(925), T(51), "// OPERATOR PROFILE", 10)
text(d, S(925), T(78), NAME, 24, WHITE, True)
text(d, S(925), T(115), TITLE, 14, CYAN, True)
draw_line(d, S(925), T(142), S(1608), T(142), CYAN_DIM)
label(d, S(925), T(156), f"{EDUCATION}  //  {COLLEGE}", 9)

# decorative signal marks inside the profile box
for i in range(5):
    x = S(1540 + i * 13)
    d.rectangle((x, T(57), x + S(6), T(62 + (i % 3) * 7)), fill=(145, 100, 255, 110))

# ------------------------------------------------------------
# CENTER LOWER — SESSION (NO CLOCK)
# ------------------------------------------------------------
session = scaled((845, 535, 1120, 705), sx, sy)
hud_panel(d, session, S(16), fill=DARK_DEEP)
corner_marks(d, session)
label(d, S(868), T(556), "// SESSION", 10)
label(d, S(868), T(582), "USER", 9)
text(d, S(940), T(579), "UMESH_YENUMULA", 9, WHITE, True)
label(d, S(868), T(611), "IDENTITY", 9)
text(d, S(940), T(608), "DATA ANALYST × AI ENGINEER", 8, CYAN, True)
label(d, S(868), T(640), "EDUCATION", 9)
text(d, S(940), T(637), "IIT MADRAS", 10, WHITE, True)
label(d, S(868), T(669), "SESSION", 9)
text(d, S(940), T(666), "ACTIVE / PUBLIC", 9, GREEN, True)

# ------------------------------------------------------------
# RIGHT LOWER — LIVE GITHUB FEED (REAL VALUES)
# ------------------------------------------------------------
feed = scaled((1185, 320, 1635, 685), sx, sy)
hud_panel(d, feed, S(16))
corner_marks(d, feed)
label(d, S(1210), T(343), "// LIVE GITHUB FEED", 10)
label(d, S(1210), T(371), "PUBLIC SIGNAL", 8, GREEN)

feed_items = [
    ("REPOSITORIES", f"{gh['repos']:02d}"),
    ("FOLLOWERS", f"{gh['followers']:02d}"),
    ("ACCOUNT", "CONNECTED"),
    ("VISIBILITY", "PUBLIC"),
    ("STATUS", "OPERATIONAL"),
]

y = 405
for key, value in feed_items:
    label(d, S(1210), T(y), key, 9)
    text(d, S(1390), T(y - 1), value, 9, GREEN if value in {"CONNECTED", "OPERATIONAL"} else WHITE, True)
    draw_line(d, S(1210), T(y + 21), S(1610), T(y + 21), CYAN_DIM)
    y += 43

label(d, S(1210), T(635), "ACTIVITY SIGNAL", 8)
# Tiny synthetic visualizer for aesthetics only — not presented as real statistics.
vals = [2, 6, 4, 10, 7, 13, 5, 9, 11, 7, 14, 9, 16, 12, 18, 10]
for i, v in enumerate(vals):
    x = S(1215 + i * 23)
    d.rectangle((x, T(675 - v), x + S(10), T(675)), fill=CYAN_SOFT)

# ------------------------------------------------------------
# FAR RIGHT — MOTIVATION
# ------------------------------------------------------------
motivation = scaled((1665, 50, 1902, 315), sx, sy)
hud_panel(d, motivation, S(16))
corner_marks(d, motivation)
label(d, S(1690), T(72), "// MOTIVATION", 9)
text(d, S(1690), T(112), "DISCIPLINE", 18, WHITE, True)
text(d, S(1740), T(141), "TODAY", 18, WHITE, True)
draw_line(d, S(1700), T(183), S(1865), T(183), VIOLET_SOFT)
text(d, S(1700), T(205), "FREEDOM", 18, WHITE, True)
text(d, S(1730), T(234), "TOMORROW", 18, WHITE, True)
label(d, S(1700), T(278), "BUILD  //  LEARN  //  EVOLVE", 7, CYAN)

# ------------------------------------------------------------
# MICRO HUD DETAILS
# ------------------------------------------------------------
label(d, S(855), T(482), "FOCUS  >  EXECUTE  >  SUCCEED", 8)
label(d, S(1745), T(335), "SYS // PROFILE // ACTIVE", 7)
label(d, S(35), T(700), "NODE 01", 7)
label(d, S(95), T(700), "SECURE", 7, GREEN)
label(d, S(1810), T(24), "LIVE", 7, GREEN)

result = Image.alpha_composite(base, layer).convert("RGB")
result.save(OUTPUT_IMAGE, quality=95)

print("==============================================")
print("HUD GENERATED SUCCESSFULLY")
print(f"Output: {OUTPUT_IMAGE}")
print(f"GitHub repositories: {gh['repos']}")
print(f"GitHub followers: {gh['followers']}")
print("Clock/date intentionally omitted from the image.")
print("==============================================")
