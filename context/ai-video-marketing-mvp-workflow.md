# AI Video Marketing MVP — End-to-End Workflow

## 1. Mục tiêu

Xây workflow tự động:

> Doanh nghiệp cung cấp thông tin + ảnh sản phẩm → hệ thống tự tạo concept → script → storyboard → video scenes → voice → subtitle → đồng bộ timeline → render → kiểm tra → trả về video quảng cáo hoàn chỉnh.

MVP không cần người mở CapCut/Premiere để chỉnh thủ công.

---

## 2. Tổng quan (Human-in-the-Loop)

```text
[ DOANH NGHIỆP / USER ] (Upload Ảnh, Video Meme, Yêu cầu)
           ↓
[ AI GEN 1 ] Phân tích Business Data, Target Audience, Angles
           ↓
🛑 [ TOUCHPOINT 1 ] User xem, chỉnh sửa và chốt Business Data
           ↓
[ AI GEN 2 ] Sinh kịch bản và Storyboard chi tiết
           ↓
🛑 [ TOUCHPOINT 2 ] User sửa thoại, điều chỉnh Visual, chọn giọng
           ↓
[ AI GEN 3 ] Gọi API sinh Voice (TTS) & Video Scenes (Motion/AI)
           ↓
🛑 [ TOUCHPOINT 3 ] User duyệt âm thanh và các cảnh video
           ↓
[ AI COMPOSER ] Ghép nối (Timeline sync), Subtitle, BGM, Render
           ↓
🛑 [ TOUCHPOINT 4 ] Final Review & Chốt Video Cuối
```

---

## 3. Business Data

Đầu vào từ doanh nghiệp:

### Product
- Tên sản phẩm
- Mô tả
- Tính năng
- Lợi ích
- Giá
- USP
- Website

### Brand
- Logo
- Màu thương hiệu
- Font
- Brand guideline
- Tone of voice

### Audience
- Độ tuổi
- Nghề nghiệp
- Pain point
- Nhu cầu
- Sở thích

### Marketing Objective
- Awareness
- Engagement
- Lead generation
- Sales
- Remarketing

### Campaign
- Platform: TikTok / Facebook / Instagram / YouTube
- Video duration
- Aspect ratio
- CTA

### Assets

```text

product.jpg
logo.png
packaging.jpg
product-detail.jpg
brand-guide.pdf

```

---

## 4. Marketing Brief

LLM chuyển business data thành brief có cấu trúc.

```json
{
  "objective": "product awareness",
  "audience": "office workers 25-40",
  "pain_point": "back discomfort",
  "key_message": "comfortable ergonomic support",
  "cta": "Discover X1",
  "platform": "TikTok",
  "duration": 15
}
```

Mục đích: biến dữ liệu doanh nghiệp thành một mục tiêu quảng cáo cụ thể.

---

## 5. Creative Idea

Xác định video sẽ kể câu chuyện gì.

Ví dụ:

> Một ngày làm việc dài trở nên thoải mái hơn.

Cấu trúc thường dùng:

```text
Hook
↓
Problem
↓
Solution
↓
Benefit
↓
CTA
```

---

## 6. Script + Storyboard

### Script

```text
0–4s:
"Bạn ngồi 8 tiếng mỗi ngày?"

4–8s:
"Hãy thử Ergonomic Chair X1."

8–13s:
"Tựa lưng công thái học giúp bạn thoải mái
hơn trong những ngày làm việc dài."

13–15s:
"Khám phá X1 ngay hôm nay."
```

### Storyboard

| Time | Voice | Visual |
|---|---|---|
| 0–4s | Bạn ngồi 8 tiếng mỗi ngày? | Người ngồi làm việc |
| 4–8s | Hãy thử X1 | Product hero shot |
| 8–13s | Lumbar support... | Close-up tựa lưng |
| 13–15s | Khám phá X1 | Product + logo + CTA |

**Nguyên tắc:** Audio/script là xương sống của timeline; visual được map vào timeline dựa trên nội dung đang được nói.

---


## 7. Generate Voice ( khá khó )

```text
Script
  ↓
TTS
  ↓
voice.mp3
```

Có thể dùng:
- ElevenLabs
- OpenAI TTS
- Google TTS
- Local TTS

Demo có thể dùng giải pháp miễn phí/local.

---

## 8. Generate Visual / Video Scenes ( khá khó )

Không nhất thiết tạo một video 15 giây duy nhất. Chia thành scene:

```text
Scene 1 — 0–4s
Office worker

Scene 2 — 4–8s
Product hero shot

Scene 3 — 8–13s
Lumbar support close-up

Scene 4 — 13–15s
Product + CTA
```

### Image → Video

```text
product.jpg
    +
"slow camera push-in"
    ↓
Kling / Runway / Veo
    ↓
scene2.mp4
```

Ảnh sản phẩm là asset/reference để AI tạo chuyển động.

---

## 9. Audio/Visual Synchronization ( khá khó ) + công cụ 

Không chỉ nối:

```text
Scene 1 → Scene 2 → Scene 3
```

Mà phải có timeline:

```text
0s       4s       8s              15s
│--------│--------│----------------│
 Scene 1  Scene 2        Scene 3
```

Lấy timestamp từ voice:

```text
voice.mp3
   ↓
Whisper
   ↓
timestamps
```

Ví dụ:

```json
[
  {
    "start": 0.0,
    "end": 3.8,
    "text": "Bạn ngồi 8 tiếng mỗi ngày?"
  },
  {
    "start": 3.8,
    "end": 7.9,
    "text": "Hãy thử Ergonomic Chair X1."
  },
  {
    "start": 7.9,
    "end": 14.8,
    "text": "Chiếc ghế được thiết kế..."
  }
]
```

Nếu duration video không khớp:
- Trim
- Extend
- Freeze frame
- Speed adjustment
- Generate lại scene

---

## 10. Subtitle ( khó )

```text
voice.mp3
   ↓
Whisper
   ↓
SRT / VTT
```

Subtitle được đưa vào rendering pipeline.

---

## 11. Build Timeline

Backend kết hợp:

```text
Storyboard
+
Video scenes
+
Voice timestamps
+
Subtitle
+
Logo
+
Music
```

Timeline:

```text
VIDEO TRACK
────────────────────────────────
Scene 1 | Scene 2 | Scene 3 | CTA

VOICE TRACK
────────────────────────────────
Voice ──────────────────────────

MUSIC TRACK
────────────────────────────────
Music ──────────────────────────

SUBTITLE TRACK
────────────────────────────────
Subtitle ───────────────────────

OVERLAY
────────────────────────────────
Logo                  CTA
```

---

## 12. Video Rendering

Không dùng CapCut/Premiere trong workflow tự động.

### MVP: FFmpeg

Input:

```text
scene1.mp4
scene2.mp4
scene3.mp4
scene4.mp4

voice.mp3
music.mp3
subtitle.srt
logo.png
```

FFmpeg:
- Concatenate video
- Trim/resize
- Mix audio
- Add music
- Add subtitle
- Add logo
- Encode

Output:

```text
final.mp4
```

### Alternative
- Shotstack
- Creatomate

MVP nên ưu tiên FFmpeg để giảm chi phí.

---

## 13. Quality Check

### Technical
- File tồn tại
- Duration đúng
- Resolution đúng
- Audio tồn tại
- Subtitle tồn tại
- Encoding hợp lệ

### Content
- Đúng sản phẩm
- Logo đúng
- Không có visual artifact
- Text không lỗi
- CTA xuất hiện

### Marketing
- Có hook
- Có product
- Có benefit
- Có CTA

Nếu fail:

```text
Quality Check
      ↓
   FAILED
      ↓
Regenerate Scene
      ↓
Render lại
```

---

## 14. Output

Ví dụ:

```text
final.mp4
15 seconds
9:16
1080x1920
Voice
Music
Subtitle
Logo
CTA
```

---

## 15. Bộ công cụ MVP

| Chức năng | Công cụ đề xuất |
|---|---|
| LLM | Gemini / ChatGPT / local LLM |
| Marketing planning | LLM |
| Script | LLM |
| Storyboard | LLM |
| Image generation | Flux / Stable Diffusion |
| Image → Video | Kling / Hugging Face / model local |
| Voice | Local TTS / free TTS |
| Transcript | Whisper local |
| Subtitle | Whisper + SRT |
| Timeline | Code của hệ thống |
| Rendering | FFmpeg |
| Storage | Local filesystem |
| Backend | Spring Boot |
| Frontend | Vue / React |

---

## 16. Kiến trúc MVP

```text
                    Vue / React
                         │
                         ↓
                    Spring Boot
                         │
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
 Marketing Planner   Asset Manager    Video Generator
       │                                   │
       ↓                                   ↓
      LLM                              AI Video
       │
       ↓
 Script + Storyboard
       │
       ├──────────────────┐
       ↓                  ↓
    TTS Service      Visual Generator
       ↓                  ↓
   voice.mp3          scenes.mp4
       │                  │
       ↓                  │
    Whisper               │
       ↓                  │
  timestamps              │
       │                  │
       └────────┬─────────┘
                ↓
          Timeline Engine
                ↓
             FFmpeg
                ↓
          Quality Check
                ↓
            final.mp4
```

---

## 17. Input → Processing → Output

### Input

```text
Business
├── Product information
├── Brand information
├── Target audience
├── Marketing objective
├── Campaign/platform
└── Assets
    ├── Product images
    ├── Logo
    └── Brand guideline
```

### Processing

```text
Business Data
    ↓
Marketing Brief
    ↓
Creative Idea
    ↓
Script
    ↓
Storyboard
    ↓
Voice
    ↓
Visual Scenes
    ↓
Timestamp
    ↓
Timeline
    ↓
Subtitle
    ↓
Rendering
    ↓
Quality Check
```

### Output

```text
final.mp4
```

---

## 18. Kịch bản demo (Interactive Flow)

### Bước 1: User cung cấp đầu vào
```text
Upload: 
- 2 ảnh sản phẩm (product.jpg, packaging.png)
- 1 video meme (meme_reaction.mp4)
Yêu cầu: "Làm 1 video tiktok hài hước bán Gà Ủ Muối"
```

### Bước 2: AI Phân tích & User Chốt (Touchpoint 1)
```text
Hệ thống: "Dựa vào dữ liệu, tệp khách hàng là Dân văn phòng bận rộn. Angle: Mệt mỏi sau giờ làm, thèm đồ ăn sẵn ngon. Mời bạn duyệt cấu trúc."
User: "Ok, đổi tệp khách hàng sang gen Z nữa."
Hệ thống: Cập nhật Business Data.
```

### Bước 3: AI Sinh Storyboard & User Chốt (Touchpoint 2)
```text
Hệ thống: Trình bày Storyboard 5 scenes.
User: "Sửa lại câu hook ở scene 1 thành: Đi làm về mệt thì ăn gì cho bốc? Chọn giọng đọc Nam Trầm."
Hệ thống: Cập nhật Storyboard JSON.
```

### Bước 4: AI Sinh Assets & User Chốt (Touchpoint 3)
```text
Hệ thống: Đã sinh ra 5 file audio mp3 và 5 file video mp4.
User: "Nghe thử file audio 1... Ok duyệt. Video scene 3 hơi tối, làm sáng lên tí."
Hệ thống: Sinh lại Video scene 3. User chốt toàn bộ.
```

### Bước 5: Render & Final Review (Touchpoint 4)
```text
Hệ thống: Đã ghép nối xong.
FINAL VIDEO
[▶ Play Video]
User: "Tuyệt vời, chốt!"
```

---

## 19. Giảm chi phí cho Demo

Không cần AI generate mọi scene.

Ví dụ:

```text
Scene 1
Ảnh + zoom bằng FFmpeg
        ↓
Scene 2
AI Image → Video
        ↓
Scene 3
Ảnh + zoom bằng FFmpeg
        ↓
Scene 4
Ảnh + text + CTA bằng FFmpeg
```

Chỉ một scene cần AI video generation.

Các phần còn lại:
- TTS: local/free
- Whisper: local
- Subtitle: local
- FFmpeg: local
- Storage: local
- Spring Boot: local

Chi phí cloud chủ yếu còn AI video generation nếu dùng dịch vụ bên ngoài.

---

## 20. Những thứ không nên làm trong MVP

Chưa cần:
- CRM
- Facebook Ads automation
- TikTok Ads automation
- Google Ads
- Kafka
- Kubernetes
- Microservices
- Recommendation engine
- Autonomous Marketing Agent
- Analytics platform
- Video editor UI
- Human manual editing

MVP chỉ cần chứng minh:

> Product information + product image → AI marketing concept → script → storyboard → visual scenes → voice → synchronized subtitle → automatic rendering → final advertising video.

---

## 21. Keywords nghiên cứu

### AI Marketing
```text
AI creative automation
AI marketing automation
AI advertising creative generation
AI video marketing
```

### Video Generation
```text
AI video generation pipeline
image to video
text to video
product image to video
AI video generation API
```

### Video Automation
```text
programmatic video generation
programmatic video editing
automated video composition
video rendering API
JSON video timeline
```

### Audio/Video Sync
```text
audio visual synchronization
Whisper timestamps
Whisper word timestamps
TTS timestamp alignment
subtitle generation pipeline
```

### Rendering
```text
FFmpeg automated video generation
FFmpeg video composition
FFmpeg audio mixing
FFmpeg subtitle overlay
```

---

## 22. Tư duy kiến trúc quan trọng nhất

Đừng coi hệ thống đơn giản là:

```text
AI → tạo video
```

Mà:

```text
                    MARKETING
                       │
                       ↓
                 CREATIVE PLAN
                       │
                       ↓
                  VIDEO PLAN
                       │
            ┌──────────┴──────────┐
            ↓                     ↓
         AUDIO                  VISUAL
            │                     │
            ↓                     ↓
           TTS                AI VIDEO
            │                     │
            └──────────┬──────────┘
                       ↓
                    TIMELINE
                       ↓
                    RENDER
                       ↓
                  FINAL VIDEO
```

**AI Video Generator chỉ là một module trong hệ thống.**

Giá trị lớn hơn của sản phẩm nằm ở việc biến dữ liệu doanh nghiệp + mục tiêu marketing thành một creative có cấu trúc, rồi tự động phối hợp audio, visual, subtitle và timeline để tạo video cuối cùng.
