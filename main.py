from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from app.ollama_client import ask_ai
from app.rag_engine import ask_coach, build_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code here runs BEFORE the server starts
    print("Server starting...")
    build_vector_store()
    
    yield

app = FastAPI(title="Deep Work Coach API", lifespan=lifespan)


class UserQuery(BaseModel):
    user_text: str


@app.get("/")
def read_root():
    return {"status": "Deep Work Coach is online. Go to /docs to test."}


@app.post("/chat")
def chat_with_coach(query: UserQuery):
    # Now we use RAG instead of sending the raw question directly!
    result = ask_coach(query.user_text)

    return {
        "you_asked": query.user_text,
        "coach_response": result["answer"],
        "sources_used": result["sources"]  # Show which parts of the book were used
    }