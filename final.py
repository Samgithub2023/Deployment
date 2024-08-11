from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from groq import Groq
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import uvicorn

load_dotenv()

groq_api_key = os.environ.get('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set. Please set it before running the script.")

app = FastAPI()

origins = [
    "http://localhost:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    text: str
   

# Initialize conversation and memory outside of the endpoint to maintain state
memory = ConversationBufferWindowMemory(k=5)
groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")
conversation = ConversationChain(llm=groq_chat, memory=memory)

@app.post("/chat")
async def chat_endpoint(chat_input: ChatInput):
    try:
        response = conversation(chat_input.text)
        
        return {"response": response['response']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

