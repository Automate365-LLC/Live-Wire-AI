from pymongo import MongoClient

# Connect to MongoDB (edit this if your URI is different)
client = MongoClient("mongodb://localhost:27017")

db = client["AI_Popups"]
conversations = db["Conversations"]

def save_conversation(client_id, text):
    conversations.insert_one({"client_id": client_id, "conversation": text})

def get_past_conversations(client_id):
    return list(conversations.find({"client_id": client_id}, {"_id": 0}))
