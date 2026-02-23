document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('downloadForm');
    const videoUrlInput = document.getElementById('videoUrl');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnIcon = submitBtn.querySelector('.btn-icon');
    const spinner = submitBtn.querySelector('.spinner');
    
    const errorMsg = document.getElementById('errorMessage');
    const resultPanel = document.getElementById('resultPanel');
    
    // UI Elements for result
    const videoThumb = document.getElementById('videoThumb');
    const videoTitle = document.getElementById('videoTitle');
    const videoDuration = document.getElementById('videoDuration');
    const videoSource = document.getElementById('videoSource');
    const formatList = document.getElementById('formatList');

    // Make initial call to root API to wake up server if needed
    fetch('/docs').catch(()=>console.log("Server warming up"));

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = videoUrlInput.value.trim();
        if (!url) return;
        
        // Setup Loading State
        setLoading(true);
        hideError();
        resultPanel.classList.add('hide');
        formatList.innerHTML = '';
        
        try {
            // Because main.py mounts public at /, API is at /api
            const response = await fetch('/api/extract', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || '影片解析失敗，請確認網址是否正確且公開。');
            }
            
            const data = await response.json();
            renderResult(data);
            
        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.textContent = '解析中...';
            btnIcon.classList.add('hide');
            spinner.classList.remove('hide');
        } else {
            submitBtn.disabled = false;
            btnText.textContent = '解析影片';
            btnIcon.classList.remove('hide');
            spinner.classList.add('hide');
        }
    }

    function showError(message) {
        errorMsg.textContent = message;
        errorMsg.classList.remove('hide');
    }
    
    function hideError() {
        errorMsg.classList.add('hide');
    }

    function formatTime(seconds) {
        if (!seconds) return '';
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        
        if (h > 0) {
            return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        }
        return `${m}:${s.toString().padStart(2, '0')}`;
    }

    function formatBytes(bytes) {
        if (!bytes) return '未知大小';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function renderResult(data) {
        // Set basic info
        videoThumb.src = data.thumbnail || 'https://via.placeholder.com/320x180?text=No+Thumbnail';
        videoTitle.textContent = data.title;
        
        if (data.duration) {
            videoDuration.textContent = formatTime(data.duration);
            videoDuration.classList.remove('hide');
        } else {
            videoDuration.classList.add('hide');
        }
        
        // Set Source Badge
        videoSource.className = 'source-badge';
        if (data.extractor.includes('youtube')) {
            videoSource.classList.add('youtube');
            videoSource.innerHTML = '<i class="fa-brands fa-youtube"></i> YouTube';
        } else if (data.extractor.includes('facebook')) {
            videoSource.classList.add('facebook');
            videoSource.innerHTML = '<i class="fa-brands fa-facebook"></i> Facebook';
        } else {
            videoSource.innerHTML = `<i class="fa-solid fa-video"></i> ${data.extractor}`;
        }

        // Render Formats
        if (data.formats && data.formats.length > 0) {
            data.formats.forEach(format => {
                const card = document.createElement('div');
                card.className = 'format-card';
                
                const showSize = format.filesize ? formatBytes(format.filesize) : '解析中...';
                
                // Usually we output directly to format.url, but we should force download 
                // in HTML5 if possible.
                card.innerHTML = `
                    <div class="format-header">
                        <span class="resolution">${format.resolution}</span>
                        <span class="ext">${format.ext}</span>
                    </div>
                    <div class="file-info">
                        <span><i class="fa-solid fa-file-video"></i> ${format.vcodec !== 'none' ? '附影片' : ''} ${format.acodec !== 'none' ? '附聲音' : ''}</span>
                        <span>${showSize}</span>
                    </div>
                    <a href="${format.url}" target="_blank" rel="noopener noreferrer" class="download-link" download>
                        <i class="fa-solid fa-download"></i> 直接下載
                    </a>
                `;
                formatList.appendChild(card);
            });
        } else {
             formatList.innerHTML = `<div class="error-message">找不到可下載的檔案格式。可能該影片受版權保護或需要登入。</div>`;
        }

        resultPanel.classList.remove('hide');
        // Scroll slightly
        setTimeout(() => {
            resultPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }
});
