import os
from tts_module import ElevenLabsProvider, ELEVENLABS_API_KEY, TTS_MODEL

import json

# Đoạn text mẫu chung
SAMPLE_TEXT = "Hôm nay là một ngày đẹp trời. Chúc bạn có những phút giây vui vẻ và ngập tràn năng lượng!"
OUTPUT_SAMPLE_DIR = "sample"
MAPPING_FILE = os.path.join(OUTPUT_SAMPLE_DIR, "voice_mapping.json")

def generate_samples():
    print("========================================")
    print("   BẮT ĐẦU SINH ÂM THANH MẪU (SAMPLES)  ")
    print("========================================")
    
    if not os.path.exists(OUTPUT_SAMPLE_DIR):
        os.makedirs(OUTPUT_SAMPLE_DIR)
        
    if not os.path.exists(MAPPING_FILE):
        print(f"Lỗi: Không tìm thấy file {MAPPING_FILE}. Vui lòng tạo file này trước.")
        return
        
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        voices_to_test = json.load(f)
        
    for name, voice_id in voices_to_test.items():
        print(f"\nĐang tạo sample cho giọng: [{name}] (ID: {voice_id})")
        output_path = os.path.join(OUTPUT_SAMPLE_DIR, f"{name}.mp3")
        
        provider = ElevenLabsProvider(
            api_key=ELEVENLABS_API_KEY,
            voice_id=voice_id,
            model_id=TTS_MODEL
        )
        
        result = provider.generate_speech(SAMPLE_TEXT, output_path)
        
        if result.success:
            print(f"  -> Thành công! Đã lưu tại: {result.file_path}")
        else:
            print(f"  -> Thất bại: {result.error_message}")
            
    print("\n[Hoàn tất] Các file mẫu và file mapping đã nằm trong thư mục sample/")

if __name__ == "__main__":
    generate_samples()
