"""
authenticate_youtube.py — 1-Click YouTube OAuth Authentication
Run this script to generate a fresh, permanent YouTube Refresh Token.
"""
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtubepartner"
]

def main():
    secrets_file = "client_secrets.json"
    if not os.path.exists(secrets_file):
        print(f"[!] Error: {secrets_file} not found!")
        return

    flow = InstalledAppFlow.from_client_secrets_file(secrets_file, SCOPES)
    print("\n[+] Opening browser for YouTube Channel authorization...")
    creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

    print("\n" + "=" * 60)
    print("  🎉 AUTHENTICATION SUCCESSFUL!")
    print("=" * 60)
    print(f"\n🔑 YOUR NEW YOUTUBE REFRESH TOKEN:\n")
    print(creds.refresh_token)
    print("\n" + "=" * 60)
    print("\n📋 Next Step:")
    print("1. Copy the token above.")
    print("2. Go to: https://github.com/rohitrana01/cs-course-automation/settings/secrets/actions")
    print("3. Update secret 'YOUTUBE_REFRESH_TOKEN' with this new value.")
    print("=" * 60 + "\n")

    # Save to local .env
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}\n")
    print("[+] Saved to local .env file.")

if __name__ == "__main__":
    main()
