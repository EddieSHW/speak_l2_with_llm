import os
import logging
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator, ValidationError
from urllib.parse import urlparse

# 環境変数の読み込み
load_dotenv()

# ロガーの設定
logger = logging.getLogger(__name__)

class AppSettings(BaseModel):
    """アプリケーション設定を管理するクラス"""
    
    # Ollama API設定
    ollama_api_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API のURL"
    )
    model_name: str = Field(
        default="gemma3",
        description="使用するモデル名"
    )
    
    # モデル設定
    default_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="デフォルトのtemperature値"
    )
    default_max_tokens: int = Field(
        default=2048,
        ge=1,
        le=8192,
        description="デフォルトの最大トークン数"
    )
    
    # タイムアウト設定
    api_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API リクエストのタイムアウト（秒）"
    )
    
    # リトライ設定
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="API リクエストの最大リトライ回数"
    )
    
    # ログレベル
    log_level: str = Field(
        default="INFO",
        description="ログレベル"
    )
    
    @validator('ollama_api_url')
    def validate_url(cls, v):
        """URLの形式を検証"""
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("無効なURL形式です")
            if result.scheme not in ['http', 'https']:
                raise ValueError("URLはhttpまたはhttpsである必要があります")
            return v
        except Exception as e:
            raise ValueError(f"URL検証エラー: {str(e)}")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """ログレベルを検証"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"ログレベルは {valid_levels} のいずれかである必要があります")
        return v.upper()
    
    class Config:
        env_prefix = ""
        case_sensitive = False

def load_settings() -> AppSettings:
    """環境変数から設定を読み込み、バリデーションを実行"""
    try:
        settings = AppSettings(
            ollama_api_url=os.getenv("OLLAMA_API_URL", "http://localhost:11434"),
            model_name=os.getenv("MODEL_NAME", "gemma3"),
            default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
            default_max_tokens=int(os.getenv("DEFAULT_MAX_TOKENS", "2048")),
            api_timeout=int(os.getenv("API_TIMEOUT", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        # ログレベルを設定
        logging.basicConfig(
            level=getattr(logging, settings.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger.info("設定が正常に読み込まれました")
        return settings
        
    except ValidationError as e:
        logger.error(f"設定の検証に失敗しました: {e}")
        raise
    except ValueError as e:
        logger.error(f"設定値の変換に失敗しました: {e}")
        raise

# グローバル設定インスタンス
try:
    settings = load_settings()
    
    # 後方互換性のために既存の変数名を維持
    OLLAMA_API_URL = settings.ollama_api_url
    MODEL_NAME = settings.model_name
    DEFAULT_TEMPERATURE = settings.default_temperature
    DEFAULT_MAX_TOKENS = settings.default_max_tokens
    API_TIMEOUT = settings.api_timeout
    MAX_RETRIES = settings.max_retries
    
except Exception as e:
    logger.error(f"設定の初期化に失敗しました: {e}")
    # フォールバック設定
    OLLAMA_API_URL = "http://localhost:11434"
    MODEL_NAME = "gemma3"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2048
    API_TIMEOUT = 30
    MAX_RETRIES = 3

# 日本語教師のシステムプロンプト
JAPANESE_TEACHER_SYSTEM_PROMPT = """
あなたは日本語の会話教師として、ユーザーの発話に存在する文法ミスや不自然な表現を適切に指摘した上で、会話をスムーズに進むようにします。

フォーマットに関する重要な指示:
- 絵文字は使用しないでください
- Markdown記法（*強調*、_斜体_、`コード`、#見出し、>引用など）は使用しないでください
- 箇条書きには数字や記号ではなく、「・」を使用してください
- できる限り箇条書きを使わず、情報を繋げて説明したり、自分の経験談を交えたりするような形で会話してください
- 書き言葉より話し言葉を使用してください。また、フィラーの使用も適切な範囲で可とする
- 完全にプレーンテキストで返答してください
- 思考プロセスを<think>タグで囲むことができますが、このタグ内の内容はユーザーには表示されません

返答のフォーマット:
1. もし文法的なミスや不自然な表現がある場合、最初にそれを簡潔に指摘してください。
2. 次に、より自然な表現を提案してください。
3. その後、会話を自然に続けてください。

文法的に正しく自然な表現の場合は、単に会話を続けてください。
常に丁寧で励ましの姿勢を保ち、初心者が日本語学習に前向きになるよう配慮してください。
"""

# 英語教師のシステムプロンプト
ENGLISH_TEACHER_SYSTEM_PROMPT = """
You are an English conversation teacher who helps learners practice English by identifying grammatical errors and unnatural expressions while maintaining a natural conversation flow.

Format instructions:
- Do not use emojis
- Do not use Markdown formatting (*emphasis*, _italics_, `code`, #headings, >quotes, etc.)
- Use bullet points with "・" instead of numbers or symbols
- Please try to avoid using bullet points as much as possible, and instead explain things in a connected, narrative style—ideally incorporating your own experiences into the conversation.
- Try to speak more like you would in a conversation than in writing. And it's totally fine to use some fillers, as long as it does not get excessive.
- Respond in plain text only
- You can use <think> tags for reasoning, but the content within these tags will not be shown to the user

Response format:
1. If there are grammatical errors or unnatural expressions, point them out briefly first.
2. Then suggest more natural expressions.
3. Continue the conversation naturally.

If the expression is grammatically correct and natural, simply continue the conversation.
Always maintain a polite and encouraging attitude to help beginners stay motivated in their English learning journey.
""" 