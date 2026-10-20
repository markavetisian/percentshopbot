"""PERCENT SHOP OTC Telegram bot.

Dependency-free (standard library only). Uses long polling.
Set BOT_TOKEN in the environment (or in a .env file next to this script).
"""

import json
import os
import time
import urllib.error
import urllib.request

WELCOME_TEXT = (
    "Welcome to <b>PERCENT SHOP OTC</b>.\n"
    "A marketplace for digital goods, unethical software, crypto payment "
    "infrastructure, Telegram assets, and private development services.\n"
    "\n"
    "🔺<b>SOFTWARE</b>\n"
    "• Custom / unethical software, tools, scripts &amp; web apps\n"
    "\n"
    "🔺<b>CRYPTO PAYMENTS</b>\n"
    "• TON / USDT payment systems, crypto checkouts &amp; non-KYC casino "
    "payment infrastructure\n"
    "\n"
    "🔺<b>TELEGRAM</b>\n"
    "• Usernames, digital assets &amp; custom Telegram solutions\n"
    "\n"
    "🔺<b>CUSTOM DEVELOPMENT</b>\n"
    "• Terminal &amp; file scripts, automation, data extraction, API "
    "integrations &amp; private tools\n"
    "\n"
    "🔺<b>CUSTOM VPN INFRASTRUCTURE</b>\n"
    "• Private VPN servers &amp; custom clients\n"
    "\n"
    "Unethical quotes open.\n"
    "\n"
    '🌐 <a href="https://percentshop.dev">Percent Shop</a>'
)

CONTACT_TEXT = (
    "<b>CONTACT / INQUIRIES</b>\n"
    "\n"
    "For custom development, software, crypto payment systems, VPN "
    "infrastructure, OTC deals, or custom requests:\n"
    "\n"
    '<a href="https://t.me/drainware">@drainware</a>\n'
    "\n"
    "DM for quotes, pricing, and project inquiries."
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


def load_token():
    token = os.environ.get("BOT_TOKEN")
    if token:
        return token.strip()
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                key, _, value = line.strip().partition("=")
                if key == "BOT_TOKEN" and value:
                    return value.strip().strip('"').strip("'")
    raise SystemExit("BOT_TOKEN is not set. Put it in the environment or in .env")


class Bot:
    def __init__(self, token):
        self.base = f"https://api.telegram.org/bot{token}/"

    def call(self, method, timeout=60, **params):
        data = json.dumps(params).encode("utf-8")
        req = urllib.request.Request(
            self.base + method,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if not result.get("ok"):
            raise RuntimeError(f"{method} failed: {result}")
        return result["result"]

    def send(self, chat_id, text, keyboard):
        return self.call(
            "sendMessage",
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=keyboard,
        )

    def edit(self, chat_id, message_id, text, keyboard):
        return self.call(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=keyboard,
        )

    def handle_update(self, update):
        message = update.get("message")
        if message and message.get("text", "").split("@")[0].split(" ")[0] in (
            "/start",
            "/menu",
        ):
            self.send(message["chat"]["id"], WELCOME_TEXT, WELCOME_KEYBOARD)
            return
        if message and message.get("text", "").split("@")[0].split(" ")[0] == "/contact":
            self.send(message["chat"]["id"], CONTACT_TEXT, CONTACT_KEYBOARD)
            return

        query = update.get("callback_query")
        if query:
            self.call("answerCallbackQuery", callback_query_id=query["id"])
            msg = query.get("message")
            if not msg:
                return
            chat_id = msg["chat"]["id"]
            if query.get("data") == "contact":
                self.edit(chat_id, msg["message_id"], CONTACT_TEXT, CONTACT_KEYBOARD)
            elif query.get("data") == "home":
                self.edit(chat_id, msg["message_id"], WELCOME_TEXT, WELCOME_KEYBOARD)

    def run(self):
        me = self.call("getMe")
        print(f"Running as @{me['username']}")
        offset = None
        while True:
            try:
                params = {"timeout": 50, "allowed_updates": ["message", "callback_query"]}
                if offset is not None:
                    params["offset"] = offset
                updates = self.call("getUpdates", timeout=60, **params)
                for update in updates:
                    offset = update["update_id"] + 1
                    try:
                        self.handle_update(update)
                    except Exception as e:
                        print(f"Error handling update: {e}")
            except (urllib.error.URLError, TimeoutError, RuntimeError) as e:
                print(f"Polling error: {e}. Retrying in 3s")
                time.sleep(3)


if __name__ == "__main__":
    Bot(load_token()).run()
