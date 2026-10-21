import os
import sys
import time
import json
import zipfile
import subprocess
import requests
from loguru import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from yt_uploader.studio_uploader import upload_video_to_studio
from yt_uploader.thumbnail_generator import create_ultra_thumbnail

DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
GITHUB_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_config.json")
SERIES_TASKS_PATH = os.path.join(BASE_DIR, "series_tasks.json")

# Target queue mapping: 5 for Get Neural Stack Pro, 5 for Silicon Pulse
AUTOPILOT_QUEUE = [
    # --- Channel 1: Get Neural Stack Pro (AI & Tech) ---
    {
        "channel_key": "ai_and_tech",
        "channel_name": "Get Neural Stack Pro",
        "episode_number": 1,
        "punchline": "TRANSFORMER SECRETS!",
        "badge": "AI MASTERCLASS"
    },
    {
        "channel_key": "ai_and_tech",
        "channel_name": "Get Neural Stack Pro",
        "episode_number": 2,
        "punchline": "AGENT SWARMS!",
        "badge": "MCP ARCHITECTURE"
    },
    {
        "channel_key": "ai_and_tech",
        "channel_name": "Get Neural Stack Pro",
        "episode_number": 4,
        "punchline": "HOW AI THINKS!",
        "badge": "REASONING MODELS"
    },
    {
        "channel_key": "ai_and_tech",
        "channel_name": "Get Neural Stack Pro",
        "episode_number": 6,
        "punchline": "DATA WALL HIT!",
        "badge": "CHINCHILLA LAWS"
    },
    {
        "channel_key": "ai_and_tech",
        "channel_name": "Get Neural Stack Pro",
        "episode_number": 20,
        "punchline": "THE AGI ENDGAME!",
        "badge": "SUPERINTELLIGENCE"
    },

    # --- Channel 2: Silicon Pulse (Hardware, Chips & Trading) ---
    {
        "channel_key": "channel_trading",
        "channel_name": "Silicon Pulse",
        "episode_number": 5,
        "punchline": "THE 2NM WAR!",
        "badge": "ASML HIGH-NA EUV"
    },
    {
        "channel_key": "channel_trading",
        "channel_name": "Silicon Pulse",
        "episode_number": 15,
        "punchline": "GRID COLLAPSE!",
        "badge": "AI ENERGY CRISIS"
    },
    {
        "channel_key": "channel_trading",
        "channel_name": "Silicon Pulse",
        "episode_number": 16,
        "punchline": "OPTICAL COMPUTE!",
        "badge": "PHOTONIC CHIPS"
    },
    {
        "channel_key": "channel_trading",
        "channel_name": "Silicon Pulse",
        "episode_number": 18,
        "punchline": "HUMANOID FLEETS!",
        "badge": "PHYSICAL AI"
    },
    {
        "channel_key": "channel_trading",
        "channel_name": "Silicon Pulse",
        "episode_number": 3,
        "punchline": "NVIDIA BLACKWELL!",
        "badge": "SILICON MONOPOLY"
    }
]


def load_github_config():
    with open(GITHUB_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_task_metadata(episode_num: int):
    with open(SERIES_TASKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for task in data.get("tasks", []):
        if task.get("episode_number") == episode_num:
            return task
    raise ValueError(f"Task for Episode {episode_num} not found in series_tasks.json")


def ensure_video_downloaded(episode_num: int) -> str:
    """Checks if video exists in Downloads. If not, fetches artifact from GitHub via curl."""
    target_dest = os.path.join(DOWNLOADS_DIR, f"Episode_{episode_num:02d}_Master_1080p.mp4")
    if os.path.exists(target_dest) and os.path.getsize(target_dest) > 50 * 1024 * 1024:
        logger.info(f"Local verified video exists: {target_dest}")
        return target_dest

    # Check for specific named downloads
    for f in os.listdir(DOWNLOADS_DIR):
        if f.lower().endswith(".mp4") and f.startswith(f"Episode_{episode_num:02d}_") and "trading" not in f.lower() and "dark_pools" not in f.lower():
            candidate = os.path.join(DOWNLOADS_DIR, f)
            if os.path.getsize(candidate) > 50 * 1024 * 1024:
                logger.info(f"Local video matched: {candidate}")
                return candidate

    # Query GitHub Actions artifacts
    cfg = load_github_config()
    token = cfg.get("github_token", "")
    owner = cfg.get("repo_owner", "sagaragarwa")
    repo = cfg.get("repo_name", "auto-video-100x")
    headers = {"Authorization": f"token {token}", "User-Agent": "Autopilot"}

    logger.info(f"Querying GitHub Actions artifacts for Episode {episode_num}...")
    art_url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts?per_page=60"
    r = requests.get(art_url, headers=headers, timeout=15).json()

    target_artifact = None
    for a in r.get("artifacts", []):
        if a.get("name") == f"episode_{episode_num}_1080p":
            target_artifact = a
            break

    if not target_artifact:
        raise FileNotFoundError(f"Artifact episode_{episode_num}_1080p not found on GitHub Actions!")

    art_id = target_artifact["id"]
    size_mb = target_artifact["size_in_bytes"] / (1024 * 1024)
    logger.info(f"Downloading Episode {episode_num} artifact via fast curl (ID: {art_id}, {size_mb:.1f} MB)...")

    zip_url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts/{art_id}/zip"
    temp_zip_path = os.path.join(DOWNLOADS_DIR, f"temp_ep_{episode_num}.zip")

    cmd = [
        "curl.exe", "-s", "-L",
        "-H", f"Authorization: token {token}",
        "-H", "User-Agent: curl/8.0",
        "--retry", "3",
        "--retry-delay", "2",
        "-o", temp_zip_path,
        zip_url
    ]
    t0 = time.time()
    subprocess.run(cmd, check=True)
    logger.success(f"Downloaded artifact zip in {time.time() - t0:.1f}s!")

    extracted_video = None
    with zipfile.ZipFile(temp_zip_path, "r") as z:
        for z_name in z.namelist():
            if z_name.endswith(".mp4"):
                extracted_video = target_dest
                with z.open(z_name) as source, open(extracted_video, "wb") as target:
                    target.write(source.read())
                logger.success(f"Extracted video to: {extracted_video} ({os.path.getsize(extracted_video)/(1024*1024):.1f} MB)")
                break

    try:
        os.remove(temp_zip_path)
    except Exception:
        pass

    if not extracted_video or not os.path.exists(extracted_video):
        raise RuntimeError(f"Failed to extract video from artifact zip for Episode {episode_num}")

    return extracted_video


def run_single_episode_autopilot(item: dict, visibility: str = "unlisted"):
    """Full end-to-end processing for a single video item."""
    ep_num = item["episode_number"]
    ch_key = item["channel_key"]
    ch_name = item["channel_name"]

    logger.info("=" * 70)
    logger.info(f"STARTING AUTOPILOT FOR EPISODE {ep_num} -> CHANNEL: {ch_name} ({ch_key})")
    logger.info("=" * 70)

    # 1. Acquire Video
    video_path = ensure_video_downloaded(ep_num)

    # 2. Acquire SEO Metadata
    meta = load_task_metadata(ep_num)
    seo_package = {
        "title": meta.get("title", f"Episode {ep_num} Documentary")[:100],
        "description": meta.get("description", "")[:5000],
        "tags": ", ".join(meta.get("tags", []))[:500],
        "visibility": visibility
    }

    # 3. Create Custom 4K Thumbnail
    thumb_path = os.path.join(DOWNLOADS_DIR, f"Episode_{ep_num:02d}_Thumbnail.jpg")
    if not os.path.exists(thumb_path):
        logger.info(f"Generating high-CTR 4K thumbnail for Episode {ep_num}...")
        create_ultra_thumbnail(
            bg_image_or_video=video_path,
            output_path=thumb_path,
            punchline=item.get("punchline", "DEEP DOCUMENTARY"),
            badge_text=item.get("badge", "MUST WATCH")
        )

    # 4. Profile path
    profile_dir = os.path.join(BASE_DIR, "yt_uploader", "profiles", ch_key)

    # 5. Upload via Browser Automation
    logger.info(f"Dispatching upload to YouTube Studio for {ch_name}...")
    upload_res = upload_video_to_studio(
        channel_profile_dir=profile_dir,
        video_file_path=video_path,
        thumbnail_file_path=thumb_path,
        seo_package=seo_package,
        headless=True
    )

    logger.success(f"Result for Episode {ep_num}: {upload_res}")
    return upload_res


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autopilot YouTube Publisher")
    parser.add_argument("--limit", type=int, default=1, help="Number of videos to process in this run")
    parser.add_argument("--visibility", type=str, default="unlisted", help="Visibility: unlisted, public, private")
    args = parser.parse_args()

    for idx, item in enumerate(AUTOPILOT_QUEUE[:args.limit]):
        logger.info(f"\n>>> PROCESSING ITEM {idx + 1} OF {args.limit} <<<\n")
        try:
            res = run_single_episode_autopilot(item, visibility=args.visibility)
        except Exception as e:
            logger.error(f"Error processing item {item}: {e}")
