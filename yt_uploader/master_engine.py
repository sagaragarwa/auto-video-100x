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

import os
import sys
import time
import json
import shutil
import asyncio
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

import edge_tts
from yt_uploader.master_prompt_parser import parse_master_prompt
from yt_uploader.cinematic_director import CinematicDirector
from yt_uploader.audio_director import select_cinematic_bgm
from yt_uploader.cinematic_render import normalize_cinematic_clip, render_cinematic_longform
from yt_uploader.seo_generator import generate_viral_seo_package
from yt_uploader.disk_governor import enforce_5gb_disk_headroom, get_disk_usage
from yt_uploader.asset_purger import format_bytes
from scripts.chat_video_agent import generate_deep_script, detect_language, detect_niche

USER_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")

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
        platforms: Optional[List[str]] = None,
        skip_thumbnail: bool = True
    ) -> Dict[str, Any]:
        """
        End-to-End autonomous generation from a single prompt in WebUI Dashboard.
        Strictly guarantees:
        1. Zero duplicate visuals (strict MD5 fingerprinting & zero in-video loops)
        2. Signature Content ID outro played in FULL at the end of every video
        3. Zero subtitles (pure clean cinematic footage)
        4. Zero thumbnails (never generate thumbnails per user mandate)
        5. Auto-delivery straight to C:\\Users\\janar\\Downloads\\
        6. Studio-grade EBU R128 loudness (-14 LUFS) & 48kHz stereo master audio
        """
        start_time = time.time()
        logger.info(f"🚀 INITIATING 5X CINEMATIC MASTER ENGINE FOR: '{prompt}'")

        # 0. Disk Safety Pre-flight
        disk_stats = enforce_5gb_disk_headroom(min_free_gb=5.0)
        logger.info(f"💾 Pre-flight Disk Check: {disk_stats.get('free_gb', 0)} GB Free (Safe > 5GB)")

        # 1. Parse Master Prompt
        plan = parse_master_prompt(prompt)
        topic = plan["topic"]
        target_duration = plan["duration_seconds"]
        channel = plan["resolved_channel"]
        if auto_upload is not None:
            plan["auto_upload"] = auto_upload

        lang = detect_language(prompt)
        niche = plan.get("niche") or detect_niche(prompt)

        # 2. Audio Synthesis (Dynamic Neural Voice if not provided)
        if custom_audio_path and os.path.exists(custom_audio_path):
            audio_path = custom_audio_path
        else:
            logger.info(f"🎙️ Synthesizing deep research voiceover for prompt ({lang.upper()})...")
            deep_script_data = generate_deep_script(prompt, niche, lang, target_duration)
            script_text = deep_script_data["script"]
            voice = "hi-IN-MadhurNeural" if lang == "hi" else "en-US-ChristopherNeural"
            audio_path = os.path.join(self.temp_dir, f"master_audio_{int(start_time)}.mp3")

            async def _do_synth():
                comm = edge_tts.Communicate(script_text, voice, rate="+4%")
                await comm.save(audio_path)
            asyncio.run(_do_synth())

        # Get audio duration
        cmd_p = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        actual_duration = float(subprocess.check_output(cmd_p).decode().strip())
        logger.info(f"Target Video Duration: {actual_duration:.1f}s ({actual_duration/60:.2f} mins)")

        # 3. Assemble Strictly UNIQUE Normalized Clips (ZERO VISUAL REPEATS)
        director = CinematicDirector(niche=niche)
        raw_unique_clips = director.gather_unique_clips_for_duration(
            target_duration=actual_duration,
            prompt=topic,
            niche=niche,
            avg_scene_duration=4.2,
            max_online_downloads=6,
            script_text=script_text
        )

        norm_dir = os.path.join(_root, "storage", "ep_norm_clips")
        os.makedirs(norm_dir, exist_ok=True)
        normalized_clips = []

        for idx, raw_clip in enumerate(raw_unique_clips):
            norm_clip = os.path.join(norm_dir, f"m_{int(start_time)}_sc_{idx:02d}.mp4")
            normalize_cinematic_clip(raw_clip, norm_clip, target_duration=4.5)
            normalized_clips.append(norm_clip)

        logger.success(f"🎬 Prepared {len(normalized_clips)} STRICTLY UNIQUE clips! Coverage: {len(normalized_clips)*4.5:.1f}s vs audio {actual_duration:.1f}s (ZERO LOOPS)!")

        # 4. Background Music Selection
        bgm_path = select_cinematic_bgm(niche=niche, duration_needed=actual_duration)
        logger.info(f"Selected Cinematic BGM: {os.path.basename(bgm_path)}")

        # 5. Render Video with Signature Content ID Outro (FULL OUTRO, ZERO SUBTITLES)
        safe_name = "".join(c for c in topic if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")[:30]
        timestamp = int(start_time)
        output_video = os.path.join(self.output_dir, f"{safe_name}_{timestamp}_5x_master.mp4")
        content_id_outro = os.path.join(_root, "resource", "assets", "content_id_outro.mp4")
        effective_outro = content_id_outro if os.path.exists(content_id_outro) else None

        logger.info(f"🎬 Rendering final 1080p master video (Subtitles: False, Full Outro: {effective_outro})...")
        render_cinematic_longform(
            normalized_clips=normalized_clips,
            audio_path=audio_path,
            srt_path=None,
            output_video_path=output_video,
            bgm_path=bgm_path,
            audio_duration=actual_duration,
            burn_subtitles=False,
            outro_clip_path=effective_outro,
            outro_duration=None  # ALWAYS PLAY FULL SIGNATURE OUTRO CLIP PER USER MANDATE
        )

        # 6. Single-Source Auto-Delivery & Ephemeral Temp Purge (Zero Disk Leak)
        is_ci = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"
        dest_download = output_video
        try:
            from yt_uploader.disk_sanitizer import safe_deliver_and_deduplicate, purge_ephemeral_clips, enforce_infinite_storage_headroom
            purge_ephemeral_clips(normalized_clips)
            enforce_infinite_storage_headroom(min_free_gb=10.0)
            if not is_ci:
                dest_download = safe_deliver_and_deduplicate(output_video, USER_DOWNLOADS, move_instead_of_copy=True)
            else:
                logger.info(f"CI runner detected: Preserving master video at {output_video} for artifact/release export.")
                dest_download = output_video
        except Exception as _ds_err:
            logger.warning(f"Disk sanitizer note: {_ds_err}")
            dest_download = output_video

        # 7. Thumbnail Policy (USER MANDATE: NEVER GENERATE THUMBNAIL)
        logger.info("🚫 Thumbnail generation permanently SKIPPED per user mandate.")
        thumb_path = None

        # 8. Viral SEO Package (Unlisted for future uploads)
        seo = generate_viral_seo_package(subject=topic, niche=niche)
        seo["visibility"] = "unlisted"
        seo_meta_file = os.path.join(self.output_dir, f"{safe_name}_{timestamp}_5x_meta.json")
        with open(seo_meta_file, "w", encoding="utf-8") as f:
            json.dump(seo, f, indent=4)

        # Determine actual surviving delivered file path
        target_video = dest_download if (dest_download and os.path.exists(dest_download)) else output_video

        # 9. Smart Multi-Platform Auto-Upload (YouTube, Rumble, etc.)
        upload_dispatch_res = None
        should_upload = plan.get("auto_upload", False) or bool(platforms) or any(k in prompt.lower() for k in ["rumble", "upload", "रंबल", "अपलोड"])
        if should_upload and auto_upload is not False:
            try:
                from yt_uploader.multi_platform_router import parse_multi_platform_intent, dispatch_to_platforms
                intent = parse_multi_platform_intent(prompt)
                effective_platforms = platforms if platforms else intent.get("platforms", ["youtube"])
                logger.info(f"🚀 Multi-Platform Auto-Upload Dispatching to: {effective_platforms}")
                upload_dispatch_res = dispatch_to_platforms(
                    video_path=target_video,
                    seo_package=seo,
                    platforms=effective_platforms,
                    youtube_channel=intent.get("youtube_channel"),
                    rumble_channel=intent.get("rumble_channel"),
                    visibility=intent.get("visibility", "unlisted"),
                    rumble_license=intent.get("rumble_license", "rumble_only"),
                    headless=True
                )
            except Exception as up_err:
                logger.warning(f"Multi-platform auto-upload encountered: {up_err}")
                upload_dispatch_res = {"success": False, "error": str(up_err)}

        # 10. Post-Render 5GB Disk Governor Enforcement
        enforce_5gb_disk_headroom(min_free_gb=5.0)

        total_time = time.time() - start_time
        v_size = os.path.getsize(target_video) if (target_video and os.path.exists(target_video)) else 0

        result = {
            "status": "success",
            "video_path": target_video,
            "downloads_path": dest_download,
            "thumbnail_path": "",
            "duration": actual_duration,
            "file_size": v_size,
            "file_size_human": format_bytes(v_size),
            "render_time_seconds": round(total_time, 1),
            "channel": channel,
            "upload_dispatch": upload_dispatch_res,
            "seo": seo,
            "plan": plan
        }

        logger.success(f"🎉 5X MASTER VIDEO COMPLETED IN {total_time:.1f}s!")
        return result
