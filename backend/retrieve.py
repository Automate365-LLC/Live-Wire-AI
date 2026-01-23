import json
import os
import argparse

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "local_vector_db.json")
MIN_SCORE_THRESHOLD = 1 

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def search(query, top_k=3):
    """
    Retrieval API v0.1
    Returns top-k chunks with scores + chunk IDs + source metadata.
    """
    db = load_db()
    results = []
    query_words = query.lower().split()
    STOP_WORDS = {"what", "is", "the", "a", "an", "of", "to", "in", "it", "does"}

    for record in db:
        
        text = record.get('text_content', '').lower()
        score = 0
        
        for word in query_words:
            if word in STOP_WORDS: continue
            if word in text: score += 1
        
        if score >= MIN_SCORE_THRESHOLD:
            # API Response Structure
            match_data = {
                "chunk_id": record["chunk_id"],       
                "score": score,
                "text_content": record["text_content"], 
                "metadata": record["metadata"]    
            }
            results.append(match_data)
            

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="The question to ask", nargs='?')
    args = parser.parse_args()
    q = args.query if args.query else input("Enter question: ")
    
    response = search(q)
    print(json.dumps(response, indent=2))