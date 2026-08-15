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

def get_photo_path(filename: str) -> str:
    path = os.path.join(PHOTOS_DIR, filename)
    if os.path.exists(path):
        return path
    photos = [os.path.join(PHOTOS_DIR, f) for f in os.listdir(PHOTOS_DIR) if f.endswith(".jpg")] if os.path.exists(PHOTOS_DIR) else []
    return photos[0] if photos else None

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

    # Load bold fonts with extra large mobile-optimized sizes
    try:
        badge_font = ImageFont.truetype("arialbd.ttf", 48)
        title_font = ImageFont.truetype("arialbd.ttf", 76)
        caption_font = ImageFont.truetype("arialbd.ttf", 64)
    except Exception:
        badge_font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        caption_font = ImageFont.load_default()

    # 1. Top Pill Badge (Large & Vibrant)
    is_course = "DAY" in badge_text.upper()
    badge_bg = (37, 99, 235, 255) if is_course else (245, 158, 11, 255)  # Electric Blue or Vibrant Amber
    badge_w = len(badge_text) * 30 + 80
    badge_x = (width - badge_w) // 2
    draw.rounded_rectangle([badge_x, 130, badge_x + badge_w, 230], radius=28, fill=badge_bg)
    draw.text((badge_x + 40, 155), badge_text, fill=(255, 255, 255), font=badge_font)

    # 2. Main Title (Extra Large 76px Bold with Drop Shadow)
    wrapped_title = textwrap.fill(title, width=18)
    y_title = 260
    for line in wrapped_title.split("\n"):
        line_w = len(line) * 40
        line_x = (width - line_w) // 2
        # Deep Drop Shadow
        draw.text((line_x + 5, y_title + 5), line, fill=(0, 0, 0, 255), font=title_font)
        draw.text((line_x, y_title), line, fill=(255, 255, 255), font=title_font)
        y_title += 90

    # 3. Center-Bottom Caption Card (Extra Large 64px Bold)
    if caption:
        # Wrap to 18-20 characters for big, punchy text
        wrapped_caption = textwrap.fill(caption, width=20)
        lines = wrapped_caption.split("\n")
        card_h = len(lines) * 90 + 70
        card_w = width - 100
        card_x = 50
        card_y = height - card_h - 220

        # Translucent dark slate card with glowing border
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=32,
            fill=(15, 23, 42, 240),
            outline=(56, 189, 248, 220),
            width=4
        )
        
        y_line = card_y + 35
        for line in lines:
            line_w = len(line) * 34
            line_x = (width - line_w) // 2
            # Drop shadow
            draw.text((line_x + 4, y_line + 4), line, fill=(0, 0, 0, 255), font=caption_font)
            draw.text((line_x, y_line), line, fill=(248, 250, 252), font=caption_font)
            y_line += 90

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
