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
        
        # Infinite Auto-Recycle: never stop uploading evening facts!
        print("  [*] All Tech Facts uploaded! Automatically recycling queue from Fact #1...")
        for f in facts:
            f["uploaded"] = False
            f.pop("video_id", None)
            f.pop("upload_date", None)
        save_json(FACTS_PATH, facts_data)
        return facts[0], "fact"

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

async def _gen_tts_with_subtitles(text: str, voice: str, out_path: str):
    comm = edge_tts.Communicate(text, voice)
    subtitles = []
    with open(out_path, "wb") as f_out:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f_out.write(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                start_s = chunk["offset"] / 10_000_000.0
                dur_s = chunk["duration"] / 10_000_000.0
                subtitles.append({
                    "start": round(start_s, 3),
                    "end": round(start_s + dur_s, 3),
                    "duration": round(dur_s, 3),
                    "text": chunk["text"].strip()
                })
    return subtitles

def generate_narration_audio(text: str, voice: str, out_path: str):
    subtitles = asyncio.run(_gen_tts_with_subtitles(text, voice, out_path))
    return out_path, subtitles

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
    20: "Why did Python throw an UnboundLocalError? Because Python uses the LEGB rule for variable scope: Local, Enclosing, Global, and Built-in! A variable defined inside a function does not exist outside it. Master scope to keep your code bulletproof! Follow for Day 21!",
    21: "Python lists are not simple arrays! Under the hood, Python lists are dynamic arrays of memory pointers. When a list grows beyond its allocated capacity, Python allocates a brand new, larger block of RAM and moves the pointers over! Follow for Day 22!",
    22: "Why do professional Python programmers use Tuples instead of Lists? Because tuples are immutable—once created, their memory block is frozen in RAM! This makes tuples faster to iterate through and safe against accidental mutation in multithreaded applications! Follow for Day 23!",
    23: "Stop using Python lists when you need speed! Searching a list of 1 million items takes 1 million checks, but searching a Python dictionary takes O(1) instantaneous time! That's because dictionaries use a cryptographic hash table under the hood to jump straight to the exact memory address! Follow for Day 24!",
    24: "99% of Python beginners format strings the slow, outdated way! Never use plus signs or percent operators to join strings—use F-strings! F-strings are evaluated at runtime directly in bytecode, making them twice as fast and 10 times cleaner to read! Follow for Day 25!",
    25: "Why does opening files in Python leak your computer's memory? If your script crashes before close is called, that file handle stays locked by the OS! Always use the with open context manager—it automatically guarantees safe file closure even if your code errors out! Follow for Day 26!",
    26: "Did you know Python gives you access to over 500,000 free software libraries with 1 command? When you type pip install, your computer talks to the Python Package Index and downloads pre-compiled wheels written by the world's best engineers! Follow for Day 27!",
    27: "Never let your software crash in production! Python's try and except blocks catch runtime errors before they terminate your application. Catch specific exceptions like KeyError and ValueError instead of bare except to prevent masking hidden bugs! Follow for Day 28!",
    28: "How do real software engineers model complex real-world systems in code? With Classes! A class is the architectural blueprint, and an object is the living instance created in memory. Classes bundle data and behavior together to power modern software! Follow for Day 29!",
    29: "Don't repeat yourself! In Python, inheritance allows a child class to inherit every method and property from a parent class, while polymorphism lets different classes respond to the same method call in unique ways! Master this to write scalable code! Follow for Day 30!",
    30: "Turn 5 lines of messy Python loops into 1 elegant line of code! List comprehensions are not just syntactic sugar—they run in optimized C bytecode under the hood, executing up to 30% faster than standard for loops! Follow for Day 31!",
    31: "How does your computer find a password among 100 million accounts in 1 millisecond? With a Hash Function! A hash function takes any input and calculates a deterministic mathematical index into memory. This gives hash tables O(1) instantaneous lookup time, powering databases, caches, and search engines worldwide! Follow for Day 32!",
    32: "Why do software engineers organize data hierarchically instead of flat lists? Because Trees mirror reality! A binary tree connects a root node to at most two child nodes—left and right. This structure forms the foundation of file systems, DOM elements in web browsers, and AI decision trees! Follow for Day 33!",
    33: "A Binary Search Tree is one of the most elegant structures ever invented. Every item smaller than the node goes left, and every item larger goes right! This simple rule cuts your search space in half with every single step, turning an impossible 1-billion-item search into just 30 comparisons! Follow for Day 34!",
    34: "What is the secret flaw of standard binary search trees? If you insert sorted data, the tree degrades into a slow, linear linked list! AVL trees solve this with auto-rotations: whenever branches become unbalanced by more than one level, the tree instantly rotates itself to maintain lightning-fast O(log N) speed! Follow for Day 35!",
    35: "How does your operating system decide which app gets CPU time first? Using a Priority Queue built on a Binary Heap! A Min-Heap or Max-Heap guarantees the highest-priority task is always sitting right at the top in O(1) instantaneous access! Follow for Day 36!",
    36: "From Google Maps to social networks, Graphs represent the real world! A graph consists of vertices connected by edges. Whether finding flight routes, mapping friendships, or routing internet packets across continents, graph theory powers the modern interconnected internet! Follow for Day 37!",
    37: "How do computers store graph networks in memory? You have two choices: an Adjacency Matrix or an Adjacency List. Matrices provide instant edge lookup but waste massive RAM on sparse networks, while lists save memory by only storing connections that actually exist! Follow for Day 38!",
    38: "Ever wonder how Google autocompletes your search before you finish typing? That is a Trie! Instead of searching every word in the dictionary, a Trie organizes characters into a tree where common prefixes share the same branch, returning search recommendations in microseconds! Follow for Day 39!",
    39: "Why should you never use standard Python lists for FIFO queues? Because popping from the beginning forces Python to shift every remaining item in memory! A Deque or Circular Buffer wraps pointers around in a ring, making insertions and deletions at both ends instantaneous O(1) operations! Follow for Day 40!",
    40: "Choosing the wrong data structure will destroy your application's performance! Need random access by index? Use an Array. Need instant key lookup? Use a Hash Map. Need strict ordering and hierarchy? Use a Tree. Mastering data structure trade-offs is the number one superpower of top software engineers! Follow for Day 41!",
    41: "What is an algorithm really? It's not magic—it's a finite, step-by-step recipe to solve a specific problem. A great algorithm doesn't just work—it minimizes CPU instructions and RAM usage. The difference between a bad algorithm and a great algorithm is the difference between a program taking 1 second or 300 years to finish! Follow for Day 42!",
    42: "Big O Notation measures how your algorithm's runtime scales as your data grows to infinity! O(1) is instant, O(N) grows linearly, and O(N squared) will crash your server when traffic spikes! Always calculate your Big O before shipping code to production! Follow for Day 43!",
    43: "Linear search is the simplest search algorithm: check element zero, then element one, until you find your target. It works on unsorted data, but takes O(N) time. If you have 10 million items, you might have to check all 10 million! That's why we need faster search algorithms! Follow for Day 44!",
    44: "Binary search is algorithmic cheat code! By sorting your data first, you check the middle element and discard half the entire list with every single question. You can search through all 8 billion people on Earth in just 33 steps! Follow for Day 45!",
    45: "Bubble sort works by repeatedly swapping adjacent items until the largest elements bubble up to the top of the array. While easy to understand, its O(N squared) time complexity makes it one of the slowest sorting algorithms in computer science history! Follow for Day 46!",
    46: "Selection sort scans the entire array, selects the absolute smallest item, and places it at the front, repeating until sorted. While it minimizes the total number of memory swaps, it still checks every pair, remaining stuck at slow O(N squared) speed! Follow for Day 47!",
    47: "Insertion sort mimics how you sort playing cards in your hand: taking one card at a time and inserting it into its correct position among the sorted cards! For small or nearly-sorted datasets, insertion sort is shockingly fast and beats complex algorithms! Follow for Day 48!",
    48: "Merge sort is the master of Divide and Conquer! It recursively splits your array down to single elements, then merges them back together in sorted order. With a guaranteed O(N log N) runtime in best, average, and worst cases, it powers production sorting worldwide! Follow for Day 49!",
    49: "QuickSort selects a pivot element and partitions the array into items smaller and larger than the pivot. In practice, QuickSort is often faster than MergeSort because its memory access patterns leverage CPU cache lines with zero extra RAM allocation! Follow for Day 50!",
    50: "Heap sort transforms an unsorted array into a binary max-heap, then repeatedly extracts the maximum root element to the end of the array. It combines the guaranteed O(N log N) speed of Merge Sort with the zero-extra-memory advantage of QuickSort! Follow for Day 51!"
}

VIRAL_TITLES = {
    13: "How Python ACTUALLY Stores Data in RAM 🤯 (Day 13/100) #Shorts #Python #Coding",
    14: "The 1 Python input() Mistake Everyone Makes! 🐍 (Day 14) #Shorts #Python #Coding",
    15: "Why Python Does Math Differently Than You Think ⚡ (Day 15) #Shorts #Coding",
    16: "Stop Writing Messy If-Else Statements in Python! 🚀 (Day 16) #Shorts #Python",
    17: "How Python For Loops WORK Under The Hood 🔁 (Day 17) #Shorts #Coding",
    18: "The Most Dangerous Bug in Python Programming ⚠️ (Day 18) #Shorts #Python",
    19: "Write Python Code 10x Faster With Functions 💡 (Day 19) #Shorts #Coding",
    20: "Why Python Throws UnboundLocalError! 🧠 (Day 20) #Shorts #Python #Coding",
    21: "The Secret Way Python Lists Work in Memory 🐍 (Day 21) #Shorts #Coding",
    22: "Why Senior Developers ALWAYS Use Tuples ⚡ (Day 22) #Shorts #Python",
    23: "Stop Using Python Lists When You Need SPEED! 🚀 (Day 23) #Shorts #Python",
    24: "Stop Formatting Python Strings The Wrong Way! ❌ (Day 24) #Shorts #Coding",
    25: "The 1 Python File Handling Bug That Crashes Servers ⚠️ (Day 25) #Shorts",
    26: "How Pip Install ACTUALLY Works Behind The Scenes 📦 (Day 26) #Shorts",
    27: "Never Let Python Crash In Production Again! 🛡️ (Day 27) #Shorts #Python",
    28: "How OOP & Classes WORK in Python Explained In 30s 💡 (Day 28) #Shorts",
    29: "Inheritance vs Polymorphism Explained Simply 🧠 (Day 29) #Shorts #Coding",
    30: "Turn 5 Lines of Python Into 1 Line! ⚡ (Day 30) #Shorts #Python",
    31: "How Databases Search Passwords in 1 Millisecond! ⚡ (Day 31) #Shorts #Coding",
    32: "Why Trees Rule Computer Science 🌳 (Day 32) #Shorts #Programming",
    33: "Search 1 BILLION Items in 30 Steps! 🤯 (Day 33) #Shorts #Algorithms",
    34: "The Self-Balancing Tree Senior Devs Love ⚖️ (Day 34) #Shorts #Coding",
    35: "How Operating Systems Prioritize Your Tasks ⚡ (Day 35) #Shorts #ComputerScience",
    36: "How Google Maps ACTUALLY Finds Shortest Routes 🗺️ (Day 36) #Shorts #Tech",
    37: "Stop Wasting RAM With The Wrong Graph Structure! 🧠 (Day 37) #Shorts #Coding",
    38: "How Google Autocomplete Works Under The Hood 🔍 (Day 38) #Shorts #Tech",
    39: "Stop Popping Python Lists Like This! ⚠️ (Day 39) #Shorts #Python #Coding",
    40: "The Data Structure Cheat Sheet You NEED 💡 (Day 40) #Shorts #Coding",
    41: "What is an Algorithm? (Explained in 30s) ⚡ (Day 41) #Shorts #Coding",
    42: "Big O Notation: The ONLY Guide You Need 📈 (Day 42) #Shorts #Algorithms",
    43: "Why Linear Search Fails at Scale ❌ (Day 43) #Shorts #Coding",
    44: "Find Anyone on Earth in 33 Steps! 🤯 (Day 44) #Shorts #Algorithms",
    45: "Why Nobody Uses Bubble Sort in Production 🧼 (Day 45) #Shorts #Coding",
    46: "How Selection Sort Works in Memory 🔢 (Day 46) #Shorts #ComputerScience",
    47: "The Playing Card Sorting Algorithm 🃏 (Day 47) #Shorts #Algorithms",
    48: "Divide and Conquer: How Merge Sort Wins ⚔️ (Day 48) #Shorts #Coding",
    49: "Why QuickSort is the King of Sorting 👑 (Day 49) #Shorts #Algorithms",
    50: "Heap Sort: The Best of Both Worlds 🚀 (Day 50) #Shorts #ComputerScience"
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
        voice = "en-US-JennyNeural"
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
        voice = "en-US-AriaNeural"
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

    # 1. Generate Voiceover Audio with Exact Subtitle Synchronization
    audio_path = os.path.join(item_dir, "narration.mp3")
    print(f"  [1/4] Generating Neural Voiceover & Subtitle Timeline...")
    audio_path, subtitles = generate_narration_audio(script, voice, audio_path)

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

    # 4. Render 9:16 Multi-Photo Animated Video with Subtitles Synchronized to Speech
    video_path = os.path.join(item_dir, "final_short.mp4")
    print(f"  [3/4] Rendering 9:16 Animated Multi-Photo Video (Synchronized Captions)...")
    build_animated_shorts_video(
        audio_path=audio_path,
        photo_files=chosen_photos,
        badge_text=badge,
        title=title,
        script=script,
        output_path=video_path,
        subtitles=subtitles
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
