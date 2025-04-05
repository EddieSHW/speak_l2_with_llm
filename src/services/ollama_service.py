import requests
import json
from src.config.settings import OLLAMA_API_URL, MODEL_NAME

class OllamaService:
    """Ollama APIと通信するためのサービスクラス"""
    
    @staticmethod
    def get_available_models():
        """利用可能なモデルの一覧を取得する"""
        try:
            response = requests.get(f"{OLLAMA_API_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except Exception:
            return []
    
    @staticmethod
    def get_chat_response(message, history, model=MODEL_NAME, temperature=0.7, max_tokens=2048):
        """チャットの応答を取得する"""
        # チャット履歴を整形
        messages = []
        for human, ai in history:
            messages.append({"role": "user", "content": human})
            if ai:  # AIの応答がある場合
                messages.append({"role": "assistant", "content": ai})
        
        # 新しいメッセージを追加
        messages.append({"role": "user", "content": message})
        
        # APIリクエストを準備
        data = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(f"{OLLAMA_API_URL}/api/chat", json=data)
            if response.status_code != 200:
                return f"エラー: {response.status_code} - {response.text}"
            
            response_data = response.json()
            return response_data["message"]["content"]
        except Exception as e:
            return f"APIエラー: {str(e)}" 