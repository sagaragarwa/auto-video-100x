"""
Kinetic Subtitle Engine (Hormozi / Vox Karaoke Style)
100% Free & Local via faster-whisper INT8 CPU Inference + ASS Formatting.
Generates word-level active glow subtitles with micro-scale bounce and contextual emojis.
"""

import os
import sys
import re
from typing import List, Dict, Any, Tuple

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("kinetic_subtitles")

from faster_whisper import WhisperModel

EMOJI_KEYWORDS = {
    "ai": "🧠",
    "intelligence": "🧠",
    "neural": "🧠",
    "brain": "🧠",
    "silicon": "💾",
    "chip": "⚡",
    "hardware": "🖥️",
    "money": "💰",
    "billion": "💵",
    "trillion": "🏦",
    "market": "📈",
    "power": "⚡",
    "energy": "🔋",
    "war": "⚔️",
    "monopoly": "🏰",
    "world": "🌍",
    "global": "🌐",
    "future": "🚀",
    "quantum": "⚛️",
    "algorithm": "⚙️",
    "data": "📊"
}


def format_ass_timestamp(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"


def get_contextual_emoji(word: str) -> str:
    clean = re.sub(r"[^\w]", "", word.lower())
    return EMOJI_KEYWORDS.get(clean, "")


def generate_kinetic_ass(
    audio_path: str,
    out_ass_path: str,
    language: str = None,
    font_name: str = "Arial Black",
    font_size: int = 42,
    words_per_group: int = 4
) -> str:
    """
    Transcribes audio with word-level precision and writes an animated .ass subtitle file.
    Each word lights up with active color highlight and micro-scale pop as it is spoken.
    """
    logger.info(f"🎙️ Transcribing audio with faster-whisper for kinetic subtitles: {audio_path}...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")

    kwargs = {"word_timestamps": True}
    if language:
        kwargs["language"] = language

    segments, info = model.transcribe(audio_path, **kwargs)
    logger.info(f"   Detected language: {info.language} ({info.language_probability:.2f})")

    # Collect all words
    all_words = []
    for seg in segments:
        for w in seg.words:
            all_words.append({
                "word": w.word.strip(),
                "start": w.start,
                "end": w.end
            })

    if not all_words:
        logger.warning("No words extracted by whisper!")
        return out_ass_path

    # Group into punchy 3-4 word phrases
    groups = []
    curr = []
    for w in all_words:
        curr.append(w)
        if len(curr) >= words_per_group or w["word"].endswith((".", "!", "?", "।")):
            groups.append(curr)
            curr = []
    if curr:
        groups.append(curr)

    # Build ASS Header
    # Colors in ASS are &HAABBGGRR (Alpha, Blue, Green, Red)
    # White: &H00FFFFFF
    # Electric Yellow/Cyan Highlight: &H0000F0FF (Yellow) or &H00FFFF00 (Cyan)
    ass_header = f"""[Script Info]
Title: 1000x Kinetic Subtitles
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KineticVox,{font_name},{font_size},&H00FFFFFF,&H0000F0FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,3.8,2.2,2,40,40,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    for grp in groups:
        grp_start = grp[0]["start"]
        grp_end = grp[-1]["end"]

        # For each active word in this group, generate a sub-event where that word is highlighted
        for active_idx, target in enumerate(grp):
            word_start = target["start"]
            word_end = target["end"]
            
            # Format phrase text with active word highlighted in electric yellow/gold
            line_parts = []
            for idx, w in enumerate(grp):
                emoji = get_contextual_emoji(w["word"])
                disp_word = (w["word"] + f" {emoji}").strip() if emoji else w["word"]
                if idx == active_idx:
                    # Active word: Golden Cyan glow + 1.12x scale pop
                    line_parts.append(r"{\c&H0024F5FF\fscx112\fscy112}" + disp_word + r"{\r}")
                else:
                    # Inactive word: Crisp white
                    line_parts.append(r"{\c&H00FFFFFF\fscx100\fscy100}" + disp_word + r"{\r}")

            combined_text = " ".join(line_parts)
            start_str = format_ass_timestamp(word_start)
            end_str = format_ass_timestamp(word_end)
            events.append(f"Dialogue: 0,{start_str},{end_str},KineticVox,,0,0,0,,{combined_text}\n")

    os.makedirs(os.path.dirname(os.path.abspath(out_ass_path)), exist_ok=True)
    with open(out_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
        for ev in events:
            f.write(ev)

    logger.success(f"✅ Kinetic ASS Subtitles ready ({len(events)} animated word-states) -> {out_ass_path}")
    return out_ass_path


if __name__ == "__main__":
    test_audio = os.path.join(_root, "output", "gemini_tts_english_sample.mp3")
    test_ass = os.path.join(_root, "output", "test_kinetic.ass")
    generate_kinetic_ass(test_audio, test_ass)
