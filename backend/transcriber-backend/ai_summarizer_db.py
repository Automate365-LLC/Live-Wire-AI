from pymongo import MongoClient
from datetime import datetime

# Connect to your local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["livewire_ai"]  # Database name
summaries = db["summaries"]  # Collection name

# Example summarization entry
sample_summary = {
    "client_id": "client_123",
    "meeting_id": "meeting_456",
    "timestamp": datetime.now(),
    "conversation_summary": "Discussed product roadmap and next quarter planning.",
    "action_items": [
        {"task": "Prepare roadmap slides", "owner": "Tanay", "due": "2025-06-02"},
        {"task": "Finalize Q3 hiring", "owner": "Amari", "due": "2025-06-03"}
    ],
    "raw_transcript_path": "transcripts/meeting_456.txt"
}

# Insert the document
result = summaries.insert_one(sample_summary)
print("✅ Inserted document with ID:", result.inserted_id)

# Verify by retrieving the inserted document
print("\n📄 Documents found:")
for doc in summaries.find({"client_id": "client_123"}):
    print(doc)
