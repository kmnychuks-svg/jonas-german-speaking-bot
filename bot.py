import os
import sys
import random
import datetime as dt
from zoneinfo import ZoneInfo

import requests


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TIMEZONE = os.getenv("TIMEZONE", "Europe/Berlin")
FREQUENCY = os.getenv("FREQUENCY", "twice").lower()  # "once" or "twice"
TASK_HOURS = os.getenv("TASK_HOURS", "8,18")  # local hours, e.g. "8" or "8,18"
RUN_MODE = os.getenv("RUN_MODE", "auto").lower()  # "auto", "morning", "evening", "once"
FORCE_SEND = os.getenv("FORCE_SEND", "false").lower() == "true"


B2_TOPICS = [
    {
        "topic": "Homeoffice vs. Büroarbeit",
        "question": "Welche Arbeitsform ist produktiver — Homeoffice oder Büroarbeit?",
        "phrases": ["Einerseits ... andererseits ...", "Aus meiner Sicht ...", "Das hängt stark davon ab, ob ..."],
        "grammar": "Nutze mindestens 3 Nebensätze mit weil, obwohl oder während."
    },
    {
        "topic": "Nachhaltiger Konsum",
        "question": "Wie kann man im Alltag nachhaltiger einkaufen, ohne zu viel Geld auszugeben?",
        "phrases": ["Ich lege Wert auf ...", "Es wäre sinnvoll, ... zu ...", "Langfristig gesehen ..."],
        "grammar": "Nutze Konjunktiv II: könnte, sollte, wäre, hätte."
    },
    {
        "topic": "Künstliche Intelligenz im Alltag",
        "question": "Welche Chancen und Risiken bringt KI für Lernende und Berufstätige?",
        "phrases": ["Ein großer Vorteil besteht darin, dass ...", "Man darf nicht unterschätzen, dass ...", "Trotzdem bin ich der Meinung, dass ..."],
        "grammar": "Baue mindestens 2 Infinitivkonstruktionen mit zu ein."
    },
    {
        "topic": "Reisen und Kultur",
        "question": "Warum ist Reisen für die persönliche Entwicklung wichtig?",
        "phrases": ["Ich habe die Erfahrung gemacht, dass ...", "Im Vergleich zu ...", "Was mich besonders beeindruckt, ist ..."],
        "grammar": "Nutze Relativsätze: der/die/das, dessen, in dem."
    },
    {
        "topic": "Gesundheit und Stress",
        "question": "Was hilft dir, mit Stress umzugehen, und was würdest du anderen empfehlen?",
        "phrases": ["Mir hilft es, wenn ...", "An deiner Stelle würde ich ...", "Entscheidend ist, dass ..."],
        "grammar": "Nutze Modalverben und Konjunktiv II."
    },
    {
        "topic": "Soziale Medien",
        "question": "Beeinflussen soziale Medien unsere Meinungen zu stark?",
        "phrases": ["Ich stimme teilweise zu, weil ...", "Man sollte kritisch hinterfragen, ob ...", "Ein Beispiel dafür ist ..."],
        "grammar": "Nutze Passiv: Es wird behauptet, dass ..."
    },
    {
        "topic": "Bildung der Zukunft",
        "question": "Wie sollte Schule oder Universität in Zukunft aussehen?",
        "phrases": ["Meiner Meinung nach müsste ...", "Es kommt darauf an, ... zu ...", "Im Mittelpunkt sollte ... stehen."],
        "grammar": "Nutze mindestens 4 Verben mit Präpositionen, z. B. sich interessieren für."
    },
    {
        "topic": "Stadtleben vs. Landleben",
        "question": "Wo lebt man besser — in der Stadt oder auf dem Land?",
        "phrases": ["Während ... bietet, ...", "Ein Nachteil besteht darin, dass ...", "Für mich persönlich überwiegen ..."],
        "grammar": "Vergleiche mit Komparativ und Superlativ."
    },
    {
        "topic": "Berufliche Ziele",
        "question": "Welche Fähigkeiten werden in deinem Berufsfeld in den nächsten Jahren wichtiger?",
        "phrases": ["In Zukunft wird es wichtiger sein, ...", "Ich arbeite gerade daran, ...", "Eine Fähigkeit, die oft unterschätzt wird, ist ..."],
        "grammar": "Nutze Futur I und Relativsätze."
    },
    {
        "topic": "Freundschaft und Kommunikation",
        "question": "Was macht eine gute Freundschaft aus?",
        "phrases": ["Für mich bedeutet Freundschaft, dass ...", "Es ist wichtig, ehrlich miteinander umzugehen.", "Selbst wenn ..., sollte man ..."],
        "grammar": "Nutze selbst wenn, damit und ohne dass."
    }
]


def local_now() -> dt.datetime:
    return dt.datetime.now(ZoneInfo(TIMEZONE))


def should_send(now: dt.datetime) -> tuple[bool, str]:
    """Return (should_send, slot)."""
    if FORCE_SEND:
        return True, RUN_MODE if RUN_MODE != "auto" else "manual"

    hours = [int(h.strip()) for h in TASK_HOURS.split(",") if h.strip()]
    if FREQUENCY == "once":
        hours = hours[:1]

    if RUN_MODE in ("morning", "once"):
        return now.hour == hours[0], "morning"
    if RUN_MODE == "evening":
        evening_hour = hours[1] if len(hours) > 1 else 18
        return now.hour == evening_hour, "evening"

    if now.hour not in hours:
        return False, "not_due"

    if len(hours) > 1 and now.hour == hours[-1]:
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
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variable.")

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
    response.raise_for_status()


def main() -> int:
    now = local_now()
    due, slot = should_send(now)

    if not due:
        print(f"Not due. Local time is {now.isoformat()}, slot={slot}, frequency={FREQUENCY}.")
        return 0

    task = pick_task(now)
    message = build_message(task, slot, now)
    send_telegram_message(message)
    print(f"Sent {slot} task for {now.date()} to Telegram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
