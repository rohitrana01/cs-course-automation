"""
modules/video_assembler.py
Merges the silent animation video with the TTS audio track.
Handles duration mismatches (loops or trims the video to match audio length).
"""
import os
import glob
import random
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, afx, vfx
from config import ENABLE_MUSIC, BACKGROUND_MUSIC_FOLDER, BACKGROUND_MUSIC_VOLUME


def assemble_video(animation_path: str, audio_path: str, output_dir: str) -> str:
    """
    Combine silent animation with TTS narration audio.

    Strategy:
    - If video is longer than audio  → trim video end
    - If video is shorter than audio → loop the last frame to fill

    Returns path to the final MP4.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "final_video.mp4")

    print("  [assembler] Loading video and audio…")
    video = VideoFileClip(animation_path)
    audio = AudioFileClip(audio_path)

    vid_dur = video.duration
    aud_dur = audio.duration

    print(f"  [assembler] Video: {vid_dur:.1f}s  |  Audio: {aud_dur:.1f}s")

    if vid_dur >= aud_dur:
        # Trim video to audio length
        video = video.subclipped(0, aud_dur)
    else:
        # Pad video: freeze last frame for remaining duration
        gap = aud_dur - vid_dur
        last_frame_time = max(vid_dur - 0.05, 0)
        freeze = video.subclipped(last_frame_time, vid_dur).with_effects([afx.vfx.Loop(duration=gap)])
        video = concatenate_videoclips([video, freeze])

    # Attach audio
    final_audio = audio

    # Mix background music if available
    if ENABLE_MUSIC and os.path.exists(BACKGROUND_MUSIC_FOLDER):
        music_files = glob.glob(os.path.join(BACKGROUND_MUSIC_FOLDER, "*.mp3")) + \
                      glob.glob(os.path.join(BACKGROUND_MUSIC_FOLDER, "*.wav"))
        if music_files:
            bg_music_path = random.choice(music_files)
            print(f"  [assembler] Mixing background music: {os.path.basename(bg_music_path)}")
            try:
                bg_audio = AudioFileClip(bg_music_path)
                if bg_audio.duration < final_audio.duration:
                    bg_audio = bg_audio.with_effects([afx.vfx.Loop(duration=final_audio.duration)])
                else:
                    bg_audio = bg_audio.subclipped(0, final_audio.duration)
                bg_audio = bg_audio.with_effects([afx.MultiplyVolume(BACKGROUND_MUSIC_VOLUME)])
                final_audio = CompositeAudioClip([audio, bg_audio])
            except Exception as e:
                print(f"  [assembler] Warning: Failed to mix background music ({e})")

    final = video.with_audio(final_audio)

    print(f"  [assembler] Writing final video → {output_path}")
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger=None,
        ffmpeg_params=["-crf", "23", "-preset", "fast"]
    )
    return output_path
