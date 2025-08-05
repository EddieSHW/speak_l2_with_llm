import requests
import json
import re
import logging
import time
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.config.settings import (
    OLLAMA_API_URL, MODEL_NAME, JAPANESE_TEACHER_SYSTEM_PROMPT, 
    ENGLISH_TEACHER_SYSTEM_PROMPT, API_TIMEOUT, MAX_RETRIES
)

class OllamaAPIError(Exception):
    """Ollama API関連のエラー"""
    pass

class OllamaConnectionError(OllamaAPIError):
    """Ollama接続エラー"""
    pass

class OllamaTimeoutError(OllamaAPIError):
    """Ollamaタイムアウトエラー"""
    pass

class OllamaService:
    """Ollama APIと通信するためのサービスクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = API_TIMEOUT
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
    )
    def get_available_models(self) -> List[str]:
        """利用可能なモデルの一覧を取得する"""
        try:
            self.logger.debug(f"モデル一覧を取得中: {OLLAMA_API_URL}/api/tags")
            response = self.session.get(f"{OLLAMA_API_URL}/api/tags", timeout=API_TIMEOUT)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                self.logger.info(f"利用可能なモデル数: {len(model_names)}")
                return model_names
            else:
                self.logger.warning(f"モデル一覧の取得に失敗: HTTP {response.status_code}")
                return []
                
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Ollamaサーバーへの接続に失敗: {str(e)}")
            raise OllamaConnectionError(f"Ollamaサーバーに接続できません: {str(e)}")
        except requests.exceptions.Timeout as e:
            self.logger.error(f"モデル一覧取得がタイムアウト: {str(e)}")
            raise OllamaTimeoutError(f"リクエストがタイムアウトしました: {str(e)}")
        except Exception as e:
            self.logger.error(f"予期しないエラーが発生: {str(e)}")
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
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout))
    )
    def get_chat_response(
        self, 
        message: str, 
        history: List[tuple], 
        model: str = MODEL_NAME, 
        temperature: float = 0.7, 
        max_tokens: int = 2048, 
        is_teacher_mode: bool = True, 
        language: str = "ja"
    ) -> str:
        """チャットの応答を取得する"""
        start_time = time.time()
        
        try:
            # チャット履歴を整形
            messages = []
            
            # システムプロンプトを追加（教師モードの場合）
            if is_teacher_mode:
                system_prompt = (JAPANESE_TEACHER_SYSTEM_PROMPT if language == "ja" 
                               else ENGLISH_TEACHER_SYSTEM_PROMPT)
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
            
            self.logger.debug(f"チャット応答を要求中 - モデル: {model}, メッセージ長: {len(message)}")
            
            response = self.session.post(
                f"{OLLAMA_API_URL}/api/chat", 
                json=data, 
                timeout=API_TIMEOUT
            )
            
            response_time = time.time() - start_time
            self.logger.info(f"応答時間: {response_time:.2f}秒")
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data["message"]["content"]
                
                # Markdown形式を除去
                content = self.remove_markdown(content)
                
                self.logger.debug(f"応答長: {len(content)} 文字")
                return content
                
            elif response.status_code == 404:
                error_msg = f"モデル '{model}' が見つかりません。利用可能なモデルを確認してください。"
                self.logger.error(error_msg)
                return error_msg
                
            elif response.status_code == 500:
                error_msg = "Ollamaサーバーで内部エラーが発生しました。モデルが正しく読み込まれているか確認してください。"
                self.logger.error(f"サーバーエラー: {response.text}")
                return error_msg
                
            else:
                error_msg = f"APIエラー (HTTP {response.status_code}): {response.text}"
                self.logger.error(error_msg)
                return error_msg
                
        except requests.exceptions.ConnectionError as e:
            error_msg = "Ollamaサーバーに接続できません。サーバーが起動しているか確認してください。"
            self.logger.error(f"接続エラー: {str(e)}")
            return error_msg
            
        except requests.exceptions.Timeout as e:
            error_msg = f"リクエストがタイムアウトしました（{API_TIMEOUT}秒）。モデルが大きすぎるか、サーバーが過負荷の可能性があります。"
            self.logger.error(f"タイムアウトエラー: {str(e)}")
            return error_msg
            
        except json.JSONDecodeError as e:
            error_msg = "サーバーからの応答を解析できませんでした。"
            self.logger.error(f"JSON解析エラー: {str(e)}")
            return error_msg
            
        except Exception as e:
            error_msg = f"予期しないエラーが発生しました: {str(e)}"
            self.logger.error(error_msg)
            return error_msg 