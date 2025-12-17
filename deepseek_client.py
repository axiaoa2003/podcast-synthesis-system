from openai import OpenAI
from config import DEEPSEEK_CONFIG

class DeepSeekClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_CONFIG["api_key"],
            base_url=DEEPSEEK_CONFIG["base_url"]
        )
        self.model = DEEPSEEK_CONFIG["model"]
    
    def generate_inspiration(self, topic, count=5, discussion_points=3):
        """
        基于主题生成播客灵感和讨论点
        
        参数:
        - topic: 播客主题
        - count: 生成的灵感数量
        - discussion_points: 每个灵感包含的讨论点数量
        
        返回:
        - 生成的灵感和讨论点
        """
        prompt = f"请为主题'{topic}'生成{count}个播客灵感，每个灵感包含{discussion_points}个讨论点。"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的播客策划师，擅长基于主题生成有趣的播客灵感和讨论点。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"生成灵感失败: {str(e)}"
    
    def generate_script(self, inspiration, length=2000, role_a="主持人", role_b="嘉宾"):
        """
        基于灵感生成结构化双人对话文稿
        
        参数:
        - inspiration: 播客灵感和讨论点
        - length: 期望的文稿长度（字符数）
        - role_a: 角色A的名称
        - role_b: 角色B的名称
        
        返回:
        - 结构化的双人对话文稿，使用[A]和[B]标记不同角色
        """
        prompt = f"基于以下灵感生成一段约{length}字的双人对话播客文稿：\n\n{inspiration}\n\n要求：\n1. 使用[A]和[B]标记不同角色的对话\n2. 对话自然流畅，符合播客风格\n3. 包含适当的开场白和结束语\n4. 结构清晰，有明确的主题推进"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是一位专业的编剧，擅长编写自然流畅的双人对话。请生成结构化的双人对话，使用[A]代表{role_a}，[B]代表{role_b}。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"生成文稿失败: {str(e)}"
    
    def optimize_script(self, script):
        """
        优化播客文稿结构和对话流畅度
        
        参数:
        - script: 原始文稿
        
        返回:
        - 优化后的文稿
        """
        prompt = f"请优化以下播客文稿，提升对话流畅度和结构合理性：\n\n{script}\n\n要求：\n1. 保持原有的角色标记([A]和[B])\n2. 优化对话的自然度和连贯性\n3. 调整节奏，使对话更适合播客收听\n4. 保留核心内容，不改变主题"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的播客编辑，擅长优化播客文稿的结构和对话流畅度。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"优化文稿失败: {str(e)}"
