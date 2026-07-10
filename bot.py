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

    for hour in hours:
        if hour < 0 or hour > 23:
            raise RuntimeError("TASK_HOURS must contain hours between 0 and 23.")

    if FREQUENCY == "once":
        return [hours[0]]

    if FREQUENCY == "twice":
        if len(hours) == 1:
            return [hours[0], 18]
        return hours[:2]

    raise RuntimeError("FREQUENCY must be 'once' or 'twice'.")


def choose_lesson(lessons: list[dict], now: dt.datetime) -> dict:
    start_date = dt.date(2026, 1, 1)
    day_number = (now.date() - start_date).days
    return lessons[day_number % len(lessons)]


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

    if FREQUENCY == "twice" and len(hours) > 1 and now.hour == hours[1]:
        return True, "evening"

    return True, "morning"


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"• {item}" for item in items)


def build_morning_message(lesson: dict, now: dt.datetime) -> str:
    return f"""🏥🇩🇪 {STUDENT_NAME}s Krankenhausdeutsch B2
📅 {now.strftime('%d.%m.%Y')}
⏱️ Dauer: 5 Minuten

Situation:
{lesson['scenario']}

Thema:
{lesson['theme']}

Sprechfrage:
{lesson['question']}

Ziel:
{lesson['goal']}

Struktur:
{bullet_list(lesson['structure'])}

Wortschatz:
{bullet_list(lesson['vocabulary'])}

Redemittel:
{bullet_list(lesson['phrases'])}

Grammatik-Fokus:
{lesson['grammar']}

Aussprache-Fokus:
{lesson['pronunciation']}

Aufgabe:
Nimm eine Telegram-Sprachnachricht auf. Sprich so, als wärst du im Krankenhaus, aber bleibe ruhig und klar.

Mini-Challenge:
{lesson['challenge']}"""


def build_evening_message(lesson: dict, now: dt.datetime) -> str:
    return f"""🌙🏥 {STUDENT_NAME}s Krankenhausdeutsch-Korrektur
📅 {now.strftime('%d.%m.%Y')}
⏱️ Dauer: 5–7 Minuten

Situation von heute:
{lesson['scenario']}

Schritt 1:
Höre deine Sprachnachricht von heute noch einmal an.

Schritt 2:
Verbessere 3 Sätze:
• 1 Satz mit besserer Wortstellung
• 1 Satz mit genauerer Grammatik
• 1 Satz mit professionellerem Krankenhausdeutsch

Schritt 3:
Sprich die Situation noch einmal, aber kürzer und besser: 90 Sekunden.

Pflicht-Wörter:
{bullet_list(lesson['vocabulary'][:4])}

Pflicht-Redemittel:
{bullet_list(lesson['phrases'])}

Lehrer-Tipp:
Im Krankenhaus ist gutes Deutsch nicht nur korrekt. Es muss ruhig, höflich, kurz und eindeutig sein."""


def build_test_message() -> str:
    return f"""✅ Testnachricht vom Krankenhausdeutsch Coach

Hallo {STUDENT_NAME}, der Telegram-Bot funktioniert.

Nächster Schritt:
Starte mit einer kurzen B2-Aufgabe für Krankenhausdeutsch."""


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
    print(f"Timezone: {TIMEZONE}")
    print(f"Frequency: {FREQUENCY}")
    print(f"Task hours: {parse_hours()}")
    print(f"Run type: {RUN_TYPE}")
    print(f"Force send: {FORCE_SEND}")
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
