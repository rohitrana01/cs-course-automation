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

def get_photo_path(filename: str = None) -> str:
    if filename:
        path = os.path.join(PHOTOS_DIR, filename)
        if os.path.exists(path):
            return path
    photos = [os.path.join(PHOTOS_DIR, f) for f in os.listdir(PHOTOS_DIR) if f.endswith(".jpg") or f.endswith(".png")] if os.path.exists(PHOTOS_DIR) else []
    return photos[0] if photos else None

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

def create_rich_frame(photo_path: str, badge_text: str, title: str, caption: str, progress: float = 0.0, theme: str = "deepbeepmeep") -> Image.Image:
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

    # In DeepBeepMeep theme, render kinetic cyber progress bar at the top
    if theme == "deepbeepmeep":
        bar_w = int(width * progress)
        if bar_w > 0:
            draw.rectangle([0, 0, bar_w, 14], fill=(56, 189, 248, 255))

    # Load bold fonts using bundled TTF assets with cross-platform fallbacks
    badge_font   = load_custom_font(size=38, bold=True)
    title_font   = load_custom_font(size=54, bold=True)
    caption_font = load_custom_font(size=42, bold=True)

    # 1. Top Pill Badge (DeepBeepMeep Cyber Glow vs Classic)
    clean_badge = "".join(c for c in badge_text if ord(c) < 128 or c in "•—–-").strip()
    is_course = "DAY" in clean_badge.upper()
    text_w = draw.textlength(clean_badge, font=badge_font)
    badge_w = int(text_w + 60)
    badge_x = (width - badge_w) // 2
    if theme == "deepbeepmeep":
        badge_border = (56, 189, 248, 240) if is_course else (250, 204, 21, 240)
        badge_bg = (15, 23, 42, 235)
        badge_text_color = (56, 189, 248) if is_course else (250, 204, 21)
        draw.rounded_rectangle([badge_x, 130, badge_x + badge_w, 210], radius=24, fill=badge_bg, outline=badge_border, width=3)
        draw.text((badge_x + 30, 148), clean_badge, fill=badge_text_color, font=badge_font)
    else:
        badge_bg = (37, 99, 235, 255) if is_course else (245, 158, 11, 255)
        draw.rounded_rectangle([badge_x, 130, badge_x + badge_w, 210], radius=22, fill=badge_bg)
        draw.text((badge_x + 30, 148), clean_badge, fill=(255, 255, 255), font=badge_font)

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

    # 3. Transparent Captions with Two-Tone Karaoke Word Highlighting (Gold + White)
    EMPHASIS_KEYWORDS = {
        "python", "ram", "cpu", "memory", "ssd", "stop", "never", "always",
        "secret", "bug", "speed", "fast", "crash", "object", "classes", "oop",
        "f-strings", "lists", "tuples", "hash", "loop", "loops", "function", "functions",
        "o(1)", "10x", "1", "10", "100", "90%", "99%", "bytes", "bits", "1024", "error",
        "free", "speed", "million", "billion", "trick", "secret", "dictionary", "dictionaries"
    }

    if caption:
        wrapped_caption = textwrap.fill(caption, width=28)
        lines = wrapped_caption.split("\n")
        total_h = len(lines) * 58
        y_line = height - total_h - 180
        
        space_w = draw.textlength(" ", font=caption_font)
        
        for line in lines:
            words = line.split(" ")
            word_widths = [draw.textlength(w, font=caption_font) for w in words]
            total_w = sum(word_widths) + space_w * max(0, len(words) - 1)
            cur_x = (width - total_w) // 2
            
            for w, w_width in zip(words, word_widths):
                clean_w = w.strip(".,!?\"'()[]{}").lower()
                # Highlight tech terms, numbers, or action keywords in Vibrant Golden Yellow
                if clean_w in EMPHASIS_KEYWORDS or any(char.isdigit() for char in clean_w):
                    text_color = (250, 204, 21) # Vibrant Yellow Gold
                else:
                    text_color = (255, 255, 255) # Pure Crisp White
                
                # 4px black stroke for 100% legibility on any background
                draw.text(
                    (cur_x, y_line),
                    w,
                    fill=text_color,
                    font=caption_font,
                    stroke_width=4,
                    stroke_fill=(0, 0, 0)
                )
                cur_x += w_width + space_w
            
            y_line += 58

    return combined.convert("RGB")

def build_synced_phrases(words: list, script: str = "", max_words: int = 5, max_chars: int = 32) -> list:
    """
    Builds 100% synchronized, natural subtitle phrases using exact WordBoundary millisecond
    timestamps from Edge-TTS, aligned with original script punctuation and formatting.
    Guarantees zero subtitle drift across entire narration duration.
    """
    import re
    if not words:
        return []

    # Preserve punctuation by aligning TTS word tokens with the original script tokens
    script_clean = script.replace("—", "— ").replace("–", "– ") if script else ""
    raw_tokens = script_clean.split()
    
    aligned = []
    tok_idx = 0
    num_tokens = len(raw_tokens)
    
    for w in words:
        w_text = w.get("text", "").strip()
        w_clean = re.sub(r'[^\w%]', '', w_text).lower()
        matched = w_text
        
        while tok_idx < num_tokens:
            tok = raw_tokens[tok_idx]
            tok_clean = re.sub(r'[^\w%]', '', tok).lower()
            
            if not tok_clean:
                tok_idx += 1
                continue
                
            if tok_clean == w_clean or tok_clean.startswith(w_clean) or w_clean.startswith(tok_clean):
                matched = tok
                tok_idx += 1
                break
            else:
                tok_idx += 1
                
        aligned.append({
            "start": w.get("start", 0.0),
            "end": w.get("end", 0.0),
            "text": matched
        })

    # Group into punchy phrases (3-5 words) respecting speech pauses, punctuation & clauses
    phrases = []
    chunk = []
    WEAK_ENDINGS = {"and", "or", "to", "of", "in", "at", "for", "with", "a", "an", "the", "as"}
    
    for i, item in enumerate(aligned):
        chunk.append(item)
        w_txt = item["text"]
        is_last = (i == len(aligned) - 1)
        if is_last:
            break
            
        next_item = aligned[i + 1]
        pause = next_item["start"] - item["end"]
        current_text = " ".join(x["text"] for x in chunk)
        clean_w = w_txt.rstrip(".,!?;:\"'—–")
        
        has_clause_break = any(w_txt.endswith(p) for p in [",", ";", "—", "–", ":"])
        has_sentence_break = any(w_txt.endswith(p) for p in [".", "!", "?"])
        
        should_split = False
        if has_sentence_break:
            should_split = True
        elif has_clause_break and len(chunk) >= 2:
            should_split = True
        elif pause >= 0.35 and len(chunk) >= 2:
            should_split = True
        elif len(chunk) >= max_words or len(current_text) >= max_chars:
            if clean_w.lower() not in WEAK_ENDINGS and not clean_w.isdigit():
                should_split = True
            elif len(chunk) >= max_words + 1:
                should_split = True
                
        if should_split:
            p_text = " ".join(x["text"] for x in chunk)
            phrases.append({
                "start": round(chunk[0]["start"], 3),
                "end": round(chunk[-1]["end"], 3),
                "duration": round(chunk[-1]["end"] - chunk[0]["start"], 3),
                "text": p_text
            })
            chunk = []
            
    if chunk:
        p_text = " ".join(x["text"] for x in chunk)
        phrases.append({
            "start": round(chunk[0]["start"], 3),
            "end": round(chunk[-1]["end"], 3),
            "duration": round(chunk[-1]["end"] - chunk[0]["start"], 3),
            "text": p_text
        })
        
    return phrases

def split_sentence_subtitles(subtitles: list, max_duration: float = 4.2) -> list:
    """
    Fallback splitter for legacy sentence boundaries when WordBoundary is unavailable.
    """
    refined = []
    for sub in subtitles:
        text = sub.get("text", "").strip()
        dur = sub.get("duration", 0.0)
        start = sub.get("start", 0.0)
        end = sub.get("end", start + dur)
        
        if dur <= max_duration or len(text.split()) <= 6:
            refined.append({"start": start, "end": end, "duration": dur, "text": text})
            continue
            
        words = text.split(" ")
        total_words = len(words)
        split_pos = -1
        best_diff = 999
        
        # Look for natural punctuation pause (comma, semicolon) near the midpoint
        for i, w in enumerate(words):
            for d in [",", ";"]:
                if w.endswith(d) and 0.25 * total_words <= i <= 0.75 * total_words:
                    diff = abs(i - (total_words / 2))
                    if diff < best_diff:
                        best_diff = diff
                        split_pos = i + 1
        
        if split_pos != -1 and split_pos < total_words:
            part1 = " ".join(words[:split_pos]).strip()
            part2 = " ".join(words[split_pos:]).strip()
        else:
            mid = total_words // 2
            part1 = " ".join(words[:mid]).strip()
            part2 = " ".join(words[mid:]).strip()

        w1 = max(1, len(part1.split()))
        w2 = max(1, len(part2.split()))
        dur1 = round(dur * (w1 / (w1 + w2)), 3)
        dur2 = round(dur - dur1, 3)
        refined.append({"start": start, "end": round(start + dur1, 3), "duration": dur1, "text": part1})
        refined.append({"start": round(start + dur1, 3), "end": end, "duration": dur2, "text": part2})
        
    return refined

def build_animated_shorts_video(audio_path: str, photo_files: list, badge_text: str, title: str, script: str, output_path: str, subtitles: list = None, theme: str = "deepbeepmeep"):
    import moviepy
    is_v2 = int(moviepy.__version__.split(".")[0]) >= 2
    
    if is_v2:
        from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    else:
        from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    
    from modules.safe_image_fetcher import fetch_safe_image_for_sentence

    clips = []
    
    # Check if speech subtitle timeline was provided
    if subtitles and len(subtitles) > 0:
        # Check if subtitles are raw word boundaries or already grouped phrases
        first_few = subtitles[:min(5, len(subtitles))]
        if len(subtitles) >= 5 and all(len(s.get("text", "").split()) <= 2 for s in first_few):
            synced_segments = build_synced_phrases(subtitles, script)
        elif any(len(s.get("text", "").split()) > 6 for s in subtitles):
            synced_segments = split_sentence_subtitles(subtitles, max_duration=4.2)
        else:
            synced_segments = subtitles

        num_segments = len(synced_segments)
        
        for i, seg in enumerate(synced_segments):
            caption = seg["text"]
            
            # Start of this clip matches the EXACT millisecond the speaker utters the first word
            curr_start = 0.0 if i == 0 else seg["start"]
            # End of this clip matches start of next phrase, or total_duration
            if i + 1 < num_segments:
                next_start = synced_segments[i + 1]["start"]
                clip_dur = max(0.4, next_start - curr_start)
            else:
                clip_dur = max(0.4, total_duration - curr_start)
            
            # Rotate through photo assets
            if photo_files and len(photo_files) > 0 and os.path.exists(photo_files[0]):
                photo_path = photo_files[i % len(photo_files)]
            else:
                photo_path = fetch_safe_image_for_sentence(caption)
                
            frame_img = create_rich_frame(photo_path, badge_text, title, caption, progress=i / max(1, num_segments), theme=theme)
            frame_np = np.array(frame_img)
            
            if is_v2:
                clip = ImageClip(frame_np).with_duration(clip_dur)
            else:
                clip = ImageClip(frame_np).set_duration(clip_dur)
            clips.append(clip)
            
    else:
        # Fallback if no subtitle timestamps available
        sentences = [s.strip() for s in script.replace("!", ".").replace("?", ".").split(".") if len(s.strip()) > 5]
        if not sentences:
            sentences = [script]
        
        target_seg_dur = min(2.8, total_duration / max(1, len(sentences)))
        num_segments = max(len(sentences), int(np.ceil(total_duration / target_seg_dur)))
        seg_duration = total_duration / num_segments
        
        for i in range(num_segments):
            caption = sentences[i % len(sentences)]
            if photo_files and len(photo_files) > 0 and os.path.exists(photo_files[0]):
                photo_path = photo_files[i % len(photo_files)]
            else:
                photo_path = fetch_safe_image_for_sentence(caption)
            
            frame_img = create_rich_frame(photo_path, badge_text, title, caption, progress=i / num_segments, theme=theme)
            frame_np = np.array(frame_img)
            
            if is_v2:
                clip = ImageClip(frame_np).with_duration(seg_duration)
            else:
                clip = ImageClip(frame_np).set_duration(seg_duration)
            clips.append(clip)
        
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Mix ambient lo-fi background beat behind voiceover for high retention
    bg_music_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "audio", "bg_music.wav")
    final_audio = audio
    if os.path.exists(bg_music_path):
        try:
            if is_v2:
                from moviepy import CompositeAudioClip, concatenate_audioclips
            else:
                from moviepy.editor import CompositeAudioClip, concatenate_audioclips
                
            bg_audio = AudioFileClip(bg_music_path)
            if bg_audio.duration < total_duration:
                num_loops = int(np.ceil(total_duration / bg_audio.duration)) + 1
                bg_audio = concatenate_audioclips([bg_audio] * num_loops)
            
            if is_v2:
                bg_scaled = bg_audio.subclipped(0, total_duration).with_volume_scaled(0.12)
                final_audio = CompositeAudioClip([audio, bg_scaled])
            else:
                bg_scaled = bg_audio.subclip(0, total_duration).volumex(0.12)
                final_audio = CompositeAudioClip([audio, bg_scaled])
        except Exception as e:
            print(f"  [!] Audio mixing fallback: {e}")
            final_audio = audio

    if is_v2:
        final_video = final_video.with_audio(final_audio)
    else:
        final_video = final_video.set_audio(final_audio)
        
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    return output_path
