import os
import time
import requests
import sounddevice as sd
import numpy as np
import torch
from pydub import AudioSegment
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import io
from collections import deque
from queue import Queue
from config import ELEVENLABS_API_KEY, VOICE_ID, SAMPLE_RATE, MAX_AUDIO_FILES, WHISPER_MODEL
import threading
import globals as glob

processor = WhisperProcessor.from_pretrained(WHISPER_MODEL)
whisper_model = WhisperForConditionalGeneration.from_pretrained(WHISPER_MODEL)
whisper_model.config.forced_decoder_ids = None

device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model = whisper_model.to(device)

text_queue = Queue()


def generate_audio(text, filename):
    if len(text) > 2500:
        raise ValueError("The text exceeds 2500 characters.")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        audio = AudioSegment.from_mp3(io.BytesIO(response.content))
        audio.export(filename, format="wav")
    else:
        print(f"Error while generating audio: {response.status_code} - {response.text}")

def play_audio_file(file_path):
    audio = AudioSegment.from_wav(file_path)
    samples = np.array(audio.get_array_of_samples())
    sd.play(samples, audio.frame_rate)
    sd.wait()

def play_audio():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_files = deque(maxlen=MAX_AUDIO_FILES)
    
    while True:
        text = text_queue.get()
        if text is None:
            break
        try:
            new_audio = os.path.join(script_dir, f"audio_{len(audio_files)}.wav")
            generate_audio(text, new_audio)
            
            if os.path.exists(new_audio):
                file_size = os.path.getsize(new_audio)
                if file_size > 0:
                    play_audio_file(new_audio)
                    audio_files.append(new_audio)
                    if len(audio_files) == MAX_AUDIO_FILES:
                        oldest_file = audio_files.popleft()
                        if os.path.exists(oldest_file):
                            os.remove(oldest_file)
                else:
                    print("The audio file is empty")
                    os.remove(new_audio)
            else:
                print(f"Couldn't generate audio: {new_audio}")
        except Exception as e:
            print(f"Error in play_audio: {e}")
            import traceback
            traceback.print_exc()

    for audio_file in audio_files:
        if os.path.exists(audio_file):
            os.remove(audio_file)

def record_audio():
    audio_data = []
    while glob.recording:
        chunk = sd.rec(int(SAMPLE_RATE * 1), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        audio_data.append(chunk.flatten())
    
    if len(audio_data) > 0:
        return np.concatenate(audio_data)
    else:
        print("Audio wasn't recorded.")
        return np.array([])


def process_audio_with_whisper(audio):
    with torch.no_grad():
        input_features = processor(audio, sampling_rate=SAMPLE_RATE, return_tensors="pt").input_features.to(device)
        predicted_ids = whisper_model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return transcription

# Variables globales
recording = False
audio_playing = threading.Event()