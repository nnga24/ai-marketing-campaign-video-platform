import os
import sys
import json
import cv2
import numpy as np
from PIL import Image

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Path constants
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORYBOARD_PATH = os.path.join(WORKSPACE_DIR, "story-board", "ga_u_muoi_storyboard.json")
ASSETS_DIR = os.path.join(WORKSPACE_DIR, "assets")
INPUT_IMAGES_DIR = os.path.join(ASSETS_DIR, "inputs", "images")
PROMPTS_OUTPUT_PATH = os.path.join(ASSETS_DIR, "prompts", "video_scene_prompts.json")
SCENES_OUTPUT_DIR = os.path.join(ASSETS_DIR, "generated_scenes")

os.makedirs(INPUT_IMAGES_DIR, exist_ok=True)
os.makedirs(os.path.join(ASSETS_DIR, "prompts"), exist_ok=True)
os.makedirs(SCENES_OUTPUT_DIR, exist_ok=True)

def load_storyboard():
    with open(STORYBOARD_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_ai_video_prompts(storyboard):
    """
    Builds optimized prompt packs for AI Video Generators (Kling, Runway Gen-3, Luma, Minimax).
    """
    scenes = storyboard.get("scenes", [])
    prompt_pack = {
        "project": "Gà Ủ Muối Bếp Sạch Việt",
        "aspect_ratio": "9:16 (1080x1920)",
        "scenes": []
    }
    
    for sc in scenes:
        sc_id = sc["id"]
        purpose = sc["purpose"]
        vis = sc.get("visual", {})
        vis_type = vis.get("type", "text_to_video")
        
        # Build cinematic English prompt for AI Video models
        subject = vis.get("subject", "")
        action = vis.get("action", "")
        env = vis.get("environment", "")
        camera = vis.get("camera", {})
        cam_movement = camera.get("movement", "slow_push_in").replace("_", " ")
        cam_shot = camera.get("shot", "medium").replace("_", " ")
        lighting = vis.get("lighting", "natural lighting")
        style = vis.get("style", "realistic commercial")
        
        if vis_type == "image_to_video":
            prompt = f"Cinematic product commercial video, {cam_shot} shot with {cam_movement}. {action}. In {env}, {lighting}, {style}, 4k ultra high resolution, food commercial aesthetics, realistic fluid motion, no distortion."
            notes = f"Input Reference Image required: {sc.get('product', {}).get('asset_ids', [])}"
        else:
            prompt = f"Cinematic TikTok commercial video, {cam_shot} shot with {cam_movement}. {subject}, {action}. Environment: {env}. Lighting: {lighting}. Atmosphere: {vis.get('emotion', '')}. Style: {style}, 4k ultra detailed, photorealistic."
            notes = "Text-to-Video generation or stock/meme injection"

        prompt_pack["scenes"].append({
            "scene_id": sc_id,
            "purpose": purpose,
            "type": vis_type,
            "estimated_duration": sc.get("estimated_duration_seconds", 3),
            "ai_video_prompt": prompt,
            "negative_prompt": "blurry, low quality, distorted anatomy, morphing artifacts, extra limbs, watermark, amateur video, flickering",
            "camera_control": {
                "movement": cam_movement,
                "angle": camera.get("angle", "eye_level")
            },
            "notes": notes
        })
        
    with open(PROMPTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(prompt_pack, f, ensure_ascii=False, indent=2)
        
    print(f"Generated AI Video Prompts saved to: {PROMPTS_OUTPUT_PATH}")
    return prompt_pack

def create_motion_clip_from_image(image_path, output_path, duration_sec=3.0, fps=30, width=1080, height=1920, 
                                  motion_type="zoom_in", overlay_text="", overlay_anim="pop_up", scene_title=""):
    """
    Creates a high-quality, professional 9:16 vertical motion video clip locally for FREE.
    Includes camera pan/zoom, subtle vignette, dynamic lighting effects, and animated text overlays.
    """
    if not image_path or not os.path.exists(image_path):
        print(f"\n⚠️ [CẢNH BÁO] Scene '{scene_title}' bị thiếu ảnh đầu vào (reference_image)!")
        print(f"👉 Hướng dẫn: Hãy cung cấp một bức ảnh cho cảnh này hoặc gọi API để gen video tự động.")
        print(f"👉 Tạm thời hệ thống sẽ tạo Phông nền giữ chỗ (Placeholder) để không làm hỏng Video...\n")
        
        # Create a stylish dark gradient background with aesthetic graphic accents
        img = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            # Vertical gradient: dark indigo to deep slate
            ratio = y / float(height)
            img[y, :] = (int(30 + 15 * ratio), int(20 + 20 * ratio), int(40 + 35 * ratio))
        
        # Draw modern aesthetic grid & glow lines
        cv2.circle(img, (width // 2, height // 2), 320, (60, 50, 90), -1)
        cv2.circle(img, (width // 2, height // 2), 220, (80, 70, 120), -1)
        
        if scene_title:
            cv2.putText(img, scene_title, (width // 2 - 250, height // 2 - 80), 
                        cv2.FONT_HERSHEY_DUPLEX, 1.3, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        pil_img = Image.open(image_path).convert("RGB")
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    orig_h, orig_w = img.shape[:2]
    total_frames = int(duration_sec * fps)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    scale = max(width / orig_w, height / orig_h)
    base_w, base_h = int(orig_w * scale * 1.2), int(orig_h * scale * 1.2)
    resized = cv2.resize(img, (base_w, base_h), interpolation=cv2.INTER_LANCZOS4)
    
    for f in range(total_frames):
        progress = f / float(total_frames)
        
        # Smooth camera curve (ease-in-out)
        ease = 0.5 - 0.5 * np.cos(progress * np.pi)
        
        if motion_type == "zoom_in":
            current_zoom = 1.0 + 0.15 * ease
        elif motion_type == "zoom_out":
            current_zoom = 1.15 - 0.15 * ease
        elif motion_type == "pan_up":
            current_zoom = 1.08
        else:
            current_zoom = 1.05
            
        cur_w = int(width / current_zoom)
        cur_h = int(height / current_zoom)
        
        center_x = base_w // 2
        center_y = base_h // 2
        
        if motion_type == "pan_up":
            center_y = int((base_h // 2 + 60) - 120 * ease)
            
        x1 = max(0, min(base_w - cur_w, center_x - cur_w // 2))
        y1 = max(0, min(base_h - cur_h, center_y - cur_h // 2))
        
        crop = resized[y1:y1+cur_h, x1:x1+cur_w]
        frame = cv2.resize(crop, (width, height), interpolation=cv2.INTER_LINEAR)
        
        # Subtle vignette / lighting enhancement for commercial look
        if motion_type == "zoom_in":
            # Soft radial glow
            overlay = frame.copy()
            cv2.circle(overlay, (width // 2, height // 2), int(width * 0.6), (255, 240, 200), -1)
            cv2.addWeighted(overlay, 0.05 * ease, frame, 1.0 - 0.05 * ease, 0, frame)
            
        # Draw Animated Text Overlay if present
        if overlay_text:
            text_alpha = 1.0
            scale_text = 1.2
            if overlay_anim == "pop_up":
                scale_text = min(1.3, 0.8 + 0.5 * min(1.0, progress * 3))
            elif overlay_anim == "pulse":
                scale_text = 1.2 + 0.15 * np.sin(progress * np.pi * 4)
                
            # Text box position
            pos_y = height - 320 if overlay_anim != "pop_up" else height // 2 + 100
            
            # Text background badge
            (tw, th), _ = cv2.getTextSize(overlay_text, cv2.FONT_HERSHEY_DUPLEX, scale_text, 3)
            tx = max(40, (width - tw) // 2)
            
            # Badge background
            badge_overlay = frame.copy()
            cv2.rectangle(badge_overlay, (tx - 30, pos_y - th - 25), (tx + tw + 30, pos_y + 25), (0, 0, 0), -1)
            cv2.addWeighted(badge_overlay, 0.65, frame, 0.35, 0, frame)
            
            # Border & Glow text
            cv2.rectangle(frame, (tx - 30, pos_y - th - 25), (tx + tw + 30, pos_y + 25), (245, 180, 0), 3)
            cv2.putText(frame, overlay_text, (tx, pos_y), cv2.FONT_HERSHEY_DUPLEX, scale_text, (255, 255, 255), 3, cv2.LINE_AA)
            
        out.write(frame)
        
    out.release()
    print(f"Generated FREE Motion Scene Video: {output_path} ({duration_sec}s, {width}x{height} @ {fps}fps)")

def render_all_fallback_scenes(storyboard):
    """
    Renders 100% FREE professional 9:16 video clips for each scene in storyboard.
    """
    scenes = storyboard.get("scenes", [])
    os.makedirs(SCENES_OUTPUT_DIR, exist_ok=True)
    
    print("\n" + "="*60)
    print("🎬 RENDERING 100% FREE 9:16 VERTICAL SCENES (Offline Engine)")
    print("="*60)
    for sc in scenes:
        sc_id = sc["id"]
        duration = sc.get("estimated_duration_seconds", 3.0)
        output_file = os.path.join(SCENES_OUTPUT_DIR, f"{sc_id}.mp4")
        
        img_path = None
        overlay_info = sc.get("overlay", {})
        overlay_text = overlay_info.get("text", "") if overlay_info.get("enabled", False) else ""
        overlay_anim = overlay_info.get("animation", "none")
        
        scene_title = f"{sc_id.upper()} - {sc['purpose'].upper()}"
        
        ref_image = sc.get("visual", {}).get("reference_image")
        if ref_image:
            abs_img_path = os.path.join(WORKSPACE_DIR, ref_image)
            if os.path.exists(abs_img_path):
                img_path = abs_img_path
        
        cam_movement = sc.get("visual", {}).get("camera", {}).get("movement", "slow_push_in")
        motion_type = "zoom_in" if "push" in cam_movement else ("zoom_out" if "pull" in cam_movement else "pan_up")
        
        create_motion_clip_from_image(
            image_path=img_path or "",
            output_path=output_file,
            duration_sec=duration,
            fps=30,
            width=1080,
            height=1920,
            motion_type=motion_type,
            overlay_text=overlay_text,
            overlay_anim=overlay_anim,
            scene_title=scene_title
        )

try:
    from ai_video_api_client import AIVideoAPIClient
except ImportError:
    from scripts.ai_video_api_client import AIVideoAPIClient

def generate_scenes_via_api(storyboard, target_scene_id=None):
    """
    Fully automated generation of scenes using AI Video API (Fal / Replicate / Runway / Luma).
    """
    client = AIVideoAPIClient()
    scenes = storyboard.get("scenes", [])
    prompt_pack = build_ai_video_prompts(storyboard)
    
    print("\n" + "="*60)
    print(f"🚀 STARTING FULLY AUTOMATED AI VIDEO GENERATION (Provider: {client.provider.upper()})")
    print("="*60)
    
    for sc in prompt_pack["scenes"]:
        sc_id = sc["scene_id"]
        if target_scene_id and sc_id != target_scene_id:
            continue
            
        vis_type = sc["type"]
        prompt = sc["ai_video_prompt"]
        duration = sc["estimated_duration"]
        output_file = os.path.join(SCENES_OUTPUT_DIR, f"{sc_id}.mp4")
        
        # Determine image reference for Image-to-Video
        image_path = None
        if vis_type == "image_to_video":
            if sc_id == "scene_03":
                # Primary product image
                candidate = os.path.join(INPUT_IMAGES_DIR, "ga_u_muoi_image_01.png")
                if not os.path.exists(candidate):
                    candidate = os.path.join(INPUT_IMAGES_DIR, "ga_u_muoi_image_01.jpg")
                if os.path.exists(candidate):
                    image_path = candidate
            elif sc_id == "scene_05":
                # Packaging / brand image
                candidate = os.path.join(INPUT_IMAGES_DIR, "ga_u_muoi_packaging.png")
                if os.path.exists(candidate):
                    image_path = candidate
                    
        print(f"\n🎬 Processing [{sc_id}] ({sc['purpose'].upper()}) | Mode: {vis_type.upper()}")
        try:
            client.generate_video(
                prompt=prompt,
                visual_type=vis_type,
                image_path=image_path,
                duration_sec=duration,
                aspect_ratio="9:16",
                output_path=output_file
            )
            print(f"✅ Scene [{sc_id}] generated and saved: {output_file}")
        except Exception as e:
            print(f"❌ Error generating [{sc_id}]: {e}")
            print("   (Check your API key in .env or run with --render-preview for local test)")

def main():
    import sys
    storyboard = load_storyboard()
    prompt_pack = build_ai_video_prompts(storyboard)
    
    print("\n" + "="*60)
    print("🎬 STEP 8: VIDEO SCENE GENERATOR (Free Demo / Enterprise API)")
    print("="*60)
    print(f"Total Scenes: {len(prompt_pack['scenes'])}")
    for sc in prompt_pack["scenes"]:
        print(f"  [{sc['scene_id']}] ({sc['purpose'].upper()}) - Type: {sc['type']} - Est: {sc['estimated_duration']}s")
        
    use_api = "--api" in sys.argv or "-a" in sys.argv
    
    if use_api:
        # Enterprise Cloud API mode
        target_scene = None
        for i, arg in enumerate(sys.argv):
            if arg in ["--scene", "-s"] and i + 1 < len(sys.argv):
                target_scene = sys.argv[i+1]
        try:
            generate_scenes_via_api(storyboard, target_scene_id=target_scene)
        except Exception as e:
            print(f"\n⚠️ API execution encountered an issue: {e}")
            print("🔄 Falling back to 100% Free Local Motion Engine...")
            render_all_fallback_scenes(storyboard)
    else:
        # Default: 100% Free Local Python Motion Engine (Zero cost)
        print("\n🚀 Running Free Local Motion Engine (Default Mode - 0đ chi phí)...")
        render_all_fallback_scenes(storyboard)
        print("\n💡 Gợi ý:")
        print("  - Để sinh video qua Cloud API (Fal.ai / Replicate / Runway): python scripts/generate_video_scenes.py --api")
        print("  - Để chuẩn hóa toàn bộ 9:16: python scripts/standardize_scenes.py")

if __name__ == "__main__":
    main()
