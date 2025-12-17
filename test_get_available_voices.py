from minimax_client import MiniMaxClient

# 初始化 MiniMax 客户端
minimax_client = MiniMaxClient()

print("=== 获取可用的系统音色列表 ===")

# 调用 get_voice_list 方法获取系统音色列表
voices = minimax_client.get_voice_list()

print(f"获取到 {len(voices)} 个可用音色")
print("\n可用音色列表:")
for i, voice in enumerate(voices):
    if isinstance(voice, dict):
        voice_id = voice.get('id', '未知ID')
        voice_name = voice.get('name', '未知名称')
        print(f"[{i+1}] ID: {voice_id}, 名称: {voice_name}")
    else:
        print(f"[{i+1}] 无效音色数据: {voice}")

# 测试第一个音色是否可用
if voices and isinstance(voices[0], dict):
    first_voice_id = voices[0].get('id')
    if first_voice_id:
        print(f"\n=== 测试第一个音色ID '{first_voice_id}' 是否可用 ===")
        result = minimax_client.synthesize_speech(
            text='这是一个测试文本。',
            voice_id=first_voice_id
        )
        
        if "error" in result:
            print(f"  错误: {result['error']}")
        else:
            base_resp = result.get("base_resp", {})
            if base_resp.get("status_code") == 0:
                print("  成功: 音色ID有效")
            else:
                print(f"  失败: {base_resp.get('status_msg', '未知错误')}")
