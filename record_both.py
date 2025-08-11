import sounddevice as sd
import soundfile as sf
import threading
import os
import ffmpeg
import numpy as np
import sys
import wave

# === CONFIG ===
mic_device_index = 65      #  Microphone input
system_device_index = 30   #  System audio (VB Cable Output)
sample_rate = 48000
channels = 1
dtype = 'int16'
mic_filename = 'mic.wav'
system_filename = 'system.wav'
merged_filename = 'merged.wav'

def record_audio(filename, device_index, label):
    def callback(indata, frames, time, status):
        if status:
            print(f"[{label} WARN] {status}", file=sys.stderr)
        file.write(indata)
        peak = np.abs(indata).max()
        bar = "#" * int(peak / 1000)
        print(f"[{label}] {bar}", end="\r")

    with sf.SoundFile(filename, mode='w', samplerate=sample_rate,
                      channels=channels, subtype='PCM_16') as file:
        with sd.InputStream(device=device_index, samplerate=sample_rate,
                            channels=channels, dtype=dtype, callback=callback):
            print(f"[{label}]  Recording from device {device_index} into {filename}...")
            input(f"[{label}] Press ENTER to stop recording.\n")
            print(f"[{label}] Saved {filename}")

def get_duration(filename):
    with wave.open(filename, 'rb') as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / float(rate)

def merge_wav_files(mic_file, sys_file, out_file):
    print("[INFO]  Merging audio...")
    ffmpeg.input(mic_file).output("left.wav").run(overwrite_output=True, quiet=True)
    ffmpeg.input(sys_file).output("right.wav").run(overwrite_output=True, quiet=True)

    dur1 = get_duration("left.wav")
    dur2 = get_duration("right.wav")
    min_dur = min(dur1, dur2)

    ffmpeg.input("left.wav").output("left_trimmed.wav", t=min_dur).run(overwrite_output=True, quiet=True)
    ffmpeg.input("right.wav").output("right_trimmed.wav", t=min_dur).run(overwrite_output=True, quiet=True)

    input1 = ffmpeg.input("left_trimmed.wav")
    input2 = ffmpeg.input("right_trimmed.wav")
    (
        ffmpeg
        .filter([input1, input2], 'amerge', inputs=2)
        .output(out_file, ac=2, format='wav')
        .run(overwrite_output=True, quiet=True)
    )

    for f in ['left.wav', 'right.wav', 'left_trimmed.wav', 'right_trimmed.wav']:
        try:
            os.remove(f)
        except:
            pass

    print(f"[INFO]  Merged file saved as {out_file}")

if __name__ == "__main__":
    print("[INFO]  Recording... Press ENTER in *either* window to stop both.")

    mic_thread = threading.Thread(target=record_audio, args=(mic_filename, mic_device_index, "MIC"))
    sys_thread = threading.Thread(target=record_audio, args=(system_filename, system_device_index, "SYSTEM"))

    mic_thread.start()
    sys_thread.start()

    mic_thread.join()
    sys_thread.join()

    merge_wav_files(mic_filename, system_filename, merged_filename)
