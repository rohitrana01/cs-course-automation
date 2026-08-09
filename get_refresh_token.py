import requests
import json

with open("client_secrets.json", "r") as f:
    cfg = json.load(f)["installed"]

code = "4/0AXEQxlAoeOJ-Br70OXK5xFojZ0y22E2suzkL_QzgMjyC-bz"

url = "https://oauth2.googleapis.com/token"
payload = {
    "client_id": cfg["client_id"],
    "client_secret": cfg["client_secret"],
    "code": code,
    "grant_type": "authorization_code",
    "redirect_uri": "http://localhost:8088/"
}

r = requests.post(url, data=payload)
print(r.status_code)
print(r.text)
