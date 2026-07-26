"""
pipeline.py — Main automation orchestrator
Run this daily to generate 3rd-grade style animated explainer videos:
  1. Pick the next topic from curriculum.json
  2. Generate script segments (narration + chalkboard text + diagram descriptions)
  3. For each segment:
     - Generate TTS narration audio + word timings for subtitles
     - Download customized base chalkboard scene with chibi teacher pose
     - Download optional sticker diagram/illustration
     - Render chalkboard slide animation with sequential points + sticker reveal
  4. Concatenate segments and mix lofi music
  5. Generate anime thumbnail
  6. Upload final video to YouTube
  7. Mark topic as completed in curriculum.json
"""
import os
import sys
import json
import glob
from datetime import datetime, timezone

from config import OUTPUT_DIR, CURRICULUM_FILE, CHANNEL_NAME
from modules.script_generator    import generate_script
from modules.tts_narrator        import generate_segment_narration
from modules.image_generator     import generate_image, generate_diagram
from modules.animator            import create_segment_animation
from modules.video_assembler     import assemble_video
from modules.thumbnail_generator import create_thumbnail
from modules.youtube_uploader    import upload_video


# ── Curriculum helpers ────────────────────────────────────────────────────────

def load_curriculum() -> dict:
    with open(CURRICULUM_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_curriculum(data: dict):
    with open(CURRICULUM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_topic(curriculum: dict) -> dict | None:
    for topic in curriculum["topics"]:
        if not topic.get("uploaded", False):
            return topic
    return None


def mark_uploaded(curriculum: dict, topic_id: str, video_id: str):
    for t in curriculum["topics"]:
        if t["id"] == topic_id:
            t["uploaded"]    = True
            t["video_id"]    = video_id
            t["upload_date"] = datetime.now(timezone.utc).isoformat()
            break


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run():
    print("\n" + "═" * 60)
    print("  🚀  3rd-Grade Explainer Video Automation Pipeline")
    print("═" * 60)

    dry_run = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")
    if dry_run:
        print("🔍  DRY RUN MODE ENABLED — No actual upload or curriculum save will occur.")

    # ── 0. Load curriculum ──────────────────────────────────────────────────
    if not os.path.exists(CURRICULUM_FILE):
        print(f"❌ Error: '{CURRICULUM_FILE}' not found! Run generate_curriculum.py first.")
        sys.exit(1)
        
    curriculum = load_curriculum()
    topic = get_next_topic(curriculum)

    if topic is None:
        print("✅  All topics in the curriculum have been uploaded! Course complete.")
        sys.exit(0)

    print(f"\n📚  Day {topic['day']:03d}: {topic['title']}")
    print(f"     Module  : {topic['module']}")
    print(f"     Level   : {topic['level']}")

    # ── Output directory for this topic ────────────────────────────────────
    out = os.path.join(OUTPUT_DIR, topic["id"])
    os.makedirs(out, exist_ok=True)

    # Inject channel name into topic dictionary for subtitle/thumbnail branding
    topic["channel"] = CHANNEL_NAME

    # ── 1. Generate script segments ─────────────────────────────────────────
    print("\n[1/6] 🤖  Generating 3rd-grade storyboard script via LLM...")
    script_data = generate_script(topic)
    print(f"       Title  : {script_data['video_title']}")
    print(f"       Segs   : {len(script_data.get('segments', []))} segments generated")

    # Save script for debugging
    with open(os.path.join(out, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)

    # ── 2 & 3. Process Segment assets & Render video clips ──────────────────
    print("\n[2-3/6] 🎨 Processing and animating blackboard segments...")
    segment_paths = []
    
    segments = script_data.get("segments", [])
    if not segments:
        print("❌ Error: No segments generated in script.")
        sys.exit(1)
        
    for idx, seg in enumerate(segments):
        print(f"\n--- Segment {idx+1} / {len(segments)}: {seg.get('title', 'Untitled')} ---")
        
        # A. TTS Audio + Word Timing Subtitles
        audio_path, subtitles, duration = generate_segment_narration(
            seg["narration"], out, idx
        )
        
        # B. Download base classroom image
        img_path = os.path.join(out, f"scene_{idx}.jpg")
        generate_image(seg["character_pose"], img_path)
        
        # C. Download optional diagram sticker illustration
        diagram_path = None
        diagram_prompt = seg.get("diagram_prompt")
        if diagram_prompt:
            diagram_path = os.path.join(out, f"scene_{idx}_diagram.png")
            generate_diagram(diagram_prompt, diagram_path)
        
        # D. Render the chalkboard slide animation clip
        video_clip_path = os.path.join(out, f"segment_{idx}.mp4")
        create_segment_animation(
            image_path=img_path,
            board_elements=seg.get("board_elements", []),
            diagram_path=diagram_path,
            subtitles=subtitles,
            duration=duration,
            audio_path=audio_path,
            output_path=video_clip_path
        )
        segment_paths.append(video_clip_path)

    # ── 4. Assemble final video (Merge clips + Background Music) ─────────────
    print("\n[4/6] 🎬  Assembling final video with background music...")
    final_path = assemble_video(segment_paths, out)

    # ── 5. Generate thumbnail ────────────────────────────────────────────────
    print("\n[5/6] 🖼️   Generating thumbnail...")
    thumb_path = create_thumbnail(topic, out)

    # ── 6. Upload to YouTube ─────────────────────────────────────────────────
    print("\n[6/6] 📤  Uploading to YouTube...")
    if dry_run:
        print("       [DRY RUN] Skipping YouTube upload. Using mock video ID.")
        video_id = "mock_video_id"
    else:
        video_id = upload_video(
            video_path=final_path,
            thumbnail_path=thumb_path,
            title=script_data["video_title"],
            description=script_data["video_description"],
            tags=script_data.get("tags", []) + topic.get("tags", []),
        )

    # ── 7. Mark as uploaded & save ───────────────────────────────────────────
    if dry_run:
        print("       [DRY RUN] Skipping curriculum.json updates.")
    else:
        mark_uploaded(curriculum, topic["id"], video_id)
        save_curriculum(curriculum)

    # ── 8. Update Local Interactive Dashboard Database ──────────────────────
    print("\n[7/7] 💾 Updating local dashboard database...")
    try:
        from modules.db_manager import update_database
        video_rel = os.path.join("output", topic["id"], "final_video.mp4")
        thumb_rel = os.path.join("output", topic["id"], "thumbnail.jpg")
        update_database(
            topic_id=topic["id"],
            quiz_questions=script_data.get("quiz", []),
            video_rel_path=video_rel,
            thumbnail_rel_path=thumb_rel
        )
    except Exception as e:
        print(f"       ⚠️ Warning: Could not update data.js database: {e}")

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print(f"  ✅  SUCCESS — Day {topic['day']} uploaded!")
    print(f"  🔗  https://www.youtube.com/watch?v={video_id}")
    remaining = sum(1 for t in curriculum["topics"] if not t.get("uploaded"))
    print(f"  📅  {remaining} topics remaining in the course")
    print("═" * 60 + "\n")

    # ── Cleanup intermediate media assets ───────────────────────────────────
    _cleanup_intermediates(out, keep=["script.json", "thumbnail.jpg", "final_video.mp4"])


def _cleanup_intermediates(out_dir: str, keep: list[str]):
    """Delete segment audio, images, and videos to save disk space."""
    print("🧹  Cleaning intermediate assets...")
    for pattern in ["segment_*.mp3", "scene_*.jpg", "scene_*_diagram.png", "segment_*.mp4"]:
        files = glob.glob(os.path.join(out_dir, pattern))
        for f in files:
            fname = os.path.basename(f)
            if fname not in keep:
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"  [cleanup] Failed to delete {fname}: {e}")


if __name__ == "__main__":
    run()
