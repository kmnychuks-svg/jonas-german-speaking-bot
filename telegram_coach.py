import datetime as dt
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

LESSON_FILE = Path(__file__).with_name("lessons.json")


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"{name} is missing. Add it in GitHub under: "
            "Settings → Secrets and variables → Actions → Repository secrets."
        )
    return value


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


BOT_TOKEN = required_env("TELEGRAM_BOT_TOKEN")
CHAT_ID = required_env("TELEGRAM_CHAT_ID")

STUDENT_NAME = os.getenv("STUDENT_NAME", "Jonas").strip() or "Jonas"
TIMEZONE = os.getenv("TIMEZONE", "Europe/Berlin").strip() or "Europe/Berlin"
FREQUENCY = os.getenv("FREQUENCY", "twice").strip().lower()
TASK_HOURS = os.getenv("TASK_HOURS", "8,18").strip()
RUN_TYPE = os.getenv("RUN_TYPE", "auto").strip().lower()
FORCE_SEND = get_bool_env("FORCE_SEND", False)


def load_lessons() -> list[dict]:
    lessons = json.loads(LESSON_FILE.read_text(encoding="utf-8"))
    if not isinstance(lessons, list) or not lessons:
        raise RuntimeError("lessons.json must contain a non-empty list.")
    return lessons


def now_local() -> dt.datetime:
    return dt.datetime.now(ZoneInfo(TIMEZONE))


def parse_hours() -> list[int]:
    try:
        hours = [int(item.strip()) for item in TASK_HOURS.split(",") if item.strip()]
    except ValueError as exc:
        raise RuntimeError("TASK_HOURS must be like '8' or '8,18'.") from exc

    if not hours:
        raise RuntimeError("TASK_HOURS must not be empty.")

    if any(hour < 0 or hour > 23 for hour in hours):
        raise RuntimeError("TASK_HOURS must contain hours between 0 and 23.")

    if FREQUENCY == "once":
        return [hours[0]]

    if FREQUENCY == "twice":
        return [hours[0], hours[1] if len(hours) > 1 else 18]

    raise RuntimeError("FREQUENCY must be 'once' or 'twice'.")


def is_last_wednesday(day: dt.date) -> bool:
    return day.weekday() == 2 and (day + dt.timedelta(days=7)).month != day.month


def lesson_kind(day: dt.date) -> str:
    weekday = day.weekday()

    if weekday == 0:
        return "monday"
    if weekday == 1:
        return "tuesday"
    if weekday == 2:
        return "monthly_mibi" if is_last_wednesday(day) else "weekly_mibi"
    if weekday == 3:
        return "thursday_sporicide"
    if weekday == 4:
        return "friday_laundry"
    if weekday == 5:
        return "saturday"
    return "sunday"


def choose_lesson(lessons: list[dict], now: dt.datetime) -> dict:
    kind = lesson_kind(now.date())
    candidates = [item for item in lessons if item.get("kind") == kind]

    if not candidates:
        raise RuntimeError(f"No lesson found for kind: {kind}")

    start_date = dt.date(2026, 1, 1)
    week_number = max(0, (now.date() - start_date).days // 7)
    return candidates[week_number % len(candidates)]


def determine_send_type(now: dt.datetime) -> tuple[bool, str]:
    if FORCE_SEND:
        if RUN_TYPE in {"evening", "correction"}:
            return True, "evening"
        if RUN_TYPE == "test":
            return True, "test"
        return True, "morning"

    hours = parse_hours()
    if now.hour not in hours:
        return False, "not_due"

    if FREQUENCY == "twice" and now.hour == hours[1]:
        return True, "evening"

    return True, "morning"


def build_morning_message(lesson: dict, now: dt.datetime) -> str:
    words = " · ".join(lesson["words"][:3])
    return f"""🏥 {STUDENT_NAME} | {lesson['theme']}
📅 {now.strftime('%d.%m.%Y')}

Situation: {lesson['scenario']}

Aufgabe: {lesson['task']}
🎙 Sprich 60–90 Sekunden.

Nutze: {words}
Start: „{lesson['starter']}“
Fokus: {lesson['focus']}"""


def build_evening_message(lesson: dict, now: dt.datetime) -> str:
    return f"""🌙 Kurzkorrektur | {lesson['theme']}

1. Höre deine Aufnahme.
2. Verbessere zwei Sätze.
3. Sprich noch einmal 45–60 Sekunden.

Ziel: {lesson['goal']}
Pflichtsatz: „{lesson['starter']}“"""


def build_test_message() -> str:
    return f"""✅ Hallo {STUDENT_NAME}

Der Krankenhausdeutsch-Bot funktioniert.
Mittwoch: MIBI
Letzter Mittwoch: Monats-MIBI
Donnerstag: Sporozid-Reinigung
Freitag: Wäsche"""


def send_telegram(text: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": True,
        },
        timeout=20,
    )

    if response.status_code == 401:
        raise RuntimeError(
            "Telegram rejected TELEGRAM_BOT_TOKEN. "
            "Copy the token again from @BotFather and update the GitHub secret."
        )

    if response.status_code == 400:
        raise RuntimeError(
            "Telegram rejected TELEGRAM_CHAT_ID or the message. "
            "Send /start to the bot, then get the correct chat id from getUpdates."
        )

    response.raise_for_status()


def main() -> int:
    now = now_local()
    lessons = load_lessons()
    should_send, send_type = determine_send_type(now)

    print(f"Local time: {now.isoformat()}")
    print(f"Lesson type: {lesson_kind(now.date())}")
    print(f"Decision: should_send={should_send}, send_type={send_type}")

    if not should_send:
        print("No message sent. This hourly run is not due.")
        return 0

    lesson = choose_lesson(lessons, now)

    if send_type == "test":
        message = build_test_message()
    elif send_type == "evening":
        message = build_evening_message(lesson, now)
    else:
        message = build_morning_message(lesson, now)

    send_telegram(message)
    print(f"Sent {send_type} message successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
