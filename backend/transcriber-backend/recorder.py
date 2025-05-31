import argparse
import sounddevice as sd
from scipy.io.wavfile import write

def record_audio(duration, filename, fs=44100, device_index=None):
    print("🎙️ Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=device_index)
    sd.wait()
    write(filename, fs, recording)
    print(f"✅ Recording saved as {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record audio from a selected device.")
    parser.add_argument("--device-index", type=int, help="Index of input device (see sounddevice.query_devices())", required=True)
    parser.add_argument("--filename", type=str, default="output.wav", help="Filename to save the recording")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds")

    args = parser.parse_args()
    record_audio(duration=args.duration, filename=args.filename, device_index=args.device_index)
