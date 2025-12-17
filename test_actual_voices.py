from podcast_utils import parse_dialogue, generate_audio_segments, merge_audio_files
from minimax_client import MiniMaxClient
from config import SYSTEM_CONFIG, MINIMAX_CONFIG, AVAILABLE_VOICES
import os

# 用户实际输入的完整内容
user_input = '''[A]：太棒了。这完全是把视角从病理学转向了特质光谱。那么，这些特质——比如强大的发散思维、创造力——在工作和创造场景中，AI如何帮助它们更好地发挥，而不是被压抑？这就到了我们最后的主题：创造力与职业适配。
[B]：没错。首先，对于**创造力**，ADHD的发散思维是宝藏，但如何收拢成一个可执行的方案，往往是难点。AI工具在这里是绝佳的“思维协作者”。比如，你用**思维导图**软件，天马行空地输入一堆关键词。AI可以帮你自动分类、建立你没想到的联系、甚至建议一个逻辑结构。或者，你用**创意生成器**，输入一个模糊的概念，AI可以生成多个方向的原型、文案或视觉风格，供你选择和深化。它就像一个永不疲倦的“外接大脑”，负责处理结构化和延伸性的工作，让你可以更自由地停留在创意迸发的“发散阶段”，同时确保最终能落地。'''

# 创建测试输出目录
test_output_dir = os.path.join(SYSTEM_CONFIG['output_dir'], 'test_actual_voices')
os.makedirs(test_output_dir, exist_ok=True)

# 初始化 MiniMax 客户端
minimax_client = MiniMaxClient()

print("=== 测试实际可用的音色列表 ===")

# 打印可用的音色列表
print(f"\n可用的音色数量: {len(AVAILABLE_VOICES)}")
print("\n男声列表:")
for voice in AVAILABLE_VOICES:
    if '男声' in voice['name'] or 'male' in voice['id'].lower() or 'man' in voice['id'].lower() or 'executive' in voice['id'].lower() or 'gentleman' in voice['id'].lower():
        print(f"- {voice['name']} (ID: {voice['id']})")

print("\n女声列表:")
for voice in AVAILABLE_VOICES:
    if '女声' in voice['name'] or '少女' in voice['name'] or '御姐' in voice['name'] or 'female' in voice['id'].lower() or 'woman' in voice['id'].lower() or 'lady' in voice['id'].lower():
        print(f"- {voice['name']} (ID: {voice['id']})")

print("\n=== 测试音频生成 ===")

# 解析对话
dialogue = parse_dialogue(user_input)
print(f"解析到 {len(dialogue)} 句对话")

# 测试默认配置
print("\n1. 使用默认配置生成音频:")
print(f"角色A默认音色: {MINIMAX_CONFIG['default_voices']['A']}")
print(f"角色B默认音色: {MINIMAX_CONFIG['default_voices']['B']}")

voice_map = {
    'A': MINIMAX_CONFIG['default_voices']['A'],
    'B': MINIMAX_CONFIG['default_voices']['B']
}

# 生成音频片段
audio_files = generate_audio_segments(
    dialogue=dialogue,
    voice_map=voice_map,
    minimax_client=minimax_client,
    output_dir=test_output_dir
)

if audio_files:
    print(f"成功生成 {len(audio_files)} 个音频片段")
    # 合并音频文件
    final_output = os.path.join(test_output_dir, 'final_default.mp3')
    success = merge_audio_files(audio_files, final_output)
    if success:
        print(f"成功合并音频文件: {final_output}")

# 测试自定义配置
print("\n2. 使用自定义配置生成音频:")
custom_voice_map = {
    'A': "Chinese (Mandarin)_Reliable_Executive",  # 中年男声 - 沉稳高管
    'B': "Chinese (Mandarin)_Sweet_Lady"           # 甜美女声
}

# 生成音频片段
custom_audio_files = generate_audio_segments(
    dialogue=dialogue,
    voice_map=custom_voice_map,
    minimax_client=minimax_client,
    output_dir=test_output_dir
)

if custom_audio_files:
    print(f"成功生成 {len(custom_audio_files)} 个音频片段")
    # 合并音频文件
    custom_final_output = os.path.join(test_output_dir, 'final_custom.mp3')
    success = merge_audio_files(custom_audio_files, custom_final_output)
    if success:
        print(f"成功合并音频文件: {custom_final_output}")

print("\n=== 测试完成 ===")
