"""
Smart Niche Router: Semantic Topic-to-Channel Mapping Engine
Evaluates video metadata (title, subject, keywords) and matches it to the optimal
channel in channels_registry.json using normalized keyword affinity and negative filtering.
Operates with 0 AI API tokens and microsecond execution speed.
"""

import os
import sys
import json
import re
from typing import Dict, Any, List, Tuple

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("smart_niche_router")

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "channels_registry.json")


def load_registry() -> Dict[str, Any]:
    if not os.path.exists(REGISTRY_PATH):
        return {"channels": {}}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(data: Dict[str, Any]):
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def calculate_niche_affinity(text: str, keywords: List[str], negative_keywords: List[str]) -> float:
    """
    Computes normalized affinity score [0.0 to 1.0] for a channel against given text.
    """
    clean_text = text.lower()
    
    # 1. Negative keyword penalty
    for neg in negative_keywords:
        if re.search(rf"\b{re.escape(neg.lower())}\b", clean_text):
            return 0.0  # Immediate disqualify if negative keyword matches strongly

    if not keywords:
        return 0.1

    if "all" in keywords:
        return 0.5  # Catch-all general channel

    # 2. Positive keyword scoring
    matches = 0
    weight = 0.0
    for kw in keywords:
        kw_clean = kw.lower()
        if re.search(rf"\b{re.escape(kw_clean)}\b", clean_text):
            matches += 1
            # Multi-word keywords get higher weight
            weight += 1.5 if " " in kw_clean else 1.0

    if matches == 0:
        return 0.0

    score = min(1.0, weight / (len(keywords) * 0.4 + 1.0))
    return score


def route_video_to_channels(title: str, subject: str = "", extra_tags: List[str] = None) -> Dict[str, Any]:
    """
    Determines the best primary YouTube channel and matching Rumble channels for a video.
    """
    registry = load_registry()
    channels = registry.get("channels", {})
    if not channels:
        logger.warning("No channels found in channels_registry.json!")
        return {"primary_channel": None, "secondary_channels": []}

    combined_text = f"{title} {subject} {' '.join(extra_tags or [])}".lower()

    scored_yt: List[Tuple[str, float, Dict[str, Any]]] = []
    scored_rumble: List[Tuple[str, float, Dict[str, Any]]] = []

    for c_key, c_data in channels.items():
        if c_data.get("auth_status") not in ("authenticated", "configured"):
            continue

        kw = c_data.get("keywords", [])
        neg_kw = c_data.get("negative_keywords", [])
        score = calculate_niche_affinity(combined_text, kw, neg_kw)

        platform = c_data.get("platform", "youtube").lower()
        if platform == "youtube":
            scored_yt.append((c_key, score, c_data))
        elif platform == "rumble":
            scored_rumble.append((c_key, score, c_data))

    # Sort descending by score
    scored_yt.sort(key=lambda x: x[1], reverse=True)
    scored_rumble.sort(key=lambda x: x[1], reverse=True)

    primary_channel = scored_yt[0][0] if scored_yt and scored_yt[0][1] > 0.0 else (scored_yt[0][0] if scored_yt else None)
    secondary_rumble = scored_rumble[0][0] if scored_rumble else None

    logger.info(f"🎯 Routed '{title[:40]}...' -> Primary YT: [{primary_channel}] (Score: {scored_yt[0][1] if scored_yt else 0:.2f})")

    return {
        "title": title,
        "primary_channel": primary_channel,
        "primary_channel_info": channels.get(primary_channel, {}),
        "primary_score": scored_yt[0][1] if scored_yt else 0.0,
        "rumble_channel": secondary_rumble,
        "all_yt_ranked": [(k, s) for k, s, _ in scored_yt]
    }


if __name__ == "__main__":
    test_title_1 = "The Silicon Monopoly: Nvidia B200 Blackwell & The AI Compute War"
    test_title_2 = "The Wall Street Dark Pool Trap: How Institutional Whales Trade Billions in Secret"

    print("Test 1 Result:", json.dumps(route_video_to_channels(test_title_1), indent=2))
    print("Test 2 Result:", json.dumps(route_video_to_channels(test_title_2), indent=2))
