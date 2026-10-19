"""
5X Cinematic Autonomous Master Engine.
Brings together Master Prompt Parsing, Semantic Visual Director, High-Fidelity Audio,
Native Fast FFmpeg Rendering, Click-Worthy Thumbnail, Viral SEO, Smart Channel Routing,
and 5GB Disk Governor into a single zero-touch pipeline.
"""

import os
import sys
import time
import json
import subprocess
from typing import Dict, Any, Optional, List
from loguru import logger

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from yt_uploader.master_prompt_parser import parse_master_prompt
from yt_uploader.cinematic_director import CinematicDirector
from yt_uploader.audio_director import select_cinematic_bgm
from yt_uploader.cinematic_render import normalize_cinematic_clip, render_cinematic_longform
from yt_uploader.thumbnail_generator import create_ultra_thumbnail
from yt_uploader.seo_generator import generate_viral_seo_package
from yt_uploader.channel_manager import auto_detect_channel
from yt_uploader.disk_governor import enforce_5gb_disk_headroom, get_disk_usage
from yt_uploader.asset_purger import format_bytes

class CinematicMasterEngine:
    def __init__(self):
        self.output_dir = os.path.join(_root, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.temp_dir = os.path.join(_root, "storage", "temp")
        os.makedirs(self.temp_dir, exist_ok=True)

    def generate_autonomous_video(
        self,
        prompt: str,
        custom_audio_path: Optional[str] = None,
        custom_srt_path: Optional[str] = None,
        auto_upload: Optional[bool] = None,
        skip_thumbnail: bool = True
    ) -> Dict[str, Any]:
        """
        End-to-End autonomous generation from a single prompt.
        """
        start_time = time.time()
        logger.info(f"🚀 INITIATING 5X CINEMATIC MASTER ENGINE FOR: '{prompt}'")

        # 0. Disk Safety Pre-flight
        disk_stats = enforce_5gb_disk_headroom(min_free_gb=5.0)
        logger.info(f"💾 Pre-flight Disk Check: {disk_stats.get('free_gb', 0)} GB Free (Safe > 5GB)")

        # 1. Parse Master Prompt
        plan = parse_master_prompt(prompt)
        topic = plan["topic"]
        duration = plan["duration_seconds"]
        channel = plan["resolved_channel"]
        if auto_upload is not None:
            plan["auto_upload"] = auto_upload

        # Determine niche
        niche = "psychology"
        if "trading" in channel or "finance" in prompt.lower() or "stock" in prompt.lower():
            niche = "trading"
        elif "tech" in channel or "ai" in prompt.lower():
            niche = "tech"

        director = CinematicDirector(niche=niche)

        # 2. Audio & Subtitles
        # If custom audio & srt provided, use them; otherwise verify or generate
        audio_path = custom_audio_path or os.path.join(_root, "storage", "demo_5min_audio.mp3")
        srt_path = custom_srt_path or os.path.join(_root, "storage", "demo_5min_subs.srt")

        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio source not found at: {audio_path}")

        # Get audio duration
        cmd_p = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        actual_duration = float(subprocess.check_output(cmd_p).decode().strip())
        logger.info(f"Target Video Duration: {actual_duration:.1f}s ({actual_duration/60:.2f} mins)")

        # 3. Scene Breakdown & Semantic Clip Gathering
        scene_duration = 5.5
        from yt_uploader.cinematic_director import parse_srt_into_scenes
        real_scenes = parse_srt_into_scenes(srt_path, target_scene_duration=scene_duration)
        if not real_scenes:
            num_scenes = max(10, int(actual_duration / scene_duration) + 1)
            real_scenes = [{"text": f"Scene {i} on {topic}", "index": i} for i in range(num_scenes)]

        logger.info(f"Planned {len(real_scenes)} semantic scenes from subtitles (zero repetition guarantee)...")
        queries = director.get_scene_visual_queries(real_scenes)

        normalized_clips = []
        norm_dir = os.path.join(_root, "storage", "cinematic_norm")
        os.makedirs(norm_dir, exist_ok=True)

        for idx, q in enumerate(queries):
            raw_clip = director.fetch_unique_scene_clip(q, idx)
            if not raw_clip or not os.path.exists(raw_clip):
                # Fallback to general pool if needed
                continue

            norm_clip = os.path.join(norm_dir, f"scene_{idx:02d}_norm.mp4")
            normalize_cinematic_clip(raw_clip, norm_clip, target_duration=scene_duration)
            normalized_clips.append(norm_clip)

        logger.success(f"Prepared {len(normalized_clips)} unique normalized clips for documentary!")

        # 4. Background Music Selection
        bgm_path = select_cinematic_bgm(niche=niche, duration_needed=actual_duration)
        logger.info(f"Selected Cinematic BGM: {os.path.basename(bgm_path)}")

        # 5. Render Video with Modern Subtitles & Dynamic Audio Ducking
        safe_name = topic.replace(" ", "_").lower()[:30]
        output_video = os.path.join(self.output_dir, f"{safe_name}_5x_master.mp4")

        render_cinematic_longform(
            normalized_clips=normalized_clips,
            audio_path=audio_path,
            srt_path=srt_path,
            output_video_path=output_video,
            bgm_path=bgm_path,
            audio_duration=actual_duration
        )

        # 6. Thumbnail Policy (USER MANDATE: NEVER GENERATE THUMBNAIL)
        thumb_path = None
        if not skip_thumbnail:
            thumb_path = os.path.join(self.output_dir, f"{safe_name}_thumb.jpg")
            best_frame_clip = normalized_clips[min(3, len(normalized_clips)-1)]
            create_ultra_thumbnail(
                bg_image_or_video=best_frame_clip,
                output_path=thumb_path,
                punchline="RESET YOUR BRAIN!",
                badge_text="5X CINEMATIC MASTERCLASS"
            )
        else:
            logger.info("🚫 Thumbnail generation permanently SKIPPED per user mandate.")

        # 7. Viral SEO Package
        seo = generate_viral_seo_package(
            subject=topic,
            niche=niche
        )

        # 8. Post-Render 5GB Disk Governor Enforcement
        enforce_5gb_disk_headroom(min_free_gb=5.0)

        total_time = time.time() - start_time
        v_size = os.path.getsize(output_video)

        result = {
            "status": "success",
            "video_path": output_video,
            "thumbnail_path": thumb_path,
            "duration": actual_duration,
            "file_size": v_size,
            "file_size_human": format_bytes(v_size),
            "render_time_seconds": round(total_time, 1),
            "channel": channel,
            "seo": seo,
            "plan": plan
        }

        logger.success(f"🎉 5X MASTER VIDEO COMPLETED IN {total_time:.1f}s!")
        return result
