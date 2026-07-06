import os
import random
import datetime as dt
from zoneinfo import ZoneInfo

import requests


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing {name}. Add it in GitHub: "
            "Settings → Secrets and variables → Actions → Repository secrets. "
            "The secret name must match exactly."
        )
    return value


BOT_TOKEN = required_env("TELEGRAM_BOT_TOKEN")
CHAT_ID = required_env("TELEGRAM_CHAT_ID")

TIMEZONE = os.getenv("TIMEZONE", "Europe/Berlin").strip() or "Europe/Berlin"
FREQUENCY = os.getenv("FREQUENCY", "twice").strip().lower()  # once or twice
TASK_HOURS = os.getenv("TASK_HOURS", "8,18").strip()
RUN_MODE = os.getenv("RUN_MODE", "auto").strip().lower()  # auto, morning, evening, manual
FORCE_SEND = os.getenv("FORCE_SEND", "false").strip().lower() == "true"


B2_TOPICS = [
    {
        "topic": "Homeoffice vs. Büroarbeit",
        "question": "Welche Arbeitsform ist produktiver — Homeoffice oder Büroarbeit?",
        "phrases": [
            "Einerseits ... andererseits ...",
            "Aus meiner Sicht ...",
            "Das hängt stark davon ab, ob ..."
        ],
        "grammar": "Nutze mindestens 3 Nebensätze mit weil, obwohl oder während."
    },
    {
        "topic": "Nachhaltiger Konsum",
        "question": "Wie kann man im Alltag nachhaltiger einkaufen, ohne zu viel Geld auszugeben?",
        "phrases": [
            "Ich lege Wert auf ...",
            "Es wäre sinnvoll, ... zu ...",
            "Langfristig gesehen ..."
        ],
        "grammar": "Nutze Konjunktiv II: könnte, sollte, wäre, hätte."
    },
    {
        "topic": "Künstliche Intelligenz im Alltag",
        "question": "Welche Chancen und Risiken bringt KI für Lernende und Berufstätige?",
        "phrases": [
            "Ein großer Vorteil besteht darin, dass ...",
            "Man darf nicht unterschätzen, dass ...",
            "Trotzdem bin ich der Meinung, dass ..."
        ],
        "grammar": "Baue mindestens 2 Infinitivkonstruktionen mit zu ein."
    },
    {
        "topic": "Reisen und Kultur",
        "question": "Warum ist Reisen für die persönliche Entwicklung wichtig?",
        "phrases": [
            "Ich habe die Erfahrung gemacht, dass ...",
            "Im Vergleich zu ...",
            "Was mich besonders beeindruckt, ist ..."
        ],
        "grammar": "Nutze Relativsätze: der/die/das, dessen, in dem."
    },
    {
        "topic": "Gesundheit und Stress",
        "question": "Was hilft dir, mit Stress umzugehen, und was würdest du anderen empfehlen?",
        "phrases": [
            "Mir hilft es, wenn ...",
            "An deiner Stelle würde ich ...",
            "Entscheidend ist, dass ..."
        ],
        "grammar": "Nutze Modalverben und Konjunktiv II."
    },
    {
        "topic": "Soziale Medien",
        "question": "Beeinflussen soziale Medien unsere Meinungen zu stark?",
        "phrases": [
            "Ich stimme teilweise zu, weil ...",
            "Man sollte kritisch hinterfragen, ob ...",
            "Ein Beispiel dafür ist ..."
        ],
        "grammar": "Nutze Passiv: Es wird behauptet, dass ..."
    },
    {
        "topic": "Bildung der Zukunft",
        "question": "Wie sollte Schule oder Universität in Zukunft aussehen?",
        "phrases": [
            "Meiner Meinung nach müsste ...",
            "Es kommt darauf an, ... zu ...",
            "Im Mittelpunkt sollte ... stehen."
        ],
        "grammar": "Nutze mindestens 4 Verben mit Präpositionen, z. B. sich interessieren für."
    },
    {
        "topic": "Stadtleben vs. Landleben",
        "question": "Wo lebt man besser — in der Stadt oder auf dem Land?",
        "phrases": [
            "Während ... bietet, ...",
            "Ein Nachteil besteht darin, dass ...",
            "Für mich persönlich überwiegen ..."
        ],
        "grammar": "Vergleiche mit Komparativ und Superlativ."
    },
    {
        "topic": "Berufliche Ziele",
        "question": "Welche Fähigkeiten werden in deinem Berufsfeld in den nächsten Jahren wichtiger?",
        "phrases": [
            "In Zukunft wird es wichtiger sein, ...",
            "Ich arbeite gerade daran, ...",
            "Eine Fähigkeit, die oft unterschätzt wird, ist ..."
        ],
        "grammar": "Nutze Futur I und Relativsätze."
    },
    {
        "topic": "Freundschaft und Kommunikation",
        "question": "Was macht eine gute Freundschaft aus?",
        "phrases": [
            "Für mich bedeutet Freundschaft, dass ...",
            "Es ist wichtig, ehrlich miteinander umzugehen.",
            "Selbst wenn ..., sollte man ..."
        ],
        "grammar": "Nutze selbst wenn, damit und ohne dass."
    },
]


def local_now() -> dt.datetime:
    return dt.datetime.now(ZoneInfo(TIMEZONE))


def parse_task_hours() -> list[int]:
    try:
        hours = [int(hour.strip()) for hour in TASK_HOURS.split(",") if hour.strip()]
    except ValueError as exc:
        raise RuntimeError("TASK_HOURS must look like '8' or '8,18'.") from exc

    if not hours:
        raise RuntimeError("TASK_HOURS is empty. Use '8' or '8,18'.")

    for hour in hours:
        if hour < 0 or hour > 23:
            raise RuntimeError("TASK_HOURS must contain hours from 0 to 23.")

    if FREQUENCY == "once":
        return [hours[0]]

    if FREQUENCY == "twice":
        if len(hours) < 2:
            return [hours[0], 18]
        return hours[:2]

    raise RuntimeError("FREQUENCY must be either 'once' or 'twice'.")


def should_send(now: dt.datetime) -> tuple[bool, str]:
    if FORCE_SEND:
        if RUN_MODE == "evening":
            return True, "evening"
        return True, "morning"

    hours = parse_task_hours()

    if now.hour not in hours:
        return False, "not_due"

    if FREQUENCY == "twice" and len(hours) > 1 and now.hour == hours[1]:
        return True, "evening"

    return True, "morning"


def pick_task(now: dt.datetime) -> dict:
    day_index = now.timetuple().tm_yday
    return B2_TOPICS[day_index % len(B2_TOPICS)]


def build_message(task: dict, slot: str, now: dt.datetime) -> str:
    date_str = now.strftime("%d.%m.%Y")

    if slot == "evening":
        return f"""🇩🇪 Jonas' B2 Deutsch-Sprechaufgabe — Abend
📅 {date_str}

Thema: {task['topic']}

1) Sprich 2 Minuten frei:
„Was habe ich heute gemacht, das zu diesem Thema passt?“

2) Korrigiere dich selbst:
Wähle 3 Sätze aus deiner Aufnahme und verbessere sie:
• Satz 1: Wortstellung
• Satz 2: Grammatik
• Satz 3: natürlicher Ausdruck

3) Bonus:
Formuliere deine Meinung noch einmal mit diesen Redemitteln:
• {task['phrases'][0]}
• {task['phrases'][1]}
• {task['phrases'][2]}

Mini-Ziel:
{task['grammar']}

Tipp:
Nimm dich mit Telegram-Sprachnachricht auf. Höre danach einmal kritisch zu und wiederhole die beste Version."""

    return f"""🇩🇪 Jonas' B2 Deutsch-Sprechaufgabe — Morgen
📅 {date_str}

Thema: {task['topic']}

Sprechfrage:
{task['question']}

Aufgabe:
Sprich 3 Minuten frei. Struktur:
1) Kurze Einleitung
2) Zwei Argumente
3) Ein persönliches Beispiel
4) Kurzes Fazit

Redemittel:
• {task['phrases'][0]}
• {task['phrases'][1]}
• {task['phrases'][2]}

Mini-Ziel:
{task['grammar']}

Nach dem Sprechen:
Schreibe 3 Wörter auf, die dir gefehlt haben, und lerne sie aktiv."""


def send_telegram_message(text: str) -> None:
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
        raise RuntimeError("Telegram rejected the bot token. Check TELEGRAM_BOT_TOKEN.")

    if response.status_code == 400:
        raise RuntimeError(
            "Telegram rejected the chat ID or message. "
            "Check TELEGRAM_CHAT_ID and make sure you have sent /start to the bot."
        )

    response.raise_for_status()


def main() -> int:
    now = local_now()
    due, slot = should_send(now)

    print(f"Local time: {now.isoformat()}")
    print(f"Frequency: {FREQUENCY}")
    print(f"Task hours: {parse_task_hours()}")
    print(f"Run mode: {RUN_MODE}")
    print(f"Force send: {FORCE_SEND}")

    if not due:
        print("No task sent because this run is not due.")
        return 0

    task = pick_task(now)
    message = build_message(task, slot, now)
    send_telegram_message(message)

    print(f"Sent {slot} task successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
