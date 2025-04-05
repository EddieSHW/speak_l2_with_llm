import gradio as gr
from src.config.settings import MODEL_NAME, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
from src.services.ollama_service import OllamaService
from src.utils.audio_utils import AudioUtils

class ChatInterface:
    """チャットインターフェースを構築するクラス"""
    
    def __init__(self):
        self.ollama_service = OllamaService()
        self.audio_utils = AudioUtils()
        
    def chat(self, message, history, temperature, max_tokens, model):
        """テキスト入力によるチャット処理"""
        # Ollamaからの応答を取得
        response = self.ollama_service.get_chat_response(
            message, history, model, temperature, max_tokens
        )
        
        # 音声ファイルの生成
        audio_file = self.audio_utils.text_to_speech(response)
        
        # 履歴を更新して返す
        history.append((message, response))
        return history, history, audio_file
    
    def voice_chat(self, audio_file, history, temperature, max_tokens, model):
        """音声入力によるチャット処理"""
        if audio_file is None:
            return history, history, None
        
        # 音声をテキストに変換
        text = self.audio_utils.transcribe_audio(audio_file)
        
        # テキストから応答を生成
        response = self.ollama_service.get_chat_response(
            text, history, model, temperature, max_tokens
        )
        
        # 応答を音声に変換
        audio_response = self.audio_utils.text_to_speech(response)
        
        # 履歴を更新
        history.append((text, response))
        return history, history, audio_response
    
    def build_interface(self):
        """Gradioインターフェースの構築"""
        with gr.Blocks(title="Gemma3 日本語音声チャット") as demo:
            gr.Markdown("# 🤖 Gemma3 日本語音声チャットボット")
            gr.Markdown("Ollamaを使用してLLMと日本語で会話できます。音声入力と音声出力に対応しています。")

            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(label="会話", height=500)
                    
                    with gr.Row():
                        text_input = gr.Textbox(label="テキストでメッセージを入力", placeholder="ここにメッセージを入力...", lines=2)
                    
                    with gr.Row():
                        audio_input = gr.Audio(
                            label="音声でメッセージを入力", 
                            type="filepath", 
                            source="microphone",
                            format="wav"
                        )
                    
                    with gr.Row():
                        audio_output = gr.Audio(label="AIの応答（音声）", autoplay=True)
                    
                    with gr.Row():
                        clear_btn = gr.Button("会話をクリア")
                    
                with gr.Column(scale=1):
                    available_models = self.ollama_service.get_available_models()
                    default_model = MODEL_NAME if MODEL_NAME in available_models else (available_models[0] if available_models else MODEL_NAME)
                    
                    model_dropdown = gr.Dropdown(
                        choices=available_models if available_models else [MODEL_NAME],
                        value=default_model,
                        label="モデル選択"
                    )
                    
                    temperature = gr.Slider(
                        minimum=0.0,
                        maximum=2.0,
                        value=DEFAULT_TEMPERATURE,
                        step=0.1,
                        label="Temperature"
                    )
                    
                    max_tokens = gr.Slider(
                        minimum=16,
                        maximum=4096,
                        value=DEFAULT_MAX_TOKENS,
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
            text_input.submit(
                self.chat, 
                [text_input, chatbot, temperature, max_tokens, model_dropdown], 
                [chatbot, chatbot, audio_output]
            ).then(lambda: "", None, [text_input])
            
            audio_input.change(
                self.voice_chat, 
                [audio_input, chatbot, temperature, max_tokens, model_dropdown], 
                [chatbot, chatbot, audio_output]
            )
            
            clear_btn.click(lambda: [], None, [chatbot])
            
            # フッター
            gr.Markdown("---")
            gr.Markdown("*このアプリケーションはローカルのOllamaを使用してLLMと会話します。データはあなたのコンピュータから外部に送信されません。*")
        
        return demo 