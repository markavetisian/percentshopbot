"""PERCENT SHOP OTC Telegram bot, as a Vercel serverless webhook.

Telegram POSTs each update to /api/webhook. The reply is returned in the
HTTP response body (Telegram's "webhook reply"), so no extra round trip is
needed and messages appear instantly.

Environment variables (set in Vercel project settings):
  BOT_TOKEN       the token from BotFather
  WEBHOOK_SECRET  any random string; must match secret_token in setWebhook
"""

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

WELCOME_TEXT = (
    "Welcome to <b>Percent Shop</b>.\n"
    "\n"
    "A shop for software, crypto payments, Telegram assets, and unethical "
    "development.\n"
    "\n"
    "🔺 <b>SOFTWARE</b>\n"
    "└ Custom / unethical software\n"
    "└ Tools &amp; scripts\n"
    "└ Web apps\n"
    "\n"
    "🔺 <b>CRYPTO PAYMENTS</b>\n"
    "└ TON / USDT systems\n"
    "└ Crypto checkouts\n"
    "└ Non-KYC casino payments\n"
    "\n"
    "🔺 <b>CUSTOM DEVELOPMENT</b>\n"
    "└ Terminal &amp; file scripts\n"
    "└ Automation\n"
    "└ Data extraction\n"
    "└ Private tools\n"
    "\n"
    "🔺 <b>CUSTOM VPN INFRASTRUCTURE</b>\n"
    "└ Private VPN servers\n"
    "└ Custom clients\n"
    "\n"
    "<b>UNETHICAL QUOTES OPEN</b>\n"
    "\n"
    '🌐 <a href="https://percentshop.dev">Visit Percent Shop’s Website!</a>'
)

CONTACT_TEXT = (
    "<b>INQUIRIES</b>💬\n"
    "\n"
    "Text Lick for all inquiries.\n"
    "\n"
    '<a href="https://t.me/drainware">@drainware</a>\n'
    "\n"
    "Text for quotes, pricing, and project inquiries."
)

WELCOME_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "📩 Contact / Inquire", "callback_data": "contact"}],
    ]
}

CONTACT_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "💬 Message @drainware", "url": "https://t.me/drainware"}],
        [{"text": "⬅️ Back", "callback_data": "home"}],
    ]
}


def telegram(method, **params):
    token = os.environ["BOT_TOKEN"]
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(params).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def screen(method, chat_id, text, keyboard, message_id=None):
    reply = {
        "method": method,
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": keyboard,
    }
    if message_id is not None:
        reply["message_id"] = message_id
    return reply


def command(text):
    return text.split(" ")[0].split("@")[0]


def build_reply(update):
    """Return the Telegram method call to send back, or None."""
    message = update.get("message")
    if message:
        cmd = command(message.get("text", ""))
        chat_id = message["chat"]["id"]
        if cmd in ("/start", "/menu"):
            return screen("sendMessage", chat_id, WELCOME_TEXT, WELCOME_KEYBOARD)
        if cmd == "/contact":
            return screen("sendMessage", chat_id, CONTACT_TEXT, CONTACT_KEYBOARD)
        return None

    query = update.get("callback_query")
    if query:
        # Stop the loading spinner on the button right away.
        try:
            telegram("answerCallbackQuery", callback_query_id=query["id"])
        except Exception as e:
            print(f"answerCallbackQuery failed: {e}")
        msg = query.get("message")
        if not msg:
            return None
        chat_id = msg["chat"]["id"]
        if query.get("data") == "contact":
            return screen("editMessageText", chat_id, CONTACT_TEXT, CONTACT_KEYBOARD, msg["message_id"])
        if query.get("data") == "home":
            return screen("editMessageText", chat_id, WELCOME_TEXT, WELCOME_KEYBOARD, msg["message_id"])
    return None


class handler(BaseHTTPRequestHandler):
    def _respond(self, status, body=None):
        data = json.dumps(body).encode("utf-8") if body is not None else b""
        self.send_response(status)
        if body is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._respond(200, {"ok": True, "bot": "PERCENT SHOP OTC"})

    def do_POST(self):
        secret = os.environ.get("WEBHOOK_SECRET")
        if secret and self.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
            self._respond(403)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            update = json.loads(self.rfile.read(length) or b"{}")
            reply = build_reply(update)
        except Exception as e:
            print(f"Error handling update: {e}")
            reply = None
        if reply:
            self._respond(200, reply)
        else:
            self._respond(200)
