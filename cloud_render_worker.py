#!/usr/bin/env python3
"""
100X Cloud Render Worker (Ultra-Fast Clean Documentary Engine)
- Zero Subtitles (Pure, clean cinematic 1080p video)
- Automated Content ID Outro Clip appended at the exact end of every video
- 100% Stream-copy concatenation (Blazing fast ~60s render per episode)
"""

import os
import sys
import time
import json
import shutil
import argparse
import asyncio
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Force UTF-8 encoding on standard streams
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import edge_tts
import requests

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "48724139-1fbe7e777966fce52b390343f")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
TEMP_DIR = os.environ.get("TEMP_DIR", "temp_render")
OUTRO_CLIP_PATH = os.environ.get("OUTRO_CLIP_PATH", os.path.join("assets", "outro_clip.mp4"))

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


async def generate_pure_audio(text: str, voice: str, audio_path: str):
    """Generate high-fidelity neural audio (pure speech, zero subtitle overhead)."""
    print(f"[VOICE] Synthesizing speech with neural voice: {voice}...", flush=True)
    communicate = edge_tts.Communicate(text, voice)
    total_bytes = 0

    with open(audio_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
                total_bytes += len(chunk["data"])

    print(f"[VOICE] Audio successfully generated: {audio_path} ({total_bytes / 1024:.1f} KB)", flush=True)


def get_media_duration(file_path: str) -> float:
    """Get exact duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def download_pixabay_clip(item: tuple) -> str | None:
    """Download single 1080p landscape clip from Pixabay."""
    url, filename = item
    if os.path.exists(filename) and os.path.getsize(filename) > 50000:
        return filename
    try:
        r = requests.get(url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            return filename
    except Exception as e:
        print(f"[WARN] Download failed for {url}: {e}", flush=True)
    return None


def fetch_broll_materials(terms: list[str], target_duration: float, cache_dir: str) -> list[str]:
    """Search and download 1080p landscape clips for terms."""
    print(f"[SEARCH] Querying Pixabay for keywords: {terms}...", flush=True)
    download_targets = []
    seen_ids = set()

    for term in terms:
        if len(download_targets) >= 12:
            break
        url = (
            f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}"
            f"&q={requests.utils.quote(term)}&video_type=film&per_page=10"
        )
        try:
            res = requests.get(url, timeout=15).json()
            hits = res.get("hits", [])
            for h in hits:
                if h["id"] in seen_ids:
                    continue
                seen_ids.add(h["id"])
                v_sizes = h.get("videos", {})
                best_video = (
                    v_sizes.get("large", {}).get("url") or
                    v_sizes.get("medium", {}).get("url") or
                    v_sizes.get("small", {}).get("url")
                )
                if best_video:
                    clip_name = os.path.join(cache_dir, f"pixabay_{h['id']}.mp4")
                    download_targets.append((best_video, clip_name))
                    if len(download_targets) >= 12:
                        break
        except Exception as e:
            print(f"[WARN] Query error for '{term}': {e}", flush=True)

    print(f"[DOWNLOAD] Downloading {len(download_targets)} B-roll clips in parallel...", flush=True)
    valid_clips = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for saved_path in pool.map(download_pixabay_clip, download_targets):
            if saved_path and os.path.exists(saved_path) and os.path.getsize(saved_path) > 50000:
                valid_clips.append(saved_path)

    # Fallback pattern if 0 clips downloaded
    if not valid_clips:
        print("[WARN] Pixabay returned 0 clips, generating local motion backdrop...", flush=True)
        fallback_clip = os.path.join(cache_dir, "fallback_motion.mp4")
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "testsrc=size=1920x1080:rate=30",
            "-t", "5",
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an",
            fallback_clip
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        valid_clips.append(fallback_clip)

    print(f"[DOWNLOAD] Ready with {len(valid_clips)} valid clips.", flush=True)
    return valid_clips


def slice_single_clip(args: tuple) -> str | None:
    """Normalize and slice a clip to 5 seconds 1080p 30fps."""
    source_file, out_file, clip_duration = args
    if os.path.exists(out_file) and os.path.getsize(out_file) > 10000:
        return out_file
    cmd = [
        "ffmpeg", "-y", "-ss", "0", "-i", source_file, "-t", str(clip_duration),
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-an", out_file
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
        return out_file
    return None


def slice_and_concat(clips: list[str], total_duration: float, temp_dir: str) -> str:
    """Normalize unique clips once, then assemble continuous stream via FFmpeg concat copy."""
    clip_duration = 5.0

    print(f"[SLICE] Normalizing {len(clips)} unique clips to 1080p 30fps...", flush=True)
    slice_tasks = []
    for idx, src in enumerate(clips):
        out_clip = os.path.join(temp_dir, f"normalized_{idx:03d}.mp4")
        slice_tasks.append((src, out_clip, clip_duration))

    normalized_files = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(slice_single_clip, slice_tasks):
            if result:
                normalized_files.append(result)

    if not normalized_files:
        raise RuntimeError("Failed to normalize any B-roll clips!")

    required_count = int(total_duration / clip_duration) + 2
    concat_list_file = os.path.join(temp_dir, "concat_list.txt")

    with open(concat_list_file, "w", encoding="utf-8") as f:
        for i in range(required_count):
            sf = normalized_files[i % len(normalized_files)]
            clean_path = os.path.abspath(sf).replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    combined_mp4 = os.path.join(temp_dir, "combined_video.mp4")
    print(f"[CONCAT] Fast stream-copy concat for {total_duration:.1f}s ({required_count} segments)...", flush=True)
    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_file,
        "-t", f"{total_duration:.3f}", "-c", "copy", "-movflags", "+faststart", combined_mp4
    ]
    subprocess.run(concat_cmd, check=True)
    print(f"[CONCAT] Video stream assembled successfully: {combined_mp4}", flush=True)
    return combined_mp4


def assemble_master_with_outro(video_path: str, audio_path: str, outro_clip_path: str, output_path: str, temp_dir: str):
    """
    1. Mux voiceover into video without re-encoding (clean, zero subtitles).
    2. Seamlessly append Content ID outro clip at the end.
    Total execution time: ~5-10 seconds!
    """
    print("[MUX] Combining 1080p video with audio (clean, zero subtitles)...", flush=True)
    main_episode_path = os.path.join(temp_dir, "main_episode_audio.mp4")

    # Mux audio into 1080p stream with standardized audio parameters (48kHz, stereo, 192k)
    mux_cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest", "-movflags", "+faststart",
        main_episode_path
    ]
    subprocess.run(mux_cmd, check=True)
    print(f"[MUX] Main documentary stream ready: {main_episode_path}", flush=True)

    # Append Content ID outro clip if present
    if outro_clip_path and os.path.exists(outro_clip_path) and os.path.getsize(outro_clip_path) > 10000:
        print(f"[OUTRO] Appending Content ID clip: {outro_clip_path}...", flush=True)

        # Standardize outro audio to 48kHz stereo
        normalized_outro = os.path.join(temp_dir, "outro_standardized.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", outro_clip_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            normalized_outro
        ], check=True, capture_output=True)

        # Stream-copy concatenate [main_episode, outro]
        final_concat_list = os.path.join(temp_dir, "final_concat_list.txt")
        with open(final_concat_list, "w", encoding="utf-8") as f:
            f.write(f"file '{os.path.abspath(main_episode_path).replace(chr(92), '/')}'\n")
            f.write(f"file '{os.path.abspath(normalized_outro).replace(chr(92), '/')}'\n")

        concat_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", final_concat_list,
            "-c", "copy", "-movflags", "+faststart",
            output_path
        ]
        subprocess.run(concat_cmd, check=True)
        print(f"[OUTRO] Master video with outro successfully merged: {output_path}", flush=True)
    else:
        print("[WARN] Outro clip not found, saving main episode directly.", flush=True)
        shutil.copyfile(main_episode_path, output_path)

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[DONE] Final Master Video Ready: {output_path} ({file_size_mb:.2f} MB)", flush=True)


def process_episode(episode_index: int):
    """Main pipeline execution for a single episode."""
    start_time = time.time()
    print("=" * 65, flush=True)
    print(f"[START] CLOUD WORKER RUNNING EPISODE {episode_index:02d}", flush=True)
    print("=" * 65, flush=True)

    with open("series_tasks.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)["tasks"]

    ep = next((t for t in tasks if t["episode_number"] == episode_index), tasks[episode_index - 1])
    print(f"[TITLE] {ep['title']}", flush=True)
    print(f"[SCRIPT] Word Count: {len(ep['video_script'].split())} words", flush=True)

    ep_temp = os.path.join(TEMP_DIR, f"ep_{episode_index:02d}")
    os.makedirs(ep_temp, exist_ok=True)

    audio_file = os.path.join(ep_temp, "voiceover.mp3")
    final_output = os.path.join(OUTPUT_DIR, f"episode_{episode_index}_master.mp4")

    # 1. Voiceover (Pure Audio, Zero Subtitles)
    is_hindi = any(0x0900 <= ord(c) <= 0x097F for c in ep["video_script"][:500])
    voice = "hi-IN-MadhurNeural" if is_hindi else "en-US-ChristopherNeural"
    asyncio.run(generate_pure_audio(ep["video_script"], voice, audio_file))

    total_duration = get_media_duration(audio_file)
    print(f"[DURATION] Spoken Duration: {total_duration:.1f}s ({total_duration / 60:.2f} minutes)", flush=True)

    # 2. B-Roll Procurement
    terms = ep.get("video_terms", ["wall street", "stock market", "technology"])
    clips = fetch_broll_materials(terms, total_duration, ep_temp)

    # 3. Fast Parallel Normalization & Instant Concat
    combined_video = slice_and_concat(clips, total_duration, ep_temp)

    # 4. Final Mux & Content ID Outro Append (Zero Subtitles)
    assemble_master_with_outro(combined_video, audio_file, OUTRO_CLIP_PATH, final_output, ep_temp)

    elapsed = time.time() - start_time
    print("=" * 65, flush=True)
    print(f"[FINISH] EPISODE {episode_index:02d} COMPLETED IN {elapsed:.1f}s ({elapsed / 60:.2f} MIN)!", flush=True)
    print(f"[OUTPUT] {final_output}", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="100X Cloud Render Worker")
    parser.add_argument("--episode", type=int, default=1, help="Episode index (1 to 20)")
    args = parser.parse_args()
    process_episode(args.episode)
