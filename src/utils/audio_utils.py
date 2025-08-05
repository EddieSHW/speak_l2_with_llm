import tempfile
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import os
import logging
import atexit
from typing import Optional, List
from contextlib import contextmanager

class AudioProcessingError(Exception):
    """音声処理関連のエラー"""
    pass

class AudioRecognitionError(AudioProcessingError):
    """音声認識エラー"""
    pass

class AudioConversionError(AudioProcessingError):
    """音声変換エラー"""
    pass

class TempFileManager:
    """一時ファイル管理クラス"""
    
    def __init__(self):
        self.temp_files: List[str] = []
        self.logger = logging.getLogger(__name__)
        # プログラム終了時に残った一時ファイルをクリーンアップ
        atexit.register(self.cleanup_all)
    
    def register_temp_file(self, filepath: str) -> None:
        """一時ファイルを登録"""
        if filepath and filepath not in self.temp_files:
            self.temp_files.append(filepath)
            self.logger.debug(f"一時ファイル登録: {filepath}")
    
    def remove_temp_file(self, filepath: str) -> None:
        """指定した一時ファイルを削除"""
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
                self.logger.debug(f"一時ファイル削除: {filepath}")
            if filepath in self.temp_files:
                self.temp_files.remove(filepath)
        except OSError as e:
            self.logger.warning(f"一時ファイルの削除に失敗: {filepath} - {str(e)}")
    
    def cleanup_all(self) -> None:
        """すべての一時ファイルをクリーンアップ"""
        for filepath in self.temp_files[:]:  # コピーを作成してイテレート
            self.remove_temp_file(filepath)
    
    @contextmanager
    def temp_file(self, suffix: str = ".tmp"):
        """一時ファイルのコンテキストマネージャー"""
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.close()
            self.register_temp_file(temp_file.name)
            yield temp_file.name
        finally:
            if temp_file:
                self.remove_temp_file(temp_file.name)

class AudioUtils:
    """音声処理のためのユーティリティクラス"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_manager = TempFileManager()
    
    def transcribe_audio(self, audio_file: str, language: str = "ja") -> str:
        """音声ファイルをテキストに変換する"""
        if not audio_file or not os.path.exists(audio_file):
            raise AudioRecognitionError("音声ファイルが存在しません")
        
        converted_file = None
        try:
            # 適切な形式に変換
            self.logger.debug(f"音声認識開始: {audio_file}")
            converted_file = self._convert_audio_format(audio_file)
            file_to_use = converted_file if converted_file else audio_file
            
            recognizer = sr.Recognizer()
            # 認識精度を向上させるための調整
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.8
            
            with sr.AudioFile(file_to_use) as source:
                # 環境ノイズを調整
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
                
                # 言語コードを設定
                lang_code = "ja-JP" if language == "ja" else "en-US"
                
                try:
                    text = recognizer.recognize_google(audio_data, language=lang_code)
                    self.logger.info(f"音声認識成功: '{text[:50]}...' ({len(text)} 文字)")
                    return text
                    
                except sr.UnknownValueError:
                    error_msg = "音声を認識できませんでした。もう一度はっきりと話してください。"
                    self.logger.warning("音声認識: 音声が不明瞭")
                    return error_msg
                    
                except sr.RequestError as e:
                    if "quota exceeded" in str(e).lower():
                        error_msg = "Google音声認識のAPIクォータを超過しました。しばらく待ってから再試行してください。"
                    elif "network" in str(e).lower() or "connection" in str(e).lower():
                        error_msg = "ネットワーク接続に問題があります。インターネット接続を確認してください。"
                    else:
                        error_msg = f"音声認識サービスでエラーが発生しました: {str(e)}"
                    self.logger.error(f"音声認識APIエラー: {str(e)}")
                    return error_msg
                
        except Exception as e:
            error_msg = f"音声処理中にエラーが発生しました: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
            
        finally:
            # 一時ファイルをクリーンアップ
            if converted_file and os.path.exists(converted_file):
                try:
                    os.remove(converted_file)
                    self.logger.debug(f"音声変換ファイルを削除: {converted_file}")
                except OSError as e:
                    self.logger.warning(f"音声変換ファイルの削除に失敗: {converted_file} - {str(e)}")
    
    def text_to_speech(self, text: str, language: str = "ja", speed: float = 1.25) -> Optional[str]:
        """テキストを音声ファイルに変換する"""
        if not text or not text.strip():
            self.logger.warning("空のテキストが音声合成に渡されました")
            return None
        
        # テキストの長さ制限
        if len(text) > 5000:
            self.logger.warning(f"テキストが長すぎます ({len(text)} 文字)。切り詰めます。")
            text = text[:5000] + "..."
        
        try:
            self.logger.debug(f"音声合成開始: '{text[:50]}...' (言語: {language}, 速度: {speed})")
            
            # 言語コードを設定
            lang_code = "ja" if language == "ja" else "en"
            
            with self.temp_manager.temp_file(suffix=".mp3") as initial_temp_file:
                try:
                    tts = gTTS(text=text, lang=lang_code, slow=False)
                    tts.save(initial_temp_file)
                    self.logger.debug("gTTSによる音声合成完了")
                    
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        self.logger.error("Google TTSのAPIクォータを超過しました")
                        return None
                    elif "network" in str(e).lower() or "connection" in str(e).lower():
                        self.logger.error("ネットワーク接続エラー")
                        return None
                    else:
                        self.logger.error(f"音声合成エラー: {str(e)}")
                        return None
                
                # 音声ファイルを読み込み
                try:
                    audio = AudioSegment.from_mp3(initial_temp_file)
                    self.logger.debug(f"音声ファイル読み込み完了: 長さ={len(audio)}ms")
                except Exception as e:
                    self.logger.error(f"音声ファイルの読み込みに失敗: {str(e)}")
                    return None
                
                # 再生速度を調整
                if speed != 1.0:
                    try:
                        audio = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * speed)
                        })
                        self.logger.debug(f"再生速度を{speed}倍に調整")
                    except Exception as e:
                        self.logger.warning(f"速度調整に失敗、元の速度を使用: {str(e)}")
                
                # 最終的な音声ファイルを作成（Gradio用に管理対象外で作成）
                try:
                    final_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    final_temp_file.close()
                    
                    audio.export(final_temp_file.name, format="mp3")
                    self.logger.info(f"音声合成完了: {final_temp_file.name}")
                    
                    # このファイルはGradioが管理するので、一時ファイル管理対象に含めない
                    return final_temp_file.name
                    
                except Exception as e:
                    self.logger.error(f"最終音声ファイルの作成に失敗: {str(e)}")
                    return None
                        
        except Exception as e:
            self.logger.error(f"音声合成中に予期しないエラー: {str(e)}")
            return None
    
    def _convert_audio_format(self, audio_file: str, target_format: str = "wav") -> Optional[str]:
        """音声ファイルを適切な形式に変換する"""
        if not audio_file or not os.path.exists(audio_file):
            self.logger.warning("変換対象の音声ファイルが存在しません")
            return None
        
        try:
            self.logger.debug(f"音声形式変換開始: {audio_file} -> {target_format}")
            
            # 音声認識用の変換ファイルは短時間で使用されるため、通常の一時ファイルを使用
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
            temp_file.close()
            
            try:
                # AudioSegmentを使用して変換
                audio = AudioSegment.from_file(audio_file)
                
                # 音声の基本情報をログ出力
                self.logger.debug(f"元音声情報: 長さ={len(audio)}ms, チャンネル={audio.channels}, サンプルレート={audio.frame_rate}Hz")
                
                # WAVに変換して保存（16bitに設定）
                if target_format.lower() == "wav":
                    audio = audio.set_sample_width(2)  # 16-bit
                    audio = audio.set_frame_rate(16000)  # 音声認識に適した16kHz
                    audio = audio.set_channels(1)  # モノラル
                
                audio.export(temp_file.name, format=target_format)
                self.logger.debug(f"音声形式変換完了: {temp_file.name}")
                
                # 呼び出し元で削除する必要があるファイルとして返す
                return temp_file.name
                
            except Exception as e:
                # エラーが発生した場合は一時ファイルを削除
                self.temp_manager.remove_temp_file(temp_file.name)
                self.logger.error(f"音声変換処理中にエラー: {str(e)}")
                return None
                    
        except Exception as e:
            self.logger.error(f"音声形式変換中に予期しないエラー: {str(e)}")
            return None 