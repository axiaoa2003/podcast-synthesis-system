#!/usr/bin/env python3
"""
测试 MiniMaxClient 的 get_voice_list() 方法是否能返回克隆音色
"""

from minimax_client import MiniMaxClient

def test_get_voice_list():
    # 初始化客户端
    minimax_client = MiniMaxClient()
    
    print("正在调用 get_voice_list() 方法...")
    
    try:
        # 调用获取声音列表的方法
        voices = minimax_client.get_voice_list()
        
        print(f"\n成功获取到 {len(voices)} 个音色：")
        
        # 遍历并打印所有音色
        for i, voice in enumerate(voices):
            print(f"{i+1}. ID: {voice['id']}, Name: {voice['name']}")
        
        # 检查是否包含克隆音色
        cloned_voices = [voice for voice in voices if 'voiceluoba' in voice['id']]
        if cloned_voices:
            print(f"\n✓ 成功找到克隆音色：")
            for voice in cloned_voices:
                print(f"  - ID: {voice['id']}, Name: {voice['name']}")
        else:
            print(f"\n✗ 未找到包含 'voiceluoba' 的克隆音色")
        
        return voices
        
    except Exception as e:
        print(f"调用失败：{str(e)}")
        return []

if __name__ == "__main__":
    test_get_voice_list()
