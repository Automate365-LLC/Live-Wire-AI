from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
#from database import save_conversation
#import os
import logging
from typing import List, Dict, Any

#Custom Modules
from retrieve import retrieve_chunks
from card_generator import generate_cards
import ghl_api

# Load environment variables
load_dotenv()
#openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure Logging (Standardized format)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

#Data Models:Pydantic to ensure API inputs are valid
class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class SearchResponse(BaseModel):
    count: int
    results: List[Dict[str, Any]]

# Retrieval API Endpoint
@app.post("/retrieve", response_model=SearchResponse)
async def manual_search(request: SearchRequest):
    """
    Search the local vector database for relevant playbook chunks.
    Used for debugging and manual testing.
    """
    try:
        logger.info(f"🔎 API Search Query: '{request.query}'")
        results = retrieve_chunks(request.query, top_k=request.top_k)
        
        return {
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Search API Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
# Real Time WebSocket Endpoint     
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint:
    - Receives transcript text from frontend
    - Retrieves top-k chunks
    - Generates grounded cards
    - Returns JSON to frontend
    """
    await websocket.accept()
    logger.info(f"✅ WebSocket connected: {websocket.client}")

    try:
        while True:
            # 1. RECEIVE (Audio Transcript)
            data = await websocket.receive_text()
            logger.info(f" Received: {data}")

            # Dummy client info (replace with real logic later)
            client_info = ghl_api.fetch_client_data("client_id")

            # 2. RETRIEVE 
            # Query the vector DB using your validated logic
            relevant_chunks = retrieve_chunks(data)
            logger.info(f" Retrieved {len(relevant_chunks)} chunks for context")

            # 3. GENERATE CARDS
            #This gaurantees zero hallucination
            cards = generate_cards(data, relevant_chunks)

            # 4. RESPOND
            # CRITICAL: Send JSON object, not raw text strings
            await websocket.send_json(cards)
            logger.info(f" Sent {len(cards)} cards to client")


        """# TODO: Update database.py to handle JSON card data
         # Save in MongoDB
            save_conversation("client_id", response_text)"""

        
    except WebSocketDisconnect:
        logger.info(" Client disconnected")
    except Exception as e:
        logger.error(f" WebSocket Critical Error: {e}", exc_info=True)
        # Fail gracefully so the UI doesn't hang
        await websocket.send_json([{
            "type": "error",
            "body": "System processing error. Please reconnect."
        }])
        await websocket.close()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "LiveWire AI Backend",
        "modules": {
            "retrieval": "active",
            "grounding": "strict (v0.1)"
        }
    } 

""" 
@app.get("/")
def read_root():
    return {"message": "LiveWire AI Backend is running"}
    await websocket.accept() # Tells the server to accept the connection from the frontend
    while True:
        data = await websocket.receive_text() # data = Audio text
        

        client_info = ghl_api.fetch_client_data("client_id") # Will have to update with actual info
        
        ai_response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant."},
                {"role": "user", "content": f"Live conversation: {data}, Previous data: {client_info}"}
            ]
        )

        # ^^^ Will need to do some prompt engineering once the application is setup

        await websocket.send_text(ai_response["choices"][0]["message"]["content"]) # Sends the AI's response back to the frontend in real time.
"""