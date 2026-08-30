from fastapi import APIRouter, UploadFile, File
from typing import List
from core.storage import storage

router = APIRouter()

@router.post("/{project_id}/init")
def init_project(project_id: str):
    """Khởi tạo cấu trúc thư mục cho dự án mới"""
    storage.init_project_workspace(project_id)
    return {"status": "success", "message": f"Dự án {project_id} đã được khởi tạo."}

@router.post("/{project_id}/upload")
async def upload_files(project_id: str, files: List[UploadFile] = File(...)):
    """Upload nhiều ảnh/video thô lên thư mục inputs của dự án"""
    uris = []
    for file in files:
        content = await file.read()
        uri = storage.save_input_file(project_id, file.filename, content)
        uris.append(uri)
    return {"status": "success", "file_uris": uris}

import os
@router.get("/list")
def list_projects():
    """Lấy danh sách các video đã render thành công"""
    projects = []
    if os.path.exists(storage.storage_dir):
        for pid in os.listdir(storage.storage_dir):
            final_vid = f"storage/{pid}/final/final_video_tiktok.mp4"
            if os.path.exists(storage.get_absolute_path(final_vid)):
                projects.append({
                    "project_id": pid,
                    "video_uri": final_vid
                })
    return {"status": "success", "projects": projects}
