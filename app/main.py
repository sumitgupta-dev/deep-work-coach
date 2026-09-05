from fastapi import FastAPI
from pydantic import BaseModel
from app.ollama_client import ask_ai

app = FastAPI(title="Deep Work Coach API")

class UserQuery(BaseModel):
    user_text: str

@app.get("/")
def read_root():
    return {"status": "Deep Work Coach is online. Go to /docs to test."}

@app.post("/chat")
def chat_with_coach(query: UserQuery):
    # For now, we just pass the text directly to the AI.
    # Later, we will intercept this to search the PDF books first!
    
    ai_response = ask_ai(query.user_text)
    
    return {
        "you_asked": query.user_text,
        "coach_response": ai_response
    }