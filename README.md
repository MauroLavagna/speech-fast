# Speecherino
 
## Overview

This AI Voice Assistant is a Python-based application that combines speech recognition, natural language processing, and text-to-speech capabilities to create an interactive voice-based AI assistant. It uses Google's Gemini model for natural language understanding and generation, Whisper for speech recognition, and ElevenLabs for text-to-speech conversion.

## Features

- Real-time speech recognition
- Natural language processing using Google's Gemini model
- Text-to-speech conversion using ElevenLabs
- Interactive command-line interface

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/ai-voice-assistant.git
   cd ai-voice-assistant
   ```

2. Create and activate a Python virtual environment:
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS and Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy the `.env.example` file to `.env`
   - Fill in your API keys and other configuration values in the `.env` file

## Usage

To start the AI Voice Assistant, run:

```
python src/main.py
```

- Press 'C' to start/stop recording
- Press 'V' to stop audio playback
- Press 'Ctrl+C' to exit the program

Note: Make sure you're in the project root directory and your virtual environment is activated when running the application.

## Project Structure

- `src/`: Source code directory
  - `main.py`: Main entry point of the application
  - `audio.py`: Audio processing functions
  - `config.py`: Configuration and environment variable management
  - `global.py`: Global variables
  - `text_processing.py`: Text processing functions
  - `ui.py`: User interface functions
  - `utils.py`: Utility functions
- `.env`: Environment variables (not tracked by git)
- `requirements.txt`: List of Python dependencies

## Configuration

The application uses environment variables for configuration. These are stored in the `.env` file. Make sure to set the following variables:

- `GOOGLE_API_KEY`: Your Google API key
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `VOICE_ID`: The ID of the voice to use for text-to-speech
- `SAMPLE_RATE`: Audio sample rate (default: 16000)
- `MAX_AUDIO_FILES`: Maximum number of audio files to keep (default: 40)
- `WHISPER_MODEL`: Whisper model to use for speech recognition (default: "openai/whisper-small")
- `GEMINI_MODEL`: Gemini model to use for natural language processing (default: "models/gemini-1.5-flash-latest")

## Contributing

Contributions to this project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Google Gemini for natural language processing
- OpenAI Whisper for speech recognition
- ElevenLabs for text-to-speech conversion