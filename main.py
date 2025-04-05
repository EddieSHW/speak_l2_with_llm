import warnings
from src.ui.chat_interface import ChatInterface

def main():
    """アプリケーションのメインエントリーポイント"""
    # 特定の警告を抑制
    warnings.filterwarnings("ignore", message="Trying to convert audio automatically")
    
    # チャットインターフェースのインスタンスを作成
    chat_interface = ChatInterface()
    
    # インターフェースを構築して起動
    demo = chat_interface.build_interface()
    demo.launch(share=False)

if __name__ == "__main__":
    main() 