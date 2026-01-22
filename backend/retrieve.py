import json
import os
import argparse
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging


# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "local_vector_db.json")
INDEX_FILE = os.path.join(BASE_DIR, "vector_index.bin")

# Grounding Policy
# L2 Distance: Lower is better. 0 = Exact Match.
# Scores > 1.5 usually mean the text is unrelated.
DISTANCE_THRESHOLD = 1.5 

# Logging goes to stderr by default, so it will NOT interfere with
# JSON output sent to stdout (important for WS3 integration)
logging.basicConfig(
    level=logging.INFO,  # change to DEBUG when tuning
    format="%(asctime)s [WS4-RETRIEVAL] %(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)

# Global Resources
_model = None
_index = None
_db = None

def get_resources():
    """
    load and cache the embedding model, FAISS index,
    and vector database.
    """
    global _model, _index, _db

    if _model is None:
        logger.info("Loading sentence transformer model")
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    if _index is None and os.path.exists(INDEX_FILE):
        logger.info("Loading FAISS index")
        _index = faiss.read_index(INDEX_FILE)

    if _db is None and os.path.exists(DB_FILE):
        logger.info("Loading vector database")
        with open(DB_FILE, "r", encoding="utf-8") as f:
            _db = json.load(f)

    return _model, _index, _db


def search(query, top_k=3):
    """
    Retrieval API and Grounding Policy Enforcement
    Returns:
        A list of grounded chunks.
        If confidence is low, returns an empty list
        so downstream systems can trigger a fallback
    """
    model, index, db = get_resources()

    # Safety check: system not initialized correctly
    if index is None or db is None:
        logger.warning("Search aborted: index or database not loaded")
        return []

    # Encode query into vector space
    query_vector = model.encode([query])
    logger.info("Query encoded successfully")

    # Perform vector search
    D, I = index.search(np.array(query_vector).astype("float32"), top_k)


    # Query level policy check
    # Check the best (lowest) score
    # D[0][0] is the distance of the closest match.
    if D.size == 0 or len(D[0]) == 0:
        logger.warning("No search results returned from FAISS")
        return []

    best_score = float(D[0][0])
    logger.info(f"Best match distance: {best_score:.4f}")
    # Policy- If even the best match is too far away (>= 1.5), 
    # we declare Low Confidence and return nothing
    if best_score >= DISTANCE_THRESHOLD:
        logger.warning(
            f"Query rejected by grounding policy (best_score={best_score:.4f})")
        return []

    # Filter Results
    results = []
    for i, idx in enumerate(I[0]):
        if idx == -1: continue # FAISS filler
        
        score = float(D[0][i])

        # Chunk-level safety (Double check 2nd/3rd results)
        if score >= DISTANCE_THRESHOLD:
            continue

        record = db[idx]
        results.append({
            "chunk_id": record["chunk_id"],
            "score": score,
            "text_content": record["text_content"],
            "metadata": record["metadata"]
        })
        
    logger.info(f"Returning {len(results)} grounded results")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="The question to ask", nargs='?')
    args = parser.parse_args()
    q = args.query if args.query else input("Enter question: ")
    
    response = search(q)
    print(json.dumps(response, indent=2))