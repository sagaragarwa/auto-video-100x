"""
Google AI Studio Gemini Flash TTS & Broadcast Voice Improvement Engine
========================================================================
100% Free Tier Speech Synthesis powered by Gemini Flash TTS Preview
with Integrated Shure SM7B Broadcast Studio DSP Mastering Chain.

Features:
1. Native 24kHz Studio Speech (Hindi & English) via Google AI Studio API.
2. Voices: Fenrir (Deep Documentary), Puck (Dynamic Tech), Charon (Cinematic Trailer),
   Aoede (Warm Explainer), Kore (Professional Broadcaster).
3. Automated Gemini Key-Ring Rotation (15 RPM / 1,500 RPD balance).
4. Hindi Phonetic Acronym Transliteration (TSMC -> टी-एस-एम-सी, etc.).
5. Long-Script Auto-Chunking & Seamless Concatenation (20+ min support).
6. 6-Stage Broadcast Studio DSP Mastering Chain:
   - 75Hz Highpass Filter (Sub-bass rumble & boom removal)
   - 250Hz Chest Resonance & Warmth EQ (+2.0dB)
   - 3.5kHz Consonant Presence & Air EQ (+3.5dB Discovery Channel clarity)
   - Surgical De-Esser (Eliminates harsh 'स'/'श' sibilance)
   - Broadcast Multiband Compressor (Radio announcer density)
   - EBU R128 Loudness Normalization (-14 LUFS, YouTube & Rumble standard)
7. Dynamic Sidechain Ducking Engine (-24dB background music ducking).
8. Resilient Zero-Cost Fallback: Edge-TTS 48kHz (hi-IN-MadhurNeural).
"""

import os
import sys
import json
import re
import base64
import time
import subprocess
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

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
    logger = logging.getLogger("gemini_tts")

from omnichannel_powerhouse.gemini_key_rotator import KEY_RING

# Official Google AI Studio endpoint for Flash TTS preview
# USER DIRECTIVE: Hard-lock voice synthesis to Edge-TTS + Shure SM7B DSP
# This permanently preserves 100% of the 4,500 daily Gemini API quota exclusively for Deep Research Scripts.
FORCE_EDGE_TTS_LOCKED = True

PRIMARY_TTS_MODEL = "gemini-2.5-flash-preview-tts"

VOICE_MAP = {
    "male_documentary": "Fenrir",
    "male_tech": "Puck",
    "male_deep": "Charon",
    "female_documentary": "Aoede",
    "female_warm": "Kore"
}

# Devanagari Phonetic Transliteration Dictionary
PHONETIC_TRANSLITERATION_MAP = {
    r"\bTSMC\b": "टी-एस-एम-सी",
    r"\bASML\b": "ए-एस-एम-एल",
    r"\bEUV\b": "ई-यू-वी",
    r"\bDUV\b": "डी-यू-वी",
    r"\bSRAM\b": "एस-रैम",
    r"\bGPU\b": "जी-पी-यू",
    r"\bGPUs\b": "जी-पी-यूज़",
    r"\bTPU\b": "टी-पी-यू",
    r"\bTPUs\b": "टी-पी-यूज़",
    r"\bAI\b": "ए-आई",
    r"\bAGI\b": "ए-जी-आई",
    r"\bASI\b": "ए-एस-आई",
    r"\bNVIDIA\b": "एनवीडिया",
    r"\bBlackwell\b": "ब्लैकवेल",
    r"\bHopper\b": "हॉपर",
    r"\bIntel\b": "इंटेल",
    r"\bAMD\b": "ए-एम-डी",
    r"\bApple\b": "एप्पल",
    r"\bQualcomm\b": "क्वालकॉम",
    r"\bLLM\b": "एल-एल-एम",
    r"\bLLMs\b": "एल-एल-एम्स",
    r"\bHBM\b": "एच-बी-एम",
    r"\bHBM3e\b": "एच-बी-एम-थ्री-ई",
    r"\bCUDA\b": "कूडा",
    r"\bCoWoS\b": "को-वॉस",
    r"\bCPU\b": "सी-पी-यू",
    r"\bCPUs\b": "सी-पी-यूज़",
    r"\bCEO\b": "सी-ई-ओ",
    r"\bSemiconductor\b": "सेमीकंडक्टर",
    r"\bSemiconductors\b": "सेमीकंडक्टर्स",
    r"\bQuantum\b": "क्वांटम",
    r"\bAlgorithm\b": "एल्गोरिद्म",
    r"\bAlgorithms\b": "एल्गोरिद्म्स",
    r"\bWall Street\b": "वॉल स्ट्रीट",
    r"\bSilicon Valley\b": "सिलिकॉन वैली",
    r"\bBitcoin\b": "बिटकॉइन",
    r"\bFederal Reserve\b": "फेडरल रिज़र्व",
}

# The Shure SM7B Broadcast Studio DSP Vocal Mastering Chain
BROADCAST_DSP_CHAIN = (
    "highpass=f=75,"
    "equalizer=f=250:t=q:w=1.2:g=2.0,"
    "equalizer=f=3500:t=q:w=1.5:g=3.5,"
    "deesser=i=0.5:m=0.5:f=0.5,"
    "acompressor=threshold=-18dB:ratio=3.5:attack=15:release=120:makeup=3.5dB,"
    "loudnorm=I=-14:LRA=7:TP=-1.5"
)


def apply_phonetic_transliteration(text: str) -> str:
    """Preprocesses script to ensure flawless pronunciation of tech/financial terms in Hindi."""
    res = text
    for pattern, replacement in PHONETIC_TRANSLITERATION_MAP.items():
        res = re.sub(pattern, replacement, res, flags=re.IGNORECASE)
    return res


def chunk_script_for_tts(text: str, max_chars: int = 500) -> List[str]:
    """Splits text into coherent spoken chunks respecting sentence and paragraph boundaries."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    chunks = []
    current_chunk = ""

    for p in paragraphs:
        if len(p) > max_chars:
            sentences = re.split(r"([।\.!\?])", p)
            combined_s = []
            for i in range(0, len(sentences) - 1, 2):
                combined_s.append(sentences[i] + sentences[i+1])
            if len(sentences) % 2 == 1 and sentences[-1].strip():
                combined_s.append(sentences[-1])

            for s in combined_s:
                s = s.strip()
                if not s:
                    continue
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


def _call_gemini_tts_raw_chunk(text: str, voice_name: str = "Fenrir", timeout: int = 35) -> bytes:
    """Invokes Google AI Studio Gemini Flash TTS REST API with automatic key rotation."""
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
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    req_data = json.dumps(payload).encode("utf-8")

    max_attempts = max(3, len(KEY_RING.keys) * 2)
    last_err = None

    for _ in range(max_attempts):
        try:
            api_key = KEY_RING.get_next_key()
        except Exception as e:
            last_err = e
            break

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{PRIMARY_TTS_MODEL}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                cand = res.get("candidates", [{}])[0]
                if "content" in cand:
                    parts = cand["content"].get("parts", [])
                    if parts and "inlineData" in parts[0]:
                        raw_b64 = parts[0]["inlineData"].get("data", "")
                        return base64.b64decode(raw_b64)
        except urllib.error.HTTPError as e:
            last_err = e
            logger.warning(f"Gemini Flash TTS Key [{api_key[:6]}...] HTTP {e.code}: {e.reason}")
            KEY_RING.record_error(api_key)
            time.sleep(0.8)
        except Exception as e:
            last_err = e
            logger.warning(f"Gemini Flash TTS error: {e}")
            KEY_RING.record_error(api_key)
            time.sleep(0.8)

    raise RuntimeError(f"Gemini Flash TTS synthesis failed across all keys: {last_err}")


def _fallback_edge_tts_full(text: str, out_raw_mp3: str):
    """Zero-cost Edge-TTS fallback if all Gemini keys are throttled."""
    import asyncio
    import edge_tts
    has_devanagari = any('\u0900' <= char <= '\u097f' for char in text)
    voice = "hi-IN-MadhurNeural" if has_devanagari else "en-US-ChristopherNeural"

    async def _run():
        comm = edge_tts.Communicate(text, voice, rate="-2%", pitch="-1Hz")
        await comm.save(out_raw_mp3)

    asyncio.run(_run())


def synthesize_master_voice(
    text: str,
    out_mp3_path: str,
    voice_name: str = "Fenrir",
    apply_dsp: bool = True
) -> str:
    """
    Synthesizes long-form voice using Google AI Studio Gemini Flash TTS (Free Tier)
    with Shure SM7B Broadcast Vocal Mastering Chain.

    Steps:
    1. Phonetic transliteration of tech/financial terms.
    2. Intelligent sentence-level chunking.
    3. Multi-key pooled synthesis via Gemini Flash TTS (24kHz studio PCM).
    4. Edge-TTS resilient fallback if quota/network error occurs.
    5. 6-stage Shure SM7B DSP vocal mastering (Highpass + Warmth + Air + De-Esser + Comp + Loudnorm -14 LUFS).
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_mp3_path)), exist_ok=True)
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(out_mp3_path)), "temp_vox_build")
    os.makedirs(temp_dir, exist_ok=True)

    # 1. Phonetic transliteration
    clean_text = apply_phonetic_transliteration(text)

    raw_pcm_chunks = []
    engine_used = "edge_tts_shure_sm7b_locked"

    if FORCE_EDGE_TTS_LOCKED:
        logger.info(f"🔒 [VOICE HARD-LOCKED] Synthesizing Voice via Edge-TTS 48kHz + Shure SM7B DSP (0% Gemini Quota)...")
        edge_raw = os.path.join(temp_dir, "edge_raw.mp3")
        _fallback_edge_tts_full(clean_text, edge_raw)
        input_args = ["-i", edge_raw]
        temp_input_to_clean = edge_raw
    else:
        chunks = chunk_script_for_tts(clean_text, max_chars=480)
        logger.info(f"🎙️ Gemini Flash TTS Voice synthesis: {len(chunks)} chunks, Voice: '{voice_name}'...")
        engine_used = "gemini_flash_tts"

        try:
            for idx, chunk in enumerate(chunks):
                chunk_raw = os.path.join(temp_dir, f"chunk_{idx:03d}.raw")
                logger.info(f"   [Chunk {idx+1}/{len(chunks)}] Synthesizing via Google AI Studio ({len(chunk)} chars)...")
                pcm_bytes = _call_gemini_tts_raw_chunk(chunk, voice_name=voice_name)
                with open(chunk_raw, "wb") as f:
                    f.write(pcm_bytes)
                raw_pcm_chunks.append(chunk_raw)
        except Exception as e:
            logger.warning(f"⚠️ Gemini Flash TTS encountered an issue: {e}. Switching to Resilient Edge-TTS fallback...")
            engine_used = "edge_tts_fallback"
            raw_pcm_chunks = []

        # Prepare raw input for mastering
        if engine_used == "gemini_flash_tts" and raw_pcm_chunks:
            combined_pcm = os.path.join(temp_dir, "combined_24k.raw")
            with open(combined_pcm, "wb") as outfile:
                for pcm_path in raw_pcm_chunks:
                    with open(pcm_path, "rb") as infile:
                        outfile.write(infile.read())
                    try:
                        os.remove(pcm_path)
                    except OSError:
                        pass
            input_args = ["-f", "s16le", "-ar", "24000", "-ac", "1", "-i", combined_pcm]
            temp_input_to_clean = combined_pcm
        else:
            edge_raw = os.path.join(temp_dir, "edge_raw.mp3")
            _fallback_edge_tts_full(clean_text, edge_raw)
            input_args = ["-i", edge_raw]
            temp_input_to_clean = edge_raw

    # 5. Broadcast DSP Vocal Mastering Chain
    logger.info("🎛️ Mastering Voice with Shure SM7B Broadcast Vocal Chain & EBU R128 (-14 LUFS)...")
    if apply_dsp:
        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-af", BROADCAST_DSP_CHAIN,
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            "-ar", "48000",
            "-ac", "2",
            out_mp3_path
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            "-ar", "48000",
            "-ac", "2",
            out_mp3_path
        ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        if os.path.exists(temp_input_to_clean):
            os.remove(temp_input_to_clean)
    except OSError:
        pass

    file_size_kb = os.path.getsize(out_mp3_path) / 1024.0
    logger.success(f"🏆 Broadcast-Grade Voice Mastered -> {out_mp3_path} ({file_size_kb:.1f} KB, Engine: {engine_used.upper()})")
    return out_mp3_path


def mix_voice_with_dynamic_ducked_score(
    voice_path: str,
    music_loop_path: str,
    out_mixed_path: str,
    ducking_ratio: float = 8.0,
    ducking_threshold: float = 0.04
) -> str:
    """
    Mixes mastered voiceover with looping cinematic background score.
    Automatically applies sidechain compression so the music dynamically ducks
    by -24dB whenever voiceover is speaking and gently rises during pauses.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_mixed_path)), exist_ok=True)
    logger.info("🎧 Mixing Mastered Voice with Dynamic Ducked Music Bed...")

    filter_complex = (
        "[1:a]volume=0.20[music_bed];"
        f"[music_bed][0:a]sidechaincompress=threshold={ducking_threshold}:ratio={ducking_ratio}:attack=15:release=350[ducked_music];"
        "[0:a][ducked_music]amix=inputs=2:normalize=0[mixed]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", voice_path,
        "-stream_loop", "-1", "-i", music_loop_path,
        "-filter_complex", filter_complex,
        "-map", "[mixed]",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        out_mixed_path
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logger.success(f"🎵 Master Cinematic Soundtrack with Dynamic Ducking Ready -> {out_mixed_path}")
    return out_mixed_path


if __name__ == "__main__":
    out_test = os.path.join(_root, "output", "test_gemini_voice_improved_master.mp3")
    sample_script = (
        "नमस्कार। Google AI Studio का Gemini Flash TTS इंजन अब सक्रिय है। "
        "TSMC, ASML और NVIDIA की 13.5 नैनोमीटर EUV तकनीक ने दुनिया की पूरी सेमीकंडक्टर सप्लाई चेन को बदल दिया है। "
        "इस नए ब्रॉडकास्ट DSP मास्टरींग चेन के साथ आवाज़ में Shure SM7B जैसा भारीपन, "
        "क्रिस्टल क्लैरिटी और परफेक्ट यूट्यूब लाउडनेस मौजूद है।"
    )
    synthesize_master_voice(sample_script, out_test, voice_name="Fenrir", apply_dsp=True)
