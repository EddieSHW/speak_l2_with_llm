import tempfile
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import wave
import os

class AudioUtils:
    """音声処理のためのユーティリティクラス"""
    
    @staticmethod
    def transcribe_audio(audio_file):
        """音声ファイルをテキストに変換する"""
        try:
            # 適切な形式に変換
            converted_file = AudioUtils._convert_audio_format(audio_file)
            file_to_use = converted_file if converted_file else audio_file
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(file_to_use) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language="ja-JP")
                
            # 一時ファイルを削除
            if converted_file and os.path.exists(converted_file):
                os.remove(converted_file)
                
            return text
        except Exception as e:
            return f"音声認識エラー: {str(e)}"
    
    @staticmethod
    def text_to_speech(text):
        """テキストを音声ファイルに変換する"""
        try:
            tts = gTTS(text=text, lang='ja', slow=False)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.close()
            tts.save(temp_file.name)
            return temp_file.name
        except Exception as e:
            print(f"音声合成エラー: {str(e)}")
            return None
    
    @staticmethod
    def _convert_audio_format(audio_file, target_format="wav"):
        """音声ファイルを適切な形式に変換する"""
        try:
            # ファイル形式を確認
            if not audio_file or not os.path.exists(audio_file):
                return None
                
            # 一時ファイルのパスを生成
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
            temp_file.close()
            
            # AudioSegmentを使用して変換
            audio = AudioSegment.from_file(audio_file)
            
            # WAVに変換して保存（16bitに設定）
            audio = audio.set_sample_width(2)  # 16-bit
            audio.export(temp_file.name, format=target_format)
            
            return temp_file.name
        except Exception as e:
            print(f"音声形式変換エラー: {str(e)}")
            return None 