# Jonas’ Krankenhausdeutsch-Coach – Version 2

## Fester Wochenrhythmus

- Montag: Reinraumbetrieb, Freigabe, Alarme und Übergabe
- Dienstag: Material, Wartung und QM
- Mittwoch: wöchentliche MIBI
- Letzter Mittwoch des Monats: monatliche MIBI statt Wochen-MIBI
- Donnerstag: Sporozid-Reinigung
- Freitag: Reinraumwäsche
- Samstag: Teamkommunikation und Rollenabgrenzung
- Sonntag: kurze Wiederholung

## Zwei kurze Nachrichten pro Tag

### Morgens
Eine reale Situation, eine klare Sprechaufgabe, drei Fachwörter, ein Satzstarter und ein Sprachfokus.

### Abends
Aufnahme anhören, zwei Sätze verbessern und dieselbe Situation in 45–60 Sekunden erneut sprechen.

## Installation

Lege diese Dateien ins Repository:

- `telegram_coach.py`
- `lessons.json`
- `.github/workflows/telegram-coach.yml`

Repository Secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Empfohlene Variables:

- `STUDENT_NAME=Jonas`
- `TIMEZONE=Europe/Berlin`
- `FREQUENCY=twice`
- `TASK_HOURS=8,18`

Der Workflow läuft stündlich. Das Python-Skript sendet nur zu den eingestellten Stunden.
