TTS Workflow Plan

1. Mục tiêu

Xây dựng workflow Text-to-Speech cho hệ thống tạo video.

Phạm vi của workflow:

Storyboard + TTS Config
        ↓
Extract speech segments
        ↓
Resolve voice config
        ↓
Call TTS API
        ↓
Collect audio results
        ↓
Audio Manifest

Boundary quan trọng

Agent chỉ phụ trách xây dựng workflow.

TTS API/service sẽ chịu trách nhiệm thực hiện việc chuyển text thành audio.

Workflow không cần tự implement:

ElevenLabs API integration

TTS provider

API key management

Audio encoding

MinIO/storage implementation

Retry/HTTP handling của TTS provider

Audio mixing

SFX/BGM processing

Video composition

2. Input

Input chính: Storyboard

Ưu tiên sử dụng Storyboard thay vì raw Script.

Lý do:

Storyboard đã chia nội dung theo scene.

Mỗi scene đã có audio.voice.

Mỗi scene có scene_id.

SFX và BGM đã được tách khỏi voice.

Đây là cấu trúc gần với production/video pipeline hơn.

Ví dụ từ storyboard hiện tại:

{
  "id": "scene_03",
  "audio": {
    "voice": "Gà ủ muối Bếp Sạch Việt. Da giòn sừn sựt, thịt chắc ngọt đậm đà."
  }
}

Workflow chỉ lấy:

scene.audio.voice

Không lấy visual/SFX/BGM làm input cho TTS.

3. Output

Workflow tạo một audio result cho mỗi scene có voice.

Ví dụ:

scene_01 → audio_01
scene_02 → audio_02
scene_03 → audio_03
scene_04 → audio_04
scene_05 → audio_05

Không tạo một audio duy nhất cho toàn bộ video.

Output cuối workflow là một Audio Manifest.

Ví dụ:

{
  "storyboard_id": "storyboard_001",
  "voice_profile": "VIETNAMESE_MALE_WARM",
  "segments": [
    {
      "scene_id": "scene_01",
      "audio": "..."
    },
    {
      "scene_id": "scene_02",
      "audio": "..."
    },
    {
      "scene_id": "scene_03",
      "audio": "..."
    }
  ]
}

Metadata audio nên có tối thiểu:

scene_id
audio reference/url
voice profile
actual audio duration
format
status

4. Speech extraction

Workflow duyệt:

storyboard.scenes[]

và lấy:

scene.audio.voice

Tạo danh sách speech segments:

[
  {
    "scene_id": "scene_01",
    "text": "Đi làm về muộn, mệt mỏi mà vẫn phải vào bếp?"
  },
  {
    "scene_id": "scene_02",
    "text": "Bụng thì đói meo mà nghĩ cảnh nấu nướng rửa dọn lại ngán ngẩm..."
  }
]

Validation

Nếu:

audio == null

hoặc scene không có audio.voice:

→ không gửi TTS request.

Nếu audio.voice tồn tại nhưng là empty string:

→ validation error hoặc skip theo policy được thống nhất.

5. Voice configuration

Mục tiêu là cho phép chọn nhiều loại giọng thông qua config.

Không hard-code voice ID trong workflow.

Ví dụ:

{
  "tts": {
    "enabled": true,
    "voice_profile": "VIETNAMESE_MALE_WARM"
  }
}

Các profile có thể tồn tại:

VIETNAMESE_MALE_WARM
VIETNAMESE_MALE_DEEP
VIETNAMESE_MALE_ENERGETIC
VIETNAMESE_FEMALE_FRIENDLY
VIETNAMESE_FEMALE_SOFT
VIETNAMESE_FEMALE_PROFESSIONAL

Tên profile chỉ là abstraction.

Workflow truyền profile/config cho TTS API; API/service quyết định voice ID/model/settings thực tế.

6. Voice configuration scope

MVP

Một voice profile cho toàn bộ video:

Storyboard
    ↓
TTS Config
    ↓
voice_profile = VIETNAMESE_MALE_WARM
    ↓
all scenes use the same voice

Future

Có thể hỗ trợ:

Global default voice
        ↓
Scene-specific override

Ví dụ:

Global: VIETNAMESE_MALE_WARM

scene_01 → global
scene_02 → global
scene_03 → VIETNAMESE_MALE_ENERGETIC
scene_04 → global
scene_05 → global

Chưa cần triển khai scene override nếu MVP chưa cần.

7. TTS API boundary

Workflow không cần biết chi tiết implementation của provider.

Concept:

Workflow
    │
    │ text + voice config
    ▼
  TTS API
    │
    │ audio
    ▼
Workflow

Workflow có thể xem TTS API như một function:

generateSpeech(text, voiceConfig)

Input:

text
voice profile/config

Output:

audio reference
actual duration
status
metadata

Provider hiện tại dự kiến là ElevenLabs, nhưng workflow không nên bị thiết kế phụ thuộc cứng vào ElevenLabs.

8. Duration

Storyboard có:

estimated_duration_seconds

Đây là estimated visual duration, không phải duration thực tế của TTS.

Không dùng:

estimated_duration_seconds = audio duration

Thay vào đó:

TTS API
    ↓
actual audio duration
    ↓
Audio Manifest

Ví dụ:

scene_03 estimated duration = 3.5s
actual TTS duration = 3.42s

Manifest phải giữ 3.42s.

Video Composer sẽ quyết định xử lý timing sau.

9. SFX và BGM

TTS workflow không xử lý:

SFX
BGM
audio mixing
volume mixing

Storyboard hiện tại đã tách:

audio.voice
audio.sfx
audio.bgm_volume

TTS chỉ chịu trách nhiệm:

audio.voice

Ví dụ scene:

{
  "audio": {
    "voice": "...",
    "sfx": [
      "sizzle_effect"
    ],
    "bgm_volume": 0.7
  }
}

Workflow chỉ xử lý:

voice

SFX/BGM sẽ thuộc workflow/audio composition khác.

10. Workflow chi tiết

START
  ↓
Receive storyboard + TTS config
  ↓
Check TTS enabled?
  ├── NO → END / return skipped
  └── YES
       ↓
Extract scenes[]
       ↓
For each scene
       ↓
Check scene.audio.voice
       ├── Missing → skip / validation according to policy
       └── Exists
             ↓
       Create speech segment
             ↓
       Resolve voice profile
             ↓
       Call TTS API
             ↓
       Receive audio result
             ↓
       Collect actual duration + audio reference
             ↓
       Continue next scene
             ↓
Generate Audio Manifest
             ↓
END

11. Expected result for current storyboard

Current storyboard có 5 scenes và mỗi scene có voice.

Workflow dự kiến tạo:

scene_01 → voice audio
scene_02 → voice audio
scene_03 → voice audio
scene_04 → voice audio
scene_05 → voice audio

Sau đó trả về một manifest chứa 5 audio segments.

12. Non-goals

Trong task này KHÔNG làm:

Video generation

Video composition

Subtitle generation

SFX generation

BGM generation

Audio mixing

Voice cloning

Voice design

ElevenLabs SDK implementation

Storage implementation

Provider abstraction nếu API đã được hệ thống cung cấp sẵn

Video timing/composition logic

Các phần trên có thể được xử lý ở workflow/service khác.

13. Kiến trúc logic mong muốn

             STORYBOARD
                  │
                  ▼
        ┌──────────────────┐
        │ Extract Speech   │
        │ Segments         │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │ Resolve Voice    │
        │ Config           │
        └────────┬─────────┘
                 │
                 ▼
             TTS API
                 │
                 ▼
        ┌──────────────────┐
        │ Collect Audio    │
        │ Results          │
        └────────┬─────────┘
                 │
                 ▼
          AUDIO MANIFEST

14. Current decision

Đã chốt

Input chính: Storyboard

Speech text: scene.audio.voice

Một audio result cho mỗi scene

Voice có thể chọn bằng config/profile

TTS API thực hiện text → audio

Workflow chỉ orchestration

Actual audio duration lấy từ TTS result

SFX/BGM không thuộc TTS workflow

Video composition không thuộc TTS workflow

Chưa chốt / future

Scene-level voice override

Subtitle/timestamp workflow

Audio mixing

Retry policy nếu retry nằm ngoài TTS API

Caching/deduplication

Parallel vs sequential TTS generation

Failure policy: fail entire workflow hay partial success

15. Đề xuất để Agent thực hiện

Agent cần tập trung vào:

Build the workflow that transforms an existing storyboard into scene-level speech audio by extracting scene.audio.voice, applying a configurable voice profile, calling the existing TTS API, collecting the generated audio results and producing an Audio Manifest.

Agent không tự implement TTS provider/API và không mở rộng scope sang video/audio composition.

16. Reference files

ga_u_muoi_storyboard.json: storyboard production structure, gồm scene, audio.voice, SFX, BGM, visual và timing.

ga_u_muoi_script.md: script/storyboard dạng Markdown, dùng để tham khảo nội dung speech và scene structure.

