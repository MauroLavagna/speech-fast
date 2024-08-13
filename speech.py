import os
import threading
import time
import requests
import google.generativeai as genai
from queue import Queue, Empty
from pydub import AudioSegment
import sounddevice as sd
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import io
from collections import deque
import keyboard
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich import box
console = Console()
conversation_history = []

# Crear el layout principal
# Update the main layout configuration
layout = Layout()
layout.split(
    Layout(name="header", size=3),
    Layout(name="main", ratio=1),
    Layout(name="footer", size=3)
)

layout["header"].update(Panel(
    "Asistente de Voz AI",
    border_style="bold magenta",
    box=box.DOUBLE
))

layout["footer"].update(Panel(
    "Presiona 'C' para iniciar/detener la grabación, 'V' para detener la reproducción de audio",
    border_style="bold cyan",
    box=box.DOUBLE
))

conversation_panel = Panel(
    Text("Inicia la conversación...", style="italic"),
    title="Conversación",
    border_style="bold blue",
    box=box.ROUNDED,
    expand=True
)

layout["main"].update(conversation_panel)

console.clear()
console.print(layout)

# Configuración de las claves API
GOOGLE_API_KEY = 'AIzaSyDAu6xlQVa3p3v7DGWThlpXioEcfiC4jeE'
ELEVENLABS_API_KEY = 'sk_a6380349776ff01846b8cab0344dc60828eebab8aece5099'
VOICE_ID = 'y6WtESLj18d0diFRruBs'

# Configurar el cliente de Google AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

# Inicializar el procesador y modelo de Whisper globalmente
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
whisper_model.config.forced_decoder_ids = None

# Mover el modelo a GPU si está disponible
device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model = whisper_model.to(device)

# Cola para almacenar respuestas de texto
text_queue = Queue()

# Variables globales
running = True
MAX_AUDIO_FILES = 5
recording = False
audio_playing = threading.Event()

def update_conversation(transcription, response):
    global conversation_history
    # Add the new interaction to the conversation history
    user_message = Text(f"Mauro: {transcription}\n", style="bold green")
    ai_message = Text(f"AI: {response}\n", style="bold blue")
    conversation_history.append(user_message)
    conversation_history.append(Text("\n"))  # Add a blank line for separation
    conversation_history.append(ai_message)

    # Combine all messages into a single Text object
    conversation_text = Text()
    for message in conversation_history:
        conversation_text.append(message)

    # Update the conversation panel
    conversation_panel = Panel(
        conversation_text,
        title="Conversación",
        border_style="cyan",
        box=box.ROUNDED,
        expand=True,
        padding=(1, 1)
    )
    layout["main"].update(conversation_panel)

    console.clear()
    console.print(layout)

# Función para generar audio a partir del texto
def generate_audio(text, filename):
    if len(text) > 2500:
        raise ValueError("El texto excede el límite de 2500 caracteres.")
    
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
        # Convertir MP3 a WAV y guardar en la carpeta del script
        audio = AudioSegment.from_mp3(io.BytesIO(response.content))
        audio.export(filename, format="wav")
    else:
        print(f"Error al generar audio: {response.status_code} - {response.text}")

# Función para reproducir un archivo de audio
def play_audio_file(file_path):
    global audio_playing
    audio = AudioSegment.from_wav(file_path)
    # Convertir AudioSegment a un array numpy
    samples = np.array(audio.get_array_of_samples())
    # Reproducir el audio usando sounddevice
    sd.play(samples, audio.frame_rate)
    
    while sd.get_stream().active:
        if not audio_playing.is_set():
            sd.stop()  # Detener la reproducción si se interrumpe
            break
        time.sleep(0.1)  # Evitar un bucle demasiado apretado
    sd.wait()

# Actualizar la función play_audio para manejar mejor la interrupción
def play_audio():
    global audio_playing
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_files = deque(maxlen=MAX_AUDIO_FILES)
    
    while True:
        text = text_queue.get()
        if text is None:
            break
        audio_playing.set()
        try:
            # Generar un nombre único para el nuevo archivo de audio en la carpeta del script
            new_audio = os.path.join(script_dir, f"audio_{len(audio_files)}.wav")
            
            # Generar el audio con la respuesta de FLASH
            generate_audio(text, new_audio)
            
            if os.path.exists(new_audio):
                file_size = os.path.getsize(new_audio)
                if file_size > 0:
                    play_audio_file(new_audio)
                    
                    # Agregar el nuevo archivo a la cola
                    audio_files.append(new_audio)
                    
                    # Si hemos excedido el número máximo de archivos, eliminar el más antiguo
                    if len(audio_files) == MAX_AUDIO_FILES:
                        oldest_file = audio_files.popleft()
                        if os.path.exists(oldest_file):
                            os.remove(oldest_file)
                else:
                    print("El archivo de audio está vacío.")
                    os.remove(new_audio)  # Eliminar el archivo vacío
            else:
                print(f"No se pudo generar el archivo de audio: {new_audio}")
        except Exception as e:
            print(f"Error en play_audio: {e}")
            import traceback
            traceback.print_exc()
        finally:
            audio_playing.clear()

    # Limpiar los archivos de audio restantes al finalizar
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            os.remove(audio_file)

# Función para detener la reproducción de audio cuando se presiona 'V'
def stop_audio():
    if audio_playing:
        sd.stop()
        print("Reproducción de audio detenida.")

def record_audio(samplerate=16000):
    audio_data = []
    while recording:
        chunk = sd.rec(int(samplerate * 1), samplerate=samplerate, channels=1, dtype='float32')
        sd.wait()
        audio_data.append(chunk.flatten())
        if not recording:  # Verifica si la grabación fue detenida
            break
    return np.concatenate(audio_data)

def toggle_recording():
    global recording
    if recording:
        recording = False  # Detener la grabación si ya estaba grabando
        print("Grabación detenida.")
    else:
        recording = True  # Iniciar la grabación
        print("Grabación iniciada.")


# Función para procesar audio con Whisper
def process_audio_with_whisper(audio):
    with torch.no_grad():
        input_features = processor(audio, sampling_rate=16000, return_tensors="pt").input_features.to(device)
        predicted_ids = whisper_model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return transcription

# Generar un nuevo mensaje para el modelo de AI
def generate_new_message(transcription):
    return [
        {
            "role": "user",
            "content": {
                "parts": [
                    {
                        "text": f" Responde siempre en el lenguaje que te habla el usuario. No respondas con simbolos ni caracteres extraños. No uses asteriscos. User: {transcription}"
                    }
                ]
            }
        }
    ]

# Procesar audio y generar la respuesta del modelo
def process_audio(transcription, script):
    try:
        messages = script + generate_new_message(transcription)
        content_messages = [
            {
                "role": message["role"],
                "parts": [{"text": part["text"]} for part in message["content"]["parts"]]
            }
            for message in messages
        ]
        response = model.generate_content(content_messages)
        return response.text
    except Exception as e:
        print(f"Error en process_audio: {e}")
        return ""

# Función principal del programa
def main_loop():
    global running, recording
    script = []

    keyboard.add_hotkey('c', toggle_recording)

    while running:
        if recording:
            try:
                # Grabar audio
                audio = record_audio()
                
                # Procesar audio con Whisper
                transcription = process_audio_with_whisper(audio)
                
                print(f"Transcripción: {transcription}")
                
                # Procesar la transcripción con FLASH
                response_text = process_audio(transcription, script)
                print(f"Respuesta de FLASH: {response_text}")

                # Mostrar la conversación en la interfaz
                update_conversation(transcription, response_text)

                # Agregar la respuesta a la cola de texto para reproducción
                text_queue.put(response_text)
                
                # Actualizar el script
                script.append(
                    {
                        "role": "model",
                        "content": {
                            "parts": [
                                {
                                    "text": response_text
                                }
                            ]
                        }
                    }
                )
            except Exception as e:
                print(f"Error durante la grabación/procesamiento: {e}")
                import traceback
                traceback.print_exc()

            recording = False
            print("Presiona 'C' para iniciar una nueva grabación.")
        
        time.sleep(0.1)

# Ejecutar el programa principal
if __name__ == '__main__':
    running = True
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()
    
    try:
        with Live(layout, refresh_per_second=4, screen=True):
            main_loop()
    except KeyboardInterrupt:
        print("Deteniendo el programa...")
    finally:
        running = False
        text_queue.put(None)
        audio_thread.join()