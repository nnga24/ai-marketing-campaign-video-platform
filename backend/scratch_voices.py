import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")

headers = {"xi-api-key": api_key}
response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
if response.status_code == 200:
    voices = response.json().get("voices", [])
    for v in voices:
        print(f"{v['name']}: {v['voice_id']} (Category: {v['category']})")
else:
    print("Lỗi:", response.text)
