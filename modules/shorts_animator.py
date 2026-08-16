"""
shorts_animator.py — High-Tech 9:16 Shorts Video Animation Engine
- Multi-photo 1080x1920 HD Ken Burns Slideshow
- Large, bold, ultra-readable mobile captions (68px+) with glowing accents & rounded cards
"""
import os
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "photos")

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")

def load_custom_font(size: int, bold: bool = True):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "arial.ttf"]
    for name in font_names:
        bundled_path = os.path.join(FONTS_DIR, name)
        if os.path.exists(bundled_path):
            try:
                return ImageFont.truetype(bundled_path, size)
            except Exception:
                pass
    linux_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for lp in linux_paths:
        if os.path.exists(lp):
            try:
                return ImageFont.truetype(lp, size)
            except Exception:
                pass
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    except Exception:
        return ImageFont.load_default(size=size) if hasattr(ImageFont, "load_default") and "size" in ImageFont.load_default.__code__.co_varnames else ImageFont.load_default()

def create_rich_frame(photo_path: str, badge_text: str, title: str, caption: str, progress: float = 0.0) -> Image.Image:
    width, height = 1080, 1920
    
    if photo_path and os.path.exists(photo_path):
        bg = Image.open(photo_path).convert("RGBA")
        # Apply smooth zoom effect (1.0 to 1.10 scale)
        zoom = 1.0 + (progress * 0.10)
        new_w = int(width * zoom)
        new_h = int(height * zoom)
        bg = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        bg = bg.crop((left, top, left + width, top + height))
    else:
        bg = Image.new("RGBA", (width, height), (15, 23, 42, 255))

    # Dark gradient overlays for crisp readability
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # Top gradient
    for y in range(550):
        alpha = int(210 * (1.0 - y / 550))
        draw_overlay.line([(0, y), (width, y)], fill=(10, 15, 29, alpha))
    
    # Bottom gradient for captions
    for y in range(1000, height):
        alpha = int(240 * ((y - 1000) / (height - 1000)))
        draw_overlay.line([(0, y), (width, y)], fill=(10, 15, 29, alpha))

    combined = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(combined)

    # Load bold fonts using bundled TTF assets with cross-platform fallbacks
    badge_font   = load_custom_font(size=38, bold=True)
    title_font   = load_custom_font(size=54, bold=True)
    caption_font = load_custom_font(size=42, bold=True)

    # 1. Top Pill Badge (Compact & Clean)
    is_course = "DAY" in badge_text.upper()
    badge_bg = (37, 99, 235, 255) if is_course else (245, 158, 11, 255)
    badge_w = len(badge_text) * 24 + 60
    badge_x = (width - badge_w) // 2
    draw.rounded_rectangle([badge_x, 130, badge_x + badge_w, 210], radius=22, fill=badge_bg)
    draw.text((badge_x + 30, 148), badge_text, fill=(255, 255, 255), font=badge_font)

    # 2. Main Title (54px Bold)
    wrapped_title = textwrap.fill(title, width=22)
    y_title = 240
    for line in wrapped_title.split("\n"):
        line_w = len(line) * 28
        line_x = (width - line_w) // 2
        # Drop Shadow
        draw.text((line_x + 3, y_title + 3), line, fill=(0, 0, 0, 240), font=title_font)
        draw.text((line_x, y_title), line, fill=(255, 255, 255), font=title_font)
        y_title += 68

    # 3. Transparent Captions (No Card Background, 100% Transparent with 3D Outline Stroke)
    if caption:
        wrapped_caption = textwrap.fill(caption, width=28)
        lines = wrapped_caption.split("\n")
        total_h = len(lines) * 58
        y_line = height - total_h - 180
        
        for line in lines:
            line_w = len(line) * 22
            line_x = (width - line_w) // 2
            
            # Thick black outline stroke + drop shadow for 100% legibility on any image
            draw.text(
                (line_x, y_line),
                line,
                fill=(255, 255, 255),
                font=caption_font,
                stroke_width=4,
                stroke_fill=(0, 0, 0)
            )
            y_line += 58

    return combined.convert("RGB")

def build_animated_shorts_video(audio_path: str, photo_files: list, badge_text: str, title: str, script: str, output_path: str):
    import moviepy
    is_v2 = int(moviepy.__version__.split(".")[0]) >= 2
    
    if is_v2:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    else:
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    # Split script into clean sentence phrases for captions
    sentences = [s.strip() for s in script.replace("!", ".").replace("?", ".").split(".") if len(s.strip()) > 5]
    if not sentences:
        sentences = [script]
    
    num_segments = max(len(photo_files), len(sentences))
    seg_duration = total_duration / num_segments
    
    clips = []
    for i in range(num_segments):
        photo_name = photo_files[i % len(photo_files)]
        photo_path = get_photo_path(photo_name)
        caption = sentences[i % len(sentences)]
        
        frame_img = create_rich_frame(photo_path, badge_text, title, caption, progress=i / num_segments)
        frame_np = np.array(frame_img)
        
        if is_v2:
            clip = ImageClip(frame_np).with_duration(seg_duration)
        else:
            clip = ImageClip(frame_np).set_duration(seg_duration)
        clips.append(clip)
        
    final_video = concatenate_videoclips(clips, method="compose")
    if is_v2:
        final_video = final_video.with_audio(audio)
    else:
        final_video = final_video.set_audio(audio)
        
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    return output_path
