import gradio as gr
from src.config.settings import MODEL_NAME, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
from src.services.ollama_service import OllamaService
from src.utils.audio_utils import AudioUtils

class ChatInterface:
    """チャットインターフェースを構築するクラス"""
    
    def __init__(self):
        self.ollama_service = OllamaService()
        self.audio_utils = AudioUtils()
        self.teacher_mode = True  # デフォルトで教師モードをオン
        
    def chat(self, message, history, temperature, max_tokens, model, teacher_mode, language, speech_speed):
        """テキスト入力によるチャット処理"""
        # 言語選択の値を言語コードに変換
        lang_code = "ja" if language == "日本語" else "en"
        
        # Ollamaからの応答を取得
        response = self.ollama_service.get_chat_response(
            message, history, model, temperature, max_tokens, is_teacher_mode=teacher_mode, language=lang_code
        )
        
        # 音声ファイルの生成
        audio_file = self.audio_utils.text_to_speech(response, language=lang_code, speed=speech_speed)
        
        # 履歴を更新して返す
        history.append((message, response))
        return history, history, audio_file
    
    def voice_chat(self, audio_file, history, temperature, max_tokens, model, teacher_mode, language, speech_speed):
        """音声入力によるチャット処理"""
        if audio_file is None:
            return history, history, None
        
        # 言語選択の値を言語コードに変換
        lang_code = "ja" if language == "日本語" else "en"
        
        # 音声をテキストに変換
        text = self.audio_utils.transcribe_audio(audio_file, language=lang_code)
        
        # テキストから応答を生成
        response = self.ollama_service.get_chat_response(
            text, history, model, temperature, max_tokens, is_teacher_mode=teacher_mode, language=lang_code
        )
        
        # 応答を音声に変換
        audio_response = self.audio_utils.text_to_speech(response, language=lang_code, speed=speech_speed)
        
        # 履歴を更新
        history.append((text, response))
        return history, history, audio_response
    
    def build_interface(self):
        """Gradioインターフェースの構築"""
        with gr.Blocks(title="Speak L2 with LLM") as ui:
            gr.Markdown("# Speak L2 with LLM")
            gr.Markdown("言語練習のためのAIアシスタントです。文法や表現の間違いを指摘し、自然な会話練習をサポートします。")

            with gr.Row():
                with gr.Column(scale=3):
                    # プレーンテキストモードでチャットボットを表示
                    chatbot = gr.Chatbot(label="会話", height=500, render_markdown=False)
                    
                    with gr.Row():
                        text_input = gr.Textbox(label="メッセージを入力", placeholder="ここにメッセージを入力...", lines=2, scale=4)
                        submit_btn = gr.Button("送信", scale=1)
                    
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
                    language_dropdown = gr.Dropdown(
                        choices=["日本語", "English"],
                        value="日本語",
                        label="言語選択"
                    )
                    
                    teacher_mode_checkbox = gr.Checkbox(
                        label="教師モード", 
                        value=True,
                        info="オンにすると、文法や表現の間違いを指摘します。オフにすると通常の会話モードになります。"
                    )
                    
                    try:
                        available_models = self.ollama_service.get_available_models()
                        default_model = MODEL_NAME if MODEL_NAME in available_models else (available_models[0] if available_models else MODEL_NAME)
                    except Exception as e:
                        available_models = [MODEL_NAME]
                        default_model = MODEL_NAME
                    
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
                    
                    speech_speed = gr.Slider(
                        minimum=0.5,
                        maximum=2.0,
                        value=1.25,
                        step=0.05,
                        label="音声スピード"
                    )
            
            # イベントハンドラの設定
            text_input.submit(
                self.chat, 
                [text_input, chatbot, temperature, max_tokens, model_dropdown, teacher_mode_checkbox, language_dropdown, speech_speed], 
                [chatbot, chatbot, audio_output]
            ).then(lambda: "", None, [text_input])
            
            submit_btn.click(
                self.chat, 
                [text_input, chatbot, temperature, max_tokens, model_dropdown, teacher_mode_checkbox, language_dropdown, speech_speed], 
                [chatbot, chatbot, audio_output]
            ).then(lambda: "", None, [text_input])
            
            audio_input.change(
                self.voice_chat, 
                [audio_input, chatbot, temperature, max_tokens, model_dropdown, teacher_mode_checkbox, language_dropdown, speech_speed], 
                [chatbot, chatbot, audio_output]
            )
            
            clear_btn.click(lambda: [], None, [chatbot])
            
            # フッター
            gr.Markdown("---")
            gr.Markdown("このアプリケーションは言語学習者向けに設計されています。ローカルのOllamaを使用しているため、データはあなたのコンピュータから外部に送信されません。")
        
        return ui