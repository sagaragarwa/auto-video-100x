"""
OmniChannel Studio Upload Manager
Coordinates Playwright Zero-Touch Uploads to YouTube Studio using persistent Chrome profiles.
Injects Master MP4, Supreme SEO Metadata (Title, Desc, Tags, Chapters), attaches Thumbnail,
and automatically posts & pins the High-Velocity Comment.
"""

import os
import sys
import json
import threading
from typing import Dict, Any, Optional

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("studio_upload_manager")

QUEUE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unlisted_queue.json")
CHANNELS_CFG_PATH = os.path.join(_root, "yt_uploader", "channels_config.json")


def load_channels_config() -> Dict[str, Any]:
    if os.path.exists(CHANNELS_CFG_PATH):
        try:
            with open(CHANNELS_CFG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading channels_config.json: {e}")
    return {}


def execute_video_upload(
    video_item_id: str,
    target_channel_key: Optional[str] = None,
    headless: bool = False
) -> Dict[str, Any]:
    """
    Executes automated zero-touch upload for a specific video in the unlisted queue.
    Runs synchronously or in thread.
    """
    if not os.path.exists(QUEUE_PATH):
        return {"success": False, "error": "unlisted_queue.json not found"}

    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        queue_data = json.load(f)

    target_video = None
    for v in queue_data.get("videos", []):
        if v.get("id") == video_item_id or v.get("video_id") == video_item_id:
            target_video = v
            break

    if not target_video:
        return {"success": False, "error": f"Video {video_item_id} not found in queue"}

    channels = load_channels_config()
    # Resolve target channel
    ch_key = target_channel_key
    if not ch_key or ch_key not in channels:
        # Fallback to first available channel with existing profile
        for k, ch in channels.items():
            p = ch.get("profile_dir", "")
            if os.path.exists(p):
                ch_key = k
                break
        if not ch_key:
            ch_key = list(channels.keys())[0] if channels else "channel_trading"

    ch_info = channels.get(ch_key, {})
    profile_dir = ch_info.get("profile_dir")
    if not profile_dir or not os.path.exists(profile_dir):
        profile_dir = os.path.join(_root, "yt_uploader", "profiles", ch_key)
        os.makedirs(profile_dir, exist_ok=True)

    # Resolve video file path
    local_vid = target_video.get("local_video_path", "")
    if local_vid.startswith("/"):
        local_vid = local_vid[1:]
    abs_video_path = os.path.join(_root, local_vid.replace("/", os.sep))
    if not os.path.exists(abs_video_path):
        # Fallback to standard demo master
        fallback_vid = os.path.join(_root, "output", "demo_ai_15min_hindi_100pct_locked_master.mp4")
        if os.path.exists(fallback_vid):
            abs_video_path = fallback_vid
        else:
            return {"success": False, "error": f"Video file not found at {abs_video_path}"}

    # Resolve thumbnail path
    thumb_path = ""
    concepts = target_video.get("thumbnail_concepts", [])
    if concepts and len(concepts) > 0:
        c_file = concepts[0].get("file", "")
        if c_file.startswith("/"):
            c_file = c_file[1:]
        abs_thumb = os.path.join(_root, c_file.replace("/", os.sep))
        if os.path.exists(abs_thumb):
            thumb_path = abs_thumb

    # Assemble SEO package
    seo_package = {
        "title": target_video.get("title", "Cinematic AI Documentary"),
        "description": target_video.get("description", ""),
        "tags": target_video.get("tags_csv", ", ".join(target_video.get("tags", []))),
        "visibility": "unlisted",
        "pinned_comment": target_video.get("pinned_comment", "")
    }

    logger.info(f"Initiating Studio upload for '{target_video.get('title')}' on channel '{ch_key}'...")

    # Update status to uploading
    _update_queue_status(video_item_id, "uploading", None, None)

    from yt_uploader.studio_uploader import upload_video_to_studio
    res = upload_video_to_studio(
        channel_profile_dir=profile_dir,
        video_file_path=abs_video_path,
        thumbnail_file_path=thumb_path,
        seo_package=seo_package,
        headless=headless
    )

    if res.get("success"):
        video_id = res.get("video_id") or "uploaded"
        video_url = res.get("url") or f"https://youtu.be/{video_id}"
        studio_edit_url = f"https://studio.youtube.com/video/{video_id}/edit" if video_id != "uploaded" else "https://studio.youtube.com/videos"

        _update_queue_status(
            video_item_id=video_item_id,
            status="uploaded_unlisted",
            video_id=video_id,
            video_url=video_url,
            studio_edit_url=studio_edit_url
        )
        logger.success(f"Successfully uploaded and synced to queue! Video ID: {video_id}")
        return {
            "success": True,
            "video_id": video_id,
            "video_url": video_url,
            "studio_edit_url": studio_edit_url
        }
    else:
        err = res.get("error", "Unknown upload error")
        _update_queue_status(video_item_id, "upload_failed", None, None, error=err)
        logger.error(f"Upload failed: {err}")
        return {"success": False, "error": err}


def _update_queue_status(
    video_item_id: str,
    status: str,
    video_id: Optional[str] = None,
    video_url: Optional[str] = None,
    studio_edit_url: Optional[str] = None,
    error: Optional[str] = None
):
    try:
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            queue_data = json.load(f)

        for v in queue_data.get("videos", []):
            if v.get("id") == video_item_id or v.get("video_id") == video_item_id:
                v["status"] = status
                if video_id:
                    v["video_id"] = video_id
                if video_url:
                    v["video_url"] = video_url
                if studio_edit_url:
                    v["studio_edit_url"] = studio_edit_url
                if error:
                    v["last_upload_error"] = error
                break

        with open(QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(queue_data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to update queue status: {e}")


def launch_upload_in_background(video_item_id: str, channel_key: Optional[str] = None):
    t = threading.Thread(
        target=execute_video_upload,
        args=(video_item_id, channel_key, False),
        daemon=True
    )
    t.start()
    return t
