"""
1000X ULTRA-CINEMATIC SUPREME ENGINE (All 6 Pillars Unified)
Pillar 1: Kinetic Animated Karaoke Subtitles (Hormozi / Vox style with word-level glowing highlights & emojis)
Pillar 2: Procedural Motion Graphics & Data Charts (Animated Market Share & Archival Headline Scanner)
Pillar 3: 2.5D Parallax Photo Motion & 35mm Film Color Grade
Pillar 4: 4-Act Progressive Scoring & Synchronized Micro-Foley (45Hz Sub-Drops, Typing, Paper Flips)
Pillar 5: Algorithmic Pattern Interrupts (3.8s Cut Ceiling, Camera Punch-Ins, 0.25s Blackout Resets)
Pillar 6: High-CTR Packaging Matrix (Triple A/B Thumbnails + Key Moments Timestamps + Pinned Comment)
"""

import os
import sys
import json
import time
import subprocess
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)
if _root not in sys.path:
    sys.path.insert(0, _root)

from loguru import logger

from omnichannel_powerhouse.voice_router import synthesize_ultra_voice
from omnichannel_powerhouse.kinetic_subtitles import generate_kinetic_ass
from omnichannel_powerhouse.motion_graphics import render_animated_bar_chart, render_headline_scanner
from omnichannel_powerhouse.foley_and_scoring import build_cinematic_audio_bed, synthesize_foley_sfx
from omnichannel_powerhouse.packaging_matrix import create_triple_thumbnail_matrix, generate_seo_metadata
from omnichannel_powerhouse.multi_stock_aggregator import fetch_multi_source_brolls
from omnichannel_powerhouse.cinematic_100x_engine import (
    apply_ken_burns_and_grade,
    create_broadcast_lower_third,
    overlay_chapter_cards
)

OUTPUT_DIR = os.path.join(_root, "output")
TEMP_DIR = os.path.join(_root, "temp_supreme_1000x")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


def get_media_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def render_1000x_master_demo(
    script_text: str = None,
    topic: str = "The Silicon Monopoly"
) -> Dict[str, Any]:
    start_time = time.time()
    logger.info("🎬 Launching 1000x Ultra-Cinematic Supreme Production Pipeline...")

    # Default high-impact investigative documentary script if none provided
    if not script_text:
        script_text = (
            "सिलिकॉन और आर्टिफिशियल इंटेलिजेंस की इस नई दुनिया में, एक ऐसा सच है जो दुनिया से छुपाया गया है। "
            "दुनिया के 90 प्रतिशत से अधिक एडवांस सेमीकंडक्टर चिप्स केवल एक ही कंपनी बनाती है। "
            "अगर यह सप्लाई चेन सिर्फ 6 महीने के लिए रुक जाए, तो दुनिया का पूरा टेक इंफ्रास्ट्रक्चर और आधुनिक अर्थव्यवस्था ठप हो जाएगी। "
            "यह लड़ाई अब सिर्फ सॉफ्टवेयर की नहीं, बल्कि पृथ्वी के सबसे जटिल हार्डवेयर और संप्रभु कम्प्यूट की है।"
        )

    # -------------------------------------------------------------
    # PILLAR 1 & VOICE ROUTER: Gemini 24kHz Native Studio PCM + DSP
    # -------------------------------------------------------------
    voice_path = os.path.join(TEMP_DIR, "supreme_voiceover.mp3")
    if not os.path.exists(voice_path) or os.path.getsize(voice_path) < 1000:
        logger.info("🎙️ [Pillar 0] Synthesizing Studio Voiceover via Gemini Flash Multimodal TTS...")
        synthesize_ultra_voice(
            script_text,
            voice_path,
            persona="cinematic_narrator",
            lang="hi"
        )
    voice_dur = get_media_duration(voice_path)
    logger.info(f"   Voiceover ready ({voice_dur:.2f} seconds)")

    # -------------------------------------------------------------
    # PILLAR 1: Kinetic Hormozi / Vox Subtitles via faster-whisper
    # -------------------------------------------------------------
    ass_path = os.path.join(TEMP_DIR, "supreme_kinetic.ass")
    if not os.path.exists(ass_path) or os.path.getsize(ass_path) < 100:
        logger.info("⚡ [Pillar 1] Generating Kinetic Word-Level Glowing Subtitles...")
        generate_kinetic_ass(voice_path, ass_path, language="hi", font_size=44)

    # -------------------------------------------------------------
    # PILLAR 2: Procedural Motion Graphics & Data Charts
    # -------------------------------------------------------------
    logger.info("📊 [Pillar 2] Procedurally Generating Animated Market Chart & Archival Headline Scanner...")
    chart_video = os.path.join(TEMP_DIR, "graphic_chart.mp4")
    if not os.path.exists(chart_video) or os.path.getsize(chart_video) < 5000:
        chart_data = [
            {"label": "TSMC (Taiwan Foundry)", "value": 91.5, "color": (0, 240, 255)},
            {"label": "Samsung Electronics", "value": 7.8, "color": (160, 180, 210)},
            {"label": "Intel / Others", "value": 0.7, "color": (95, 110, 135)}
        ]
        render_animated_bar_chart(
            title="Sub-3nm Leading-Edge Semiconductor Monopoly",
            subtitle="Global market share of leading-edge AI compute foundry capacity.",
            data=chart_data,
            out_video_path=chart_video,
            duration=4.0
        )

    headline_video = os.path.join(TEMP_DIR, "graphic_headline.mp4")
    if not os.path.exists(headline_video) or os.path.getsize(headline_video) < 5000:
        render_headline_scanner(
            publication="Financial Times • Global Intelligence",
            headline="TSMC HALTS ADVANCED AI CHIP SHIPMENTS",
            highlight_text="US Commerce Department imposes immediate restrictions on sub-7nm silicon exports.",
            out_video_path=headline_video,
            duration=4.0
        )

    # -------------------------------------------------------------
    # PILLAR 3 & 5: Visual Assembler (3.8s Cut Ceiling + Multi-Stock)
    # -------------------------------------------------------------
    logger.info("🎞️ [Pillar 3 & 5] Procuring 4K Multi-Stock B-Roll & Enforcing 3.8s Cut Ceiling...")
    search_queries = [
        "semiconductor cleanroom silicon wafer",
        "artificial intelligence glowing neural network",
        "asml lithography extreme ultraviolet",
        "supercomputer datacenter liquid cooling",
        "cyberpunk matrix data stream 4k"
    ]
    raw_clips = fetch_multi_source_brolls(search_queries, target_duration=voice_dur, cache_dir=TEMP_DIR)
    
    # Process B-roll clips with Ken Burns camera motion & 35mm color grading
    processed_brolls = []
    clip_dur = 3.6  # Strict 3.6s cut ceiling
    for i, src in enumerate(raw_clips[:6]):
        dest = os.path.join(TEMP_DIR, f"kb_clip_{i:02d}.mp4")
        apply_ken_burns_and_grade(src, dest, clip_dur, motion_index=i)
        processed_brolls.append(dest)

    # Interleave B-Roll with Motion Graphics and Blackout Pattern Interrupt
    # Sequence: B-roll 0 -> B-roll 1 -> Animated Chart -> B-roll 2 -> Headline Scanner -> B-roll 3
    final_sequence = []
    if len(processed_brolls) > 0: final_sequence.append(processed_brolls[0])
    if len(processed_brolls) > 1: final_sequence.append(processed_brolls[1])
    final_sequence.append(chart_video)
    if len(processed_brolls) > 2: final_sequence.append(processed_brolls[2])
    final_sequence.append(headline_video)
    if len(processed_brolls) > 3: final_sequence.append(processed_brolls[3])

    concat_file = os.path.join(TEMP_DIR, "visual_sequence.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for vf in final_sequence:
            f.write(f"file '{os.path.abspath(vf).replace(chr(92), '/')}'\n")

    assembled_visual = os.path.join(TEMP_DIR, "assembled_visual.mp4")
    logger.info(f"⚡ Fast stream concat of visual sequence ({voice_dur:.2f}s target)...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-t", f"{voice_dur:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        assembled_visual
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # -------------------------------------------------------------
    # PILLAR 4: 4-Act Scoring & Micro-Foley Synchronized Audio Bed
    # -------------------------------------------------------------
    logger.info("🎧 [Pillar 4] Mixing 4-Act Music Bed with Synchronized Micro-Foley & Sidechain Ducking...")
    ambient_music = os.path.join(_root, "resource", "assets", "ambient_cinematic_drone.mp3")
    foley_events = [
        {"sfx": "sub_boom", "time": 0.2},     # Opening dramatic sub-drop
        {"sfx": "whoosh", "time": 7.2},       # Transition into Animated Chart
        {"sfx": "typing", "time": 8.0},       # Technical data typing chatter
        {"sfx": "paper_flip", "time": 14.8},  # Newspaper headline reveal
        {"sfx": "sub_boom", "time": 19.5}     # Geopolitical climax boom
    ]
    mixed_audio = os.path.join(TEMP_DIR, "supreme_master_audio.m4a")
    build_cinematic_audio_bed(voice_path, ambient_music, foley_events, mixed_audio)

    # -------------------------------------------------------------
    # COMBINE: Video + Master Audio + Burn-in Kinetic Subtitles
    # -------------------------------------------------------------
    logger.info("🔥 Burning Kinetic Hormozi Subtitles into Video Stream...")
    subbed_episode = os.path.join(TEMP_DIR, "subbed_episode.mp4")
    # Clean path for libass in Windows
    clean_ass = os.path.abspath(ass_path).replace("\\", "/").replace(":", "\\:")
    cmd = [
        "ffmpeg", "-y",
        "-i", assembled_visual,
        "-i", mixed_audio,
        "-vf", f"ass='{clean_ass}'",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        "-t", f"{voice_dur:.3f}",
        subbed_episode
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # -------------------------------------------------------------
    # ATTACH: Hard-Locked 173.25s Vintage Content ID Outro Clip
    # -------------------------------------------------------------
    logger.info("🔒 Hard-locking signature 173.25s Content ID Outro...")
    outro_path = os.path.join(_root, "resource", "assets", "content_id_outro.mp4")
    final_output_mp4 = os.path.join(OUTPUT_DIR, "demo_1000x_supreme_master.mp4")

    # Normalize outro audio to match
    norm_outro = os.path.join(TEMP_DIR, "norm_outro.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", outro_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        norm_outro
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    final_concat_list = os.path.join(TEMP_DIR, "final_concat_supreme.txt")
    with open(final_concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.abspath(subbed_episode).replace(chr(92), '/')}'\n")
        f.write(f"file '{os.path.abspath(norm_outro).replace(chr(92), '/')}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", final_concat_list,
        "-c", "copy", "-movflags", "+faststart",
        final_output_mp4
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    total_len = get_media_duration(final_output_mp4)
    final_size_mb = os.path.getsize(final_output_mp4) / (1024 * 1024)

    # -------------------------------------------------------------
    # PILLAR 6: High-CTR Packaging Matrix (Triple A/B Thumbnails & SEO)
    # -------------------------------------------------------------
    logger.info("🎯 [Pillar 6] Generating Triple A/B Thumbnail Matrix & Algorithmic SEO...")
    # Extract keyframe from chart scene
    thumb_base = os.path.join(TEMP_DIR, "thumb_base.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-ss", "8.0", "-i", subbed_episode, "-vframes", "1", "-q:v", "2", thumb_base
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    thumbnails = create_triple_thumbnail_matrix(thumb_base, OUTPUT_DIR, prefix="demo_1000x")
    
    chapters = [
        {"start": 0.0, "title": "The Hidden Silicon Reality"},
        {"start": 7.2, "title": "TSMC 92% Global Monopoly"},
        {"start": 14.5, "title": "Geopolitical Export Sanctions"},
        {"start": 21.0, "title": "The Sovereign Compute War"},
        {"start": voice_dur, "title": "Hard-Locked Signature Outro"}
    ]
    seo_data = generate_seo_metadata(topic, total_len, chapters)
    seo_file = os.path.join(OUTPUT_DIR, "demo_1000x_supreme_seo.json")
    with open(seo_file, "w", encoding="utf-8") as f:
        json.dump(seo_data, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    logger.success("=" * 70)
    logger.success(f"🏆 1000X ULTRA-CINEMATIC SUPREME MASTER COMPLETE IN {elapsed:.1f} SECONDS!")
    logger.success(f"📁 Master Video: {final_output_mp4} ({final_size_mb:.2f} MB | {total_len:.1f}s)")
    logger.success(f"🖼️ Triple A/B Thumbnails: {list(thumbnails.values())}")
    logger.success(f"📝 SEO Metadata: {seo_file}")
    logger.success("=" * 70)

    return {
        "master_video": final_output_mp4,
        "thumbnails": thumbnails,
        "seo": seo_data,
        "duration": total_len,
        "size_mb": final_size_mb
    }


if __name__ == "__main__":
    render_1000x_master_demo()
