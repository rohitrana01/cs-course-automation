import os
import sys

# Configure UTF-8 encoding for Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

os.environ["DRY_RUN"] = "true"
os.environ["PYTHONIOENCODING"] = "utf-8"

from pipeline import run

if __name__ == "__main__":
    print("[+] Starting Day 1 CS Video Generation (Dry Run Mode)...")
    run()
