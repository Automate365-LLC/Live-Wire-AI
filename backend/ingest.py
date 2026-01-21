import os
import json
import uuid
from datetime import datetime

# --- CONFIGURATION ---
# Uses relative paths so this works on any developer's machine
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYBOOK_FILE = os.path.join(BASE_DIR, "gold_playbook.txt")
DB_FILE = os.path.join(BASE_DIR, "local_vector_db.json")

def ingest_playbook():
    """
    Core Ingestion Logic :
    1. Reads the raw 'gold_playbook.txt'.
    2. Chunks text by double-newline (Q&A pairs).
    3. Generates UUIDs and timestamps.
    4. Saves a structured JSON database.
    """
    
    # 1. VALIDATION: Ensure the source file exists before crashing
    if not os.path.exists(PLAYBOOK_FILE):
        print(f" ERROR: File not found at {PLAYBOOK_FILE}")
        return

    print(f"---  STARTING INGESTION: {os.path.basename(PLAYBOOK_FILE)} ---")

    # 2. READ FILE
    with open(PLAYBOOK_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. CHUNKING STRATEGY
    # We split by double newlines (\n\n) to keep Q&A pairs together.
    # This prevents the AI from finding a Question without its Answer.
    raw_chunks = content.split('\n\n')
    
    database_records = []
    print(f"   -> Found {len(raw_chunks)} raw blocks. Filtering...")

    for chunk in raw_chunks:
        clean_chunk = chunk.strip()

        # Filter: Skip empty lines
        if not clean_chunk:
            continue
            
        # Filter: Skip Metadata Headers (e.g., '--- Title: ...')
        # We assume headers start with '---' or 'Title:' based on the file format.
        if clean_chunk.startswith("---") or clean_chunk.startswith("Title:"):
            print("   -> Skipping Metadata Header block.")
            continue

        # 4. DATA MODEL [WS4-04]
        # This schema matches the Architecture Doc.
        # It prepares the data for the Retrieval API (WS4-2.1).
        record = {
            "chunk_id": str(uuid.uuid4()),        # Unique ID for tracking
            "text_content": clean_chunk,          # The raw Q&A text
            "embedding": [],                      # Placeholder: Phase 2 will fill this with Vectors
            "metadata": {
                "source_file": "gold_playbook.txt",
                "character_len": len(clean_chunk),
                "ingested_at": str(datetime.now())
            }
        }
        database_records.append(record)

    # 5. PERSISTENCE 
    # We use 'w' (write) mode to fully overwrite the database.
    # This ensures "Idempotency" (running script twice doesn't create duplicates).
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(database_records, f, indent=2)
            
        print(f"--- SUCCESS ---")
        print(f"   -> Saved {len(database_records)} compliant chunks to '{os.path.basename(DB_FILE)}'")
        
    except Exception as e:
        print(f" ERROR Saving database: {e}")

if __name__ == "__main__":
    ingest_playbook()