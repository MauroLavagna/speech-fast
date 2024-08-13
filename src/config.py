import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
VOICE_ID = os.getenv('VOICE_ID')

SAMPLE_RATE = int(os.getenv('SAMPLE_RATE', 16000))
MAX_AUDIO_FILES = int(os.getenv('MAX_AUDIO_FILES', 40))

WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'openai/whisper-small')

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'models/gemini-1.5-flash-latest'))