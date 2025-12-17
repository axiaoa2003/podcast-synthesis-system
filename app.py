from flask import Flask, render_template, request, jsonify
import os
import uuid
from deepseek_client import DeepSeekClient
from minimax_client import MiniMaxClient
from podcast_utils import (
    parse_dialogue,
    generate_audio_segments,
    merge_audio_files,
    validate_script,
    clean_temp_files
)
from config import SYSTEM_CONFIG, MINIMAX_CONFIG

app = Flask(__name__)

# 初始化 API 客户端
deepseek_client = DeepSeekClient()
minimax_client = MiniMaxClient()

# 首页路由
@app.route('/')
def index():
    # 获取可用声音列表
    voices = minimax_client.get_voice_list()
    return render_template('index.html', voices=voices)

# 生成灵感路由
@app.route('/api/generate-inspiration', methods=['POST'])
def api_generate_inspiration():
    data = request.json
    topic = data.get('topic', '')
    
    if not topic:
        return jsonify({'success': False, 'message': '请输入播客主题'})
    
    try:
        inspiration = deepseek_client.generate_inspiration(topic)
        return jsonify({'success': True, 'inspiration': inspiration})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成灵感失败: {str(e)}'})

# 生成文稿路由
@app.route('/api/generate-script', methods=['POST'])
def api_generate_script():
    data = request.json
    inspiration = data.get('inspiration', '')
    length = data.get('length', SYSTEM_CONFIG['default_script_length'])
    
    if not inspiration:
        return jsonify({'success': False, 'message': '请提供灵感内容'})
    
    try:
        script = deepseek_client.generate_script(inspiration, length=length)
        return jsonify({'success': True, 'script': script})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成文稿失败: {str(e)}'})

# 优化文稿路由
@app.route('/api/optimize-script', methods=['POST'])
def api_optimize_script():
    data = request.json
    script = data.get('script', '')
    
    if not script:
        return jsonify({'success': False, 'message': '请提供文稿内容'})
    
    try:
        optimized_script = deepseek_client.optimize_script(script)
        return jsonify({'success': True, 'script': optimized_script})
    except Exception as e:
        return jsonify({'success': False, 'message': f'优化文稿失败: {str(e)}'})

# 合成音频路由
@app.route('/api/synthesize-audio', methods=['POST'])
def api_synthesize_audio():
    data = request.json
    script = data.get('script', '')
    voice_a = data.get('voice_a', MINIMAX_CONFIG['default_voices']['A'])
    voice_b = data.get('voice_b', MINIMAX_CONFIG['default_voices']['B'])
    
    if not script:
        return jsonify({'success': False, 'message': '请提供文稿内容'})
    
    try:
        # 验证文稿格式
        validation = validate_script(script)
        if not validation['valid']:
            return jsonify({'success': False, 'message': validation['message']})
        
        # 解析对话
        dialogue = parse_dialogue(script)
        if not dialogue:
            return jsonify({'success': False, 'message': '文稿中未找到有效的对话内容'})
        
        # 打印接收到的声音配置
        print(f"接收到的声音配置 - A: {voice_a}, B: {voice_b}")
        
        # 从AVAILABLE_VOICES中查找对应的声音配置
        from config import AVAILABLE_VOICES
        
        # 创建声音映射
        voice_map = {}
        
        # 处理角色A的声音配置
        for voice in AVAILABLE_VOICES:
            if voice['id'] == voice_a:
                voice_map['A'] = voice
                break
        else:
            # 如果没有找到，使用默认配置
            voice_map['A'] = MINIMAX_CONFIG['default_voices']['A']
        
        # 处理角色B的声音配置
        for voice in AVAILABLE_VOICES:
            if voice['id'] == voice_b:
                voice_map['B'] = voice
                break
        else:
            # 如果没有找到，使用默认配置
            voice_map['B'] = MINIMAX_CONFIG['default_voices']['B']
        
        # 打印声音映射
        print(f"创建的声音映射: {voice_map}")
        
        # 生成唯一标识符
        session_id = str(uuid.uuid4())
        output_dir = os.path.join(SYSTEM_CONFIG['output_dir'], session_id)
        
        # 生成音频片段
        audio_files = generate_audio_segments(
            dialogue=dialogue,
            voice_map=voice_map,
            minimax_client=minimax_client,
            output_dir=output_dir
        )
        
        if not audio_files:
            return jsonify({'success': False, 'message': '生成音频片段失败'})
        
        # 检查生成的音频片段数量是否与对话数量一致
        if len(audio_files) != len(dialogue):
            return jsonify({'success': False, 'message': f'生成音频片段不完整，成功生成 {len(audio_files)} 个片段，共需生成 {len(dialogue)} 个片段'})
        
        # 合并音频文件
        final_output = os.path.join(SYSTEM_CONFIG['output_dir'], f'podcast_{session_id}.mp3')
        success = merge_audio_files(audio_files, final_output)
        
        if not success:
            return jsonify({'success': False, 'message': '合并音频失败'})
        
        # 清理临时文件
        clean_temp_files(audio_files)
        
        # 返回相对路径，便于前端访问
        # 确保路径格式正确，使用 '/' 分隔符
        relative_path = final_output.replace('\\', '/')
        
        return jsonify({
            'success': True,
            'audio_url': relative_path,
            'message': f'播客生成成功，共 {len(dialogue)} 句对话',
            'dialogue_count': len(dialogue),
            'audio_files_count': len(audio_files)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成音频失败: {str(e)}'})

# 验证文稿路由
@app.route('/api/validate-script', methods=['POST'])
def api_validate_script():
    data = request.json
    script = data.get('script', '')
    
    if not script:
        return jsonify({'success': False, 'message': '请提供文稿内容'})
    
    validation = validate_script(script)
    return jsonify(validation)

if __name__ == '__main__':
    # 创建静态音频目录
    os.makedirs(SYSTEM_CONFIG['output_dir'], exist_ok=True)
    
    # 启动 Flask 应用
    app.run(debug=True, host='0.0.0.0', port=5000)
