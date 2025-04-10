# Speak L2 with LLM - AI 第２言語会話練習アプリ

Ollama を使用して動作する日本語および英語学習者向けの会話練習アプリケーションです。このアプリは、文法的な間違いや不自然な表現を指摘し、より自然な日本語と英語を学ぶことができます。

## 主な機能

- **教師モード**: 文法的な間違いや不自然な表現を指摘し、より良い表現を提案
- **音声入力**: マイクから日本語と英語を話して練習
- **音声出力**: AI の応答を音声で聞くことができる
- **テキスト入力・出力**: キーボードで入力して練習することも可能
- **完全プライベート**: ローカルの Ollama を使用するため、データは外部に送信されません
- **カスタマイズ可能**: 温度パラメータやトークン数を調整可能
- **多言語対応**: 日本語と英語の両方で会話練習が可能
- **言語切り替え**: 練習中に簡単に言語を切り替え可能

## 前提条件

- Python 3.9 以上
- [Ollama](https://ollama.ai/)がインストール済みで実行中
- 少なくとも 1 つのモデルが Ollama にインストールされていること（推奨：gemma3）
- 音声認識には適切なマイク設定が必要

## インストール方法

1. リポジトリをクローン、またはファイルをダウンロードします。
2. 必要なパッケージをインストールします：

```bash
pip install -r requirements.txt
```

3. `.env.example`を`.env`にコピーして必要に応じて設定を変更します：

```bash
cp .env.example .env
```

## 使い方

1. Ollama が実行中であることを確認します。
2. 以下のコマンドでアプリケーションを起動します：

```bash
python3 main.py
```

3. ブラウザで`http://localhost:7860`にアクセスしてアプリケーションを使用します。
4. テキスト入力または音声入力を使用して日本語か英語で会話練習ができます。
   - テキスト入力：入力ボックスに日本語か英語でテキストを入力して Enter キーを押す
   - 音声入力：マイクボタンをクリックして話し、停止ボタンで音声認識を実行
5. AI が文法や表現の間違いを指摘し、より自然な表現を提案します。

## 教師モードについて

このアプリのデフォルト設定では「教師モード」が有効になっています。このモードでは：

1. 文法的なミスや不自然な表現を指摘
2. より自然な表現の提案
3. 会話の自然な継続

を AI が行います。教師モードをオフにすると、通常の会話モードになり、文法チェックなしで会話が続きます。

## Ollama モデルのインストール方法

会話に適したモデルをインストールするには：

```bash
ollama pull gemma3
# または
ollama pull llama3
```

## トラブルシューティング

- **「Ollama サーバーに接続できません」エラー**：Ollama が実行中であることを確認してください。
- **音声認識エラー**：マイクが正しく設定されていることを確認してください。
- **音声出力が聞こえない**：ブラウザの音声設定を確認してください。
- **音声の認識精度が低い**：静かな環境で、明瞭に話してください。
- **応答が遅い**：より小さなモデルを使用するか、GPU アクセラレーションが有効になっていることを確認してください。

## 学習に役立つヒント

- 毎日少しずつ練習することが効果的です
- 初めは簡単な文章から始めましょう
- AI からの修正提案を声に出して練習しましょう
- 同じ表現でもさまざまな言い方を試してみましょう

## 免責事項

このアプリケーションは学習支援ツールであり、プロの日本語と英語教師に代わるものではありません。AI の提案には間違いが含まれる可能性もあるため、重要な場面では専門家に相談することをお勧めします。

## ライセンス

MIT ライセンス

---

# Speak L2 with LLM - AI Language Practice App

An AI-powered conversation practice application for language learners using Ollama. This app identifies grammatical errors and unnatural expressions, helping you learn more natural language expressions.

## Key Features

- **Language Teacher Mode**: Identifies grammatical errors and unnatural expressions, suggesting better alternatives
- **Voice Input**: Practice speaking through your microphone
- **Voice Output**: Listen to AI responses via audio
- **Text Input/Output**: Practice using keyboard input as well
- **Completely Private**: Uses local Ollama, so data is never sent externally
- **Customizable**: Adjust temperature parameters and token counts
- **Multi-language Support**: Practice both Japanese and English conversations
- **Language Switching**: Easily switch between languages during practice

## Requirements

- Python 3.9 or higher
- [Ollama](https://ollama.ai/) installed and running
- At least one model installed in Ollama (recommended: gemma3)
- Proper microphone setup for voice recognition

## Installation

1. Clone the repository or download the files.
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and modify settings as needed:

```bash
cp .env.example .env
```

## Usage

1. Make sure Ollama is running.
2. Start the application with:

```bash
python3 main.py
```

3. Access the application in your browser at `http://localhost:7860`.
4. Practice conversations using text or voice input.
   - Text input: Type text in the input box and press Enter
   - Voice input: Click the microphone button to speak, then click stop for voice recognition
5. The AI will identify grammar or expression errors and suggest more natural alternatives.

## About Language Teacher Mode

The default setting enables "Language Teacher Mode" which:

1. Points out grammatical mistakes and unnatural expressions
2. Suggests more natural expressions
3. Continues the conversation naturally

Disabling Teacher Mode switches to normal conversation mode without grammar checking.

## Installing Ollama Models

To install models suitable for language conversation:

```bash
ollama pull gemma3
# or
ollama pull llama3
```

## Troubleshooting

- **"Cannot connect to Ollama server" error**: Ensure Ollama is running.
- **Voice recognition errors**: Check that your microphone is properly set up.
- **No audio output**: Check your browser's audio settings.
- **Low recognition accuracy**: Speak clearly in a quiet environment.
- **Slow responses**: Use a smaller model or ensure GPU acceleration is enabled.

## Learning Tips

- Practice a little each day for best results
- Start with simple sentences
- Practice the AI's correction suggestions out loud
- Try different ways of expressing the same content

## Disclaimer

This application is a learning aid and not a replacement for professional language teachers. AI suggestions may contain errors, so consult professionals for important situations.

## License

MIT License

---

# Speak L2 with LLM - AI 英日語練習應用程式

這是一個針對外語學習者的會話練習應用程式，使用 Ollama 運行。此應用程式可以指出語法錯誤和不自然的表達，幫助您學習更自然的英日語。

## 主要功能

- **教師模式**: 指出語法錯誤和不自然的表達，並提供更好的表達建議
- **語音輸入**: 通過麥克風說英/日語進行練習
- **語音輸出**: 可以聽取 AI 回應的語音
- **文字輸入輸出**: 也可以通過鍵盤輸入進行練習
- **完全私密**: 使用本地 Ollama 運行，數據不會發送到外部
- **可自定義**: 可調整溫度參數和語句長度
- **多語言支援**: 支援日語和英語的會話練習
- **語言切換**: 練習過程中可以輕鬆切換語言

## 前提條件

- Python 3.9 或更高版本
- 已安裝並運行[Ollama](https://ollama.ai/)
- Ollama 中至少安裝了一個模型（推薦：gemma3）
- 語音識別需要適當的麥克風設置

## 安裝方法

1. 複製軟體倉庫或下載文件。
2. 安裝必要的套件：

```bash
pip install -r requirements.txt
```

3. 將`.env.example`複製為`.env`並根據需要修改設置：

```bash
cp .env.example .env
```

## 使用方法

1. 確認 Ollama 正在運行。
2. 使用以下命令啟動應用程式：

```bash
python3 main.py
```

3. 在瀏覽器中訪問`http://localhost:7860`使用應用程式。
4. 可以使用文字輸入或語音輸入進行英日語會話練習。
   - 文字輸入：在輸入框中輸入英日語文字，然後按 Enter 鍵
   - 語音輸入：點擊麥克風按鈕說話，然後點擊停止按鈕進行語音識別
5. AI 將指出語法或表達的錯誤，並提出更自然的表達建議。

## 關於教師模式

此應用的預設設置啟用了「教師模式」。在此模式下，AI 將：

1. 指出語法錯誤和不自然的表達
2. 提供更自然的表達建議
3. 自然地繼續對話

如果禁用教師模式，將切換到普通對話模式，對話將在沒有語法檢查的情況下繼續。

## Ollama 模型安裝方法

要安裝適合英日語對話的模型，請執行：

```bash
ollama pull gemma3
# 或者
ollama pull llama3
# 或者
ollama pull gemma:7b
```

## 故障排除

- **「無法連接到 Ollama 伺服器」錯誤**：確認 Ollama 正在運行。
- **語音識別錯誤**：確認麥克風設置正確。
- **聽不到語音輸出**：檢查瀏覽器的音頻設置。
- **語音識別準確度低**：在安靜的環境中清晰地說話。
- **回應緩慢**：使用更小的模型或確認 GPU 加速已啟用。

## 學習有用的提示

- 每天進行少量練習是有效的
- 從簡單的句子開始
- 大聲練習 AI 提出的修正建議
- 嘗試用各種方式表達相同的內容

## 免責聲明

此應用程式是學習輔助工具，不能取代專業英日語教師。AI 的建議可能包含錯誤，因此在重要場合諮詢專業人士。

## 授權

MIT 授權
