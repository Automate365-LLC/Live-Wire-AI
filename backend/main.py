from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
from database import save_conversation
import openai
import os
import ghl_api

# Load environment variables (like your OpenAI API key)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket connection accepted")

    while True:
        try:
            data = await websocket.receive_text()
            print(f"📥 Received from user: {data}")

            # Dummy client info (replace with real logic later)
            client_info = ghl_api.fetch_client_data("client_id")

            # Call OpenAI's GPT-4o model
            ai_response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an AI assistant."},
                    {"role": "user", "content": f"Live conversation: {data}, Previous data: {client_info}"}
                ]
            )

            # Get the reply
            response_text = ai_response.choices[0].message.content
            print(f"🧠 GPT response: {response_text}")

            # Send back to frontend
            await websocket.send_text(response_text)

            # Save in MongoDB
            save_conversation("client_id", response_text)

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"❌ WebSocket error: {e}")
            await websocket.close()
            break

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
