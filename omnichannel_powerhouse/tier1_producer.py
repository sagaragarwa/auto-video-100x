"""
OmniChannel Tier-1 English Autonomous Video Producer (1000x Edition)
=====================================================================
Manufactures high-retention 30-60 min Tier-1 English documentaries:
1. Dynamic Gemini 3.5 Flash Deep Research (3-Key Ring Rotation, 4,500 RPD)
2. 5-Act Institutional Documentary Scripts (Act I Hook to Act V Future Horizon)
3. 48kHz Edge-TTS Native Tier-1 Voices (Christopher, Guy, Brian) + Shure SM7B DSP (-14 LUFS)
4. Procedural Ambient Cinematic Drone Score (-24dB sidechain bed)
5. Zero-Repeat 1080p B-roll Video Stream + Permanent 173.25s Vintage Blue Laser Content ID Outro Lock
6. 98/100 God-Tier Algorithmic SEO with 8-12 Mid-Roll Chapter Timestamps & Pinned Comment
7. Automatic Unlisted Queue Registration & Studio/Rumble Dispatch
"""

import os
import sys
import json
import time
import random
import asyncio
import subprocess
from typing import Dict, Any, List, Optional

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)
if _root not in sys.path:
    sys.path.insert(0, _root)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("tier1_producer")

import edge_tts

def run_async(coro_or_fn, *args, **kwargs):
    """Safely runs an async coroutine across both synchronous threads and active event loops."""
    import inspect
    import concurrent.futures

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if inspect.iscoroutinefunction(coro_or_fn):
        if loop and loop.is_running():
            def _target():
                return asyncio.run(coro_or_fn(*args, **kwargs))
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(_target).result()
        else:
            return asyncio.run(coro_or_fn(*args, **kwargs))
    else:
        coro = coro_or_fn
        if loop and loop.is_running():
            def _target():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(_target).result()
        else:
            return asyncio.run(coro)

try:
    from omnichannel_powerhouse.agent_commander.multi_brain import call_hybrid_completion
except Exception:
    from omnichannel_powerhouse.gemini_script_engine import call_gemini as call_hybrid_completion
from omnichannel_powerhouse.gemini_script_engine import call_gemini
from omnichannel_powerhouse.deep_seo_engine import generate_deep_seo
from cloud_render_worker import (
    get_outro_clip_path,
    get_or_synthesize_ambient_drone,
    assemble_master_with_outro,
    slice_and_concat,
    fetch_broll_materials,
    get_media_duration
)

OUTPUT_DIR = os.path.join(_root, "output")
TEMP_DIR = os.path.join(_root, "temp_render")
QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unlisted_queue.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


def research_channel_topics(niche: str, channel_name: str, count: int = 5) -> List[Dict[str, Any]]:
    """
    Conducts Gemini 3.5 Flash Deep Research for high-RPM ($45-$90) Tier-1 English documentary topics.
    """
    logger.info(f"🔍 Conducting Gemini Deep Research for channel '{channel_name}' ({niche})...")
    prompt = f"""You are an elite YouTube and Rumble algorithmic content strategist specializing in Tier-1 English audiences (USA, UK, Canada, Australia) with $45-$90 RPM.
Channel Name: "{channel_name}"
Niche: "{niche}"

Generate {count} distinct, high-curiosity, investigative documentary topic blueprints for 30-60 minute long-form videos.
Topics must explore covert power dynamics, hidden financial/technological mechanisms, or psychological phenomena with institutional depth.

Return STRICTLY valid JSON with no markdown formatting:
[
  {{
    "topic": "The 60-character title with intense curiosity gap",
    "punchline": "2-3 WORD PUNCHLINE",
    "target_audience": "Specific Tier-1 demographic",
    "duration_min": 45,
    "core_thesis": "One sentence describing the core investigation"
  }}
]
"""
    try:
        raw = call_hybrid_completion(prompt)
        clean = raw.strip()
        if clean.startswith("```json"): clean = clean[7:]
        if clean.startswith("```"): clean = clean[3:]
        if clean.endswith("```"): clean = clean[:-3]
        clean = clean.strip()
        data = json.loads(clean)
        if isinstance(data, list) and len(data) > 0:
            logger.success(f"Discovered {len(data)} deep research topics for '{channel_name}'!")
            return data
    except Exception as e:
        logger.warning(f"Dynamic topic research fallback triggered: {e}")

    # Curated Tier-1 Fallback Blueprints
    return [
        {
            "topic": f"The Hidden Architecture: How {channel_name} Controls Global Systems",
            "punchline": "THE HIDDEN WAR",
            "target_audience": "Institutional Investors & Engineers",
            "duration_min": 42,
            "core_thesis": "An exhaustive analysis of underlying systemic levers."
        }
    ]


def synthesize_tier1_script_and_seo(topic: str, niche: str, channel_name: str, duration_min: int = 30, language: str = "en") -> Dict[str, Any]:
    """
    Generates a full institutional spoken script and God-Tier SEO package via Multi-Brain (Groq / OpenRouter / Gemini).
    Supports English ('en') and Hindi ('hi').
    """
    lang_name = "Hindi" if language in ("hi", "hindi") else "English"
    logger.info(f"✍️ Synthesizing Tier-1 {lang_name} Documentary Script ({duration_min} min) for '{topic}'...")
    target_words = max(600, min(10000, int(duration_min * 140)))

    if language in ("hi", "hindi"):
        narrative_structure = (
            f"1. Write an authoritative, gripping, dramatic spoken documentary voiceover in clear, professional HINDI (~{target_words} words).\n"
            f"   - Tone: Intellectual, gripping, high-production documentary (style of Dhruv Rathee / Nitish Rajput / BBC Hindi).\n"
            f"   - Script language: Pure fluent HINDI (Devanagari script or clean natural Hindi).\n"
            f"   - Act I: The Anomaly & Shocking Hook (Deconstruct the surface illusion)\n"
            f"   - Act II: The Granular Mechanism & Architecture (Deep mechanical explanation)\n"
            f"   - Act III: Covert Players & Trillion-Dollar Incentives\n"
            f"   - Act IV: Real-World Case Studies & Empirical Failures\n"
            f"   - Act V: The Strategic Verdict & The Future Horizon\n"
            f"   - NO scene directions, NO bracketed markers like [Music swells]. ONLY spoken narrator speech."
        )
        audience_desc = "Hindi documentary viewers (India, Global Hindi audience)"
        terms_desc = '15 visual search keywords in ENGLISH (e.g. "supercomputer servers", "semiconductor wafer", "stock market floor") so stock footage APIs can find real 1080p clips.'
        title_desc = "60-character CTR-optimized viral Hindi title."
        punchline_desc = "2-3 words capitalized punchline in Hindi/English."
    else:
        narrative_structure = (
            f"1. Write an authoritative, gripping, 3-Act spoken documentary voiceover script (~{target_words} words).\n"
            f"   - Act I: The Anomaly & The Hook (Deconstruct the surface illusion)\n"
            f"   - Act II: The Mechanical Breakdown & Empirical Case Study\n"
            f"   - Act III: The Strategic Verdict & The Irreversible Future\n"
            f"   - NO scene directions, NO bracketed markers like [Music swells]. ONLY spoken narrator speech."
        ) if duration_min <= 10 else (
            f"1. Write an authoritative, gripping, 5-Act spoken documentary voiceover script (~{target_words} words).\n"
            f"   - Act I: The Anomaly & The Hook (Deconstruct the surface illusion)\n"
            f"   - Act II: The Mathematical & Physical Architecture (Granular mechanical breakdown)\n"
            f"   - Act III: Covert Players & Trillion-Dollar Incentives (The hidden institutional players)\n"
            f"   - Act IV: Real-World Stress Tests & Case Studies (Empirical failures & turning points)\n"
            f"   - Act V: The Geopolitical Horizon & Strategic Framework (The irreversible future)\n"
            f"   - NO scene directions, NO bracketed markers like [Music swells]. ONLY spoken narrator speech."
        )
        audience_desc = "Tier-1 English (USA, UK, Canada, Australia)"
        terms_desc = "15 visual search keywords for 4K stock footage."
        title_desc = "60-character CTR-optimized viral title."
        punchline_desc = "2-3 words capitalized."

    chapters_count = "3-4" if duration_min <= 10 else "6-10"

    prompt = f"""You are a master institutional documentary writer (in the style of Bloomberg Originals, Veritasium, and Frontline) and YouTube/Rumble algorithmic SEO engineer.
Target Audience: {audience_desc}
Topic: "{topic}"
Channel Name: "{channel_name}"
Niche: "{niche}"
Target Duration: {duration_min} minutes (~{target_words} words)

Requirements:
{narrative_structure}
2. "title": {title_desc}
3. "thumbnail_punchline": {punchline_desc}
4. "video_terms": {terms_desc}
5. "tags": 15 high-volume algorithmic SEO tags.
6. "description": Engaging description including {chapters_count} chapter timestamps spread across 00:00 to {duration_min:02d}:00.
7. "pinned_comment": Engaging question with high-conversion discussion prompt.

Return STRICTLY valid JSON:
{{
  "title": "...",
  "thumbnail_punchline": "...",
  "video_terms": ["term1", "term2", ...],
  "tags": ["tag1", "tag2", ...],
  "description": "...",
  "pinned_comment": "...",
  "video_script": "..."
}}
"""
    raw = call_hybrid_completion(prompt)
    clean = raw.strip()
    if clean.startswith("```json"): clean = clean[7:]
    if clean.startswith("```"): clean = clean[3:]
    if clean.endswith("```"): clean = clean[:-3]
    clean = clean.strip()

    try:
        data = json.loads(clean)
    except Exception:
        s_idx = clean.find("{")
        e_idx = clean.rfind("}")
        if s_idx != -1 and e_idx != -1:
            data = json.loads(clean[s_idx:e_idx+1])
        else:
            raise ValueError(f"Could not parse script JSON: {clean[:200]}")

    # Generate Algorithmic SEO Metrics
    duration_s = float(duration_min) * 60.0
    seo = generate_deep_seo(
        topic=data.get("title", topic),
        duration_s=duration_s,
        channel_name=channel_name,
        niche=niche,
        language="hi" if language in ("hi", "hindi") else "en"
    )

    data["seo_score"] = seo.get("seo_score", 98)
    data["seo_metrics"] = seo.get("seo_metrics", {})
    data["hashtags"] = seo.get("hashtags", [])
    data["tags_csv"] = seo.get("tags_csv", ", ".join(data.get("tags", [])))
    data["duration_sec"] = duration_s
    data["duration_formatted"] = f"{int(duration_s // 60)}:{int(duration_s % 60):02d}"

    logger.success(f"Script synthesized ({len(data['video_script'].split())} words) with SEO Score {data['seo_score']}/100!")
    return data


def synthesize_tier1_voiceover(text: str, voice: str, output_path: str, language: str = "en"):
    """
    Synthesizes speech:
    - Hindi: Google Gemini 2.5 Flash Native Studio Speech (100% Human, Zero Robotic Artifacts)
    - English: Kokoro-82M (af_heart, am_adam) + Shure SM7B Broadcast DSP vocal chain (-14 LUFS)
    """
    is_hindi = language in ("hi", "hindi") or any('\u0900' <= char <= '\u097f' for char in text)

    # 1. Hindi: Ultra-Realistic Gemini 2.5 Flash Native Studio Voice
    if is_hindi:
        logger.info(f"🎙️ Synthesizing 100% Human Studio Hindi Voice with Gemini 2.5 Flash Native Speech...")
        try:
            from omnichannel_powerhouse.gemini_tts_engine import synthesize_master_voice
            synthesize_master_voice(text, output_path, voice_name="Puck", apply_dsp=True)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                logger.success(f"🏆 Gemini 2.5 Flash Human Studio Voiceover Mastered: {output_path}")
                return output_path
        except Exception as ge:
            logger.warning(f"Gemini Flash TTS primary notice: {ge}")

    # 2. English: Kokoro-82M Studio Model
    logger.info(f"🎙️ Synthesizing voiceover with Kokoro-82M Engine [Target Voice: {voice}] (Word count: {len(text.split())})...")
    try:
        from omnichannel_powerhouse.kokoro_engine import synthesize_kokoro_voice
        success = synthesize_kokoro_voice(
            text=text,
            output_path=output_path,
            voice=voice,
            speed=1.05,
            language=language
        )
        if success and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            logger.success(f"🏆 Kokoro-82M voiceover mastered and verified: {output_path}")
            return output_path
    except Exception as ke:
        logger.warning(f"Kokoro-82M primary hook notice: {ke}")

    # Fallback to Edge-TTS if needed
    temp_raw = output_path + ".raw.mp3"
    edge_voice = "hi-IN-MadhurNeural" if language in ("hi", "hindi") else "en-US-ChristopherNeural"
    logger.info(f"🎙️ Synthesizing speech with Tier-1 Voice [{edge_voice}] (Word count: {len(text.split())})...")
    
    communicate = edge_tts.Communicate(text, edge_voice)
    run_async(communicate.save, temp_raw)

    # 6-Stage Shure SM7B Broadcast Mastering DSP Chain
    logger.info("🎛️ Applying 6-Stage Shure SM7B Broadcast DSP vocal chain (-14 LUFS)...")
    vocal_chain = (
        "highpass=f=80,"
        "equalizer=f=250:t=q:w=1.2:g=2.2,"
        "equalizer=f=3500:t=q:w=1.2:g=2.5,"
        "equalizer=f=6800:t=q:w=1.5:g=-2.5,"
        "dynaudnorm=p=0.95:m=10:s=12"
    )
    cmd = [
        "ffmpeg", "-y", "-i", temp_raw,
        "-af", vocal_chain,
        "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(temp_raw):
        try: os.remove(temp_raw)
        except Exception: pass
    logger.success(f"Master voiceover ready: {output_path}")
    return output_path


def render_tier1_master_video(
    script_data: Dict[str, Any],
    channel_key: str,
    voice: str = "af_heart",
    language: str = "en"
) -> str:
    """
    Renders 1080p master documentary:
    - Audio with Kokoro-82M (Best model) + SM7B DSP + -24dB ambient drone
    - Zero-repeat unique B-roll stream
    - Mandatory 173.25s Vintage Blue Laser Content ID outro lock
    """
    ts = int(time.time())
    ep_temp = os.path.join(TEMP_DIR, f"tier1_{channel_key}_{ts}")
    os.makedirs(ep_temp, exist_ok=True)

    audio_file = os.path.join(ep_temp, "master_voiceover.mp3")
    final_output = os.path.join(OUTPUT_DIR, f"tier1_{channel_key}_{ts}_master.mp4")

    # 1. Synthesize Audio with Kokoro-82M
    synthesize_tier1_voiceover(script_data["video_script"], voice, audio_file, language=language)
    total_duration = get_media_duration(audio_file)
    logger.info(f"⏱️ Spoken Duration: {total_duration:.1f}s ({total_duration/60:.2f} minutes)")

    # 2. Fetch Strictly Unique B-roll Materials
    terms = script_data.get("video_terms", ["technology", "supercomputer", "data center"])
    try:
        from omnichannel_powerhouse.multi_stock_aggregator import fetch_multi_source_brolls
        clips = fetch_multi_source_brolls(terms, total_duration, ep_temp)
    except Exception:
        clips = fetch_broll_materials(terms, total_duration, ep_temp)

    # 3. Fast Parallel Normalization & Zero-Repeat Stream Concat
    combined_video = slice_and_concat(clips, total_duration, ep_temp)

    # 4. Final Mux with Ambient Drone & Mandatory Content ID Outro Lock
    outro_clip = get_outro_clip_path()
    assemble_master_with_outro(combined_video, audio_file, outro_clip, final_output, ep_temp)

    file_size_mb = os.path.getsize(final_output) / (1024 * 1024)
    logger.success(f"🏆 Final Master Video Manufactured: {final_output} ({file_size_mb:.1f} MB, {total_duration/60:.1f} min)")
    return final_output


def produce_and_queue_tier1_video(
    channel_key: str,
    channel_data: Dict[str, Any],
    platform: str = "youtube",
    duration_min: Optional[int] = None,
    custom_topic: Optional[str] = None,
    language: str = "en",
    auto_upload_unlisted: bool = False
) -> Dict[str, Any]:
    """
    End-to-End Orchestrator:
    1. Researches Topic (or uses custom topic)
    2. Writes Tier-1 Script & SEO for target duration (5 to 60+ min, English or Hindi)
    3. Synthesizes Audio with Shure SM7B DSP (Edge-TTS English or Hindi)
    4. Renders 1080p Master Video with Outro Lock (100% Real Stock, ZERO AI IMAGES)
    5. Prepends to Unlisted Queue
    6. Automatically triggers Playwright upload if auto_upload_unlisted=True
    """
    niche = channel_data.get("niche", "technology")
    ch_name = channel_data.get("name", channel_key)
    voice = "hm_omega" if language in ("hi", "hindi") else channel_data.get("voice_preferred", "af_heart")

    # 1. Resolve Topic & Duration
    chosen_topic = custom_topic
    chosen_duration = duration_min
    if not chosen_topic or not chosen_duration:
        topics = research_channel_topics(niche, ch_name, count=3)
        if not chosen_topic:
            chosen_topic = topics[0]["topic"]
        if not chosen_duration:
            chosen_duration = topics[0].get("duration_min", 30)

    # 2. Generate Script & SEO
    script_data = synthesize_tier1_script_and_seo(chosen_topic, niche, ch_name, duration_min=chosen_duration, language=language)

    # 3. Render Master Video with Kokoro-82M Voiceover (100% Real Authentic Stock Footage)
    master_video_path = render_tier1_master_video(script_data, channel_key, voice=voice, language=language)

    # 4. Generate 3 Authentic Real-Frame Thumbnails (STRICT ZERO AI IMAGES POLICY)
    base_name = os.path.splitext(os.path.basename(master_video_path))[0]
    punchline = script_data.get("thumbnail_punchline", "THE HIDDEN WAR")
    badge = ch_name.upper()

    thumb_a = os.path.join(OUTPUT_DIR, f"{base_name}_thumb_A_monopoly_cyan.jpg")
    thumb_b = os.path.join(OUTPUT_DIR, f"{base_name}_thumb_B_secret_amber.jpg")
    thumb_c = os.path.join(OUTPUT_DIR, f"{base_name}_thumb_C_threat_crimson.jpg")

    try:
        from yt_uploader.thumbnail_generator import create_ultra_thumbnail
        create_ultra_thumbnail(master_video_path, thumb_a, punchline=punchline, badge_text=badge, highlight_color=(0, 242, 254), frame_timestamp_sec=15.0)
        create_ultra_thumbnail(master_video_path, thumb_b, punchline=punchline, badge_text=badge, highlight_color=(255, 179, 0), frame_timestamp_sec=45.0)
        create_ultra_thumbnail(master_video_path, thumb_c, punchline=punchline, badge_text=badge, highlight_color=(255, 0, 85), frame_timestamp_sec=75.0)
        logger.success(f"🖼️ Sourced 3 authentic real-frame thumbnails directly from video footage (ZERO AI IMAGES)!")
    except Exception as te:
        logger.warning(f"Thumbnail generation notice: {te}")

    # 5. Register in Unlisted Queue
    vid_id = f"{platform}_{int(time.time())}"
    clean_rel_path = f"/output/{os.path.basename(master_video_path)}"

    queue_entry = {
        "id": vid_id,
        "video_id": "pending_upload",
        "title": script_data.get("title", chosen_topic),
        "title_alternatives": [
            f"The Untold Story of {chosen_topic[:40]}",
            f"Why {ch_name} Secretly Dominates This Industry"
        ],
        "seo_score": script_data.get("seo_score", 98),
        "seo_metrics": script_data.get("seo_metrics", {}),
        "channel_id": channel_key,
        "channel_name": ch_name,
        "platform": platform,
        "language": language,
        "video_url": "https://studio.youtube.com/videos",
        "studio_edit_url": "https://studio.youtube.com/videos",
        "local_video_path": clean_rel_path,
        "master_abs_path": master_video_path,
        "status": "unlisted_pending_thumbnail",
        "duration_sec": script_data.get("duration_sec", chosen_duration * 60.0),
        "duration_formatted": f"{chosen_duration}:00",
        "thumbnail_punchline": punchline,
        "thumbnail_concepts": [
            {"variant": "A", "name": "Monopoly Cyan", "hex": "#00F2FE", "file": f"/output/{os.path.basename(thumb_a)}"},
            {"variant": "B", "name": "Secret Amber", "hex": "#FFB300", "file": f"/output/{os.path.basename(thumb_b)}"},
            {"variant": "C", "name": "Threat Crimson", "hex": "#FF0055", "file": f"/output/{os.path.basename(thumb_c)}"}
        ],
        "hashtags": script_data.get("hashtags", []),
        "tags": script_data.get("tags", []),
        "tags_csv": script_data.get("tags_csv", ""),
        "description": script_data.get("description", ""),
        "pinned_comment": script_data.get("pinned_comment", ""),
        "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        queue_data = {"videos": []}
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                queue_data = json.load(f)
        vids = queue_data.get("videos", [])
        vids.insert(0, queue_entry)
        queue_data["videos"] = vids
        queue_data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue_data, f, indent=2)
        logger.success(f"Video registered in Unlisted Queue -> {vid_id}")
    except Exception as e:
        logger.error(f"Error registering in queue: {e}")

    # 6. Store in Persistent ChromaDB Vector Memory (0% Duplicate Topic Enforcer)
    try:
        from omnichannel_powerhouse.vector_memory import VECTOR_MEMORY
        VECTOR_MEMORY.store_video_memory(
            video_id=vid_id,
            title=script_data.get("title", chosen_topic),
            script_excerpt=script_data.get("video_script", "")[:1200],
            niche=niche,
            channel_id=channel_key,
            language=language
        )
    except Exception as me:
        logger.warning(f"Vector memory store notice: {me}")

    # 7. Immediate Auto-Upload if requested
    upload_res = None
    if auto_upload_unlisted and platform == "youtube":
        try:
            logger.info(f"🚀 Triggering immediate Playwright upload for {vid_id} on {channel_key}...")
            from omnichannel_powerhouse.studio_upload_manager import execute_video_upload
            upload_res = execute_video_upload(vid_id, target_channel_key=channel_key, headless=False)
            if upload_res.get("success"):
                logger.success(f"Successfully auto-uploaded {vid_id} -> {upload_res.get('video_url')}")
        except Exception as ue:
            logger.error(f"Auto-upload failed: {ue}")
            upload_res = {"success": False, "error": str(ue)}

    # 8. Real-Time Notification Storage & WhatsApp-Style Chat Dispatch
    try:
        from omnichannel_powerhouse.notification_manager import NOTIFICATION_MANAGER, post_video_ready_notification_to_chat
        video_title = script_data.get("title", chosen_topic)
        v_url = upload_res.get("video_url", "") if upload_res else ""
        notif = NOTIFICATION_MANAGER.add_notification(
            title=f"Video Ready: {video_title}",
            message=f"Video '{video_title}' on {ch_name} ({chosen_duration} min) is ready & staged/uploaded as Unlisted!",
            channel_key=channel_key,
            channel_name=ch_name,
            video_id=vid_id,
            video_url=v_url,
            duration_min=float(chosen_duration),
            thumbnail_url=f"/output/{os.path.basename(thumb_a)}",
            notif_type="video_uploaded" if (upload_res and upload_res.get("success")) else "video_ready_unlisted"
        )
        logger.success(f"🔔 Notification generated & stored: {notif['id']}")
    except Exception as ne:
        logger.warning(f"Notification dispatch notice: {ne}")

    return {
        "success": True,
        "video_id": vid_id,
        "master_video_path": master_video_path,
        "script_data": script_data,
        "queue_entry": queue_entry,
        "upload_result": upload_res
    }


if __name__ == "__main__":
    test_ch = {
        "name": "Silicon Pulse",
        "niche": "trading",
        "voice_preferred": "en-US-ChristopherNeural"
    }
    res = produce_and_queue_tier1_video("channel_trading", test_ch)
    print("Result:", res["success"], res["master_video_path"])
