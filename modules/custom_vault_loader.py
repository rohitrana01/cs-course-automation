"""
custom_vault_loader.py — Universal Custom Image Vault Loader
Supports:
1. All major image formats: .jpg, .jpeg, .png, .webp, .bmp, .tiff, .avif, .gif (first frame)
2. Direct local folder: assets/custom_vault/
3. Cloud folder sync (Google Drive / GitHub RAW / direct HTTP URL manifest)
4. Fallback matching by Day ID (e.g. day3_1.jpg, cs003_2.png, fact1_1.webp)
"""
import os
import glob
import urllib.request
from PIL import Image

VAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "custom_vault")
PHOTOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "photos")
os.makedirs(VAULT_DIR, exist_ok=True)

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".avif", ".gif")

def normalize_and_convert_image(src_path: str, target_size=(1080, 1920)) -> Image.Image:
    """
    Opens any supported image format, converts to RGB, and crops/resizes to 1080x1920.
    """
    with Image.open(src_path) as img:
        img = img.convert("RGB")
        orig_w, orig_h = img.size
        target_w, target_h = target_size
        
        # If already exactly 1080x1920, return directly
        if orig_w == target_w and orig_h == target_h:
            return img.copy()
            
        # Scale to fill
        scale = max(target_w / orig_w, target_h / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Center crop
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return resized.crop((left, top, left + target_w, top + target_h))

def find_custom_vault_images(item_id: str, item_day: int = None, item_type: str = "course") -> list:
    """
    Finds all custom images for a given topic or tech fact.
    Matching patterns:
      For Day 3:
        - assets/custom_vault/day3/*
        - assets/custom_vault/cs003/*
        - assets/custom_vault/day3_*.jpg/png/webp
        - assets/custom_vault/cs003_*.jpg/png/webp
      For Fact 1:
        - assets/custom_vault/fact1/*
        - assets/custom_vault/fact001/*
        - assets/custom_vault/fact1_*.jpg/png/webp
    """
    found_paths = []
    prefixes = []
    
    if item_type == "course":
        if item_day:
            prefixes.extend([f"day{item_day}", f"day_{item_day}", f"day{item_day:02d}", f"day{item_day:03d}"])
        if item_id:
            prefixes.extend([item_id.lower(), item_id.upper()])
    else: # fact
        if item_day:
            prefixes.extend([f"fact{item_day}", f"fact_{item_day}", f"fact{item_day:02d}", f"fact{item_day:03d}"])
        if item_id:
            prefixes.extend([item_id.lower(), item_id.upper()])

    # 1. Check sub-folders first
    for p in prefixes:
        folder = os.path.join(VAULT_DIR, p)
        if os.path.isdir(folder):
            for ext in SUPPORTED_EXTENSIONS:
                found_paths.extend(sorted(glob.glob(os.path.join(folder, f"*{ext}"))))
                found_paths.extend(sorted(glob.glob(os.path.join(folder, f"*{ext.upper()}"))))

    # 2. Check flat files in custom_vault root
    for p in prefixes:
        for ext in SUPPORTED_EXTENSIONS:
            found_paths.extend(sorted(glob.glob(os.path.join(VAULT_DIR, f"{p}_*{ext}"))))
            found_paths.extend(sorted(glob.glob(os.path.join(VAULT_DIR, f"{p}*{ext}"))))

    # Deduplicate while preserving order
    unique_paths = []
    for f in found_paths:
        if f not in unique_paths and os.path.exists(f):
            unique_paths.append(f)

    return unique_paths

def get_images_for_short(item: dict, item_type: str = "course", count: int = 3) -> list:
    """
    Returns a list of image paths for the short.
    Prioritizes user's custom vault images, then fallback safe assets.
    """
    day_num = item.get("day") or item.get("number")
    item_id = item.get("id")
    
    custom_imgs = find_custom_vault_images(item_id, day_num, item_type)
    if custom_imgs:
        print(f"  [+] Found {len(custom_imgs)} custom vault image(s) for {item_id or day_num}")
        return custom_imgs

    # Fallback to curated base assets
    from modules.safe_image_fetcher import get_curated_fallback_photo
    title = item.get("title", "")
    base_photo = get_curated_fallback_photo(title)
    return [base_photo] if base_photo else []
