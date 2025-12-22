#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文稿处理功能

测试内容：
1. 文稿解析功能
2. 文稿验证功能
3. 音频生成功能（可选）
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from podcast_utils import parse_dialogue, validate_script


def test_parse_dialogue():
    """
    测试文稿解析功能
    """
    print("=== 测试文稿解析功能 ===")
    
    # 测试用例1：带情绪参数的文稿
    test_script_1 = """
    [A](happy,1.2,0): 你好，今天天气真好啊！
    [B](sad,0.8,2): 是啊，但是我有点不开心。
    [A](surprised,1.5,-1): 为什么呢？发生什么事了吗？
    [B](calm,1.0,0): 没什么，就是有点累了。
    """
    
    print("测试用例1：带情绪参数的文稿")
    result_1 = parse_dialogue(test_script_1)
    print(f"解析结果：{result_1}")
    print(f"解析对话数量：{len(result_1)}")
    
    # 测试用例2：不带情绪参数的文稿
    test_script_2 = """
    [A]: 你好，今天天气真好啊！
    [B]: 是啊，但是我有点不开心。
    [A]: 为什么呢？发生什么事了吗？
    [B]: 没什么，就是有点累了。
    """
    
    print("\n测试用例2：不带情绪参数的文稿")
    result_2 = parse_dialogue(test_script_2)
    print(f"解析结果：{result_2}")
    print(f"解析对话数量：{len(result_2)}")
    
    # 测试用例3：混合格式的文稿
    test_script_3 = """
    [A](happy,1.2,0): 你好，今天天气真好啊！
    [B]: 是啊，但是我有点不开心。
    [A](surprised,1.5,-1): 为什么呢？发生什么事了吗？
    [B]: 没什么，就是有点累了。
    """
    
    print("\n测试用例3：混合格式的文稿")
    result_3 = parse_dialogue(test_script_3)
    print(f"解析结果：{result_3}")
    print(f"解析对话数量：{len(result_3)}")
    
    # 测试用例4：JSON格式的文稿
    test_script_4 = '''
    {
        "dialogues": [
            {
                "role": "A",
                "text": "你好，今天天气真好啊！",
                "emotion": "happy",
                "speed": 1.2,
                "pitch": 0
            },
            {
                "role": "B",
                "text": "是啊，但是我有点不开心。",
                "emotion": "sad",
                "speed": 0.8,
                "pitch": 2
            }
        ]
    }
    '''
    
    print("\n测试用例4：JSON格式的文稿")
    result_4 = parse_dialogue(test_script_4)
    print(f"解析结果：{result_4}")
    print(f"解析对话数量：{len(result_4)}")
    
    print("\n=== 文稿解析功能测试完成 ===")
    print()


def test_validate_script():
    """
    测试文稿验证功能
    """
    print("=== 测试文稿验证功能 ===")
    
    # 测试用例1：有效的带情绪参数的文稿
    test_script_1 = """
    [A](happy,1.2,0): 你好，今天天气真好啊！
    [B](sad,0.8,2): 是啊，但是我有点不开心。
    """
    
    print("测试用例1：有效的带情绪参数的文稿")
    result_1 = validate_script(test_script_1)
    print(f"验证结果：{result_1}")
    
    # 测试用例2：有效的不带情绪参数的文稿
    test_script_2 = """
    [A]: 你好，今天天气真好啊！
    [B]: 是啊，但是我有点不开心。
    """
    
    print("\n测试用例2：有效的不带情绪参数的文稿")
    result_2 = validate_script(test_script_2)
    print(f"验证结果：{result_2}")
    
    # 测试用例3：无效的文稿格式
    test_script_3 = """
    A: 你好，今天天气真好啊！
    B: 是啊，但是我有点不开心。
    """
    
    print("\n测试用例3：无效的文稿格式（缺少括号）")
    result_3 = validate_script(test_script_3)
    print(f"验证结果：{result_3}")
    
    # 测试用例4：无效的情绪参数
    test_script_4 = """
    [A](invalid_emotion,1.2,0): 你好，今天天气真好啊！
    [B](sad,0.8,2): 是啊，但是我有点不开心。
    """
    
    print("\n测试用例4：无效的情绪参数")
    result_4 = validate_script(test_script_4)
    print(f"验证结果：{result_4}")
    
    # 测试用例5：无效的语速参数
    test_script_5 = """
    [A](happy,3.0,0): 你好，今天天气真好啊！
    [B](sad,0.8,2): 是啊，但是我有点不开心。
    """
    
    print("\n测试用例5：无效的语速参数（超出范围）")
    result_5 = validate_script(test_script_5)
    print(f"验证结果：{result_5}")
    
    # 测试用例6：无效的语调参数
    test_script_6 = """
    [A](happy,1.2,15): 你好，今天天气真好啊！
    [B](sad,0.8,2): 是啊，但是我有点不开心。
    """
    
    print("\n测试用例6：无效的语调参数（超出范围）")
    result_6 = validate_script(test_script_6)
    print(f"验证结果：{result_6}")
    
    # 测试用例7：缺少角色B的文稿
    test_script_7 = """
    [A](happy,1.2,0): 你好，今天天气真好啊！
    [A](sad,0.8,2): 是啊，但是我有点不开心。
    """
    
    print("\n测试用例7：缺少角色B的文稿")
    result_7 = validate_script(test_script_7)
    print(f"验证结果：{result_7}")
    
    print("\n=== 文稿验证功能测试完成 ===")
    print()


def main():
    """
    主函数
    """
    print("=== 开始测试文稿处理功能 ===")
    print()
    
    # 测试文稿解析功能
    test_parse_dialogue()
    
    # 测试文稿验证功能
    test_validate_script()
    
    print("=== 所有测试完成 ===")


if __name__ == "__main__":
    main()
