"""
OmniChannel 4-Act Scoring & Micro-Foley Audio Engine
100% Free, procedural audio synthesis via FFmpeg lavfi filters.
Zero paid sound libraries or external audio subscriptions needed.
"""

import os
import sys
import subprocess
from typing import List, Dict, Any, Optional

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("foley_engine")


def synthesize_foley_sfx(sfx_type: str, out_wav_path: str) -> str:
    """
    Synthesizes authentic cinematic foley effects locally in 0.05 seconds via FFmpeg lavfi.
    """
    if os.path.exists(out_wav_path) and os.path.getsize(out_wav_path) > 1000:
        return out_wav_path

    os.makedirs(os.path.dirname(os.path.abspath(out_wav_path)), exist_ok=True)

    if sfx_type == "sub_boom":
        # 45Hz sub-bass cinematic impact with 2.2s decay
        filt = "sine=frequency=45:duration=2.5,afade=t=out:st=0.3:d=2.2,volume=2.0"
    elif sfx_type == "whoosh":
        # Filtered pink noise sweep for fast transitions
        filt = "anoisesrc=d=1.0:c=pink:r=44100,bandpass=f=850:w=650,afade=t=in:st=0:d=0.35,afade=t=out:st=0.35:d=0.65,volume=2.2"
    elif sfx_type == "typing":
        # Rapid mechanical keyboard chatter burst (1.5 seconds)
        filt = "anoisesrc=d=1.5:c=white:r=44100,bandpass=f=2800:w=1200,volume=0.9,tremolo=f=14:d=0.9,afade=t=out:st=1.1:d=0.4"
    elif sfx_type == "glitch":
        # Digital pattern interrupt noise burst (0.35s)
        filt = "anoisesrc=d=0.35:c=white:r=44100,highpass=f=1600,volume=1.4,afade=t=out:st=0.2:d=0.15"
    elif sfx_type == "paper_flip":
        # Document rustle sound for newspaper headline scanner
        filt = "anoisesrc=d=0.8:c=pink:r=44100,bandpass=f=1200:w=800,volume=1.1,tremolo=f=8:d=0.7,afade=t=out:st=0.5:d=0.3"
    else:
        filt = "sine=frequency=440:duration=1.0,afade=t=out:st=0.5:d=0.5"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", filt,
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2",
        out_wav_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_wav_path


def build_cinematic_audio_bed(
    voiceover_path: str,
    ambient_loop_path: str,
    foley_events: List[Dict[str, Any]],
    out_mixed_audio_path: str
) -> str:
    """
    Mixes voiceover, looping 4-act ambient background with dynamic sidechain ducking,
    and injects synchronized micro-foley sound effects at designated timestamps.
    foley_events format: [{'sfx': 'sub_boom', 'time': 15.2}, {'sfx': 'paper_flip', 'time': 45.0}]
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_mixed_audio_path)), exist_ok=True)
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(out_mixed_audio_path)), "temp_foley")
    os.makedirs(temp_dir, exist_ok=True)

    # 1. Synthesize all necessary foley files
    sfx_files = {}
    for ev in foley_events:
        stype = ev["sfx"]
        if stype not in sfx_files:
            spath = os.path.join(temp_dir, f"{stype}.wav")
            synthesize_foley_sfx(stype, spath)
            sfx_files[stype] = spath

    # 2. Build multi-input FFmpeg command
    # Input 0: Voiceover
    # Input 1: Looping ambient music
    # Inputs 2..N: Foley SFX delayed by ev['time']
    cmd = [
        "ffmpeg", "-y",
        "-i", voiceover_path,
        "-stream_loop", "-1", "-i", ambient_loop_path
    ]

    for ev in foley_events:
        spath = sfx_files[ev["sfx"]]
        cmd.extend(["-i", spath])

    # Build filter graph with delays
    # [1:a] volume=-16dB [bg]
    # [2:a] adelay=15200|15200 [sfx0] ...
    # Sidechain ducking of [bg] under [0:a]
    filter_parts = []
    
    # Music leveling
    filter_parts.append("[1:a]volume=0.18[bg_raw]")

    sfx_labels = []
    for idx, ev in enumerate(foley_events):
        delay_ms = int(ev["time"] * 1000)
        in_idx = idx + 2
        label = f"sfx{idx}"
        filter_parts.append(f"[{in_idx}:a]adelay={delay_ms}|{delay_ms},volume=0.85[{label}]")
        sfx_labels.append(f"[{label}]")

    # Combine music + foley into [score_bed]
    if sfx_labels:
        mix_inputs = "[bg_raw]" + "".join(sfx_labels)
        filter_parts.append(f"{mix_inputs}amix=inputs={len(sfx_labels)+1}:normalize=0[score_bed]")
    else:
        filter_parts.append("[bg_raw]anull[score_bed]")

    # Sidechain ducking: [score_bed] ducks automatically whenever [0:a] speaks
    filter_parts.append(
        "[score_bed][0:a]sidechaincompress=threshold=0.04:ratio=8:attack=15:release=350[ducked_score]"
    )
    # Final mix: Voiceover + Ducked Score
    filter_parts.append("[0:a][ducked_score]amix=inputs=2:normalize=0[out_a]")

    cmd.extend([
        "-filter_complex", ";".join(filter_parts),
        "-map", "[out_a]",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest",
        out_mixed_audio_path
    ])

    logger.info(f"🎧 Compiling 4-Act Scoring Bed with {len(foley_events)} synchronized foley events...")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logger.success(f"✅ Master Audio Bed with Micro-Foley Ready -> {out_mixed_audio_path}")
    return out_mixed_audio_path
