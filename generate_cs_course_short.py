"""
Generate High-Quality Animated CS Course Short Video with Pre-Resized 1080p HD Photos
"""
import sys
import time
import requests
import json
import os

# UTF-8 stdout encoding for Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

API_BASE_URL = "http://127.0.0.1:8080/api/v1"

def generate_cs_short(day_num: int, subject: str, script_text: str, voice_name: str = "en-US-AvaNeural-Female"):
    payload = {
        "video_subject": f"Day {day_num}: {subject}",
        "video_script": script_text,
        "video_terms": "computer, technology, future",
        "video_source": "local",
        "video_materials": [
            {"provider": "local", "url": "cs_photo_1_1080p.jpg"},
            {"provider": "local", "url": "cs_photo_2_1080p.jpg"},
            {"provider": "local", "url": "cs_photo_3_1080p.jpg"},
            {"provider": "local", "url": "cs_photo_4_1080p.jpg"}
        ],
        "video_clip_duration": 4,
        "voice_name": voice_name,
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
    
    print(f"[+] Submitting MoneyPrinterTurbo Short pipeline task for Day {day_num}: {subject} with 1080p HD photos...")
    resp = requests.post(f"{API_BASE_URL}/videos", json=payload)
    if resp.status_code != 200:
        print(f"[-] Failed to submit task: {resp.text}")
        return None
    
    data = resp.json()
    task_id = data.get("data", {}).get("task_id")
    print(f"[+] Task created successfully! Task ID: {task_id}")
    return task_id

def poll_task(task_id: str, timeout_seconds: int = 300):
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        resp = requests.get(f"{API_BASE_URL}/tasks/{task_id}")
        if resp.status_code == 200:
            task_info = resp.json().get("data", {})
            state = task_info.get("state")
            progress = task_info.get("progress", 0)
            print(f"[*] Task status: state={state}, progress={progress}%")
            
            if state == 1 or task_info.get("videos"):
                videos = task_info.get("videos") or task_info.get("result", {}).get("videos", [])
                print(f"[SUCCESS] Animated HD Photo Short rendered successfully via MoneyPrinterTurbo!")
                print(f"Rendered Output MP4: {videos}")
                return videos
            elif state == -1 or task_info.get("error"):
                print(f"[!] Task failed: {task_info.get('error')}")
                return None
        time.sleep(5)
    print("[-] Task timeout.")
    return None

if __name__ == "__main__":
    day = 1
    subject = "What is a Computer?"
    script = "Welcome to Day 1 of 100 Days of Computer Science! What actually is a computer? At its core, a computer is an electronic device that takes raw data as INPUT, processes it using its CPU brain, and produces meaningful OUTPUT. From smartphones to supercomputers, every machine follows this exact loop. Subscribe for Day 2!"
    
    tid = generate_cs_short(day, subject, script)
    if tid:
        poll_task(tid)
