from minimax_client import MiniMaxClient

# 初始化 MiniMax 客户端
minimax_client = MiniMaxClient()

# 测试文本
text = '这是一个测试文本。'

# 测试多个声音ID
voice_ids_to_test = [
    'male-qn-qingse',    # 青年男声 - 青色（已验证有效）
    'female-qn-qianxi',   # 青年女声 - 纤喜
    'male-yq-chenxu',     # 年轻男声 - 晨旭
    'female-yq-xiyao',    # 年轻女声 - 熙瑶
    'male-zh-zhongshi',   # 中年男声 - 忠实
    'female-zh-huihua',   # 中年女声 - 惠华
    'male-qn-heiyan',     # 青年男声 - 黑岩
    'female-qn-lingxi',   # 青年女声 - 灵犀
    'male-yq-mingyu',     # 年轻男声 - 明宇
    'female-yq-ruxi',     # 年轻女声 - 如溪
    'male-zh-chengbao',   # 中年男声 - 晨宝
    'female-zh-wanrong'   # 中年女声 - 婉蓉
]

print("=== 测试多个声音ID有效性 ===")

valid_voices = []
invalid_voices = []

for voice_id in voice_ids_to_test:
    print(f"\n测试声音ID '{voice_id}':")
    result = minimax_client.synthesize_speech(
        text=text,
        voice_id=voice_id
    )

    if "error" in result:
        print(f"  错误: {result['error']}")
        invalid_voices.append(voice_id)
    else:
        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code") == 0:
            print("  成功: 声音ID有效")
            valid_voices.append(voice_id)
        else:
            print(f"  失败: {base_resp.get('status_msg', '未知错误')}")
            invalid_voices.append(voice_id)

print(f"\n=== 测试结果总结 ===")
print(f"有效声音ID数量: {len(valid_voices)}")
print(f"无效声音ID数量: {len(invalid_voices)}")
print(f"\n有效声音ID列表: {valid_voices}")
print(f"无效声音ID列表: {invalid_voices}")
