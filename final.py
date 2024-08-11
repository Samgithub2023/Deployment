from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from groq import Groq
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import uvicorn

load_dotenv()

groq_api_key = os.environ.get('GROQ_API_KEY')
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set. Please set it before running the script.")

app = FastAPI()

class ChatInput(BaseModel):
    text: str
    model: str = "mixtral-8x7b-32768"
    memory_length: int = 5

# Initialize conversation and memory outside of the endpoint to maintain state
memory = ConversationBufferWindowMemory(k=5)
groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")
conversation = ConversationChain(llm=groq_chat, memory=memory)

@app.post("/chat")
async def chat_endpoint(chat_input: ChatInput):
    try:
        # Update conversation parameters if they've changed
        if chat_input.model != groq_chat.model_name:
            groq_chat.model_name = chat_input.model
            conversation.llm = groq_chat

        if chat_input.memory_length != memory.k:
            memory.k = chat_input.memory_length

        # Get response from the conversation chain
        response = conversation(chat_input.text)
        
        return {"response": response['response']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

