from pydub import AudioSegment
import os
import re
from config import SYSTEM_CONFIG

def parse_dialogue(script):
    """
    解析双人对话文稿，支持逐句情绪参数
    
    参数:
    - script: 播客文稿文本或JSON字符串
    
    返回:
    - 对话列表，每个元素为 (角色, 文本, 情绪, 语速, 语调) 元组
    """
    # 尝试解析为JSON
    try:
        import json
        data = json.loads(script)
        dialogues = data.get('dialogues', [])
        result = []
        for d in dialogues:
            result.append((
                d.get('role', 'A'),
                d.get('text', ''),
                d.get('emotion', ''),
                d.get('speed', 1.0),
                d.get('pitch', 0)
            ))
        print(f"成功解析JSON格式文稿，共 {len(result)} 句对话")
        return result
    except json.JSONDecodeError:
        # 解析为文本文稿
        print("解析为文本文稿格式")
        pass
    
    dialogue = []
    lines = script.split('\n')
    
    for line_number, line in enumerate(lines, 1):
        original_line = line.strip()
        line = original_line.strip()
        if not line:
            continue
        
        # 忽略注释行（以#开头）
        if line.startswith('#'):
            print(f"正在解析第 {line_number} 行: {original_line} - 跳过注释行")
            continue
        
        print(f"正在解析第 {line_number} 行: {original_line}")
        
        # 匹配带情绪参数的格式：[A](happy,1.2,0): 文本内容
        # 增强正则表达式，支持更灵活的格式，包括空格处理
        pattern = r'^\[([AB])\]\(([^,]+),([^,]+),([^)]+)\)\s*[:：]\s*(.*)$'
        match = re.match(pattern, line)
        if match:
            # 成功匹配带元数据的格式
            role = match.group(1)
            emotion = match.group(2).strip()
            speed_str = match.group(3).strip()
            pitch_str = match.group(4).strip()
            text = match.group(5).strip()
            
            try:
                # 转换数值参数
                speed = float(speed_str)
                pitch = int(pitch_str)
                
                if text:
                    dialogue.append((role, text, emotion, speed, pitch))
                    print(f"  解析成功: 角色={role}, 情绪={emotion}, 语速={speed}, 语调={pitch}, 对话='{text[:20]}...'")
                else:
                    print(f"  解析警告: 第 {line_number} 行对话内容为空")
            except ValueError as e:
                print(f"  解析错误: 第 {line_number} 行参数格式无效 - {e}")
                # 尝试作为无元数据格式处理
                continue
        else:
            # 匹配不带情绪参数的格式：[A]: 文本内容
            simple_pattern = r'^\[([AB])\]\s*[:：]\s*(.*)$'
            simple_match = re.match(simple_pattern, line)
            
            if simple_match:
                role = simple_match.group(1)
                text = simple_match.group(2).strip()
                
                if text:
                    dialogue.append((role, text, '', 1.0, 0))
                    print(f"  解析成功: 角色={role}, 对话='{text[:20]}...'")
                else:
                    print(f"  解析警告: 第 {line_number} 行对话内容为空")
            else:
                print(f"  解析错误: 第 {line_number} 行格式无效，应为 [A]: 对话 或 [A](情绪,语速,语调): 对话")
    
    print(f"文稿解析完成，共解析 {len(dialogue)} 句对话")
    return dialogue

def fix_script_format(script):
    """
    修复文稿格式，确保符合正则表达式规范
    
    参数:
    - script: 播客文稿文本
    
    返回:
    - 修复后的文稿文本
    """
    fixed_lines = []
    lines = script.split('\n')
    
    for line in lines:
        original_line = line.strip()
        line = original_line.strip()
        if not line:
            fixed_lines.append('')
            continue
        
        print(f"修复格式 - 原行: {original_line}")
        
        # 检查是否已经符合格式（包括带元数据和普通格式）
        # 支持: [A](happy,1,0): 文本 和 [A]: 文本
        if re.match(r'^\[([AB])\](\([^)]+\))?\s*[:：]\s*(.*)$', line):
            fixed_lines.append(line)
            print(f"  ✅ 格式正确，无需修复")
            continue
        
        # 尝试修复格式问题
        # 1. 检查是否缺少冒号
        match = re.match(r'^\[([AB])\]\s*(.*)$', line)
        if match:
            role = match.group(1)
            text = match.group(2).strip()
            if text:
                fixed_line = f"[{role}]: {text}"
                fixed_lines.append(fixed_line)
                print(f"  🛠️  修复缺少冒号: {fixed_line}")
                continue
        
        # 2. 检查是否缺少括号
        match = re.match(r'^([AB])\s*[:：]\s*(.*)$', line)
        if match:
            role = match.group(1)
            text = match.group(2).strip()
            if text:
                fixed_line = f"[{role}]: {text}"
                fixed_lines.append(fixed_line)
                print(f"  🛠️  修复缺少括号: {fixed_line}")
                continue
        
        # 3. 检查是否有其他格式问题，尝试提取角色和文本
        # 简单的启发式方法：查找第一个A或B，假设后面是文本
        match = re.search(r'[AB]', line)
        if match:
            role = match.group(0)
            text = line[match.end():].strip()
            # 移除文本中的特殊标记
            text = re.sub(r'[\[\](){}]', '', text)
            if text:
                fixed_line = f"[{role}]: {text}"
                fixed_lines.append(fixed_line)
                print(f"  🛠️  修复其他格式问题: {fixed_line}")
                continue
        
        # 如果无法修复，保留原行
        fixed_lines.append(line)
        print(f"  ❌ 无法修复，保留原行")
    
    result = '\n'.join(fixed_lines)
    print(f"修复完成，共处理 {len(lines)} 行")
    return result

def clean_script(script):
    """
    清理文稿，移除多余的空格、特殊字符等
    
    参数:
    - script: 播客文稿文本
    
    返回:
    - 清理后的文稿文本
    """
    # 移除多余的空行
    script = re.sub(r'\n\s*\n', '\n\n', script)
    # 移除行首行尾的空格
    lines = script.split('\n')
    cleaned_lines = [line.strip() for line in lines]
    # 移除多余的空格
    cleaned_lines = [re.sub(r'\s+', ' ', line) for line in cleaned_lines]
    # 过滤掉纯空格的行
    cleaned_lines = [line for line in cleaned_lines if line != '']
    
    return '\n'.join(cleaned_lines)

def generate_audio_segments(dialogue, voice_config, minimax_client, output_dir=SYSTEM_CONFIG["output_dir"]):
    """
    逐句合成音频片段，支持逐句情绪参数
    
    参数:
    - dialogue: 对话列表，由 parse_dialogue 返回，每个元素为 (角色, 文本, 情绪, 语速, 语调) 元组
    - voice_config: 角色到声音配置的映射，包含voice_id
    - minimax_client: MiniMaxClient 实例
    - output_dir: 输出目录
    
    返回:
    - 生成的音频文件路径列表
    """
    audio_files = []
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    print(f"使用输出目录: {output_dir}")
    
    for i, dialogue_item in enumerate(dialogue):
        print(f"\n处理第 {i+1} 句对话")
        
        # 解析对话项，支持不同长度的元组（兼容旧格式）
        if len(dialogue_item) == 2:
            # 旧格式：(角色, 文本)
            role, text = dialogue_item
            emotion = ""
            speed = 1.0
            pitch = 0
            print(f"  对话格式: 旧格式 (角色, 文本)")
        elif len(dialogue_item) == 5:
            # 新格式：(角色, 文本, 情绪, 语速, 语调)
            role, text, emotion, speed, pitch = dialogue_item
            print(f"  对话格式: 新格式 (角色, 文本, 情绪, 语速, 语调)")
        else:
            print(f"  错误: 无效的对话项格式，长度为 {len(dialogue_item)}")
            continue
        
        if not text:
            print(f"  警告: 第 {i+1} 句文本为空，跳过处理")
            continue
        
        # 获取当前角色的基础配置
        if role not in voice_config:
            print(f"  错误: 未找到角色 {role} 的声音配置，使用默认配置")
            config = {}
        else:
            config = voice_config[role]
        
        voice_id = config.get('voice_id', 'male-qn-qingse')
        print(f"  角色: {role}, 文本: {text[:50]}...")
        
        # 使用逐句的情绪参数，若为空则使用角色默认配置
        final_emotion = emotion or config.get('emotion', '')
        final_speed = speed or config.get('speed', 1.0)
        final_pitch = pitch or config.get('pitch', 0)
        
        # 验证参数范围
        if not (0.5 <= final_speed <= 2.0):
            print(f"  警告: 语速 {final_speed} 超出有效范围 [0.5, 2.0]，将使用默认值 1.0")
            final_speed = 1.0
        
        if not (-12 <= final_pitch <= 12):
            print(f"  警告: 语调 {final_pitch} 超出有效范围 [-12, 12]，将使用默认值 0")
            final_pitch = 0
        
        print(f"  使用配置: 声音ID={voice_id}, 情绪={final_emotion}, 语速={final_speed}, 语调={final_pitch}")
        
        # 调用 MiniMax API 合成音频
        try:
            result = minimax_client.synthesize_speech(
                text=text,
                voice_id=voice_id,
                emotion=final_emotion,  # 传递情绪参数
                speed=final_speed,
                pitch=final_pitch
            )
            
            if "error" in result:
                print(f"  错误: 合成音频失败 - {result['error']}")
                continue
            
            # 检查 API 响应状态
            base_resp = result.get("base_resp", {})
            status_code = base_resp.get("status_code")
            if status_code is None:
                print(f"  错误: API 响应缺少状态码")
                continue
            
            if status_code != 0:
                print(f"  错误: API 返回错误，状态码: {status_code}, 消息: {base_resp.get('status_msg', '未知错误')}")
                continue
            
            # 获取音频数据
            data = result.get("data", {})
            hex_audio = data.get("audio", "")
            if not hex_audio:
                print(f"  错误: API 未返回音频数据")
                continue
            
            print(f"  成功获取音频数据，长度: {len(hex_audio)} 字符")
            
            # 保存音频文件
            output_path = os.path.join(output_dir, f"segment_{i:03d}_{role}.mp3")
            if minimax_client.hex_to_audio_file(hex_audio, output_path):
                audio_files.append(output_path)
                print(f"  成功生成音频片段: {output_path}")
            else:
                print(f"  错误: 保存音频文件失败")
        except Exception as e:
            print(f"  错误: 合成音频时发生异常 - {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n音频片段生成完成，成功生成 {len(audio_files)} 个片段，共 {len(dialogue)} 句对话")
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
    print(f"\n=== 开始合并音频文件 ===")
    print(f"要合并的音频文件数量: {len(audio_files)}")
    print(f"输出路径: {output_path}")
    
    # 验证输入
    if not audio_files:
        print("错误: 没有要合并的音频文件")
        return False
    
    # 检查输出目录是否存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"已创建输出目录: {output_dir}")
        except Exception as e:
            print(f"错误: 创建输出目录失败 - {str(e)}")
            return False
    
    # 检查所有音频文件是否存在
    missing_files = []
    for file in audio_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"错误: 以下音频文件不存在:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    # 检查文件大小
    for file in audio_files:
        if os.path.getsize(file) == 0:
            print(f"警告: 音频文件 {file} 大小为 0 字节")
    
    try:
        # 创建空的音频片段
        combined = AudioSegment.empty()
        print(f"开始拼接音频片段...")
        
        # 逐个添加音频文件
        for i, file in enumerate(audio_files, 1):
            print(f"  处理第 {i}/{len(audio_files)} 个文件: {file}")
            audio = AudioSegment.from_mp3(file)
            print(f"    文件时长: {len(audio)/1000:.2f} 秒")
            combined += audio
        
        print(f"拼接完成，总时长: {len(combined)/1000:.2f} 秒")
        
        # 导出合并后的音频
        print(f"正在导出合并后的音频...")
        combined.export(output_path, format="mp3")
        
        # 验证输出文件
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ 成功合并音频文件: {output_path}")
            print(f"   文件大小: {os.path.getsize(output_path)/1024:.2f} KB")
            return True
        else:
            print(f"❌ 合并失败: 输出文件不存在或大小为 0")
            return False
    except Exception as e:
        print(f"❌ 合并音频文件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 检查是否缺少 ffmpeg
        if "Couldn't find ffmpeg or avconv" in str(e) or "ffmpeg" in str(e).lower():
            print(f"\n💡 提示: 缺少必要的音频处理工具 ffmpeg 或 avconv")
            print(f"   解决方法: 安装 ffmpeg 并确保其在系统 PATH 中")
            print(f"   Windows 下载: https://ffmpeg.org/download.html")
            print(f"   安装后将 ffmpeg.exe 所在目录添加到系统环境变量 PATH")
        
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
    验证文稿格式，支持逐句情绪参数
    
    参数:
    - script: 播客文稿文本
    
    返回:
    - 包含验证结果的字典
    """
    print(f"开始验证文稿，长度: {len(script)} 字符")
    
    # 尝试直接解析文稿，检查格式
    lines = script.split('\n')
    valid_lines = 0
    invalid_lines = []
    role_counts = {"A": 0, "B": 0}
    # 扩展有效的情绪列表，包括更多常用情绪
    valid_emotions = ["", "happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent", "whisper", "excited", "curious", "neutral", "joyful", "annoyed", "amazed", "confused"]
    
    for line_number, line in enumerate(lines, 1):
        original_line = line.strip()
        line = original_line.strip()
        if not line:
            continue
        
        # 跳过注释行
        if line.startswith('#'):
            print(f"  验证第 {line_number} 行: {original_line} - 跳过注释行")
            continue
        
        print(f"  验证第 {line_number} 行: {original_line[:50]}...")
        
        # 匹配带情绪参数的格式：[A](happy,1.2,0): 文本内容
        match = re.match(r'^\[([AB])\]\(([^,]+),([^,]+),([^)]+)\)\s*[:：]\s*(.*)$', line)
        if match:
            role = match.group(1)
            emotion = match.group(2).strip()
            speed_str = match.group(3).strip()
            pitch_str = match.group(4).strip()
            text = match.group(5).strip()
            
            # 验证文本是否为空
            if not text:
                invalid_lines.append(f"第 {line_number} 行: 文本内容为空")
                continue
            
            # 验证情绪参数
            if emotion not in valid_emotions:
                invalid_lines.append(f"第 {line_number} 行: 情绪参数无效: {emotion}")
                continue
            
            # 验证语速参数
            try:
                speed = float(speed_str)
                if speed < 0.5 or speed > 2.0:
                    invalid_lines.append(f"第 {line_number} 行: 语速参数无效: {speed}，范围应在 0.5-2.0 之间")
                    continue
            except ValueError:
                invalid_lines.append(f"第 {line_number} 行: 语速参数格式无效: {speed_str}，应为数字")
                continue
            
            # 验证语调参数
            try:
                pitch = int(pitch_str)
                if pitch < -12 or pitch > 12:
                    invalid_lines.append(f"第 {line_number} 行: 语调参数无效: {pitch}，范围应在 -12-12 之间")
                    continue
            except ValueError:
                invalid_lines.append(f"第 {line_number} 行: 语调参数格式无效: {pitch_str}，应为整数")
                continue
            
            role_counts[role] += 1
            valid_lines += 1
            print(f"  验证通过: 第 {line_number} 行，角色 {role}")
        else:
            # 匹配不带情绪参数的格式：[A]: 文本内容
            match = re.match(r'^\[([AB])\]\s*[:：]\s*(.*)$', line)
            if match:
                role = match.group(1)
                text = match.group(2).strip()
                
                # 验证文本是否为空
                if not text:
                    invalid_lines.append(f"第 {line_number} 行: 文本内容为空")
                    continue
                
                role_counts[role] += 1
                valid_lines += 1
                print(f"  验证通过: 第 {line_number} 行，角色 {role}")
            else:
                # 无法识别的格式
                invalid_lines.append(f"第 {line_number} 行: 格式无效，应为 [A]: 文本 或 [A](情绪,语速,语调): 文本")
    
    # 检查是否有有效行
    if valid_lines == 0:
        if invalid_lines:
            return {
                "valid": False,
                "message": f"文稿中未找到有效的对话内容，以下是具体错误:\n" + "\n".join(invalid_lines)
            }
        else:
            return {
                "valid": False,
                "message": "文稿中未找到有效的对话内容，请使用 [A] 和 [B] 标记角色"
            }
    
    # 检查角色分布
    if role_counts["A"] == 0 or role_counts["B"] == 0:
        missing_roles = []
        if role_counts["A"] == 0:
            missing_roles.append("A")
        if role_counts["B"] == 0:
            missing_roles.append("B")
        return {
            "valid": False,
            "message": f"文稿中缺少角色 {', '.join(missing_roles)} 的对话，当前分布: 角色 A: {role_counts['A']} 句，角色 B: {role_counts['B']} 句"
        }
    
    # 检查是否有无效行
    if invalid_lines:
        return {
            "valid": False,
            "message": f"文稿中存在 {len(invalid_lines)} 处格式错误，以下是具体错误:\n" + "\n".join(invalid_lines)
        }
    
    # 验证通过
    result = {
        "valid": True,
        "message": f"文稿验证通过，包含 {valid_lines} 句对话，角色 A: {role_counts['A']} 句，角色 B: {role_counts['B']} 句",
        "dialogue_count": valid_lines,
        "role_counts": role_counts
    }
    print(f"文稿验证通过: {result['message']}")
    return result
