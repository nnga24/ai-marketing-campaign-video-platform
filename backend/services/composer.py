import os
import numpy as np
import textwrap
from PIL import Image, ImageDraw, ImageFont
from core.storage import storage
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx

class ComposerService:
    def draw_subtitle_on_frame(self, frame, t, text, total_duration):
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
            
        chunk_size = 4
        chunk_idx = current_word_idx // chunk_size
        start_idx = chunk_idx * chunk_size
        end_idx = min(start_idx + chunk_size, total_words)
        
        raw_text = " ".join(words[start_idx:end_idx]).upper()
        display_text = "\n".join(textwrap.wrap(raw_text, width=22))
        
        try:
            font = ImageFont.truetype("arialbd.ttf", 65)
        except:
            font = ImageFont.load_default()
            
        try:
            tw, th = draw.textsize(display_text, font=font)
        except AttributeError:
            bbox = draw.multiline_textbbox((0,0), display_text, font=font, align="center")
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            
        w, h = img.size
        x = (w - tw) // 2
        y = int(h * 0.75)
        
        try:
            draw.multiline_text((x, y), display_text, font=font, fill=(255, 200, 0), stroke_width=4, stroke_fill=(0,0,0), align="center")
        except TypeError:
            draw.multiline_text((x-3, y-3), display_text, font=font, fill=(0,0,0), align="center")
            draw.multiline_text((x+3, y+3), display_text, font=font, fill=(0,0,0), align="center")
            draw.multiline_text((x, y), display_text, font=font, fill=(255, 200, 0), align="center")
            
        return np.array(img)

    def compose_video(self, project_id: str, scene_data_list: list) -> str:
        """
        Ghép nối video, âm thanh và phụ đề.
        scene_data_list: Danh sách chứa dict: {"scene_id": "...", "video_uri": "...", "audio_uri": "...", "text": "..."}
        """
        final_clips = []
        for item in scene_data_list:
            audio_path = storage.get_absolute_path(item['audio_uri'])
            video_path = storage.get_absolute_path(item['video_uri'])
            text = item.get('text', "")
            
            if not os.path.exists(audio_path) or not os.path.exists(video_path):
                print(f"Bỏ qua cảnh vì thiếu file: {item['scene_id']}")
                continue
                
            audio_clip = AudioFileClip(audio_path)
            video_clip = VideoFileClip(video_path)
            
            # Đồng bộ thời gian
            if video_clip.duration < audio_clip.duration:
                video_clip = video_clip.fx(vfx.loop, duration=audio_clip.duration)
            else:
                video_clip = video_clip.subclip(0, audio_clip.duration)
                
            video_clip = video_clip.set_audio(audio_clip)
            
            # Gắn phụ đề
            if text:
                def make_fl(txt, dur):
                    return lambda gf, t: self.draw_subtitle_on_frame(gf(t), t, txt, dur)
                video_clip = video_clip.fl(make_fl(text, video_clip.duration), apply_to=['video'])
                
            final_clips.append(video_clip)
            
        if not final_clips:
            raise ValueError("Không có clip nào hợp lệ để ghép.")
            
        final_video = concatenate_videoclips(final_clips, method="compose")
        filename = "final_video_tiktok.mp4"
        output_path = os.path.join(storage._get_project_dir(project_id), "final", filename)
        
        final_video.write_videofile(
            output_path, 
            fps=30, 
            codec="libx264", 
            audio_codec="aac", 
            preset="ultrafast", 
            threads=4,
            logger=None
        )
        
        return f"storage/{project_id}/final/{filename}"

composer_service = ComposerService()
