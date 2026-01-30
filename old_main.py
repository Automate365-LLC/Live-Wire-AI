# main.py (inside transcriber-backend)

from fastapi import FastAPI
from record_and_transcribe import record_audio as start_recording
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Transcriber backend running"}

@app.get("/record")
def record_audio():
    text = start_recording(duration=30)  # You can modify duration as needed
    return {"transcription": text}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
