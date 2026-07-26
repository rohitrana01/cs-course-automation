"""
modules/tts_narrator.py
Generates narration audio from the script using Microsoft Edge TTS.
Generates segment-level audio files and word-level timing subtitles.
"""
import asyncio
import os
import subprocess
from config import TTS_VOICE


async def _generate_async(text: str, output_path: str, voice: str):
    """Run edge-tts and save to output_path."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_segment_narration(narration_text: str, output_dir: str, seg_idx: int = 0, voice: str = None):
    """
    Generate TTS audio for a single script segment and calculate estimated word timing subtitles.
    Returns (audio_path, subtitles_list, duration_seconds)
    """
    voice = (voice or TTS_VOICE or "en-US-AriaNeural").strip()
    if not voice:
        voice = "en-US-AriaNeural"
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, f"segment_{seg_idx}_narration.mp3")

    print(f"  [tts] Generating segment {seg_idx} audio with voice: {voice}")

    try:
        asyncio.run(_generate_async(narration_text, audio_path, voice))
    except RuntimeError:
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_generate_async(narration_text, audio_path, voice))

    duration = _get_audio_duration(audio_path, narration_text)

    # Estimate word-level timing for subtitles
    words = narration_text.split()
    subtitles = []
    if words:
        words_per_sec = len(words) / max(duration, 1.0)
        chunk_size = 4  # 4 words per caption line
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            start_t = i / words_per_sec
            end_t = min((i + len(chunk)) / words_per_sec, duration)
            subtitles.append({
                "start": start_t,
                "end": end_t,
                "text": " ".join(chunk)
            })

    print(f"  [tts] Audio segment generated: {duration:.1f}s → {audio_path}")
    return audio_path, subtitles, duration


def generate_narration(narration_text: str, output_dir: str, voice: str = None) -> tuple[str, float]:
    """Legacy alias for whole-file narration generation."""
    audio_path, _, duration = generate_segment_narration(narration_text, output_dir, 0, voice)
    return audio_path, duration


def _get_audio_duration(path: str, narration_text: str) -> float:
    """Use ffprobe to get precise audio duration in seconds."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                path
            ],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())
    except Exception:
        word_count = len(narration_text.split())
        return max(word_count / 140 * 60, 5.0)
