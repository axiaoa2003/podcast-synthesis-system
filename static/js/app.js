// 双人对话播客合成系统 - 前端交互逻辑

// 防抖工具函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 友好的错误信息处理
function getFriendlyErrorMessage(error, operation) {
    const errorMsg = error.message || error.toString();

    // 网络相关错误
    if (errorMsg.includes('Failed to fetch') || errorMsg.includes('NetworkError')) {
        return `${operation}失败：无法连接到服务器，请检查网络连接或确认后端服务已启动`;
    }

    // API 密钥相关错误
    if (errorMsg.includes('401') || errorMsg.includes('Unauthorized') || errorMsg.includes('API_KEY_INVALID')) {
        return `${operation}失败：API密钥无效，请检查"API密钥配置"中的密钥是否正确`;
    }

    if (errorMsg.includes('429') || errorMsg.includes('rate limit') || errorMsg.includes('QUOTA_EXCEEDED')) {
        return `${operation}失败：API调用次数超限或配额不足，请稍后再试`;
    }

    if (errorMsg.includes('403') || errorMsg.includes('Forbidden')) {
        return `${operation}失败：权限不足，请检查API密钥权限`;
    }

    // 服务器错误
    if (errorMsg.includes('500') || errorMsg.includes('502') || errorMsg.includes('503')) {
        return `${operation}失败：服务器错误，请稍后重试`;
    }

    if (errorMsg.includes('timeout') || errorMsg.includes('Timeout')) {
        return `${operation}失败：请求超时，请检查网络连接或稍后重试`;
    }

    // 其他错误，显示原始信息
    return `${operation}失败：${errorMsg}`;
}

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
    document.getElementById('refreshEmotionPanelBtn').addEventListener('click', renderEmotionConfigPanel);
    
    // 4. 播客生成
    document.getElementById('startGenerateBtn').addEventListener('click', startGeneratePodcast);

    // 5. 标签页切换事件
    const tabElements = document.querySelectorAll('#podcastTabs button');
    tabElements.forEach(tab => {
        tab.addEventListener('shown.bs.tab', handleTabChange);
    });

    // 6. 初始化声音选择Dropdown
    initializeVoiceDropdowns();

    // 7. 文稿编辑器事件（使用防抖优化性能）
    const scriptEditor = document.getElementById('scriptEditor');
    if (scriptEditor) {
        const debouncedRender = debounce(renderEmotionConfigPanel, 300);
        scriptEditor.addEventListener('input', debouncedRender);
        scriptEditor.addEventListener('change', renderEmotionConfigPanel);
    }
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
        const friendlyMsg = getFriendlyErrorMessage(error, '生成灵感');
        showMessage('inspirationResult', friendlyMsg, 'danger');
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
            // 将生成的文稿自动填充到编辑器中
            document.getElementById('scriptEditor').value = data.script;
        } else {
            showMessage('scriptResult', data.message, 'danger');
        }
    } catch (error) {
        const friendlyMsg = getFriendlyErrorMessage(error, '生成文稿');
        showMessage('scriptResult', friendlyMsg, 'danger');
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
        const friendlyMsg = getFriendlyErrorMessage(error, '优化文稿');
        showMessage('validationResult', friendlyMsg, 'danger');
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
        const friendlyMsg = getFriendlyErrorMessage(error, '验证文稿');
        showMessage('validationResult', friendlyMsg, 'danger');
    } finally {
        hideLoading(validateBtn, originalText);
    }
}

// 复制文稿到剪贴板
async function copyScript() {
    const scriptEditor = document.getElementById('scriptEditor');

    try {
        await navigator.clipboard.writeText(scriptEditor.value);
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
        const friendlyMsg = getFriendlyErrorMessage(error, '生成播客');
        showMessage('generationStatus', friendlyMsg, 'danger');
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

// 初始化声音选择Dropdown
function initializeVoiceDropdowns() {
    // 处理声音A的Dropdown
    const voiceADropdown = document.getElementById('voiceADropdown');
    const voiceA = document.getElementById('voiceA');
    const voiceAItems = document.querySelectorAll('#voiceADropdown + .dropdown-menu .dropdown-item');
    
    // 处理声音B的Dropdown
    const voiceBDropdown = document.getElementById('voiceBDropdown');
    const voiceB = document.getElementById('voiceB');
    const voiceBItems = document.querySelectorAll('#voiceBDropdown + .dropdown-menu .dropdown-item');
    
    // 更新Dropdown按钮显示当前选中的值
    function updateDropdownButton(dropdownButton, selectElement) {
        const selectedValue = selectElement.value;
        const selectedOption = selectElement.querySelector(`option[value="${selectedValue}"]`);
        if (selectedOption && dropdownButton) {
            dropdownButton.textContent = selectedOption.textContent;
        }
    }
    
    // 初始化Dropdown按钮显示
    updateDropdownButton(voiceADropdown, voiceA);
    updateDropdownButton(voiceBDropdown, voiceB);
    
    // 为声音A的Dropdown菜单项添加点击事件
    voiceAItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const value = this.getAttribute('data-value');
            const text = this.textContent;
            
            // 更新隐藏的select元素
            voiceA.value = value;
            
            // 更新Dropdown按钮文本
            voiceADropdown.textContent = text;
        });
    });
    
    // 为声音B的Dropdown菜单项添加点击事件
    voiceBItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const value = this.getAttribute('data-value');
            const text = this.textContent;
            
            // 更新隐藏的select元素
            voiceB.value = value;
            
            // 更新Dropdown按钮文本
            voiceBDropdown.textContent = text;
        });
    });
}

// 文本文稿转结构化数据
function parseScriptToDialogues(script) {
    const dialogues = [];
    const lines = script.split('\n');
    
    lines.forEach(line => {
        line = line.trim();
        if (!line) {
            // 保留空行
            dialogues.push({ type: 'empty' });
            return;
        }
        
        // 匹配带情绪参数的格式
        const match = line.match(/^\[([AB])\]\(([^,]*),([^,]+),([^)]+)\)\s*[:：]\s*(.*)$/);
        if (match) {
            dialogues.push({
                type: 'dialogue',
                role: match[1],
                text: match[5].trim(),
                emotion: match[2].trim(),
                speed: parseFloat(match[3].trim()),
                pitch: parseInt(match[4].trim())
            });
        } else {
            // 匹配不带情绪参数的格式
            const simpleMatch = line.match(/^\[([AB])\]\s*[:：]\s*(.*)$/);
            if (simpleMatch) {
                dialogues.push({
                    type: 'dialogue',
                    role: simpleMatch[1],
                    text: simpleMatch[2].trim(),
                    emotion: '',
                    speed: 1.0,
                    pitch: 0
                });
            } else {
                // 保留其他类型的行（如注释、说明等）
                dialogues.push({ type: 'other', content: line });
            }
        }
    });
    
    return dialogues;
}

// 结构化数据转文本文稿
function dialoguesToScript(dialogues) {
    let script = '';
    dialogues.forEach(item => {
        if (item.type === 'dialogue') {
            const dialogue = item;
            if (dialogue.emotion || dialogue.speed !== 1.0 || dialogue.pitch !== 0) {
                // 带情绪参数的格式
                script += `[${dialogue.role}](${dialogue.emotion || ''},${dialogue.speed},${dialogue.pitch}): ${dialogue.text}\n`;
            } else {
                // 不带情绪参数的格式
                script += `[${dialogue.role}]: ${dialogue.text}\n`;
            }
        } else if (item.type === 'empty') {
            // 保留空行
            script += '\n';
        } else if (item.type === 'other') {
            // 保留其他类型的行
            script += `${item.content}\n`;
        }
    });
    return script;
}

// 渲染情绪配置面板
function renderEmotionConfigPanel() {
    const script = document.getElementById('scriptEditor').value;
    const panel = document.getElementById('emotionConfigPanel');
    
    // 解析文稿，获取对话列表
    const items = parseScriptToDialogues(script);
    
    // 过滤出只包含对话类型的项
    const dialogues = items.filter(item => item.type === 'dialogue');
    
    // 渲染配置面板
    panel.innerHTML = '';
    dialogues.forEach((dialogue, index) => {
        const configDiv = document.createElement('div');
        configDiv.className = 'mb-3 p-3 border rounded';
        configDiv.innerHTML = `
            <h6>第 ${index + 1} 句 [${dialogue.role}]</h6>
            <p class="text-muted">${dialogue.text}</p>
            <div class="row">
                <div class="col-md-4">
                    <label for="emotion-${index}" class="form-label">情绪</label>
                    <select class="form-select" id="emotion-${index}" data-index="${index}">
                        <option value="" ${dialogue.emotion === '' ? 'selected' : ''}>自动</option>
                        <option value="happy" ${dialogue.emotion === 'happy' ? 'selected' : ''}>高兴</option>
                        <option value="sad" ${dialogue.emotion === 'sad' ? 'selected' : ''}>悲伤</option>
                        <option value="angry" ${dialogue.emotion === 'angry' ? 'selected' : ''}>愤怒</option>
                        <option value="fearful" ${dialogue.emotion === 'fearful' ? 'selected' : ''}>害怕</option>
                        <option value="disgusted" ${dialogue.emotion === 'disgusted' ? 'selected' : ''}>厌恶</option>
                        <option value="surprised" ${dialogue.emotion === 'surprised' ? 'selected' : ''}>惊讶</option>
                        <option value="calm" ${dialogue.emotion === 'calm' ? 'selected' : ''}>中性</option>
                        <option value="fluent" ${dialogue.emotion === 'fluent' ? 'selected' : ''}>生动</option>
                        <option value="whisper" ${dialogue.emotion === 'whisper' ? 'selected' : ''}>低语</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label for="speed-${index}" class="form-label">语速 (0.5-2.0)</label>
                    <input type="range" class="form-range" id="speed-${index}" min="0.5" max="2.0" step="0.1" 
                           value="${dialogue.speed || 1.0}" data-index="${index}">
                    <div class="text-center">${dialogue.speed || 1.0}</div>
                </div>
                <div class="col-md-4">
                    <label for="pitch-${index}" class="form-label">语调 (-12-12)</label>
                    <input type="range" class="form-range" id="pitch-${index}" min="-12" max="12" step="1" 
                           value="${dialogue.pitch || 0}" data-index="${index}">
                    <div class="text-center">${dialogue.pitch || 0}</div>
                </div>
            </div>
        `;
        panel.appendChild(configDiv);
    });
    
    // 添加事件监听器
    addEmotionConfigListeners();
}

// 添加情绪配置面板事件监听器
function addEmotionConfigListeners() {
    // 情绪选择事件
    document.querySelectorAll('[id^="emotion-"]').forEach(select => {
        select.addEventListener('change', updateScriptFromConfig);
    });
    
    // 语速滑块事件
    document.querySelectorAll('[id^="speed-"]').forEach(range => {
        range.addEventListener('input', function() {
            this.nextElementSibling.textContent = this.value;
            updateScriptFromConfig();
        });
    });
    
    // 语调滑块事件
    document.querySelectorAll('[id^="pitch-"]').forEach(range => {
        range.addEventListener('input', function() {
            this.nextElementSibling.textContent = this.value;
            updateScriptFromConfig();
        });
    });
}

// 根据情绪配置面板更新文稿
function updateScriptFromConfig() {
    // 从配置面板获取所有对话行的情绪参数
    const configs = [];
    document.querySelectorAll('[id^="emotion-"]').forEach((select, index) => {
        const emotion = select.value;
        const speed = document.getElementById(`speed-${index}`).value;
        const pitch = document.getElementById(`pitch-${index}`).value;
        configs.push({ emotion, speed, pitch });
    });
    
    // 解析当前文稿，获取所有行（包括对话、空行、其他类型）
    const script = document.getElementById('scriptEditor').value;
    const items = parseScriptToDialogues(script);
    
    // 遍历所有行，更新对话行的情绪参数，保留其他类型的行不变
    let dialogueIndex = 0;
    const updatedItems = items.map(item => {
        if (item.type === 'dialogue') {
            // 更新对话行的情绪参数
            const config = configs[dialogueIndex] || { emotion: '', speed: '1.0', pitch: '0' };
            const updatedDialogue = {
                ...item,
                emotion: config.emotion,
                speed: parseFloat(config.speed),
                pitch: parseInt(config.pitch)
            };
            dialogueIndex++;
            return updatedDialogue;
        } else {
            // 保留其他类型的行不变
            return item;
        }
    });
    
    // 转换回文本文稿
    const updatedScript = dialoguesToScript(updatedItems);
    
    // 更新文本编辑器
    document.getElementById('scriptEditor').value = updatedScript;
}
