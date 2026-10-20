"""
modules/deepbeepmeep_engine.py — DeepBeepMeep / Wan2GP 3D Character & Motion Engine
Integrates the signature DeepBeepMeep (Wan2GP) AI cartoon style into the YouTube Shorts pipeline:
1. Wan2GP Structured Prompt Enhancer (Subject + Environment + Motion + Camera + Lighting)
2. Wan2GP Batch Prompt Exporter (multi-line format compatible with Wan2GP prompt box)
3. 3D Cartoon Mascot Asset Registry & Fallback Manager
4. Gradio / Remote Wan2GP API Hook (optional local GPU connection)
"""
import os
import re
from typing import List, Dict, Any

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "photos")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

# DeepBeepMeep 3D Cartoon Asset Registry
DEEPBEEPMEEP_ASSETS = [
    "cs_deepbeepmeep_mascot_desk.jpg",
    "cs_deepbeepmeep_mascot_pointing.jpg",
    "cs_deepbeepmeep_mascot_server.jpg",
    "cs_deepbeepmeep_mascot_chip.jpg",
    "cs_photo_developer_1080p.jpg",
    "cs_photo_ai_neural_1080p.jpg"
]

def format_wan2gp_prompt(topic: str, scene_context: str = "", character_action: str = "") -> str:
    """
    Constructs a cinematic 3D animation prompt adhering strictly to DeepBeepMeep's
    Wan2GP prompt syntax:
    Subject + Environment + Motion + Camera Motion + Lighting/Aesthetic
    """
    subject = "3D Pixar-style friendly orange tech mascot character wearing studio headphones"
    
    # Topic-specific actions and environment
    clean_topic = topic.replace("in Python", "").strip()
    
    if not character_action:
        if any(k in clean_topic.lower() for k in ["memory", "ram", "storage", "speed", "fast"]):
            character_action = "excitedly holding a glowing holographic memory block with data flowing through it"
            environment = "high-tech futuristic cyber laboratory with neon purple and cyan ambient glow"
            camera = "cinematic slow push-in, low-angle 3/4 perspective"
        elif any(k in clean_topic.lower() for k in ["cpu", "chip", "hardware", "byte", "bits"]):
            character_action = "inspecting an intricate glowing golden microchip pulsating with electric circuit light"
            environment = "sleek sci-fi tech workstation surrounded by floating interactive holographic displays"
            camera = "smooth 360-degree subtle orbit camera movement"
        elif any(k in clean_topic.lower() for k in ["loop", "function", "code", "python", "syntax", "string"]):
            character_action = "gesturing enthusiastically at floating neon Python code snippets and algorithms"
            environment = "cozy dark cyber developer room with multi-monitor workstation and ambient warm neon lights"
            camera = "slow cinematic tracking shot, subtle parallax depth"
        else:
            character_action = f"explaining the core concepts of {clean_topic} with an enthusiastic, confident expression"
            environment = "futuristic interactive digital classroom with floating holographic charts and diagrams"
            camera = "smooth push-in from medium shot to close-up"
    else:
        environment = "futuristic cyber workstation with glowing holographic monitors"
        camera = "slow cinematic push-in tracking shot"

    style_tokens = (
        "3D CGI animation, Pixar Disney aesthetic, Octane render, raytracing, "
        "volumetric studio lighting, subsurface scattering, vibrant saturated colors, 8k masterpiece, 9:16 portrait vertical"
    )

    return f"{subject}, {character_action}, {environment}, {camera}, {style_tokens}"

def export_wan2gp_batch_file(item: Dict[str, Any], item_type: str = "course", output_path: str = None) -> str:
    """
    Exports a batch generation prompt file matching DeepBeepMeep's Wan2GP prompt box rules:
    - '#' lines are comments
    - '!' lines are macros/parameters
    - Plain lines are individual scene prompts (1 video per line)
    """
    if output_path is None:
        slot_id = item.get("id", "short")
        target_dir = os.path.join(OUTPUT_DIR, slot_id)
        os.makedirs(target_dir, exist_ok=True)
        output_path = os.path.join(target_dir, "wan2gp_batch_prompts.txt")

    title = item.get("title", "Computer Science")
    day_or_num = item.get("day", item.get("number", 1))
    badge = f"DAY {day_or_num}" if item_type == "course" else f"FACT #{day_or_num}"

    lines = [
        f"# =================================================================",
        f"# DeepBeepMeep Wan2GP Batch Prompt — {badge}: {title}",
        f"# Paste into Wan2GP WebUI prompt box for automated overnight batching",
        f"# =================================================================",
        f"!width 1080",
        f"!height 1920",
        f"!fps 24",
        f"!steps 30",
        f"!motion_scale 1.15",
        f"",
        f"# Shot 1: Opening Hook Scene",
        format_wan2gp_prompt(title, character_action="looking at camera with excited, mind-blown expression pointing at glowing title"),
        f"",
        f"# Shot 2: Deep-Dive Technical Explanation",
        format_wan2gp_prompt(title, character_action="breaking down the concept with glowing holographic diagrams in mid-air"),
        f"",
        f"# Shot 3: Benchmark / Performance Comparison",
        format_wan2gp_prompt(title, character_action="showing lightning-fast CPU/memory performance chart with blue neon speed lines"),
        f"",
        f"# Shot 4: Outro & Call to Action",
        format_wan2gp_prompt(title, character_action="waving enthusiastically with a subscribe banner glowing in the background")
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  [DeepBeepMeep] Wan2GP batch prompt file saved → {output_path}")
    return output_path

def get_deepbeepmeep_photos(item: Dict[str, Any] = None, item_type: str = "course") -> List[str]:
    """
    Returns a list of 1080x1920 3D cartoon mascot visual assets for the current short.
    Uses dedicated DeepBeepMeep 3D CGI assets if available, falling back to curated tech photos.
    """
    available_photos = []
    
    # 1. Check for dedicated DeepBeepMeep 3D assets in assets/photos
    for filename in DEEPBEEPMEEP_ASSETS:
        full_path = os.path.join(PHOTOS_DIR, filename)
        if os.path.exists(full_path):
            available_photos.append(full_path)

    # 2. Check custom vault for 3D assets
    vault_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "custom_vault")
    if os.path.exists(vault_dir):
        for f in os.listdir(vault_dir):
            if f.lower().endswith((".jpg", ".png", ".webp")) and any(k in f.lower() for k in ["deep", "mascot", "3d", "wan"]):
                p = os.path.join(vault_dir, f)
                if p not in available_photos:
                    available_photos.append(p)

    # 3. Fallback to existing high-res tech photos if 3D assets not yet on disk
    if len(available_photos) < 2:
        for backup in ["cs_photo_developer_1080p.jpg", "cs_photo_ai_neural_1080p.jpg", "cs_photo_supercomputer_1080p.jpg", "cs_photo_code_1080p.jpg"]:
            bp = os.path.join(PHOTOS_DIR, backup)
            if os.path.exists(bp) and bp not in available_photos:
                available_photos.append(bp)

    return available_photos
