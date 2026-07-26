"""
modules/thumbnail_generator.py
Creates a professional 1280x720 anime-style YouTube thumbnail.
Generates an topic-relevant anime background illustration, crops/resizes it,
and overlays a readable translucent metadata panel, day badge, and level tag.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720

LEVEL_COLORS = {
    "Beginner":     (34, 197, 94),    # green
    "Intermediate": (250, 204, 21),   # amber
    "Advanced":     (239, 68, 68),    # red
}


def _load_font(paths, name_candidates, size):
    for base in paths:
        for name in name_candidates:
            try:
                return ImageFont.truetype(os.path.join(base, name), size)
            except Exception:
                pass
    return ImageFont.load_default()


def _wrap(draw, text, x, y, font, color, max_w):
    lh = font.size + 10
    words = text.split()
    line = []
    lines_drawn = 0
    for word in words:
        line.append(word)
        bb = draw.textbbox((0, 0), " ".join(line), font=font)
        if bb[2] > max_w and len(line) > 1:
            line.pop()
            if lines_drawn < 3:
                draw.text((x, y), " ".join(line), font=font, fill=color)
            y += lh
            lines_drawn += 1
            line = [word]
    if line and lines_drawn < 3:
        draw.text((x, y), " ".join(line), font=font, fill=color)
        y += lh
    return y


def create_thumbnail(topic: dict, output_dir: str) -> str:
    """
    Generate a professional anime-style YouTube thumbnail.
    Downloads an anime illustration for the background and overlays a formatted metadata card.
    """
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "thumbnail.jpg")

    font_paths = [
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/truetype/liberation/",
        "C:/Windows/Fonts/",
        os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts") + "/",
    ]
    bold_names    = ["DejaVuSans-Bold.ttf",    "LiberationSans-Bold.ttf", "arialbd.ttf", "seguib.ttf"]
    regular_names = ["DejaVuSans.ttf",         "LiberationSans-Regular.ttf", "arial.ttf", "segoeui.ttf"]

    f_title  = _load_font(font_paths, bold_names,    56)
    f_sub    = _load_font(font_paths, regular_names, 28)
    f_badge  = _load_font(font_paths, bold_names,    22)
    f_small  = _load_font(font_paths, regular_names, 20)
    f_module = _load_font(font_paths, bold_names,    24)

    # ── 1. Fetch / Render Background Image ───────────────────────────────────
    bg_path = os.path.join(output_dir, "thumbnail_raw_bg.jpg")
    from config import IMAGE_PROVIDER

    if IMAGE_PROVIDER == "local":
        print("  [thumbnail] [LOCAL MODEL] Using local clean gradient background for thumbnail.")
        img = Image.new("RGB", (W, H), (15, 20, 40))
        fallback_draw = ImageDraw.Draw(img)
        for y in range(H):
            t = y / H
            r = int(15  + t * 12)
            g = int(20  + t * 15)
            b = int(40  + t * 20)
            fallback_draw.line([(0, y), (W, y)], fill=(r, g, b))
    else:
        thumbnail_prompt = (
            f"An eye-catching, child-friendly educational illustration representing: {topic['title']}, "
            f"vibrant colors, clean vector art, G-rated, safe for work"
        )
        try:
            from modules.image_generator import generate_image
            generate_image(thumbnail_prompt, bg_path)
            img = Image.open(bg_path)
        except Exception as e:
            print(f"  [thumbnail] Warning: Failed to generate background image ({e}). Using gradient background.")
            img = Image.new("RGB", (W, H), (15, 20, 40))
            fallback_draw = ImageDraw.Draw(img)
            for y in range(H):
                t = y / H
                r = int(15  + t * 12)
                g = int(20  + t * 15)
                b = int(40  + t * 20)
                fallback_draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Ensure background image is sized to 1280x720
    if img.size != (W, H):
        # Crop and resize
        img = img.resize((W, H), Image.Resampling.LANCZOS)

    # ── 2. Create Translucent Text Overlay Card ──────────────────────────────
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Render left-side metadata dark card (slate base with 80% opacity)
    card_box = [30, 30, 620, H - 30]
    overlay_draw.rounded_rectangle(card_box, radius=24, fill=(15, 23, 42, 200))
    
    # Outer accent border on card
    overlay_draw.rounded_rectangle(card_box, radius=24, outline=(99, 102, 241, 255), width=2)
    
    # Composite card overlay onto the background image
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # ── 3. Draw Text Overlays on Composited Image ─────────────────────────────
    # Day badge inside the card
    day = topic.get("day", 1)
    badge_text = f"DAY {day}"
    draw.rounded_rectangle([60, 60, 180, 98], radius=15, fill=(99, 102, 241))
    draw.text((75, 68), badge_text, font=f_badge, fill=(255, 255, 255))

    # Module label
    module = topic.get("module", "General")
    draw.text((60, 118), module.upper(), font=f_module, fill=(99, 102, 241))

    # Topic Title (max width fits inside left card: 560px)
    title_y = _wrap(draw, topic["title"], 60, 170, f_title, (255, 255, 255), 520)

    # Decorative divider
    draw.rectangle([60, title_y + 16, 200, title_y + 20], fill=(99, 102, 241))

    # Subtitle descriptor
    draw.text((60, title_y + 36), "5-min explainer lesson", font=f_sub, fill=(148, 163, 184))

    # Channel branding at bottom of card
    channel = topic.get("channel", "Daily Explainer")
    draw.text((60, H - 75), f"🖥  {channel}", font=f_small, fill=(99, 102, 241))

    # Level badge (drawn on bottom right corner, outside the card)
    level = topic.get("level", "Beginner")
    lc    = LEVEL_COLORS.get(level, (99, 102, 241))
    lbb   = draw.textbbox((0, 0), f"● {level}", font=f_badge)
    lw    = lbb[2] - lbb[0] + 24
    lx    = W - lw - 40
    
    # Drawing a level card on bottom-right to stand out on top of raw background
    level_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    level_draw = ImageDraw.Draw(level_overlay)
    level_draw.rounded_rectangle(
        [lx, H - 78, lx + lw, H - 42], 
        radius=12, 
        fill=(15, 23, 42, 220), 
        outline=lc, 
        width=2
    )
    
    img = Image.alpha_composite(img.convert("RGBA"), level_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text((lx + 12, H - 72), f"● {level}", font=f_badge, fill=lc)

    # ── 4. Save and Cleanup ──────────────────────────────────────────────────
    img.save(out_path, "JPEG", quality=95, optimize=True)
    print(f"  [thumbnail] Saved → {out_path}")
    
    # Clean raw background
    if os.path.exists(bg_path):
        os.remove(bg_path)
        
    return out_path
