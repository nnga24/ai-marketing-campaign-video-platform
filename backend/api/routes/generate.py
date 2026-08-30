from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import json
import os

from services.llm_gemini import llm_service
from services.tts_service import tts_service
from services.image_gen import image_gen
from services.motion_engine import motion_engine
from services.composer import composer_service
from core.storage import storage

router = APIRouter()

from typing import List, Optional

class BusinessDataRequest(BaseModel):
    project_id: str
    product_info: str
    images: Optional[List[str]] = None

class StoryboardRequest(BaseModel):
    project_id: str
    business_data: dict
    
class AssetsRequest(BaseModel):
    project_id: str
    voice_id: Optional[str] = None
    
class VoiceTestRequest(BaseModel):
    project_id: str
    text: str
    voice_id: str

@router.post("/business-data")
def generate_business_data(req: BusinessDataRequest):
    data = llm_service.generate_business_data(req.product_info, req.images)
    storage.write_text_file(f"storage/{req.project_id}/business_data.json", json.dumps(data, ensure_ascii=False))
    return data

@router.post("/test-voice")
def test_voice(req: VoiceTestRequest):
    uri = tts_service.generate_voice(req.project_id, "test_voice", req.text, req.voice_id)
    return {"status": "success", "audio_uri": uri}

@router.post("/storyboard")
def generate_storyboard(req: StoryboardRequest):
    data = llm_service.generate_storyboard(req.business_data)
    storage.write_text_file(f"storage/{req.project_id}/storyboard.json", json.dumps(data, ensure_ascii=False, indent=2))
    return data

@router.post("/assets")
def generate_assets(req: AssetsRequest):
    """
    Sinh toàn bộ Voice, Ảnh và Cắt Cảnh (Motion) cho toàn bộ kịch bản.
    """
    storyboard_json = storage.read_text_file(f"storage/{req.project_id}/storyboard.json")
    if not storyboard_json:
        return {"error": "Không tìm thấy storyboard.json. Hãy sinh Kịch bản trước."}
        
    storyboard = json.loads(storyboard_json)
    results = []
    
    input_dir = os.path.join(storage._get_project_dir(req.project_id), "inputs")
    uploaded_images = []
    if os.path.exists(input_dir):
        for f in os.listdir(input_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not f.startswith('ai_gen_'):
                uploaded_images.append(f"storage/{req.project_id}/inputs/{f}")
    
    for index, sc in enumerate(storyboard.get("scenes", [])):
        sc_id = sc["id"]
        text = sc.get("audio", {}).get("voice", "")
        img_prompt = f"{sc.get('visual', {}).get('subject')} in {sc.get('visual', {}).get('environment')}, cinematic 8k, professional lighting"
        
        # 1. Gen Voice
        print(f"[{sc_id}] Generating Voice...")
        audio_uri = tts_service.generate_voice(req.project_id, sc_id, text, req.voice_id)
        
        # 2. Gen Image or Use Uploaded
        if uploaded_images:
            img_uri = uploaded_images[index % len(uploaded_images)]
            print(f"[{sc_id}] Using uploaded image: {img_uri}")
        else:
            print(f"[{sc_id}] Generating Image...")
            img_uri = image_gen.generate_image(req.project_id, sc_id, img_prompt)
        
        # 3. Gen Motion
        print(f"[{sc_id}] Generating Motion...")
        video_uri = motion_engine.generate_scene(req.project_id, sc_id, img_uri)
        
        results.append({
            "scene_id": sc_id,
            "audio_uri": audio_uri,
            "image_uri": img_uri,
            "video_uri": video_uri,
            "text": text
        })
        
    # Lưu lại trạng thái assets
    storage.write_text_file(f"storage/{req.project_id}/assets_manifest.json", json.dumps(results, ensure_ascii=False, indent=2))
    return {"status": "success", "assets": results}

@router.post("/compose")
def compose_video(req: AssetsRequest):
    """
    Ghép toàn bộ Audio + Video Scenes + Phụ đề thành Video MP4 duy nhất.
    """
    manifest_json = storage.read_text_file(f"storage/{req.project_id}/assets_manifest.json")
    if not manifest_json:
        return {"error": "Chưa sinh Assets."}
        
    manifest = json.loads(manifest_json)
    print("Rendering final video...")
    final_uri = composer_service.compose_video(req.project_id, manifest)
    return {"status": "success", "final_video_uri": final_uri}
