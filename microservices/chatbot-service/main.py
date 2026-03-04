from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from cassandra.cluster import Cluster
import os
import requests
import json

app = FastAPI(title="Chatbot Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")

# Auth service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

# Cassandra connection
def get_cassandra_session():
    cluster = Cluster(
        [os.getenv("CASSANDRA_HOST", "cassandra")],
        port=int(os.getenv("CASSANDRA_PORT", "9042"))
    )
    session = cluster.connect()
    session.set_keyspace("ent_db")
    
    # Create chat history table
    session.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id UUID PRIMARY KEY,
            username TEXT,
            question TEXT,
            answer TEXT,
            timestamp TIMESTAMP
        )
    """)
    
    # Create index on username
    session.execute("""
        CREATE INDEX IF NOT EXISTS ON chat_history (username)
    """)
    
    return session

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    context_used: bool

class ChatHistory(BaseModel):
    id: str
    question: str
    answer: str
    timestamp: datetime

# Helper functions
async def verify_token(token: str):
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/verify-token",
            params={"token": token}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth service error: {str(e)}")

async def get_current_user(token: str):
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    token = token.replace("Bearer ", "")
    return await verify_token(token)

def get_courses_context():
    """Get all courses information to provide context to the chatbot"""
    try:
        session = get_cassandra_session()
        rows = session.execute("SELECT title, description, teacher_username FROM courses")
        
        courses_info = []
        for row in rows:
            courses_info.append(
                f"Cours: {row.title}\n"
                f"Description: {row.description}\n"
                f"Enseignant: {row.teacher_username}"
            )
        
        if courses_info:
            return "Voici la liste des cours disponibles:\n\n" + "\n\n".join(courses_info)
        return "Aucun cours disponible pour le moment."
    except Exception as e:
        print(f"Error getting courses context: {e}")
        return ""

def query_ollama(prompt: str, system_prompt: str = None) -> str:
    """Query Ollama API with Llama 3 model"""
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Désolé, je n'ai pas pu générer une réponse.")
        else:
            return "Erreur de connexion au service d'IA."
    
    except requests.exceptions.RequestException as e:
        print(f"Ollama request error: {e}")
        return "Le service d'IA n'est pas disponible actuellement."

# Routes
@app.get("/")
async def root():
    return {"message": "Chatbot Service is running", "version": "1.0.0"}

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authorization: str = Header(None)
):
    # Verify authentication
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    user = await get_current_user(authorization)
    
    # Build system prompt with ENT context
    system_prompt = """Tu es un assistant intelligent pour un Espace Numérique de Travail (ENT) éducatif.
Tu aides les étudiants et enseignants avec leurs questions sur les cours, l'organisation, et le système.
Réponds de manière claire, concise et professionnelle en français.
"""
    
    # Add courses context if relevant
    courses_context = get_courses_context()
    
    # Build the complete prompt
    if request.context:
        full_prompt = f"{courses_context}\n\nContexte additionnel: {request.context}\n\nQuestion: {request.question}"
    else:
        full_prompt = f"{courses_context}\n\nQuestion: {request.question}"
    
    # Query Ollama
    answer = query_ollama(full_prompt, system_prompt)
    
    # Save to chat history
    try:
        session = get_cassandra_session()
        import uuid
        chat_id = uuid.uuid4()
        
        session.execute(
            """
            INSERT INTO chat_history (id, username, question, answer, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (chat_id, user["username"], request.question, answer, datetime.utcnow())
        )
    except Exception as e:
        print(f"Error saving chat history: {e}")
    
    return ChatResponse(
        answer=answer,
        context_used=bool(courses_context)
    )

@app.get("/history", response_model=List[ChatHistory])
async def get_chat_history(
    limit: int = 10,
    authorization: str = Depends(lambda x: x)
):
    # Verify authentication
    user = await get_current_user(authorization)
    
    session = get_cassandra_session()
    
    # Get user's chat history
    rows = session.execute(
        "SELECT * FROM chat_history WHERE username = %s ALLOW FILTERING LIMIT %s",
        [user["username"], limit]
    )
    
    history = []
    for row in rows:
        history.append(ChatHistory(
            id=str(row.id),
            question=row.question,
            answer=row.answer,
            timestamp=row.timestamp
        ))
    
    return history

@app.delete("/history")
async def clear_chat_history(authorization: str = Depends(lambda x: x)):
    # Verify authentication
    user = await get_current_user(authorization)
    
    session = get_cassandra_session()
    
    # Get all chat IDs for this user
    rows = session.execute(
        "SELECT id FROM chat_history WHERE username = %s ALLOW FILTERING",
        [user["username"]]
    )
    
    # Delete each chat
    for row in rows:
        session.execute(
            "DELETE FROM chat_history WHERE id = %s",
            [row.id]
        )
    
    return {"message": "Chat history cleared"}

@app.get("/health")
async def health_check():
    """Check if Ollama service is available"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "ollama": "connected"}
        else:
            return {"status": "degraded", "ollama": "error"}
    except Exception as e:
        return {"status": "degraded", "ollama": "unavailable", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
