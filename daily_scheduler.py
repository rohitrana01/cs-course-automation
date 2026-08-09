"""
Daily 2 Shorts Automation Pipeline (Morning & Evening)
Powered by MoneyPrinterTurbo REST API
"""
import sys
import os
import json
import time
import argparse
import datetime
import requests

# UTF-8 stdout encoding for Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRICULUM_PATH = os.path.join(os.path.dirname(__file__), "curriculum.json")
API_BASE_URL = os.environ.get("MONEYPRINTER_API_URL", "http://127.0.0.1:8080/api/v1")

def load_curriculum():
    with open(CURRICULUM_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_curriculum(data):
    with open(CURRICULUM_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_unuploaded_topic(curriculum_data, slot_name="Morning"):
    topics = curriculum_data.get("topics", [])
    for t in topics:
        if not t.get("uploaded", False):
            return t
    return None

def trigger_moneyprinter_short(topic, slot="Morning"):
    day = topic.get("day", 1)
    title = topic.get("title", "Computer Science")
    key_points = topic.get("key_points", [])
    points_text = " ".join(key_points[:3]) if key_points else "Learn core computer science concepts step by step."
    
    script = (
        f"Good {slot}! Welcome to Day {day} of 100 Days Computer Course. "
        f"Today's topic is {title}. {points_text} "
        f"Subscribe for your next daily short lesson!"
    )
    
    payload = {
        "video_subject": f"Day {day} ({slot}): {title}",
        "video_script": script,
        "video_terms": "computer, technology, future",
        "video_source": "local",
        "video_materials": [
            {"provider": "local", "url": "cs_photo_1_1080p.jpg"},
            {"provider": "local", "url": "cs_photo_2_1080p.jpg"},
            {"provider": "local", "url": "cs_photo_3_1080p.jpg"},
            {"provider": "local", "url": "cs_photo_4_1080p.jpg"}
        ],
        "video_clip_duration": 4,
        "voice_name": "en-US-AvaNeural-Female" if slot == "Morning" else "en-US-ChristopherNeural-Male",
        "video_aspect": "9:16",
        "subtitle_enabled": True,
        "subtitle_position": "bottom",
        "text_fore_color": "#FFFFFF",
        "text_background_color": "#0F172A",
        "rounded_subtitle_background": True,
        "font_size": 60,
        "stroke_color": "#000000",
        "stroke_width": 2.0,
        "bgm_type": "random",
        "bgm_volume": 0.15
    }
    
    print(f"\n[🚀 {slot.upper()} SHORT] Submitting pipeline task for Day {day}: {title}...")
    try:
        resp = requests.post(f"{API_BASE_URL}/videos", json=payload, timeout=30)
        if resp.status_code != 200:
            print(f"[-] API Error ({resp.status_code}): {resp.text}")
            return False
        
        task_id = resp.json().get("data", {}).get("task_id")
        print(f"[+] Task created successfully! Task ID: {task_id}")
        
        # Poll task
        start_time = time.time()
        while time.time() - start_time < 300:
            tr = requests.get(f"{API_BASE_URL}/tasks/{task_id}", timeout=10)
            if tr.status_code == 200:
                tinfo = tr.json().get("data", {})
                state = tinfo.get("state")
                progress = tinfo.get("progress", 0)
                print(f"[*] Task status ({slot}): state={state}, progress={progress}%")
                if state == 1 or tinfo.get("videos"):
                    videos = tinfo.get("videos") or tinfo.get("result", {}).get("videos", [])
                    print(f"[✅ {slot.upper()} SUCCESS] Output MP4: {videos}")
                    return True
                elif state == -1 or tinfo.get("error"):
                    print(f"[!] Task failed: {tinfo.get('error')}")
                    return False
            time.sleep(5)
        print(f"[-] Task timed out after 300s.")
        return False
    except Exception as e:
        print(f"[!] Connection Exception: {e}")
        return False

def run_slot(slot="Morning"):
    print(f"\n==================================================")
    print(f"  🎬 EXECUTING DAILY SHORT PIPELINE — {slot.upper()}")
    print(f"  Timestamp: {datetime.datetime.now().isoformat()}")
    print(f"==================================================")
    
    curr = load_curriculum()
    topic = get_next_unuploaded_topic(curr, slot_name=slot)
    if not topic:
        print("[!] No remaining topics in curriculum!")
        return
    
    success = trigger_moneyprinter_short(topic, slot=slot)
    if success:
        topic["uploaded"] = True
        topic["last_generated"] = datetime.datetime.now().isoformat()
        topic["slot"] = slot
        save_curriculum(curr)
        print(f"[+] Curriculum updated for Day {topic.get('day')} ({slot}).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily 2 Shorts Automation (Morning & Evening)")
    parser.add_argument("--slot", choices=["morning", "evening", "both"], default="morning", help="Which slot to generate")
    args = parser.parse_args()
    
    if args.slot == "both":
        run_slot("Morning")
        time.sleep(2)
        run_slot("Evening")
    elif args.slot == "morning":
        run_slot("Morning")
        topic_night = run_slot("Evening")
