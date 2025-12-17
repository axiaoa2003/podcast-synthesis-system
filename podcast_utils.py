from pydub import AudioSegment
import os
import re
from config import SYSTEM_CONFIG

def parse_dialogue(script):
    """
    解析双人对话文稿，返回角色和文本列表
    
    参数:
    - script: 播客文稿文本
    
    返回:
    - 对话列表，每个元素为 (角色, 文本) 元组
    """
    dialogue = []
    # 使用正则表达式匹配角色标记和文本
    lines = script.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 匹配 [A] 或 [B] 开头的行，支持中文冒号和英文冒号
        match = re.match(r'^\[([AB])\]\s*[:：]\s*(.*)$', line)
        if match:
            role = match.group(1)
            text = match.group(2).strip()
            if text:
                dialogue.append((role, text))
        else:
            # 如果没有角色标记，尝试合并到上一行
            if dialogue:
                prev_role, prev_text = dialogue[-1]
                dialogue[-1] = (prev_role, f"{prev_text} {line}")
    
    return dialogue

def generate_audio_segments(dialogue, voice_map, minimax_client, output_dir=SYSTEM_CONFIG["output_dir"]):
    """
    逐句合成音频片段
    
    参数:
    - dialogue: 对话列表，由 parse_dialogue 返回
    - voice_map: 角色到声音 ID 的映射
    - minimax_client: MiniMaxClient 实例
    - output_dir: 输出目录
    
    返回:
    - 生成的音频文件路径列表
    """
    audio_files = []
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    for i, (role, text) in enumerate(dialogue):
        if not text:
            continue
        
        # 获取声音配置
        voice_config = voice_map[role]
        
        # 解析声音配置
        if isinstance(voice_config, dict):
            voice_id = voice_config.get('id', 'male-qn-qingse')
            speed = voice_config.get('speed', 1.0)
            pitch = voice_config.get('pitch', 0)
        else:
            # 兼容旧的字符串格式
            voice_id = voice_config
            speed = 1.0
            pitch = 0
        
        # 调用 MiniMax API 合成音频
        print(f"正在为角色 {role} 生成音频，使用声音ID: {voice_id}, 语速: {speed}, 语调: {pitch}")
        result = minimax_client.synthesize_speech(
            text=text,
            voice_id=voice_id,
            speed=speed,
            pitch=pitch
        )
        
        if "error" in result:
            print(f"合成音频失败 (第 {i+1} 句): {result['error']}")
            continue
        
        # 检查 API 响应状态
        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            print(f"合成音频失败 (第 {i+1} 句): {base_resp.get('status_msg', '未知错误')}")
            continue
        
        # 获取音频数据
        data = result.get("data", {})
        hex_audio = data.get("audio", "")
        if not hex_audio:
            print(f"合成音频失败 (第 {i+1} 句): 未返回音频数据")
            continue
        
        # 保存音频文件
        output_path = os.path.join(output_dir, f"segment_{i:03d}_{role}.mp3")
        if minimax_client.hex_to_audio_file(hex_audio, output_path):
            audio_files.append(output_path)
            print(f"成功生成音频片段: {output_path}")
        else:
            print(f"保存音频文件失败: {output_path}")
    
    return audio_files

def merge_audio_files(audio_files, output_path):
    """
    拼接音频文件
    
    参数:
    - audio_files: 音频文件路径列表，按顺序拼接
    - output_path: 输出文件路径
    
    返回:
    - True 表示成功，False 表示失败
    """
    try:
        # 创建空的音频片段
        combined = AudioSegment.empty()
        
        # 逐个添加音频文件
        for file in audio_files:
            audio = AudioSegment.from_mp3(file)
            combined += audio
        
        # 导出合并后的音频
        combined.export(output_path, format="mp3")
        print(f"成功合并音频文件: {output_path}")
        return True
    except Exception as e:
        print(f"合并音频文件失败: {str(e)}")
        return False

def clean_temp_files(file_list):
    """
    清理临时文件
    
    参数:
    - file_list: 要清理的文件路径列表
    
    返回:
    - 成功清理的文件数量
    """
    count = 0
    for file in file_list:
        try:
            os.remove(file)
            count += 1
        except Exception as e:
            print(f"清理文件失败 {file}: {str(e)}")
    return count

def validate_script(script):
    """
    验证文稿格式
    
    参数:
    - script: 播客文稿文本
    
    返回:
    - 包含验证结果的字典
    """
    dialogue = parse_dialogue(script)
    
    if not dialogue:
        return {
            "valid": False,
            "message": "文稿中未找到有效的对话内容，请使用 [A] 和 [B] 标记角色"
        }
    
    # 检查角色分布
    role_counts = {"A": 0, "B": 0}
    for role, _ in dialogue:
        role_counts[role] += 1
    
    if role_counts["A"] == 0 or role_counts["B"] == 0:
        return {
            "valid": False,
            "message": "文稿中缺少一个或多个角色的对话"
        }
    
    return {
        "valid": True,
        "message": f"文稿验证通过，包含 {len(dialogue)} 句对话，角色 A: {role_counts['A']} 句，角色 B: {role_counts['B']} 句",
        "dialogue_count": len(dialogue),
        "role_counts": role_counts
    }
