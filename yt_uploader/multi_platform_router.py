"""
Omni-Channel Multi-Platform Distribution Router.
Seamlessly routes and publishes videos across YouTube Studio, Rumble, and other platforms
according to user natural language commands from Chat or WebUI Dashboard.
"""

import os
import sys
import re
import json
from typing import Dict, Any, List, Optional
from loguru import logger

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from yt_uploader.channel_manager import load_channels, auto_detect_channel
from yt_uploader.rumble_uploader import load_rumble_channels, auto_detect_rumble_channel

def parse_multi_platform_intent(prompt: str) -> Dict[str, Any]:
    """
    Parses natural language prompt for platforms, quantities, and channels.
    Examples:
    - "5 psychology videos banao aur rumble aur youtube dono pe upload karo"
    - "3 trading videos banao aur sirf rumble pe daalo"
    - "1 video banao aur unlisted youtube pe upload karo"
    """
    p_lower = prompt.lower()
    
    # 1. Detect Platforms
    platforms = []
    has_yt = any(k in p_lower for k in ["youtube", "yt", "studio", "चैनल"])
    has_rumble = any(k in p_lower for k in ["rumble", "रंबल"])
    
    if has_rumble and has_yt:
        platforms = ["youtube", "rumble"]
    elif has_rumble:
        platforms = ["rumble"]
    elif has_yt or "upload" in p_lower or "अपलोड" in p_lower:
        platforms = ["youtube"]
    else:
        # Default if auto-upload requested without explicit platform name
        platforms = ["youtube"]

    # 2. Detect Count
    count_match = re.search(r"\b(\d+)\s*(?:[a-zA-Z\s]{0,20})?(?:video|videos|वीडियो|क्लिप)\b", p_lower)
    video_count = int(count_match.group(1)) if count_match else 1

    # 3. Detect Niche / Channel Topic
    niche = "psychology"
    if any(k in p_lower for k in ["trading", "market", "stock", "forex", "finance", "nifty"]):
        niche = "trading"
    elif any(k in p_lower for k in ["tech", "ai", "artificial intelligence", "robot"]):
        niche = "tech"

    # 4. Resolve Channels
    yt_channels = load_channels()
    rumble_channels = load_rumble_channels()

    resolved_yt = "channel_trading" if niche == "trading" else "channel_psychology"
    if resolved_yt not in yt_channels and yt_channels:
        resolved_yt = list(yt_channels.keys())[0]

    resolved_rumble = "rumble_trading" if niche == "trading" else "rumble_psychology"
    if resolved_rumble not in rumble_channels and rumble_channels:
        resolved_rumble = list(rumble_channels.keys())[0]

    # 5. Visibility / Licensing
    visibility = "unlisted" if any(k in p_lower for k in ["unlisted", "अनलिस्टेड", "private"]) else "public"
    rumble_license = "exclusive" if "exclusive" in p_lower else "rumble_only"

    return {
        "platforms": platforms,
        "video_count": video_count,
        "niche": niche,
        "youtube_channel": resolved_yt,
        "rumble_channel": resolved_rumble,
        "visibility": visibility,
        "rumble_license": rumble_license,
        "clean_topic": re.sub(r"\b(?:youtube|rumble|upload|pe|par|dono|karo|banao|videos?)\b", "", prompt, flags=re.IGNORECASE).strip()
    }

def dispatch_to_platforms(
    video_path: str,
    seo_package: dict,
    platforms: Optional[List[str]] = None,
    youtube_channel: Optional[str] = None,
    rumble_channel: Optional[str] = None,
    visibility: str = "unlisted",
    rumble_license: str = "rumble_only",
    headless: bool = True
) -> Dict[str, Any]:
    """
    Executes automated upload to all target platforms.
    """
    if platforms is None:
        platforms = ["youtube"]

    results = {
        "video_path": video_path,
        "dispatched_platforms": platforms,
        "youtube": None,
        "rumble": None,
        "all_successful": True
    }

    # 1. YouTube Upload
    if "youtube" in platforms:
        try:
            logger.info(f"▶️ Executing YouTube Upload -> Channel: {youtube_channel}...")
            from yt_uploader.studio_uploader import upload_video_to_studio
            from yt_uploader.channel_manager import load_channels

            yt_channels = load_channels()
            ch_info = yt_channels.get(youtube_channel) or list(yt_channels.values())[0]
            profile_dir = ch_info.get("profile_dir")

            # Ensure visibility is set
            seo_copy = seo_package.copy()
            seo_copy["visibility"] = visibility

            yt_res = upload_video_to_studio(
                channel_profile_dir=profile_dir,
                video_file_path=video_path,
                thumbnail_file_path="",  # STRICT ZERO THUMBNAILS PER USER MANDATE
                seo_package=seo_copy,
                headless=headless
            )
            results["youtube"] = yt_res
            if not yt_res.get("success"):
                results["all_successful"] = False
        except Exception as e:
            logger.error(f"YouTube Dispatch failed: {e}")
            results["youtube"] = {"success": False, "error": str(e)}
            results["all_successful"] = False

    # 2. Rumble Upload
    if "rumble" in platforms:
        try:
            logger.info(f"▶️ Executing Rumble Upload -> Channel: {rumble_channel}...")
            from yt_uploader.rumble_uploader import upload_video_to_rumble

            rum_res = upload_video_to_rumble(
                channel_key=rumble_channel or "rumble_general",
                video_file_path=video_path,
                seo_package=seo_package,
                license_type=rumble_license,
                headless=headless
            )
            results["rumble"] = rum_res
            if not rum_res.get("success"):
                results["all_successful"] = False
        except Exception as e:
            logger.error(f"Rumble Dispatch failed: {e}")
            results["rumble"] = {"success": False, "error": str(e)}
            results["all_successful"] = False

    logger.success(f"🏁 Multi-Platform Dispatch Completed: {results}")
    return results
