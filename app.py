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

# 首页路由
@app.route('/')
def index():
    # 初始化默认客户端
    minimax_client = MiniMaxClient()
    # 获取可用声音列表
    voices = minimax_client.get_voice_list()
    return render_template('index.html', voices=voices)

# 生成灵感路由
@app.route('/api/generate-inspiration', methods=['POST'])
def api_generate_inspiration():
    """
    生成灵感路由
    
    请求体参数:
    - topic: 播客主题，字符串，必填
    - deepseek_api_key: DeepSeek API密钥，字符串，可选
    
    请求头参数:
    - X-DeepSeek-API-Key: DeepSeek API密钥，字符串，可选（优先级高于请求体中的api_key）
    
    响应:
    - success: 布尔值，表示请求是否成功
    - message: 字符串，表示请求结果的描述
    - inspiration: 字符串，表示生成的灵感内容
    """
    data = request.json
    topic = data.get('topic', '')
    
    if not topic:
        return jsonify({'success': False, 'message': '请输入播客主题'})
    
    try:
        # 从请求中获取API密钥
        api_key = request.headers.get('X-DeepSeek-API-Key') or data.get('deepseek_api_key', '')
        # 初始化客户端
        deepseek_client = DeepSeekClient(api_key=api_key)
        
        inspiration = deepseek_client.generate_inspiration(topic)
        return jsonify({'success': True, 'inspiration': inspiration})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成灵感失败: {str(e)}'})

# 生成文稿路由
@app.route('/api/generate-script', methods=['POST'])
def api_generate_script():
    """
    生成文稿路由
    
    请求体参数:
    - inspiration: 灵感内容，字符串，必填
    - length: 文稿长度，整数，可选，默认值为配置文件中的default_script_length
    - deepseek_api_key: DeepSeek API密钥，字符串，可选
    
    请求头参数:
    - X-DeepSeek-API-Key: DeepSeek API密钥，字符串，可选（优先级高于请求体中的api_key）
    
    响应:
    - success: 布尔值，表示请求是否成功
    - message: 字符串，表示请求结果的描述
    - script: 字符串，表示生成的文稿内容
    """
    data = request.json
    inspiration = data.get('inspiration', '')
    length = data.get('length', SYSTEM_CONFIG['default_script_length'])
    
    if not inspiration:
        return jsonify({'success': False, 'message': '请提供灵感内容'})
    
    try:
        # 从请求中获取API密钥
        api_key = request.headers.get('X-DeepSeek-API-Key') or data.get('deepseek_api_key', '')
        # 初始化客户端
        deepseek_client = DeepSeekClient(api_key=api_key)
        
        script = deepseek_client.generate_script(inspiration, length=length)
        
        # 应用格式修复和清理
        from podcast_utils import fix_script_format, clean_script
        script = fix_script_format(script)
        script = clean_script(script)
        
        return jsonify({'success': True, 'script': script})
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成文稿失败: {str(e)}'})

# 优化文稿路由
@app.route('/api/optimize-script', methods=['POST'])
def api_optimize_script():
    """
    优化文稿路由
    
    请求体参数:
    - script: 文稿内容，字符串，必填
    - deepseek_api_key: DeepSeek API密钥，字符串，可选
    
    请求头参数:
    - X-DeepSeek-API-Key: DeepSeek API密钥，字符串，可选（优先级高于请求体中的api_key）
    
    响应:
    - success: 布尔值，表示请求是否成功
    - message: 字符串，表示请求结果的描述
    - script: 字符串，表示优化后的文稿内容
    """
    data = request.json
    script = data.get('script', '')
    
    if not script:
        return jsonify({'success': False, 'message': '请提供文稿内容'})
    
    try:
        # 从请求中获取API密钥
        api_key = request.headers.get('X-DeepSeek-API-Key') or data.get('deepseek_api_key', '')
        # 初始化客户端
        deepseek_client = DeepSeekClient(api_key=api_key)
        
        optimized_script = deepseek_client.optimize_script(script)
        
        # 应用格式修复和清理
        from podcast_utils import fix_script_format, clean_script
        optimized_script = fix_script_format(optimized_script)
        optimized_script = clean_script(optimized_script)
        
        return jsonify({'success': True, 'script': optimized_script})
    except Exception as e:
        return jsonify({'success': False, 'message': f'优化文稿失败: {str(e)}'})

# 合成音频路由
@app.route('/api/synthesize-audio', methods=['POST'])
def api_synthesize_audio():
    """
    合成音频路由
    
    请求体参数:
    - script: 播客文稿文本，支持JSON格式或文本格式
    - voice_a: 角色A的声音ID
    - voice_b: 角色B的声音ID
    - emotion_a: 角色A的默认情绪
    - emotion_b: 角色B的默认情绪
    - minimax_api_key: MiniMax API密钥
    
    响应:
    - success: 布尔值，表示请求是否成功
    - message: 字符串，表示请求结果的描述
    - audio_url: 字符串，表示生成的音频文件的相对路径
    - dialogue_count: 整数，表示文稿中的对话数量
    - audio_files_count: 整数，表示成功生成的音频片段数量
    """
    data = request.json
    script = data.get('script', '')
    voice_a = data.get('voice_a', MINIMAX_CONFIG['default_voices']['A'])
    voice_b = data.get('voice_b', MINIMAX_CONFIG['default_voices']['B'])
    
    print(f"接收到音频合成请求，脚本长度: {len(script)} 字符")
    
    if not script:
        print("错误: 未提供文稿内容")
        return jsonify({'success': False, 'message': '请提供文稿内容'})
    
    try:
        # 从请求中获取API密钥
        api_key = request.headers.get('X-MiniMax-API-Key') or data.get('minimax_api_key', '')
        print(f"使用API密钥: {'已提供' if api_key else '未提供，将使用配置文件中的默认值'}")
        
        # 初始化MiniMax客户端
        minimax_client = MiniMaxClient(api_key=api_key)
        
        # 获取情绪参数
        emotion_a = data.get('emotion_a', '')
        emotion_b = data.get('emotion_b', '')
        
        # 应用格式修复和清理
        from podcast_utils import fix_script_format, clean_script
        script = fix_script_format(script)
        script = clean_script(script)
        
        # 验证文稿格式
        validation = validate_script(script)
        if not validation['valid']:
            print(f"文稿验证失败: {validation['message']}")
            return jsonify({'success': False, 'message': validation['message']})
        print(f"文稿验证通过: {validation['message']}")
        
        # 解析对话
        dialogue = parse_dialogue(script)
        if not dialogue:
            print("错误: 文稿中未找到有效的对话内容")
            return jsonify({'success': False, 'message': '文稿中未找到有效的对话内容'})
        print(f"成功解析对话，共 {len(dialogue)} 句")
        
        # 打印接收到的声音配置
        print(f"接收到的声音配置 - A: {voice_a} (情绪: {emotion_a}), B: {voice_b} (情绪: {emotion_b})")
        
        # 创建配置映射，包含声音ID和情绪
        voice_config = {
            'A': {
                'voice_id': voice_a,
                'emotion': emotion_a
            },
            'B': {
                'voice_id': voice_b,
                'emotion': emotion_b
            }
        }
        
        # 打印声音配置
        print(f"创建的声音配置: {voice_config}")
        
        # 生成唯一标识符
        session_id = str(uuid.uuid4())
        output_dir = os.path.join(SYSTEM_CONFIG['output_dir'], session_id)
        print(f"创建临时目录: {output_dir}")
        
        # 生成音频片段
        audio_files = generate_audio_segments(
            dialogue=dialogue,
            voice_config=voice_config,  # 传递包含情绪的配置
            minimax_client=minimax_client,
            output_dir=output_dir
        )
        
        if not audio_files:
            print("错误: 生成音频片段失败")
            return jsonify({'success': False, 'message': '生成音频片段失败'})
        
        # 检查生成的音频片段数量是否与对话数量一致
        if len(audio_files) != len(dialogue):
            print(f"错误: 生成音频片段不完整，成功生成 {len(audio_files)} 个片段，共需生成 {len(dialogue)} 个片段")
            return jsonify({'success': False, 'message': f'生成音频片段不完整，成功生成 {len(audio_files)} 个片段，共需生成 {len(dialogue)} 个片段'})
        print(f"成功生成 {len(audio_files)} 个音频片段")
        
        # 合并音频文件
        final_output = os.path.join(SYSTEM_CONFIG['output_dir'], f'podcast_{session_id}.mp3')
        print(f"正在合并音频文件，输出路径: {final_output}")
        success = merge_audio_files(audio_files, final_output)
        
        if not success:
            print("错误: 合并音频失败")
            return jsonify({'success': False, 'message': '合并音频失败'})
        print(f"成功合并音频文件: {final_output}")
        
        # 清理临时文件
        print(f"正在清理临时文件，共 {len(audio_files)} 个文件")
        clean_temp_files(audio_files)
        
        # 返回相对路径，便于前端访问
        # 确保路径格式正确，使用 '/' 分隔符
        relative_path = final_output.replace('\\', '/')
        
        print(f"音频合成成功，返回路径: {relative_path}")
        return jsonify({
            'success': True,
            'audio_url': relative_path,
            'message': f'播客生成成功，共 {len(dialogue)} 句对话',
            'dialogue_count': len(dialogue),
            'audio_files_count': len(audio_files)
        })
    except Exception as e:
        print(f"错误: 生成音频失败 - {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'生成音频失败: {str(e)}'})

# 验证文稿路由
@app.route('/api/validate-script', methods=['POST'])
def api_validate_script():
    """
    验证文稿路由
    
    请求体参数:
    - script: 文稿内容，字符串，必填
    
    响应:
    - valid: 布尔值，表示文稿是否有效
    - message: 字符串，表示验证结果的描述
    - dialogue_count: 整数，表示文稿中的对话数量（仅当valid为true时返回）
    - role_counts: 字典，表示各角色的对话数量分布（仅当valid为true时返回）
    """
    data = request.json
    script = data.get('script', '')
    
    if not script:
        return jsonify({'success': False, 'message': '请提供文稿内容'})
    
    validation = validate_script(script)
    return jsonify(validation)

# 获取音色列表路由
@app.route('/api/get-voice-list', methods=['POST'])
def api_get_voice_list():
    """
    获取音色列表路由
    
    请求体参数:
    - minimax_api_key: MiniMax API密钥，字符串，可选
    
    请求头参数:
    - X-MiniMax-API-Key: MiniMax API密钥，字符串，可选（优先级高于请求体中的api_key）
    
    响应:
    - success: 布尔值，表示请求是否成功
    - message: 字符串，表示请求结果的描述
    - voices: 数组，表示可用的音色列表，每个元素包含id和name字段
    """
    try:
        # 从请求中获取API密钥
        api_key = request.headers.get('X-MiniMax-API-Key') or request.json.get('minimax_api_key', '')
        
        # 初始化MiniMax客户端
        minimax_client = MiniMaxClient(api_key=api_key)
        
        # 获取可用声音列表
        voices = minimax_client.get_voice_list()
        
        return jsonify({'success': True, 'voices': voices})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取音色列表失败: {str(e)}'})

if __name__ == '__main__':
    # 创建静态音频目录
    os.makedirs(SYSTEM_CONFIG['output_dir'], exist_ok=True)
    
    # 启动 Flask 应用
    app.run(debug=True, host='0.0.0.0', port=5000)
