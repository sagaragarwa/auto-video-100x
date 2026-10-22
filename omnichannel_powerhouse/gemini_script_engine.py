"""
OmniChannel Gemini Script & SEO Engine
Powered by Google Gemini Flash (Free Tier)
Generates Institutional PhD-Grade 6-Beat Documentaries with 0 Antigravity Token Consumption.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("gemini_engine")

from omnichannel_powerhouse.smart_niche_router import route_video_to_channels
from omnichannel_powerhouse.quota_balancer import check_and_allocate_upload_slot
from omnichannel_powerhouse.gemini_key_rotator import KEY_RING

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini_api_key.local")


def get_gemini_api_key() -> str:
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE, "r", encoding="utf-8").read().strip()
    return os.environ.get("GEMINI_API_KEY", "")


def call_gemini(prompt: str, model: str = "gemini-3.5-flash", max_retries: int = 5) -> str:
    clean_model = model.replace("models/", "")
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "maxOutputTokens": 8192
        }
    }
    req_data = json.dumps(payload).encode("utf-8")

    last_err = None
    for attempt in range(max_retries):
        try:
            key = KEY_RING.get_next_key()
        except Exception:
            key = get_gemini_api_key()

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={key}"
        try:
            req = urllib.request.Request(
                url, data=req_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=90) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            last_err = e
            logger.warning(f"Gemini API attempt {attempt+1} on key [{key[:6]}...] failed: {e}")
            try:
                KEY_RING.record_error(key)
            except Exception:
                pass
            time.sleep(1.0)

    raise RuntimeError(f"Gemini API call failed after {max_retries} attempts across Key-Ring: {last_err}")


def generate_documentary_package(topic: str, niche: str = "tech", target_words: int = 2500) -> Dict[str, Any]:
    """
    Generates a full institutional documentary package with:
    - Title
    - 6-beat narrative script (~target_words)
    - 3-word punchline for thumbnail
    - 12+ B-roll video search terms
    - Full chapter timestamps and description
    - 15+ SEO tags
    """
    logger.info(f"✨ Generating institutional documentary package for: {topic} ({niche})...")

    prompt = f"""You are an elite institutional documentary scriptwriter and algorithmic SEO strategist for high-retention YouTube & Rumble channels.
Target Niche: {niche.upper()}
Topic: {topic}

Generate a complete production JSON package for a 15-20 minute deep research documentary.

Strict Structure Requirements:
1. "title": A viral, curiosity-inducing, authoritative 60-character title (e.g. "The Silicon Monopoly: Inside Nvidia's $3T Compute War").
2. "video_subject": One concise technical subject summary.
3. "thumbnail_punchline": A high-impact 2-to-3 word capitalized punchline for the thumbnail (e.g. "THE CHIP TRAP", "WHALES HID THIS", "THE SECRET CODE").
4. "video_terms": A list of exactly 15 concrete, visual stock-footage search keywords (e.g. "supercomputer glowing", "cleanroom silicon wafer", "fiber optic laser", "server racks flashing").
5. "tags": A list of 15 high-volume algorithmic SEO tags.
6. "description": A captivating YouTube description including exact timestamps formatted as:
   00:00 - Chapter 1: The Hidden Paradigm
   03:15 - Chapter 2: The Mathematical Architecture
   07:20 - Chapter 3: Silicon & Hardware Execution
   11:30 - Chapter 4: Production Benchmarks & Stress Tests
   15:45 - Chapter 5: Geopolitical & Economic Warfare
   18:30 - Chapter 6: The Autonomous Horizon
7. "video_script": An exhaustive, institutional documentary voiceover script (~{target_words} words).
   - Write in an authoritative, cinematic, dramatic documentary tone (similar to Bloomberg Originals or Veritasium).
   - Break into 6 distinct narrative beats:
     Beat 1: Hook and the historical breakdown of old paradigms.
     Beat 2: Formal mathematical derivations, equations, and high-dimensional geometry explained with granular precision.
     Beat 3: Physical silicon hardware, low-level micro-architecture, SRAM cache line alignment, and thermodynamics.
     Beat 4: Real-world benchmark telemetry, empirical error safeguards, and stress tests.
     Beat 5: Geopolitical warfare, corporate extinction events, and trillion-dollar stakes.
     Beat 6: The autonomous future horizon and compelling call to subscribe.
   - Do NOT include scene directions or bracketed markers like [Music swells] or [Visual of chip]. ONLY spoken narrator speech.

Return STRICTLY valid JSON with no markdown backticks, no markdown code block fencing, and no preamble:
{{
  "title": "...",
  "video_subject": "...",
  "thumbnail_punchline": "...",
  "video_terms": ["term1", "term2", ...],
  "tags": ["tag1", "tag2", ...],
  "description": "...",
  "video_script": "..."
}}
"""

    raw_response = call_gemini(prompt)
    clean_text = raw_response.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError:
        # Fallback repair
        logger.warning("Attempting JSON extraction fallback...")
        s_idx = clean_text.find("{")
        e_idx = clean_text.rfind("}")
        if s_idx != -1 and e_idx != -1:
            data = json.loads(clean_text[s_idx:e_idx+1])
        else:
            raise ValueError(f"Failed to parse Gemini output as JSON: {clean_text[:200]}")

    # Autonomous Channel & Quota Decision Engine
    title = data.get("title", topic)
    subject = data.get("video_subject", topic)
    route = route_video_to_channels(title=title, subject=subject, extra_tags=data.get("tags", []))

    target_yt = route.get("primary_channel", "ai_and_tech")
    target_rumble = route.get("rumble_channel", "rumble_trading")
    slot = check_and_allocate_upload_slot(target_yt)

    data["assigned_youtube_channel"] = target_yt
    data["assigned_rumble_channel"] = target_rumble
    data["scheduled_slot"] = slot.get("recommended_action", "upload_unlisted")
    data["scheduled_time"] = slot.get("scheduled_timestamp", "")
    data["routing_affinity_score"] = route.get("primary_score", 1.0)
    data["routing_reasoning"] = f"Semantic match to '{target_yt}' (Score: {route.get('primary_score', 1.0):.2f}). Daily upload status: {slot.get('reason')}."

    data["niche"] = niche
    data["language"] = "hi" if ("hindi" in topic.lower() or "hindi" in niche.lower()) else "en"
    logger.success(f"✅ Generated master documentary: '{data.get('title')}' -> Routed to YT: [{target_yt}] | Rumble: [{target_rumble}]")
    return data


def create_dynamic_20_series_with_gemini(master_theme: str = "Frontier AI & High-Frequency Quantitative Trading") -> Dict[str, Any]:
    """
    Uses Gemini to plan and write all 20 episodes dynamically, then saves to series_tasks.json.
    """
    logger.info(f"🌟 Creating 20-Episode Master Series with Gemini for theme: {master_theme}...")
    
    plan_prompt = f"""Generate a master curriculum of 20 deep institutional documentary episode titles and core topics for the theme: "{master_theme}".
10 episodes MUST be TECH/AI (niche: "tech"), and 10 episodes MUST be QUANTITATIVE FINANCE/MARKET MICROSTRUCTURE (niche: "finance").

Return STRICTLY valid JSON:
[
  {{"episode_number": 1, "title": "...", "subject": "...", "niche": "tech"}},
  ...
  {{"episode_number": 20, "title": "...", "subject": "...", "niche": "finance"}}
]
"""
    raw_plan = call_gemini(plan_prompt)
    clean_plan = raw_plan.strip()
    if clean_plan.startswith("```json"): clean_plan = clean_plan[7:]
    if clean_plan.startswith("```"): clean_plan = clean_plan[3:]
    if clean_plan.endswith("```"): clean_plan = clean_plan[:-3]
    clean_plan = clean_plan.strip()

    plan_items = json.loads(clean_plan)
    tasks = []

    for item in plan_items:
        ep_num = item["episode_number"]
        title = item["title"]
        subject = item["subject"]
        niche = item["niche"]

        logger.info(f"Writing Episode {ep_num}/20 via Gemini: {title}...")
        pkg = generate_documentary_package(topic=f"{title}: {subject}", niche=niche, target_words=2200)
        
        task = {
            "episode_number": ep_num,
            "title": pkg["title"],
            "video_subject": pkg["video_subject"],
            "video_script": pkg["video_script"],
            "video_terms": pkg["video_terms"],
            "tags": pkg["tags"],
            "description": pkg["description"],
            "thumbnail_punchline": pkg["thumbnail_punchline"],
            "niche": niche,
            "language": "en"
        }
        tasks.append(task)
        time.sleep(2) # Respect RPM limits safely

    manifest = {
        "series_title": f"Gemini Supreme Series: {master_theme}",
        "total_episodes": len(tasks),
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tasks": tasks
    }

    out_file = os.path.join(_root, "series_tasks.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.success(f"🎉 Successfully wrote and saved all 20 episodes to {out_file} using Gemini Flash Free!")
    return manifest


if __name__ == "__main__":
    test_pkg = generate_documentary_package("The TSMC 2nm Monopoly: High-NA EUV and A16 GAAFET Physics", niche="tech", target_words=1000)
    print("SUCCESS! Title:", test_pkg["title"])
    print("Thumbnail Punchline:", test_pkg["thumbnail_punchline"])
    print("Words in script:", len(test_pkg["video_script"].split()))
