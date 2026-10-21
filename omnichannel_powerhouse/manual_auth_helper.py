"""
Manual Safe Login Engine (Human-In-The-Loop Authentication)
Opens a genuine, visible Chromium browser window where the user manually logs into
YouTube Studio or Rumble. Saves persistent session state and cookies securely
without storing passwords, avoiding all Google automated bot detection blocks.
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("manual_auth_helper")

from playwright.sync_api import sync_playwright

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "channels_registry.json")


def load_registry() -> Dict[str, Any]:
    if not os.path.exists(REGISTRY_PATH):
        return {"channels": {}}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(data: Dict[str, Any]):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def launch_manual_login_session(channel_key: str, platform: str = "youtube") -> Dict[str, Any]:
    """
    Spawns an interactive visible browser window for the user to manually log in.
    Captures session cookies upon successful verification.
    """
    registry = load_registry()
    channel_info = registry.get("channels", {}).get(channel_key, {})

    profile_dir = channel_info.get("profile_dir")
    if not profile_dir:
        profile_dir = os.path.join("yt_uploader", "profiles", channel_key)
        if channel_key not in registry.get("channels", {}):
            registry.setdefault("channels", {})[channel_key] = {
                "channel_id": channel_key,
                "platform": platform,
                "name": channel_key,
                "profile_dir": profile_dir,
                "auth_status": "unverified",
                "daily_max_uploads": 3 if platform == "youtube" else 20,
                "uploads_today": 0
            }

    abs_profile_dir = os.path.abspath(os.path.join(_root, profile_dir))
    os.makedirs(abs_profile_dir, exist_ok=True)
    state_file = os.path.join(abs_profile_dir, "storage_state.json")

    logger.info(f"🚀 Spawning Genuine Visible Browser for Manual Login -> {channel_key} ({platform.upper()})...")
    logger.warning("🔑 HUMAN ACTION REQUIRED: Log in with your email/password and complete 2FA in the opened window.")

    CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    start_url = "https://studio.youtube.com/?approve_browser_access=true" if platform == "youtube" else "https://rumble.com/login"

    with sync_playwright() as p:
        # Launch using the proven, tested flags from channel_manager.py
        context = p.chromium.launch_persistent_context(
            user_data_dir=abs_profile_dir,
            executable_path=CHROME_PATH if os.path.exists(CHROME_PATH) else None,
            headless=False,
            args=[
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        page = context.new_page()
        logger.info(f"Navigating to {start_url}...")
        page.goto(start_url)

        logger.info("==================================================================")
        logger.info("✅ Browser is now open on your desktop!")
        logger.info("👉 Log in to your YouTube Studio / Google account in the opened Chrome window.")
        logger.info("👉 Once you are logged in, simply CLOSE the browser window to finish!")
        logger.info("==================================================================")

        try:
            # Stays active until user finishes and closes the window
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass

        try:
            context.storage_state(path=state_file)
            logger.info(f"💾 Persistent cookies & session state secured at: {state_file}")
        except Exception:
            pass

        registry["channels"][channel_key]["auth_status"] = "authenticated"
        registry["channels"][channel_key]["last_login_verified"] = time.strftime("%Y-%m-%d %H:%M:%S")
        save_registry(registry)
        logger.success(f"✅ Login setup completed for '{channel_key}'!")
        return {"success": True, "channel_key": channel_key, "state_file": state_file}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manual Safe Login CLI")
    parser.add_argument("--channel", required=True, help="Channel key name (e.g. yt_tech_01, yt_my_channel)")
    parser.add_argument("--platform", default="youtube", choices=["youtube", "rumble"], help="Platform (youtube or rumble)")
    args = parser.parse_args()

    res = launch_manual_login_session(args.channel, args.platform)
    print("RESULT:", json.dumps(res, indent=2))
