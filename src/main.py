import threading
import time
import keyboard
from rich.live import Live
from audio import record_audio, process_audio_with_whisper, play_audio, text_queue
from text_processing import process_transcription
from ui import layout, update_conversation, initialize_ui
from utils import toggle_recording, stop_audio
import globals as global_vars

def main_loop():
    script = []

    keyboard.add_hotkey('c', toggle_recording)
    keyboard.add_hotkey('v', stop_audio)

    while global_vars.running:
        if global_vars.recording:
            try:
                audio = record_audio()
                transcription = process_audio_with_whisper(audio)
                print(f"Transcription: {transcription}")
                
                response_text = process_transcription(transcription, script)
                print(f"Flash answer: {response_text}")

                update_conversation(transcription, response_text)
                text_queue.put(response_text)
                
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
                print(f"Error while recording/processing: {e}")
                import traceback
                traceback.print_exc()
        
        time.sleep(0.1)

if __name__ == '__main__':
    global_vars.init()
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()
    
    try:
        initialize_ui()
        with Live(layout, refresh_per_second=4, screen=True):
            main_loop()
    except KeyboardInterrupt:
        print("Stopping program...")
    finally:
        global_vars.running = False
        text_queue.put(None)
        audio_thread.join()