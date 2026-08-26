import os
import sys
import time
import json
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables
load_dotenv()

class AIVideoAPIClient:
    """
    Unified AI Video Generation Client supporting multiple providers:
    - Fal.ai (Kling 1.5, Minimax Hailuo, Luma, Wan 2.1)
    - Replicate (Kling, Minimax, Wan 2.1, SVD)
    - Runway (Gen-3 Alpha Turbo)
    - Luma AI (Dream Machine API)
    """

    def __init__(self, provider=None):
        self.provider = provider or os.getenv("AI_VIDEO_PROVIDER", "fal").lower()
        self.fal_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        self.runway_secret = os.getenv("RUNWAY_API_SECRET")
        self.luma_key = os.getenv("LUMA_API_KEY")
        
    def _image_to_data_uri(self, image_path: str) -> str:
        """Converts local image to base64 Data URI."""
        ext = Path(image_path).suffix.lower().replace(".", "")
        if ext == "jpg":
            ext = "jpeg"
        with open(image_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/{ext};base64,{b64_data}"

    def generate_video(self, prompt: str, visual_type: str = "text_to_video", 
                       image_path: str = None, duration_sec: float = 5.0, 
                       aspect_ratio: str = "9:16", output_path: str = None) -> str:
        """
        Main entrypoint: Generates video scene from text prompt or image reference.
        """
        print(f"\n[AI Video API] Dispatching scene generation ({self.provider.upper()})...")
        print(f"  Mode: {visual_type.upper()}")
        print(f"  Aspect Ratio: {aspect_ratio}, Duration: {duration_sec}s")
        print(f"  Prompt: {prompt[:100]}...")

        if self.provider == "fal":
            video_url = self._generate_fal(prompt, visual_type, image_path, duration_sec, aspect_ratio)
        elif self.provider == "replicate":
            video_url = self._generate_replicate(prompt, visual_type, image_path, duration_sec, aspect_ratio)
        elif self.provider == "runway":
            video_url = self._generate_runway(prompt, visual_type, image_path, duration_sec, aspect_ratio)
        elif self.provider == "luma":
            video_url = self._generate_luma(prompt, visual_type, image_path, duration_sec, aspect_ratio)
        else:
            raise ValueError(f"Unsupported AI Video provider: {self.provider}")

        if video_url and output_path:
            self._download_video(video_url, output_path)
            return output_path
        return video_url

    # -------------------------------------------------------------
    # 1. FAL.AI ADAPTER (Recommended: Kling 1.5, Minimax, Wan 2.1)
    # -------------------------------------------------------------
    def _generate_fal(self, prompt: str, visual_type: str, image_path: str, duration_sec: float, aspect_ratio: str) -> str:
        if not self.fal_key:
            raise ValueError("FAL_KEY is missing in environment/.env file! Please set FAL_KEY.")

        headers = {
            "Authorization": f"Key {self.fal_key}",
            "Content-Type": "application/json"
        }

        # Select model: Kling 1.5 Standard (High quality & cost-effective)
        if visual_type == "image_to_video" and image_path and os.path.exists(image_path):
            endpoint = "https://queue.fal.run/fal-ai/kling-video/v1.5/standard/image-to-video"
            image_uri = self._image_to_data_uri(image_path)
            payload = {
                "prompt": prompt,
                "image_url": image_uri,
                "aspect_ratio": aspect_ratio,
                "duration": "5"
            }
        else:
            endpoint = "https://queue.fal.run/fal-ai/kling-video/v1.5/standard/text-to-video"
            payload = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "duration": "5"
            }

        # Submit request to Queue
        print(f"[Fal.ai] Submitting job to {endpoint}...")
        resp = requests.post(endpoint, headers=headers, json=payload)
        
        if resp.status_code == 403:
            err_json = {}
            try:
                err_json = resp.json()
            except Exception:
                pass
            if "Exhausted balance" in str(err_json):
                raise RuntimeError("⚠️ Tài khoản Fal.ai của bạn đã hết số dư (Exhausted balance). Vui lòng nạp thêm credit ($5 - $10) tại: https://fal.ai/dashboard/billing để tiếp tục sinh video tự động.")
            else:
                raise RuntimeError(f"Fal.ai 403 Forbidden: {resp.text}")
                
        resp.raise_for_status()
        data = resp.json()
        
        request_id = data.get("request_id")
        status_url = data.get("status_url")
        response_url = data.get("response_url")

        # Poll status until finished
        print(f"[Fal.ai] Job submitted (ID: {request_id}). Waiting for video rendering...")
        while True:
            time.sleep(5)
            st_resp = requests.get(status_url, headers=headers)
            st_resp.raise_for_status()
            st_data = st_resp.json()
            status = st_data.get("status")
            print(f"  Status: {status}...")

            if status == "COMPLETED":
                res_resp = requests.get(response_url, headers=headers)
                res_resp.raise_for_status()
                res_data = res_resp.json()
                video_url = res_data.get("video", {}).get("url") or res_data.get("video_url")
                print(f"[Fal.ai] Video generated successfully: {video_url}")
                return video_url
            elif status in ["FAILED", "CANCELLED"]:
                raise RuntimeError(f"Fal.ai video generation failed: {st_data}")

    # -------------------------------------------------------------
    # 2. REPLICATE ADAPTER (Kling / Minimax / Wan 2.1)
    # -------------------------------------------------------------
    def _generate_replicate(self, prompt: str, visual_type: str, image_path: str, duration_sec: float, aspect_ratio: str) -> str:
        if not self.replicate_token:
            raise ValueError("REPLICATE_API_TOKEN is missing in environment/.env file!")

        headers = {
            "Authorization": f"Bearer {self.replicate_token}",
            "Content-Type": "application/json"
        }

        # Model version for Kling 1.5 standard / Wan 2.1
        if visual_type == "image_to_video" and image_path and os.path.exists(image_path):
            version = "kwaivgi/kling-v1.5-standard"
            image_uri = self._image_to_data_uri(image_path)
            payload = {
                "version": "latest",
                "input": {
                    "prompt": prompt,
                    "start_image": image_uri,
                    "aspect_ratio": aspect_ratio,
                    "duration": 5
                }
            }
        else:
            payload = {
                "version": "latest",
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio
                }
            }

        endpoint = "https://api.replicate.com/v1/models/kwaivgi/kling-v1.5-standard/predictions"
        resp = requests.post(endpoint, headers=headers, json=payload)
        resp.raise_for_status()
        pred = resp.json()
        
        poll_url = pred["urls"]["get"]
        print(f"[Replicate] Job submitted. Polling {poll_url}...")
        while True:
            time.sleep(5)
            p_resp = requests.get(poll_url, headers=headers)
            p_resp.raise_for_status()
            p_data = p_resp.json()
            status = p_data.get("status")
            print(f"  Status: {status}...")
            if status == "succeeded":
                output = p_data.get("output")
                video_url = output if isinstance(output, str) else output[0]
                return video_url
            elif status in ["failed", "canceled"]:
                raise RuntimeError(f"Replicate generation failed: {p_data.get('error')}")

    # -------------------------------------------------------------
    # 3. RUNWAY ADAPTER (Gen-3 Alpha Turbo)
    # -------------------------------------------------------------
    def _generate_runway(self, prompt: str, visual_type: str, image_path: str, duration_sec: float, aspect_ratio: str) -> str:
        if not self.runway_secret:
            raise ValueError("RUNWAY_API_SECRET is missing in environment/.env file!")

        headers = {
            "Authorization": f"Bearer {self.runway_secret}",
            "X-Runway-Version": "2024-09-13",
            "Content-Type": "application/json"
        }

        endpoint = "https://api.dev.runwayml.com/v1/image_to_video"
        image_uri = self._image_to_data_uri(image_path) if image_path and os.path.exists(image_path) else None
        
        payload = {
            "promptImage": image_uri,
            "promptText": prompt,
            "model": "gen3a_turbo",
            "duration": 5,
            "ratio": "768:1280" if aspect_ratio == "9:16" else "1280:768"
        }

        resp = requests.post(endpoint, headers=headers, json=payload)
        resp.raise_for_status()
        task_id = resp.json().get("id")
        
        status_url = f"https://api.dev.runwayml.com/v1/tasks/{task_id}"
        print(f"[Runway] Job submitted (Task: {task_id}). Polling...")
        while True:
            time.sleep(5)
            s_resp = requests.get(status_url, headers=headers)
            s_resp.raise_for_status()
            s_data = s_resp.json()
            status = s_data.get("status")
            print(f"  Status: {status}...")
            if status == "SUCCEEDED":
                return s_data["output"][0]
            elif status in ["FAILED", "CANCELLED"]:
                raise RuntimeError(f"Runway generation failed: {s_data}")

    # -------------------------------------------------------------
    # 4. LUMA DREAM MACHINE ADAPTER
    # -------------------------------------------------------------
    def _generate_luma(self, prompt: str, visual_type: str, image_path: str, duration_sec: float, aspect_ratio: str) -> str:
        if not self.luma_key:
            raise ValueError("LUMA_API_KEY is missing in environment/.env file!")

        headers = {
            "Authorization": f"Bearer {self.luma_key}",
            "Content-Type": "application/json"
        }

        endpoint = "https://api.lumalabs.ai/dream-machine/v1/generations"
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "loop": False
        }
        if image_path and os.path.exists(image_path):
            payload["keyframes"] = {
                "frame0": {
                    "type": "image",
                    "url": self._image_to_data_uri(image_path)
                }
            }

        resp = requests.post(endpoint, headers=headers, json=payload)
        resp.raise_for_status()
        gen_id = resp.json().get("id")
        
        status_url = f"https://api.lumalabs.ai/dream-machine/v1/generations/{gen_id}"
        print(f"[Luma] Job submitted (ID: {gen_id}). Polling...")
        while True:
            time.sleep(5)
            s_resp = requests.get(status_url, headers=headers)
            s_resp.raise_for_status()
            s_data = s_resp.json()
            state = s_data.get("state")
            print(f"  State: {state}...")
            if state == "completed":
                return s_data["assets"]["video"]
            elif state in ["failed", "dreaming_failed"]:
                raise RuntimeError(f"Luma generation failed: {s_data.get('failure_reason')}")

    def _download_video(self, url: str, output_path: str):
        print(f"[Download] Downloading video stream to: {output_path}...")
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[Download] Saved scene file: {output_path} ({os.path.getsize(output_path)} bytes)")
