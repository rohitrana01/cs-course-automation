"""
thumbnail_generator.py — Generates clean, click-worthy 9:16 (1080x1920) Vertical Shorts Thumbnails
100% Safe, Educational & High-Tech Aesthetic
"""
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

from modules.shorts_animator import load_custom_font

def create_shorts_thumbnail(title: str, subtitle: str, badge_text: str, bg_image_path: str, output_path: str):
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
    
    # Load fonts using bundled cross-platform font loader
    badge_font = load_custom_font(size=36, bold=True)
    title_font = load_custom_font(size=64, bold=True)
    sub_font   = load_custom_font(size=38, bold=False)

    # Draw Top Badge (e.g. "DAY 1 • 100 DAYS CS" or "TECH FUN FACT #1")
    badge_bg_color = (37, 99, 235, 240) if "DAY" in badge_text.upper() else (217, 119, 6, 240) # Blue for CS, Amber for Trivia
    badge_box = [80, 320, 80 + len(badge_text) * 24 + 40, 390]
    draw.rounded_rectangle(badge_box, radius=16, fill=badge_bg_color)
    draw.text((100, 335), badge_text, fill=(255, 255, 255), font=badge_font)

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
        wrapped_sub = textwrap.fill(subtitle, width=32)
        y_text += 20
        for line in wrapped_sub.split("\n"):
            draw.text((82, y_text + 2), line, fill=(0, 0, 0, 180), font=sub_font)
            draw.text((80, y_text), line, fill=(148, 163, 184), font=sub_font)
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
        output_path="test_thumbnail.jpg"
    )
    print(f"Test thumbnail created: {test_out}")
