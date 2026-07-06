# Jonas German B2 Telegram Task Bot

This bot sends Jonas German B2 speaking tasks on Telegram using GitHub Actions.

## Recommendation

Use `FREQUENCY: twice`.

For B2 speaking, twice daily is better than once daily:

- Morning: 3-minute free speaking task
- Evening: reflection, correction, and improved second attempt

Once daily is fine if Jonas often skips tasks, but twice daily gives more repetition and faster speaking improvement.

## Files

- `bot.py` — creates and sends the German task
- `.github/workflows/send-german-task.yml` — runs the bot from GitHub Actions
- `requirements.txt` — Python dependency list

## Setup

### 1. Create a Telegram bot

1. Open Telegram.
2. Search for `@BotFather`.
3. Send `/newbot`.
4. Copy the bot token.

### 2. Get your Telegram chat ID

The easiest method:

1. Send any message to your new bot.
2. Open this URL in your browser, replacing `<BOT_TOKEN>`:

```text
https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```

3. Find `"chat":{"id":...}`.
4. Copy that number.

### 3. Add GitHub repository secrets

In your GitHub repository:

`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Add:

```text
TELEGRAM_BOT_TOKEN = your Telegram bot token
TELEGRAM_CHAT_ID = your chat ID
```

### 4. Choose once or twice daily

Open:

```text
.github/workflows/send-german-task.yml
```

For twice daily, keep:

```yaml
FREQUENCY: twice
TASK_HOURS: "8,18"
```

For once daily, change it to:

```yaml
FREQUENCY: once
TASK_HOURS: "8"
```

The times are local Europe/Berlin time.

## Manual test

Go to:

`Actions` → `Send German Telegram Task` → `Run workflow`

This sends a test task immediately.
