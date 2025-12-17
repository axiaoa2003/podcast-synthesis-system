from podcast_utils import parse_dialogue

# 模拟用户在网页中输入的内容
user_input = '''[A]：太棒了。这完全是把视角从病理学转向了特质光谱。那么，这些特质——比如强大的发散思维、创造力——在工作和创造场景中，AI如何帮助它们更好地发挥，而不是被压抑？这就到了我们最后的主题：创造力与职业适配。
[B]：没错。首先，对于**创造力**，ADHD的发散思维是宝藏，但如何收拢成一个可执行的方案，往往是难点。AI工具在这里是绝佳的“思维协作者”。比如，你用**思维导图**软件，天马行空地输入一堆关键词。AI可以帮你自动分类、建立你没想到的联系、甚至建议一个逻辑结构。或者，你用**创意生成器**，输入一个模糊的概念，AI可以生成多个方向的原型、文案或视觉风格，供你选择和深化。它就像一个永不疲倦的“外接大脑”，负责处理结构化和延伸性的工作，让你可以更自由地停留在创意迸发的“发散阶段”，同时确保最终能落地。'''

# 测试解析对话
print("=== 测试网页输入解析 ===")
dialogue = parse_dialogue(user_input)
print(f"解析到 {len(dialogue)} 句对话")
for i, (role, text) in enumerate(dialogue):
    print(f"[{i+1}] 角色{role}: {text[:50]}...")  # 只显示前50个字符

# 检查角色分布
role_counts = {'A': 0, 'B': 0}
for role, _ in dialogue:
    role_counts[role] += 1

print(f"角色A数量: {role_counts['A']}")
print(f"角色B数量: {role_counts['B']}")
