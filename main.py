import warnings
from src.ui.chat_interface import ChatInterface

def main():
    """アプリケーションのメインエントリーポイント"""
    # 特定の警告を抑制
    warnings.filterwarnings("ignore", message="Trying to convert audio automatically")
    
    # タイトルを表示
    print("====================================")
    print("日本語会話教師 - AI日本語練習アプリ")
    print("====================================")
    print("アプリケーションを起動中...")
    
    # チャットインターフェースのインスタンスを作成
    chat_interface = ChatInterface()
    
    # インターフェースを構築して起動
    ui = chat_interface.build_interface()
    ui.launch(share=False)

if __name__ == "__main__":
    main()