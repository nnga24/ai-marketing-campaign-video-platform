import os
import cv2
import numpy as np
from core.storage import storage

class MotionEngineService:
    def generate_scene(self, project_id: str, scene_id: str, image_uri: str, duration: float = 3.0) -> str:
        """Tạo video zoom nhẹ (Ken Burns effect) từ ảnh tĩnh"""
        image_path = storage.get_absolute_path(image_uri)
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Không tìm thấy ảnh tại {image_path}")
            
        h, w = img.shape[:2]
        target_w, target_h = 1080, 1920
        aspect_img = w / h
        aspect_target = target_w / target_h
        
        if aspect_img > aspect_target:
            new_w = int(h * aspect_target)
            offset = (w - new_w) // 2
            img = img[:, offset:offset+new_w]
        else:
            new_h = int(w / aspect_target)
            offset = (h - new_h) // 2
            img = img[offset:offset+new_h, :]
            
        img = cv2.resize(img, (target_w, target_h))
        h, w = 1920, 1080
        fps = 30
        total_frames = int(duration * fps)
        
        filename = f"{scene_id}.mp4"
        output_path = os.path.join(storage._get_project_dir(project_id), "scenes", filename)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        for i in range(total_frames):
            progress = i / max(1, (total_frames - 1))
            # Hiệu ứng Zoom in 10%
            scale = 1.0 + (0.1 * progress) 
            
            new_w = int(w / scale)
            new_h = int(h / scale)
            
            x = (w - new_w) // 2
            y = (h - new_h) // 2
            
            cropped = img[y:y+new_h, x:x+new_w]
            resized = cv2.resize(cropped, (w, h))
            out.write(resized)
            
        out.release()
        return f"storage/{project_id}/scenes/{filename}"

motion_engine = MotionEngineService()
