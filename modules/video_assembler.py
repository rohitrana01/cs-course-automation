"""
modules/video_assembler.py
Merges segment video clips into the final video and overlays subtle background music if enabled.
Handles both single-file animation merging and multi-segment list concatenation.
"""
import os
import glob
import random
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
from config import ENABLE_MUSIC, BACKGROUND_MUSIC_FOLDER, BACKGROUND_MUSIC_VOLUME


def assemble_video(video_input, output_dir_or_audio: str = None, output_dir: str = None) -> str:
    """
    Concatenates segment video clips into the final video and mixes background music.

    Supports:
    - assemble_video(segment_paths_list, output_dir)
    - assemble_video(animation_path, audio_path, output_dir)
    """
    if isinstance(video_input, list):
        segment_paths = video_input
        out_dir = output_dir_or_audio or "."
        os.makedirs(out_dir, exist_ok=True)
        final_output_path = os.path.join(out_dir, "final_video.mp4")

        print(f"  [assembler] Concatenating {len(segment_paths)} segment video clips...")
        clips = [VideoFileClip(p) for p in segment_paths if os.path.exists(p)]
        if not clips:
            raise RuntimeError("No valid segment video clips found to concatenate.")
            
        final_video = concatenate_videoclips(clips, method="compose")

    else:
        animation_path = video_input
        audio_path = output_dir_or_audio
        out_dir = output_dir or "."
        os.makedirs(out_dir, exist_ok=True)
        final_output_path = os.path.join(out_dir, "final_video.mp4")

        print("  [assembler] Loading single video animation and audio track...")
        video = VideoFileClip(animation_path)
        audio = AudioFileClip(audio_path)

        if video.duration >= audio.duration:
            video = video.subclip(0, audio.duration)
        else:
            gap = audio.duration - video.duration
            last_frame_time = max(video.duration - 0.05, 0)
            freeze = video.subclip(last_frame_time, video.duration).loop(duration=gap)
            video = concatenate_videoclips([video, freeze])

        final_video = video.set_audio(audio)

    # ── Background Music Mixing ──────────────────────────────────────────────
    if ENABLE_MUSIC and os.path.exists(BACKGROUND_MUSIC_FOLDER):
        music_files = glob.glob(os.path.join(BACKGROUND_MUSIC_FOLDER, "*.mp3")) + \
                      glob.glob(os.path.join(BACKGROUND_MUSIC_FOLDER, "*.wav"))
        if music_files:
            bg_music_path = random.choice(music_files)
            print(f"  [assembler] Mixing background music: {os.path.basename(bg_music_path)}")
            try:
                bg_audio = AudioFileClip(bg_music_path)
                # Loop background music if shorter than video duration
                if bg_audio.duration < final_video.duration:
                    bg_audio = bg_audio.loop(duration=final_video.duration)
                else:
                    bg_audio = bg_audio.subclip(0, final_video.duration)
                
                bg_audio = bg_audio.volumex(BACKGROUND_MUSIC_VOLUME)
                
                # Combine main audio with background music
                if final_video.audio:
                    composite_audio = CompositeAudioClip([final_video.audio, bg_audio])
                else:
                    composite_audio = bg_audio
                    
                final_video = final_video.set_audio(composite_audio)
            except Exception as e:
                print(f"  [assembler] Warning: Failed to mix background music ({e}). Continuing with main audio.")

    print(f"  [assembler] Writing final video → {final_output_path}")
    final_video.write_videofile(
        final_output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None,
        ffmpeg_params=["-crf", "22", "-preset", "fast"]
    )

    return final_output_path
