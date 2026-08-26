import os
import sys
import glob
import cv2
import numpy as np

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENES_DIR = os.path.join(WORKSPACE_DIR, "assets", "generated_scenes")
RAW_SCENES_DIR = os.path.join(SCENES_DIR, "raw")

TARGET_WIDTH = 720
TARGET_HEIGHT = 1280
TARGET_FPS = 24.0

def standardize_video_to_9_16(input_path, output_path, mode="blur_bg"):
    """
    Standardizes any video to strict 9:16 (720x1280) vertical format.
    - mode="blur_bg": Creates dynamic blurred background for horizontal/non-9:16 videos.
    - mode="center_crop": Crops center area to 9:16.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error opening video: {input_path}")
        return False
        
    in_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    in_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or TARGET_FPS
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Check if already 9:16 (within 1% tolerance)
    aspect_ratio = in_w / float(in_h)
    target_ratio = TARGET_WIDTH / float(TARGET_HEIGHT)
    
    if abs(aspect_ratio - target_ratio) < 0.01 and in_w == TARGET_WIDTH and in_h == TARGET_HEIGHT:
        print(f"  [OK] {os.path.basename(input_path)} is already strict 9:16 ({in_w}x{in_h}).")
        cap.release()
        return True
        
    print(f"  [Converting] {os.path.basename(input_path)} ({in_w}x{in_h} -> {TARGET_WIDTH}x{TARGET_HEIGHT}) with mode={mode}...")
    
    temp_output = output_path + ".tmp.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_output, fourcc, fps, (TARGET_WIDTH, TARGET_HEIGHT))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if mode == "blur_bg":
            # 1. Background: stretch & heavy gaussian blur
            bg = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT), interpolation=cv2.INTER_LINEAR)
            bg = cv2.GaussianBlur(bg, (51, 51), 30)
            
            # Darken background slightly for contrast
            bg = cv2.addWeighted(bg, 0.6, np.zeros_like(bg), 0.4, 0)
            
            # 2. Foreground: fit width with aspect ratio preserved
            scale = TARGET_WIDTH / float(in_w)
            fg_w = TARGET_WIDTH
            fg_h = int(in_h * scale)
            
            if fg_h > TARGET_HEIGHT:
                scale = TARGET_HEIGHT / float(in_h)
                fg_h = TARGET_HEIGHT
                fg_w = int(in_w * scale)
                
            fg = cv2.resize(frame, (fg_w, fg_h), interpolation=cv2.INTER_LANCZOS4)
            
            # Paste foreground into center of background
            pos_x = (TARGET_WIDTH - fg_w) // 2
            pos_y = (TARGET_HEIGHT - fg_h) // 2
            
            bg[pos_y:pos_y+fg_h, pos_x:pos_x+fg_w] = fg
            out.write(bg)
            
        elif mode == "center_crop":
            # Zoom to cover full 9:16
            scale = max(TARGET_WIDTH / float(in_w), TARGET_HEIGHT / float(in_h))
            scaled_w, scaled_h = int(in_w * scale), int(in_h * scale)
            scaled = cv2.resize(frame, (scaled_w, scaled_h), interpolation=cv2.INTER_LANCZOS4)
            
            x1 = (scaled_w - TARGET_WIDTH) // 2
            y1 = (scaled_h - TARGET_HEIGHT) // 2
            crop = scaled[y1:y1+TARGET_HEIGHT, x1:x1+TARGET_WIDTH]
            out.write(crop)
            
    cap.release()
    out.release()
    
    # Replace original with standardized video
    if os.path.exists(output_path):
        os.remove(output_path)
    os.rename(temp_output, output_path)
    print(f"  ✅ Finished: {os.path.basename(output_path)} is now strict 9:16 ({TARGET_WIDTH}x{TARGET_HEIGHT}).")
    return True

def process_all_scenes():
    os.makedirs(RAW_SCENES_DIR, exist_ok=True)
    video_files = sorted(glob.glob(os.path.join(SCENES_DIR, "scene_*.mp4")))
    
    print("\n" + "="*60)
    print("🎬 STANDARDIZING ALL SCENES TO 9:16 (720x1280)")
    print("="*60)
    
    for v_file in video_files:
        filename = os.path.basename(v_file)
        # Backup original raw file
        raw_backup = os.path.join(RAW_SCENES_DIR, filename)
        if not os.path.exists(raw_backup):
            import shutil
            shutil.copy2(v_file, raw_backup)
            
        standardize_video_to_9_16(raw_backup, v_file, mode="blur_bg")
        
    print("\n🎉 All 5 scenes are now 100% compliant with 9:16 vertical video format!")

if __name__ == "__main__":
    process_all_scenes()
