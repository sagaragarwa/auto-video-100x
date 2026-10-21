"""
5X Audio Director: Edge-TTS Narration, Seamless BGM Looping & Dynamic Sidechain Ducking.
Ensures studio-grade voice clarity, zero jarring music loop cuts, and professional
audio ducking where BGM naturally breathes around voice pauses.
"""

import os
import sys
import glob
import subprocess
import time
import random
from typing import Dict, Any, Optional, Tuple
from loguru import logger

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

def select_cinematic_bgm(niche: str = "psychology", duration_needed: float = 300.0) -> str:
    """
    Selects the best matching cinematic background music track from resource/songs.
    Randomly chooses among valid tracks for the niche so each video has a distinct atmosphere.
    """
    songs_dir = os.path.join(_root, "resource", "songs")
    all_songs = sorted(glob.glob(os.path.join(songs_dir, "*.mp3")))
    if not all_songs:
        raise FileNotFoundError(f"No BGM tracks found in {songs_dir}")

    # Map niche to preferred vibe
    niche_map = {
        "psychology": [0, 4, 7, 12, 19, 3, 10],  # Deep, contemplative, ambient
        "trading": [1, 5, 8, 15, 23, 6, 14],     # Fast, tense, rhythmic
        "tech": [2, 6, 9, 14, 21, 11, 18],       # Modern, synth, progressive
        "history": [0, 7, 12, 16, 20],           # Epic, solemn, atmospheric
        "science": [2, 4, 9, 13, 17]             # Ambient, curiosity, floating
    }
    preferred = niche_map.get(niche.lower(), [0, 4, 7, 1, 5, 2])
    candidates = []
    for idx in preferred:
        candidate = os.path.join(songs_dir, f"output{idx:03d}.mp3")
        if os.path.exists(candidate):
            candidates.append(candidate)

    if candidates:
        chosen = random.choice(candidates)
        logger.info(f"🎶 Randomly selected thematic BGM ({niche}): {os.path.basename(chosen)}")
        return chosen

    chosen = random.choice(all_songs)
    logger.info(f"🎶 Randomly selected general BGM: {os.path.basename(chosen)}")
    return chosen

def build_dynamic_audio_filter(has_bgm: bool = True) -> str:
    """
    Constructs FFmpeg filter complex for studio dynamic audio ducking and broadcast loudness.
    Input 1: Voiceover (hi-IN / en-US Edge TTS)
    Input 2: Background Music (looped)
    
    Using sidechaincompress + loudnorm:
    - Normalizes voice to standard broadcast loudness (-14 LUFS)
    - Voice acts as the sidechain control signal (input 1)
    - When voice speaks: BGM is suppressed by ~18-20dB
    - When voice pauses: BGM smoothly recovers with attack=15ms, release=400ms
    - Master output is balanced to 48000Hz stereo at YouTube -14 LUFS standard!
    """
    if not has_bgm:
        return "[1:a]volume=1.8,aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-14:LRA=7:TP=-1.5[aout]"

    filter_complex = (
        "[1:a]volume=1.8,aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v_main][v_sc];"
        "[2:a]volume=0.28,aformat=sample_rates=48000:channel_layouts=stereo[bgm_in];"
        "[bgm_in][v_sc]sidechaincompress=threshold=0.08:ratio=10:attack=15:release=450[bgm_ducked];"
        "[v_main][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:LRA=7:TP=-1.5[aout]"
    )
    return filter_complex
