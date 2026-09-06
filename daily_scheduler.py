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
HARDWARE_PHOTOS = ["cs_photo_4_1080p.jpg", "cs_photo_1_1080p.jpg", "cs_photo_2_1080p.jpg", "cs_photo_3_1080p.jpg"]
NETWORK_PHOTOS  = ["cs_photo_network_1080p.jpg", "cs_photo_3_1080p.jpg", "cs_photo_4_1080p.jpg"]
CODING_PHOTOS   = ["cs_photo_code_1080p.jpg", "cs_photo_4_1080p.jpg", "cs_photo_3_1080p.jpg"]
DEFAULT_PHOTOS  = ["cs_photo_4_1080p.jpg", "cs_photo_1_1080p.jpg", "cs_photo_network_1080p.jpg", "cs_photo_code_1080p.jpg"]

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

VIRAL_COURSE_LESSONS = {
    1: "A computer is an electronic machine that takes raw input data, processes it at incredible speeds, and outputs meaningful results. It follows the Input, Process, Output, and Storage cycle. The CPU acts as the brain, RAM provides lightning-fast temporary memory, and hard drives store your data permanently. Underneath it all, computers operate entirely on binary code—zeros and ones turning electrical switches on and off billions of times every second!",
    2: "The history of computing started with mechanical calculators like Charles Babbage's Analytical Engine in the 1800s. In 1945, the world's first electronic general-purpose computer, ENIAC, was built—it weighed 30 tons and occupied an entire room! The invention of the silicon transistor and microchip revolutionized technology, shrinking massive room-sized supercomputers into the powerful smartphones we carry in our pockets today!",
    13: "Stop writing Python variables until you know what actually happens in memory! In Python, variables aren't storage boxes—they are memory labels pointing to objects in your computer's RAM. When you type x equals 10, Python creates an integer object and slaps the label x onto it. Change x to 20, and the label simply points to a brand new object! Follow for Day 14!",
    14: "Why does Python's input function break almost every beginner's project? Because input always captures your data as a text string, not a number! If you type 5 plus 5, Python gives you 55 instead of 10! You must wrap it in an int or float function to perform real mathematical calculations! Follow for Day 15!",
    15: "Did you know Python has two completely different ways to divide numbers? A single forward slash gives you a floating point decimal, but a double slash performs floor division, rounding down and chopping off decimals entirely! Master these operators to prevent silent bugs in your algorithms! Follow for Day 16!",
    16: "This 1 logic trick will make your Python code 10 times cleaner! Instead of writing messy nested if statements, Python evaluates conditions from top to bottom with elif and stops the moment it finds a match! Structure your most frequent conditions first for lightning-fast execution! Follow for Day 17!",
    17: "How do Python for loops actually work under the hood? Python doesn't use simple index counters like C++ or Java—it uses iterators! When you loop over a list or string, Python automatically requests the next element until the sequence is exhausted! Follow for Day 18!",
    18: "The most dangerous bug in computer programming is the infinite while loop! If your loop condition never evaluates to False, your CPU core gets pegged at 100% until the program crashes. Always ensure your while loop has a guaranteed exit condition or break statement! Follow for Day 19!",
    19: "Write once, execute everywhere! Functions are the building blocks of clean software engineering. Instead of copy-pasting code, bundle your logic into a reusable function with inputs and outputs to eliminate bugs instantly! Follow for Day 20!",
    20: "Why did Python throw an UnboundLocalError? Because Python uses the LEGB rule for variable scope: Local, Enclosing, Global, and Built-in! A variable defined inside a function does not exist outside it. Master scope to keep your code bulletproof! Follow for Day 21!"
}

VIRAL_TITLES = {
    13: "How Python ACTUALLY Stores Data in RAM 🤯 (Day 13/100) #Shorts #Python #Coding",
    14: "The 1 Python input() Mistake Everyone Makes! 🐍 (Day 14) #Shorts #Python #Coding",
    15: "Why Python Does Math Differently Than You Think ⚡ (Day 15) #Shorts #Coding",
    16: "Stop Writing Messy If-Else Statements in Python! 🚀 (Day 16) #Shorts #Python",
    17: "How Python For Loops WORK Under The Hood 🔁 (Day 17) #Shorts #Coding",
    18: "The Most Dangerous Bug in Python Programming ⚠️ (Day 18) #Shorts #Python",
    19: "Write Python Code 10x Faster With Functions 💡 (Day 19) #Shorts #Coding",
    20: "Why Python Throws UnboundLocalError! 🧠 (Day 20) #Shorts #Python #Coding"
}

def get_course_script(day: int, title: str, module: str, tags: list) -> str:
    if day in VIRAL_COURSE_LESSONS:
        return VIRAL_COURSE_LESSONS[day]
    # High-curiosity dynamic hook (NO boring lectures!)
    clean = title.replace("in Python", "").strip()
    return (
        f"Here is the one concept about {clean} that every programmer MUST know! "
        f"In computer science, {clean} controls how your system processes information and executes logic. "
        f"Understanding how {clean} interacts with your CPU and memory separates beginner coders from senior software engineers. "
        f"Save this video and follow for Day {day + 1}!"
    )

def generate_viral_title(day: int, title: str, itype: str = "course") -> str:
    if itype == "course":
        if day in VIRAL_TITLES:
            return VIRAL_TITLES[day]
        clean_title = title.replace("in Python", "").replace("–", "").replace("-", "").strip()
        return f"{clean_title}: What They Don't Teach Beginners 🤯 (Day {day}/100) #Shorts #Python #Coding"
    else:
        clean = title.replace("?", "").strip()
        return f"Mind-Blowing Tech Fact: {clean} 💡 #Shorts #TechFacts #Technology"

def produce_and_upload_short(item, item_type="course", slot="Morning"):
    slot_id = item.get("id", "short")
    item_dir = os.path.join(OUTPUT_DIR, slot_id)
    os.makedirs(item_dir, exist_ok=True)

    if item_type == "course":
        day = item.get("day", 1)
        title = item.get("title", "Computer Science")
        module = item.get("module", "Computer Science")
        tags = ["Shorts", "Python", "Coding", "Programming", "ComputerScience", "LearnToCode", "Tech", "Developer"]
        voice = "en-US-AvaNeural"
        badge = f"DAY {day} • 100 DAYS CS"
        video_title = generate_viral_title(day, title, "course")
        script = get_course_script(day, title, module, tags)
        description = (
            f"{video_title}\n\n"
            f"100 Days of Computer Science & Python Mastery.\n"
            f"Learn how computers, software, and algorithms work under the hood!\n\n"
            f"#Shorts #Python #Coding #Programming #ComputerScience #Tech #SoftwareEngineer #LearnToCode"
        )
    else:
        num = item.get("number", 1)
        title = item.get("title", "Tech Fun Fact")
        tags = ["Shorts", "TechFacts", "Technology", "Trivia", "DidYouKnow", "Science", "Tech"]
        voice = "en-US-ChristopherNeural"
        badge = f"TECH FACT #{num} 💡"
        video_title = generate_viral_title(num, title, "fact")
        raw_script = item.get("script", title)
        hook = item.get("hook", "Did you know this mind-blowing tech secret?")
        script = f"{hook} {raw_script} Subscribe for more daily tech secrets!"
        description = (
            f"{video_title}\n\n"
            f"Daily Mind-Blowing Technical Secrets and Trivia.\n\n"
            f"#Shorts #TechFacts #Technology #FunFacts #Trivia #Science #Tech"
        )

    print(f"\n" + "=" * 60)
    print(f"  🎬 PRODUCING {slot.upper()} SHORT [{item_type.upper()}]")
    print(f"  📌 Title: {video_title}")
    print(f"  🗣️ Voice: {voice}")
    print(f"=" * 60)

    # 1. Generate Voiceover Audio
    audio_path = os.path.join(item_dir, "narration.mp3")
    print(f"  [1/4] Generating Neural Voiceover...")
    generate_narration_audio(script, voice, audio_path)

    # 2. Select Topic-Matched Images (Custom Vault Images -> Safe Stock -> Curated Fallback)
    from modules.custom_vault_loader import get_images_for_short
    chosen_photos = get_images_for_short(item, item_type=item_type)

    # 3. Generate 9:16 High-Contrast Thumbnail
    thumb_path = os.path.join(item_dir, "thumbnail.jpg")
    print(f"  [2/4] Generating 9:16 Vertical Thumbnail...")
    bg_photo = chosen_photos[0] if chosen_photos else None
    create_shorts_thumbnail(
        title=title,
        subtitle=item.get("module", "Daily Tech Insights"),
        badge_text=badge,
        bg_image_path=bg_photo,
        output_path=thumb_path
    )

    # 4. Render 9:16 Multi-Photo Animated Video
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
            print(f"  [!] Item '{title}' remains un-uploaded and will retry on next run.")
            raise e
    else:
        print("  [!] YOUTUBE_REFRESH_TOKEN not found in environment.")
        raise ValueError("Missing YOUTUBE_REFRESH_TOKEN secret in environment.")

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
