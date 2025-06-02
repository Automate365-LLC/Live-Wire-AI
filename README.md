# Live-Wire-AI Backend

This repository contains the backend system for Live-Wire-AI, which enables real-time audio recording, transcription, summarization, and conversation storage for meetings such as Zoom or Google Meet. It includes an AI-driven summarization feature and MongoDB integration for storing client-specific meeting data.

## Features

- Records both sides of a conversation using system audio and microphone
- Transcribes recorded meetings using OpenAI Whisper
- Generates AI-based meeting summaries and action items
- Stores meeting data in MongoDB, organized by client and meeting
- WebSocket-based real-time communication with frontend
- Environment configuration via `.env` file

## Technologies Used

- Python 3.13
- FastAPI
- WebSocket
- OpenAI API (gpt-4o and Whisper)
- PyMongo with MongoDB
- VB-Audio Virtual Cable (for system audio recording)

## Folder Structure

backend/
├── recorder.py                # Records audio from virtual cable/mic
├── record\_and\_transcribe.py   # Records and transcribes audio
├── ai\_summarizer\_db.py        # Stores summaries in MongoDB
├── transcribe\_test.py         # Test script for transcription
├── main.py                    # FastAPI WebSocket backend
├── .env                       # Environment variables (excluded from git)
└── requirements.txt           # Python dependencies

## MongoDB Schema

Database: `livewire_ai`

Collection: `summaries`

Example document:
```json
{
  "client_id": "client_123",
  "meeting_id": "meeting_456",
  "timestamp": "2025-06-02T10:00:00Z",
  "conversation_summary": "Discussed product roadmap and Q3 planning.",
  "action_items": [
    {
      "task": "Prepare roadmap slides",
      "owner": "Tanay",
      "due": "2025-06-05"
    }
  ],
  "raw_transcript_path": "transcripts/meeting_456.txt"
}
````

## How to Run

1. Start MongoDB locally:
   mongod
2. Install dependencies:
   pip install -r requirements.txt
3. Run the FastAPI server:
   uvicorn main:app --reload
4. Run local recording:
   python recorder.py --device-index 2 --duration 60
5. Transcribe and save:
   python transcribe_test.py
## Notes

1. Make sure `VB-Audio Virtual Cable` is configured for capturing both system and mic audio.
2. Do not push `.env` files or sensitive keys to GitHub.
3. If using Windows, run shell installers as Administrator when needed.
