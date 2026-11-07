
import json
import html
import textwrap
import streamlit as st

from pathlib import Path
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


# ============================================================
# 1. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="My Data Science Study Planner",
    page_icon="🌷",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DAILY_DIR = DATA_DIR / "daily_records"
SYLLABUS_FILE = DATA_DIR / "syllabus.json"

START_DATE = date(2026, 11, 9)
TOTAL_DAYS = 100
IST = ZoneInfo("Asia/Kolkata")

TASKS = [
    ("learning", "9 AM – 12 PM",
     "Learn: {topic}"),

    ("practical", "1 PM – 4 PM",
     "Practical coding + class assignment related to today's topic"),

    ("github", "5 PM – 7 PM",
     "GitHub project: build / improve / document something related to this module"),

    ("revision", "7 PM – 9 PM",
     "Revise today's topic + solve MCQs + prepare interview questions")
]

COMPLETION_ITEMS = [
    "Learning",
    "Practical",
    "Assignment",
    "GitHub",
    "Revision"
]

RATINGS = ["Great", "Okay", "Need to catch up"]


# ============================================================
# 2. LOAD SYLLABUS
# ============================================================

def load_syllabus():

    if not SYLLABUS_FILE.exists():
        st.error("data/syllabus.json file nahi mili.")
        st.stop()

    with open(SYLLABUS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])

    if len(days) != TOTAL_DAYS:
        st.error(
            f"syllabus.json mein {len(days)} days hain. "
            "Exactly 100 days hone chahiye."
        )
        st.stop()

    return days


syllabus = load_syllabus()


# ============================================================
# 3. DATE FUNCTIONS
# ============================================================

def get_date(day_number):

    item = syllabus[day_number - 1]

    if item.get("date"):
        return date.fromisoformat(item["date"])

    current = START_DATE
    count = 1

    while count < day_number:
        current += timedelta(days=1)

        if current.weekday() != 6:
            count += 1

    return current


def get_today_day():

    today = datetime.now(IST).date()

    if today < START_DATE:
        return 1

    current_day = 1

    while current_day < TOTAL_DAYS:
        next_date = get_date(current_day + 1)

        if next_date <= today:
            current_day += 1
        else:
            break

    return current_day


TODAY = datetime.now(IST).date()
TODAY_DAY = get_today_day()


# ============================================================
# 4. DAILY JSON RECORDS
# ============================================================

def record_path(day_number):

    return DAILY_DIR / (
        f"day_{day_number:03d}_{get_date(day_number)}.json"
    )


def create_record(day):

    d = get_date(day["day"])

    return {
        "day": day["day"],
        "date": d.isoformat(),
        "module": day["module"],
        "topic": day["topic"],

        "tasks": {
            task[0]: False for task in TASKS
        },

        "completion": {
            item: False for item in COMPLETION_ITEMS
        },

        "understood": "",
        "doubts": "",
        "rating": "",
        "updated_at": None
    }


def save_record(record):

    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    path = record_path(record["day"])
    temp = path.with_suffix(".tmp")

    with open(temp, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=4, ensure_ascii=False)

    temp.replace(path)


def load_record(day):

    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    path = record_path(day["day"])

    if not path.exists():
        record = create_record(day)
        save_record(record)
        return record

    with open(path, "r", encoding="utf-8") as f:
        record = json.load(f)

    record.setdefault("tasks", {})
    record.setdefault("completion", {})
    record.setdefault("understood", "")
    record.setdefault("doubts", "")
    record.setdefault("rating", "")

    for task in TASKS:
        record["tasks"].setdefault(task[0], False)

    for item in COMPLETION_ITEMS:
        record["completion"].setdefault(item, False)

    return record


def prepare_all_records():

    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    for day in syllabus:

        path = record_path(day["day"])

        # Existing records are never overwritten.
        if not path.exists():
            save_record(create_record(day))


prepare_all_records()


# ============================================================
# 5. SESSION STATE
# ============================================================

if "selected_day" not in st.session_state:
    st.session_state.selected_day = TODAY_DAY

if "page" not in st.session_state:
    st.session_state.page = "Today's Planner"

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "last_saved" not in st.session_state:
    st.session_state.last_saved = None


# ============================================================
# 6. CSS — IMPORTANT: CSS IS INSIDE STYLE TAG
# ============================================================

LIGHT_CSS = """
.stApp {
    background: #fffaff;
    color: #24133f;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8f0ff, #fff0f5);
    border-right: 1px solid #eadcf8;
}

[data-testid="stSidebar"] * {
    color: #35205f;
}

h1, h2, h3 {
    color: #39205f;
}

"""

DARK_CSS = """
.stApp {
    background: #1e1728;
    color: #f7edff;
}

[data-testid="stSidebar"] {
    background: #281d35;
    border-right: 1px solid #59446d;
}

[data-testid="stSidebar"] * {
    color: #f7edff;
}

h1, h2, h3, p, label {
    color: #f7edff;
}

.stTextArea textarea,
.stTextInput input {
    background: #30233e !important;
    color: white !important;
}

[data-testid="stExpander"] {
    background: #30233e;
}

"""

css = DARK_CSS if st.session_state.theme == "Dark" else LIGHT_CSS

st.markdown(
    "<style>\n" + css + """

    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap'
    );

    body, .stApp {
        font-family: 'DM Sans', sans-serif;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        min-width: 280px;
        max-width: 280px;
    }

    /* Hero banner */

    .hero {
        height: 128px;
        width: 100%;
        border-radius: 20px;
        margin-bottom: 20px;
        padding: 15px 22px;
        box-sizing: border-box;

        display: flex;
        align-items: center;
        justify-content: space-between;

        border: 1px solid #ead6f4;

        background:
            radial-gradient(ellipse at 15% 90%, #e5d4f7 0%, transparent 35%),
            radial-gradient(ellipse at 85% 15%, #ffe2ed 0%, transparent 40%),
            linear-gradient(100deg, #f2e5ff, #fbe9f6, #fff0e8);

        overflow: hidden;
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(23px, 3vw, 38px);
        color: #67418b;
        font-style: italic;
        text-align: center;
        font-weight: 700;
    }

    .hero-subtitle {
        color: #51356f;
        text-align: center;
        font-size: 16px;
        margin-top: 5px;
    }

    .hero-decoration {
        font-size: 38px;
        white-space: nowrap;
    }

    /* Day header */

    .day-panel {
        border: 1px solid #e8d5f5;
        border-radius: 17px;
        background: linear-gradient(100deg, #fff, #fff9ff);
        padding: 20px;
        margin: 8px 0 18px 0;
    }

    .day-badge {
        background: linear-gradient(135deg, #ead7ff, #f5e5fb);
        color: #3c2164;
        padding: 15px 12px;
        border-radius: 14px;
        font-size: 30px;
        font-weight: 700;
        text-align: center;
    }

    .day-topic {
        color: #28144d;
        font-size: 19px;
        font-weight: 700;
    }

    /* Timetable */

    .table-wrap {
        border: 1px solid #d9c2ee;
        border-radius: 13px;
        overflow: hidden;
        background: white;
    }

    .table-head {
        background: #eadcf8;
        color: #34205e;
        font-weight: 700;
        padding: 12px 15px;
        border-right: 1px solid #d7c1ed;
    }

    .table-cell {
        padding: 13px 15px;
        color: #21143a;
        min-height: 48px;
        border-top: 1px solid #dfd0ee;
        border-right: 1px solid #dfd0ee;
        display: flex;
        align-items: center;
    }

    /* Notes cards */

    .note-heading {
        font-size: 19px;
        font-weight: 700;
        color: #54266e;
        margin-bottom: 9px;
    }

    .notes-card {
        background: linear-gradient(130deg, #fff0f7, #fceaf4);
        border: 1px solid #f2d9e9;
        border-radius: 17px;
        padding: 16px;
    }

    .doubts-card {
        background: linear-gradient(130deg, #fff5ed, #fff1e9);
        border: 1px solid #f3dfd0;
        border-radius: 17px;
        padding: 16px;
    }

    /* Completion area */

    .completion-panel {
        border: 1px solid #eadcf5;
        background: linear-gradient(100deg, #fbf5ff, #fff8fb);
        border-radius: 16px;
        padding: 15px;
        margin-top: 18px;
    }

    /* Buttons */

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 12px;
        min-height: 40px;
        font-weight: 600;
        border: 1px solid #dfc9ee;
    }

    div.stFormSubmitButton > button {
        background: linear-gradient(110deg, #a77bd0, #8860b8);
        color: white;
        border: none;
    }

    div.stFormSubmitButton > button:hover {
        background: #8056ae;
        color: white;
    }

    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #dfc9ee;
        background: white;
        color: #24133f;
    }

    div[data-testid="stProgress"] > div > div {
        background: #a77bd0;
    }

    @media(max-width: 700px) {
        [data-testid="stSidebar"] {
            min-width: 0;
            max-width: none;
        }

        .hero {
            height: 105px;
            padding: 10px;
        }

        .hero-title {
            font-size: 20px;
        }

        .hero-subtitle {
            font-size: 12px;
        }

        .hero-decoration {
            font-size: 22px;
        }

        .day-badge {
            font-size: 22px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 7. SIDEBAR
# ============================================================

with st.sidebar:

    # Planner title
    st.markdown(
        """
        <div style="text-align:center; padding:12px 0 20px 0;">
            <div style="font-size:42px;">💻</div>
            <div style="font-size:24px; font-weight:700;">
                My Data Science Planner ✨
            </div>
            <div style="font-size:14px; margin-top:8px;">
                100 Days of Data Science
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # Appearance
    st.radio(
        "🌗 Appearance",
        ["Light", "Dark"],
        key="theme",
        horizontal=True
    )

    st.divider()

    # Navigation
    pages = [
        "Today's Planner",
        "Calendar",
        "All Days",
        "My Progress",
        "My Notes",
        "Settings"
    ]

    page_icons = {
        "Today's Planner": "⌂",
        "Calendar": "▦",
        "All Days": "◇",
        "My Progress": "▥",
        "My Notes": "▤",
        "Settings": "⚙"
    }

    selected_page = st.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state.page),
        format_func=lambda x: f"{page_icons[x]}   {x}",
        label_visibility="collapsed"
    )

    st.session_state.page = selected_page

    st.divider()

    # Jump to any day
    selected_day = st.selectbox(
        "Jump to any day",
        range(1, TOTAL_DAYS + 1),
        index=st.session_state.selected_day - 1,
        format_func=lambda x: f"Day {x:02d} / 100"
    )

    st.session_state.selected_day = selected_day

    if st.button("🏠 Go to Today's Day", use_container_width=True):
        st.session_state.selected_day = TODAY_DAY
        st.session_state.page = "Today's Planner"
        st.rerun()

    st.divider()

    # Overall progress
    completed_days = 0

    for item in syllabus:
        saved = load_record(item)

        if all(
            saved["completion"].get(x, False)
            for x in COMPLETION_ITEMS
        ):
            completed_days += 1

    percentage = completed_days / TOTAL_DAYS

    st.markdown("### Overall Progress")
    st.write(f"{completed_days} / 100 days")
    st.progress(percentage)
    st.write(f"{percentage * 100:.0f}%")

    st.divider()

    # Planner date information
    with st.container(border=True):

        st.markdown("### 📅 Start Date")
        st.write("9 November 2026")

        st.markdown("### 🎯 End Date")
        st.write(
            get_date(100).strftime("%d %B %Y")
        )

        st.markdown("### 📚 Study Pattern")
        st.write("Monday – Saturday")
        st.write("(Sunday Off)")

        st.markdown("### 🕘 Daily Window")
        st.write("9:00 AM – 9:00 PM")

    # Decorative footer
    st.markdown(
        """
        <div style="text-align:center; font-size:27px; padding:20px;">
            🌿 🌷 🌿
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 8. MAIN HERO BANNER
# ============================================================

hero_html = """
<div class="hero"><div class="hero-decoration">🌿</div><div style="flex:1;"><div class="hero-title">My Data Science Study Planner</div><div class="hero-subtitle">Learn &nbsp; • &nbsp; Practice &nbsp; • &nbsp; Build &nbsp; • &nbsp; Revise &nbsp; • &nbsp; Grow ♡</div></div><div class="hero-decoration">☕ 📚 🌿</div></div>
"""

st.markdown(hero_html, unsafe_allow_html=True)

# ============================================================
# 9. TODAY'S PLANNER PAGE
# ============================================================

if st.session_state.page == "Today's Planner":

    day_number = st.session_state.selected_day
    day = syllabus[day_number - 1]
    record = load_record(day)
    study_date = get_date(day_number)

    day_col, info_col, nav_col = st.columns([1.1, 4.2, 2.4])

    with day_col:
        st.markdown(
            f'<div class="day-badge">DAY {day_number:02d}</div>',
            unsafe_allow_html=True
        )

    with info_col:

        st.write(f"▦  {study_date.strftime('%A, %d %B %Y')}")
        st.write(f"◇  {day['module']}")

        st.markdown(
            f'<div class="day-topic">{html.escape(day["topic"])}</div>',
            unsafe_allow_html=True
        )

    with nav_col:

        prev_col, next_col = st.columns(2)

        with prev_col:
            if st.button(
                "❮ Previous",
                disabled=day_number == 1,
                use_container_width=True
            ):
                st.session_state.selected_day -= 1
                st.rerun()

        with next_col:
            if st.button(
                "Next ❯",
                disabled=day_number == TOTAL_DAYS,
                use_container_width=True
            ):
                st.session_state.selected_day += 1
                st.rerun()

    st.write("")

    # --------------------------------------------------------
    # TIMETABLE
    # --------------------------------------------------------

    st.markdown(
        '<div style="font-size:20px;font-weight:700;color:#44266b;margin-bottom:10px;">',
        unsafe_allow_html=True
    )

    with st.container(border=True):

        head1, head2, head3 = st.columns([1.2, 4.8, 0.6])

        head1.markdown('<div class="table-head">Time</div>', unsafe_allow_html=True)
        head2.markdown('<div class="table-head">Today\'s work</div>', unsafe_allow_html=True)
        head3.markdown('<div class="table-head">Done</div>', unsafe_allow_html=True)

        timetable_values = {}

        for task_id, time_text, work_text in TASKS:

            c1, c2, c3 = st.columns([1.2, 4.8, 0.6])

            with c1:
                st.markdown(
                    f'<div class="table-cell">◷ &nbsp; {html.escape(time_text)}</div>',
                    unsafe_allow_html=True
                )

            with c2:

                work = work_text.replace("{topic}", day["topic"])

                st.markdown(
                    f'<div class="table-cell">{html.escape(work)}</div>',
                    unsafe_allow_html=True
                )

            with c3:

                timetable_values[task_id] = st.checkbox(
                    "Done",
                    value=record["tasks"].get(task_id, False),
                    key=f"schedule_{day_number}_{task_id}",
                    label_visibility="collapsed"
                )

    # --------------------------------------------------------
    # NOTES AND DOUBTS
    # --------------------------------------------------------

    st.write("")

    note_col, doubt_col = st.columns(2)

    with note_col:

        st.markdown(
            """
            <div class="note-heading">▤ &nbsp; What I understood today:</div>
            """,
            unsafe_allow_html=True
        )

        understood = st.text_area(
            "Learning notes",
            value=record.get("understood", ""),
            placeholder="Write your learning notes here...",
            height=100,
            label_visibility="collapsed",
            key=f"understood_{day_number}"
        )

    with doubt_col:

        st.markdown(
            """
            <div class="note-heading">ⓘ &nbsp; Doubts / topics to revisit:</div>
            """,
            unsafe_allow_html=True
        )

        doubts = st.text_area(
            "Doubts",
            value=record.get("doubts", ""),
            placeholder="Write your doubts or topics here...",
            height=100,
            label_visibility="collapsed",
            key=f"doubts_{day_number}"
        )


    # --------------------------------------------------------
    # DAILY COMPLETION, RATING AND PENDING TASKS
    # --------------------------------------------------------

    st.write("")

    completion_col, rating_col = st.columns(2, gap="medium")

    # LEFT CARD: DAILY COMPLETION
    with completion_col:

        with st.container(border=True):

            st.markdown("### Daily completion")

            completion_cols = st.columns(3)

            completion_values = {}

            for i, item in enumerate(COMPLETION_ITEMS):

                with completion_cols[i % 3]:

                    completion_values[item] = st.checkbox(
                        item,
                        value=record["completion"].get(item, False),
                        key=f"completion_{day_number}_{item}"
                    )


    # RIGHT CARD: DAILY RATING
    with rating_col:

        with st.container(border=True):

            st.markdown("### How was today?")

            ratings = ["Great", "Okay", "Need to catch up"]

            rating = st.radio(
                "Daily rating",
                ratings,
                index=(
                    ratings.index(record.get("rating"))
                    if record.get("rating") in ratings
                    else None
                ),
                key=f"rating_{day_number}",
                label_visibility="collapsed"
            )



    # --------------------------------------------------------
    # PENDING TASKS CARD
    # --------------------------------------------------------

    st.write("")

    TASK_LABELS = {
        "learning": "9 AM – 12 PM | Learn today's topic",
        "practical": "1 PM – 4 PM | Practical coding + class assignment",
        "github": "5 PM – 7 PM | GitHub project work",
        "revision": "7 PM – 9 PM | Revision + MCQs + interview preparation"
    }

    with st.container(border=True):

        st.markdown("### 📌 Pending Tasks")

        pending_today_col, pending_previous_col = st.columns(2)

        # TODAY'S PENDING
        with pending_today_col:

            st.markdown("**Today's Pending**")

            today_pending = []

            for task_key, task_done in timetable_values.items():

                if not task_done:

                    label = TASK_LABELS.get(
                        task_key.lower(),
                        task_key.replace("_", " ").title()
                    )

                    today_pending.append(label)

            if today_pending:

                for task in today_pending:
                    st.markdown(f"- {task}")

            else:
                st.success("All today's tasks completed! 🎉")

        # PREVIOUS DAYS PENDING
        with pending_previous_col:

            st.markdown("**Previous Days Pending**")

            previous_pending = []

            for item in syllabus:

                previous_day = item["day"]

                if previous_day >= day_number:
                    continue

                previous_record = load_record(item)
                previous_tasks = previous_record.get("tasks", {})

                for task_key, task_done in previous_tasks.items():

                    if not task_done:

                        label = TASK_LABELS.get(
                            task_key.lower(),
                            task_key.replace("_", " ").title()
                        )

                        previous_pending.append(
                            f"Day {previous_day:02d} — {label}"
                        )

            if previous_pending:

                for task in previous_pending:
                    st.markdown(f"- {task}")

            else:
                st.success("No previous pending tasks! 💜")




































# --------------------------------------------------------
# SAVE
# --------------------------------------------------------

    st.write("")

    save_col, status_col = st.columns([1, 1.3])

    with save_col:

        if st.button(
            "💾  Save Today's Progress",
            use_container_width=True,
            key=f"save_progress_{day_number}"
        ):

            record["tasks"] = timetable_values
            record["completion"] = completion_values
            record["understood"] = understood
            record["doubts"] = doubts
            record["rating"] = rating or ""
            record["updated_at"] = datetime.now(IST).isoformat()

            save_record(record)

            st.rerun()


    with status_col:

        # Read saved timestamp from this day's JSON file
        saved_record = load_record(
            next(item for item in syllabus if item["day"] == day_number)
        )

        saved_time = saved_record.get("updated_at")

        if saved_time:

            try:
                saved_datetime = datetime.fromisoformat(saved_time)

                formatted_time = saved_datetime.astimezone(IST).strftime(
                    "%d %b %Y, %I:%M %p"
                )

                st.success("✓ Progress Saved Successfully! 💜")
                st.caption(f"Last saved: {formatted_time}")

            except (ValueError, TypeError):
                st.success("✓ Progress Saved Successfully! 💜")

        else:
            st.info("Your progress is not saved yet.")


# ============================================================
# 10. CALENDAR PAGE
# ============================================================

elif st.session_state.page == "Calendar":

    st.markdown("## 📅 Study Calendar")

    search = st.text_input(
        "Search by day, module or topic"
    )

    for item in syllabus:

        number = item["day"]
        d = get_date(number)
        saved = load_record(item)

        searchable = (
            f"{number} {item['module']} {item['topic']} {d}"
        ).casefold()

        if search and search.casefold() not in searchable:
            continue

        # Check the 4 timetable tasks
        tasks = saved.get("tasks", {})

        total_tasks = len(tasks)
        completed_tasks = sum(
            1 for value in tasks.values() if value
        )

        if total_tasks > 0 and completed_tasks == total_tasks:
            status = "✅ Completed"

        elif completed_tasks > 0:
            status = "🔄 In Progress"

        else:
            status = "📝 Pending"

        with st.expander(
            f"Day {number:02d} — "
            f"{d.strftime('%a, %d %b %Y')} — {status}"
        ):

            st.write(item["module"])
            st.write(item["topic"])

            st.caption(
                f"Timetable progress: {completed_tasks}/{total_tasks}"
            )

            if st.button(
                f"Open Day {number:02d}",
                key=f"calendar_{number}"
            ):
                st.session_state.selected_day = number
                st.session_state.page = "Today's Planner"
                st.rerun()

# ============================================================
# 11. ALL DAYS PAGE
# ============================================================

elif st.session_state.page == "All Days":

    st.markdown("## 📚 All 100 Study Days")

    search = st.text_input("Search module or topic")

    for item in syllabus:

        number = item["day"]

        if search and search.casefold() not in (
            item["module"] + " " + item["topic"]
        ).casefold():
            continue

        with st.expander(
            f"DAY {number:02d} — {item['module']}"
        ):

            st.write(get_date(number).strftime("%A, %d %B %Y"))
            st.write(item["topic"])

            if st.button(
                f"Open Day {number:02d}",
                key=f"all_{number}"
            ):
                st.session_state.selected_day = number
                st.session_state.page = "Today's Planner"
                st.rerun()



# ============================================================
# 12. PROGRESS PAGE
# ============================================================

elif st.session_state.page == "My Progress":

    st.markdown("## 📊 My Progress")

    completed = 0
    partial = 0

    for item in syllabus:

        saved = load_record(item)
        tasks = saved.get("tasks", {})

        completed_tasks = sum(
            bool(value) for value in tasks.values()
        )

        if completed_tasks == 4:
            completed += 1
        elif completed_tasks > 0:
            partial += 1

    pending = TOTAL_DAYS - completed - partial

    st.metric("Completed days", f"{completed}/100")
    st.progress(completed / TOTAL_DAYS)

    c1, c2, c3 = st.columns(3)

    c1.metric("Completed", completed)
    c2.metric("Partially done", partial)
    c3.metric("Pending", pending)


# ============================================================
# 13. NOTES PAGE
# ============================================================

elif st.session_state.page == "My Notes":

    st.markdown("## 📝 My Notes")

    found = False

    for item in syllabus:

        saved = load_record(item)

        if saved["understood"] or saved["doubts"]:

            found = True

            with st.expander(
                f"Day {item['day']:02d} — {item['topic']}"
            ):

                st.markdown("**What I understood:**")
                st.write(saved["understood"] or "No notes")

                st.markdown("**Doubts:**")
                st.write(saved["doubts"] or "No doubts")

    if not found:
        st.info("Your saved notes and doubts will appear here.")


# ============================================================
# 14. SETTINGS PAGE
# ============================================================

elif st.session_state.page == "Settings":

    st.markdown("## ⚙️ Settings")

    st.write("Start date: 9 November 2026")
    st.write(
        f"End date: {get_date(100).strftime('%d %B %Y')}"
    )
    st.write("Study days: Monday to Saturday")
    st.write("Sunday: Rest day")
    st.write("Timezone: India Standard Time")

    st.info(
        "Every study day has its own JSON file. "
        "Saving one day updates only that day's file. "
        "Previous days remain editable."
    )


# ============================================================
# 15. FOOTER
# ============================================================

st.markdown(
    """
    <hr>
    <div style="
        text-align:center;
        color:#9988aa;
        padding:15px;
        font-size:14px;
    ">
        My Data Science Study Planner 🌷
        <br>
        Consistency over perfection.
        Learn it, practise it, write it, build it.
    </div>
    """,
    unsafe_allow_html=True
)
