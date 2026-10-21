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

    start_url = "https://studio.youtube.com" if platform == "youtube" else "https://rumble.com/login"

    with sync_playwright() as p:
        # Prefer genuine installed Google Chrome if present on the machine
        chrome_installed = os.path.exists(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        launch_kwargs = {
            "user_data_dir": abs_profile_dir,
            "headless": False,
            "viewport": {"width": 1280, "height": 800},
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ],
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        if chrome_installed:
            launch_kwargs["channel"] = "chrome"

        context = p.chromium.launch_persistent_context(**launch_kwargs)

        page = context.pages[0] if context.pages else context.new_page()
        page.goto(start_url)

        logger.info("⏳ Waiting for user to complete manual login. You have up to 5 minutes...")

        authenticated = False
        t_start = time.time()

        # Check loop: wait until user is visibly logged in
        while time.time() - t_start < 300:
            current_url = page.url.lower()

            if platform == "youtube":
                # User reached YouTube Studio dashboard
                if "studio.youtube.com/channel/" in current_url or ("studio.youtube.com" in current_url and "accounts.google.com" not in current_url):
                    time.sleep(3)
                    authenticated = True
                    break
            elif platform == "rumble":
                # User reached Rumble account / dashboard
                if "rumble.com/account" in current_url or ("rumble.com" in current_url and "login" not in current_url and page.locator("a[href*='/account']").count() > 0):
                    time.sleep(3)
                    authenticated = True
                    break

            time.sleep(2)

        if authenticated:
            logger.success(f"✅ Manual Login Verified for {channel_key}!")
            # Extract storage state
            context.storage_state(path=state_file)
            logger.info(f"💾 Persistent cookies & session state secured at: {state_file}")

            # Inspect channel details if possible
            detected_name = channel_info.get("name", channel_key)
            try:
                if platform == "youtube":
                    # Attempt to extract channel title from page
                    title_elem = page.locator("#channel-title, #entity-name").first
                    if title_elem.count() > 0:
                        detected_name = title_elem.inner_text().strip()
            except Exception:
                pass

            # Update registry
            registry["channels"][channel_key]["auth_status"] = "authenticated"
            registry["channels"][channel_key]["name"] = detected_name
            registry["channels"][channel_key]["last_login_verified"] = time.strftime("%Y-%m-%d %H:%M:%S")
            save_registry(registry)

            context.close()
            return {"success": True, "channel_key": channel_key, "name": detected_name, "state_file": state_file}
        else:
            logger.error("❌ Login timed out after 300 seconds without verification.")
            context.close()
            return {"success": False, "error": "Login timed out"}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manual Safe Login CLI")
    parser.add_argument("--channel", required=True, help="Channel key name (e.g. yt_tech_01, yt_my_channel)")
    parser.add_argument("--platform", default="youtube", choices=["youtube", "rumble"], help="Platform (youtube or rumble)")
    args = parser.parse_args()

    res = launch_manual_login_session(args.channel, args.platform)
    print("RESULT:", json.dumps(res, indent=2))
