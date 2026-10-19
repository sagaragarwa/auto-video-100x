import os
import sys

# Ensure root dir and .venv site-packages are on sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

venv_site = os.path.join(root_dir, ".venv", "Lib", "site-packages")
if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
from loguru import logger

from yt_uploader.channel_manager import load_channels, open_login_window
from yt_uploader.seo_generator import generate_viral_seo_package
from yt_uploader.thumbnail_generator import create_ultra_thumbnail
from yt_uploader.studio_uploader import upload_video_to_studio
from yt_uploader.asset_purger import purge_video_assets, format_bytes
from yt_uploader.disk_governor import enforce_5gb_disk_headroom, is_disk_space_safe, get_disk_usage

def upload_single_video_flow(
    channel_info: dict,
    video_path: str,
    subject: str = "",
    punchline: str = "",
    visibility: str = "unlisted",
    delete_after_upload: bool = True,
    headless: bool = False,
    skip_thumbnail: bool = True
) -> dict:
    """
    Executes full upload pipeline for one video:
    1. Pre-flight Disk Check: Ensures at least 5 GB free disk space exists
    2. Generates Algorithm-Catchy SEO
    3. Skips Thumbnail (Enforced by User Mandate: NEVER GENERATE THUMBNAIL)
    4. Uploads to YouTube Studio as UNLISTED
    5. IF confirmed uploaded: IMMEDIATELY DELETES video files & task directories to reclaim disk space!
    6. Ensures >= 5 GB disk headroom is maintained at all times.
    """
    video_path = os.path.abspath(video_path)
    if not os.path.exists(video_path):
        return {"success": False, "error": f"Video not found: {video_path}"}

    # Pre-flight Disk Check (Mandate: At least 5 GB free)
    disk_check = enforce_5gb_disk_headroom(min_free_gb=5.0)
    logger.info(f"💾 Pre-flight Disk Health: {disk_check['free_gb']} GB Free on drive (Safe threshold: >= 5.0 GB)")

    subj = subject or os.path.splitext(os.path.basename(video_path))[0].replace("_", " ")

    # 1. Generate SEO Package
    logger.info(f"Generating Algorithm-Catchy SEO for '{subj}'...")
    seo = generate_viral_seo_package(subject=subj, niche=channel_info.get("niche", "general"))
    seo["visibility"] = visibility

    # 2. Thumbnail Policy (USER MANDATE: NEVER GENERATE THUMBNAIL)
    thumb_path = None
    if not skip_thumbnail:
        thumb_path = os.path.join(os.path.dirname(video_path), f"{os.path.splitext(os.path.basename(video_path))[0]}_thumb.jpg")
        p_line = punchline or seo.get("punchline", "MUST WATCH!")
        logger.info(f"Generating Ultra Thumbnail with punchline: '{p_line}'...")
        create_ultra_thumbnail(
            bg_image_or_video=video_path,
            output_path=thumb_path,
            punchline=p_line,
            badge_text=seo.get("badge", "EXCLUSIVE")
        )
    else:
        logger.info("🚫 Thumbnail generation permanently SKIPPED per user mandate.")

    # 3. Upload to YouTube Studio
    logger.info(f"Dispatching video to channel: '{channel_info.get('name')}'...")
    res = upload_video_to_studio(
        channel_profile_dir=channel_info["profile_dir"],
        video_file_path=video_path,
        thumbnail_file_path=thumb_path,
        seo_package=seo,
        headless=headless
    )

    # 4. Immediate Post-Upload Purge with 5 GB Guarantee
    if res.get("success"):
        logger.success(f"Upload Confirmed! Video Link: {res.get('url') or 'Published'}")
        if delete_after_upload:
            logger.info("🗑️ Auto-delete triggered: Purging uploaded video, thumbnail, and task files to free storage...")
            purge_res = purge_video_assets(video_path=video_path, thumbnail_path=thumb_path)
            res["purge_summary"] = purge_res
            free_gb = purge_res.get("free_disk_gb", "Unknown")
            logger.success(f"✨ Storage Reclaimed: {purge_res['freed_human']} freed! Drive Free Space: {free_gb} GB (5 GB Safety Guarantee Maintained)")
        else:
            logger.info("Keep assets enabled: Skipping file deletion.")
    else:
        logger.warning(f"Upload failed or incomplete. Preserving local video files for safety: {res.get('error')}")

    return res

def main():
    parser = argparse.ArgumentParser(description="Multi-Channel YouTube Studio Persistent Uploader (No API Quota)")
    subparsers = parser.add_subparsers(dest="command")

    # Command: list
    subparsers.add_parser("list", help="List all configured channels")

    # Command: login
    login_parser = subparsers.add_parser("login", help="Perform one-time login for a channel")
    login_parser.add_argument("--channel", required=True, help="Channel key (e.g. channel_psychology)")

    # Command: upload
    upload_parser = subparsers.add_parser("upload", help="Upload a video to a specific channel with auto SEO and Thumbnail")
    upload_parser.add_argument("--channel", required=True, help="Channel key (e.g. channel_psychology)")
    upload_parser.add_argument("--video", required=True, help="Path to the video file")
    upload_parser.add_argument("--subject", default="", help="Video topic/subject for SEO generation")
    upload_parser.add_argument("--punchline", default="", help="Custom thumbnail punchline (optional)")
    upload_parser.add_argument("--visibility", default="public", choices=["public", "unlisted", "private"])
    upload_parser.add_argument("--keep-assets", action="store_true", help="Do NOT delete assets after upload (by default uploaded video & temp files are auto-deleted)")

    # Command: batch-upload
    batch_parser = subparsers.add_parser("batch-upload", help="Sequentially upload multiple videos and delete each one immediately upon upload")
    batch_parser.add_argument("--channel", required=True, help="Channel key")
    batch_parser.add_argument("--dir", default="output", help="Directory containing videos (default: output)")
    batch_parser.add_argument("--pattern", default="*.mp4", help="Glob pattern for videos (default: *.mp4)")
    batch_parser.add_argument("--visibility", default="public", choices=["public", "unlisted", "private"])
    batch_parser.add_argument("--keep-assets", action="store_true", help="Do NOT delete assets after upload")

    # Command: master-engine
    master_parser = subparsers.add_parser("master-engine", help="5X Cinematic Autonomous Video Engine: Generate 1080p documentary from 1 prompt")
    master_parser.add_argument("--prompt", required=True, help="Natural language prompt (e.g. '5 minute dopamine detox documentary in Hindi')")
    master_parser.add_argument("--auto-upload", action="store_true", help="Automatically upload to the routed channel")

    # Command: cloud-watcher
    watcher_parser = subparsers.add_parser("cloud-watcher", help="Run 30-second GitHub Cloud Watcher Daemon to keep repo active and offload load")
    watcher_parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds (default: 30)")

    # Command: cloud-render
    cloud_parser = subparsers.add_parser("cloud-render", help="Dispatch video generation to GitHub Cloud (Zero local CPU/disk load)")
    cloud_parser.add_argument("--prompt", required=True, help="Video prompt")
    cloud_parser.add_argument("--auto-upload", action="store_true", help="Auto upload to YouTube Studio")

    args = parser.parse_args()

    channels = load_channels()

    if args.command == "cloud-watcher":
        import time
        from yt_uploader.github_cloud_watcher import get_cloud_watcher
        watcher = get_cloud_watcher()
        watcher.config["check_interval_seconds"] = args.interval
        logger.info(f"🔄 Starting GitHub Cloud 30s Watcher on {watcher.config['repo_owner']}/{watcher.config['repo_name']}...")
        try:
            while True:
                watcher.run_cycle()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Cloud Watcher stopped.")
        return

    if args.command == "cloud-render":
        from yt_uploader.github_cloud_watcher import queue_cloud_video_task, get_cloud_watcher
        task = queue_cloud_video_task(prompt=args.prompt, auto_upload=args.auto_upload)
        watcher = get_cloud_watcher()
        watcher.run_cycle()
        return

    if args.command == "master-engine":
        from yt_uploader.master_engine import CinematicMasterEngine
        engine = CinematicMasterEngine()
        res = engine.generate_autonomous_video(prompt=args.prompt, auto_upload=args.auto_upload)
        if args.auto_upload and res.get("status") == "success":
            ch_key = res["channel"]
            if ch_key in channels:
                upload_single_video_flow(
                    channel_info=channels[ch_key],
                    video_path=res["video_path"],
                    subject=res["plan"]["topic"],
                    visibility="public",
                    delete_after_upload=True
                )
        return

    if args.command == "list" or not args.command:
        print("\n=== Registered Multi-Channel YouTube Profiles ===")
        for k, v in channels.items():
            prof = v.get("profile_dir", "")
            exists = os.path.exists(prof) and len(os.listdir(prof)) > 0 if os.path.exists(prof) else False
            status = "✅ Profile Configured (Ready)" if exists else "⚠️ Not Logged In Yet (Run 'login')"
            print(f" • Channel Key : {k}")
            print(f"   Name        : {v.get('name')}")
            print(f"   Niche       : {v.get('niche')}")
            print(f"   Status      : {status}")
            print(f"   Profile Dir : {prof}\n")
        return

    if args.command == "login":
        if args.channel not in channels:
            logger.error(f"Channel '{args.channel}' not found. Available: {list(channels.keys())}")
            return
        open_login_window(args.channel)
        return

    if args.command == "upload":
        if args.channel not in channels:
            logger.error(f"Channel '{args.channel}' not found. Available: {list(channels.keys())}")
            return
        ch = channels[args.channel]
        delete_after = not args.keep_assets
        upload_single_video_flow(
            channel_info=ch,
            video_path=args.video,
            subject=args.subject,
            punchline=args.punchline,
            visibility=args.visibility,
            delete_after_upload=delete_after
        )

    if args.command == "batch-upload":
        import glob
        from yt_uploader.channel_manager import auto_detect_channel

        is_auto_channel = (args.channel.lower() == "auto")
        if not is_auto_channel and args.channel not in channels:
            logger.error(f"Channel '{args.channel}' not found. Available: {list(channels.keys())} or 'auto'")
            return

        search_dir = os.path.abspath(args.dir)
        search_pattern = os.path.join(search_dir, args.pattern)
        matched_videos = sorted(glob.glob(search_pattern))
        # Filter out with_outro or temp if originals exist
        videos = [v for v in matched_videos if not ("_thumb." in v or ".temp" in v)]

        if not videos:
            logger.warning(f"No videos found matching pattern: {search_pattern}")
            return

        mode_name = "🎯 Smart Auto-Route (Dynamic per-video)" if is_auto_channel else channels[args.channel].get('name')
        logger.info(f"🚀 Starting Batch Sequential Upload for {len(videos)} videos [Target: {mode_name}]...")
        logger.info(f"🗑️ Per-Video Auto-Delete: {'ENABLED (Files deleted immediately after upload)' if not args.keep_assets else 'DISABLED'}")

        total_freed = 0
        success_count = 0
        fail_count = 0

        for idx, vid in enumerate(videos, start=1):
            vname = os.path.basename(vid)
            if is_auto_channel:
                target_key = auto_detect_channel(vname)
                ch = channels[target_key]
            else:
                ch = channels[args.channel]

            logger.info(f"\n==========================================")
            logger.info(f"▶️ [{idx}/{len(videos)}] Processing: {vname} ➔ Channel: '{ch.get('name')}'")
            logger.info(f"==========================================")
            
            res = upload_single_video_flow(
                channel_info=ch,
                video_path=vid,
                visibility=args.visibility,
                delete_after_upload=not args.keep_assets
            )
            if res.get("success"):
                success_count += 1
                if "purge_summary" in res:
                    total_freed += res["purge_summary"].get("freed_bytes", 0)
            else:
                fail_count += 1
                logger.error(f"Failed to upload {vid}: {res.get('error')}")

        logger.info(f"\n🎉 Batch Upload Queue Finished!")
        logger.info(f" • Uploaded : {success_count} / {len(videos)}")
        logger.info(f" • Failed   : {fail_count}")
        logger.info(f" • Storage Reclaimed : {format_bytes(total_freed)}")

if __name__ == "__main__":
    main()

