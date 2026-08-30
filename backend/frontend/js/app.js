const API_BASE = "http://localhost:8000/api";

let projectId = "";
let currentBusinessData = null;
let currentStoryboard = null;

// Giao diện Loader
function showLoader(text) {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.classList.remove('hidden');
        document.getElementById('loader-text').innerText = text;
    }
}
function hideLoader() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.classList.add('hidden');
    }
}

// Hàm mã hóa tên thành slug
function slugify(text) {
    return text.toString().toLowerCase()
        .replace(/á|à|ả|ã|ạ|ă|ắ|ằ|ẳ|ẵ|ặ|â|ấ|ầ|ẩ|ẫ|ậ/g, 'a')
        .replace(/é|è|ẻ|ẽ|ẹ|ê|ế|ề|ể|ễ|ệ/g, 'e')
        .replace(/i|í|ì|ỉ|ĩ|ị/g, 'i')
        .replace(/ó|ò|ỏ|õ|ọ|ô|ố|ồ|ổ|ỗ|ộ|ơ|ớ|ờ|ở|ỡ|ợ/g, 'o')
        .replace(/ú|ù|ủ|ũ|ụ|ư|ứ|ừ|ử|ữ|ự/g, 'u')
        .replace(/ý|ỳ|ỷ|ỹ|ỵ/g, 'y')
        .replace(/đ/g, 'd')
        .replace(/\s+/g, '_')
        .replace(/[^\w\-]+/g, '')
        .replace(/\_\_+/g, '_')
        .replace(/^_/, '')
        .replace(/_$/, '');
}

// Load danh sách project cũ
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/api/projects/list");
        const data = await res.json();
        if (data.projects) {
            const datalist = document.getElementById('existing-projects');
            data.projects.forEach(p => {
                const option = document.createElement('option');
                option.value = p.project_id;
                datalist.appendChild(option);
            });
        }
    } catch (err) {
        console.error("Failed to load projects", err);
    }
    
    // Load dữ liệu cũ từ localStorage
    const savedName = localStorage.getItem('saved_project_name');
    const savedInfo = localStorage.getItem('saved_product_info');
    
    if (savedName) {
        const projectNameInput = document.getElementById('project-name');
        if (projectNameInput) {
            projectNameInput.value = savedName;
            document.getElementById('project-id-preview').innerText = slugify(savedName);
        }
    }
    if (savedInfo) {
        const infoInput = document.getElementById('product-info');
        if (infoInput) infoInput.value = savedInfo;
    }

    // Live update preview và lưu localStorage
    const projectNameInput = document.getElementById('project-name');
    if (projectNameInput) {
        projectNameInput.addEventListener('input', (e) => {
            const val = e.target.value;
            const slug = slugify(val);
            document.getElementById('project-id-preview').innerText = slug || 'chua_nhap_ten';
            localStorage.setItem('saved_project_name', val);
        });
    }
    
    const productInfoInput = document.getElementById('product-info');
    if (productInfoInput) {
        productInfoInput.addEventListener('input', (e) => {
            localStorage.setItem('saved_product_info', e.target.value);
        });
    }
});

// Điều hướng giao diện
function goToStep(step) {
    document.querySelectorAll('.step-section').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav li').forEach(el => el.classList.remove('active'));
    document.getElementById(`step-${step}`).classList.add('active');
    document.getElementById(`nav-step-${step}`).classList.add('active');
    
    // Hiển thị nút "Xem Kịch bản đã có" nếu đã có data
    if(step === 2 && currentStoryboard) {
        document.getElementById('btn-skip-to-3').style.display = 'block';
    } else {
        document.getElementById('btn-skip-to-3').style.display = 'none';
    }
}

// Xử lý nút Quay lại & Điều hướng tự do
document.getElementById('btn-back-1')?.addEventListener('click', () => goToStep(1));
document.getElementById('btn-back-2')?.addEventListener('click', () => goToStep(2));
document.getElementById('btn-skip-to-3')?.addEventListener('click', () => goToStep(3));
document.getElementById('btn-back-1-new')?.addEventListener('click', () => {
    document.getElementById('project-name').value = '';
    document.getElementById('product-info').value = '';
    document.getElementById('product-file').value = '';
    goToStep(1);
});

// Cho phép click thẳng vào thanh bên trái để nhảy bước (nếu thích)
document.querySelectorAll('.nav li').forEach((el, index) => {
    el.style.cursor = 'pointer';
    el.addEventListener('click', () => goToStep(index + 1));
});

function fillBusinessDataToUI() {
    if (!currentBusinessData) return;
    
    // Product
    const prod = currentBusinessData.product || {};
    document.getElementById('bd-product-name').value = prod.name || "";
    document.getElementById('bd-product-desc').value = prod.description || "";
    document.getElementById('bd-product-features').value = (prod.features || []).join('\n');
    document.getElementById('bd-product-benefits').value = (prod.benefits || []).join('\n');
    document.getElementById('bd-product-price').value = prod.price || "";
    document.getElementById('bd-product-usp').value = prod.usp || "";
    
    // Audience
    const aud = currentBusinessData.audience || {};
    document.getElementById('bd-audience-age').value = aud.age || "";
    document.getElementById('bd-audience-job').value = aud.occupation || "";
    document.getElementById('bd-audience-pain').value = (aud.pain_points || []).join('\n');
    document.getElementById('bd-audience-needs').value = (aud.needs || []).join(', ');
    document.getElementById('bd-audience-hobbies').value = (aud.hobbies || []).join(', ');
    
    // Marketing & Brand
    const mkt = currentBusinessData.marketing || {};
    const brnd = currentBusinessData.brand || {};
    document.getElementById('bd-marketing-platform').value = mkt.platform || "TikTok";
    document.getElementById('bd-marketing-duration').value = mkt.duration || "15-30s";
    document.getElementById('bd-marketing-objective').value = mkt.objective || "";
    document.getElementById('bd-marketing-cta').value = mkt.cta || "";
    document.getElementById('bd-brand-tone').value = brnd.tone_of_voice || "";
}

// BƯỚC 1: SINH BUSINESS DATA
document.getElementById('btn-init').addEventListener('click', async () => {
    const rawName = document.getElementById('project-name').value.trim();
    projectId = slugify(rawName);
    const info = document.getElementById('product-info').value.trim();
    
    if(!projectId || !info) return alert("Vui lòng điền đủ tên dự án và thông tin sản phẩm!");
    
    showLoader("🧠 Đang dùng AI Gemini phân tích dữ liệu kinh doanh...\nVui lòng chờ trong giây lát ⏳");

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
        fillBusinessDataToUI();
        
        goToStep(2);
    } catch(err) {
        alert(err.message);
    } finally {
        hideLoader();
    }
});

// RESUME CŨ
document.getElementById('btn-resume').addEventListener('click', async () => {
    const rawName = document.getElementById('project-name').value.trim();
    projectId = slugify(rawName);
    if(!projectId) return alert("Vui lòng điền tên dự án cần tiếp tục!");
    
    showLoader("Đang khôi phục dữ liệu dự án...\nVui lòng chờ trong giây lát ⏳");
    try {
        let hasData = false;
        
        // 1. Fetch Business Data
        const resBd = await fetch(`/storage/${projectId}/business_data.json`);
        if(resBd.ok) {
            currentBusinessData = await resBd.json();
            fillBusinessDataToUI();
            hasData = true;
        }

        // 2. Fetch Storyboard
        const resSb = await fetch(`/storage/${projectId}/storyboard.json`);
        if(resSb.ok) {
            currentStoryboard = await resSb.json();
            renderStoryboard();
            hasData = true;
        }
        
        if(!hasData) throw new Error("Dự án này chưa có Dữ liệu hoặc đã bị xóa!");
        
        alert("Đã khôi phục thành công! Hãy xem lại từng bước.");
        goToStep(2);
    } catch (e) {
        alert(e.message);
    } finally {
        hideLoader();
    }
});

// BƯỚC 2: SINH STORYBOARD
document.getElementById('btn-gen-storyboard').addEventListener('click', async () => {
    const btn = document.getElementById('btn-gen-storyboard');
    btn.innerText = "⏳ Đang viết Kịch bản 5 cảnh...";
    btn.disabled = true;

    // Lấy data mới nhất nếu người dùng có sửa chữa
    currentBusinessData = {
        product: {
            name: document.getElementById('bd-product-name').value,
            description: document.getElementById('bd-product-desc').value,
            features: document.getElementById('bd-product-features').value.split('\n').map(x=>x.trim()).filter(x=>x),
            benefits: document.getElementById('bd-product-benefits').value.split('\n').map(x=>x.trim()).filter(x=>x),
            price: document.getElementById('bd-product-price').value,
            usp: document.getElementById('bd-product-usp').value
        },
        audience: {
            age: document.getElementById('bd-audience-age').value,
            occupation: document.getElementById('bd-audience-job').value,
            pain_points: document.getElementById('bd-audience-pain').value.split('\n').map(x=>x.trim()).filter(x=>x),
            needs: document.getElementById('bd-audience-needs').value.split(',').map(x=>x.trim()).filter(x=>x),
            hobbies: document.getElementById('bd-audience-hobbies').value.split(',').map(x=>x.trim()).filter(x=>x)
        },
        marketing: {
            platform: document.getElementById('bd-marketing-platform').value,
            duration: document.getElementById('bd-marketing-duration').value,
            objective: document.getElementById('bd-marketing-objective').value,
            cta: document.getElementById('bd-marketing-cta').value
        },
        brand: {
            tone_of_voice: document.getElementById('bd-brand-tone').value
        }
    };

    showLoader("🎬 Đang dùng AI Đạo diễn viết kịch bản 5 cảnh...\nViệc này có thể tốn khoảng 10-15 giây ⏳");

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
        hideLoader();
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
