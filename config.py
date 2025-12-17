# 配置文件

# DeepSeek API 配置
DEEPSEEK_CONFIG = {
    "api_key": "sk-1f275c7f79764dc4bdb5de6910b41961",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat"
}

# MiniMax API 配置
MINIMAX_CONFIG = {
    "api_key": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLlva3mtanlnaQiLCJVc2VyTmFtZSI6IuW9rea1qeWdpCIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTgzNDAzNzgwMDExNDY3MjAwIiwiUGhvbmUiOiIxNTMzNzI1Mzc5OCIsIkdyb3VwSUQiOiIxOTgzNDAzNzgwMDA3MjcyODk2IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMTItMTcgMTM6MTM6NDIiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.evh7xMf_R-JH6D3IvMlBD3Xvv8dRqwtFo7s1xN0Ec-SgdhEFC7EHiW1lMlfpQZ6nfOa_HZdkTaKTRRSw_nxXgZm71QCKTLMUtls76iXVmipVO7KFu6rvDxlP0qNkY9f4yRYFCYtbmJCT3C58Mli_XHZiUlWIH0kGKGuT5BWFuK5cWFhIqluVZbPxmT4Drw7UQ4AXSEjtq2VsDsZVglQJSzqfHD7DINQdDyxIQ39RCB9VCp4Nnhr5TXON9eHm5N9GjCR-lUN5xq_5T5ebYlcI51Tstvtxa_4L3tUAmMsoLW7d280peazHjSaH8lfngr7s-KYi7OzOdqdxqpVPhDcFjA",
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

# 可用声音列表（从MiniMax API获取的实际可用音色）
AVAILABLE_VOICES = [
    # 中文男声系列
    {"id": "male-qn-qingse", "name": "青年男声 - 青涩"},
    {"id": "male-qn-jingying", "name": "青年男声 - 精英"},
    {"id": "male-qn-badao", "name": "青年男声 - 霸道"},
    {"id": "male-qn-daxuesheng", "name": "青年男声 - 大学生"},
    {"id": "Chinese (Mandarin)_Reliable_Executive", "name": "中年男声 - 沉稳高管"},
    {"id": "Chinese (Mandarin)_Unrestrained_Young_Man", "name": "青年男声 - 不羁"},
    {"id": "Chinese (Mandarin)_Gentleman", "name": "青年男声 - 温润"},
    {"id": "Chinese (Mandarin)_Male_Announcer", "name": "中年男声 - 播报"},
    {"id": "Chinese (Mandarin)_Southern_Young_Man", "name": "青年男声 - 南方小哥"},
    {"id": "Chinese (Mandarin)_Gentle_Youth", "name": "青年男声 - 温柔"},
    # 中文女声系列
    {"id": "female-shaonv", "name": "少女音色"},
    {"id": "female-yujie", "name": "御姐音色"},
    {"id": "female-chengshu", "name": "成熟女性音色"},
    {"id": "female-tianmei", "name": "甜美女性音色"},
    {"id": "Chinese (Mandarin)_News_Anchor", "name": "新闻女声"},
    {"id": "Chinese (Mandarin)_Mature_Woman", "name": "傲娇御姐"},
    {"id": "Chinese (Mandarin)_Warm_Bestie", "name": "温暖闺蜜"},
    {"id": "Chinese (Mandarin)_Sweet_Lady", "name": "甜美女声"},
    {"id": "Chinese (Mandarin)_Wise_Women", "name": "阅历姐姐"},
    {"id": "Chinese (Mandarin)_Warm_Girl", "name": "温暖少女"},
    {"id": "Chinese (Mandarin)_Crisp_Girl", "name": "清脆少女"},
    {"id": "Chinese (Mandarin)_Soft_Girl", "name": "软软女孩"}
]
