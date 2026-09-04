from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import urllib.request
import urllib.error
import json

# ============================================================
# UMESH YENUMULA — CINEMATIC GITHUB HUD
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_IMAGE = BASE_DIR / "hero.png"
OUTPUT_IMAGE = BASE_DIR / "hero-live.png"

# ============================================================
# PROFILE
# ============================================================

NAME = "UMESH YENUMULA"
TITLE = "DATA ANALYST  ×  AI ENGINEER"

COLLEGE = "IIT MADRAS"
PROGRAM = "BS IN DATA SCIENCE & APPLICATIONS"

GITHUB_USERNAME = "yenumula-umesh"

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

# ============================================================
# HUD COLORS
# ============================================================

CYAN = (70, 195, 255, 235)
CYAN_SOFT = (70, 195, 255, 125)
CYAN_DIM = (70, 195, 255, 50)

VIOLET = (165, 110, 255, 225)
VIOLET_SOFT = (165, 110, 255, 105)

GREEN = (70, 255, 175, 235)

WHITE = (230, 243, 250, 238)
WHITE_DIM = (175, 205, 220, 185)

GLASS = (2, 10, 18, 88)
GLASS_DARK = (2, 10, 18, 115)

# ============================================================
# FONT PATHS
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
# DRAWING HELPERS
# ============================================================

def line(draw, x1, y1, x2, y2, fill=CYAN_DIM, width=1):
    draw.line(
        (x1, y1, x2, y2),
        fill=fill,
        width=width,
    )


def text_label(draw, x, y, text, size=9, fill=WHITE_DIM):
    draw.text(
        (x, y),
        str(text).upper(),
        font=font(size),
        fill=fill,
    )


def text_title(draw, x, y, text, size=22, fill=CYAN):
    draw.text(
        (x, y),
        str(text),
        font=font(size, bold=True),
        fill=fill,
    )


def clipped_panel(
    draw,
    box,
    cut=14,
    fill=GLASS,
    outline=CYAN_SOFT,
    width=1,
):
    """
    Futuristic transparent panel with cut corners.
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

    draw.polygon(
        points,
        fill=fill,
    )

    draw.line(
        points + [points[0]],
        fill=outline,
        width=width,
        joint="curve",
    )


def corner_marks(draw, box, length=15):
    """
    Small technical corner brackets.
    """

    x1, y1, x2, y2 = box

    # top-left
    line(draw, x1, y1 + length, x1, y1, CYAN_SOFT)
    line(draw, x1, y1, x1 + length, y1, CYAN_SOFT)

    # top-right
    line(draw, x2 - length, y1, x2, y1, VIOLET_SOFT)
    line(draw, x2, y1, x2, y1 + length, VIOLET_SOFT)

    # bottom-left
    line(draw, x1, y2 - length, x1, y2, VIOLET_SOFT)
    line(draw, x1, y2, x1 + length, y2, VIOLET_SOFT)

    # bottom-right
    line(draw, x2 - length, y2, x2, y2, CYAN_SOFT)
    line(draw, x2, y2 - length, x2, y2, CYAN_SOFT)


def glow_panel(base, box):
    """
    Very subtle glow behind a HUD panel.
    """

    glow = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0),
    )

    gd = ImageDraw.Draw(glow)

    gd.rounded_rectangle(
        box,
        radius=14,
        outline=CYAN,
        width=2,
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(7)
    )

    base.alpha_composite(glow)


def fit_text(
    draw,
    text,
    max_width,
    start_size,
    min_size=8,
    bold=False,
):
    size = start_size

    while size > min_size:

        current_font = font(
            size,
            bold=bold,
        )

        width = draw.textbbox(
            (0, 0),
            text,
            font=current_font,
        )[2]

        if width <= max_width:
            return current_font

        size -= 1

    return font(
        min_size,
        bold=bold,
    )


def wrap_text(draw, text, max_width, text_font):
    """
    Wrap text to fit inside a HUD panel.
    """

    words = str(text).split()

    lines = []
    current = ""

    for word in words:

        test = f"{current} {word}".strip()

        width = draw.textbbox(
            (0, 0),
            test,
            font=text_font,
        )[2]

        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


# ============================================================
# GITHUB API
# ============================================================

API_HEADERS = {
    "User-Agent": "umesh-github-profile-hud",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def github_get(path):
    """
    Request data from GitHub public REST API.
    """

    url = f"https://api.github.com{path}"

    request = urllib.request.Request(
        url,
        headers=API_HEADERS,
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


# ============================================================
# GET LIVE GITHUB DATA
# ============================================================

def get_github_data():

    fallback = {
        "repos": 0,
        "followers": 0,
        "following": 0,

        "latest_name": "NO PROJECT FOUND",
        "latest_description": (
            "No public project information available."
        ),
        "latest_language": "N/A",

        "latest_sha": "N/A",
        "latest_author": "N/A",
        "latest_commit_date": "N/A",
        "latest_commit_time": "N/A",
    }

    try:

        # ----------------------------------------------------
        # Profile data
        # ----------------------------------------------------

        user = github_get(
            f"/users/{GITHUB_USERNAME}"
        )

        # ----------------------------------------------------
        # Public repositories
        # ----------------------------------------------------

        repositories = github_get(
            f"/users/{GITHUB_USERNAME}/repos"
            "?type=owner"
            "&sort=pushed"
            "&direction=desc"
            "&per_page=30"
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Exclude the GitHub profile repository.
        #
        # Otherwise the workflow itself updates the profile
        # repository and it would constantly appear as the
        # "latest repository".
        # ----------------------------------------------------

        project_repositories = [
            repo
            for repo in repositories
            if repo.get("name", "").lower()
            != GITHUB_USERNAME.lower()
            and not repo.get("fork", False)
        ]

        latest_repo = (
            project_repositories[0]
            if project_repositories
            else None
        )

        result = {
            "repos": int(
                user.get(
                    "public_repos",
                    0,
                )
            ),

            "followers": int(
                user.get(
                    "followers",
                    0,
                )
            ),

            "following": int(
                user.get(
                    "following",
                    0,
                )
            ),

            "latest_name": "NO PROJECT FOUND",

            "latest_description": (
                "No public project information available."
            ),

            "latest_language": "N/A",

            "latest_sha": "N/A",
            "latest_author": "N/A",
            "latest_commit_date": "N/A",
            "latest_commit_time": "N/A",
        }

        # ----------------------------------------------------
        # Latest repository
        # ----------------------------------------------------

        if latest_repo:

            repo_name = latest_repo.get(
                "name",
                "UNKNOWN",
            )

            description = (
                latest_repo.get(
                    "description"
                )
                or "Public repository."
            )

            language = (
                latest_repo.get(
                    "language"
                )
                or "N/A"
            )

            result["latest_name"] = repo_name
            result["latest_description"] = description
            result["latest_language"] = language

            # ------------------------------------------------
            # Latest commit
            # ------------------------------------------------

            try:

                commits = github_get(
                    f"/repos/"
                    f"{GITHUB_USERNAME}/"
                    f"{repo_name}"
                    "/commits?per_page=1"
                )

                if commits:

                    latest_commit = commits[0]

                    result["latest_sha"] = (
                        latest_commit
                        .get("sha", "N/A")[:8]
                    )

                    commit_info = (
                        latest_commit
                        .get("commit", {})
                    )

                    author_info = (
                        commit_info
                        .get("author", {})
                    )

                    result["latest_author"] = (
                        author_info
                        .get(
                            "name",
                            "UNKNOWN",
                        )
                    )

                    timestamp = (
                        author_info
                        .get("date")
                    )

                    if timestamp:

                        parsed = (
                            datetime
                            .fromisoformat(
                                timestamp
                                .replace(
                                    "Z",
                                    "+00:00",
                                )
                            )
                        )

                        ist = (
                            parsed.astimezone(
                                ZoneInfo(
                                    "Asia/Kolkata"
                                )
                            )
                        )

                        result["latest_commit_date"] = (
                            ist.strftime(
                                "%d %b %Y"
                            ).upper()
                        )

                        result["latest_commit_time"] = (
                            ist.strftime(
                                "%H:%M"
                            )
                        )

            except Exception as commit_error:

                print(
                    "Latest commit lookup warning:",
                    commit_error,
                )

        return result

    except Exception as error:

        print(
            "GitHub API warning:",
            error,
        )

        return fallback


# ============================================================
# LOAD BACKGROUND IMAGE
# ============================================================

if not INPUT_IMAGE.exists():

    raise FileNotFoundError(
        f"Could not find hero.png at: {INPUT_IMAGE}"
    )


base = Image.open(
    INPUT_IMAGE
).convert("RGBA")

WIDTH, HEIGHT = base.size

# ============================================================
# SCALE
# ============================================================

# Your current image was designed around
# approximately 1920 × 768.

SX = WIDTH / 1920
SY = HEIGHT / 768


def S(value):
    return int(value * SX)


def T(value):
    return int(value * SY)


# ============================================================
# FETCH DATA
# ============================================================

github = get_github_data()


# ============================================================
# CREATE HUD LAYERS
# ============================================================

overlay = Image.new(
    "RGBA",
    (WIDTH, HEIGHT),
    (0, 0, 0, 0),
)

glow_layer = Image.new(
    "RGBA",
    (WIDTH, HEIGHT),
    (0, 0, 0, 0),
)

draw = ImageDraw.Draw(overlay)


# ============================================================
# 01 — SYSTEM STATUS
# ============================================================

system_box = (
    S(18),
    T(48),
    S(325),
    T(405),
)

glow_panel(
    glow_layer,
    system_box,
)

clipped_panel(
    draw,
    system_box,
    cut=S(14),
    fill=GLASS,
    outline=CYAN_SOFT,
)

corner_marks(
    draw,
    system_box,
)

text_label(
    draw,
    S(38),
    T(72),
    "// SYSTEM STATUS",
    10,
)

text_title(
    draw,
    S(38),
    T(98),
    "OPERATIONAL",
    23,
)

# Online indicator

draw.ellipse(
    (
        S(286),
        T(100),
        S(296),
        T(110),
    ),
    fill=GREEN,
)

text_label(
    draw,
    S(38),
    T(135),
    "PROFILE ONLINE",
    9,
    GREEN,
)

line(
    draw,
    S(38),
    T(161),
    S(300),
    T(161),
    CYAN_DIM,
)

# Decorative signal waveform

wave_points = []

wave_pattern = [
    0,
    -3,
    2,
    5,
    1,
    -2,
    4,
    0,
    3,
    -1,
]

for i in range(120):

    x = S(38) + S(i)

    y = (
        T(181)
        + T(
            wave_pattern[
                i % len(wave_pattern)
            ]
        )
    )

    wave_points.append(
        (x, y)
    )

if len(wave_points) > 1:

    draw.line(
        wave_points,
        fill=CYAN_SOFT,
        width=1,
    )

text_label(
    draw,
    S(38),
    T(205),
    "// ACCOUNT SIGNAL",
    9,
)

text_label(
    draw,
    S(38),
    T(232),
    f"REPOSITORIES   {github['repos']:02d}",
    10,
)

text_label(
    draw,
    S(38),
    T(255),
    f"FOLLOWERS      {github['followers']:02d}",
    10,
)

text_label(
    draw,
    S(38),
    T(278),
    f"FOLLOWING      {github['following']:02d}",
    10,
)

line(
    draw,
    S(38),
    T(302),
    S(300),
    T(302),
    CYAN_DIM,
)

text_label(
    draw,
    S(38),
    T(320),
    "// NETWORK",
    9,
)

text_label(
    draw,
    S(38),
    T(344),
    "GITHUB          CONNECTED",
    9,
    GREEN,
)

text_label(
    draw,
    S(38),
    T(368),
    "API SIGNAL      ACTIVE",
    9,
)


# ============================================================
# 02 — SKILLS
# ============================================================

skills_box = (
    S(18),
    T(420),
    S(325),
    T(625),
)

clipped_panel(
    draw,
    skills_box,
    cut=S(14),
    fill=GLASS,
    outline=VIOLET_SOFT,
)

corner_marks(
    draw,
    skills_box,
)

text_label(
    draw,
    S(38),
    T(442),
    "// SKILL MATRIX",
    10,
)

skill_y = 469

for index, skill in enumerate(
    SKILLS[:7]
):

    accent = (
        CYAN_SOFT
        if index % 2 == 0
        else VIOLET_SOFT
    )

    draw.ellipse(
        (
            S(40),
            T(skill_y + 3),
            S(47),
            T(skill_y + 10),
        ),
        outline=accent,
        width=1,
    )

    draw.text(
        (
            S(58),
            T(skill_y),
        ),
        skill,
        font=font(10),
        fill=WHITE,
    )

    line(
        draw,
        S(58),
        T(skill_y + 19),
        S(298),
        T(skill_y + 19),
        (65, 190, 255, 28),
    )

    skill_y += 29


# ============================================================
# 03 — LATEST REPOSITORY
# ============================================================

latest_box = (
    S(845),
    T(515),
    S(1118),
    T(705),
)

glow_panel(
    glow_layer,
    latest_box,
)

clipped_panel(
    draw,
    latest_box,
    cut=S(16),
    fill=GLASS_DARK,
    outline=VIOLET_SOFT,
)

corner_marks(
    draw,
    latest_box,
)

text_label(
    draw,
    S(868),
    T(537),
    "// LATEST REPOSITORY",
    9,
)

latest_name = (
    github["latest_name"]
)

latest_name_font = fit_text(
    draw,
    latest_name.upper(),
    S(220),
    16,
    8,
    bold=True,
)

draw.text(
    (
        S(868),
        T(562),
    ),
    latest_name.upper(),
    font=latest_name_font,
    fill=CYAN,
)

line(
    draw,
    S(868),
    T(594),
    S(1094),
    T(594),
    CYAN_DIM,
)

description_font = font(
    8
)

description_lines = wrap_text(
    draw,
    github["latest_description"],
    S(215),
    description_font,
)

for i, desc_line in enumerate(
    description_lines[:3]
):

    draw.text(
        (
            S(868),
            T(
                607 + i * 15
            ),
        ),
        desc_line.upper(),
        font=description_font,
        fill=WHITE_DIM,
    )

meta_y = 662

text_label(
    draw,
    S(868),
    T(meta_y),
    f"LANGUAGE   {github['latest_language']}",
    8,
)

text_label(
    draw,
    S(868),
    T(meta_y + 18),
    "SOURCE     GITHUB",
    8,
    GREEN,
)


# ============================================================
# 04 — OPERATOR PROFILE
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
    fill=GLASS,
    outline=CYAN_SOFT,
)

corner_marks(
    draw,
    profile_box,
)

text_label(
    draw,
    S(1220),
    T(51),
    "// OPERATOR PROFILE",
    10,
)

text_title(
    draw,
    S(1220),
    T(78),
    NAME,
    23,
)

title_font = fit_text(
    draw,
    TITLE,
    S(390),
    14,
    9,
    bold=True,
)

draw.text(
    (
        S(1220),
        T(114),
    ),
    TITLE,
    font=title_font,
    fill=VIOLET,
)

line(
    draw,
    S(1220),
    T(145),
    S(1625),
    T(145),
    CYAN_DIM,
)

text_label(
    draw,
    S(1220),
    T(159),
    PROGRAM,
    8,
)

text_label(
    draw,
    S(1220),
    T(178),
    f"// {COLLEGE}",
    9,
    WHITE,
)


# ============================================================
# 05 — REAL-TIME GITHUB FEED
# ============================================================

feed_box = (
    S(1215),
    T(435),
    S(1635),
    T(685),
)

glow_panel(
    glow_layer,
    feed_box,
)

clipped_panel(
    draw,
    feed_box,
    cut=S(16),
    fill=GLASS,
    outline=CYAN_SOFT,
)

corner_marks(
    draw,
    feed_box,
)

text_label(
    draw,
    S(1240),
    T(457),
    "// REAL-TIME GITHUB FEED",
    9,
)

text_label(
    draw,
    S(1240),
    T(486),
    "LATEST COMMIT",
    8,
)

commit_sha = (
    github["latest_sha"]
)

draw.text(
    (
        S(1240),
        T(508),
    ),
    f"#{commit_sha}",
    font=font(
        12,
        bold=True,
    ),
    fill=CYAN,
)

feed_repo_font = fit_text(
    draw,
    github["latest_name"].upper(),
    S(330),
    8,
    7,
)

draw.text(
    (
        S(1240),
        T(540),
    ),
    github["latest_name"].upper(),
    font=feed_repo_font,
    fill=WHITE,
)

line(
    draw,
    S(1240),
    T(561),
    S(1605),
    T(561),
    CYAN_DIM,
)

text_label(
    draw,
    S(1240),
    T(575),
    f"AUTHOR      {github['latest_author']}",
    8,
)

text_label(
    draw,
    S(1240),
    T(600),
    f"DATE        {github['latest_commit_date']}",
    8,
)

text_label(
    draw,
    S(1240),
    T(623),
    f"TIME        {github['latest_commit_time']} IST",
    8,
    GREEN,
)

line(
    draw,
    S(1240),
    T(645),
    S(1605),
    T(645),
    CYAN_DIM,
)

text_label(
    draw,
    S(1240),
    T(659),
    "ACCOUNT      CONNECTED",
    8,
    GREEN,
)

text_label(
    draw,
    S(1435),
    T(659),
    f"REPOS {github['repos']:02d}",
    8,
)

# Small decorative graph

graph_points = []

graph_pattern = [
    0,
    3,
    -2,
    4,
    1,
    -1,
    5,
    -3,
    2,
    1,
]

for i in range(65):

    x = (
        S(1435)
        + int(i * S(2.1))
    )

    y = (
        T(681)
        + T(
            graph_pattern[
                i % len(graph_pattern)
            ]
        )
    )

    graph_points.append(
        (x, y)
    )

if len(graph_points) > 1:

    draw.line(
        graph_points,
        fill=VIOLET_SOFT,
        width=1,
    )


# ============================================================
# 06 — MOTIVATION
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
    fill=GLASS,
    outline=VIOLET_SOFT,
)

corner_marks(
    draw,
    motivation_box,
)

text_label(
    draw,
    S(1690),
    T(72),
    "// MOTIVATION",
    9,
)

draw.text(
    (
        S(1690),
        T(112),
    ),
    "DISCIPLINE",
    font=font(
        17,
        bold=True,
    ),
    fill=WHITE,
)

draw.text(
    (
        S(1738),
        T(142),
    ),
    "TODAY",
    font=font(
        17,
        bold=True,
    ),
    fill=CYAN,
)

line(
    draw,
    S(1700),
    T(182),
    S(1865),
    T(182),
    CYAN_DIM,
)

draw.text(
    (
        S(1700),
        T(207),
    ),
    "FREEDOM",
    font=font(
        17,
        bold=True,
    ),
    fill=WHITE,
)

draw.text(
    (
        S(1726),
        T(237),
    ),
    "TOMORROW",
    font=font(
        17,
        bold=True,
    ),
    fill=VIOLET,
)

draw.ellipse(
    (
        S(1777),
        T(280),
        S(1787),
        T(290),
    ),
    outline=CYAN_SOFT,
    width=1,
)

line(
    draw,
    S(1705),
    T(285),
    S(1760),
    T(285),
    CYAN_DIM,
)

line(
    draw,
    S(1805),
    T(285),
    S(1860),
    T(285),
    VIOLET_SOFT,
)


# ============================================================
# 07 — MICRO HUD DETAILS
# ============================================================

text_label(
    draw,
    S(858),
    T(480),
    "FOCUS > EXECUTE > SUCCEED",
    7,
)

text_label(
    draw,
    S(1752),
    T(330),
    "SYS // PROFILE // ACTIVE",
    7,
)

text_label(
    draw,
    S(35),
    T(698),
    "NODE 01",
    7,
)

text_label(
    draw,
    S(95),
    T(698),
    "SECURE",
    7,
    GREEN,
)

text_label(
    draw,
    S(1810),
    T(25),
    "LIVE",
    7,
    GREEN,
)


# ============================================================
# COMPOSITE
# ============================================================

# Put glow underneath the HUD itself.
overlay = Image.alpha_composite(
    glow_layer,
    overlay,
)

result = Image.alpha_composite(
    base,
    overlay,
).convert("RGB")

result.save(
    OUTPUT_IMAGE,
    format="PNG",
    optimize=True,
)


# ============================================================
# ACTION LOG
# ============================================================

print("==============================================")
print("HUD GENERATED SUCCESSFULLY")
print("----------------------------------------------")
print(f"GitHub repositories : {github['repos']}")
print(f"GitHub followers    : {github['followers']}")
print(f"GitHub following    : {github['following']}")
print(f"Latest repository   : {github['latest_name']}")
print(f"Latest language     : {github['latest_language']}")
print(f"Latest commit SHA   : {github['latest_sha']}")
print(f"Latest commit author: {github['latest_author']}")
print(f"Latest commit date  : {github['latest_commit_date']}")
print(f"Latest commit time  : {github['latest_commit_time']} IST")
print("----------------------------------------------")
print("Normal live clock   : REMOVED")
print(f"Output              : {OUTPUT_IMAGE}")
print("==============================================")
