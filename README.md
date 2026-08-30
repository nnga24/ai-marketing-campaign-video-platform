# AI Video Creator SaaS

Hệ thống tự động hóa quá trình tạo Video Marketing ngắn (TikTok/Reels/Shorts) hoàn toàn bằng trí tuệ nhân tạo (AI).

## 🚀 Các tính năng chính
- **Thu thập yêu cầu đa phương thức (Multi-modal)**: Nhập mô tả sản phẩm và tải lên nhiều hình ảnh thực tế của sản phẩm.
- **Tiếp tục Dự án cũ (Resume)**: Dễ dàng load lại kịch bản của một dự án cũ mà không cần chạy lại luồng phân tích.
- **Phân tích Kinh doanh (Gemini AI Vision)**: Tự động trích xuất Tệp khách hàng, Nỗi đau và Thông điệp cốt lõi dựa trên text và nhận diện chi tiết hình ảnh sản phẩm.
- **Xây dựng Kịch bản (Storyboard)**: Lên kịch bản 5 phân cảnh (Hook, Problem, Solution, Benefit, CTA) bằng AI.
- **Nghe thử & Chốt Giọng (Voice Test)**: Tích hợp bảng điều khiển test giọng trực tiếp trên giao diện.
- **Giọng đọc AI (ElevenLabs v3)**: Tích hợp Model Turbo v2.5 cho giọng đọc tiếng Việt siêu thực (Alice, Adam, Jessica...).
- **Tạo chuyển động (Motion Engine)**: Cắt cúp (crop/resize) ảnh tĩnh của người dùng về chuẩn tỷ lệ 9:16 và áp dụng hiệu ứng Ken Burns (Zoom) bằng OpenCV.
- **Render Video Hoàn chỉnh**: Tự động ráp ảnh, âm thanh và chèn phụ đề thông minh (Textwrap - tự động xuống dòng) để xuất file MP4 cuối cùng.

## 📂 Cấu trúc thư mục
- `backend/`: Chứa mã nguồn FastAPI, logic tích hợp AI (Gemini, ElevenLabs), xử lý video (MoviePy) và xử lý ảnh (OpenCV/Pillow).
- `backend/frontend/`: Chứa giao diện người dùng Web SPA (HTML, CSS, JS) - được mount trực tiếp bởi FastAPI.
- `backend/storage/`: Nơi lưu trữ dữ liệu của các dự án (Kịch bản JSON, file ghi âm, file ảnh, file video mp4).

## 💻 Hướng dẫn cài đặt (Môi trường Local)

1. **Cài đặt Python 3.10+** và các thư viện:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. **Cấu hình API Keys** trong file `backend/.env`:
   - `GEMINI_API_KEY="your_google_gemini_key"`
   - `ELEVENLABS_API_KEY="your_elevenlabs_key"`
3. **Chạy Server Backend**:
   ```bash
   uvicorn main:app --reload
   ```
4. **Trải nghiệm**: Mở trình duyệt và truy cập vào [http://localhost:8000](http://localhost:8000).

## 🐳 Hướng dẫn triển khai với Docker

Hệ thống đã được đính kèm sẵn `Dockerfile` hỗ trợ cài đặt tự động đầy đủ môi trường (ffmpeg, libgl).

1. **Build Docker Image**:
   ```bash
   cd backend
   docker build -t ai-video-creator .
   ```
2. **Chạy Container**:
   (Lưu ý: Bạn nên mount thư mục `storage` ra ngoài máy host để không bị mất dữ liệu video khi khởi động lại container).
   ```bash
   docker run -d -p 8000:8000 -v $(pwd)/storage:/app/storage ai-video-creator
   ```
