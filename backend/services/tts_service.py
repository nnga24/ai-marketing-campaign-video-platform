import os
import requests
from core.config import settings
from core.storage import storage

class TTSService:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID

    def generate_voice(self, project_id: str, scene_id: str, text: str, voice_id: str = None) -> str:
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY chưa được cấu hình trong file .env.")
            
        target_voice = voice_id if voice_id else self.voice_id
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2_5"
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            filename = f"{scene_id}.mp3"
            uri = storage.save_file(project_id, "voice", filename, response.content)
            return uri
        else:
            raise Exception(f"Lỗi gọi ElevenLabs API: {response.text}")

tts_service = TTSService()
