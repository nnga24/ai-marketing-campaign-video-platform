import os
import sys
import json
import requests
import urllib.parse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORYBOARD_PATH = os.path.join(WORKSPACE_DIR, "story-board", "ga_u_muoi_storyboard.json")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "assets", "inputs", "images")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_image_api(prompt: str, output_path: str):
    print(f"🎨 Đang gọi Pollinations AI (Miễn phí, không cần API Key) để vẽ: '{prompt}'...")
    
    # Encode prompt vào URL. Format 9:16 (1080x1920) cho Tiktok
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true"
    
    for attempt in range(3):
        try:
            print(f"   ⏳ Thử lần {attempt + 1}/3...")
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Đã vẽ xong và lưu tại: {output_path}")
                return True
            else:
                print(f"❌ Lỗi API ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"❌ Lỗi kết nối (timeout/mạng) ở lần {attempt + 1}: {e}")
            
    print("❌ Đã thử 3 lần nhưng không thành công do server quá tải.")
    return False

def main():
    if not os.path.exists(STORYBOARD_PATH):
        print(f"Không tìm thấy storyboard tại {STORYBOARD_PATH}")
        return

    with open(STORYBOARD_PATH, "r", encoding="utf-8") as f:
        storyboard = json.load(f)

    scenes = storyboard.get("scenes", [])
    updated = False

    print("🔍 Đang quét Storyboard tìm các Cảnh bị thiếu ảnh...")
    for sc in scenes:
        sc_id = sc["id"]
        visual = sc.get("visual", {})
        ref_image = visual.get("reference_image", "")
        
        # Nếu thiếu ảnh
        if not ref_image or not os.path.exists(os.path.join(WORKSPACE_DIR, ref_image)):
            print(f"\n⚠️ Cảnh [{sc_id}] chưa có ảnh đầu vào.")
            print(f"1. Tự cung cấp ảnh thủ công.")
            print(f"2. Sử dụng AI tự do để tạo ảnh.")
            choice = input("Lựa chọn của bạn (1/2): ").strip()
            
            if choice == "2":
                subject = visual.get("subject", "")
                environment = visual.get("environment", "")
                # Prompt tiếng anh cho AI dễ hiểu
                prompt = f"Cinematic photography of {subject}. Environment: {environment}. 8k resolution, highly detailed, professional lighting."
                
                output_filename = f"ai_gen_{sc_id}.png"
                output_rel_path = f"assets/inputs/images/{output_filename}"
                output_abs_path = os.path.join(OUTPUT_DIR, output_filename)
                
                success = generate_image_api(prompt, output_abs_path)
                if success:
                    visual["reference_image"] = output_rel_path
                    updated = True
            else:
                print("⏳ Vui lòng sao chép ảnh của bạn vào thư mục 'assets/inputs/images' và sửa lại storyboard.json nhé.")

    if updated:
        with open(STORYBOARD_PATH, "w", encoding="utf-8") as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)
        print("\n💾 Đã cập nhật lại file storyboard.json với các ảnh AI vừa vẽ!")
    else:
        print("\n✅ Quét hoàn tất, không có thay đổi nào.")

if __name__ == "__main__":
    main()
