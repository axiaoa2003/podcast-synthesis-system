from minimax_client import MiniMaxClient

# 初始化 MiniMax 客户端
minimax_client = MiniMaxClient()

# 测试文本
text = '这是一个测试文本。'

# 尝试一些可能有效的女声ID
female_voice_ids = [
    'female-qn-qingse',    # 青年女声 - 青色
    'female-qn-wanxia',     # 青年女声 - 婉夏
    'female-yq-ruxi',       # 年轻女声 - 如溪
    'female-zh-lingzhi',    # 中年女声 - 灵智
    'female-xiaoqing',      # 小青女声
    'female-huahua',        # 花花女声
    'female-lingling',      # 玲玲女声
    'female-xiuxiu',        # 秀秀女声
    'female-qianqian',      # 倩倩女声
    'female-yingying'       # 盈盈女声
]

print("=== 测试女声ID有效性 ===")

valid_voices = []
invalid_voices = []

for voice_id in female_voice_ids:
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
