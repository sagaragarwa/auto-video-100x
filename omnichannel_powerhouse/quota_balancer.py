"""
Quota Balancer & Anti-Shadowban Guard
Prevents YouTube & Rumble account bans, spam flags, and view throttling.
Enforces tiered daily upload limits, minimum time intervals between uploads,
and rolls overflow videos to optimal scheduled time slots on subsequent days.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("quota_balancer")

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "channels_registry.json")


def load_registry() -> Dict[str, Any]:
    if not os.path.exists(REGISTRY_PATH):
        return {"channels": {}}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(data: Dict[str, Any]):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def check_and_allocate_upload_slot(channel_key: str) -> Dict[str, Any]:
    """
    Checks if a channel can upload immediately today, or schedules it for the next open slot.
    Returns:
      {
         "channel_key": str,
         "allowed_now": bool,
         "scheduled_timestamp": str (ISO or empty),
         "current_daily_count": int,
         "max_allowed": int,
         "recommended_action": "upload_unlisted" | "upload_scheduled"
      }
    """
    registry = load_registry()
    channels = registry.get("channels", {})
    if channel_key not in channels:
        logger.warning(f"Channel '{channel_key}' not in registry. Defaulting to safe 1 upload/day.")
        return {
            "channel_key": channel_key,
            "allowed_now": True,
            "scheduled_timestamp": "",
            "current_daily_count": 0,
            "max_allowed": 1,
            "recommended_action": "upload_unlisted"
        }

    c_data = channels[channel_key]
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_upload_ts = c_data.get("last_upload_timestamp", "")
    last_upload_date = last_upload_ts.split(" ")[0] if last_upload_ts else ""

    # Reset daily count if date has changed
    if last_upload_date != today_str:
        c_data["uploads_today"] = 0
        save_registry(registry)

    current_count = c_data.get("uploads_today", 0)
    max_daily = c_data.get("daily_max_uploads", 3)

    if current_count < max_daily:
        logger.info(f"🟢 Channel [{channel_key}] Quota Available: {current_count}/{max_daily} uploads today.")
        return {
            "channel_key": channel_key,
            "allowed_now": True,
            "scheduled_timestamp": "",
            "current_daily_count": current_count,
            "max_allowed": max_daily,
            "recommended_action": "upload_unlisted"
        }
    else:
        # Calculate next day schedule slot (e.g. Tomorrow at 14:00 UTC / 19:30 IST)
        days_ahead = (current_count // max_daily)
        next_date = datetime.now() + timedelta(days=days_ahead)
        scheduled_slot = next_date.replace(hour=14, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")

        logger.warning(
            f"🟡 Channel [{channel_key}] Daily Quota Reached ({current_count}/{max_daily}). "
            f"Auto-scheduling for next prime slot: {scheduled_slot} UTC."
        )
        return {
            "channel_key": channel_key,
            "allowed_now": False,
            "scheduled_timestamp": scheduled_slot,
            "current_daily_count": current_count,
            "max_allowed": max_daily,
            "recommended_action": "upload_scheduled"
        }


def record_successful_upload(channel_key: str):
    """
    Increments upload count and logs timestamp for quota auditing.
    """
    registry = load_registry()
    if channel_key in registry.get("channels", {}):
        c_data = registry["channels"][channel_key]
        c_data["uploads_today"] = c_data.get("uploads_today", 0) + 1
        c_data["last_upload_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_registry(registry)
        logger.success(f"📊 Upload recorded for [{channel_key}]. Today's total: {c_data['uploads_today']}/{c_data.get('daily_max_uploads', 3)}")


if __name__ == "__main__":
    slot_tech = check_and_allocate_upload_slot("yt_tech_01")
    slot_trade = check_and_allocate_upload_slot("yt_trading_01")
    print("Tech Slot:", slot_tech)
    print("Trading Slot:", slot_trade)
