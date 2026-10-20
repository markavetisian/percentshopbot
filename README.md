# PERCENT SHOP OTC bot

Telegram bot. `/start` shows the shop menu with a **Contact / Inquire** button.

No dependencies, just Python 3.8+.

## Run

```
cp .env.example .env      # then put your real token in .env
python3 bot.py
```

Or: `BOT_TOKEN=xxxx python3 bot.py`

`.env` is gitignored so the token never gets committed.

Commands: `/start`, `/menu`, `/contact`.
