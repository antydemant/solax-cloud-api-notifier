import requests
import time
import json
import os
from dotenv import load_dotenv
from translations import get_translation

load_dotenv()

# Load translations
_ = get_translation()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError(_("❌ TELEGRAM_TOKEN is not set in the environment variables."))
    
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

SUBSCRIBERS_FILE = "subscribers.json"

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(list(subs), f)

def get_updates(offset=None):
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    resp = requests.get(f"{TELEGRAM_API}/getUpdates", params=params, timeout=60)
    return resp.json()

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

def main():
    print(_("▶️ Subscriber collector started..."))
    subscribers = load_subscribers()
    last_update_id = None

    updates = get_updates(last_update_id + 1 if last_update_id else None)
    if updates.get("ok"):
        for u in updates["result"]:
            last_update_id = u["update_id"]
            msg = u.get("message")
            if not msg:
                continue
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")

            if text.strip().lower() == "/start":
                if chat_id not in subscribers:
                    subscribers.add(chat_id)
                    save_subscribers(subscribers)
                    send_message(chat_id, _("✅ You are subscribed to power notifications ⚡️"))
                    print(_("➕ New subscriber: {chat_id}").format(chat_id=chat_id))
                # else:
                #     send_message(chat_id, _("ℹ️ You are already subscribed."))

if __name__ == "__main__":
    main()
