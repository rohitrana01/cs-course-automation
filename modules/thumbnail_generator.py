"""
thumbnail_generator.py — Generates clean, click-worthy 9:16 (1080x1920) Vertical Shorts Thumbnails
Supports both DeepBeepMeep 3D Cyber Aesthetic and Classic Modern Tech themes.
"""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

from modules.shorts_animator import load_custom_font

def create_shorts_thumbnail(title: str, subtitle: str, badge_text: str, bg_image_path: str, output_path: str, theme: str = "deepbeepmeep"):
    # Base 1080x1920 vertical canvas
    width, height = 1080, 1920
    
    if bg_image_path and os.path.exists(bg_image_path):
        bg = Image.open(bg_image_path).convert("RGBA")
        bg = bg.resize((width, height), Image.Resampling.LANCZOS)
    else:
        # Dark tech navy gradient fallback
        bg = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    
    # Dark vignette overlay to ensure text is 100% readable
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # Gradient dimming from center to bottom
    for y in range(height):
        alpha = int(140 + (y / height) * 90)  # 140 to 230 alpha
        draw_overlay.line([(0, y), (width, y)], fill=(10, 15, 29, min(255, alpha)))
    
    combined = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(combined)
    
    # In DeepBeepMeep theme, render top cyber cyan accent bar
    if theme == "deepbeepmeep":
        draw.rectangle([0, 0, width, 14], fill=(56, 189, 248, 255))

    # Load fonts using bundled cross-platform font loader
    badge_font = load_custom_font(size=36, bold=True)
    title_font = load_custom_font(size=64, bold=True)
    sub_font   = load_custom_font(size=38, bold=False)

    clean_badge = "".join(c for c in badge_text if ord(c) < 128 or c in "•—–-").strip()
    is_course = "DAY" in clean_badge.upper()
    text_w = draw.textlength(clean_badge, font=badge_font)
    badge_box = [80, 320, 80 + int(text_w) + 40, 390]

    # Draw Top Badge (DeepBeepMeep Cyber Pill vs Classic)
    if theme == "deepbeepmeep":
        badge_border = (56, 189, 248, 240) if is_course else (250, 204, 21, 240)
        badge_bg = (15, 23, 42, 235)
        badge_text_color = (56, 189, 248) if is_course else (250, 204, 21)
        draw.rounded_rectangle(badge_box, radius=20, fill=badge_bg, outline=badge_border, width=3)
        draw.text((100, 335), clean_badge, fill=badge_text_color, font=badge_font)
    else:
        badge_bg_color = (37, 99, 235, 240) if is_course else (217, 119, 6, 240) # Blue for CS, Amber for Trivia
        draw.rounded_rectangle(badge_box, radius=16, fill=badge_bg_color)
        draw.text((100, 335), clean_badge, fill=(255, 255, 255), font=badge_font)

    # Draw Main Title (Wrapped)
    wrapped_title = textwrap.fill(title, width=22)
    y_text = 440
    for line in wrapped_title.split("\n"):
        # Shadow for 3D pop
        draw.text((83, y_text + 3), line, fill=(0, 0, 0, 220), font=title_font)
        draw.text((80, y_text), line, fill=(255, 255, 255), font=title_font)
        y_text += 80

    # Draw Subtitle / Hook
    if subtitle:
        sub_color = (56, 189, 248) if theme == "deepbeepmeep" else (148, 163, 184)
        wrapped_sub = textwrap.fill(subtitle, width=32)
        y_text += 20
        for line in wrapped_sub.split("\n"):
            draw.text((82, y_text + 2), line, fill=(0, 0, 0, 180), font=sub_font)
            draw.text((80, y_text), line, fill=sub_color, font=sub_font)
            y_text += 50

    # Save final RGB JPEG
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    combined.convert("RGB").save(output_path, "JPEG", quality=95)
    return output_path

if __name__ == "__main__":
    test_out = create_shorts_thumbnail(
        title="What is a Computer?",
        subtitle="Hardware, CPU & Binary Basics",
        badge_text="DAY 1 • 100 DAYS CS",
        bg_image_path=None,
        output_path="test_thumbnail.jpg",
        theme="deepbeepmeep"
    )
    print(f"Test thumbnail created: {test_out}")
