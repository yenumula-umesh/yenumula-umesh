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
# PERSONAL INFORMATION
# ============================================================

NAME = "UMESH YENUMULA"
TITLE = "DATA ANALYST  ×  AI ENGINEER"
EDUCATION = "BS IN DATA SCIENCE & APPLICATIONS"
COLLEGE = "IIT MADRAS"

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
VIOLET = (155, 100, 255, 210)
VIOLET_SOFT = (155, 100, 255, 105)

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
        return ImageFont.truetype(
            path,
            size=size,
        )

    return ImageFont.load_default()


# ============================================================
# HELPERS
# ============================================================

def rounded_hud(
    draw,
    box,
    radius=16,
    fill=DARK_SOFT,
    outline=CYAN_SOFT,
    width=1,
):
    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def clipped_panel(
    draw,
    box,
    cut=16,
    fill=DARK_SOFT,
    outline=CYAN_SOFT,
    width=1,
):
    """
    Transparent futuristic panel with clipped corners.
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


def line(
    draw,
    x1,
    y1,
    x2,
    y2,
    fill=CYAN_DIM,
    width=1,
):
    draw.line(
        (x1, y1, x2, y2),
        fill=fill,
        width=width,
    )


def label(
    draw,
    x,
    y,
    text_value,
    size=12,
    fill=WHITE_DIM,
):
    draw.text(
        (x, y),
        str(text_value).upper(),
        font=font(size),
        fill=fill,
    )


def title(
    draw,
    x,
    y,
    text_value,
    size=26,
    fill=CYAN,
):
    draw.text(
        (x, y),
        str(text_value),
        font=font(
            size,
            bold=True,
        ),
        fill=fill,
    )


def draw_corner_marks(
    draw,
    box,
    length=18,
):
    x1, y1, x2, y2 = box

    # top left
    line(
        draw,
        x1,
        y1 + length,
        x1,
        y1,
        CYAN_SOFT,
    )

    line(
        draw,
        x1,
        y1,
        x1 + length,
        y1,
        CYAN_SOFT,
    )

    # top right
    line(
        draw,
        x2 - length,
        y1,
        x2,
        y1,
        VIOLET_SOFT,
    )

    line(
        draw,
        x2,
        y1,
        x2,
        y1 + length,
        VIOLET_SOFT,
    )

    # bottom left
    line(
        draw,
        x1,
        y2 - length,
        x1,
        y2,
        VIOLET_SOFT,
    )

    line(
        draw,
        x1,
        y2,
        x1 + length,
        y2,
        VIOLET_SOFT,
    )

    # bottom right
    line(
        draw,
        x2 - length,
        y2,
        x2,
        y2,
        CYAN_SOFT,
    )

    line(
        draw,
        x2,
        y2 - length,
        x2,
        y2,
        CYAN_SOFT,
    )


def glow_panel(
    base,
    box,
    blur=8,
):
    glow = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0),
    )

    gd = ImageDraw.Draw(
        glow
    )

    gd.rounded_rectangle(
        box,
        radius=15,
        outline=CYAN,
        width=3,
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(
            blur
        )
    )

    base.alpha_composite(
        glow
    )


def fitted_font(
    draw,
    value,
    max_width,
    start_size,
    minimum_size=7,
    bold=False,
):
    """
    Reduce font size until the text fits the available width.
    """

    size = start_size

    while size > minimum_size:

        current_font = font(
            size,
            bold=bold,
        )

        bbox = draw.textbbox(
            (0, 0),
            str(value),
            font=current_font,
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:
            return current_font

        size -= 1

    return font(
        minimum_size,
        bold=bold,
    )


def wrap_text(
    draw,
    value,
    max_width,
    text_font,
    max_lines=3,
):
    words = str(value).split()

    lines = []
    current = ""

    for word in words:

        candidate = (
            f"{current} {word}".strip()
        )

        bbox = draw.textbbox(
            (0, 0),
            candidate,
            font=text_font,
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:

            current = candidate

        else:

            if current:
                lines.append(
                    current
                )

            current = word

            if len(lines) >= max_lines:
                break

    if current and len(lines) < max_lines:
        lines.append(current)

    return lines[:max_lines]


# ============================================================
# GITHUB API
# ============================================================

GITHUB_HEADERS = {
    "User-Agent": "umesh-github-profile-hud",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def github_get(endpoint):
    url = (
        "https://api.github.com"
        + endpoint
    )

    request = urllib.request.Request(
        url,
        headers=GITHUB_HEADERS,
        method="GET",
    )

    with urllib.request.urlopen(
        request,
        timeout=15,
    ) as response:

        return json.loads(
            response.read().decode(
                "utf-8"
            )
        )


# ============================================================
# GITHUB DATA
# ============================================================

def get_github_data():

    fallback = {
        "repos": 0,

        "recent_repos": [],

        "latest_name": "N/A",
        "latest_description": "N/A",
        "latest_language": "N/A",

        "latest_commit_sha": "N/A",
        "latest_commit_author": "N/A",

        "latest_commit_date": "N/A",
        "latest_commit_time": "N/A",

        "latest_visibility": "N/A",
        "latest_status": "N/A",
    }

    try:

        # ----------------------------------------------------
        # USER PROFILE
        # ----------------------------------------------------

        user = github_get(
            f"/users/{GITHUB_USERNAME}"
        )

        total_repos = int(
            user.get(
                "public_repos",
                0,
            )
        )

        # ----------------------------------------------------
        # PUBLIC REPOSITORIES
        #
        # Sorted by latest push.
        # ----------------------------------------------------

        repositories = github_get(
            f"/users/{GITHUB_USERNAME}/repos"
            "?type=owner"
            "&sort=pushed"
            "&direction=desc"
            "&per_page=30"
        )

        # ----------------------------------------------------
        # REMOVE PROFILE REPOSITORY
        #
        # The profile repo itself gets changed by the workflow.
        # If we didn't remove it, it could constantly appear as
        # the latest project.
        # ----------------------------------------------------

        project_repositories = []

        for repo in repositories:

            repo_name = repo.get(
                "name",
                "",
            )

            is_profile_repo = (
                repo_name.lower()
                == GITHUB_USERNAME.lower()
            )

            is_fork = repo.get(
                "fork",
                False,
            )

            if is_profile_repo:
                continue

            if is_fork:
                continue

            project_repositories.append(
                repo
            )

        # ----------------------------------------------------
        # ONLY FIVE REPOSITORIES
        # ----------------------------------------------------

        recent_repos = [
            repo.get(
                "name",
                "UNKNOWN",
            )
            for repo in project_repositories[:5]
        ]

        result = {
            "repos": total_repos,

            "recent_repos": recent_repos,

            "latest_name": "N/A",
            "latest_description": "N/A",
            "latest_language": "N/A",

            "latest_commit_sha": "N/A",
            "latest_commit_author": "N/A",

            "latest_commit_date": "N/A",
            "latest_commit_time": "N/A",

            "latest_visibility": "N/A",
            "latest_status": "N/A",
        }

        # ----------------------------------------------------
        # LATEST REPOSITORY
        # ----------------------------------------------------

        if not project_repositories:
            return result

        latest = project_repositories[0]

        latest_name = latest.get(
            "name",
            "UNKNOWN",
        )

        latest_description = (
            latest.get(
                "description"
            )
            or "No description available."
        )

        latest_language = (
            latest.get(
                "language"
            )
            or "N/A"
        )

        result["latest_name"] = (
            latest_name
        )

        result["latest_description"] = (
            latest_description
        )

        result["latest_language"] = (
            latest_language
        )

        # ----------------------------------------------------
        # VISIBILITY
        #
        # Since we're looking through public user repos,
        # this will normally be PUBLIC.
        # ----------------------------------------------------

        if latest.get(
            "private",
            False,
        ):

            result[
                "latest_visibility"
            ] = "PRIVATE"

        else:

            result[
                "latest_visibility"
            ] = "PUBLIC"

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if latest.get(
            "archived",
            False,
        ):

            result[
                "latest_status"
            ] = "ARCHIVED"

        else:

            result[
                "latest_status"
            ] = "ACTIVE"

        # ----------------------------------------------------
        # LATEST COMMIT
        # ----------------------------------------------------

        try:

            commits = github_get(
                f"/repos/"
                f"{GITHUB_USERNAME}/"
                f"{latest_name}"
                "/commits?per_page=1"
            )

            if commits:

                commit = commits[0]

                result[
                    "latest_commit_sha"
                ] = (
                    commit.get(
                        "sha",
                        "N/A",
                    )[:8]
                )

                commit_data = (
                    commit.get(
                        "commit",
                        {},
                    )
                )

                author_data = (
                    commit_data.get(
                        "author",
                        {},
                    )
                )

                result[
                    "latest_commit_author"
                ] = (
                    author_data.get(
                        "name",
                        "UNKNOWN",
                    )
                )

                timestamp = (
                    author_data.get(
                        "date"
                    )
                )

                if timestamp:

                    parsed = (
                        datetime
                        .fromisoformat(
                            timestamp.replace(
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

                    result[
                        "latest_commit_date"
                    ] = (
                        ist.strftime(
                            "%d %b %Y"
                        ).upper()
                    )

                    result[
                        "latest_commit_time"
                    ] = (
                        ist.strftime(
                            "%H:%M"
                        )
                    )

        except Exception as commit_error:

            print(
                "Commit lookup warning:",
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
# LOAD IMAGE
# ============================================================

if not INPUT_IMAGE.exists():

    raise FileNotFoundError(
        f"Could not find hero.png at: "
        f"{INPUT_IMAGE}"
    )


base = Image.open(
    INPUT_IMAGE
).convert("RGBA")

WIDTH, HEIGHT = base.size

# ============================================================
# SCALE
# ============================================================

SX = WIDTH / 1920
SY = HEIGHT / 768


def S(x):
    return int(x * SX)


def T(y):
    return int(y * SY)


# ============================================================
# DRAWING LAYER
# ============================================================

overlay = Image.new(
    "RGBA",
    (WIDTH, HEIGHT),
    (0, 0, 0, 0),
)

draw = ImageDraw.Draw(
    overlay
)


# ============================================================
# GITHUB
# ============================================================

github = get_github_data()


# ============================================================
# 01 — SYSTEM STATUS
# LEFT SIDE
#
# CHANGED:
# Normal clock/date removed.
# Followers/network/API fields removed.
# Replaced with maximum 5 recent repositories.
# ============================================================

system_box = (
    S(18),
    T(48),
    S(325),
    T(405),
)

glow_panel(
    overlay,
    system_box,
)

clipped_panel(
    draw,
    system_box,
    cut=S(14),
    fill=DARK_SOFT,
    outline=CYAN_SOFT,
)

draw_corner_marks(
    draw,
    system_box,
)

label(
    draw,
    S(38),
    T(72),
    "// SYSTEM STATUS",
    11,
)

title(
    draw,
    S(38),
    T(97),
    "OPERATIONAL",
    24,
)

# online indicator

draw.ellipse(
    (
        S(286),
        T(99),
        S(296),
        T(109),
    ),
    fill=GREEN,
)

label(
    draw,
    S(38),
    T(136),
    "SYSTEM ONLINE",
    9,
    GREEN,
)

# decorative signal waveform
wave_x = S(38)
wave_y = T(168)

points = []

wave_pattern = [
    0,
    -3,
    2,
    -1,
    5,
    -2,
    1,
    0,
    3,
]

for i in range(145):

    px = (
        wave_x
        + S(i)
    )

    py = (
        wave_y
        + T(
            wave_pattern[
                i % len(
                    wave_pattern
                )
            ]
        )
    )

    points.append(
        (px, py)
    )

if len(points) > 1:

    draw.line(
        points,
        fill=CYAN_SOFT,
        width=1,
    )

line(
    draw,
    S(38),
    T(188),
    S(300),
    T(188),
    CYAN_DIM,
)

# ------------------------------------------------------------
# RECENT REPOSITORIES
# MAXIMUM FIVE
# ------------------------------------------------------------

label(
    draw,
    S(38),
    T(207),
    "// RECENT REPOSITORIES",
    9,
)

recent_repos = github.get(
    "recent_repos",
    []
)[:5]

repo_y = 232

for index, repo_name in enumerate(
    recent_repos
):

    # number
    number_color = (
        CYAN
        if index % 2 == 0
        else VIOLET
    )

    label(
        draw,
        S(38),
        T(repo_y),
        f"{index + 1:02d}",
        8,
        number_color,
    )

    # repository name
    repo_font = fitted_font(
        draw,
        repo_name.upper(),
        S(225),
        9,
        7,
        bold=True,
    )

    draw.text(
        (
            S(70),
            T(repo_y),
        ),
        repo_name.upper(),
        font=repo_font,
        fill=WHITE,
    )

    line(
        draw,
        S(70),
        T(repo_y + 18),
        S(298),
        T(repo_y + 18),
        (65, 190, 255, 35),
    )

    repo_y += 28


if not recent_repos:

    label(
        draw,
        S(38),
        T(232),
        "NO PUBLIC PROJECTS",
        8,
        WHITE_DIM,
    )


# ============================================================
# 02 — MODULES / SKILLS
# KEEP EXISTING STRUCTURE
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
    outline=CYAN_SOFT,
)

draw_corner_marks(
    draw,
    modules_box,
)

label(
    draw,
    S(38),
    T(442),
    "// SKILL MATRIX",
    11,
)

skill_y = 470

for i, skill in enumerate(
    SKILLS[:7]
):

    accent = (
        CYAN_SOFT
        if i % 2 == 0
        else VIOLET_SOFT
    )

    draw.ellipse(
        (
            S(40),
            T(skill_y + 4),
            S(46),
            T(skill_y + 10),
        ),
        outline=accent,
        width=1,
    )

    skill_font = fitted_font(
        draw,
        skill,
        S(220),
        10,
        7,
    )

    draw.text(
        (
            S(56),
            T(skill_y),
        ),
        skill,
        font=skill_font,
        fill=WHITE,
    )

    line(
        draw,
        S(56),
        T(skill_y + 21),
        S(296),
        T(skill_y + 21),
        (65, 190, 255, 40),
    )

    skill_y += 30


# ============================================================
# 03 — SESSION
# UNCHANGED
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
    outline=CYAN_SOFT,
)

draw_corner_marks(
    draw,
    session_box,
)

label(
    draw,
    S(868),
    T(556),
    "// SESSION",
    10,
)

label(
    draw,
    S(868),
    T(582),
    "USER",
    9,
)

session_user_font = fitted_font(
    draw,
    "UMESH_YENUMULA",
    S(150),
    10,
    7,
    bold=True,
)

draw.text(
    (
        S(940),
        T(580),
    ),
    "UMESH_YENUMULA",
    font=session_user_font,
    fill=WHITE,
)

label(
    draw,
    S(868),
    T(608),
    "IDENTITY",
    9,
)

session_identity_font = fitted_font(
    draw,
    TITLE,
    S(150),
    9,
    7,
)

draw.text(
    (
        S(940),
        T(606),
    ),
    TITLE,
    font=session_identity_font,
    fill=CYAN,
)

label(
    draw,
    S(868),
    T(634),
    "EDUCATION",
    9,
)

draw.text(
    (
        S(940),
        T(632),
    ),
    COLLEGE,
    font=font(
        10,
        bold=True,
    ),
    fill=WHITE,
)

label(
    draw,
    S(868),
    T(659),
    "SESSION",
    9,
)

draw.text(
    (
        S(940),
        T(657),
    ),
    "ACTIVE / PUBLIC",
    font=font(
        9,
        bold=True,
    ),
    fill=GREEN,
)

# decorative activity bars remain unchanged

for i in range(9):

    height = (
        4
        + ((i * 7) % 15)
    )

    draw.rectangle(
        (
            S(
                865
                + i * 19
            ),
            T(
                688
                - height
            ),
            S(
                874
                + i * 19
            ),
            T(688),
        ),
        fill=CYAN_SOFT,
    )


# ============================================================
# 04 — PROFILE / IDENTITY
# KEEP EXISTING STRUCTURE
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
    outline=CYAN_SOFT,
)

draw_corner_marks(
    draw,
    profile_box,
)

label(
    draw,
    S(1220),
    T(52),
    "// OPERATOR PROFILE",
    11,
)

title(
    draw,
    S(1220),
    T(79),
    NAME,
    25,
)

draw.text(
    (
        S(1220),
        T(116),
    ),
    TITLE,
    font=font(
        15,
        bold=True,
    ),
    fill=CYAN,
)

line(
    draw,
    S(1220),
    T(148),
    S(1625),
    T(148),
    CYAN_DIM,
)

profile_education = (
    f"{EDUCATION}"
    f"  //  "
    f"{COLLEGE}"
)

education_font = fitted_font(
    draw,
    profile_education,
    S(405),
    10,
    7,
)

draw.text(
    (
        S(1220),
        T(163),
    ),
    profile_education,
    font=education_font,
    fill=WHITE_DIM,
)


# ============================================================
# 05 — PUBLIC SIGNAL
# RIGHT / LOWER
#
# ONLY:
# - Latest repo name
# - Last commit date/time
# - Visibility
# - Status
# - Total repos
# ============================================================

feed_box = (
    S(1215),
    T(435),
    S(1635),
    T(685),
)

glow_panel(
    overlay,
    feed_box,
)

clipped_panel(
    draw,
    feed_box,
    cut=S(16),
    fill=DARK_SOFT,
    outline=CYAN_SOFT,
)

draw_corner_marks(
    draw,
    feed_box,
)

label(
    draw,
    S(1240),
    T(457),
    "// PUBLIC SIGNAL",
    11,
)

signal_rows = [
    (
        "LATEST REPO",
        github.get(
            "latest_name",
            "N/A",
        ),
        CYAN,
    ),

    (
        "LAST COMMIT",
        (
            f"{github.get('latest_commit_date', 'N/A')}"
            f" // "
            f"{github.get('latest_commit_time', 'N/A')}"
            f" IST"
        ),
        WHITE,
    ),

    (
        "VISIBILITY",
        github.get(
            "latest_visibility",
            "N/A",
        ),
        GREEN,
    ),

    (
        "STATUS",
        github.get(
            "latest_status",
            "N/A",
        ),
        GREEN,
    ),

    (
        "TOTAL REPOS",
        str(
            github.get(
                "repos",
                0,
            )
        ).zfill(2),
        WHITE,
    ),
]

signal_y = 490

for key, value, value_color in signal_rows:

    label(
        draw,
        S(1240),
        T(signal_y),
        key,
        8,
    )

    value_font = fitted_font(
        draw,
        str(value).upper(),
        S(235),
        9,
        7,
        bold=(
            key in {
                "LATEST REPO",
                "STATUS",
            }
        ),
    )

    draw.text(
        (
            S(1350),
            T(signal_y - 1),
        ),
        str(value).upper(),
        font=value_font,
        fill=value_color,
    )

    line(
        draw,
        S(1240),
        T(signal_y + 21),
        S(1605),
        T(signal_y + 21),
        (65, 190, 255, 35),
    )

    signal_y += 35


# ============================================================
# 06 — MOTIVATION
# KEEP EXISTING STRUCTURE
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
    outline=CYAN_SOFT,
)

draw_corner_marks(
    draw,
    motivation_box,
)

label(
    draw,
    S(1690),
    T(72),
    "// MOTIVATION",
    10,
)

draw.text(
    (
        S(1690),
        T(115),
    ),
    "DISCIPLINE",
    font=font(
        19,
        bold=True,
    ),
    fill=WHITE,
)

draw.text(
    (
        S(1737),
        T(145),
    ),
    "TODAY",
    font=font(
        19,
        bold=True,
    ),
    fill=WHITE,
)

line(
    draw,
    S(1700),
    T(185),
    S(1865),
    T(185),
    CYAN_DIM,
)

draw.text(
    (
        S(1700),
        T(208),
    ),
    "FREEDOM",
    font=font(
        19,
        bold=True,
    ),
    fill=WHITE,
)

draw.text(
    (
        S(1730),
        T(238),
    ),
    "TOMORROW",
    font=font(
        19,
        bold=True,
    ),
    fill=WHITE,
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
    CYAN_DIM,
)


# ============================================================
# 07 — MICRO HUD DETAILS
# KEEP EXISTING STRUCTURE
# ============================================================

line(
    draw,
    S(858),
    T(503),
    S(1050),
    T(503),
    CYAN_DIM,
)

label(
    draw,
    S(870),
    T(481),
    "FOCUS  >  EXECUTE  >  SUCCEED",
    9,
)

label(
    draw,
    S(1750),
    T(332),
    "SYS // PROFILE // ACTIVE",
    8,
)

label(
    draw,
    S(35),
    T(698),
    "NODE 01",
    8,
)

label(
    draw,
    S(95),
    T(698),
    "SECURE",
    8,
    GREEN,
)

label(
    draw,
    S(1810),
    T(25),
    "LIVE",
    8,
    GREEN,
)


# ============================================================
# COMPOSITE
# ============================================================

result = Image.alpha_composite(
    base,
    overlay,
)

result = result.convert(
    "RGB"
)

result.save(
    OUTPUT_IMAGE,
    format="PNG",
    quality=95,
)


# ============================================================
# ACTION LOG
# ============================================================

print("==============================================")
print("HUD GENERATED SUCCESSFULLY")
print("----------------------------------------------")
print(
    f"Total public repos : "
    f"{github['repos']}"
)
print(
    f"Latest repository  : "
    f"{github['latest_name']}"
)
print(
    f"Latest commit SHA  : "
    f"{github['latest_commit_sha']}"
)
print(
    f"Commit author      : "
    f"{github['latest_commit_author']}"
)
print(
    f"Commit date        : "
    f"{github['latest_commit_date']}"
)
print(
    f"Commit time IST    : "
    f"{github['latest_commit_time']}"
)
print(
    f"Visibility         : "
    f"{github['latest_visibility']}"
)
print(
    f"Status             : "
    f"{github['latest_status']}"
)
print("----------------------------------------------")
print("Recent repositories:")

for index, repo in enumerate(
    github.get(
        "recent_repos",
        [],
    ),
    1,
):
    print(
        f"  {index}. {repo}"
    )

print("----------------------------------------------")
print("Normal clock/date   : REMOVED")
print("Followers/following : REMOVED")
print("Network/API signal  : REMOVED")
print(f"Output              : {OUTPUT_IMAGE}")
print("==============================================")
