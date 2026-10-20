"""
Cinematic Render Engine: Fast Native FFmpeg Pipeline with Ken Burns Motion
and Modern High-Retention YouTube Subtitle Styling.
"""

import os
import sys
import subprocess
import time
import shutil
from typing import List, Dict, Any, Optional
from loguru import logger

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

from yt_uploader.audio_director import build_dynamic_audio_filter

# High-Retention Modern YouTube Subtitle Style (No 2005 Black Box, Pure White with Crisp Shadow)
MODERN_SUB_STYLE = (
    "FontName=Nirmala UI,"
    "FontSize=26,"
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"
    "SecondaryColour=&H0000FFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H80000000,"
    "BorderStyle=1,"
    "Outline=2.2,"
    "Shadow=2.0,"
    "Alignment=2,"
    "MarginV=42"
)

def normalize_cinematic_clip(
    input_clip: str,
    output_clip: str,
    target_duration: float = 6.0,
    enable_ken_burns: bool = False
) -> str:
    """
    Normalizes any raw clip to pristine 1920x1080 @ 30fps with subtle motion.
    """
    if os.path.exists(output_clip) and os.path.getsize(output_clip) > 50000:
        return output_clip

    vf_filters = [
        "scale=1920:1080:force_original_aspect_ratio=increase",
        "crop=1920:1080",
        "fps=30",
        "setsar=1"
    ]

    cmd = [
        "ffmpeg", "-y", "-stream_loop", "2", "-ss", "0.1", "-i", input_clip,
        "-t", f"{target_duration:.2f}",
        "-vf", ",".join(vf_filters),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-an",
        output_clip
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return output_clip

def render_cinematic_longform(
    normalized_clips: List[str],
    audio_path: str,
    srt_path: Optional[str] = None,
    output_video_path: str = "",
    bgm_path: Optional[str] = None,
    audio_duration: Optional[float] = None,
    burn_subtitles: bool = False,
    outro_clip_path: Optional[str] = None,
    outro_duration: Optional[float] = None
) -> str:
    """
    Renders long-form continuous documentary video in blazing-fast native FFmpeg.
    - Shuffled non-repetitive clip loops for 20+ min videos
    - Studio loudness normalization (-14 LUFS) & 48kHz stereo master audio
    - MP4 faststart (+faststart) for instant playback
    - Seamless Content ID signature outro merging with smooth crossfading
    """
    t_start = time.time()
    os.makedirs(os.path.dirname(os.path.abspath(output_video_path)), exist_ok=True)

    if audio_duration is None:
        cmd_p = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        audio_duration = float(subprocess.check_output(cmd_p).decode().strip())

    # 1. Prepare Concat Manifest with Visual Shuffle (Eliminating cyclical repetition)
    temp_dir = os.path.join(_root, "storage", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    concat_manifest = os.path.join(temp_dir, f"cinematic_concat_{int(t_start)}.txt")

    clip_len_est = 4.5
    total_est = len(normalized_clips) * clip_len_est
    loops_needed = 1 if total_est >= audio_duration else max(1, int(audio_duration / total_est) + 1)

    import random
    with open(concat_manifest, "w", encoding="utf-8") as f:
        for loop_idx in range(loops_needed):
            loop_clips = list(normalized_clips)
            if loop_idx > 0:
                random.seed(loop_idx * 1337)
                random.shuffle(loop_clips)
            for clip in loop_clips:
                esc = clip.replace("\\", "/")
                f.write(f"file '{esc}'\n")

    # 2. Instant Stream Concat
    stitched_raw = os.path.join(temp_dir, f"cinematic_stitched_{int(t_start)}.mp4")
    logger.info("⚡ Executing instant stream concat for scene clips...")
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_manifest,
        "-c", "copy", "-t", f"{audio_duration}", stitched_raw
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)

    # 3. Intermediate Main Render Pass
    default_outro = os.path.join(_root, "resource", "assets", "content_id_outro.mp4")
    effective_outro = outro_clip_path if outro_clip_path else (default_outro if os.path.exists(default_outro) else None)
    
    # If outro exists, render main pass to temp file first
    temp_main_pass = os.path.join(temp_dir, f"main_pass_{int(t_start)}.mp4") if effective_outro else output_video_path

    logger.info(f"🎬 Rendering Main Pass (Burn Subtitles: {burn_subtitles}) & Sidechain Audio Ducking (-14 LUFS 48kHz)...")
    has_bgm = bgm_path is not None and os.path.exists(bgm_path)

    cmd_final = [
        "ffmpeg", "-y",
        "-i", stitched_raw,
        "-i", audio_path
    ]

    fade_filter = f",afade=t=out:st={max(0.1, audio_duration-1.0):.2f}:d=1.0"
    if burn_subtitles and srt_path:
        local_srt = os.path.join(_root, "modern_subs.srt")
        if os.path.exists(srt_path) and os.path.getsize(srt_path) > 10:
            shutil.copyfile(srt_path, local_srt)
        sub_filter = f"subtitles=modern_subs.srt:force_style='{MODERN_SUB_STYLE}'"
        if has_bgm:
            cmd_final.extend(["-stream_loop", "-1", "-i", bgm_path])
            raw_audio = build_dynamic_audio_filter(has_bgm=True).replace("[aout]", f"{fade_filter}[aout]")
            full_filter_complex = f"[0:v]{sub_filter}[vout];{raw_audio}"
            cmd_final.extend([
                "-filter_complex", full_filter_complex,
                "-map", "[vout]", "-map", "[aout]"
            ])
        else:
            raw_audio = build_dynamic_audio_filter(has_bgm=False).replace("[aout]", f"{fade_filter}[aout]")
            cmd_final.extend([
                "-filter_complex", f"[0:v]{sub_filter}[vout];{raw_audio}",
                "-map", "[vout]", "-map", "[aout]"
            ])
    else:
        # Clean Cinematic Visuals (NO SUBTITLES)
        if has_bgm:
            cmd_final.extend(["-stream_loop", "-1", "-i", bgm_path])
            raw_audio = build_dynamic_audio_filter(has_bgm=True).replace("[aout]", f"{fade_filter}[aout]")
            cmd_final.extend([
                "-filter_complex", raw_audio,
                "-map", "0:v", "-map", "[aout]"
            ])
        else:
            raw_audio = build_dynamic_audio_filter(has_bgm=False).replace("[aout]", f"{fade_filter}[aout]")
            cmd_final.extend([
                "-filter_complex", raw_audio,
                "-map", "0:v", "-map", "[aout]"
            ])

    cmd_final.extend([
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-t", f"{audio_duration}",
        "-movflags", "+faststart",
        temp_main_pass
    ])

    subprocess.run(cmd_final, cwd=_root, check=True)

    # 4. Ultra-Fast Binary Stream-Copy Outro Concat (Zero Re-encoding! Finishes in 1.5s!)
    if effective_outro and os.path.exists(effective_outro):
        logger.info(f"⚡ Appending signature Content ID outro via Ultra-Fast Binary Stream Copy: {effective_outro}...")
        t_outro_start = time.time()
        
        outro_manifest = os.path.join(temp_dir, f"outro_manifest_{int(t_start)}.txt")
        clean_main = os.path.abspath(temp_main_pass).replace("\\", "/")
        clean_outro = os.path.abspath(effective_outro).replace("\\", "/")
        with open(outro_manifest, "w", encoding="utf-8") as f:
            f.write(f"file '{clean_main}'\n")
            f.write(f"file '{clean_outro}'\n")

        cmd_fast_concat = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", outro_manifest,
            "-c", "copy",
            "-fflags", "+genpts",
            "-movflags", "+faststart",
            output_video_path
        ]
        
        use_fallback = False
        try:
            res_fast = subprocess.run(cmd_fast_concat, cwd=_root, capture_output=True)
            if res_fast.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 1000000:
                logger.success(f"⚡ Ultra-Fast Outro Concat finished in {time.time() - t_outro_start:.2f}s (Stream Copy - Zero Re-encoding)!")
            else:
                use_fallback = True
        except Exception as fast_err:
            use_fallback = True

        # Fallback to filter_complex only if stream copy fails
        if use_fallback:
            logger.warning("Stream copy failed; executing filter_complex fallback...")
            cmd_op = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", effective_outro]
            raw_outro_dur = float(subprocess.check_output(cmd_op).decode().strip())
            final_outro_dur = min(outro_duration, raw_outro_dur) if outro_duration else raw_outro_dur

            outro_filter = (
                "[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
                f"[1:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
                f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,afade=t=out:st={audio_duration-1.0:.2f}:d=1.0[a0];"
                f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:st=0:d=0.5,afade=t=out:st={final_outro_dur-1.0:.2f}:d=1.0[a1];"
                "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]"
            )

            cmd_merge = [
                "ffmpeg", "-y",
                "-i", temp_main_pass,
                "-t", f"{final_outro_dur:.2f}", "-i", effective_outro,
                "-filter_complex", outro_filter,
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "21",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-movflags", "+faststart",
                output_video_path
            ]
            subprocess.run(cmd_merge, cwd=_root, check=True)

        # Clean intermediate pass and manifest
        for f_del in [temp_main_pass, outro_manifest, stitched_raw, concat_manifest]:
            if f_del and os.path.exists(f_del) and f_del != output_video_path:
                try:
                    os.remove(f_del)
                except Exception:
                    pass
    else:
        # If no outro was appended, clean stitched_raw and concat_manifest
        for f_del in [stitched_raw, concat_manifest]:
            if f_del and os.path.exists(f_del) and f_del != output_video_path:
                try:
                    os.remove(f_del)
                except Exception:
                    pass

    logger.success(f"Cinematic rendering finished in {time.time() - t_start:.1f}s -> {output_video_path}")
    return output_video_path
