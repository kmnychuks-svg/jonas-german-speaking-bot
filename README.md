# Hospital German Speaking Coach Bot

This repository sends short B2 German speaking lessons for hospital communication through Telegram.

## Important file placement

`bot.py` must contain Python code.

The workflow YAML must be here:

```text
.github/workflows/send-hospital-german-speaking-lesson.yml
```

If `bot.py` starts with this line, it is wrong:

```text
name: Send Hospital German Speaking Lesson
```

That line belongs in the workflow file, not in `bot.py`.

## Required GitHub secrets

Add these in:

```text
Settings → Secrets and variables → Actions → Repository secrets
```

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```
