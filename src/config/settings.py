import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Ollama API設定
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3")

# モデル設定のデフォルト値
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "2048")) 