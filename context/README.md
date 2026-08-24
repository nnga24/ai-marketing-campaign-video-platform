# Storyboard Generator — Spec Package

Bộ tài liệu này tách từ `storyboard-generator-specification.md` (bản gốc, đầy đủ 50 phần) thành các file nhỏ, mỗi file phục vụ một mục đích riêng — để đưa vào agent/workflow mà **không cần load toàn bộ 50 phần vào context mỗi lần**.

## Cấu trúc

```
storyboard/
│
├── README.md                     ← file này
│
├── storyboard-specification.md   ← narrative spec: mục đích, nguyên tắc, quy trình
│                                     (đọc để hiểu "tại sao" và "làm như thế nào")
│
├── storyboard-schema.json        ← structural contract (JSON Schema)
│                                     (dùng cho structured output / function calling / validate JSON)
│
├── storyboard-example.json       ← golden example (1 storyboard hợp lệ, pass toàn bộ rule)
│                                     (few-shot example cho prompt, hoặc test fixture)
│
├── storyboard-rules.yaml         ← machine-readable business rules + hard constraints
│                                     (dùng cho rule engine / code validator)
│
└── quality-rules.yaml            ← scoring weights + pass/fail threshold + issue format
                                      (dùng cho quality gate sau khi LLM generate xong)
```

## Dùng ở đâu trong pipeline

```
                    LLM (Storyboard Generator agent)
                     │
        system prompt = storyboard-specification.md (rút gọn)
                      + storyboard-schema.json (output contract)
                      + storyboard-example.json (few-shot, optional)
                     ↓
             Storyboard JSON
                     ↓
          ┌──────────┴──────────┐
          ↓                     ↓
   storyboard-schema.json   storyboard-rules.yaml
   (JSON Schema validator)  (Rule Engine validator)
          ↓                     ↓
          └──────────┬──────────┘
                     ↓
         quality-rules.yaml → Semantic Judge (LLM chấm điểm)
                     ↓
                PASS / FAIL
```

**Gợi ý áp dụng:**

| Mục đích | File cần |
|---|---|
| Prompt cho agent sinh storyboard | `storyboard-specification.md` (+ có thể trích input contract tương ứng) |
| Ép LLM trả JSON đúng cấu trúc (structured output / tool schema) | `storyboard-schema.json` |
| Few-shot / golden test case | `storyboard-example.json` |
| Code validate business rule, hard constraint | `storyboard-rules.yaml` |
| Chấm điểm chất lượng, quyết định pass/fail | `quality-rules.yaml` |

## Nguyên tắc giữ nguyên từ bản gốc

- **LLM không phải validator của chính nó.** Nó tự đánh giá (`quality` object), nhưng `storyboard-rules.yaml` + `storyboard-schema.json` (code) mới là authority quyết định pass/fail.
- **Storyboard ≠ Timeline.** Storyboard chỉ chứa `estimated_duration_seconds`; timestamp thật lấy sau khi TTS + Whisper alignment, ở bước Timeline Engine.
- **Audio là semantic anchor** — visual luôn được thiết kế để phục vụ nội dung voice đang nói, không làm ngược lại.
