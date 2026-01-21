import json
import os
import argparse

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "local_vector_db.json")

# Guardrail: Confidence Threshold
MIN_SCORE_THRESHOLD = 1 

def load_db():
    if not os.path.exists(DB_FILE):
        print("Database not found. Run ingest.py first!")
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def search(query):
    # Query Builder: Simple text input for v0
    db = load_db()
    print(f"--- SEARCHING FOR: '{query}' ---")
    
    results = []
    query_words = query.lower().split()

    # Search Logic Keyword Matching
    # Common words that don't add meaning
    STOP_WORDS = {"what", "is", "the", "a", "an", "of", "to", "in", "it", "does"}

    for record in db:
        text = record['text'].lower()
        score = 0
        
        for word in query_words:
            # OPTIMIZATION: Skip the word if it is a "Stop Word"
            if word in STOP_WORDS:
                continue
                
            if word in text:
                score += 1
        
        if score >= MIN_SCORE_THRESHOLD:
            results.append((score, record))

    # Sort by highest score
    results.sort(key=lambda x: x[0], reverse=True)

    if results:
        best_record = results[0][1]
        print(f"FOUND MATCH (Score: {results[0][0]})")
        print(f"   Source: {best_record['metadata']['source']}")
        print(f"   Answer: {best_record['text']}")
    else:
        #No-source behavior
        print(" No matching answer found in playbook.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="The question to ask", nargs='?')
    args = parser.parse_args()

    if args.query:
        search(args.query)
    else:
        user_input = input("Enter a question: ")
        search(user_input)