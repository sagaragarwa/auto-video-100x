#!/usr/bin/env python3
"""
Autonomous 40-Episode Master Documentary Producer (Zero Antigravity Overhead).
- 30 Institutional Trading Masterclasses (>20 minutes each)
- 10 Mental Health & Psychiatric Masterclasses (>20 minutes each)
- High-retention narrative, natural Subscribe/Like/Comment CTAs at 3m, 10m, and 18m
- Pure English (en-US-ChristopherNeural & en-US-GuyNeural)
- 100% C++ FFmpeg Fast Pipeline (Zero slow MoviePy)
- THUMBNAIL GENERATION PERMANENTLY DISABLED (Skipped)
- FUTURE UPLOAD POLICY: UNLISTED (No current upload)
- 5GB Free Disk Governor enforced after every single episode
"""

import os
import sys
import time
import json
import asyncio
import argparse
import subprocess
from typing import Dict, Any, List, Optional
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
from yt_uploader.cinematic_director import CinematicDirector, parse_srt_into_scenes
from yt_uploader.audio_director import select_cinematic_bgm
from yt_uploader.cinematic_render import normalize_cinematic_clip, render_cinematic_longform
from yt_uploader.disk_governor import enforce_5gb_disk_headroom
from yt_uploader.asset_purger import format_bytes
from yt_uploader.seo_generator import generate_viral_seo_package
from yt_uploader.deep_script_generator import generate_deep_script_content

CATALOG_PATH = os.path.join(_root, "master_40_series_catalog.json")
USER_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")

def load_catalog() -> Dict[str, Any]:
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

async def synthesize_episode_audio(text: str, voice: str, out_audio: str, out_srt: str):
    """
    Generates pristine Edge-TTS neural speech and synchronized SRT subtitles.
    """
    communicate = edge_tts.Communicate(text, voice, rate="+4%")
    submaker = edge_tts.SubMaker()
    
    with open(out_audio, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)

    srt_content = submaker.get_srt()
    if not srt_content or len(srt_content.strip()) < 10:
        # Fallback to text sentence cues
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        cues = []
        t_cur = 0.5
        for idx, s in enumerate(sentences):
            dur = max(2.5, len(s.split()) * 0.42)
            t_end = t_cur + dur
            s_h, s_m, s_s = int(t_cur // 3600), int((t_cur % 3600) // 60), int(t_cur % 60)
            s_ms = int((t_cur - int(t_cur)) * 1000)
            e_h, e_m, e_s = int(t_end // 3600), int((t_end % 3600) // 60), int(t_end % 60)
            e_ms = int((t_end - int(t_end)) * 1000)
            cues.append(f"{idx+1}\n{s_h:02d}:{s_m:02d}:{s_s:02d},{s_ms:03d} --> {e_h:02d}:{e_m:02d}:{e_s:02d},{e_ms:03d}\n{s}\n")
            t_cur = t_end + 0.1
        srt_content = "\n".join(cues)

    with open(out_srt, "w", encoding="utf-8") as f:
        f.write(srt_content)

def produce_single_episode(ep_info: Dict[str, Any], niche: str, voice: str) -> Dict[str, Any]:
    """
    Executes end-to-end production of one 1080p documentary episode.
    SKIPS THUMBNAILS PERMANENTLY.
    SAVES FUTURE UPLOAD METADATA AS UNLISTED (NO CURRENT UPLOAD).
    """
    ep_num = ep_info["episode"]
    title = ep_info["title"]
    logger.info(f"\n=======================================================")
    logger.info(f"🎬 PRODUCING EPISODE {ep_num}: '{title}' [{niche.upper()}]")
    logger.info(f"=======================================================")

    t0 = time.time()
    enforce_5gb_disk_headroom(min_free_gb=5.0)

    # 1. Generate Deep Long-Form Script
    script_text = generate_deep_script_content(ep_info, niche)
    
    # 2. Audio & Subtitles
    temp_dir = os.path.join(_root, "storage", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    audio_path = os.path.join(temp_dir, f"ep_{ep_num:02d}_voice.mp3")
    srt_path = os.path.join(temp_dir, f"ep_{ep_num:02d}_subs.srt")

    logger.info(f"Synthesizing neural audio with voice: {voice}...")
    asyncio.run(synthesize_episode_audio(script_text, voice, audio_path, srt_path))

    cmd_p = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
    duration = float(subprocess.check_output(cmd_p).decode().strip())
    logger.info(f"Audio synthesized successfully! Duration: {duration:.1f}s ({duration/60:.2f} mins)")

    # 3. Scene Breakdown & Semantic Clip Gathering (Zero Duplicate Hashes)
    director = CinematicDirector(niche=niche)
    raw_unique_clips = director.gather_unique_clips_for_duration(
        target_duration=min(duration, 700.0), # Assemble 120-160+ unique clips per episode
        prompt=title,
        niche=niche,
        avg_scene_duration=4.5
    )

    norm_dir = os.path.join(_root, "storage", "ep_norm_clips")
    os.makedirs(norm_dir, exist_ok=True)
    normalized_clips = []

    for idx, raw_clip in enumerate(raw_unique_clips):
        n_clip = os.path.join(norm_dir, f"ep_{ep_num:02d}_sc_{idx:02d}.mp4")
        normalize_cinematic_clip(raw_clip, n_clip, target_duration=4.8)
        normalized_clips.append(n_clip)

    logger.success(f"🎬 Assembled {len(normalized_clips)} STRICTLY UNIQUE 1080p normalized clips for Episode {ep_num}!")

    # 4. Background Music
    bgm_path = select_cinematic_bgm(niche=niche, duration_needed=duration)

    # 5. Render 1080p Master Video (Zero Subtitles, Broadcast Loudness, Signature Content ID Outro)
    out_dir = os.path.join(_root, "output", "master_40_series")
    os.makedirs(out_dir, exist_ok=True)
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_")[:35]
    final_video = os.path.join(out_dir, f"Episode_{ep_num:02d}_{safe_title}.mp4")
    content_id_outro = os.path.join(_root, "resource", "assets", "content_id_outro.mp4")

    logger.info("Rendering final 1080p documentary with dynamic sidechain ducking (-14 LUFS) & Content ID outro (NO SUBTITLES)...")
    render_cinematic_longform(
        normalized_clips=normalized_clips,
        audio_path=audio_path,
        srt_path=srt_path,
        output_video_path=final_video,
        bgm_path=bgm_path,
        audio_duration=duration,
        burn_subtitles=False,
        outro_clip_path=content_id_outro if os.path.exists(content_id_outro) else None,
        outro_duration=None  # ALWAYS PLAY FULL SIGNATURE OUTRO CLIP PER USER MANDATE
    )

    # 6. THUMBNAIL POLICY: STRICTLY SKIPPED PER USER MANDATE
    logger.info("🚫 Thumbnail generation permanently SKIPPED per user mandate. Zero thumbnail files created.")

    # 7. Generate Viral SEO & Save Future Unlisted Upload Payload (NO UPLOAD NOW)
    channel_key = "channel_trading" if niche == "trading" else "channel_psychology"
    seo = generate_viral_seo_package(subject=title, niche=niche)
    seo["visibility"] = "unlisted"  # Strictly unlisted for future uploads

    # 8. Single-Source Auto-Delivery to Downloads & Ephemeral Temp Purge (Zero Disk Leak)
    from yt_uploader.disk_sanitizer import safe_deliver_and_deduplicate, purge_ephemeral_clips, enforce_infinite_storage_headroom
    dest_video = safe_deliver_and_deduplicate(final_video, USER_DOWNLOADS, move_instead_of_copy=True)
    purge_ephemeral_clips(normalized_clips)
    enforce_infinite_storage_headroom(min_free_gb=10.0)

    upload_meta_path = os.path.join(out_dir, f"Episode_{ep_num:02d}_upload_meta.json")
    future_upload_payload = {
        "episode": ep_num,
        "title": title,
        "video_path": dest_video,
        "channel_key": channel_key,
        "visibility": "unlisted",
        "skip_thumbnail": True,
        "uploaded": False,
        "seo": seo,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(upload_meta_path, "w", encoding="utf-8") as f:
        json.dump(future_upload_payload, f, indent=4)

    elapsed = time.time() - t0
    target_f = dest_video if os.path.exists(dest_video) else final_video
    v_size = os.path.getsize(target_f) if os.path.exists(target_f) else 0
    logger.success(f"✅ EPISODE {ep_num} COMPLETE in {elapsed:.1f}s ({elapsed/60:.2f} mins) | Size: {format_bytes(v_size)}")
    logger.info(f"📦 Output Video Delivered: {dest_video}")
    logger.info(f"📋 Future Upload Payload (Unlisted): {upload_meta_path}")

    return future_upload_payload

def main():
    parser = argparse.ArgumentParser(description="Autonomous 40-Episode Master Producer Engine (Zero Antigravity Usage)")
    parser.add_argument("--episode", type=int, default=None, help="Produce single episode (1-40)")
    parser.add_argument("--batch", choices=["trading", "mental_health", "all"], default=None, help="Batch production")
    args = parser.parse_args()

    catalog = load_catalog()
    trading_topics = catalog["batches"]["trading_institutional_30"]["topics"]
    health_topics = catalog["batches"]["mental_health_psychology_10"]["topics"]

    episodes_to_run = []
    if args.episode:
        all_topics = trading_topics + health_topics
        match = [t for t in all_topics if t["episode"] == args.episode]
        if not match:
            print(f"Error: Episode {args.episode} not found (Range: 1-40).")
            return
        ep_info = match[0]
        niche = "trading" if ep_info["episode"] <= 30 else "psychology"
        voice = catalog["batches"]["trading_institutional_30"]["voice"] if niche == "trading" else catalog["batches"]["mental_health_psychology_10"]["voice"]
        episodes_to_run.append((ep_info, niche, voice))
    elif args.batch == "trading":
        voice = catalog["batches"]["trading_institutional_30"]["voice"]
        episodes_to_run = [(t, "trading", voice) for t in trading_topics]
    elif args.batch == "mental_health":
        voice = catalog["batches"]["mental_health_psychology_10"]["voice"]
        episodes_to_run = [(t, "psychology", voice) for t in health_topics]
    elif args.batch == "all":
        t_voice = catalog["batches"]["trading_institutional_30"]["voice"]
        h_voice = catalog["batches"]["mental_health_psychology_10"]["voice"]
        episodes_to_run = [(t, "trading", t_voice) for t in trading_topics] + [(t, "psychology", h_voice) for t in health_topics]
    else:
        print("\n=== 40 Master Documentary Series Catalog ===")
        print(f"Total Trading Episodes        : {len(trading_topics)} (Episodes 1-30)")
        print(f"Total Mental Health Episodes  : {len(health_topics)} (Episodes 31-40)")
        print("\nUsage Options:")
        print("  python scripts/autonomous_40_producer.py --episode 1")
        print("  python scripts/autonomous_40_producer.py --batch trading")
        print("  python scripts/autonomous_40_producer.py --batch mental_health")
        print("  python scripts/autonomous_40_producer.py --batch all\n")
        return

    logger.info(f"🚀 Starting autonomous production queue for {len(episodes_to_run)} episodes...")
    for ep_info, niche, voice in episodes_to_run:
        produce_single_episode(ep_info, niche, voice)

if __name__ == "__main__":
    main()
