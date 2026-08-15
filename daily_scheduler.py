"""
daily_scheduler.py — Full End-to-End Daily 2 Shorts Generator & YouTube Uploader
Morning Short (08:30 AM IST): 100 Days CS Course Lesson (curriculum.json)
Evening Short (05:30 PM IST): Viral Technical Fun Facts & Trivia (tech_facts.json)
"""
import sys
import os
import json
import time
import argparse
import datetime
import asyncio
import edge_tts

# UTF-8 stdout encoding for Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRICULUM_PATH = os.path.join(os.path.dirname(__file__), "curriculum.json")
FACTS_PATH = os.path.join(os.path.dirname(__file__), "tech_facts.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

from modules.thumbnail_generator import create_shorts_thumbnail
from modules.shorts_animator import build_animated_shorts_video
from modules.youtube_uploader import upload_video

# Photo Asset Registry by Topic Domain
HARDWARE_PHOTOS = ["cs_photo_1_1080p.jpg", "cs_photo_2_1080p.jpg", "cs_photo_3_1080p.jpg"]
NETWORK_PHOTOS  = ["cs_photo_network_1080p.jpg", "cs_photo_3_1080p.jpg", "cs_photo_4_1080p.jpg"]
CODING_PHOTOS   = ["cs_photo_code_1080p.jpg", "cs_photo_3_1080p.jpg", "cs_photo_4_1080p.jpg"]
DEFAULT_PHOTOS  = ["cs_photo_1_1080p.jpg", "cs_photo_network_1080p.jpg", "cs_photo_code_1080p.jpg", "cs_photo_4_1080p.jpg"]

def select_photos_for_topic(title: str, tags: list = None) -> list:
    text = (title + " " + " ".join(tags or [])).lower()
    if any(k in text for k in ["internet", "network", "cloud", "web", "http", "ip", "cable"]):
        return NETWORK_PHOTOS
    elif any(k in text for k in ["code", "program", "python", "algorithm", "variable", "function", "software", "language"]):
        return CODING_PHOTOS
    elif any(k in text for k in ["cpu", "hardware", "computer", "ram", "memory", "input", "output", "chip", "drive", "mouse", "keyboard"]):
        return HARDWARE_PHOTOS
    return DEFAULT_PHOTOS

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_item(slot_name="Morning"):
    if slot_name.lower() == "morning":
        curriculum = load_json(CURRICULUM_PATH)
        topics = curriculum.get("topics", [])
        for t in topics:
            if not t.get("uploaded", False):
                return t, "course"
        return None, "course"
    else:
        facts_data = load_json(FACTS_PATH)
        facts = facts_data.get("facts", [])
        for f in facts:
            if not f.get("uploaded", False):
                return f, "fact"
        return None, "fact"

def mark_item_uploaded(item, item_type="course", video_id="uploaded"):
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if item_type == "course":
        curriculum = load_json(CURRICULUM_PATH)
        for t in curriculum.get("topics", []):
            if t.get("id") == item.get("id"):
                t["uploaded"] = True
                t["video_id"] = video_id
                t["upload_date"] = now_iso
                break
        save_json(CURRICULUM_PATH, curriculum)
    else:
        facts_data = load_json(FACTS_PATH)
        for f in facts_data.get("facts", []):
            if f.get("id") == item.get("id"):
                f["uploaded"] = True
                f["video_id"] = video_id
                f["upload_date"] = now_iso
                break
        save_json(FACTS_PATH, facts_data)

async def _gen_tts(text: str, voice: str, out_path: str):
    comm = edge_tts.Communicate(text, voice)
    await comm.save(out_path)

def generate_narration_audio(text: str, voice: str, out_path: str):
    asyncio.run(_gen_tts(text, voice, out_path))
    return out_path

def render_shorts_video(audio_path: str, thumbnail_path: str, output_video_path: str):
    import moviepy
    is_v2 = int(moviepy.__version__.split(".")[0]) >= 2
    
    if is_v2:
        from moviepy import ImageClip, AudioFileClip
        audio = AudioFileClip(audio_path)
        clip = ImageClip(thumbnail_path).with_duration(audio.duration).with_audio(audio)
        clip.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    else:
        from moviepy.editor import ImageClip, AudioFileClip
        audio = AudioFileClip(audio_path)
        clip = ImageClip(thumbnail_path).set_duration(audio.duration).set_audio(audio)
        clip.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    
    return output_video_path

def produce_and_upload_short(item, item_type="course", slot="Morning"):
    slot_id = item.get("id", "short")
    item_dir = os.path.join(OUTPUT_DIR, slot_id)
    os.makedirs(item_dir, exist_ok=True)

    if item_type == "course":
        day = item.get("day", 1)
        title = item.get("title", "Computer Science")
        tags = item.get("tags", ["Shorts", "ComputerScience", "LearnCS"])
        voice = "en-US-AvaNeural"
        badge = f"DAY {day} • 100 DAYS CS"
        video_title = f"Day {day}: {title} | 100 Days CS Course #Shorts"
        script = f"Welcome to Day {day} of the 100 Days Computer Science Course! Today's topic is {title}. Let's understand the core fundamentals step by step. Stay tuned and subscribe for daily CS lessons!"
        description = f"Day {day}: {title}\nPart of 100 Days Computer Science Course.\n\n#Shorts #ComputerScience #Tech #Education #LearnCoding"
    else:
        num = item.get("number", 1)
        title = item.get("title", "Tech Fun Fact")
        tags = item.get("tags", ["Shorts", "TechFacts", "Trivia"])
        voice = "en-US-ChristopherNeural"
        badge = f"TECH FACT #{num} 💡"
        video_title = f"Tech Fact #{num}: {title} 💡 #Shorts"
        script = item.get("script", f"Did you know this mind-blowing tech fact? {title}. Subscribe for daily technical trivia!")
        description = f"Tech Fact #{num}: {title}\nDaily Mind-Blowing Technical Trivia.\n\n#Shorts #TechFacts #Technology #FunFacts #Trivia"

    print(f"\n" + "=" * 60)
    print(f"  🎬 PRODUCING {slot.upper()} SHORT [{item_type.upper()}]")
    print(f"  📌 Title: {video_title}")
    print(f"  🗣️ Voice: {voice}")
    print(f"=" * 60)

    # 1. Generate Voiceover Audio
    audio_path = os.path.join(item_dir, "narration.mp3")
    print(f"  [1/4] Generating Neural Voiceover...")
    generate_narration_audio(script, voice, audio_path)

    # 2. Select Topic-Matched 1080p Photos
    chosen_photos = select_photos_for_topic(title, tags)

    # 3. Generate 9:16 High-Contrast Thumbnail
    thumb_path = os.path.join(item_dir, "thumbnail.jpg")
    print(f"  [2/4] Generating 9:16 Vertical Thumbnail...")
    from modules.shorts_animator import get_photo_path
    bg_photo = get_photo_path(chosen_photos[0])
    create_shorts_thumbnail(
        title=title,
        subtitle=item.get("module", "Daily Tech Insights"),
        badge_text=badge,
        bg_image_path=bg_photo,
        output_path=thumb_path
    )

    # 4. Render 9:16 Multi-Photo Animated Video (with large bold captions & Ken Burns motion)
    video_path = os.path.join(item_dir, "final_short.mp4")
    print(f"  [3/4] Rendering 9:16 Animated Multi-Photo Video...")
    build_animated_shorts_video(
        audio_path=audio_path,
        photo_files=chosen_photos,
        badge_text=badge,
        title=title,
        script=script,
        output_path=video_path
    )

    # 5. Upload to YouTube
    print(f"  [4/4] Uploading to YouTube Channel...")
    has_token = bool(os.environ.get("YOUTUBE_REFRESH_TOKEN"))
    if has_token:
        try:
            video_id = upload_video(
                video_path=video_path,
                thumbnail_path=thumb_path,
                title=video_title,
                description=description,
                tags=tags
            )
            print(f"\n  🎉 SUCCESS! Video Live at: https://www.youtube.com/watch?v={video_id}")
            mark_item_uploaded(item, item_type, video_id)
            return video_id
        except Exception as e:
            print(f"  [!] YouTube upload error: {e}")
            mark_item_uploaded(item, item_type, "upload_failed")
            return None
    else:
        print("  [!] YOUTUBE_REFRESH_TOKEN not found in environment. Video rendered locally.")
        mark_item_uploaded(item, item_type, "local_rendered")
        return "local_rendered"

def run_schedule(slot="both"):
    print(f"\n[+] Daily 2 Shorts Pipeline Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if slot in ["morning", "both"]:
        item, itype = get_next_item("Morning")
        if item:
            produce_and_upload_short(item, itype, "Morning")
        else:
            print("[i] All Morning CS Course lessons have been uploaded!")

    if slot in ["evening", "both"]:
        item, itype = get_next_item("Evening")
        if item:
            produce_and_upload_short(item, itype, "Evening")
        else:
            print("[i] All Evening Tech Fun Facts have been uploaded!")

def main():
    parser = argparse.ArgumentParser(description="Daily 2 Shorts Automation Pipeline")
    parser.add_argument("--slot", choices=["morning", "evening", "both"], default="both", help="Schedule slot to run")
    args = parser.parse_args()
    run_schedule(args.slot)

if __name__ == "__main__":
    main()
