# ====================== 用户配置区域 ======================
# 只需要在这里填入你的API密钥
DEEPSEEK_API_KEY = ""    # 填入你的DeepSeek API密钥
MINIMAX_API_KEY = ""     # 填入你的MiniMax API密钥
# ========================================================

# DeepSeek API 配置
DEEPSEEK_CONFIG = {
    "api_key": DEEPSEEK_API_KEY,
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat"
}

# MiniMax API 配置
MINIMAX_CONFIG = {
    "api_key": MINIMAX_API_KEY,
    "base_url": "https://api.minimaxi.com",
    "model": "speech-2.6-hd",
    "default_voices": {
        "A": "male-qn-qingse",  # 角色A默认使用男声
        "B": "female-shaonv"    # 角色B默认使用女声
    }
}

# 系统配置
SYSTEM_CONFIG = {
    "output_dir": "static/audio",
    "max_script_length": 10000,
    "default_script_length": 2000
}

# 可用声音列表将通过API动态获取，不再硬编码
AVAILABLE_VOICES = []