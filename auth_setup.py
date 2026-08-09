"""
auth_setup.py — Get your YouTube refresh token cleanly.
"""
import json
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

SECRETS_FILE = "client_secrets.json"


def main():
    if not os.path.exists(SECRETS_FILE):
        print(f"❌ {SECRETS_FILE} not found.", flush=True)
        return

    print("🔐 Starting OAuth authentication flow...", flush=True)

    flow = InstalledAppFlow.from_client_secrets_file(
        SECRETS_FILE,
        SCOPES
    )

    creds = flow.run_local_server(
        host="localhost",
        port=8055,
        authorization_prompt_message="🔐 Complete authorization in your browser window:\n",
        success_message="✅ Authentication successful! You can close this tab now.",
        open_browser=True
    )

    print("\n" + "=" * 60, flush=True)
    print("  ✅ AUTHENTICATION SUCCESSFUL!", flush=True)
    print("=" * 60, flush=True)
    print(f"YOUTUBE_CLIENT_ID: {creds.client_id}", flush=True)
    print(f"YOUTUBE_CLIENT_SECRET: {creds.client_secret}", flush=True)
    print(f"YOUTUBE_REFRESH_TOKEN: {creds.refresh_token}", flush=True)
    print("=" * 60 + "\n", flush=True)

    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"YOUTUBE_CLIENT_ID={creds.client_id}\n")
        f.write(f"YOUTUBE_CLIENT_SECRET={creds.client_secret}\n")
        f.write(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}\n")
    print("Saved credentials to .env file.", flush=True)


if __name__ == "__main__":
    main()
