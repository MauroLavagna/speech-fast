import sounddevice as sd
import globals as global_vars

def toggle_recording():
    global_vars.recording = not global_vars.recording
    print("Grabación iniciada." if global_vars.recording else "Grabación detenida.")

def stop_audio():
    sd.stop()
    print("Reproducción de audio detenida.")