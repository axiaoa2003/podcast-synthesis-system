import requests
import json
from config import MINIMAX_CONFIG

class MiniMaxClient:
    def __init__(self):
        self.api_key = MINIMAX_CONFIG["api_key"]
        self.base_url = MINIMAX_CONFIG["base_url"]
        self.model = MINIMAX_CONFIG["model"]
        self.default_voices = MINIMAX_CONFIG["default_voices"]
    
    def synthesize_speech(self, text, voice_id, speed=1.0, volume=1.0, pitch=0, format="mp3"):
        """
        调用 MiniMax 语音合成 API 生成音频
        
        参数:
        - text: 待合成的文本
        - voice_id: 声音 ID
        - speed: 语速，范围 [0.5, 2.0]，默认 1.0
        - volume: 音量，范围 (0, 10]，默认 1.0
        - pitch: 语调，范围 [-12, 12]，默认 0
        - format: 音频格式，可选 "mp3", "pcm", "flac", "wav"，默认 "mp3"
        
        返回:
        - 包含音频数据的字典，或错误信息
        """
        url = f"{self.base_url}/v1/t2a_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": speed,
                "vol": volume,
                "pitch": pitch
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": format,
                "channel": 1
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API 请求失败: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON 解析失败: {str(e)}"}
    
    def hex_to_audio_file(self, hex_data, output_path):
        """
        将 hex 编码的音频数据转换为音频文件
        
        参数:
        - hex_data: hex 编码的音频数据
        - output_path: 输出文件路径
        
        返回:
        - True 表示成功，False 表示失败
        """
        try:
            audio_bytes = bytes.fromhex(hex_data)
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            return True
        except Exception as e:
            print(f"保存音频文件失败: {str(e)}")
            return False
    
    def get_voice_list(self):
        """
        获取可用的声音列表
        
        返回:
        - 可用的声音列表
        """
        # 调用 MiniMax API 获取可用的声音列表
        url = f"{self.base_url}/v1/get_voice"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "voice_type": "system"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # 处理 API 返回的格式
            voice_list = []
            if "system_voice" in data:
                for voice in data["system_voice"]:
                    voice_list.append({
                        "id": voice["voice_id"],
                        "name": voice["voice_name"]
                    })
            
            # 如果 API 返回了可用的声音列表，返回它
            if voice_list:
                return voice_list
            else:
                # 如果 API 返回格式不符合预期，返回配置文件中定义的声音列表
                from config import AVAILABLE_VOICES
                return AVAILABLE_VOICES
        except Exception as e:
            print(f"获取声音列表失败: {str(e)}")
            # 发生错误时，返回配置文件中定义的声音列表
            from config import AVAILABLE_VOICES
            return AVAILABLE_VOICES
