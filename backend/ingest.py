import os
import json
import uuid
from datetime import datetime

# --- CONFIGURATION ---
#  Finds files relative to the script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYBOOK_FILE = os.path.join(BASE_DIR, "gold_playbook.txt")
DB_FILE = os.path.join(BASE_DIR, "local_vector_db.json")

def ingest_playbook():
    """
    Reads the Gold Playbook, strips metadata, chunks by logical Q&A blocks, 
    and saves a clean JSON database.
    """
    
    # 1. VALIDATION
    if not os.path.exists(PLAYBOOK_FILE):
        print(f"ERROR: File not found at {PLAYBOOK_FILE}")
        return

    print(f"--- STARTING INGESTION: {os.path.basename(PLAYBOOK_FILE)} ---")

    # 2. READ FILE
    with open(PLAYBOOK_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. CHUNKING LOGIC
    # We split by double newlines to separate Q&A blocks
    raw_chunks = content.split('\n\n')
    
    database_records = []
    
    print(f"   -> Found {len(raw_chunks)} raw blocks. filtering...")

    for chunk in raw_chunks:
        clean_chunk = chunk.strip()

        # Skip empty chunks
        if not clean_chunk:
            continue
            
        # Skip the Header Metadata (The block that starts and ends with ---)
        # We check if it starts with --- OR if it looks like the Title block
        if clean_chunk.startswith("---") or clean_chunk.startswith("Title:"):
            print("   -> Skipping Metadata Header block.")
            continue

        # 4. CREATE RECORD
        # This structure mimics what a Vector DB (like Pinecone/Chroma) expects
        record = {
            "id": str(uuid.uuid4()),
            "text": clean_chunk,
            "metadata": {
                "source": "gold_playbook.txt",
                "character_len": len(clean_chunk),
                "ingested_at": str(datetime.now())
            }
        }
        database_records.append(record)

    # 5. SAVE TO DISK
    # We use 'w' (write) mode to overwrite the file every time. 
    # This prevents duplicate data during testing.
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(database_records, f, indent=2)
            
        print(f"--- SUCCESS ---")
        print(f"   -> Saved {len(database_records)} clean chunks to '{os.path.basename(DB_FILE)}'")
        print(f"   -> Ready for retrieval testing.")
        
    except Exception as e:
        print(f" ERROR Saving database: {e}")

if __name__ == "__main__":
    ingest_playbook()