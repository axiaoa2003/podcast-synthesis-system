// 双人对话播客合成系统 - 前端交互逻辑

// DOM 加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化事件监听器
    initializeEventListeners();
});

// 初始化事件监听器
function initializeEventListeners() {
    // 1. 灵感生成
    document.getElementById('generateInspirationBtn').addEventListener('click', generateInspiration);
    
    // 2. 文稿生成
    document.getElementById('generateScriptBtn').addEventListener('click', generateScript);
    
    // 3. 文稿编辑相关
    document.getElementById('optimizeScriptBtn').addEventListener('click', optimizeScript);
    document.getElementById('validateScriptBtn').addEventListener('click', validateScript);
    document.getElementById('copyScriptBtn').addEventListener('click', copyScript);
    
    // 4. 播客生成
    document.getElementById('startGenerateBtn').addEventListener('click', startGeneratePodcast);
    
    // 5. 标签页切换事件
    const tabElements = document.querySelectorAll('#podcastTabs button');
    tabElements.forEach(tab => {
        tab.addEventListener('shown.bs.tab', handleTabChange);
    });
}

// 处理标签页切换
function handleTabChange(event) {
    const activeTab = event.target.getAttribute('id');
    
    // 当切换到文稿生成标签时，自动填充灵感内容
    if (activeTab === 'script-tab') {
        const inspirationResult = document.getElementById('inspirationResult').textContent;
        const inspirationInput = document.getElementById('inspirationInput');
        if (inspirationResult && !inspirationInput.value) {
            inspirationInput.value = inspirationResult;
        }
    }
    
    // 当切换到文稿编辑标签时，自动填充文稿内容
    if (activeTab === 'edit-tab') {
        const scriptResult = document.getElementById('scriptResult').textContent;
        const scriptEditor = document.getElementById('scriptEditor');
        if (scriptResult && !scriptEditor.value) {
            scriptEditor.value = scriptResult;
        }
    }
    
    // 当切换到生成播客标签时，自动填充最终文稿
    if (activeTab === 'generate-tab') {
        const scriptEditor = document.getElementById('scriptEditor').value;
        const finalScript = document.getElementById('finalScript');
        if (scriptEditor && !finalScript.value) {
            finalScript.value = scriptEditor;
        }
    }
}

// 显示加载状态
function showLoading(element) {
    const originalText = element.textContent;
    element.innerHTML = '<span class="loading"></span> 处理中...';
    element.disabled = true;
    return originalText;
}

// 隐藏加载状态
function hideLoading(element, originalText) {
    element.textContent = originalText;
    element.disabled = false;
}

// 显示消息
function showMessage(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
}

// 清除消息
function clearMessage(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = '';
}

// 生成灵感
async function generateInspiration() {
    const topicInput = document.getElementById('topicInput');
    const inspirationResult = document.getElementById('inspirationResult');
    const generateBtn = document.getElementById('generateInspirationBtn');
    
    const topic = topicInput.value.trim();
    if (!topic) {
        showMessage('inspirationResult', '请输入播客主题', 'warning');
        return;
    }
    
    const originalText = showLoading(generateBtn);
    clearMessage('inspirationResult');
    
    try {
        const response = await fetch('/api/generate-inspiration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ topic: topic })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 先显示成功消息
            showMessage('inspirationResult', '灵感生成成功！', 'success');
            // 然后在消息下方添加实际结果
            const resultDiv = document.createElement('div');
            resultDiv.className = 'mt-3 p-3 bg-light border rounded';
            resultDiv.textContent = data.inspiration;
            document.getElementById('inspirationResult').appendChild(resultDiv);
        } else {
            showMessage('inspirationResult', data.message, 'danger');
        }
    } catch (error) {
        showMessage('inspirationResult', `生成灵感失败: ${error.message}`, 'danger');
    } finally {
        hideLoading(generateBtn, originalText);
    }
}

// 生成文稿
async function generateScript() {
    const inspirationInput = document.getElementById('inspirationInput');
    const scriptLength = document.getElementById('scriptLength');
    const scriptResult = document.getElementById('scriptResult');
    const generateBtn = document.getElementById('generateScriptBtn');
    
    const inspiration = inspirationInput.value.trim();
    const length = parseInt(scriptLength.value);
    
    if (!inspiration) {
        showMessage('scriptResult', '请输入灵感内容', 'warning');
        return;
    }
    
    if (isNaN(length) || length < 500 || length > 10000) {
        showMessage('scriptResult', '文稿长度应在 500-10000 字符之间', 'warning');
        return;
    }
    
    const originalText = showLoading(generateBtn);
    clearMessage('scriptResult');
    
    try {
        const response = await fetch('/api/generate-script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                inspiration: inspiration, 
                length: length 
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 先显示成功消息
            showMessage('scriptResult', '文稿生成成功！', 'success');
            // 然后在消息下方添加实际结果
            const resultDiv = document.createElement('div');
            resultDiv.className = 'mt-3 p-3 bg-light border rounded';
            resultDiv.textContent = data.script;
            document.getElementById('scriptResult').appendChild(resultDiv);
        } else {
            showMessage('scriptResult', data.message, 'danger');
        }
    } catch (error) {
        showMessage('scriptResult', `生成文稿失败: ${error.message}`, 'danger');
    } finally {
        hideLoading(generateBtn, originalText);
    }
}

// 优化文稿
async function optimizeScript() {
    const scriptEditor = document.getElementById('scriptEditor');
    const optimizeBtn = document.getElementById('optimizeScriptBtn');
    
    const script = scriptEditor.value.trim();
    if (!script) {
        showMessage('validationResult', '请输入文稿内容', 'warning');
        return;
    }
    
    const originalText = showLoading(optimizeBtn);
    clearMessage('validationResult');
    
    try {
        const response = await fetch('/api/optimize-script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ script: script })
        });
        
        const data = await response.json();
        
        if (data.success) {
            scriptEditor.value = data.script;
            showMessage('validationResult', '文稿优化成功！', 'success');
        } else {
            showMessage('validationResult', data.message, 'danger');
        }
    } catch (error) {
        showMessage('validationResult', `优化文稿失败: ${error.message}`, 'danger');
    } finally {
        hideLoading(optimizeBtn, originalText);
    }
}

// 验证文稿格式
async function validateScript() {
    const scriptEditor = document.getElementById('scriptEditor');
    const validateBtn = document.getElementById('validateScriptBtn');
    
    const script = scriptEditor.value.trim();
    if (!script) {
        showMessage('validationResult', '请输入文稿内容', 'warning');
        return;
    }
    
    const originalText = showLoading(validateBtn);
    clearMessage('validationResult');
    
    try {
        const response = await fetch('/api/validate-script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ script: script })
        });
        
        const data = await response.json();
        
        if (data.valid) {
            showMessage('validationResult', data.message, 'success');
        } else {
            showMessage('validationResult', data.message, 'warning');
        }
    } catch (error) {
        showMessage('validationResult', `验证文稿失败: ${error.message}`, 'danger');
    } finally {
        hideLoading(validateBtn, originalText);
    }
}

// 复制文稿到剪贴板
function copyScript() {
    const scriptEditor = document.getElementById('scriptEditor');
    
    scriptEditor.select();
    scriptEditor.setSelectionRange(0, 99999); // 适用于移动设备
    
    try {
        document.execCommand('copy');
        showMessage('validationResult', '文稿已复制到剪贴板！', 'success');
        
        // 3秒后清除消息
        setTimeout(() => {
            clearMessage('validationResult');
        }, 3000);
    } catch (error) {
        showMessage('validationResult', '复制失败，请手动复制', 'danger');
    }
}

// 开始生成播客
async function startGeneratePodcast() {
    const finalScript = document.getElementById('finalScript');
    const voiceA = document.getElementById('voiceA');
    const voiceB = document.getElementById('voiceB');
    const startGenerateBtn = document.getElementById('startGenerateBtn');
    const generationProgress = document.getElementById('generationProgress').querySelector('.progress-bar');
    const generationStatus = document.getElementById('generationStatus');
    
    const script = finalScript.value.trim();
    
    if (!script) {
        showMessage('generationStatus', '请输入最终文稿', 'warning');
        return;
    }
    
    // 显示加载状态
    const originalText = showLoading(startGenerateBtn);
    clearMessage('generationStatus');
    
    // 重置进度条
    generationProgress.style.width = '0%';
    generationProgress.setAttribute('aria-valuenow', '0');
    
    try {
        // 更新状态
        showMessage('generationStatus', '正在生成播客...', 'info');
        
        // 打印发送到后端的声音ID
        console.log('发送到后端的声音ID:', {
            voice_a: voiceA.value,
            voice_b: voiceB.value
        });
        
        // 调用 API 生成播客
        const response = await fetch('/api/synthesize-audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                script: script,
                voice_a: voiceA.value,
                voice_b: voiceB.value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 更新进度条为 100%
            generationProgress.style.width = '100%';
            generationProgress.setAttribute('aria-valuenow', '100');
            
            // 显示成功消息
            showMessage('generationStatus', data.message, 'success');
            
            // 准备结果预览数据
            prepareResultPreview(data.audio_url, data.message);
            
            // 自动切换到结果预览标签页
            const resultTab = new bootstrap.Tab(document.getElementById('result-tab'));
            resultTab.show();
        } else {
            showMessage('generationStatus', data.message, 'danger');
        }
    } catch (error) {
        showMessage('generationStatus', `生成播客失败: ${error.message}`, 'danger');
    } finally {
        hideLoading(startGenerateBtn, originalText);
    }
}

// 准备结果预览
function prepareResultPreview(audioUrl, message) {
    const resultMessage = document.getElementById('resultMessage');
    const audioPreview = document.getElementById('audioPreview');
    const downloadSection = document.getElementById('downloadSection');
    
    // 显示结果消息
    resultMessage.innerHTML = `<div class="alert alert-success" role="alert">${message}</div>`;
    
    // 确保音频URL格式正确
    let correctedAudioUrl = audioUrl;
    if (!correctedAudioUrl.startsWith('static/')) {
        correctedAudioUrl = `static/${correctedAudioUrl}`;
    }
    
    // 创建音频预览元素
    audioPreview.innerHTML = `
        <h6>音频预览</h6>
        <audio controls>
            <source src="${correctedAudioUrl}" type="audio/mpeg">
            您的浏览器不支持音频播放。
        </audio>
        <div class="mt-2">
            <small>音频URL: ${correctedAudioUrl}</small>
        </div>
    `;
    
    // 创建下载按钮
    const fullUrl = `${window.location.origin}/${correctedAudioUrl}`;
    downloadSection.innerHTML = `
        <a href="${correctedAudioUrl}" class="btn btn-success download-btn" download>
            <i class="bi bi-download"></i> 下载播客
        </a>
    `;
}

// 辅助函数：获取 CSRF 令牌
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : '';
}

// 辅助函数：格式化时间
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// 辅助函数：计算文稿字数
function countCharacters(text) {
    return text.length;
}

// 辅助函数：计算对话句数
function countDialogues(text) {
    const lines = text.split('\n');
    let count = 0;
    
    lines.forEach(line => {
        line = line.trim();
        if (line.startsWith('[A]') || line.startsWith('[B]')) {
            count++;
        }
    });
    
    return count;
}
