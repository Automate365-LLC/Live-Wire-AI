import sounddevice as sd
import soundfile as sf
import threading
import os
import subprocess

# === CONFIGURATION ===
mic_index = 1        # Replace with your MIC device index
sys_index = 2        # Replace with your SYSTEM AUDIO device index
sample_rate = 48000
channels = 1
recordings_dir = os.path.abspath('.')  # Saves to current directory

mic_path = os.path.join(recordings_dir, "mic.wav")
sys_path = os.path.join(recordings_dir, "system.wav")
merged_path = os.path.join(recordings_dir, "merged.wav")

# === RECORDING FUNCTION ===
def record_device(index, filename, stop_event, label):
    print(f"[INFO] 🎙️ Recording from device {index} into {filename}...")
    with sf.SoundFile(filename, mode='w', samplerate=sample_rate, channels=channels) as file:
        with sd.InputStream(samplerate=sample_rate, device=index, channels=channels, dtype='int16') as stream:
            while not stop_event.is_set():
                data, _ = stream.read(1024)
                file.write(data)
    print(f"[INFO]  Saved {filename}")

# === MAIN ===
def main():
    stop_event = threading.Event()

    print(f"[INFO]  Recording... Press ENTER to stop.\n")

    mic_thread = threading.Thread(target=record_device, args=(mic_index, mic_path, stop_event, "MIC"))
    sys_thread = threading.Thread(target=record_device, args=(sys_index, sys_path, stop_event, "SYSTEM"))

    mic_thread.start()
    sys_thread.start()

    input()  # Wait for user to press Enter
    stop_event.set()

    mic_thread.join()
    sys_thread.join()

    print(f"[INFO]  Merging mic.wav and system.wav into merged.wav...")
    merge_cmd = [
        "ffmpeg", "-y",
        "-i", mic_path,
        "-i", sys_path,
        "-filter_complex", "[0:a][1:a]amerge=inputs=2[aout]",
        "-map", "[aout]",
        "-ac", "2",
        merged_path
    ]
    try:
        subprocess.run(merge_cmd, check=True)
        print(f"[INFO]  Merged audio saved as {merged_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to merge: {e}")

if __name__ == "__main__":
    main()
