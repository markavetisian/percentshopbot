# PERCENT SHOP OTC bot

Telegram bot running on Vercel as a webhook. `/start` shows the shop menu with a
**Contact / Inquire** button. Commands: `/start`, `/menu`, `/contact`.

No dependencies. The whole bot is `api/webhook.py`.

## Deploy on Vercel

1. Import this GitHub repo in Vercel (Add New > Project). No build settings needed.
2. In Project Settings > Environment Variables add:
   - `BOT_TOKEN` = your BotFather token
   - `WEBHOOK_SECRET` = any random string (letters, numbers, `_` and `-` only)
3. Redeploy so the variables take effect.
4. Point Telegram at your deployment by opening this URL in a browser once
   (fill in your values):

   ```
   https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<your-project>.vercel.app/api/webhook&secret_token=<WEBHOOK_SECRET>&allowed_updates=["message","callback_query"]
   ```

   You should see `"Webhook was set"`.

Check it any time with `https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo`.
