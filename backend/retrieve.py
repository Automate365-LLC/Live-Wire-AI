import json
import os
import argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "local_vector_db.json")
INDEX_FILE = os.path.join(BASE_DIR, "vector_index.bin")

# Global Load (to prevent reloading on every function call in WS3)
_model = None
_index = None
_db = None

def get_resources():
    global _model, _index, _db
    if _model is None:
        # Load Model
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        # Load Index
        if os.path.exists(INDEX_FILE):
            _index = faiss.read_index(INDEX_FILE)
        # Load DB
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                _db = json.load(f)
    return _model, _index, _db

def search(query, top_k=3):
    """
    [WS4-2.1] Retrieval API v0.1 (Vector Version)
    Input: Query string
    Output: Top-k semantic matches
    """
    model, index, db = get_resources()
    
    if not index or not db:
        return []

    # 1. Convert Query to Vector
    query_vector = model.encode([query])
    
    # 2. Search FAISS Index
    # D = distances (scores), I = indices (row numbers)
    D, I = index.search(np.array(query_vector).astype('float32'), top_k)
    
    results = []
    
    # 3. Map FAISS IDs back to JSON Data
    for i, idx in enumerate(I[0]):
        if idx == -1: continue # No match found
        
        # FAISS Index ID maps directly to JSON List Index
        record = db[idx]
        
        match_data = {
            "chunk_id": record["chunk_id"],
            "score": float(D[0][i]), # Distance score (Lower is better for L2)
            # NOTE:
            # FAISS returns L2 distance by default.
            # Lower score = more similar.
            # Normalization / confidence conversion happens at reranking layer 
            "text_content": record["text_content"],
            "metadata": record.get("metadata", {})

        }
        results.append(match_data)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="The question to ask", nargs='?')
    args = parser.parse_args()
    q = args.query if args.query else input("Enter question: ")
    
    response = search(q)
    print(json.dumps(response, indent=2))