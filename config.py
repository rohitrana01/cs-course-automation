"""
config.py — central configuration for the YouTube automation pipeline
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "claude" or "gemini"

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL   = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

# Gemini (Free Tier Alternative)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# YouTube OAuth
YOUTUBE_CLIENT_ID     = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

# Channel settings
CHANNEL_NAME  = os.getenv("CHANNEL_NAME") or "LearnCS Daily"
TTS_VOICE     = os.getenv("TTS_VOICE") or "en-US-AriaNeural"
VIDEO_PRIVACY = os.getenv("VIDEO_PRIVACY") or "public"

# Niche & Art Style Configurations (Strictly G-Rated & Child-Friendly)
NICHE                 = os.getenv("NICHE", "Computer Science")
CHARACTER_DESCRIPTION = os.getenv("CHARACTER_DESCRIPTION", "A friendly cute cartoon teacher mascot wearing glasses and a blue sweater, wholesome 3rd-grade educational style, clean vector art")
VISUAL_STYLE          = os.getenv("VISUAL_STYLE", "cute child-friendly educational cartoon, G-rated, wholesome, bright pastel colors, clean vector illustration, safe for work, SFW")

# Safety & Image Provider Settings
IMAGE_PROVIDER        = os.getenv("IMAGE_PROVIDER", "online").lower()  # "online" (Pollinations AI) or "local" (Procedural Pillow)
SAFE_MODE             = os.getenv("SAFE_MODE", "true").lower() in ("true", "1", "yes")

# Audio & Background Music Configurations
ENABLE_MUSIC          = os.getenv("ENABLE_MUSIC", "true").lower() in ("true", "1", "yes")
BACKGROUND_MUSIC_FOLDER = os.getenv("BACKGROUND_MUSIC_FOLDER", "resources/music")
BACKGROUND_MUSIC_VOLUME = float(os.getenv("BACKGROUND_MUSIC_VOLUME", "0.10"))

# Paths
OUTPUT_DIR       = "output"
CURRICULUM_FILE  = "curriculum.json"

# Video settings
VIDEO_WIDTH   = 1920
VIDEO_HEIGHT  = 1080
VIDEO_FPS     = 24
TARGET_DURATION = 300   # 5 minutes in seconds
