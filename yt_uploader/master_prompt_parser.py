"""
Master Prompt Natural Language Parser for 5X Cinematic Autonomous Video Engine.
Parses natural language prompts like:
  - "5 minute dopamine detox documentary in Hindi, auto upload"
  - "10 minutes trading psychology, upload to channel_trading, fast cuts"
  - "3 min tech artificial intelligence future in english"
"""

import re
from typing import Dict, Any, Optional
from loguru import logger
from yt_uploader.channel_manager import auto_detect_channel, load_channels

def parse_master_prompt(prompt: str) -> Dict[str, Any]:
    """
    Parses a single natural language user prompt into structured engine configuration.
    """
    p_lower = prompt.lower().strip()
    logger.info(f"🧠 Parsing Master Prompt: '{prompt}'")

    # 1. Parse Duration (default: 300s = 5 minutes)
    duration_seconds = 300
    duration_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:min|mins|minute|minutes|m\b)", p_lower)
    if duration_match:
        mins = float(duration_match.group(1))
        duration_seconds = int(mins * 60)
    else:
        sec_match = re.search(r"(\d+)\s*(?:sec|secs|second|seconds|s\b)", p_lower)
        if sec_match:
            duration_seconds = int(sec_match.group(1))

    # Clamp duration to sane boundaries (60s to 1200s = 1 to 20 mins)
    duration_seconds = max(60, min(1200, duration_seconds))

    # 2. Parse Language (default: hindi)
    language = "hi-IN"
    voice_name = "hi-IN-MadhurNeural"
    if "english" in p_lower or "angrezi" in p_lower:
        language = "en-US"
        voice_name = "en-US-ChristopherNeural"
    elif "female" in p_lower or "aurat" in p_lower or "ladki" in p_lower:
        language = "hi-IN"
        voice_name = "hi-IN-SwaraNeural"

    # 3. Parse Channel Target
    channels = load_channels()
    target_channel = "auto"

    # Check explicit channel mention
    for ch_key in channels.keys():
        if ch_key.lower() in p_lower:
            target_channel = ch_key
            break

    if target_channel == "auto":
        # Check by niche keywords
        if "trading" in p_lower or "stock" in p_lower or "finance" in p_lower or "crypto" in p_lower:
            target_channel = "channel_trading" if "channel_trading" in channels else "auto"
        elif "psychology" in p_lower or "mind" in p_lower or "dopamine" in p_lower or "habit" in p_lower:
            target_channel = "channel_psychology" if "channel_psychology" in channels else "auto"
        elif "tech" in p_lower or "ai" in p_lower or "software" in p_lower:
            target_channel = "channel_tech" if "channel_tech" in channels else "auto"
        elif "science" in p_lower or "space" in p_lower or "physics" in p_lower:
            target_channel = "channel_science" if "channel_science" in channels else "auto"

    # 4. Parse Visual Style & Pacing
    visual_style = "cinematic_documentary"
    if "fast" in p_lower or "reels" in p_lower or "high energy" in p_lower:
        visual_style = "high_energy_fast_cut"
    elif "dark" in p_lower or "moody" in p_lower:
        visual_style = "dark_cinematic"

    # 5. Extract Core Subject / Topic
    # Clean duration, channel, and language tokens from prompt
    clean_topic = prompt
    clean_patterns = [
        r"\b\d+\s*(?:min|mins|minute|minutes|sec|secs|second|seconds|m|s)\b",
        r"\b(?:in\s+)?(?:hindi|english|angrezi)\b",
        r"\b(?:documentary|masterclass|fast cuts|cinematic|quality)\b",
        r"\b(?:auto\s+upload(?:\s+to)?|upload(?:\s+to)?|auto)\b",
        r"\b(?:channel_\w+|psychology channel|trading channel|tech channel|science channel)\b",
        r"\b(?:channel|to)\b",
        r"\b(?:banao|generate|create|make)\b",
        r"\b(?:ki\s+)?video\b",
        r"\bvideo\b"
    ]
    for pat in clean_patterns:
        clean_topic = re.sub(pat, " ", clean_topic, flags=re.IGNORECASE)

    clean_topic = re.sub(r"\b(\w+)(?:\s+\1\b)+", r"\1", clean_topic, flags=re.IGNORECASE)
    clean_topic = re.sub(r"[,;:\-_\s]+", " ", clean_topic).strip()
    clean_topic = re.sub(r"\b(?:ki|ka|ke|ko|in|on|of|for|to)\s*$", "", clean_topic, flags=re.IGNORECASE).strip()
    if not clean_topic:
        clean_topic = "Dopamine Detox Mind Reset"

    # 6. Auto-detect channel if still auto
    detected_channel = auto_detect_channel(clean_topic) if target_channel == "auto" else target_channel

    from scripts.chat_video_agent import detect_niche
    detected_niche = detect_niche(prompt)

    # 7. Aspect Ratio
    aspect = "16:9"
    if "vertical" in p_lower or "shorts" in p_lower or "reels" in p_lower or "9:16" in p_lower:
        aspect = "9:16"

    parsed_plan = {
        "raw_prompt": prompt,
        "topic": clean_topic,
        "niche": detected_niche,
        "duration_seconds": duration_seconds,
        "duration_minutes": round(duration_seconds / 60, 2),
        "language": language,
        "voice_name": voice_name,
        "requested_channel": target_channel,
        "resolved_channel": detected_channel,
        "visual_style": visual_style,
        "aspect_ratio": aspect,
        "auto_upload": "upload" in p_lower or "auto" in p_lower
    }

    logger.success(f"Parsed Plan: Topic='{clean_topic}', Dur={duration_seconds}s, Channel={detected_channel}, Lang={language}")
    return parsed_plan
