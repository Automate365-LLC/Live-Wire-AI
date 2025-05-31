# Transcriber Backend

This module handles real-time and file-based audio transcription using OpenAI Whisper.

##  Features Implemented

 Microphone recording using `sounddevice`
 VB-Audio Cable integration to capture system + mic audio
 Transcription using OpenAI Whisper
 Tested with `transcribe_test.py`

## How to Use

1. Install dependencies:

 pip install -r requirements.txt


2. Record audio:

 python recorder.py --device-index <index> --filename output.wav --duration 10

3. Transcribe the audio:

 python transcribe_test.py


## Known Issues

- Zoom/Google Meet system audio capture needs improvement
- Still working on clean merging of speaker + system channels

## Note

`.env` file (excluded via `.gitignore`) stores your OpenAI API key:

OPENAI_API_KEY= (your-api-key)