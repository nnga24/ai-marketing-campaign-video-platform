import os
import requests
import urllib.parse
from core.storage import storage

class ImageGeneratorService:
    def generate_image(self, project_id: str, scene_id: str, prompt: str) -> str:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true"
        
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=60)
                if response.status_code == 200:
                    filename = f"ai_gen_{scene_id}.png"
                    # Lưu file ảnh vào thư mục inputs
                    uri = storage.save_file(project_id, "inputs", filename, response.content)
                    return uri
            except Exception as e:
                print(f"Lỗi kết nối ảnh lần {attempt+1}: {e}")
                
        raise Exception(f"Không thể tạo ảnh cho cảnh {scene_id} sau 3 lần thử do server tải nặng.")

image_gen = ImageGeneratorService()
