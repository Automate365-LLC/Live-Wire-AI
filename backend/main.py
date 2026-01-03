from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import openai
from . import database
from . import ghl_api
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
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


stats = {
    "active_users": 0,
    "total_messages": 0,
    "errors_today": 0
}
dashboard_clients = set()

@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    stats["active_users"] += 1
    await broadcast_dashboard()
    try:
        while True:
            data = await websocket.receive_text()
            stats["total_messages"] += 1
            # ( chat message logic here)
            await websocket.send_text(f"You said: {data}")
            await broadcast_dashboard()
    except WebSocketDisconnect:
        stats["active_users"] -= 1
        await broadcast_dashboard()

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await websocket.accept()
    dashboard_clients.add(websocket)
    await websocket.send_json(stats)
    try:
        while True:
            await asyncio.sleep(10)  
    except WebSocketDisconnect:
        dashboard_clients.remove(websocket)

async def broadcast_dashboard():
    for client in list(dashboard_clients):
        try:
            await client.send_json(stats)
        except Exception:
            dashboard_clients.remove(client)

### This code works for testing ###

# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # Initialize the OpenAI client
# client = openai.OpenAI()

# # Open and transcribe the audio file
# with open(r"", "rb") as audio_file:
#     transcript = client.audio.transcriptions.create(
#         model="whisper-1",
#         file=audio_file,
#         response_format="text"
#     )

# # Print the transcript text
# print(transcript)