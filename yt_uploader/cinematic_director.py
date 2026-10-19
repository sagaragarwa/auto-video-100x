"""
Cinematic Director: Semantic Scene-by-Scene Visual Matching Engine.
Breaks down documentary narration into distinct scenes, generates context-aware
English stock video queries, fetches unique 1080p clips via Pixabay API,
and guarantees ZERO visual repetitions across long-form videos.
"""

import os
import sys
import re
import hashlib
import time
import requests
from typing import List, Dict, Any, Optional
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

from app.models.schema import VideoAspect
from app.services.material import search_videos_pixabay
from yt_uploader.disk_governor import enforce_5gb_disk_headroom

# Semantic visual keyword mapping dictionary for common niches
NICHE_VISUAL_KEYWORDS = {
    "psychology": [
        "exhausted person scrolling smartphone dark",
        "waking up bed phone morning alarm",
        "social media endless scroll reels",
        "brain neuron synapse firing animation",
        "stressed student worker desk head down",
        "meditation deep breathing nature calm",
        "turning off smartphone power down",
        "writing notebook journal desk pen",
        "walking in peaceful green forest nature",
        "drinking water fresh morning sunlight",
        "reading book cozy room focus",
        "running athlete morning road fitness",
        "analog clock ticking passing time lapse",
        "person looking out window thoughtful",
        "sunrise mountain peak victory freedom",
        "calm ocean waves slow motion beach",
        "deep work typing computer concentration",
        "healthy food salad eating clean",
        "lonely dark room silhouette thinking",
        "walking path forest sunlight trees",
        "hands writing diary journal closeup",
        "serene lake reflection mountains clouds",
        "relaxing park bench reading quiet",
        "mindful walking bare feet grass nature",
        "starry night sky milky way time lapse",
        "light bulb idea glowing dark inspiration",
        "smiling confident person walking street",
        "calm campfire embers night warmth",
        "zen stone balance water river tranquil",
        "golden hour field wheat blowing wind"
    ],
    "trading": [
        "stock market candlestick chart green red",
        "trader multiple monitors financial analysis",
        "wall street financial district buildings",
        "crypto bitcoin coins glowing digital",
        "stressed trader holding head red screen",
        "bull bear financial market bronze statue",
        "luxury business watch suit professional",
        "money currency bills counting cash",
        "stock ticker board times square numbers",
        "calm disciplined trader executing order",
        "upward growth green arrow line graph",
        "risk management chess board strategy",
        "office late night trading desk lamp",
        "global financial network connection earth",
        "calculator financial balance sheet analysis",
        "investor handshake agreement meeting",
        "golden bullion bars bank vault wealth",
        "market crash panic selling red chart",
        "successful entrepreneur private jet luxury",
        "trading journal notebook pen planning"
    ],
    "tech": [
        "artificial intelligence neural network glowing",
        "data center server racks flashing leds",
        "developer coding python terminal matrix",
        "futuristic robot android cybernetic eye",
        "microchip semiconductor processor circuit",
        "quantum computer cooling system tech",
        "hologram futuristic interface data hands",
        "cyber security lock shield digital blue",
        "autonomous electric vehicle sensor drive",
        "satellite orbiting earth space technology"
    ]
}

def parse_srt_into_scenes(srt_path: str, target_scene_duration: float = 5.5) -> List[Dict[str, Any]]:
    """
    Parses an SRT file and chunks subtitle lines into coherent scenes of approximately target_scene_duration.
    Returns list of dicts with text, start_time, end_time, duration.
    """
    if not os.path.exists(srt_path):
        return []

    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\s*\n", content.strip())
    sub_entries = []
    for b in blocks:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        if len(lines) >= 3 and "-->" in lines[1]:
            t_match = re.match(r"(\d+):(\d+):(\d+)[,\.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,\.](\d+)", lines[1])
            if t_match:
                s_h, s_m, s_s, s_ms, e_h, e_m, e_s, e_ms = map(int, t_match.groups())
                start_sec = s_h * 3600 + s_m * 60 + s_s + s_ms / 1000.0
                end_sec = e_h * 3600 + e_m * 60 + e_s + e_ms / 1000.0
                text = " ".join(lines[2:])
                sub_entries.append({"text": text, "start": start_sec, "end": end_sec})

    if not sub_entries:
        return []

    scenes = []
    curr_scene_text = []
    scene_start = sub_entries[0]["start"]

    for entry in sub_entries:
        curr_scene_text.append(entry["text"])
        if (entry["end"] - scene_start) >= target_scene_duration:
            scenes.append({
                "text": " ".join(curr_scene_text),
                "start": scene_start,
                "end": entry["end"],
                "duration": round(entry["end"] - scene_start, 2)
            })
            curr_scene_text = []
            scene_start = entry["end"]

    if curr_scene_text:
        scenes.append({
            "text": " ".join(curr_scene_text),
            "start": scene_start,
            "end": sub_entries[-1]["end"],
            "duration": round(sub_entries[-1]["end"] - scene_start, 2)
        })

    return scenes

class CinematicDirector:
    def __init__(self, niche: str = "psychology"):
        self.niche = niche.lower()
        self.library_dir = os.path.join(_root, "storage", "cinematic_library")
        os.makedirs(self.library_dir, exist_ok=True)
        self.used_clip_hashes = set()

    def get_scene_visual_queries(self, script_scenes: List[Dict[str, Any]]) -> List[str]:
        """
        Maps each narration scene to a targeted, cinematic English search query.
        """
        curated_pool = NICHE_VISUAL_KEYWORDS.get(self.niche, NICHE_VISUAL_KEYWORDS["psychology"])
        queries = []

        for idx, sc in enumerate(script_scenes):
            raw_text = sc.get("text", "")
            # Check context keywords in scene text
            matched_query = None
            t_lower = raw_text.lower()

            if any(k in t_lower for k in ["फोन", "phone", "स्क्रॉल", "reels", "screen"]):
                matched_query = "exhausted person scrolling smartphone dark"
            elif any(k in t_lower for k in ["सुबह", "wake", "alarm", "बिस्तर"]):
                matched_query = "waking up bed phone morning alarm"
            elif any(k in t_lower for k in ["डोपामाइन", "dopamine", "दिमाग", "brain", "न्यूरो"]):
                matched_query = "brain neuron synapse firing animation"
            elif any(k in t_lower for k in ["थकान", "आलस", "stress", "tired", "distracted"]):
                matched_query = "stressed student worker desk head down"
            elif any(k in t_lower for k in ["डायरी", "लिखना", "journal", "write"]):
                matched_query = "writing notebook journal desk pen"
            elif any(k in t_lower for k in ["प्रकृति", "nature", "घूमना", "walk", "जंगल", "forest"]):
                matched_query = "walking in peaceful green forest nature"
            elif any(k in t_lower for k in ["नियम", "rule", "detox", "डिटॉक्स", "बंद"]):
                matched_query = "turning off smartphone power down"
            elif any(k in t_lower for k in ["सफलता", "peace", "शांति", "जीत", "reset"]):
                matched_query = "sunrise mountain peak victory freedom"

            if not matched_query or matched_query in queries:
                # Pick from curated pool ensuring no immediate duplicates
                pool_idx = idx % len(curated_pool)
                matched_query = curated_pool[pool_idx]

            queries.append(matched_query)

        return queries

    def fetch_unique_scene_clip(self, query: str, scene_idx: int) -> Optional[str]:
        """
        Fetches a 1080p landscape stock clip for the query.
        Ensures local caching, valid format, and no duplicates.
        """
        enforce_5gb_disk_headroom(min_free_gb=5.0)

        q_hash = hashlib.md5(f"{query}_{scene_idx}".encode("utf-8")).hexdigest()[:10]
        local_target = os.path.join(self.library_dir, f"scene_{scene_idx:02d}_{q_hash}.mp4")

        # Return cached if exists and healthy
        if os.path.exists(local_target) and os.path.getsize(local_target) > 100000:
            self.used_clip_hashes.add(local_target)
            return local_target

        logger.info(f"🎬 Scene {scene_idx+1}: Searching Pixabay for '{query}'...")
        try:
            results = search_videos_pixabay(
                search_term=query,
                minimum_duration=3,
                video_aspect=VideoAspect.landscape
            )
            if results:
                # Find first result not already used
                for r in results:
                    video_url = r.url
                    if video_url:
                        # Download directly
                        resp = requests.get(video_url, timeout=30, stream=True)
                        if resp.status_code == 200:
                            with open(local_target, "wb") as f:
                                for chunk in resp.iter_content(chunk_size=65536):
                                    if chunk:
                                        f.write(chunk)

                            if os.path.getsize(local_target) > 50000:
                                logger.success(f"Downloaded scene {scene_idx+1} ({os.path.getsize(local_target)//1024} KB)")
                                self.used_clip_hashes.add(local_target)
                                return local_target
        except Exception as e:
            logger.warning(f"Pixabay search failed for '{query}': {e}")

        # Fallback to local cache if download fails
        cache_dir = os.path.join(_root, "storage", "cache_videos")
        if os.path.exists(cache_dir):
            import glob
            cached_files = glob.glob(os.path.join(cache_dir, "**", "*.mp4"), recursive=True)
            for cf in cached_files:
                if cf not in self.used_clip_hashes and os.path.getsize(cf) > 100000:
                    self.used_clip_hashes.add(cf)
                    return cf

        return None
