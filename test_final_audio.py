from podcast_utils import parse_dialogue, generate_audio_segments, merge_audio_files
from minimax_client import MiniMaxClient
from config import SYSTEM_CONFIG, MINIMAX_CONFIG
import os

# 用户实际输入的完整内容
user_input = '''[A]：太棒了。这完全是把视角从病理学转向了特质光谱。那么，这些特质——比如强大的发散思维、创造力——在工作和创造场景中，AI如何帮助它们更好地发挥，而不是被压抑？这就到了我们最后的主题：创造力与职业适配。
[B]：没错。首先，对于**创造力**，ADHD的发散思维是宝藏，但如何收拢成一个可执行的方案，往往是难点。AI工具在这里是绝佳的“思维协作者”。比如，你用**思维导图**软件，天马行空地输入一堆关键词。AI可以帮你自动分类、建立你没想到的联系、甚至建议一个逻辑结构。或者，你用**创意生成器**，输入一个模糊的概念，AI可以生成多个方向的原型、文案或视觉风格，供你选择和深化。它就像一个永不疲倦的“外接大脑”，负责处理结构化和延伸性的工作，让你可以更自由地停留在创意迸发的“发散阶段”，同时确保最终能落地。'''

# 创建测试输出目录
test_output_dir = os.path.join(SYSTEM_CONFIG['output_dir'], 'test_final')
os.makedirs(test_output_dir, exist_ok=True)

# 初始化 MiniMax 客户端
minimax_client = MiniMaxClient()

print("=== 测试最终音频生成流程 ===")

# 1. 解析对话
print("\n1. 解析对话：")
dialogue = parse_dialogue(user_input)
print(f"解析到 {len(dialogue)} 句对话")
for i, (role, text) in enumerate(dialogue):
    print(f"[{i+1}] 角色{role}: {text[:50]}...")

# 2. 使用默认的声音配置生成音频片段
print("\n2. 使用默认声音配置生成音频片段：")
voice_map = {
    'A': MINIMAX_CONFIG['default_voices']['A'],
    'B': MINIMAX_CONFIG['default_voices']['B']
}

# 调用生成音频片段函数
audio_files = generate_audio_segments(
    dialogue=dialogue,
    voice_map=voice_map,
    minimax_client=minimax_client,
    output_dir=test_output_dir
)

print(f"成功生成 {len(audio_files)} 个音频片段")
for i, file in enumerate(audio_files):
    print(f"[{i+1}] 音频片段: {file}")

# 检查每个角色的音频片段数量
role_files = {'A': 0, 'B': 0}
for file in audio_files:
    if '_A.' in file:
        role_files['A'] += 1
    elif '_B.' in file:
        role_files['B'] += 1

print(f"角色A音频片段数量: {role_files['A']}")
print(f"角色B音频片段数量: {role_files['B']}")

# 3. 合并音频文件
if audio_files:
    print("\n3. 合并音频文件：")
    final_output = os.path.join(test_output_dir, 'final_podcast_default.mp3')
    success = merge_audio_files(audio_files, final_output)
    if success:
        print(f"成功合并音频文件: {final_output}")
        print(f"合并的音频文件数量: {len(audio_files)}")

# 4. 使用自定义的声音配置生成音频片段
print("\n4. 使用自定义声音配置生成音频片段：")
custom_voice_map = {
    'A': {"id": "male-qn-qingse", "name": "青年男声 - 明亮", "pitch": 3},
    'B': {"id": "male-qn-qingse", "name": "青年女声 - 甜美", "pitch": 10}
}

# 调用生成音频片段函数
custom_audio_files = generate_audio_segments(
    dialogue=dialogue,
    voice_map=custom_voice_map,
    minimax_client=minimax_client,
    output_dir=test_output_dir
)

print(f"成功生成 {len(custom_audio_files)} 个音频片段")
for i, file in enumerate(custom_audio_files):
    print(f"[{i+1}] 音频片段: {file}")

# 5. 合并自定义配置的音频文件
if custom_audio_files:
    print("\n5. 合并自定义配置的音频文件：")
    custom_final_output = os.path.join(test_output_dir, 'final_podcast_custom.mp3')
    success = merge_audio_files(custom_audio_files, custom_final_output)
    if success:
        print(f"成功合并音频文件: {custom_final_output}")
        print(f"合并的音频文件数量: {len(custom_audio_files)}")

print("\n=== 测试完成 ===")
