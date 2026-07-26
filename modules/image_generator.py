"""
modules/image_generator.py
Handles visual asset creation using either an ONLINE AI model (Pollinations.ai with strict safety filters)
or a LOCAL procedural renderer (Pillow-based chalkboard & diagram graphics). Keeps online and local models strictly separated.
"""
import os
import time
import re
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
from config import VISUAL_STYLE, IMAGE_PROVIDER, SAFE_MODE

# Negative prompt to strictly block adult, uncensored, or inappropriate visual output when using online model
STRICT_NEGATIVE_PROMPT = (
    "nsfw, nude, adult, explicit, inappropriate, sexual, cleavage, bikini, naked, undressed, "
    "violence, gore, suggestive, seductive, revealing clothing, realistic human body, NSFW"
)

# Safety prefix added to every single online visual prompt
SAFETY_PREFIX = "G-rated, child friendly, 3rd grade educational content, safe for work, SFW, clean cartoon, wholesome, fully clothed, modest"

def _sanitize_prompt(text: str) -> str:
    """Removes any potentially ambiguous or inappropriate words from prompts."""
    banned_words = [
        "sexy", "nude", "naked", "18-year-old", "girl", "bikini", "lingerie", 
        "cleavage", "provocative", "sensual", "unclothed", "strip", "erotic"
    ]
    cleaned = text
    for word in banned_words:
        cleaned = re.sub(r'\b' + re.escape(word) + r'\b', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def generate_image(character_pose: str, output_path: str, retries: int = 3) -> str:
    """
    Generate a base blackboard classroom scene.
    Uses LOCAL procedural rendering if IMAGE_PROVIDER == 'local', else ONLINE model.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if IMAGE_PROVIDER == "local":
        print(f"  [image_gen] [LOCAL MODEL] Rendering clean blackboard classroom scene using local Pillow graphics.")
        return _render_procedural_scene(character_pose, output_path)

    # ONLINE MODEL
    clean_pose = _sanitize_prompt(character_pose)
    full_prompt = (
        f"{SAFETY_PREFIX}, cute cartoon teacher character on the left side of the screen, {clean_pose}, "
        f"pointing to a large blank empty green chalkboard on the right, colorful 3rd-grade classroom background, "
        f"blank chalkboard, no text on board, clean chalkboard, {VISUAL_STYLE.strip()}"
    )
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    encoded_negative = urllib.parse.quote(STRICT_NEGATIVE_PROMPT)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1920&height=1080&nologo=true&private=true&enhance=false&safe=true"
        f"&negative={encoded_negative}&model=flux"
    )
    
    print(f"  [image_gen] [ONLINE MODEL] Requesting safe base scene: '{clean_pose[:60]}...'")
    return _download_file(url, output_path, retries)


def generate_diagram(diagram_prompt: str, output_path: str, retries: int = 3) -> str:
    """
    Generate a simple cartoon sticker diagram/illustration on a white background.
    Uses LOCAL procedural rendering if IMAGE_PROVIDER == 'local', else ONLINE model.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if IMAGE_PROVIDER == "local":
        print(f"  [image_gen] [LOCAL MODEL] Rendering procedural sticker diagram using local Pillow graphics.")
        return _render_procedural_diagram(diagram_prompt, output_path)

    # ONLINE MODEL
    clean_diagram = _sanitize_prompt(diagram_prompt)
    full_prompt = (
        f"{SAFETY_PREFIX}, {clean_diagram}, cute cartoon sticker style, white background, "
        f"simple educational icon, vector illustration, wholesome"
    )
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    encoded_negative = urllib.parse.quote(STRICT_NEGATIVE_PROMPT)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=512&height=512&nologo=true&private=true&enhance=false&safe=true"
        f"&negative={encoded_negative}&model=flux"
    )
    
    print(f"  [image_gen] [ONLINE MODEL] Requesting safe diagram sticker: '{clean_diagram[:60]}...'")
    return _download_file(url, output_path, retries)


def _download_file(url: str, output_path: str, retries: int) -> str:
    """Helper to download a file from a URL with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=45) as response:
                data = response.read()
                
            with open(output_path, "wb") as f:
                f.write(data)
                
            print(f"  [image_gen] Safe image downloaded successfully → {output_path}")
            return output_path
            
        except Exception as e:
            print(f"  [image_gen] Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(3)
            else:
                raise RuntimeError(f"Failed to fetch image after {retries} attempts: {e}")


def _render_procedural_scene(pose_text: str, output_path: str) -> str:
    """Renders a clean, high-resolution 1920x1080 chalkboard classroom scene locally using Pillow."""
    img = Image.new("RGB", (1920, 1080), (240, 243, 246))
    draw = ImageDraw.Draw(img)
    
    # Draw classroom wall background with subtle gradient
    for y in range(1080):
        t = y / 1080
        r = int(245 - t * 15)
        g = int(247 - t * 15)
        b = int(250 - t * 15)
        draw.line([(0, y), (1920, y)], fill=(r, g, b))
        
    # Draw wooden floor (bottom 180px)
    draw.rectangle([0, 900, 1920, 1080], fill=(217, 155, 102))
    draw.rectangle([0, 900, 1920, 910], fill=(185, 125, 75))
    
    # Draw large green chalkboard (x=880 to 1840, y=100 to 860)
    wood_frame = (140, 90, 50)
    draw.rounded_rectangle([860, 80, 1860, 880], radius=15, fill=wood_frame)
    draw.rounded_rectangle([880, 100, 1840, 860], radius=10, fill=(35, 75, 55))
    
    # Draw chalk tray
    draw.rectangle([860, 875, 1860, 895], fill=(160, 110, 65))
    draw.rectangle([920, 880, 980, 888], fill=(255, 255, 255))   # White chalk
    draw.rectangle([1000, 880, 1060, 888], fill=(253, 224, 71)) # Yellow chalk
    draw.rectangle([1100, 878, 1180, 889], fill=(120, 80, 50))  # Eraser
    
    # Draw cute cartoon teacher figure on the left (x=100 to 800)
    # Teacher body / desk illustration using clean shapes
    draw.ellipse([300, 200, 540, 440], fill=(255, 220, 190))     # Head
    draw.ellipse([320, 240, 520, 420], fill=(255, 225, 200))
    # Hair
    draw.ellipse([290, 170, 550, 310], fill=(70, 50, 40))
    # Glasses
    draw.ellipse([340, 280, 410, 330], outline=(40, 40, 40), width=4)
    draw.ellipse([430, 280, 500, 330], outline=(40, 40, 40), width=4)
    draw.line([(410, 305), (430, 305)], fill=(40, 40, 40), width=4)
    # Smile
    draw.arc([390, 340, 450, 390], start=10, end=170, fill=(200, 60, 60), width=4)
    # Clothes (sweater)
    draw.rounded_rectangle([250, 430, 590, 900], radius=40, fill=(59, 130, 246))
    draw.polygon([(420, 430), (370, 520), (470, 520)], fill=(255, 255, 255))
    # Tie / Collar
    draw.polygon([(410, 470), (430, 470), (425, 580), (420, 470)], fill=(239, 68, 68))
    # Arm pointing to the board
    draw.line([(550, 500), (840, 300)], fill=(59, 130, 246), width=36)
    draw.ellipse([820, 280, 860, 320], fill=(255, 220, 190))
    
    img.save(output_path, "JPEG", quality=95)
    return output_path


def _render_procedural_diagram(prompt_text: str, output_path: str) -> str:
    """Renders a clean, cute 512x512 educational sticker icon locally using Pillow."""
    img = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Cute sticker border
    draw.rounded_rectangle([20, 20, 492, 492], radius=40, fill=(240, 249, 255), outline=(186, 230, 253), width=6)
    
    # Draw a cute lightbulb / star icon
    draw.ellipse([156, 100, 356, 300], fill=(254, 240, 138), outline=(234, 179, 8), width=8)
    draw.polygon([(216, 280), (296, 280), (286, 360), (226, 360)], fill=(203, 213, 225), outline=(100, 116, 139), width=6)
    
    # Light rays
    draw.line([(256, 40), (256, 80)], fill=(234, 179, 8), width=8)
    draw.line([(100, 150), (135, 170)], fill=(234, 179, 8), width=8)
    draw.line([(412, 150), (377, 170)], fill=(234, 179, 8), width=8)
    
    # Cute face on lightbulb
    draw.ellipse([210, 180, 230, 210], fill=(51, 65, 85))
    draw.ellipse([282, 180, 302, 210], fill=(51, 65, 85))
    draw.arc([236, 215, 276, 245], start=0, end=180, fill=(225, 29, 72), width=6)
    
    img.convert("RGB").save(output_path, "PNG")
    return output_path
