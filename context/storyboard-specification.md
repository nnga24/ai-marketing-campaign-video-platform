# Storyboard Generator — Specification

**Version:** 1.0 · **Status:** Draft / MVP

> Field-level output contract → xem `storyboard-schema.json`
> Business rules & hard constraints → xem `storyboard-rules.yaml`
> Quality scoring & pass criteria → xem `quality-rules.yaml`
> Ví dụ hợp lệ → xem `storyboard-example.json`

---

## 1. Mục đích

Storyboard Generator nhận thông tin đã chuẩn hóa từ Marketing Planning và Script Generation, tạo ra một **Storyboard có cấu trúc** để các module downstream sử dụng:

```
Storyboard → Voice Generation → Visual/Video Generation → Subtitle → Timeline → Rendering
```

**Vị trí trong workflow tổng thể:**

```
Business Data → Marketing Brief → Creative Idea → Script
      → ★ Storyboard Generator ★
      → Voice → Visual Scenes → Timestamp → Timeline → Subtitle → Rendering → Quality Check
```

---

## 2. Định nghĩa Storyboard

**Là:** bản thiết kế cho việc kể chuyện bằng hình ảnh và âm thanh của video.

**Không phải:** final video, final timeline, subtitle file, video generation prompt thuần túy, danh sách hình ảnh, hay một đoạn văn mô tả video.

Storyboard là cầu nối giữa:

```
SCRIPT → "Người xem nghe gì?"        VISUAL → "Người xem nhìn thấy gì?"
```

**Ví dụ:**

```
0–4s   Voice: "Bạn ngồi 8 tiếng mỗi ngày?"   Visual: Người ngồi làm việc
4–8s   Voice: "Hãy thử X1"                    Visual: Product hero shot
```

---

## 3. Mục tiêu của Generator

1. **Narrative** — video có logic `Hook → Problem/Context → Solution → Benefit/Proof → CTA`
2. **Audio-Visual Alignment** — voice và visual nói cùng một câu chuyện
3. **Product Consistency** — không tự bịa thông tin sản phẩm
4. **Production Feasibility** — visual có khả năng được tạo bởi pipeline AI/video hiện tại
5. **Downstream Compatibility** — output đủ cấu trúc cho TTS, Visual Generator, Subtitle, Timeline Engine, Rendering

---

## 4. Input Contract (tổng quan)

Generator **không được tự suy đoán** dữ liệu quan trọng. Input gồm 8 nhóm:

`Marketing Brief` · `Creative Idea` · `Script` · `Product Data` · `Brand Data` · `Assets` · `Platform Constraints` · `Generation Capabilities`

Cấu trúc field chi tiết của từng nhóm nằm trong `storyboard-schema.json` (định nghĩa `$defs.inputs.*`). Ba nguyên tắc quan trọng cần nhớ khi generate:

- **Script:** không được tự ý sửa nội dung. Nếu Script cần thay đổi → trả về `Script Revision Required`, không silently sửa.
- **Product Data:** chỉ dùng `product.features` + `approved_claims` để mô tả sản phẩm — không tự tạo claim (vd: "10-year warranty", "clinically proven").
- **Generation Capabilities:** nếu hệ thống chỉ hỗ trợ `image_to_video`, không được sinh scene yêu cầu `text_to_video` phức tạp.

---

## 5. Processing Pipeline

```
1. Validate Input
2. Analyze Marketing Objective
3. Analyze Audience
4. Analyze Creative Structure
5. Analyze Script
6. Map Script → Scenes
7. Define Visual for Each Scene
8. Validate Product Claims
9. Validate Platform Constraints
10. Validate Production Feasibility
11. Self-evaluate
12. Return Storyboard
```

### 5.1 Validate Input

Thiếu bất kỳ dữ liệu critical nào (Marketing Brief, Script, Product Data, Platform, Duration, Required Assets) → trả `INPUT_INVALID`. Không được cố đoán.

### 5.2 Map Script → Scene (bước cốt lõi)

Mỗi script segment map sang scene có `purpose` tương ứng trong creative structure (hook/problem/solution/benefit/cta).

**Không ép 1 script segment = 1 scene.** Có thể:

- `1 script segment → 1 scene`, hoặc
- `1 script segment → 2 scenes` (nếu cần thể hiện nhiều visual)

`2 unrelated script segments → 1 visual` chỉ được phép nếu visual thực sự hỗ trợ cả hai.

### 5.3 Audio là Semantic Anchor

```
Voice → "What is being said?" → "What should viewer see?"
```

**Không làm ngược** (generate visual ngẫu nhiên rồi tìm voice để khớp). Audio/script là xương sống; visual được map dựa trên nội dung đang được nói.

---

## 6. Nguyên tắc viết Voice & Visual

**Voice — MUST:** natural speech, nhất quán với Script/scene purpose/marketing message.
**Voice — MUST NOT:** chứa camera/visual/editing instruction, hay unsupported product claim.

> Bad: "Bạn ngồi 8 tiếng mỗi ngày, sau đó camera zoom vào chiếc ghế."
> Good: "Bạn ngồi 8 tiếng mỗi ngày?"

**Visual** phải cụ thể hóa: subject, action, environment, emotion, composition, camera, lighting, style — không chấp nhận mô tả chung chung.

> Bad: "Show an office."
> Good: "A young office worker sits at a modern desk, showing slight discomfort after prolonged sitting. Medium shot, eye-level camera, subtle slow push-in, natural daylight, realistic commercial style."

**Audio-Visual Alignment:** Voice Meaning → Visual Meaning → Semantic Alignment. Ví dụ FAIL: voice nói "lumbar support" nhưng visual là "person drinking coffee".

Rule chi tiết (camera allowed list, claim traceability, duration tolerance, CTA/overlay/transition rules, hard constraints HC-01…HC-12) → xem `storyboard-rules.yaml`.

---

## 7. Duration & Timestamp

Storyboard chỉ chứa `estimated_duration_seconds` — **không chứa final timestamp**.

```
voice.mp3 → Whisper / Forced Alignment → actual timestamps → Timeline Engine
```

Timestamp thật chỉ được xác định **sau** khi TTS chạy xong, thông qua Whisper alignment, trước khi Timeline Engine xử lý.

---

## 8. Quality Evaluation & Regeneration

Storyboard tự đánh giá qua object `quality` (5 tiêu chí có trọng số — xem `quality-rules.yaml` cho công thức và ngưỡng pass).

**Regeneration có mục tiêu, không mù:**

```
Storyboard → Validator → FAIL → Identify Problems → Regenerate → Validate Again
```

Chỉ regenerate **toàn bộ** storyboard nếu: creative structure broken, core message broken, script mapping broken, hoặc global duration broken. Nếu chỉ 1 scene lỗi → chỉ regenerate scene đó.

---

## 9. Storyboard ≠ Timeline (rule kiến trúc)

| Storyboard | Timeline |
|---|---|
| Scene, Voice, Visual, Purpose, Estimated duration | start, end, track, asset, audio, subtitle, overlay |

Storyboard không nên làm thay nhiệm vụ của Timeline Engine.

---

## 10. Trách nhiệm & Ranh giới

**MUST:** hiểu Marketing Brief/Creative Idea/Script/Product → chia Script thành scenes → xác định purpose/visual/camera/product visibility/overlay/transition cho từng scene → kiểm tra audio-visual consistency, product claims, production feasibility → self-evaluate.

**MUST NOT:** tạo final video/timestamp, tự sửa product data, tự bịa claim, tự đổi CTA/duration, tạo visual không liên quan đến voice, dùng capability hệ thống không hỗ trợ.

**Boundary trong pipeline:**

```
Marketing Planner → Creative Generator → Script Generator
      → Storyboard Generator
      ├→ Voice Generator → voice.mp3   ┐
      └→ Visual Generator → scenes.mp4 ┴→ Timeline Engine → FFmpeg → Final Video
```

---

## 11. MVP Success Criteria

Given: Product + Brand + Audience + Marketing Objective + Campaign + Assets + Creative Idea + Script
→ Generate → Valid Storyboard JSON → pass: Schema validation, Business rules, Product claim validation, Audio/visual alignment, Platform validation, Production feasibility, Quality threshold
→ Output đưa trực tiếp cho TTS + Visual Generator.

---

## 12. Kiến trúc Validation

**Không nhét toàn bộ rule vào một prompt.** Chia thành 3 lớp:

```
LLM → Storyboard JSON
        ├→ JSON Schema Validation (storyboard-schema.json)
        └→ Rule Engine Validation (storyboard-rules.yaml)
                ↓
        Semantic Judge (LLM chấm điểm — quality-rules.yaml)
                ↓
            PASS / FAIL
```

- **Deterministic rules** (code validate): required fields, enum, duration, scene count, CTA, platform, aspect ratio, asset IDs, product IDs.
- **Semantic rules** (LLM/VLM evaluate): visual có support voice không? story có thuyết phục không? scene có coherent không? visual có production-friendly không?
- **Hard rules** (code phải chặn): unsupported product claim, invalid schema, invalid duration, missing CTA, invalid asset.

> **Nguyên tắc giữ vững:** LLM không phải validator của chính nó. Nó có thể tự đánh giá, nhưng system validator (code) mới là authority.

**Keyword nên nghiên cứu tiếp:** LLM structured output JSON Schema, constrained decoding, LLM guardrails, LLM output validation, LLM as a judge, semantic validation, AI agent quality gate, Pydantic JSON schema, OpenAI structured outputs, Gemini structured output.
