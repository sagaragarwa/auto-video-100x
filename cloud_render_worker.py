#!/usr/bin/env python3
"""
⚡ 100X Cloud Render Worker (Headless Linux & Cloud Runner)
Designed for GitHub Actions, Kaggle, Colab, and Linux Servers.
Renders 1080p Full HD viral documentaries in ~3-5 minutes per episode.
"""

import os
import sys
import time
import json
import argparse
import asyncio
import subprocess
from concurrent.futures import ThreadPoolExecutor

import edge_tts
import requests

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "48724139-1fbe7e777966fce52b390343f")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
TEMP_DIR = os.environ.get("TEMP_DIR", "temp_render")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

async def generate_audio_and_srt(text: str, voice: str, audio_path: str, srt_path: str):
    """Generate high-fidelity neural audio and word-level SRT subtitles."""
    print(f"🎙️ Generating voiceover with {voice}...")
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()
    
    with open(audio_path, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
                
    with open(srt_path, "w", encoding="utf-8") as file:
        file.write(submaker.get_srt())
    print(f"✅ Audio generated: {audio_path} ({os.path.getsize(audio_path) / 1024:.1f} KB)")
    print(f"✅ Subtitles generated: {srt_path}")

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
        print(f"⚠️ Download failed for {url}: {e}")
    return None

def fetch_broll_materials(terms: list[str], target_duration: float, cache_dir: str) -> list[str]:
    """Search and download 1080p landscape clips for terms until duration covered."""
    print(f"🔍 Searching Pixabay for keywords: {terms}...")
    download_targets = []
    total_found_duration = 0.0
    
    for term in terms:
        if total_found_duration >= target_duration + 30.0:
            break
        url = (
            f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}"
            f"&q={requests.utils.quote(term)}&video_type=film&per_page=15"
        )
        try:
            res = requests.get(url, timeout=15).json()
            hits = res.get("hits", [])
            for h in hits:
                v_dur = h.get("duration", 0)
                # Select 1080p or high-res mp4
                v_sizes = h.get("videos", {})
                best_video = (
                    v_sizes.get("large", {}).get("url") or
                    v_sizes.get("medium", {}).get("url") or
                    v_sizes.get("small", {}).get("url")
                )
                if best_video:
                    clip_name = os.path.join(cache_dir, f"pixabay_{h['id']}.mp4")
                    download_targets.append((best_video, clip_name))
                    total_found_duration += v_dur
                    if total_found_duration >= target_duration + 30.0:
                        break
        except Exception as e:
            print(f"⚠️ Query error for '{term}': {e}")
            
    print(f"📥 Downloading {len(download_targets)} B-roll clips in parallel...")
    valid_clips = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for saved_path in pool.map(download_pixabay_clip, download_targets):
            if saved_path and os.path.exists(saved_path):
                valid_clips.append(saved_path)
                
    print(f"✅ Downloaded {len(valid_clips)} valid clips ({total_found_duration:.1f}s footage).")
    return valid_clips

def slice_single_clip(args: tuple) -> str | None:
    """Fast-slice a 5-second 1080p clip directly with FFmpeg."""
    source_file, out_file, clip_duration = args
    # Normalize to 1920x1080 30fps yuv420p with ultrafast encoding
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
    """Slice clips in parallel and concatenate into single stream."""
    clip_duration = 5.0
    required_count = int(total_duration / clip_duration) + 2
    
    # Loop available clips to cover required count
    selected_sources = []
    while len(selected_sources) < required_count:
        for c in clips:
            selected_sources.append(c)
            if len(selected_sources) >= required_count:
                break
                
    print(f"⚡ Slicing {len(selected_sources)} clips with multi-core FFmpeg...")
    slice_tasks = []
    for idx, src in enumerate(selected_sources):
        out_clip = os.path.join(temp_dir, f"slice_{idx:04d}.mp4")
        slice_tasks.append((src, out_clip, clip_duration))
        
    sliced_files = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for idx, result in enumerate(pool.map(slice_single_clip, slice_tasks), 1):
            if result:
                sliced_files.append(result)
            if idx % 20 == 0 or idx == len(slice_tasks):
                print(f"📊 Slicing progress: {idx}/{len(slice_tasks)} clips ({(idx / len(slice_tasks)) * 100:.1f}%)")
                
    # Concat using FFmpeg stream copy
    concat_list_file = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for sf in sliced_files:
            clean_path = os.path.abspath(sf).replace("\\", "/")
            f.write(f"file '{clean_path}'\n")
            
    combined_mp4 = os.path.join(temp_dir, "combined_video.mp4")
    print("⚡ Instant stream-copy concat...")
    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_file,
        "-t", f"{total_duration:.3f}", "-c", "copy", "-movflags", "+faststart", combined_mp4
    ]
    subprocess.run(concat_cmd, check=True)
    print(f"✅ Concat completed in seconds! File: {combined_mp4}")
    return combined_mp4

def burn_subtitles_and_mux_audio(video_path: str, audio_path: str, srt_path: str, output_path: str):
    """Burn subtitles and mix audio into final 1080p MP4."""
    print("✨ Burning subtitles & mixing audio...")
    escaped_srt = os.path.abspath(srt_path).replace("\\", "/").replace(":", "\\:")
    
    style = (
        "FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,BorderStyle=1,Outline=2.0,Alignment=2,MarginV=35"
    )
    vf = f"subtitles=filename='{escaped_srt}':force_style='{style}'"
    
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
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg render failed: {res.stderr[:400]}")
    print(f"🏆 Final Master Video Ready: {output_path} ({os.path.getsize(output_path) / (1024 * 1024):.2f} MB)")

def process_episode(episode_index: int):
    """Main pipeline execution for a single episode."""
    start_time = time.time()
    print("=" * 65)
    print(f"🚀 CLOUD WORKER RUNNING EPISODE {episode_index:02d}")
    print("=" * 65)
    
    with open("series_tasks.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)["tasks"]
        
    ep = next((t for t in tasks if t["episode_number"] == episode_index), tasks[episode_index - 1])
    print(f"🎬 Title: {ep['title']}")
    print(f"📝 Word Count: {len(ep['video_script'].split())} words")
    
    ep_temp = os.path.join(TEMP_DIR, f"ep_{episode_index:02d}")
    os.makedirs(ep_temp, exist_ok=True)
    
    audio_file = os.path.join(ep_temp, "voiceover.mp3")
    srt_file = os.path.join(ep_temp, "subtitles.srt")
    final_output = os.path.join(OUTPUT_DIR, f"episode_{episode_index:02d}_master.mp4")
    
    # 1. Voiceover & SRT (10-20 seconds)
    is_hindi = any(0x0900 <= ord(c) <= 0x097F for c in ep["video_script"][:500])
    voice = "hi-IN-MadhurNeural" if is_hindi else "en-US-ChristopherNeural"
    asyncio.run(generate_audio_and_srt(ep["video_script"], voice, audio_file, srt_file))
    
    total_duration = get_audio_duration(audio_file)
    print(f"⏱️ Spoken Duration: {total_duration:.1f}s ({total_duration / 60:.2f} minutes)")
    
    # 2. B-Roll Procurement (20-30 seconds over datacenter fiber)
    terms = ep.get("video_terms", ["wall street", "stock market", "technology"])
    clips = fetch_broll_materials(terms, total_duration, ep_temp)
    if not clips:
        raise RuntimeError("No B-Roll clips could be downloaded!")
        
    # 3. Parallel Slicing & Instant Concat (60-90 seconds)
    combined_video = slice_and_concat(clips, total_duration, ep_temp)
    
    # 4. Final Subtitles & Audio Mux (30-45 seconds)
    burn_subtitles_and_mux_audio(combined_video, audio_file, srt_file, final_output)
    
    elapsed = time.time() - start_time
    print("=" * 65)
    print(f"🎉 EPISODE {episode_index:02d} COMPLETED IN {elapsed:.1f}s ({elapsed / 60:.2f} MIN)!")
    print(f"📦 Output File: {final_output}")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="100X Cloud Render Worker")
    parser.add_argument("--episode", type=int, default=1, help="Episode index (1 to 20)")
    args = parser.parse_args()
    process_episode(args.episode)
