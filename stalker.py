"""
LeetCode Public Account Reporter
================================

Periodically fetches a PUBLIC LeetCode profile and prints an extensive
account report every 250 seconds.

It also:
- Detects changes since the previous report
- Shows solved counts by difficulty
- Shows ranking and reputation
- Shows recent accepted submissions
- Shows languages used in recent accepted submissions
- Shows activity timing
- Sends a Windows notification when meaningful changes are detected
- Stores only a small JSON snapshot locally

No LeetCode login, password, cookies, Selenium, or browser is required.

Install:
    pip install requests winotify

Run:
    python stalker.py

Change the monitored account:
    USERNAME = "TanushriSapate"
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

try:
    from winotify import Notification
except ImportError:
    Notification = None


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = "TanushriSapate"

# Full account report interval.
REPORT_INTERVAL = 250  # seconds

# HTTP timeout.
REQUEST_TIMEOUT = 20

# Number of recent accepted submissions to request.
RECENT_SUBMISSIONS_LIMIT = 20

STATE_FILE = Path("leetcode_state.json")

GRAPHQL_URL = "https://leetcode.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0 Safari/537.36"
    ),
}


# ============================================================
# GRAPHQL
# ============================================================

QUERY = """
query userProfile($username: String!, $limit: Int!) {
    matchedUser(username: $username) {
        username

        profile {
            realName
            aboutMe
            userAvatar
            ranking
            reputation
            websites
            countryName
            company
            school
            skillTags
            starRating
        }

        submitStats {
            acSubmissionNum {
                difficulty
                count
                submissions
            }

            totalSubmissionNum {
                difficulty
                count
                submissions
            }
        }

        badges {
            id
            displayName
            icon
            creationDate
        }

        contributions {
            points
            questionCount
            testcaseCount
        }

        submissionCalendar

        languageProblemCount {
            languageName
            problemsSolved
        }
    }

    recentAcSubmissionList(
        username: $username
        limit: $limit
    ) {
        title
        titleSlug
        timestamp
        statusDisplay
        lang
    }
}
"""


# ============================================================
# UTILITIES
# ============================================================

def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def format_number(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "N/A"


def format_timestamp(timestamp: Any) -> str:
    """
    Convert a Unix timestamp to local-readable time.
    """
    try:
        dt = datetime.fromtimestamp(
            int(timestamp),
            tz=timezone.utc,
        ).astimezone()

        return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    except (TypeError, ValueError, OSError):
        return "Unknown time"


def relative_time(timestamp: Any) -> str:
    """
    Return a compact 'time ago' representation.
    """
    try:
        then = datetime.fromtimestamp(
            int(timestamp),
            tz=timezone.utc,
        )

        now = datetime.now(timezone.utc)
        seconds = max(0, int((now - then).total_seconds()))

        if seconds < 60:
            return f"{seconds}s ago"

        minutes = seconds // 60

        if minutes < 60:
            return f"{minutes}m ago"

        hours = minutes // 60

        if hours < 24:
            return f"{hours}h ago"

        days = hours // 24

        return f"{days}d ago"

    except (TypeError, ValueError, OSError):
        return "unknown"


def shorten(text: Any, length: int = 80) -> str:
    if text is None:
        return ""

    text = " ".join(str(text).split())

    if len(text) <= length:
        return text

    return text[: length - 3] + "..."


# ============================================================
# NOTIFICATION
# ============================================================

def notify(title: str, message: str) -> None:
    """
    Send a Windows notification when winotify is available.
    """

    if Notification is None:
        return

    try:
        Notification(
            app_id="LeetCode Account Reporter",
            title=title,
            msg=message,
        ).show()
    except Exception as exc:
        print(f"[!] Notification failed: {exc}")


# ============================================================
# LEETCODE API
# ============================================================

def fetch_account() -> dict:
    """
    Fetch public account information from LeetCode.
    """

    response = requests.post(
        GRAPHQL_URL,
        headers=HEADERS,
        json={
            "query": QUERY,
            "variables": {
                "username": USERNAME,
                "limit": RECENT_SUBMISSIONS_LIMIT,
            },
        },
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("errors"):
        raise RuntimeError(
            "LeetCode GraphQL error:\n"
            + json.dumps(
                payload["errors"],
                indent=2,
            )
        )

    data = payload.get("data")

    if not data:
        raise RuntimeError(
            "LeetCode returned no data."
        )

    user = data.get("matchedUser")

    if user is None:
        raise RuntimeError(
            f"User '{USERNAME}' was not found."
        )

    return data


# ============================================================
# NORMALIZATION
# ============================================================

def build_snapshot(data: dict) -> dict:
    """
    Convert the API response into a compact JSON-serializable
    snapshot.

    Only information needed for reporting/comparison is stored.
    """

    user = data["matchedUser"]
    profile = user.get("profile") or {}

    solved_by_difficulty = {}
    submissions_by_difficulty = {}

    for item in user.get("submitStats", {}).get(
        "acSubmissionNum", []
    ):
        difficulty = item.get("difficulty", "Unknown")

        solved_by_difficulty[difficulty] = safe_int(
            item.get("count")
        )

        submissions_by_difficulty[difficulty] = safe_int(
            item.get("submissions")
        )

    total_submissions = {}

    for item in user.get("submitStats", {}).get(
        "totalSubmissionNum", []
    ):
        difficulty = item.get("difficulty", "Unknown")

        total_submissions[difficulty] = {
            "count": safe_int(item.get("count")),
            "submissions": safe_int(item.get("submissions")),
        }

    recent = []

    for item in data.get(
        "recentAcSubmissionList"
    ) or []:
        recent.append(
            {
                "title": item.get("title"),
                "slug": item.get("titleSlug"),
                "timestamp": safe_int(item.get("timestamp")),
                "status": item.get("statusDisplay"),
                "language": item.get("lang"),
            }
        )

    languages = {}

    for item in user.get(
        "languageProblemCount"
    ) or []:
        language = item.get("languageName")

        if language:
            languages[language] = safe_int(
                item.get("problemsSolved")
            )

    badges = []

    for badge in user.get("badges") or []:
        badges.append(
            {
                "id": badge.get("id"),
                "name": badge.get("displayName"),
                "creationDate": badge.get("creationDate"),
            }
        )

    contributions = user.get(
        "contributions"
    ) or {}

    return {
        "username": user.get("username", USERNAME),

        "profile": {
            "realName": profile.get("realName"),
            "aboutMe": profile.get("aboutMe"),
            "ranking": profile.get("ranking"),
            "reputation": profile.get("reputation"),
            "country": profile.get("countryName"),
            "company": profile.get("company"),
            "school": profile.get("school"),
            "starRating": profile.get("starRating"),
        },

        "solved": solved_by_difficulty,

        "accepted_submissions": submissions_by_difficulty,

        "total_submissions": total_submissions,

        "languages": languages,

        "badges": badges,

        "contributions": {
            "points": safe_int(
                contributions.get("points")
            ),
            "questions": safe_int(
                contributions.get("questionCount")
            ),
            "testcases": safe_int(
                contributions.get("testcaseCount")
            ),
        },

        "recent_submissions": recent,

        "checked_at": int(
            time.time()
        ),
    }


# ============================================================
# STATE
# ============================================================

def load_state() -> dict | None:
    if not STATE_FILE.exists():
        return None

    try:
        return json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )
    except (
        OSError,
        json.JSONDecodeError,
    ):
        print(
            "[!] State file is invalid. "
            "Creating a new baseline."
        )

        return None


def save_state(snapshot: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(
            snapshot,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )


# ============================================================
# COMPARISON
# ============================================================

def detect_changes(
    previous: dict | None,
    current: dict,
) -> list[str]:
    """
    Return human-readable changes between reports.
    """

    if previous is None:
        return ["Initial baseline created."]

    changes = []

    # --------------------------------------------------------
    # Solved counts
    # --------------------------------------------------------

    old_solved = previous.get("solved", {})
    new_solved = current.get("solved", {})

    for difficulty in (
        "All",
        "Easy",
        "Medium",
        "Hard",
    ):
        old = safe_int(
            old_solved.get(difficulty)
        )
        new = safe_int(
            new_solved.get(difficulty)
        )

        if new != old:
            delta = new - old

            changes.append(
                f"{difficulty}: "
                f"{old} → {new} "
                f"({delta:+d})"
            )

    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------

    old_rank = previous.get(
        "profile", {}
    ).get("ranking")

    new_rank = current.get(
        "profile", {}
    ).get("ranking")

    if old_rank != new_rank:
        changes.append(
            f"Ranking: "
            f"{format_number(old_rank)} → "
            f"{format_number(new_rank)}"
        )

    # --------------------------------------------------------
    # Reputation
    # --------------------------------------------------------

    old_rep = previous.get(
        "profile", {}
    ).get("reputation")

    new_rep = current.get(
        "profile", {}
    ).get("reputation")

    if old_rep != new_rep:
        changes.append(
            f"Reputation: "
            f"{format_number(old_rep)} → "
            f"{format_number(new_rep)}"
        )

    # --------------------------------------------------------
    # New recent submissions
    # --------------------------------------------------------

    old_submissions = {
        item.get("timestamp"): item
        for item in previous.get(
            "recent_submissions",
            [],
        )
    }

    for item in current.get(
        "recent_submissions",
        [],
    ):
        timestamp = item.get("timestamp")

        if timestamp not in old_submissions:
            changes.append(
                "New accepted submission: "
                f"{item.get('title', 'Unknown')}"
            )

    return changes


# ============================================================
# REPORT
# ============================================================

def print_header(title: str) -> None:
    print()
    print("=" * 78)
    print(title.center(78))
    print("=" * 78)


def print_account_report(
    snapshot: dict,
    changes: list[str],
) -> None:

    profile = snapshot["profile"]

    solved = snapshot["solved"]

    accepted = snapshot["accepted_submissions"]

    total_submissions = snapshot["total_submissions"]

    languages = snapshot["languages"]

    badges = snapshot["badges"]

    contributions = snapshot["contributions"]

    recent = snapshot["recent_submissions"]

    print_header(
        f"LEETCODE ACCOUNT REPORT — @{snapshot['username']}"
    )

    # --------------------------------------------------------
    # Profile
    # --------------------------------------------------------

    print("\n[ PROFILE ]")

    print(
        f"Username       : "
        f"{snapshot['username']}"
    )

    print(
        f"Name           : "
        f"{profile.get('realName') or 'N/A'}"
    )

    print(
        f"Country        : "
        f"{profile.get('country') or 'N/A'}"
    )

    print(
        f"Company        : "
        f"{profile.get('company') or 'N/A'}"
    )

    print(
        f"School         : "
        f"{profile.get('school') or 'N/A'}"
    )

    print(
        f"Ranking        : "
        f"{format_number(profile.get('ranking'))}"
    )

    print(
        f"Reputation     : "
        f"{format_number(profile.get('reputation'))}"
    )

    print(
        f"Star Rating    : "
        f"{profile.get('starRating') or 'N/A'}"
    )

    # --------------------------------------------------------
    # Solved
    # --------------------------------------------------------

    total_solved = sum(
        value
        for key, value in solved.items()
        if key != "All"
    )

    if solved.get("All") is not None:
        total_solved = solved["All"]

    print("\n[ PROBLEM SOLVING ]")

    print(
        f"Total Solved   : "
        f"{format_number(total_solved)}"
    )

    print(
        f"Easy           : "
        f"{format_number(solved.get('Easy'))}"
    )

    print(
        f"Medium         : "
        f"{format_number(solved.get('Medium'))}"
    )

    print(
        f"Hard           : "
        f"{format_number(solved.get('Hard'))}"
    )

    # --------------------------------------------------------
    # Acceptance statistics
    # --------------------------------------------------------

    print("\n[ SUBMISSION STATISTICS ]")

    for difficulty in (
        "All",
        "Easy",
        "Medium",
        "Hard",
    ):
        stats = total_submissions.get(
            difficulty,
            {},
        )

        accepted_count = accepted.get(
            difficulty,
            0,
        )

        submission_count = stats.get(
            "submissions",
            0,
        )

        attempts = stats.get(
            "count",
            0,
        )

        print(
            f"{difficulty:<8} : "
            f"{accepted_count:,} solved | "
            f"{submission_count:,} submissions | "
            f"{attempts:,} accepted entries"
        )

    # --------------------------------------------------------
    # Languages
    # --------------------------------------------------------

    print("\n[ LANGUAGES ]")

    if languages:
        sorted_languages = sorted(
            languages.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        for language, count in sorted_languages:
            print(
                f"{language:<20} "
                f"{count:,} problems"
            )
    else:
        print("No language data available.")

    # --------------------------------------------------------
    # Contributions
    # --------------------------------------------------------

    print("\n[ CONTRIBUTIONS ]")

    print(
        f"Points         : "
        f"{format_number(contributions['points'])}"
    )

    print(
        f"Questions      : "
        f"{format_number(contributions['questions'])}"
    )

    print(
        f"Testcases      : "
        f"{format_number(contributions['testcases'])}"
    )

    # --------------------------------------------------------
    # Badges
    # --------------------------------------------------------

    print("\n[ BADGES ]")

    if badges:

        for badge in badges[:20]:

            name = badge.get(
                "name"
            ) or "Unknown"

            date = badge.get(
                "creationDate"
            ) or "Unknown date"

            print(
                f"- {name} "
                f"({date})"
            )

        if len(badges) > 20:
            print(
                f"... and "
                f"{len(badges) - 20} more"
            )

    else:
        print("No badges available.")

    # --------------------------------------------------------
    # Recent submissions
    # --------------------------------------------------------

    print("\n[ RECENT ACCEPTED SUBMISSIONS ]")

    if recent:

        for index, item in enumerate(
            recent,
            start=1,
        ):

            title = item.get(
                "title",
                "Unknown",
            )

            language = item.get(
                "language",
                "Unknown",
            )

            timestamp = item.get(
                "timestamp"
            )

            print(
                f"{index:02d}. "
                f"{title} | "
                f"{language} | "
                f"{format_timestamp(timestamp)} | "
                f"{relative_time(timestamp)}"
            )

    else:
        print(
            "No recent accepted submissions available."
        )

    # --------------------------------------------------------
    # Last activity
    # --------------------------------------------------------

    if recent:

        latest_timestamp = max(
            item["timestamp"]
            for item in recent
            if item.get("timestamp")
        )

        print("\n[ ACTIVITY ]")

        print(
            f"Last visible accepted activity : "
            f"{format_timestamp(latest_timestamp)}"
        )

        print(
            f"Time since last activity       : "
            f"{relative_time(latest_timestamp)}"
        )

    # --------------------------------------------------------
    # Changes
    # --------------------------------------------------------

    print("\n[ CHANGES SINCE PREVIOUS REPORT ]")

    if changes:
        for change in changes:
            print(f"- {change}")
    else:
        print(
            "No detected changes."
        )

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    checked = snapshot.get(
        "checked_at"
    )

    print()
    print(
        f"Report generated: "
        f"{format_timestamp(checked)}"
    )

    print(
        f"Next report in: "
        f"{REPORT_INTERVAL} seconds"
    )

    print("=" * 78)


# ============================================================
# NOTIFICATION SUMMARY
# ============================================================

def notify_changes(
    changes: list[str],
) -> None:

    if not changes:
        return

    meaningful = [
        change
        for change in changes
        if change != "Initial baseline created."
    ]

    if not meaningful:
        return

    # Windows notifications should stay reasonably short.
    message = "\n".join(
        meaningful[:4]
    )

    if len(meaningful) > 4:
        message += (
            f"\n+ {len(meaningful) - 4} more changes"
        )

    notify(
        "LeetCode Activity Detected",
        message,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print(
        r"""
╔══════════════════════════════════════════════════════════════╗
║             LEETCODE PUBLIC ACCOUNT REPORTER                ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    print(
        f"Target account : @{USERNAME}"
    )

    print(
        f"Report interval: {REPORT_INTERVAL} seconds"
    )

    print(
        f"State file     : {STATE_FILE.resolve()}"
    )

    print()

    previous = load_state()

    while True:

        started = time.monotonic()

        try:

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                "Fetching account..."
            )

            data = fetch_account()

            current = build_snapshot(data)

            changes = detect_changes(
                previous,
                current,
            )

            print_account_report(
                current,
                changes,
            )

            notify_changes(
                changes
            )

            save_state(current)

            previous = current

            elapsed = time.monotonic() - started

            print(
                f"\nFetch/report completed in "
                f"{elapsed:.2f}s."
            )

        except KeyboardInterrupt:

            print(
                "\n\nStopped by user."
            )

            break

        except requests.RequestException as exc:

            print_header(
                "NETWORK ERROR"
            )

            print(exc)

            print(
                "\nWill retry after the interval."
            )

        except Exception as exc:

            print_header(
                "ERROR"
            )

            print(
                f"{type(exc).__name__}: {exc}"
            )

            print(
                "\nWill retry after the interval."
            )

        # ----------------------------------------------------
        # Keep the interval approximately 250 seconds between
        # report starts, rather than sleeping 250 seconds after
        # a slow request.
        # ----------------------------------------------------

        elapsed = time.monotonic() - started

        sleep_for = max(
            1,
            REPORT_INTERVAL - elapsed,
        )

        print(
            f"\nSleeping {sleep_for:.0f}s..."
        )

        try:
            time.sleep(sleep_for)

        except KeyboardInterrupt:

            print(
                "\n\nStopped by user."
            )

            break


if __name__ == "__main__":
    main()
