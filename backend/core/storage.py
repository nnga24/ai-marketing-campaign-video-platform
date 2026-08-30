import os
import shutil
from typing import List, Optional
from core.config import settings

class StorageService:
    """
    Tầng Abstraction cho Lưu trữ.
    Tất cả các hàm Đọc/Ghi file đều đi qua đây. Tương lai dễ dàng đổi sang MinIO/S3.
    """
    def __init__(self):
        self.storage_dir = settings.STORAGE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_project_dir(self, project_id: str) -> str:
        return os.path.join(self.storage_dir, project_id)

    def init_project_workspace(self, project_id: str):
        """Khởi tạo cấu trúc thư mục chuẩn cho 1 dự án mới"""
        project_dir = self._get_project_dir(project_id)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, "inputs"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "voice"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "scenes"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "final"), exist_ok=True)

    def save_input_file(self, project_id: str, filename: str, content: bytes) -> str:
        """Lưu file ảnh/video người dùng upload"""
        return self.save_file(project_id, "inputs", filename, content)
        
    def save_file(self, project_id: str, subfolder: str, filename: str, content: bytes) -> str:
        """Lưu file bất kỳ vào thư mục con của dự án (inputs, voice, scenes...)"""
        filepath = os.path.join(self._get_project_dir(project_id), subfolder, filename)
        with open(filepath, "wb") as f:
            f.write(content)
        return f"storage/{project_id}/{subfolder}/{filename}"

    def get_absolute_path(self, relative_uri: str) -> str:
        """Chuyển đổi URI lưu trữ thành đường dẫn tuyệt đối (trên Local Disk)"""
        if relative_uri.startswith("storage/"):
            # storage/project_id/inputs/file.jpg -> backend/storage/project_id/...
            return os.path.join(settings.BASE_DIR, relative_uri)
        return relative_uri

    def read_text_file(self, relative_uri: str) -> Optional[str]:
        path = self.get_absolute_path(relative_uri)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def write_text_file(self, relative_uri: str, content: str) -> str:
        path = self.get_absolute_path(relative_uri)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return relative_uri

storage = StorageService()
