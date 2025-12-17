from minimax_client import MiniMaxClient

# 初始化 MiniMax 客户端
minimax_client = MiniMaxClient()

# 测试有效的声音ID
valid_voice_id = 'male-qn-qingse'
# 测试无效的声音ID（故意使用错误的ID）
invalid_voice_id = 'invalid-voice-id'

# 测试文本
text = '这是一个测试文本。'

print("=== 测试声音ID有效性 ===")

# 测试有效声音ID
print(f"\n测试有效声音ID '{valid_voice_id}':")
result = minimax_client.synthesize_speech(
    text=text,
    voice_id=valid_voice_id
)

if "error" in result:
    print(f"  错误: {result['error']}")
else:
    base_resp = result.get("base_resp", {})
    if base_resp.get("status_code") == 0:
        print("  成功: 声音ID有效")
    else:
        print(f"  失败: {base_resp.get('status_msg', '未知错误')}")

# 测试无效声音ID
print(f"\n测试无效声音ID '{invalid_voice_id}':")
result = minimax_client.synthesize_speech(
    text=text,
    voice_id=invalid_voice_id
)

if "error" in result:
    print(f"  错误: {result['error']}")
else:
    base_resp = result.get("base_resp", {})
    if base_resp.get("status_code") == 0:
        print("  成功: 声音ID有效")
    else:
        print(f"  失败: {base_resp.get('status_msg', '未知错误')}")
