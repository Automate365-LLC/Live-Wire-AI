import warnings
warnings.filterwarnings("ignore")

import whisper

# Load Whisper model
model = whisper.load_model("base")

# Transcribe the recorded audio
result = model.transcribe("output.wav")

# Print the transcribed text
print("Transcription Result:")
print(result["text"])
