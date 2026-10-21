"""
20-Minute Ultra-Cinematic AI Documentary Builder (100x V2 Edition)
Integrates:
- Studio Vocal Chain (80Hz Highpass + Vocal Air Treble + Broadcast Compand)
- Dynamic Sidechain Audio Ducking (Auto-Volume Swells on Voice Pauses)
- Alternating Ken Burns Camera Motions (Zoom In, Pan Right, Zoom Out)
- 35mm Film Color Grading & Optical Vignette
- Broadcast Lower-Third Chapter Badges (Minimalist Vox/Bloomberg Cards)
- Multi-Source Footage (Pixabay + Keyless Pexels 4K CDN + Wikimedia)
- Hard-Locked Signature Content ID Outro (173.25s)
- 1080p High-CTR Click-Worthy Thumbnail
"""

import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

import json
import time
import asyncio
import subprocess
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from loguru import logger
import edge_tts

from omnichannel_powerhouse.gemini_key_rotator import call_gemini_rotator
from omnichannel_powerhouse.multi_stock_aggregator import fetch_multi_source_brolls
from omnichannel_powerhouse.cinematic_100x_engine import (
    master_voiceover_audio,
    apply_ken_burns_and_grade,
    apply_dynamic_sidechain_ducking,
    create_broadcast_lower_third,
    overlay_chapter_cards,
    generate_procedural_sfx
)
from yt_uploader.thumbnail_generator import create_ultra_thumbnail

OUTPUT_DIR = os.path.join(_root, "output")
TEMP_DIR = os.path.join(_root, "temp_demo_hindi")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


CHAPTER_METADATA = [
    {
        "beat": 1,
        "title": "Attention Is All You Need",
        "subtitle": "The Transformer Paradigm Shift",
        "relative_pos": 0.02
    },
    {
        "beat": 2,
        "title": "Mathematics of Intelligence",
        "subtitle": "Latent Space & Scaled Dot-Product",
        "relative_pos": 0.18
    },
    {
        "beat": 3,
        "title": "Bare-Metal Silicon Hardware",
        "subtitle": "TSMC 3nm & ASML High-NA Lithography",
        "relative_pos": 0.40
    },
    {
        "beat": 4,
        "title": "Production Telemetry",
        "subtitle": "100K GPU Clusters & Liquid Cooling",
        "relative_pos": 0.62
    },
    {
        "beat": 5,
        "title": "Geopolitical Silicon Warfare",
        "subtitle": "Sovereign Compute & Nuclear Power",
        "relative_pos": 0.82
    },
    {
        "beat": 6,
        "title": "Autonomous Future Horizon",
        "subtitle": "Synthetic Reasoning & The Road to AGI",
        "relative_pos": 0.94
    }
]


def get_media_duration(file_path: str) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def slice_clip_100x(args: tuple) -> str | None:
    src, dest, dur, idx = args
    return apply_ken_burns_and_grade(src, dest, dur, motion_index=idx)


def main():
    start_time = time.time()
    logger.info("🎬 Initiating 100x Ultra-Cinematic V2 Documentary Production (Hindi)...")

    # 1. Voiceover File (Check cache or synthesize)
    voiceover_raw = os.path.join(TEMP_DIR, "hindi_voiceover.mp3")
    if not os.path.exists(voiceover_raw) or os.path.getsize(voiceover_raw) < 100000:
        logger.info("🎙️ Synthesizing Studio Hindi Neural Voiceover (hi-IN-MadhurNeural)...")
        # Reuse existing or fallback script
        from omnichannel_powerhouse.build_hindi_20min_demo import generate_hindi_institutional_script, synthesize_neural_hindi_speech
        pkg = generate_hindi_institutional_script()
        asyncio.run(synthesize_neural_hindi_speech(pkg["video_script"], voiceover_raw))

    # 2. Master Voiceover with Broadcast Vocal Chain
    voiceover_mastered = os.path.join(TEMP_DIR, "hindi_voiceover_mastered.mp3")
    master_voiceover_audio(voiceover_raw, voiceover_mastered)
    speech_duration = get_media_duration(voiceover_mastered)
    logger.info(f"⏳ Spoken Hindi Duration: {speech_duration:.1f}s ({speech_duration/60:.2f} Minutes)")

    # 3. Procure Multi-Stock Footage (ZERO REPEATS)
    terms = [
        "artificial intelligence glowing neural network",
        "supercomputer datacenter liquid cooling",
        "semiconductor cleanroom silicon wafer",
        "asml lithography extreme ultraviolet",
        "cyberpunk matrix data stream 4k",
        "abstract quantum physics particle nodes",
        "developer coding terminal high tech",
        "microchip processor macro 1080p",
        "server racks flashing green led"
    ]
    clips = fetch_multi_source_brolls(terms, target_duration=speech_duration, cache_dir=TEMP_DIR)
    if not clips:
        raise RuntimeError("No clips procured!")

    num_clips = len(clips)
    clip_dur = (speech_duration + 2.0) / num_clips
    logger.info(f"🎞️ Applying Ken Burns + 35mm Film Grade across {num_clips} clips ({clip_dur:.2f}s each)...")

    slice_tasks = [
        (src, os.path.join(TEMP_DIR, f"kb_norm_{i:03d}.mp4"), clip_dur, i)
        for i, src in enumerate(clips)
    ]
    normalized = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for res in pool.map(slice_clip_100x, slice_tasks):
            if res:
                normalized.append(res)

    concat_list = os.path.join(TEMP_DIR, "concat_list_100x.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for nf in normalized:
            clean_p = os.path.abspath(nf).replace("\\", "/")
            f.write(f"file '{clean_p}'\n")

    combined_video = os.path.join(TEMP_DIR, "combined_video_100x.mp4")
    logger.info(f"⚡ Fast stream-copy concat for {speech_duration:.1f}s...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-t", f"{speech_duration:.3f}", "-c", "copy", "-movflags", "+faststart",
        combined_video
    ], check=True)

    # 4. Generate Broadcast Lower-Third Chapter Badges
    logger.info("🎨 Rendering Broadcast Lower-Third Chapter Cards...")
    chapter_overlays = []
    for ch in CHAPTER_METADATA:
        start_t = max(5.0, ch["relative_pos"] * speech_duration)
        png_path = os.path.join(TEMP_DIR, f"lower_third_beat_{ch['beat']}.png")
        create_broadcast_lower_third(ch["beat"], ch["title"], ch["subtitle"], png_path)
        chapter_overlays.append({
            "png": png_path,
            "start": start_t,
            "duration": 6.5
        })

    video_with_badges = os.path.join(TEMP_DIR, "video_with_badges_100x.mp4")
    overlay_chapter_cards(combined_video, chapter_overlays, video_with_badges)

    # 5. Dynamic Sidechain Audio Ducking (Music ducks under speech, swells on pauses)
    ambient_path = os.path.join(_root, "resource", "assets", "ambient_cinematic_drone.mp3")
    ducked_episode_path = os.path.join(TEMP_DIR, "ducked_episode_100x.mp4")
    apply_dynamic_sidechain_ducking(
        video_with_badges,
        voiceover_mastered,
        ambient_path,
        ducked_episode_path
    )

    # 6. Hard-Lock Mandatory 173.25s Content ID Outro Clip
    outro_path = os.path.join(_root, "resource", "assets", "content_id_outro.mp4")
    norm_outro = os.path.join(TEMP_DIR, "norm_outro_100x.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", outro_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        norm_outro
    ], check=True, capture_output=True)

    final_100x_output = os.path.join(OUTPUT_DIR, "demo_ai_20min_hindi_100x_master.mp4")
    final_concat = os.path.join(TEMP_DIR, "final_concat_100x.txt")
    with open(final_concat, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.abspath(ducked_episode_path).replace(chr(92), '/')}'\n")
        f.write(f"file '{os.path.abspath(norm_outro).replace(chr(92), '/')}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", final_concat,
        "-c", "copy", "-movflags", "+faststart",
        final_100x_output
    ], check=True)

    total_len = get_media_duration(final_100x_output)
    final_size_mb = os.path.getsize(final_100x_output) / (1024 * 1024)

    # 7. Generate 1080p Ultra High-CTR Thumbnail
    thumb_output = os.path.join(OUTPUT_DIR, "demo_ai_20min_hindi_100x_thumbnail.jpg")
    create_ultra_thumbnail(
        final_100x_output,
        thumb_output,
        punchline="CHIP WAR\nTHE MONOPOLY",
        badge_text="100X CINEMA MASTERCLASS"
    )

    elapsed = time.time() - start_time
    logger.success("=" * 65)
    logger.success(f"🎉 100X ULTRA-CINEMATIC HINDI MASTERCLASS READY IN {elapsed/60:.2f} MINUTES!")
    logger.success(f"📁 Master Video: {final_100x_output} ({final_size_mb:.2f} MB | {total_len/60:.2f} Minutes)")
    logger.success(f"🖼️ Thumbnail: {thumb_output}")
    logger.success(f"🎧 Audio: Mastered Voiceover + Dynamic Sidechain Ducking")
    logger.success(f"🎥 Visuals: Ken Burns Dynamic Motions + 35mm Film Grade + Vignette")
    logger.success(f"🏷️ Broadcast Cards: 6 Vox/Bloomberg Lower-Third Badges")
    logger.success(f"🔒 Outro Hard-Locked: 173.25s Vintage Blue-Laser Clip permanently attached")
    logger.success("=" * 65)


if __name__ == "__main__":
    main()
