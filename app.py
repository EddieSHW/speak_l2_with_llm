import gradio as gr
import requests
import json
import os
import tempfile
import time
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Ollama API設定
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3")

# チャット履歴
chat_history = []

# 音声認識関数
def transcribe_audio(audio_file):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ja-JP")
            return text
    except Exception as e:
        return f"音声認識エラー: {str(e)}"

# テキスト読み上げ関数
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='ja', slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.close()
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"音声合成エラー: {str(e)}")
        return None

# Ollama APIでチャット応答を取得
def get_ollama_response(message, history, temperature=0.7, max_tokens=2048):
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
        "model": MODEL_NAME,
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

# テキスト入力によるチャット処理
def chat(message, history, temperature, max_tokens):
    # Ollamaからの応答を取得
    response = get_ollama_response(message, history, temperature, max_tokens)
    
    # 音声ファイルの生成
    audio_file = text_to_speech(response)
    
    # 履歴を更新して返す
    history.append((message, response))
    return history, history, audio_file

# 音声入力によるチャット処理
def voice_chat(audio_file, history, temperature, max_tokens):
    if audio_file is None:
        return history, history, None
    
    # 音声をテキストに変換
    text = transcribe_audio(audio_file)
    
    # テキストから応答を生成
    response = get_ollama_response(text, history, temperature, max_tokens)
    
    # 応答を音声に変換
    audio_response = text_to_speech(response)
    
    # 履歴を更新
    history.append((text, response))
    return history, history, audio_response

# 利用可能なモデルを取得
def get_available_models():
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        return []
    except:
        return []

# Gradioインターフェースの構築
def build_interface():
    with gr.Blocks(title="Gemma3 日本語音声チャット") as demo:
        gr.Markdown("# 🤖 Gemma3 日本語音声チャットボット")
        gr.Markdown("Ollamaを使用してLLMと日本語で会話できます。音声入力と音声出力に対応しています。")

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="会話", height=500)
                
                with gr.Row():
                    text_input = gr.Textbox(label="テキストでメッセージを入力", placeholder="ここにメッセージを入力...", lines=2)
                
                with gr.Row():
                    audio_input = gr.Audio(source="microphone", type="filepath", label="音声でメッセージを入力")
                
                with gr.Row():
                    audio_output = gr.Audio(label="AIの応答（音声）", autoplay=True)
                
                with gr.Row():
                    clear_btn = gr.Button("会話をクリア")
                
            with gr.Column(scale=1):
                available_models = get_available_models()
                default_model = MODEL_NAME if MODEL_NAME in available_models else (available_models[0] if available_models else MODEL_NAME)
                
                model_dropdown = gr.Dropdown(
                    choices=available_models if available_models else [MODEL_NAME],
                    value=default_model,
                    label="モデル選択"
                )
                
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=0.7,
                    step=0.1,
                    label="Temperature"
                )
                
                max_tokens = gr.Slider(
                    minimum=16,
                    maximum=4096,
                    value=2048,
                    step=16,
                    label="最大トークン数"
                )
                
                gr.Markdown("### モデル情報")
                if available_models:
                    gr.Markdown("インストール済みモデル:")
                    for model in available_models:
                        gr.Markdown(f"- `{model}`")
                else:
                    gr.Markdown("**警告**: Ollamaサーバーに接続できないか、モデルが見つかりません。")
                    gr.Markdown("Ollamaが実行中であることを確認してください。")
        
        # イベントハンドラの設定
        text_input.submit(chat, [text_input, chatbot, temperature, max_tokens], [chatbot, chatbot, audio_output]).then(
            lambda: "", None, [text_input]
        )
        
        audio_input.change(voice_chat, [audio_input, chatbot, temperature, max_tokens], [chatbot, chatbot, audio_output])
        
        clear_btn.click(lambda: [], None, [chatbot])
        
        # モデル変更時の処理
        def update_model(model_name):
            global MODEL_NAME
            MODEL_NAME = model_name
            return MODEL_NAME
        
        model_dropdown.change(update_model, [model_dropdown], None)
        
        # フッター
        gr.Markdown("---")
        gr.Markdown("*このアプリケーションはローカルのOllamaを使用してLLMと会話します。データはあなたのコンピュータから外部に送信されません。*")
    
    return demo

# メイン実行
if __name__ == "__main__":
    demo = build_interface()
    demo.launch(share=False) 