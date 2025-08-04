import json
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from translations import get_translation

load_dotenv()

# Load translations
_ = get_translation()

SOLAX_API_URL = os.getenv("SOLAX_API_URL")
if not SOLAX_API_URL:
    raise ValueError(_("❌ SOLAX_API_URL is not set in the environment variables."))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError(_("❌ TELEGRAM_TOKEN is not set in the environment variables."))

SOLAX_TOKEN = os.getenv("SOLAX_TOKEN")
if not SOLAX_TOKEN:
    raise ValueError(_("❌ SOLAX_TOKEN is not set in the environment variables."))

SOLAX_SN = os.getenv("SOLAX_SN")
if not SOLAX_SN:
    raise ValueError(_("❌ SOLAX_SN is not set in the environment variables."))

SUBSCRIBERS_FILE = "subscribers.json"


def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    return []


def send_telegram_to_all(text: str):
    subs = load_subscribers()
    for chat_id in subs:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
        except Exception as error:
            print(
                _("❌ Failed to send message to {chat_id}: {e}").format(
                    chat_id=chat_id, e=error
                )
            )


def now():
    return datetime.now()


def now_str():
    return now().strftime("%d.%m.%Y %H:%M:%S")


def current_year():
    return datetime.now().strftime("%Y")


def state_file():
    return f"solax_state_{current_year()}.json"


def get_inverter_status():
    params = {"tokenId": SOLAX_TOKEN, "sn": SOLAX_SN}
    try:
        r = requests.get(SOLAX_API_URL, params=params, timeout=10)
        data = r.json()
        if data.get("success") and "result" in data:
            return data["result"]
        else:
            print(_("❌ API returned an error:"), data)
            return None
    except Exception as e:
        print(_("❌ API error:"), e)
        return None


def load_state():
    if os.path.exists(state_file()):
        with open(state_file(), "r") as f:
            return json.load(f)
    return {
        "grid_status": None,
        "inverter_online": True,
        "last_off_time": None,
        "history": [],
    }


def save_state(state):
    with open(state_file(), "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def add_history_entry(state, event_type, message):
    state["history"].append(
        {"time": now_str(), "event": event_type, "message": message}
    )


def format_duration(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if hours:
        parts.append(_("{hours} hours").format(hours=hours))
    if minutes:
        parts.append(_("{minutes} minutes").format(minutes=minutes))
    if seconds and not hours:  # Show seconds only for short outages
        parts.append(_("{seconds} seconds").format(seconds=seconds))
    return " ".join(parts) if parts else _("0 seconds")


def detect_grid_status(status):
    """Returns 'ON', 'OFF', or None (unknown)"""
    feedinpower = status.get("feedinpower", 0) or 0
    acpower = status.get("acpower", 0) or 0

    if feedinpower != 0:
        return "ON"

    if feedinpower == 0 and acpower > 0:
        return "OFF"

    return None


def main():
    prev_state = load_state()
    prev_grid_status = prev_state.get("grid_status")
    prev_inverter_online = prev_state.get("inverter_online", True)

    status = get_inverter_status()

    if status:
        upload_time_str = status.get("uploadTime")
        if upload_time_str:
            upload_time = datetime.strptime(upload_time_str, "%Y-%m-%d %H:%M:%S")
            if now() - upload_time > timedelta(minutes=5):
                if prev_inverter_online:
                    msg = _(
                        "🚨 Inverter has not updated data >5 minutes ({time})"
                    ).format(time=now_str())
                    send_telegram_to_all(msg)
                    add_history_entry(prev_state, "inverter_offline", msg)
                prev_state["inverter_online"] = False
                save_state(prev_state)
                return

        if not prev_inverter_online:
            msg = _("✅ Inverter is back online ({time})").format(time=now_str())
            send_telegram_to_all(msg)
            add_history_entry(prev_state, "inverter_online", msg)
        prev_state["inverter_online"] = True

        current_grid_status = detect_grid_status(status)

        if current_grid_status is not None:
            soc = status.get("soc", 0)
            acpower = status.get("acpower", 0)
            feedin = status.get("feedinpower", 0)

            if prev_grid_status and current_grid_status != prev_grid_status:
                if current_grid_status == "OFF":
                    prev_state["last_off_time"] = now().isoformat()
                    msg = _(
                        "⚠️ Power went out! ⏰ {time}\nSOC: {soc}% | Home: {acpower}W | Grid: {feedin}W"
                    ).format(time=now_str(), soc=soc, acpower=acpower, feedin=feedin)
                else:
                    duration_str = ""
                    if prev_state.get("last_off_time"):
                        off_time = datetime.fromisoformat(prev_state["last_off_time"])
                        delta = now() - off_time
                        duration_str = _(" (out for {duration})").format(
                            duration=format_duration(delta)
                        )
                        prev_state["last_off_time"] = None

                    msg = _(
                        "✅ Power is back! ⏰ {time}{duration}\nSOC: {soc}% | Home: {acpower}W | Grid: {feedin}W"
                    ).format(
                        time=now_str(),
                        duration=duration_str,
                        soc=soc,
                        acpower=acpower,
                        feedin=feedin,
                    )

                send_telegram_to_all(msg)
                add_history_entry(
                    prev_state, f"grid_{current_grid_status.lower()}", msg
                )

            prev_state["grid_status"] = current_grid_status

    else:
        if prev_inverter_online:
            msg = _("🚨 Inverter is unavailable (API not responding) ⏰ {time}").format(
                time=now_str()
            )
            send_telegram_to_all(msg)
            add_history_entry(prev_state, "inverter_offline", msg)
        prev_state["inverter_online"] = False

    save_state(prev_state)


if __name__ == "__main__":
    main()
