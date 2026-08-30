const API_BASE = "http://localhost:8000/api";

let projectId = "";
let currentBusinessData = null;
let currentStoryboard = null;

// Điều hướng giao diện
function goToStep(step) {
    document.querySelectorAll('.step-section').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav li').forEach(el => el.classList.remove('active'));
    document.getElementById(`step-${step}`).classList.add('active');
    document.getElementById(`nav-step-${step}`).classList.add('active');
}

// BƯỚC 1: SINH BUSINESS DATA
document.getElementById('btn-init').addEventListener('click', async () => {
    projectId = document.getElementById('project-id').value.trim();
    const info = document.getElementById('product-info').value.trim();
    
    if(!projectId || !info) return alert("Vui lòng điền đủ mã dự án và thông tin sản phẩm!");
    
    const btn = document.getElementById('btn-init');
    btn.innerText = "⏳ Đang phân tích bằng Gemini...";
    btn.disabled = true;

    try {
        // Khởi tạo thư mục
        await fetch(`${API_BASE}/projects/${projectId}/init`, { method: "POST" });
        
        // Upload file nếu có
        const fileInput = document.getElementById('product-file');
        let uploadedImages = [];
        if (fileInput.files.length > 0) {
            const formData = new FormData();
            for(let i=0; i<fileInput.files.length; i++) {
                formData.append('files', fileInput.files[i]);
            }
            const uploadRes = await fetch(`${API_BASE}/projects/${projectId}/upload`, {
                method: "POST",
                body: formData
            });
            const uploadData = await uploadRes.json();
            if (uploadData.file_uris) uploadedImages = uploadData.file_uris;
        }
        
        // Gọi LLM phân tích Business Data (truyền thêm list ảnh)
        const res = await fetch(`${API_BASE}/generate/business-data`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ project_id: projectId, product_info: info, images: uploadedImages })
        });
        
        if(!res.ok) throw new Error("Lỗi API Gemini");
        
        currentBusinessData = await res.json();
        
        // Đổ data ra màn hình Bước 2
        document.getElementById('bd-target').value = currentBusinessData.target_audience || "";
        document.getElementById('bd-pain').value = (currentBusinessData.pain_points || []).join('\n');
        document.getElementById('bd-core').value = currentBusinessData.core_message || "";
        
        goToStep(2);
    } catch(err) {
        alert(err.message);
    } finally {
        btn.innerText = "Bắt đầu Phân tích AI";
        btn.disabled = false;
    }
});

// RESUME CŨ
document.getElementById('btn-resume').addEventListener('click', async () => {
    projectId = document.getElementById('project-id').value.trim();
    if(!projectId) return alert("Vui lòng điền mã dự án!");
    
    try {
        const res = await fetch(`/storage/${projectId}/storyboard.json`);
        if(!res.ok) throw new Error("Dự án này chưa có Kịch bản hoặc đã bị xóa!");
        
        currentStoryboard = await res.json();
        renderStoryboard();
        goToStep(3);
    } catch (e) {
        alert(e.message);
    }
});

// BƯỚC 2: SINH STORYBOARD
document.getElementById('btn-gen-storyboard').addEventListener('click', async () => {
    const btn = document.getElementById('btn-gen-storyboard');
    btn.innerText = "⏳ Đang viết Kịch bản 5 cảnh...";
    btn.disabled = true;

    // Lấy data mới nhất nếu người dùng có sửa chữa
    currentBusinessData.target_audience = document.getElementById('bd-target').value;
    currentBusinessData.pain_points = document.getElementById('bd-pain').value.split('\n');
    currentBusinessData.core_message = document.getElementById('bd-core').value;

    try {
        const res = await fetch(`${API_BASE}/generate/storyboard`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ project_id: projectId, business_data: currentBusinessData })
        });
        
        if(!res.ok) throw new Error("Lỗi API Gemini");
        
        currentStoryboard = await res.json();
        renderStoryboard();
        goToStep(3);
    } catch (err) {
        alert(err.message);
    } finally {
        btn.innerText = "Duyệt & Viết Kịch Bản";
        btn.disabled = false;
    }
});

function renderStoryboard() {
    const container = document.getElementById('storyboard-container');
    container.innerHTML = "";
    (currentStoryboard.scenes || []).forEach((scene, index) => {
        const div = document.createElement('div');
        div.className = "scene-card";
        div.innerHTML = `
            <h4>Phân cảnh ${index + 1} (${scene.id})</h4>
            <div class="form-group">
                <label>Mô tả Ảnh AI (Tiếng Anh)</label>
                <input type="text" id="vis-${scene.id}" value="${scene.visual?.subject || ''} in ${scene.visual?.environment || ''}" />
            </div>
            <div class="form-group">
                <label>Lời thoại Audio (Tiếng Việt)</label>
                <textarea id="aud-${scene.id}" rows="2">${scene.audio?.voice || ''}</textarea>
            </div>
        `;
        container.appendChild(div);
    });
}

// TEST GIỌNG ĐỌC
document.getElementById('btn-test-voice').addEventListener('click', async () => {
    const voiceId = document.getElementById('voice-select').value;
    const text = document.getElementById('voice-test-text').value;
    const btn = document.getElementById('btn-test-voice');
    
    btn.innerText = "Đang tạo...";
    btn.disabled = true;
    try {
        const res = await fetch(`${API_BASE}/generate/test-voice`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ project_id: projectId, text: text, voice_id: voiceId })
        });
        if(!res.ok) throw new Error("Lỗi khi tạo giọng mẫu");
        const data = await res.json();
        
        const audioPlayer = document.getElementById('audio-test-player');
        audioPlayer.src = `http://localhost:8000/${data.audio_uri}?t=${Date.now()}`;
        audioPlayer.style.display = 'block';
        audioPlayer.play();
    } catch(e) {
        alert(e.message);
    } finally {
        btn.innerText = "Nghe thử";
        btn.disabled = false;
    }
});

// BƯỚC 3 & 4: SINH ASSETS VÀ RENDER VIDEO
document.getElementById('btn-gen-assets').addEventListener('click', async () => {
    goToStep(4);
    const statusEl = document.getElementById('render-status');
    const voiceId = document.getElementById('voice-select').value;
    
    try {
        // Note: Trong môi trường thực tế, ta cần gửi lại bản Storyboard đã chỉnh sửa lên Backend để lưu.
        // Tạm thời ở bản MVP, Web sẽ chạy luồng tạo Assets bằng bản gốc (hoặc có thể viết thêm 1 API save).
        
        statusEl.innerText = "Bắt đầu pha 2: Đang gọi ElevenLabs sinh giọng đọc và Pollinations vẽ ảnh... (Tốn khoảng 1-2 phút)";
        
        const resAssets = await fetch(`${API_BASE}/generate/assets`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ project_id: projectId, voice_id: voiceId })
        });

        if(!resAssets.ok) throw new Error("Lỗi khi tạo thư viện Ảnh và Âm thanh!");
        
        statusEl.innerText = "Bắt đầu hậu kỳ: Đang tính toán hiệu ứng và gắn phụ đề... (Khoảng 30 giây)";
        
        const resCompose = await fetch(`${API_BASE}/generate/compose`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ project_id: projectId })
        });
        
        if(!resCompose.ok) throw new Error("Lỗi Render Video!");
        
        const composeData = await resCompose.json();
        
        // Hiện video
        document.getElementById('progress-box').classList.add('hidden');
        const videoContainer = document.getElementById('final-video-container');
        videoContainer.classList.remove('hidden');
        
        const videoPlayer = document.getElementById('final-video');
        videoPlayer.src = `http://localhost:8000/${composeData.final_video_uri}`;
        
    } catch (e) {
        document.querySelector('.spinner').style.display = 'none';
        statusEl.style.color = '#ef4444';
        statusEl.innerText = `❌ ${e.message}`;
    }
});
