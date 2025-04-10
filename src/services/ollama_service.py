import requests
import json
import re
from src.config.settings import OLLAMA_API_URL, MODEL_NAME, JAPANESE_TEACHER_SYSTEM_PROMPT, ENGLISH_TEACHER_SYSTEM_PROMPT

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
    def remove_markdown(text):
        """テキストからMarkdown形式と<think>タグ内の内容を除去する"""
        if not text:
            return text
            
        # <think>タグ内の内容を除去
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # *による強調表示を除去
        text = re.sub(r'\*{1,3}([^*]+?)\*{1,3}', r'\1', text)
        
        # _による強調表示を除去
        text = re.sub(r'_{1,3}([^_]+?)_{1,3}', r'\1', text)
        
        # `によるコード表示を除去
        text = re.sub(r'`{1,3}([^`]+?)`{1,3}', r'\1', text)
        
        # #による見出しを通常テキストに変換
        text = re.sub(r'^#{1,6}\s+(.+?)$', r'\1', text, flags=re.MULTILINE)
        
        # >による引用を通常テキストに変換
        text = re.sub(r'^>\s+(.+?)$', r'\1', text, flags=re.MULTILINE)
        
        # - や * による箇条書きを通常テキストに変換
        text = re.sub(r'^[\*\-\+]\s+(.+?)$', r'・\1', text, flags=re.MULTILINE)
        
        # 1. などの番号付きリストを通常テキストに変換
        text = re.sub(r'^\d+\.\s+(.+?)$', r'\1', text, flags=re.MULTILINE)
        
        # [text](url)形式のリンクをテキストのみに変換
        text = re.sub(r'\[([^\]]+?)\]\([^\)]+?\)', r'\1', text)
        
        return text
    
    @staticmethod
    def get_chat_response(message, history, model=MODEL_NAME, temperature=0.7, max_tokens=2048, is_teacher_mode=True, language="ja"):
        """チャットの応答を取得する"""
        # チャット履歴を整形
        messages = []
        
        # システムプロンプトを追加（教師モードの場合）
        if is_teacher_mode:
            system_prompt = JAPANESE_TEACHER_SYSTEM_PROMPT if language == "ja" else ENGLISH_TEACHER_SYSTEM_PROMPT
            system_prompt += "\n\n重要: 絶対に '*', '_', '`', '#', '>' のようなMarkdown記法や絵文字は使わないでください。通常のプレーンテキストで返答してください。"
            messages.append({"role": "system", "content": system_prompt})
        
        # 過去の会話履歴を追加
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
            content = response_data["message"]["content"]
            
            # Markdown形式を除去
            content = OllamaService.remove_markdown(content)
            
            return content
        except Exception as e:
            return f"APIエラー: {str(e)}" 