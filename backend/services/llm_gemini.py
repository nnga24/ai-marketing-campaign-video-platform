import os
import json
import google.generativeai as genai
import PIL.Image
from core.config import settings
from core.storage import storage

class GeminiService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            self.model = None

    def _extract_json(self, text: str) -> dict:
        """Trích xuất JSON an toàn từ kết quả trả về của LLM"""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Lỗi parse JSON: {e}")
            print(f"RAW TEXT: {text}")
            raise ValueError("AI không trả về định dạng JSON hợp lệ.")

    def generate_business_data(self, product_info: str, images: list = None) -> dict:
        if not self.model:
            raise ValueError("Vui lòng cấu hình GEMINI_API_KEY trong file .env")
            
        prompt = f"""
        Bạn là một chuyên gia Marketing AI xuất sắc.
        Dựa vào mô tả sản phẩm của người dùng và các hình ảnh đính kèm (nếu có), hãy xác định Dữ liệu Kinh doanh cốt lõi (Business Data) để làm video Tiktok ngắn.
        Đặc biệt chú ý đến chi tiết trong hình ảnh sản phẩm (nhãn mác, màu sắc, bao bì,...) để viết thông điệp cốt lõi sát thực tế nhất.
        
        Mô tả sản phẩm: {product_info}
        
        TRẢ VỀ ĐÚNG 1 FILE JSON THEO CẤU TRÚC SAU (KHÔNG KÈM TEXT GIẢI THÍCH):
        {{
          "product": {{
            "name": "Tên sản phẩm",
            "description": "Mô tả",
            "features": ["Tính năng 1", "Tính năng 2"],
            "benefits": ["Lợi ích 1", "Lợi ích 2"],
            "price": "Giá hoặc phân khúc",
            "usp": "Điểm bán hàng độc nhất"
          }},
          "brand": {{
            "tone_of_voice": "Tone giọng điệu (VD: Hài hước, Chuyên gia...)"
          }},
          "audience": {{
            "age": "Độ tuổi",
            "occupation": "Nghề nghiệp",
            "pain_points": ["Nỗi đau 1", "Nỗi đau 2"],
            "needs": ["Nhu cầu 1"],
            "hobbies": ["Sở thích 1"]
          }},
          "marketing": {{
            "objective": "Mục tiêu (Sales, Awareness...)",
            "platform": "TikTok",
            "duration": "15-30s",
            "cta": "Lời kêu gọi hành động"
          }}
        }}
        """
        contents = [prompt]
        if images:
            for uri in images:
                try:
                    abs_path = storage.get_absolute_path(uri)
                    img = PIL.Image.open(abs_path)
                    contents.append(img)
                except Exception as e:
                    print(f"Lỗi đọc ảnh {abs_path}: {e}")
                    
        response = self.model.generate_content(contents)
        return self._extract_json(response.text)

    def generate_storyboard(self, business_data: dict, num_scenes: int = 5) -> dict:
        if not self.model:
            raise ValueError("Vui lòng cấu hình GEMINI_API_KEY trong file .env")
            
        prompt = f"""
        Bạn là một Đạo diễn Video Tiktok AI.
        Dựa vào dữ liệu kinh doanh dưới đây, hãy tạo một kịch bản Storyboard {num_scenes} phân cảnh (Hook -> Problem -> Solution -> Benefit -> Call to Action).
        
        Dữ liệu kinh doanh:
        {json.dumps(business_data, ensure_ascii=False)}
        
        QUY TẮC BẮT BUỘC:
        1. "subject" và "environment" phải viết bằng TIẾNG ANH (Để gửi cho AI vẽ ảnh).
        2. "voice" phải viết bằng TIẾNG VIỆT, ngắn gọn, tự nhiên, đọc trong khoảng 2-4 giây mỗi cảnh.
        
        TRẢ VỀ ĐÚNG 1 FILE JSON THEO CẤU TRÚC SAU (KHÔNG KÈM TEXT GIẢI THÍCH):
        {{
          "scenes": [
            {{
              "id": "scene_01",
              "visual": {{
                "subject": "e.g., A tired office worker",
                "environment": "e.g., modern apartment living room, night"
              }},
              "audio": {{
                "voice": "Cả ngày đi làm về mệt rã rời, bạn chỉ muốn lăn ra ngủ?"
              }}
            }},
            // ... các cảnh khác
          ]
        }}
        """
        response = self.model.generate_content(prompt)
        return self._extract_json(response.text)

llm_service = GeminiService()
