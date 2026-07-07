name: Send Hospital German Speaking Lesson

on:
  schedule:
    # GitHub cron uses UTC. This workflow runs hourly.
    # bot.py checks Europe/Berlin time and sends only at TASK_HOURS.
    - cron: "0 * * * *"

  workflow_dispatch:
    inputs:
      run_type:
        description: "Message to send now"
        required: true
        default: "test"
        type: choice
        options:
          - test
          - morning
          - evening

permissions:
  contents: read

jobs:
  send-lesson:
    runs-on: ubuntu-latest

    env:
      TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
      TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}

      STUDENT_NAME: Jonas
      TIMEZONE: Europe/Berlin
      FREQUENCY: twice
      TASK_HOURS: "8,18"

      RUN_TYPE: ${{ github.event.inputs.run_type || 'auto' }}
      FORCE_SEND: ${{ github.event_name == 'workflow_dispatch' && 'true' || 'false' }}

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Check required secrets
        shell: bash
        run: |
          if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
            echo "❌ TELEGRAM_BOT_TOKEN is missing."
            echo "Go to Settings → Secrets and variables → Actions → Repository secrets."
            echo "Create a secret named TELEGRAM_BOT_TOKEN."
            exit 1
          fi

          if [ -z "$TELEGRAM_CHAT_ID" ]; then
            echo "❌ TELEGRAM_CHAT_ID is missing."
            echo "Go to Settings → Secrets and variables → Actions → Repository secrets."
            echo "Create a secret named TELEGRAM_CHAT_ID."
            exit 1
          fi

          echo "✅ Required secrets exist."

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Python dependencies
        run: pip install -r requirements.txt

      - name: Send Telegram lesson
        run: python bot.py
