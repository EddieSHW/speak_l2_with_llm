# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Speak L2 with LLM" - an AI-powered language learning application that helps users practice Japanese and English conversation using local Ollama models. The app provides grammar correction and natural expression suggestions in a "teacher mode" while maintaining conversational flow.

## Key Architecture

**Main Components:**
- `main.py`: Application entry point that launches the Gradio interface
- `src/ui/chat_interface.py`: Core Gradio UI implementation with chatbot, audio input/output, and settings
- `src/services/ollama_service.py`: Handles all Ollama API communication and response processing
- `src/utils/audio_utils.py`: Speech recognition (Google) and text-to-speech (gTTS) functionality
- `src/config/settings.py`: Configuration management with environment variables and system prompts

**Data Flow:**
1. User input (text/voice) → ChatInterface
2. Audio processing (if voice) → AudioUtils → text
3. Text → OllamaService → LLM response with teacher feedback
4. Response → AudioUtils → speech synthesis → user

## Development Commands

**Setup and Running:**
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Run application (launches on http://localhost:7860)
python3 main.py
```

**Dependencies:**
- Python 3.9+
- Local Ollama installation with models (gemma3 recommended)
- Audio dependencies for speech recognition/synthesis

## Important Configuration

**Environment Variables (.env):**
- `OLLAMA_API_URL`: Ollama server endpoint (default: http://localhost:11434)
- `MODEL_NAME`: Default model (default: gemma3)
- `DEFAULT_TEMPERATURE`: LLM temperature (default: 0.7)
- `DEFAULT_MAX_TOKENS`: Response length limit (default: 2048)

**System Prompts:**
The application uses sophisticated system prompts for Japanese and English teacher modes that:
- Prohibit markdown formatting and emojis
- Format corrections in a specific teaching structure
- Maintain conversational flow while providing feedback
- Use plain text output with `<think>` tags for reasoning

## Key Technical Details

**Markdown Removal:** The `OllamaService.remove_markdown()` function strips all markdown formatting from LLM responses to ensure plain text output, including removal of `<think>` tag content.

**Audio Processing:** Uses Google Speech Recognition for transcription and gTTS for synthesis with 1.25x playback speed. Handles audio format conversion automatically.

**Language Support:** Switches between Japanese and English modes with appropriate language codes for speech services and different system prompts.

**Teacher Mode:** Core feature that provides grammar correction and natural expression suggestions while maintaining conversation flow. Can be toggled on/off.