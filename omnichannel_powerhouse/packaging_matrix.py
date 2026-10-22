"""
High-CTR Packaging & YouTube SEO Matrix Engine
Generates:
1. Triple A/B Psychological Thumbnail Matrix (Cyan Monopoly, Amber Secret, Crimson Threat)
2. Automated Google Search "Key Moments" Chapter Timestamps
3. Algorithmically Engineered Titles, Descriptions & Pinned Comment Catalyst
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

from PIL import Image, ImageDraw, ImageFont, ImageFilter
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("packaging_matrix")


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:\\Windows\\Fonts\\impact.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def extract_keyframe(video_path: str, timestamp_s: float, out_jpg: str):
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp_s),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        out_jpg
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_triple_thumbnail_matrix(
    base_frame_path: str,
    output_dir: str,
    prefix: str = "demo_1000x"
) -> Dict[str, str]:
    """
    Renders 3 distinct psychological A/B test thumbnails at 1920x1080:
    Variant A: Cyan Monopoly (Investigative Tech)
    Variant B: Amber Secret (Financial Thriller)
    Variant C: Crimson Threat (Geopolitical War)
    """
    os.makedirs(output_dir, exist_ok=True)
    base_img = Image.open(base_frame_path).convert("RGBA").resize((1920, 1080))

    variants = [
        {
            "id": "A_monopoly_cyan",
            "punchline": "THE MONOPOLY\nIT'S OVER",
            "badge": "INVESTIGATIVE EXCLUSIVE",
            "accent": (0, 240, 255),
            "tint": (10, 20, 40, 130)
        },
        {
            "id": "B_secret_amber",
            "punchline": "$500B SECRET\nHIDDEN INSIDE",
            "badge": "DOCUMENTARY LEAK",
            "accent": (255, 190, 0),
            "tint": (40, 30, 10, 130)
        },
        {
            "id": "C_threat_crimson",
            "punchline": "TAIWAN CHIP WAR\nTHE COLLAPSE",
            "badge": "GLOBAL GEOPOLITICS",
            "accent": (255, 40, 70),
            "tint": (45, 10, 15, 140)
        }
    ]

    out_paths = {}

    for var in variants:
        canvas = base_img.copy()

        # 1. Dark Cinematic Color Tint & Contrast Wash
        tint_layer = Image.new("RGBA", (1920, 1080), var["tint"])
        canvas = Image.alpha_composite(canvas, tint_layer)

        # 2. Heavy Vignette & Bottom-Left Gradient for text contrast
        grad = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(grad)
        # Left-to-right dark gradient
        for x in range(1200):
            alpha = int(220 * (1.0 - (x / 1200.0)))
            gdraw.line([(x, 0), (x, 1080)], fill=(0, 0, 0, alpha))
        canvas = Image.alpha_composite(canvas, grad)

        draw = ImageDraw.Draw(canvas)

        # 3. Outer Neon Accent Border
        border_col = var["accent"]
        draw.rectangle([(0, 0), (1919, 1079)], outline=border_col, width=14)

        # 4. Top Category Badge
        badge_font = get_font(28, bold=True)
        badge_text = var["badge"]
        badge_box = [(90, 90), (90 + 380, 90 + 52)]
        draw.rounded_rectangle(badge_box, radius=10, fill=border_col)
        draw.text((115, 98), badge_text, fill=(0, 0, 0), font=badge_font)

        # 5. Giant Punchline Text with 3D Drop Shadow
        font_huge = get_font(120, bold=True)
        lines = var["punchline"].split("\n")
        y = 220
        for line in lines:
            # Drop shadow
            draw.text((95 + 8, y + 8), line, fill=(0, 0, 0, 240), font=font_huge)
            draw.text((95, y), line, fill=(255, 255, 255), font=font_huge)
            y += 145

        # 6. Glowing Corner Indicator
        draw.ellipse([(1780, 80), (1840, 140)], fill=border_col)

        out_jpg = os.path.join(output_dir, f"{prefix}_thumbnail_{var['id']}.jpg")
        canvas.convert("RGB").save(out_jpg, "JPEG", quality=95)
        out_paths[var["id"]] = out_jpg
        logger.success(f"🖼️ Thumbnail Variant Generated: {out_jpg}")

    return out_paths


def generate_seo_metadata(
    topic: str,
    duration_s: float,
    chapters: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generates complete YouTube metadata, timestamps, and pinned comment."""
    timestamps_text = ""
    for ch in chapters:
        start_s = ch.get("start", 0.0)
        mins = int(start_s // 60)
        secs = int(start_s % 60)
        title = ch.get("title", "Chapter")
        timestamps_text += f"{mins:02d}:{secs:02d} - {title}\n"

    seo = {
        "title_variants": [
            f"The Secret Semiconductor Monopoly That Controls Humanity | {topic}",
            f"How One Single Machine Holds The Entire World Hostage ({topic})",
            f"The $500B Chip War: Inside The Most Dangerous Monopoly on Earth"
        ],
        "description": f"""In this ultra-cinematic investigative documentary, we uncover the hidden architecture behind global semiconductor dominance, extreme ultraviolet lithography, and the geopolitical battle for sovereign compute.

TIMESTAMPS (KEY MOMENTS):
{timestamps_text}
⚡ PRODUCTION SPECIFICATIONS:
• Master Resolution: 1080p 60fps Ultra-Wide
• Audio: 24kHz Studio Multimodal Voiceover (-16 LUFS Broadcast EBU R128)
• Visuals: Kinetic 2.5D Motion Graphics & Micro-Foley Scoring

#AI #Semiconductor #TSMC #ASML #NVIDIA #Technology #Documentary""",
        "tags": [
            "artificial intelligence", "semiconductor", "tsmc", "asml", "nvidia",
            "microchip", "silicon", "gpu", "china taiwan chip war", "quantum computing",
            "extreme ultraviolet lithography", "supercomputer", "high tech documentary",
            "documentary hindi", "geopolitics", "future of technology"
        ],
        "pinned_comment": "💬 सवाल: अगर किसी वजह से ताइवान और ASML की सिलिकॉन सप्लाई चेन 6 महीने के लिए बंद हो जाए, तो दुनिया पर इसका सबसे बड़ा असर क्या होगा? कमेंट्स में अपनी राय ज़रूर शेयर करें! 👇"
    }

    return seo
