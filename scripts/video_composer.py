import os
import glob
import json
import sys

# Đảm bảo xử lý lỗi encoding tiếng Việt trên Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORYBOARD_PATH = os.path.join(WORKSPACE_DIR, "story-board", "ga_u_muoi_storyboard.json")
VOICE_DIR = os.path.join(WORKSPACE_DIR, "story-board", "voice")
GENERATED_SCENES_DIR = os.path.join(WORKSPACE_DIR, "assets", "generated_scenes")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "assets", "final_videos")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_latest_manifest():
    # Tìm tất cả các file audio_manifest.json
    manifests = glob.glob(os.path.join(VOICE_DIR, "**", "audio_manifest.json"), recursive=True)
    if not manifests:
        return None
    # Sắp xếp để lấy thư mục mới tạo gần nhất
    manifests.sort(key=os.path.getmtime, reverse=True)
    return manifests[0]

def draw_subtitle_on_frame(frame, t, text, total_duration):
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    
    words = text.split()
    total_words = len(words)
    if total_words == 0:
        return frame
        
    progress = min(1.0, max(0.0, t / total_duration))
    current_word_idx = int(progress * total_words)
    if current_word_idx >= total_words:
        current_word_idx = total_words - 1
        
    chunk_size = 5
    chunk_idx = current_word_idx // chunk_size
    start_idx = chunk_idx * chunk_size
    end_idx = min(start_idx + chunk_size, total_words)
    display_text = " ".join(words[start_idx:end_idx]).upper()
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 75)
    except:
        font = ImageFont.load_default()
        
    try:
        tw, th = draw.textsize(display_text, font=font)
    except AttributeError:
        bbox = draw.textbbox((0,0), display_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
    w, h = img.size
    x = (w - tw) // 2
    y = int(h * 0.75)
    
    try:
        draw.text((x, y), display_text, font=font, fill=(255, 200, 0), stroke_width=5, stroke_fill=(0,0,0))
    except TypeError:
        draw.text((x-3, y-3), display_text, font=font, fill=(0,0,0))
        draw.text((x+3, y+3), display_text, font=font, fill=(0,0,0))
        draw.text((x, y), display_text, font=font, fill=(255, 200, 0))
        
    return np.array(img)

def main():
    print("============================================================")
    print("🎬 BƯỚC 2.5: VIDEO COMPOSER (HẬU KỲ VÀ GHÉP NỐI)")
    print("============================================================")
    
    manifest_path = find_latest_manifest()
    if not manifest_path:
        print("❌ Không tìm thấy audio_manifest.json. Bạn đã chạy sinh âm thanh chưa?")
        return
        
    print(f"✅ Tìm thấy âm thanh mới nhất tại: {manifest_path}")
    
    with open(STORYBOARD_PATH, "r", encoding="utf-8") as f:
        storyboard = json.load(f)
    scenes_data = {sc["id"]: sc for sc in storyboard.get("scenes", [])}
    
    manifest_dir = os.path.dirname(manifest_path)
    final_clips = []
    
    # Đọc tuần tự các scene (1 đến 5)
    scene_ids = ["scene_01", "scene_02", "scene_03", "scene_04", "scene_05"]
    
    for sc_id in scene_ids:
        audio_abs_path = os.path.join(manifest_dir, f"{sc_id}.mp3")
        video_abs_path = os.path.join(GENERATED_SCENES_DIR, f"{sc_id}.mp4")
        
        if not os.path.exists(audio_abs_path):
            print(f"⚠️ Thiếu file Audio cho {sc_id}. Bỏ qua...")
            continue
        if not os.path.exists(video_abs_path):
            print(f"⚠️ Thiếu file Video cho {sc_id}. Bỏ qua...")
            continue
            
        print(f"⚙️ Đang xử lý đồng bộ {sc_id}...")
        audio_clip = AudioFileClip(audio_abs_path)
        video_clip = VideoFileClip(video_abs_path)
        
        # LOGIC ĐỒNG BỘ (TIMELINE SYNC): Audio là gốc (Master)
        # Nếu video ngắn hơn audio, lặp lại video. Nếu dài hơn, cắt bớt.
        if video_clip.duration < audio_clip.duration:
            video_clip = video_clip.fx(vfx.loop, duration=audio_clip.duration)
        else:
            video_clip = video_clip.subclip(0, audio_clip.duration)
            
        # Gắn âm thanh vào video
        video_clip = video_clip.set_audio(audio_clip)
        
        # Áp dụng thuật toán phụ đề
        scene_text = scenes_data.get(sc_id, {}).get("audio", {}).get("voice", "")
        if scene_text:
            def fl_fun(gf, t, text=scene_text, dur=video_clip.duration):
                return draw_subtitle_on_frame(gf(t), t, text, dur)
            video_clip = video_clip.fl(fl_fun, apply_to=['video'])
            
        final_clips.append(video_clip)
        
    if not final_clips:
        print("❌ Không có clip nào để ghép.")
        return
        
    print(f"\n🔗 Đang ghép {len(final_clips)} cảnh lại với nhau trên 1 Timeline duy nhất...")
    final_video = concatenate_videoclips(final_clips, method="compose")
    
    output_path = os.path.join(OUTPUT_DIR, "final_video_tiktok.mp4")
    print(f"⏳ Đang Render xuất file MP4... (Quá trình này mất khoảng 30s - 1 phút)")
    
    # Render với thông số chuẩn Tiktok (9:16, Ultrafast)
    final_video.write_videofile(
        output_path, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac", 
        preset="ultrafast", 
        threads=4,
        logger=None # Tắt thanh tiến trình rối mắt
    )
    
    print(f"\n🎉 HOÀN TẤT MVP! Video cuối cùng đã được lưu tại: {output_path}")

if __name__ == "__main__":
    main()
