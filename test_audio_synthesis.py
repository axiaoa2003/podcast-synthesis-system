import os
import sys
import uuid
from podcast_utils import parse_dialogue
from minimax_client import MiniMaxClient
from config import SYSTEM_CONFIG, MINIMAX_CONFIG

# 创建 MiniMax 客户端实例
minimax_client = MiniMaxClient()

# 示例文稿内容
script = '''[A]：你好，欢迎收听今天的播客节目。
[B]：大家好，很高兴能来到这里。
[A]：今天我们要讨论的话题是人工智能。
[B]：是的，人工智能是一个非常热门的话题。
'''

# 解析对话
dialogue = parse_dialogue(script)
print(f"解析到 {len(dialogue)} 句对话")
for i, (role, text) in enumerate(dialogue):
    print(f"[{i+1}] [{role}]：{text}")

# 创建声音映射
voice_map = {
    'A': MINIMAX_CONFIG['default_voices']['A'],
    'B': MINIMAX_CONFIG['default_voices']['B']
}
print(f"使用的声音映射: {voice_map}")

# 生成唯一标识符
session_id = str(uuid.uuid4())
output_dir = os.path.join(SYSTEM_CONFIG['output_dir'], session_id)

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

print("开始生成音频片段...")
# 逐句生成音频，查看每一句的生成情况
for i, (role, text) in enumerate(dialogue):
    print(f"\n生成第 {i+1} 句，角色 {role}...")
    print(f"文本：{text}")
    
    # 调用 MiniMax API 合成音频
    result = minimax_client.synthesize_speech(
        text=text,
        voice_id=voice_map[role]
    )
    
    print(f"API 返回结果: {result}")
    
    if "error" in result:
        print(f"❌ 合成失败: {result['error']}")
        continue
    
    # 检查 API 响应状态
    base_resp = result.get("base_resp", {})
    if base_resp.get("status_code") != 0:
        print(f"❌ 合成失败: {base_resp.get('status_msg', '未知错误')}")
        continue
    
    # 获取音频数据
    data = result.get("data", {})
    hex_audio = data.get("audio", "")
    if not hex_audio:
        print(f"❌ 合成失败: 未返回音频数据")
        continue
    
    # 保存音频文件
    output_path = os.path.join(output_dir, f"segment_{i:03d}_{role}.mp3")
    if minimax_client.hex_to_audio_file(hex_audio, output_path):
        print(f"✅ 合成成功: {output_path}")
    else:
        print(f"❌ 保存失败: {output_path}")

print("\n测试完成!")
