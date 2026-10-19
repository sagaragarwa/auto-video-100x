#!/usr/bin/env python3
"""
100X Cloud Render Worker (Headless Linux & Cloud Runner)
Designed for GitHub Actions, Kaggle, Colab, and Linux/Windows Servers.
Renders 1080p Full HD viral documentaries in ~2-4 minutes per episode.
"""

import os
import sys
import time
import json
import argparse
import asyncio
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Force UTF-8 encoding on standard streams to prevent charmap encoding errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import edge_tts
import requests

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "48724139-1fbe7e777966fce52b390343f")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
TEMP_DIR = os.environ.get("TEMP_DIR", "temp_render")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


async def generate_audio_and_srt(text: str, voice: str, audio_path: str, srt_path: str):
    """Generate high-fidelity neural audio and SRT subtitles."""
    print(f"[VOICE] Generating voiceover with {voice}...", flush=True)
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()
    total_audio = 0

    with open(audio_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
                total_audio += len(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)

    srt_content = submaker.get_srt()
    if not srt_content.strip():
        # Fallback subtitle generation if stream had no boundary tags
        print("[WARN] No boundary tags received, creating synthetic subtitles...", flush=True)
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        lines = []
        # Estimate ~3 seconds per sentence
        curr_time = 0.0
        for i, s in enumerate(sentences, 1):
            dur = max(2.0, min(8.0, len(s.split()) * 0.45))
            start_s = f"{int(curr_time // 3600):02d}:{int((curr_time % 3600) // 60):02d}:{int(curr_time % 60):02d},000"
            end_t = curr_time + dur
            end_s = f"{int(end_t // 3600):02d}:{int((end_t % 3600) // 60):02d}:{int(end_t % 60):02d},000"
            lines.append(f"{i}\n{start_s} --> {end_s}\n{s}\n")
            curr_time = end_t
        srt_content = "\n".join(lines)

    with open(srt_path, "w", encoding="utf-8") as file:
        file.write(srt_content)

    print(f"[VOICE] Audio generated: {audio_path} ({os.path.getsize(audio_path) / 1024:.1f} KB)", flush=True)
    print(f"[VOICE] Subtitles generated: {srt_path} ({len(srt_content)} chars)", flush=True)


def get_audio_duration(audio_path: str) -> float:
    """Get exact duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
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

    # Fallback to test video pattern if no clips downloaded
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

    # Calculate required repetitions to cover full audio duration
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


def burn_subtitles_and_mux_audio(video_path: str, audio_path: str, srt_path: str, output_path: str):
    """Burn subtitles and mix audio into final 1080p MP4."""
    print("[MUX] Rendering final master with subtitles and audio...", flush=True)
    has_srt = os.path.exists(srt_path) and os.path.getsize(srt_path) > 20
    rendered = False

    if has_srt:
        escaped_srt = os.path.abspath(srt_path).replace("\\", "/").replace(":", "\\:")
        style = (
            "FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,BorderStyle=1,Outline=2.0,Alignment=2,MarginV=35"
        )
        vf = f"subtitles='{escaped_srt}':force_style='{style}'"

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            output_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            rendered = True
            print(f"[SUCCESS] Master video with burned subtitles rendered: {output_path}", flush=True)
        else:
            print(f"[WARN] Subtitle burn warning ({res.stderr[:200] if res.stderr else ''}), falling back to direct audio mux...", flush=True)

    if not rendered:
        # Fallback mux without subtitles filter (guarantees completion)
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"[SUCCESS] Master video rendered with audio: {output_path}", flush=True)

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
    srt_file = os.path.join(ep_temp, "subtitles.srt")
    final_output = os.path.join(OUTPUT_DIR, f"episode_{episode_index}_master.mp4")

    # 1. Voiceover & SRT
    is_hindi = any(0x0900 <= ord(c) <= 0x097F for c in ep["video_script"][:500])
    voice = "hi-IN-MadhurNeural" if is_hindi else "en-US-ChristopherNeural"
    asyncio.run(generate_audio_and_srt(ep["video_script"], voice, audio_file, srt_file))

    total_duration = get_audio_duration(audio_file)
    print(f"[DURATION] Spoken Duration: {total_duration:.1f}s ({total_duration / 60:.2f} minutes)", flush=True)

    # 2. B-Roll Procurement
    terms = ep.get("video_terms", ["wall street", "stock market", "technology"])
    clips = fetch_broll_materials(terms, total_duration, ep_temp)

    # 3. Fast Parallel Normalization & Instant Concat
    combined_video = slice_and_concat(clips, total_duration, ep_temp)

    # 4. Final Subtitles & Audio Mux
    burn_subtitles_and_mux_audio(combined_video, audio_file, srt_file, final_output)

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
