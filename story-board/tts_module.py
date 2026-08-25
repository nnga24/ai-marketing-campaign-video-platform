import os
import json
import time
import requests
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# ==========================================
# CONFIGURATION
# (Có thể tích hợp bằng dotenv hoặc env vars)
# ==========================================
STORYBOARD_FILE = "ga_u_muoi_storyboard.json"
AUDIO_JSON_FILE = "audio.json"
MANIFEST_FILE = "audio_manifest.json"
OUTPUT_DIR = "voice"

# ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "YOUR_API_KEY_HERE")
ELEVENLABS_API_KEY = "sk_bb6a7e8811fc672625424e4cdfcbf009871bc70ff970a0ea"
VOICE_ID = "qvqJAcNJfpjBa72HFXsB"
TTS_MODEL = "eleven_turbo_v2_5" # Lưu ý: Nếu web bạn dùng V3, hãy thử đổi thành "eleven_turbo_v2_5" hoặc "eleven_multilingual_v2"
VOICE_PROFILE_NAME = "VIETNAMESE_MALE_WARM"

# ==========================================
# 1. DATA CLASSES
# ==========================================
@dataclass
class TTSResult:
    """Định dạng chuẩn kết quả trả về từ bất kỳ TTS Provider nào."""
    success: bool
    file_path: str = ""
    duration_seconds: float = 0.0
    error_message: str = ""

# ==========================================
# 2. STORYBOARD PARSER
# ==========================================
class StoryboardParser:
    """Chịu trách nhiệm lọc dữ liệu âm thanh từ storyboard gốc."""
    
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file

    def parse_and_save(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.input_file):
            print(f"[Parser] Lỗi: Không tìm thấy file {self.input_file}")
            return []

        with open(self.input_file, "r", encoding="utf-8") as f:
            storyboard = json.load(f)

        scenes = storyboard.get("scenes", [])
        audio_data = []

        for scene in scenes:
            scene_id = scene.get("id", "unknown_scene")
            voice_text = scene.get("audio", {}).get("voice", "")
            
            audio_data.append({
                "scene_id": scene_id,
                "voice_text": voice_text
            })

        # Xuất ra file audio.json trung gian
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(audio_data, f, ensure_ascii=False, indent=2)
            
        print(f"[Parser] Đã trích xuất {len(audio_data)} scenes và lưu vào {self.output_file}")
        return audio_data

# ==========================================
# 3. TTS PROVIDERS (ADAPTER PATTERN)
# ==========================================
class BaseTTSProvider(ABC):
    """Abstract class định nghĩa giao thức chung cho TTS."""
    
    @abstractmethod
    def generate_speech(self, text: str, output_path: str) -> TTSResult:
        pass


class ElevenLabsProvider(BaseTTSProvider):
    """Adapter tích hợp với ElevenLabs API."""
    
    def __init__(self, api_key: str, voice_id: str, model_id: str):
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    def generate_speech(self, text: str, output_path: str) -> TTSResult:
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            print(f"  [ElevenLabs Mock] Tạo audio giả lập -> {output_path}")
            # Mock logic
            try:
                with open(output_path, "wb") as f:
                    f.write(b"Mock ElevenLabs Audio")
                return TTSResult(success=True, file_path=output_path, duration_seconds=1.0)
            except Exception as e:
                return TTSResult(success=False, error_message=str(e))

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": text,
            "model_id": self.model_id
            # Đã xoá voice_settings để API tự động dùng thông số chuẩn (default) giống hệt trên Web
        }

        start_time = time.time()
        try:
            response = requests.post(self.api_url, json=data, headers=headers)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                duration = round(time.time() - start_time, 2)
                return TTSResult(success=True, file_path=output_path, duration_seconds=duration)
            else:
                return TTSResult(success=False, error_message=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            return TTSResult(success=False, error_message=f"Request Failed: {str(e)}")

# ==========================================
# 4. ORCHESTRATOR
# ==========================================
class TTSOrchestrator:
    """Điều phối toàn bộ workflow: đọc audio.json -> gọi Provider -> lưu Manifest."""
    
    def __init__(self, provider: BaseTTSProvider, output_dir: str, manifest_file: str):
        self.provider = provider
        self.output_dir = output_dir
        self.manifest_file = manifest_file
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def process(self, audio_data: List[Dict[str, str]], voice_profile: str):
        print("[Orchestrator] Bắt đầu gọi TTS API...")
        manifest_segments = []

        for item in audio_data:
            scene_id = item["scene_id"]
            voice_text = item["voice_text"]

            # Khởi tạo dữ liệu output cho manifest
            segment_result = {
                "scene_id": scene_id,
                "status": "skipped",
                "audio_file": None,
                "voice_text": voice_text,
                "actual_duration_seconds": 0.0,
                "error": None
            }

            if not voice_text or voice_text.strip() == "":
                print(f"[{scene_id}] Skip (Không có thoại)")
                manifest_segments.append(segment_result)
                continue

            print(f"[{scene_id}] Đang xử lý: '{voice_text[:30]}...'")
            output_filepath = os.path.join(self.output_dir, f"{scene_id}.mp3")
            
            # Đẩy việc gọi API cho Provider xử lý
            result: TTSResult = self.provider.generate_speech(voice_text, output_filepath)
            
            if result.success:
                segment_result["status"] = "success"
                segment_result["audio_file"] = result.file_path
                segment_result["actual_duration_seconds"] = result.duration_seconds
            else:
                segment_result["status"] = "failed"
                segment_result["error"] = result.error_message
                print(f"  [Lỗi] {result.error_message}")

            manifest_segments.append(segment_result)

        # Lưu Manifest
        self._save_manifest(manifest_segments, voice_profile)

    def _save_manifest(self, segments: List[dict], voice_profile: str):
        manifest_data = {
            "source": AUDIO_JSON_FILE,
            "voice_profile": voice_profile,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "segments": segments
        }

        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=2)
        print(f"[Orchestrator] Hoàn tất! Đã lưu Audio Manifest vào: {self.manifest_file}")


# ==========================================
# 5. ENTRY POINT
# ==========================================
if __name__ == "__main__":
    # Bước 1: Parse Storyboard để lấy audio.json
    parser = StoryboardParser(input_file=STORYBOARD_FILE, output_file=AUDIO_JSON_FILE)
    audio_data_list = parser.parse_and_save()

    if audio_data_list:
        # Bước 2: Khởi tạo TTS Provider (ElevenLabs)
        elevenlabs_provider = ElevenLabsProvider(
            api_key=ELEVENLABS_API_KEY, 
            voice_id=VOICE_ID, 
            model_id=TTS_MODEL
        )
        
        # Bước 3: Điều phối và sinh audio
        orchestrator = TTSOrchestrator(
            provider=elevenlabs_provider, 
            output_dir=OUTPUT_DIR, 
            manifest_file=MANIFEST_FILE
        )
        
        orchestrator.process(audio_data=audio_data_list, voice_profile=VOICE_PROFILE_NAME)
