import requests
import json
from config import MINIMAX_CONFIG

class MiniMaxClient:
    def __init__(self, api_key=None):
        # 如果没有传入api_key，使用配置文件中的默认值
        self.api_key = api_key or MINIMAX_CONFIG["api_key"]
        self.base_url = MINIMAX_CONFIG["base_url"]
        self.model = MINIMAX_CONFIG["model"]
        self.default_voices = MINIMAX_CONFIG["default_voices"]
    
    def synthesize_speech(self, text, voice_id, speed=1.0, volume=1.0, pitch=0, emotion="", format="mp3"):
        """
        调用 MiniMax 语音合成 API 生成音频
        
        参数:
        - text: 待合成的文本
        - voice_id: 声音 ID
        - speed: 语速，范围 [0.5, 2.0]，默认 1.0
        - volume: 音量，范围 (0, 10]，默认 1.0
        - pitch: 语调，范围 [-12, 12]，默认 0
        - emotion: 情绪，可选 "happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent", "whisper"，默认 ""（自动）
        - format: 音频格式，可选 "mp3", "pcm", "flac", "wav"，默认 "mp3"
        
        返回:
        - 包含音频数据的字典，或错误信息
        """
        # 验证参数范围
        if not (0.5 <= speed <= 2.0):
            print(f"  警告: 语速 {speed} 超出有效范围 [0.5, 2.0]，将使用默认值 1.0")
            speed = 1.0
        
        if not (0 < volume <= 10):
            print(f"  警告: 音量 {volume} 超出有效范围 (0, 10]，将使用默认值 1.0")
            volume = 1.0
        
        if not (-12 <= pitch <= 12):
            print(f"  警告: 语调 {pitch} 超出有效范围 [-12, 12]，将使用默认值 0")
            pitch = 0
        
        # 验证情绪参数
        valid_emotions = ["", "happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent", "whisper"]
        if emotion not in valid_emotions:
            print(f"  警告: 情绪 {emotion} 无效，将使用自动情绪")
            emotion = ""
        
        # 验证音频格式
        valid_formats = ["mp3", "pcm", "flac", "wav"]
        if format not in valid_formats:
            print(f"  警告: 音频格式 {format} 无效，将使用默认格式 mp3")
            format = "mp3"
        
        url = f"{self.base_url}/v1/t2a_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        voice_setting = {
            "voice_id": voice_id,
            "speed": speed,
            "vol": volume,
            "pitch": pitch
        }
        
        # 只有当emotion不为空时才添加到voice_setting中
        if emotion:
            voice_setting["emotion"] = emotion
        
        payload = {
            "model": self.model,
            "text": text,
            "stream": False,
            "voice_setting": voice_setting,
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": format,
                "channel": 1
            }
        }
        
        print(f"  准备调用 MiniMax API: {url}")
        print(f"  请求参数: model={self.model}, voice_id={voice_id}, speed={speed}, volume={volume}, pitch={pitch}, emotion={emotion}, format={format}")
        print(f"  文本长度: {len(text)} 字符")
        
        try:
            # 发送请求
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            print(f"  API 响应状态码: {response.status_code}")
            
            # 检查响应状态码
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            print(f"  API 响应成功，包含 base_resp: {response_data.get('base_resp', {})}")
            
            return response_data
        except requests.exceptions.Timeout:
            error_msg = "API 请求超时"
            print(f"  错误: {error_msg}")
            return {"error": error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "API 连接失败"
            print(f"  错误: {error_msg}")
            return {"error": error_msg}
        except requests.exceptions.HTTPError as e:
            error_msg = f"API HTTP 错误: {str(e)}"
            print(f"  错误: {error_msg}")
            try:
                # 尝试解析错误响应
                error_response = response.json()
                if "base_resp" in error_response:
                    error_msg = f"API 错误: {error_response['base_resp'].get('status_msg', error_msg)}"
                    print(f"  详细错误: {error_msg}")
            except json.JSONDecodeError:
                pass
            return {"error": error_msg}
        except json.JSONDecodeError as e:
            error_msg = f"API 响应解析失败: {str(e)}"
            print(f"  错误: {error_msg}")
            print(f"  原始响应: {response.text[:200]}...")
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"API 请求异常: {str(e)}"
            print(f"  错误: {error_msg}")
            import traceback
            traceback.print_exc()
            return {"error": error_msg}
    
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
            "voice_type": "all"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # 处理 API 返回的格式
            voice_list = []
            
            # 处理系统音色
            if "system_voice" in data:
                for voice in data["system_voice"]:
                    voice_list.append({
                        "id": voice["voice_id"],
                        "name": voice["voice_name"]
                    })
            
            # 处理克隆音色
            if "voice_cloning" in data:
                for voice in data["voice_cloning"]:
                    voice_list.append({
                        "id": voice["voice_id"],
                        "name": voice["voice_name"] or voice["voice_id"]  # 如果voice_name为空，使用voice_id作为名称
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
