"""
OmniChannel Ultra-Voice Router (1000x Audio Engine)
Supports:
1. Google Gemini Flash Native Multimodal Audio (gemini-2.5-flash-preview-tts) - 100% Free, Studio 24kHz PCM
2. Automated Chunking & Key-Ring Rotation for Long-Form (20+ Minute) Documentaries
3. Edge-TTS Automatic Resilient Fallback (hi-IN-MadhurNeural, en-US-ChristopherNeural)
4. Shure SM7B Broadcast DSP Vocal Chain (80Hz Highpass + 250Hz Chest Warmth + 3.5kHz Presence + DynAudNorm)
"""

import os
import sys
import json
import time
import base64
import asyncio
import subprocess
import urllib.request
import urllib.error
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
    logger = logging.getLogger("voice_router")

from omnichannel_powerhouse.gemini_key_rotator import KEY_RING

VOICE_PERSONAS = {
    "cinematic_narrator": {
        "gemini_voice": "Fenrir",
        "edge_hindi": "hi-IN-MadhurNeural",
        "edge_english": "en-US-ChristopherNeural",
        "desc": "Deep, resonant, authoritative documentary narrator"
    },
    "conversational_tech": {
        "gemini_voice": "Puck",
        "edge_hindi": "hi-IN-MadhurNeural",
        "edge_english": "en-US-GuyNeural",
        "desc": "Dynamic, high-energy modern tech podcast host"
    },
    "authoritative_female": {
        "gemini_voice": "Kore",
        "edge_hindi": "hi-IN-SwaraNeural",
        "edge_english": "en-US-AriaNeural",
        "desc": "Clear, articulate, professional female broadcaster"
    },
    "warm_educational": {
        "gemini_voice": "Aoede",
        "edge_hindi": "hi-IN-SwaraNeural",
        "edge_english": "en-US-JennyNeural",
        "desc": "Warm, engaging, educational explainer guide"
    }
}


def chunk_text_for_tts(text: str, max_chars: int = 600) -> List[str]:
    """Splits text cleanly along paragraphs or sentence ends to ensure natural speech flow."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    chunks = []
    current_chunk = ""

    for p in paragraphs:
        # If paragraph itself is too large, split by sentences
        if len(p) > max_chars:
            sentences = []
            cur_s = ""
            for ch in p:
                cur_s += ch
                if ch in [".", "।", "!", "?"]:
                    sentences.append(cur_s.strip())
                    cur_s = ""
            if cur_s.strip():
                sentences.append(cur_s.strip())

            for s in sentences:
                if len(current_chunk) + len(s) + 1 <= max_chars:
                    current_chunk += (" " if current_chunk else "") + s
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = s
        else:
            if len(current_chunk) + len(p) + 2 <= max_chars:
                current_chunk += ("\n\n" if current_chunk else "") + p
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = p

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def call_gemini_tts_api(text: str, voice_name: str = "Fenrir", timeout: int = 30) -> bytes:
    """Calls Gemini Flash Preview TTS REST API and returns raw 24kHz linear 16-bit PCM bytes."""
    api_key = KEY_RING.get_next_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            }
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=timeout) as response:
        res = json.loads(response.read().decode("utf-8"))
        candidates = res.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"Gemini TTS returned no candidates: {res}")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError(f"Gemini TTS returned no parts: {res}")
        
        inline_data = parts[0].get("inlineData", {})
        raw_b64 = inline_data.get("data", "")
        if not raw_b64:
            raise RuntimeError("Gemini TTS response missing inlineData audio bytes")
        
        return base64.b64decode(raw_b64)


async def synthesize_edge_tts_fallback(text: str, voice: str, out_path: str):
    """Fallback Edge-TTS synthesizer if cloud API is unreachable."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice=voice, rate="+3%")
    await communicate.save(out_path)


def synthesize_ultra_voice(
    text: str,
    out_path: str,
    persona: str = "cinematic_narrator",
    lang: str = "hi",
    preferred_engine: str = "gemini"
) -> str:
    """
    Main entry point for 1000x voice synthesis:
    1. Chunks long texts safely.
    2. Synthesizes via Gemini 2.5 Flash Multimodal Audio (24kHz studio PCM).
    3. Seamlessly falls back to Edge-TTS if needed.
    4. Applies broadcast DSP vocal chain mastering.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(out_path)), "temp_voice_chunks")
    os.makedirs(temp_dir, exist_ok=True)

    persona_cfg = VOICE_PERSONAS.get(persona, VOICE_PERSONAS["cinematic_narrator"])
    gemini_voice = persona_cfg["gemini_voice"]
    edge_voice = persona_cfg["edge_hindi"] if lang.lower().startswith("hi") else persona_cfg["edge_english"]

    chunks = chunk_text_for_tts(text, max_chars=550)
    logger.info(f"🎙️ Synthesizing voice across {len(chunks)} text chunks (Persona: {persona} / {gemini_voice})...")

    raw_pcm_files = []
    engine_used = "gemini"

    if preferred_engine == "gemini":
        try:
            for idx, chunk in enumerate(chunks):
                chunk_pcm_path = os.path.join(temp_dir, f"chunk_{idx:03d}.raw")
                logger.info(f"   [Chunk {idx+1}/{len(chunks)}] Gemini TTS synthesis ({len(chunk)} chars)...")
                pcm_bytes = call_gemini_tts_api(chunk, voice_name=gemini_voice)
                with open(chunk_pcm_path, "wb") as f:
                    f.write(pcm_bytes)
                raw_pcm_files.append(chunk_pcm_path)
        except Exception as e:
            logger.warning(f"⚠️ Gemini TTS encountered an issue: {e}. Falling back to Edge-TTS resilient engine.")
            engine_used = "edge_tts"
            raw_pcm_files = []

    if engine_used == "edge_tts" or not raw_pcm_files:
        logger.info(f"🎙️ Using Resilient Edge-TTS fallback voice: {edge_voice}...")
        edge_raw_path = os.path.join(temp_dir, "edge_raw_combined.mp3")
        try:
            asyncio.run(synthesize_edge_tts_fallback(text, edge_voice, edge_raw_path))
            raw_input = edge_raw_path
            input_args = ["-i", raw_input]
        except Exception as err:
            logger.error(f"Both Gemini and Edge-TTS failed: {err}")
            raise
    else:
        # Concatenate raw 24kHz PCM chunks
        combined_pcm_path = os.path.join(temp_dir, "combined_24k.raw")
        with open(combined_pcm_path, "wb") as outfile:
            for pcm_f in raw_pcm_files:
                with open(pcm_f, "rb") as infile:
                    outfile.write(infile.read())
                try:
                    os.remove(pcm_f)
                except OSError:
                    pass
        raw_input = combined_pcm_path
        input_args = ["-f", "s16le", "-ar", "24000", "-ac", "1", "-i", raw_input]

    # Master with Studio DSP Broadcast Vocal Chain
    logger.info("🎛️ Applying Broadcast DSP Mastering Chain (80Hz Highpass + 250Hz Warmth + 3.5kHz Air + DynAudNorm)...")
    vocal_chain = (
        "highpass=f=80,"
        "equalizer=f=250:t=q:w=1.2:g=2.0,"
        "equalizer=f=3500:t=q:w=1.2:g=2.5,"
        "dynaudnorm=p=0.95:m=10:s=12"
    )

    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-af", vocal_chain,
        "-c:a", "libmp3lame" if out_path.endswith(".mp3") else "aac",
        "-b:a", "192k",
        "-ar", "48000",
        out_path
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Clean up temp files
    try:
        if os.path.exists(raw_input):
            os.remove(raw_input)
    except OSError:
        pass

    logger.success(f"✅ Studio-Grade Mastered Voiceover ready: {out_path} (Engine: {engine_used.upper()})")
    return out_path
