"""
10,000x Procedural 3D Exploded-View Isometric Hardware Engine (Lemmino / Apple Keynote Style)
Uses mathematical isometric software projection (Zero Blender or external 3D engine required).
Renders 1080p animated exploded silicon architecture with glowing conduits & technical callouts.
"""

import os
import sys
import math
import subprocess
from typing import List, Dict, Any, Tuple

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_venv_site = os.path.join(_root, ".venv", "Lib", "site-packages")
if os.path.exists(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

from PIL import Image, ImageDraw, ImageFont

try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("isometric_3d")


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\impact.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def project_iso(x: float, y: float, z: float, origin: Tuple[int, int], scale: float = 1.0) -> Tuple[int, int]:
    """Projects 3D cartesian coordinates (x, y, z) into 2D isometric screen space."""
    ox, oy = origin
    iso_x = ox + (x - y) * math.cos(math.radians(30)) * scale
    iso_y = oy + (x + y) * math.sin(math.radians(30)) * scale - (z * scale)
    return int(iso_x), int(iso_y)


def draw_isometric_slab(
    draw: ImageDraw.Draw,
    center_x: float,
    center_y: float,
    z_height: float,
    thickness: float,
    w: float,
    l: float,
    top_color: Tuple[int, int, int, int],
    side_color: Tuple[int, int, int, int],
    edge_color: Tuple[int, int, int, int],
    origin: Tuple[int, int],
    scale: float = 1.0
):
    """Draws a 3D isometric rectangular slab at specified Z elevation."""
    # 4 top vertices
    p1 = project_iso(center_x - w/2, center_y - l/2, z_height + thickness, origin, scale)
    p2 = project_iso(center_x + w/2, center_y - l/2, z_height + thickness, origin, scale)
    p3 = project_iso(center_x + w/2, center_y + l/2, z_height + thickness, origin, scale)
    p4 = project_iso(center_x - w/2, center_y + l/2, z_height + thickness, origin, scale)

    # 4 bottom vertices
    b1 = project_iso(center_x - w/2, center_y - l/2, z_height, origin, scale)
    b2 = project_iso(center_x + w/2, center_y - l/2, z_height, origin, scale)
    b3 = project_iso(center_x + w/2, center_y + l/2, z_height, origin, scale)
    b4 = project_iso(center_x - w/2, center_y + l/2, z_height, origin, scale)

    # Front right face
    draw.polygon([p2, p3, b3, b2], fill=side_color, outline=edge_color)
    # Front left face
    draw.polygon([p3, p4, b4, b3], fill=side_color, outline=edge_color)
    # Top face
    draw.polygon([p1, p2, p3, p4], fill=top_color, outline=edge_color)


def render_exploded_silicon_blueprint(
    out_video_path: str,
    duration: float = 4.5,
    fps: int = 30
) -> str:
    """
    Renders an animated 1080p exploded-view hardware blueprint showing:
    Layer 1: Substrate
    Layer 2: Silicon Interposer
    Layer 3: Twin Compute Dies & HBM Memory Stacks
    Separating smoothly with technical dimension lines and labels.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_video_path)), exist_ok=True)
    frames_dir = os.path.join(os.path.dirname(os.path.abspath(out_video_path)), "temp_iso_frames")
    os.makedirs(frames_dir, exist_ok=True)

    W, H = 1920, 1080
    origin = (820, 580)
    scale = 1.35
    total_frames = int(duration * fps)
    anim_frames = int(2.2 * fps)

    font_title = get_font(44, bold=True)
    font_sub = get_font(22, bold=False)
    font_callout = get_font(24, bold=True)
    font_dim = get_font(18, bold=False)

    for f_idx in range(total_frames):
        raw_t = min(1.0, f_idx / anim_frames)
        # Smooth easeOutCubic
        ease_t = 1.0 - math.pow(1.0 - raw_t, 3)

        img = Image.new("RGBA", (W, H), (8, 12, 20, 255))
        draw = ImageDraw.Draw(img)

        # Technical blueprint background grid
        for gx in range(0, W, 80):
            draw.line([(gx, 0), (gx, H)], fill=(16, 24, 40, 255), width=1)
        for gy in range(0, H, 80):
            draw.line([(0, gy), (W, gy)], fill=(16, 24, 40, 255), width=1)

        # Top Header Overlay
        draw.text((120, 90), "BLACKWELL ARCHITECTURE // EXPLODED 3D SCHEMATIC", fill=(255, 255, 255, 255), font=font_title)
        draw.text((120, 145), "TSMC 3nm Dual-Die Reticle Limit • CoWoS-L Advanced Packaging Integration", fill=(140, 170, 210, 255), font=font_sub)

        # Separation Distances
        z_layer1 = 0.0
        z_layer2 = 70.0 * ease_t
        z_layer3 = 190.0 * ease_t

        # ---------------------------------------------------------
        # Layer 1 (Bottom): Organic Package Substrate (Dark Graphite)
        # ---------------------------------------------------------
        draw_isometric_slab(
            draw, 0, 0, z_layer1, thickness=18, w=480, l=480,
            top_color=(24, 32, 48, 255), side_color=(14, 20, 32, 255), edge_color=(45, 65, 95, 255),
            origin=origin, scale=scale
        )

        # ---------------------------------------------------------
        # Layer 2 (Middle): TSMC CoWoS-L Silicon Interposer (Cobalt Blue)
        # ---------------------------------------------------------
        draw_isometric_slab(
            draw, 0, 0, z_layer2, thickness=12, w=400, l=400,
            top_color=(18, 48, 88, 255), side_color=(10, 28, 54, 255), edge_color=(0, 180, 255, 255),
            origin=origin, scale=scale
        )

        # ---------------------------------------------------------
        # Layer 3 (Top): Dual Compute Dies + 8 HBM3e Memory Stacks
        # ---------------------------------------------------------
        # Die 1 (Left GPU)
        draw_isometric_slab(
            draw, -85, 0, z_layer3, thickness=20, w=150, l=240,
            top_color=(0, 210, 230, 255), side_color=(0, 140, 160, 255), edge_color=(255, 255, 255, 255),
            origin=origin, scale=scale
        )
        # Die 2 (Right GPU)
        draw_isometric_slab(
            draw, 85, 0, z_layer3, thickness=20, w=150, l=240,
            top_color=(0, 210, 230, 255), side_color=(0, 140, 160, 255), edge_color=(255, 255, 255, 255),
            origin=origin, scale=scale
        )

        # HBM3e Memory Stacks (Gold/Amber)
        for hbm_x in [-180, 180]:
            for hbm_y in [-90, -30, 30, 90]:
                draw_isometric_slab(
                    draw, hbm_x, hbm_y, z_layer3, thickness=22, w=50, l=50,
                    top_color=(255, 190, 40, 255), side_color=(190, 130, 20, 255), edge_color=(255, 235, 140, 255),
                    origin=origin, scale=scale
                )

        # ---------------------------------------------------------
        # Technical Floating Callout Leaders & Dimension Lines
        # ---------------------------------------------------------
        if ease_t > 0.4:
            alpha_leader = int(255 * min(1.0, (ease_t - 0.4) / 0.6))
            lead_color = (0, 240, 255, alpha_leader)

            # Leader 1: Top Compute Die
            c1 = project_iso(0, 0, z_layer3 + 22, origin, scale)
            draw.line([c1, (c1[0] + 160, c1[1] - 80), (c1[0] + 480, c1[1] - 80)], fill=lead_color, width=2)
            draw.text((c1[0] + 170, c1[1] - 116), "DUAL BLACKWELL GPU DIES", fill=(255, 255, 255, alpha_leader), font=font_callout)
            draw.text((c1[0] + 170, c1[1] - 86), "208 Billion Transistors • 10 TB/s NV-HighSpeed Interconnect", fill=(140, 210, 255, alpha_leader), font=font_dim)

            # Leader 2: HBM3e Memory
            c2 = project_iso(180, 60, z_layer3 + 24, origin, scale)
            draw.line([c2, (c2[0] + 120, c2[1] + 40), (c2[0] + 420, c2[1] + 40)], fill=(255, 190, 40, alpha_leader), width=2)
            draw.text((c2[0] + 130, c2[1] + 8), "8X HBM3e ULTRA-MEMORY", fill=(255, 210, 80, alpha_leader), font=font_callout)
            draw.text((c2[0] + 130, c2[1] + 46), "192 GB Capacity • 8.0 TB/s Silicon Bandwidth", fill=(220, 190, 130, alpha_leader), font=font_dim)

            # Leader 3: CoWoS Silicon Interposer
            c3 = project_iso(200, 200, z_layer2 + 12, origin, scale)
            draw.line([c3, (c3[0] + 140, c3[1] + 110), (c3[0] + 440, c3[1] + 110)], fill=(0, 160, 240, alpha_leader), width=2)
            draw.text((c3[0] + 150, c3[1] + 78), "TSMC CoWoS-L INTERPOSER", fill=(120, 200, 255, alpha_leader), font=font_callout)
            draw.text((c3[0] + 150, c3[1] + 116), "Sub-Micron Micro-Bumps • 3.3x Reticle Footprint", fill=(130, 160, 200, alpha_leader), font=font_dim)

        frame_path = os.path.join(frames_dir, f"iso_{f_idx:04d}.png")
        img.save(frame_path)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "iso_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "fast",
        out_video_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for f in os.listdir(frames_dir):
        try:
            os.remove(os.path.join(frames_dir, f))
        except OSError:
            pass
    try:
        os.rmdir(frames_dir)
    except OSError:
        pass

    logger.success(f"✅ 10,000x Exploded 3D Silicon Blueprint Ready -> {out_video_path}")
    return out_video_path


if __name__ == "__main__":
    test_iso = os.path.join(_root, "output", "test_exploded_blackwell_3d.mp4")
    render_exploded_silicon_blueprint(test_iso, duration=4.0)
