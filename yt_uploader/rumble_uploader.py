"""
Rumble Multi-Channel Autonomous Persistent Uploader (No API Quotas).
Provides 1-click persistent login and zero-touch video publishing for Rumble:
- Multiple sub-channels and multi-account profile support
- Automated metadata injection (Title, Description, Tags, Category)
- Channel routing & Licensing automation (Rumble Only, Exclusive, Personal)
- Extract direct video URL and post-upload telemetry
"""

import os
import sys
import time
import json
import re
from typing import Dict, Any, Optional, List
from loguru import logger

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
RUMBLE_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rumble_config.json")
RUMBLE_PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles_rumble")

DEFAULT_RUMBLE_CONFIG = {
    "rumble_psychology": {
        "name": "Rumble Psychology & Mental Health",
        "profile_dir": os.path.join(RUMBLE_PROFILES_DIR, "rumble_psychology"),
        "sub_channel": "",
        "niche": "psychology",
        "license": "rumble_only"  # "rumble_only", "exclusive", "personal"
    },
    "rumble_trading": {
        "name": "Rumble Trading & Finance Channel",
        "profile_dir": os.path.join(RUMBLE_PROFILES_DIR, "rumble_trading"),
        "sub_channel": "",
        "niche": "trading",
        "license": "rumble_only"
    },
    "rumble_general": {
        "name": "Rumble Main / General Channel",
        "profile_dir": os.path.join(RUMBLE_PROFILES_DIR, "rumble_general"),
        "sub_channel": "",
        "niche": "general",
        "license": "rumble_only"
    }
}

def load_rumble_channels() -> Dict[str, Any]:
    os.makedirs(RUMBLE_PROFILES_DIR, exist_ok=True)
    if not os.path.exists(RUMBLE_CONFIG_FILE):
        save_rumble_channels(DEFAULT_RUMBLE_CONFIG)
        return DEFAULT_RUMBLE_CONFIG.copy()
    try:
        with open(RUMBLE_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure keys exist
            for k, v in DEFAULT_RUMBLE_CONFIG.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception as e:
        logger.error(f"Failed to read rumble_config.json: {e}")
        return DEFAULT_RUMBLE_CONFIG.copy()

def save_rumble_channels(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(RUMBLE_CONFIG_FILE), exist_ok=True)
    with open(RUMBLE_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def open_rumble_login_window(channel_key: str = "rumble_general") -> bool:
    """
    Opens real Chrome window with Rumble profile.
    User logs in manually ONCE. All cookies and tokens are permanently saved.
    """
    from playwright.sync_api import sync_playwright

    channels = load_rumble_channels()
    if channel_key not in channels:
        logger.error(f"Rumble Channel key '{channel_key}' not found in rumble_config.json")
        return False

    ch_info = channels[channel_key]
    profile_path = os.path.abspath(ch_info["profile_dir"])
    os.makedirs(profile_path, exist_ok=True)

    logger.info(f"Opening Chrome window for Rumble profile: '{ch_info['name']}'...")
    logger.info("Please log in to your Rumble account in the opened Chrome window.")
    logger.info("Once logged in to Rumble, close the browser window to complete setup.")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            executable_path=CHROME_PATH if os.path.exists(CHROME_PATH) else None,
            headless=False,
            args=[
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        page = context.new_page()
        page.goto("https://rumble.com/login.php", timeout=60000)
        page.wait_for_timeout(5000)

        logger.info("Browser is active. Log in to your Rumble account and close the window when done...")
        try:
            context.pages[0].wait_for_event("close", timeout=0)
        except Exception:
            pass

    logger.success(f"Rumble channel profile setup complete for '{channel_key}'! Cookies are permanently saved.")
    return True

def auto_detect_rumble_channel(video_name_or_subject: str) -> str:
    """
    Smart Channel Router for Rumble:
    Maps video subject to the appropriate Rumble channel key.
    """
    channels = load_rumble_channels()
    if not channels:
        return "rumble_general"

    text = video_name_or_subject.lower()
    if any(k in text for k in ["trading", "market", "stock", "crypto", "forex", "money", "paiso", "nifty"]):
        return "rumble_trading" if "rumble_trading" in channels else list(channels.keys())[0]
    elif any(k in text for k in ["psychology", "depression", "anxiety", "mind", "calm", "dopamine", "habit", "mental"]):
        return "rumble_psychology" if "rumble_psychology" in channels else list(channels.keys())[0]
    return "rumble_general" if "rumble_general" in channels else list(channels.keys())[0]

def upload_video_to_rumble(
    channel_key: str,
    video_file_path: str,
    seo_package: dict,
    license_type: str = "rumble_only",
    sub_channel_name: Optional[str] = None,
    headless: bool = False
) -> Dict[str, Any]:
    """
    Uploads a video to Rumble using persistent browser profile without API quota.
    1. Injects Title, Description, Tags, Category, and Sub-channel (if any).
    2. Selects Licensing (Rumble Only, Exclusive, Personal Use).
    3. Accepts Terms and Submits.
    4. Returns published Rumble URL.
    """
    from playwright.sync_api import sync_playwright

    if not os.path.exists(video_file_path):
        raise FileNotFoundError(f"Video file not found: {video_file_path}")

    channels = load_rumble_channels()
    ch_info = channels.get(channel_key, DEFAULT_RUMBLE_CONFIG.get("rumble_general"))
    profile_dir = os.path.abspath(ch_info["profile_dir"])
    effective_license = license_type or ch_info.get("license", "rumble_only")

    abs_video = os.path.abspath(video_file_path)
    title = seo_package.get("title", "Cinematic Master Documentary")[:100]
    description = seo_package.get("description", "")
    tags_list = seo_package.get("tags", [])
    if isinstance(tags_list, str):
        tags_str = tags_list
    else:
        tags_str = ", ".join(tags_list[:10])

    logger.info(f"🚀 Initiating Rumble Autonomous Upload via Profile: {profile_dir}")
    logger.info(f"Target Video: {abs_video}")
    logger.info(f"Title: {title}")
    logger.info(f"License: {effective_license.upper()}")

    result = {"success": False, "url": None, "error": None, "platform": "rumble", "channel": channel_key}

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=CHROME_PATH if os.path.exists(CHROME_PATH) else None,
            headless=headless,
            args=[
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        page = context.new_page()

        try:
            logger.info("Navigating to Rumble Upload Portal...")
            page.goto("https://rumble.com/upload.php", timeout=60000)
            page.wait_for_timeout(4000)

            # Check if login required
            if "login.php" in page.url or "signin" in page.url:
                result["error"] = f"Rumble profile '{channel_key}' not logged in. Run 'open_rumble_login_window' first."
                logger.error(result["error"])
                return result

            # 1. Inject Video File
            logger.info("Injecting video file into Rumble upload dropzone...")
            file_input = page.query_selector('input[type="file"]')
            if not file_input:
                file_input = page.wait_for_selector('input[type="file"]', timeout=30000)
            file_input.set_input_files(abs_video)
            logger.info("Video file attached. Waiting for Rumble form fields to populate...")
            page.wait_for_timeout(5000)

            # 2. Fill Title
            logger.info(f"Injecting Title: {title[:40]}...")
            title_el = (
                page.query_selector('input[name="title"]')
                or page.query_selector('#video-title')
                or page.query_selector('input#title')
            )
            if title_el:
                title_el.click()
                title_el.fill(title)
            else:
                logger.warning("Could not locate title field directly, trying generic input selector")
                page.fill('input[placeholder*="Title"]', title)

            # 3. Fill Description
            logger.info("Injecting Description...")
            desc_el = (
                page.query_selector('textarea[name="description"]')
                or page.query_selector('#video-description')
                or page.query_selector('textarea#description')
            )
            if desc_el:
                desc_el.click()
                desc_el.fill(description)

            # 4. Fill Tags
            if tags_str:
                logger.info("Injecting Tags...")
                tags_el = (
                    page.query_selector('input[name="tags"]')
                    or page.query_selector('#video-tags')
                    or page.query_selector('input[placeholder*="Tag"]')
                )
                if tags_el:
                    tags_el.click()
                    tags_el.fill(tags_str)

            # 5. Select Sub-Channel (if specified)
            target_sub = sub_channel_name or ch_info.get("sub_channel")
            if target_sub:
                logger.info(f"Selecting Rumble sub-channel: '{target_sub}'...")
                channel_select = page.query_selector('select[name="channel_id"]') or page.query_selector('#video-channel')
                if channel_select:
                    try:
                        channel_select.select_option(label=target_sub)
                    except Exception:
                        pass

            # 6. Click Primary Upload / Next Button
            logger.info("Clicking Upload / Continue button...")
            upload_btn = (
                page.query_selector('button#submit-button')
                or page.query_selector('input[type="submit"]')
                or page.query_selector('button:has-text("Upload")')
                or page.query_selector('button:has-text("Next")')
            )
            if upload_btn:
                upload_btn.click()
            else:
                page.keyboard.press("Enter")

            logger.info("Waiting for upload progress and licensing screen...")
            # Wait for licensing page or upload progress bar
            page.wait_for_timeout(6000)

            # 7. Licensing & Monetization Page
            logger.info(f"Setting License Option to: {effective_license}...")
            # Check for radio buttons for license
            if effective_license == "exclusive":
                lic_radio = page.query_selector('input[value="1"]') or page.query_selector('input#exclusive')
            elif effective_license == "personal":
                lic_radio = page.query_selector('input[value="3"]') or page.query_selector('input#personal')
            else:  # default "rumble_only"
                lic_radio = page.query_selector('input[value="2"]') or page.query_selector('input#rumble_only') or page.query_selector('input[value="rumble_player"]')

            if lic_radio:
                try:
                    lic_radio.check()
                except Exception:
                    lic_radio.click()

            # Agree to Terms checkboxes
            logger.info("Accepting Terms & Conditions...")
            terms_checkboxes = page.query_selector_all('input[type="checkbox"]')
            for cb in terms_checkboxes:
                try:
                    if not cb.is_checked():
                        cb.check()
                except Exception:
                    try:
                        cb.click()
                    except Exception:
                        pass

            page.wait_for_timeout(2000)

            # Final Submit Button
            logger.info("Submitting final publish request on Rumble...")
            submit_btn = (
                page.query_selector('button[type="submit"]:has-text("Submit")')
                or page.query_selector('input[value="Submit"]')
                or page.query_selector('button:has-text("Submit")')
                or page.query_selector('button#submit-button')
            )
            if submit_btn:
                submit_btn.click()
            else:
                page.keyboard.press("Enter")

            # Wait for redirect to completion screen with direct link
            page.wait_for_timeout(7000)
            final_url = page.url
            logger.info(f"Rumble post-publish URL: {final_url}")

            # Extract direct video link if available
            link_el = page.query_selector('a[href*="/v"]') or page.query_selector('input[value*="rumble.com"]')
            video_link = None
            if link_el:
                video_link = link_el.get_attribute("href") or link_el.get_attribute("value")
            if not video_link:
                video_link = final_url

            result["success"] = True
            result["url"] = video_link
            logger.success(f"🎉 RUMBLE UPLOAD SUCCESSFUL! Link: {video_link}")

        except Exception as e:
            logger.error(f"Rumble upload failed: {e}")
            result["error"] = str(e)
        finally:
            try:
                context.close()
            except Exception:
                pass

    return result
