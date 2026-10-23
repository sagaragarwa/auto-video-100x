import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

def create_ultra_thumbnail(
    bg_image_or_video: str,
    output_path: str,
    punchline: str = "IT'S A TRAP!",
    badge_text: str = "DEEP DOCUMENTARY",
    highlight_color: tuple = (255, 230, 0), # Electric Yellow
    frame_timestamp_sec: float = 15.0,
):
    """
    Renders an Ultra High-CTR, algorithm-catchy 1080p YouTube thumbnail.
    STRICT ZERO AI IMAGES POLICY:
    Extracts an authentic crisp 1080p frame from real video footage (Pexels/Pixabay),
    boosts cinematic contrast/saturation, and stamps high-converting 3D typography.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    target_w, target_h = 1920, 1080

    # 1. Acquire base frame from actual video footage (ZERO AI GENERATED IMAGES)
    im = None
    if bg_image_or_video.lower().endswith((".mp4", ".mov", ".mkv", ".avi", ".webm")):
        import subprocess
        ffmpeg_bin = "ffmpeg"
        temp_frame = output_path + f".temp_frame_{int(frame_timestamp_sec)}.jpg"
        for ts in [str(frame_timestamp_sec), "10", "3", "0"]:
            try:
                cmd = [
                    ffmpeg_bin, "-y",
                    "-ss", ts,
                    "-i", bg_image_or_video,
                    "-vframes", "1",
                    "-q:v", "2",
                    temp_frame
                ]
                subprocess.run(cmd, capture_output=True, check=True)
                if os.path.exists(temp_frame) and os.path.getsize(temp_frame) > 1000:
                    im = Image.open(temp_frame).convert("RGB")
                    try:
                        os.remove(temp_frame)
                    except Exception:
                        pass
                    break
            except Exception:
                if os.path.exists(temp_frame):
                    try:
                        os.remove(temp_frame)
                    except Exception:
                        pass

    if im is None:
        if os.path.exists(bg_image_or_video) and bg_image_or_video.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            im = Image.open(bg_image_or_video).convert("RGB")
        else:
            # Fallback to rich dark gradient
            im = Image.new("RGB", (target_w, target_h), (12, 16, 28))

    im = im.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # 2. Cinematic Color Grade & Pop
    # Boost saturation (+35%) and contrast (+25%) for irresistible eye attraction
    enh_color = ImageEnhance.Color(im)
    im = enh_color.enhance(1.35)
    enh_con = ImageEnhance.Contrast(im)
    im = enh_con.enhance(1.25)

    # 3. Vignette & Contrast Gradients
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    d_ov = ImageDraw.Draw(overlay)

    # Dark gradient at the bottom for ultra-crisp text readability
    grad_height = 420
    for y_step in range(grad_height):
        alpha = int((y_step / grad_height) ** 1.5 * 200)
        y_pos = target_h - grad_height + y_step
        d_ov.line([(0, y_pos), (target_w, y_pos)], fill=(0, 0, 0, alpha))

    # Dark radial vignette around the outer perimeter
    for border in range(60):
        alpha = int((1.0 - (border / 60)) * 120)
        d_ov.rectangle([border, border, target_w - border, target_h - border], outline=(0, 0, 0, alpha), width=2)

    im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(im)

    # 4. Font Resolution
    font_paths = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/seguiemb.ttf",
    ]
    main_font = None
    badge_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                main_font = ImageFont.truetype(fp, 140)
                badge_font = ImageFont.truetype(fp, 46)
                break
            except Exception:
                continue

    if not main_font:
        main_font = ImageFont.load_default()
        badge_font = main_font

    # 5. Render Attention Badge (Top-Left)
    if badge_text:
        badge_text_clean = badge_text.upper()
        bbox = badge_font.getbbox(badge_text_clean)
        bw = bbox[2] - bbox[0] + 48
        bh = bbox[3] - bbox[1] + 28
        bx, by = 80, 80
        # Draw Crimson Red Badge
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(220, 20, 60))
        # Draw Yellow Accent line on left of badge
        draw.rectangle([bx, by, bx + 10, by + bh], fill=highlight_color)
        draw.text((bx + 26, by + 12), badge_text_clean, font=badge_font, fill=(255, 255, 255))

    # 6. Render Ultra 3D Punchline Text (Bottom-Left)
    punchline_lines = [l.strip().upper() for l in punchline.split("\n") if l.strip()]
    if not punchline_lines:
        punchline_lines = [punchline.upper()]

    start_y = target_h - (len(punchline_lines) * 155) - 60
    base_x = 80

    for line_idx, line in enumerate(punchline_lines):
        line_y = start_y + (line_idx * 155)
        # Deep black 3D shadow & stroke (8-direction offset)
        stroke_radius = 8
        for dx in range(-stroke_radius, stroke_radius + 1):
            for dy in range(-stroke_radius, stroke_radius + 1):
                draw.text((base_x + dx, line_y + dy), line, font=main_font, fill=(0, 0, 0))

        # Bottom-right extra 3D drop shadow
        for shadow_offset in range(4, 14, 2):
            draw.text((base_x + shadow_offset, line_y + shadow_offset), line, font=main_font, fill=(0, 0, 0))

        # Vibrant foreground text
        # If multiple lines: Alternate between Electric Yellow and Pure White
        line_color = highlight_color if line_idx % 2 == 0 else (255, 255, 255)
        draw.text((base_x, line_y), line, font=main_font, fill=line_color)

    im.save(output_path, "JPEG", quality=95)
    return output_path

if __name__ == "__main__":
    test_out = "output/sample_ultra_thumbnail.jpg"
    res = create_ultra_thumbnail(
        "output/depression_ep01_neurobiology.mp4",
        test_out,
        punchline="TRAPPED IN\nYOUR BRAIN?",
        badge_text="HARVARD NEUROSCIENCE"
    )
    print(f"Thumbnail created: {res} ({os.path.getsize(res)} bytes)")
