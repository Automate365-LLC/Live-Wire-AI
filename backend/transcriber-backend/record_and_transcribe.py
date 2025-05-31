import sounddevice as sd
from scipy.io.wavfile import write
import whisper

def record_audio(duration=5, fs=44100, filename="output.wav"):
    print("🎙️ Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)
    print("✅ Recording complete.")
    return filename

def transcribe_audio(filepath):
    model = whisper.load_model("base")
    result = model.transcribe(filepath)
    print("🧠 Transcription result:", result["text"])
    return result["text"]
