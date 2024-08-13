import sounddevice as sd
import globals as global_vars

def toggle_recording():
    global_vars.recording = not global_vars.recording
    print("Recording started." if global_vars.recording else "Recording stopped.")

def stop_audio():
    sd.stop()
    print("Audio Playback stopped.")