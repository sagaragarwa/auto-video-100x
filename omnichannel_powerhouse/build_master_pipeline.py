"""
OmniChannel Master Pipeline (100x Production Engine)
Fully Unified & Auto-Corrected:
1. Zero-Silence Duration Guard (Speech & Video Strictly Synchronized)
2. Devanagari Tech Transliteration (टी-एस-एम-सी, ए-एस-एम-एल, ई-यू-वी)
3. Intel QuickSync (h264_qsv) Hardware Accelerated Encoding
4. Semantic B-Roll Keyword Matching (No Blind Montages)
5. Dynamic 4-Act Harmonic Scoring Bed & Dynamic Ducking
6. Faster-Whisper Kinetic Karaoke Subtitles (ASS Glow)
"""

import os
import sys
import time
import math
import asyncio
import subprocess
from typing import List, Dict, Any

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)
if _root not in sys.path:
    sys.path.insert(0, _root)

from loguru import logger
import edge_tts

from omnichannel_powerhouse.voice_router import (
    transliterate_tech_terms,
    calculate_script_metrics
)
from omnichannel_powerhouse.cinematic_100x_engine import (
    get_best_hardware_encoder,
    generate_4act_cinematic_bed,
    generate_procedural_sfx
)
from omnichannel_powerhouse.smart_broll_matcher import (
    build_semantic_visual_timeline
)
from omnichannel_powerhouse.kinetic_subtitles import (
    generate_kinetic_ass
)

OUTPUT_DIR = os.path.join(_root, "output")
TEMP_DIR = os.path.join(_root, "temp_demo_hindi")
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


async def synthesize_master_voice(script: str, out_raw: str, voice: str = "hi-IN-MadhurNeural"):
    """Synthesizes voice with transliteration and documentary pacing."""
    clean_script = transliterate_tech_terms(script)
    logger.info(f"🎙️ Synthesizing Voice with Phonetic Devanagari Engine ({len(clean_script)} chars)...")
    comm = edge_tts.Communicate(clean_script, voice=voice, rate="-2%", pitch="-1Hz")
    await comm.save(out_raw)


def apply_broadcast_dsp_mastering(in_mp3: str, out_mp3: str):
    """Applies Shure SM7B Vocal DSP Mastering Chain."""
    logger.info("🎛️ Applying Shure SM7B Broadcast Vocal Mastering Chain...")
    vocal_chain = (
        "highpass=f=80,"
        "equalizer=f=250:t=q:w=1.2:g=2.2,"
        "equalizer=f=3500:t=q:w=1.2:g=2.5,"
        "equalizer=f=6800:t=q:w=1.5:g=-2.5,"
        "dynaudnorm=p=0.95:m=10:s=12"
    )
    cmd = [
        "ffmpeg", "-y", "-i", in_mp3,
        "-af", vocal_chain,
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
        out_mp3
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logger.success(f"✅ Mastered Broadcast Voiceover Ready: {out_mp3}")


def produce_synchronized_master(
    script: str,
    output_video_path: str,
    target_duration: float = None,
    include_subtitles: bool = True
) -> str:
    """
    Main 100x Production Pipeline:
    Ensures EXACT audio-video synchronization (Zero Dead Silence),
    Intel QuickSync Hardware encoding, and Semantic B-roll placement.
    """
    t0 = time.time()
    logger.info("🚀 Launching OmniChannel 100x Master Pipeline...")

    # Step 1: Voice Synthesis
    raw_voice = os.path.join(TEMP_DIR, "master_raw_voice.mp3")
    master_voice = os.path.join(TEMP_DIR, "master_dsp_voice.mp3")
    asyncio.run(synthesize_master_voice(script, raw_voice))
    apply_broadcast_dsp_mastering(raw_voice, master_voice)

    speech_dur = get_media_duration(master_voice)
    logger.info(f"🎙️ Voice Duration: {speech_dur:.2f}s ({speech_dur/60.0:.2f} min)")

    # DURATION GUARD: Video MUST match voice duration precisely
    actual_dur = speech_dur
    if target_duration and target_duration > speech_dur:
        logger.warning(
            f"⚠️ Target duration was {target_duration:.1f}s, but speech is {speech_dur:.1f}s. "
            f"Locking video to exact speech duration {speech_dur:.1f}s to prevent dead silence!"
        )

    # Step 2: Semantic Visual Alignment
    cached_brolls = [
        os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR)
        if f.endswith(".mp4") and f.startswith("kb_norm_")
    ]
    custom_assets = {
        "exploded_3d": os.path.join(OUTPUT_DIR, "test_exploded_blackwell_3d.mp4"),
        "flux_asml": os.path.join(OUTPUT_DIR, "test_flux_asml_clip.mp4"),
        "market_chart": os.path.join(OUTPUT_DIR, "test_chart.mp4"),
        "headline_scan": os.path.join(OUTPUT_DIR, "test_headline.mp4")
    }

    # Split script into logical beats
    sentences = [s.strip() for s in script.split("।") if s.strip()]
    if not sentences:
        sentences = [s.strip() for s in script.split(".") if s.strip()]

    beat_dur = actual_dur / max(len(sentences), 1)
    sentence_timeline = [{"text": s, "duration": beat_dur} for s in sentences]

    visual_timeline = build_semantic_visual_timeline(
        sentence_timeline, cached_brolls, custom_assets, actual_dur
    )

    # Concat visuals
    concat_txt = os.path.join(TEMP_DIR, "master_visual_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for item in visual_timeline:
            clean_p = os.path.abspath(item["clip_path"]).replace("\\", "/")
            f.write(f"file '{clean_p}'\n")

    raw_visual_video = os.path.join(TEMP_DIR, "master_raw_visual.mp4")
    hw_flags = get_best_hardware_encoder()
    logger.info(f"🎞️ Concatting Visual Track with Hardware Flags: {' '.join(hw_flags)}...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-t", f"{actual_dur:.3f}",
        *hw_flags,
        raw_visual_video
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Step 3: Dynamic 4-Act Harmonic Scoring Bed & Sidechain Ducking
    scoring_bed = os.path.join(TEMP_DIR, "master_4act_scoring.mp3")
    generate_4act_cinematic_bed(actual_dur, scoring_bed)

    logger.info("🎚️ Applying Dynamic Sidechain Ducking (-24dB speech ducking)...")
    complex_filter = (
        "[1:a]aloop=loop=-1:size=2e+09[bg];"
        "[bg][0:a]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=400:level_in=0.15[ducked];"
        "[0:a][ducked]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    muxed_video = os.path.join(TEMP_DIR, "master_muxed_temp.mp4")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", master_voice,
        "-i", scoring_bed,
        "-i", raw_visual_video,
        "-filter_complex", complex_filter,
        "-map", "2:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{actual_dur:.3f}",
        muxed_video
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Step 4: Kinetic Karaoke Subtitles (Optional / Default True)
    final_output = output_video_path
    if include_subtitles:
        try:
            logger.info("⚡ Generating Kinetic Karaoke Subtitles (faster-whisper INT8)...")
            ass_path = os.path.join(TEMP_DIR, "master_kinetic_subs.ass")
            generate_kinetic_ass(master_voice, ass_path)
            clean_ass = ass_path.replace("\\", "/").replace(":", "\\:")
            hw_flags = get_best_hardware_encoder()
            cmd = [
                "ffmpeg", "-y", "-i", muxed_video,
                "-vf", f"ass='{clean_ass}'",
                *hw_flags,
                "-c:a", "copy",
                final_output
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.success("✅ Kinetic Subtitles Burned Successfully!")
        except Exception as e:
            logger.warning(f"Subtitles engine bypassed: {e}. Using muxed video directly.")
            import shutil
            shutil.copyfile(muxed_video, final_output)
    else:
        import shutil
        shutil.copyfile(muxed_video, final_output)

    dur = get_media_duration(final_output)
    size_mb = os.path.getsize(final_output) / (1024 * 1024)
    elapsed = time.time() - t0

    logger.success(f"🎉 100x Master Video Successfully Completed in {elapsed:.1f}s!")
    logger.info(f"   Destination: {final_output} ({dur:.2f}s, {size_mb:.2f} MB)")
    return final_output


if __name__ == "__main__":
    test_script = (
        "नमस्ते दोस्तों। TSMC और ASML की एक्सट्रीम अल्ट्रावायलेट लेज़र तकनीक ने पूरे विश्व के "
        "आर्टिफिशियल इंटेलिजेंस हार्डवेयर पर एकाधिकार स्थापित कर लिया है। "
        "एनवीडिया का ब्लैकवेल सुपरचिप इसी 13.5 नैनोमीटर प्रक्रिया पर तैयार होता है। "
        "भारत अब इंडिया एआई मिशन के तहत अपना सॉवरेन कंप्यूट इन्फ्रास्ट्रक्चर तैयार कर रहा है।"
    )
    test_out = os.path.join(OUTPUT_DIR, "test_100x_master_pipeline.mp4")
    produce_synchronized_master(test_script, test_out, include_subtitles=False)
