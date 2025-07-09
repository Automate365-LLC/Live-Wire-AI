# Transcriber Backend

This module records both microphone and system audio simultaneously, merges them into a single stereo file, and saves it locally.

## Features
- Record microphone and system audio in parallel
- Save as `mic.wav`, `system.wav`, and `merged.wav`
- Stop recording by pressing `ENTER`

## How to Use

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2. Run the script:
    ```bash
    python record_both.py
    ```

3. Select:
    - Microphone input device
    - System audio (e.g., VB Cable output)

4. Press `ENTER` to stop the recording.

## Output
- `mic.wav`: Microphone recording
- `system.wav`: System audio recording
- `merged.wav`: Final merged stereo audio

## Dependencies
- `sounddevice`
- `numpy`
- `ffmpeg-python`
- [FFmpeg](https://ffmpeg.org/download.html) must be installed and added to your PATH.

## License
MIT
