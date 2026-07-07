# Hospital German Speaking Coach Bot

A Telegram bot for short daily B2 German speaking practice focused on hospital communication.

The bot is designed for Jonas because he works in a hospital. It trains useful German for patient communication, ward routines, colleague conversations, shift handovers, and professional speaking.

This is a language-learning bot. It does not provide medical instructions or clinical advice.

## Recommended rhythm

Use **twice daily**:

- Morning: 5-minute hospital German speaking task
- Evening: 5–7-minute correction and repetition task

This is better than one long lesson because professional speaking improves through repetition, self-recording, and correction.

## Lesson focus

Each lesson includes:

- hospital situation
- B2 speaking question
- answer structure
- hospital vocabulary
- professional Redemittel
- grammar focus
- pronunciation focus
- speaking challenge
- evening self-correction

## Files

```text
bot.py
lessons.json
requirements.txt
.github/workflows/send-hospital-german-speaking-lesson.yml
.env.example
README.md
```

## GitHub setup

### 1. Create Telegram bot

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Choose a bot name
5. Choose a username ending in `bot`
6. Copy the token

### 2. Get your Telegram chat ID

1. Send `/start` to your new bot
2. Send any message to the bot, for example `hello`
3. Open this URL in your browser:

```text
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

4. Find:

```json
"chat":{"id":123456789}
```

5. Copy the number.

For groups, the chat ID is often negative.

### 3. Add GitHub secrets

In your GitHub repo, go to:

```text
Settings → Secrets and variables → Actions → Repository secrets
```

Create exactly these two secrets:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Important:

- Use **Secrets**, not Variables
- Names must match exactly
- Do not add quotes around the values

## Schedule

Default:

```yaml
FREQUENCY: twice
TASK_HOURS: "8,18"
```

That means:

```text
08:00 → morning hospital German speaking lesson
18:00 → evening correction task
```

For once daily:

```yaml
FREQUENCY: once
TASK_HOURS: "8"
```

The workflow runs hourly because GitHub cron uses UTC. The Python script checks Europe/Berlin time and sends only at the correct local hours.

## Manual test

In GitHub:

```text
Actions → Send Hospital German Speaking Lesson → Run workflow
```

Choose:

```text
test
```

Then test:

```text
morning
```

or:

```text
evening
```

## Customize lessons

Edit:

```text
lessons.json
```

Each lesson has this format:

```json
{
  "title": "...",
  "theme": "...",
  "scenario": "...",
  "question": "...",
  "goal": "...",
  "vocabulary": ["...", "..."],
  "structure": ["...", "..."],
  "phrases": ["...", "..."],
  "grammar": "...",
  "pronunciation": "...",
  "challenge": "..."
}
```

## Suggested repo name

```text
hospital-german-speaking-coach-bot
```
