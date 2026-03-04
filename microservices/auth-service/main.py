from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import os
import uuid

app = FastAPI(title="Auth Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Cassandra connection
def get_cassandra_session():
    cluster = Cluster(
        [os.getenv("CASSANDRA_HOST", "cassandra")],
        port=int(os.getenv("CASSANDRA_PORT", "9042"))
    )
    session = cluster.connect()
    
    # Create keyspace if not exists
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS ent_db
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
    """)
    
    session.set_keyspace("ent_db")
    
    # Create users table
    session.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            username TEXT,
            email TEXT,
            hashed_password TEXT,
            role TEXT,
            full_name TEXT,
            created_at TIMESTAMP
        )
    """)
    
    # Create index on username
    session.execute("""
        CREATE INDEX IF NOT EXISTS ON users (username)
    """)
    
    return session

# Pydantic models
class User(BaseModel):
    username: str
    email: str
    full_name: str
    role: str  # admin, teacher, student

class UserInDB(User):
    id: uuid.UUID
    hashed_password: str
    created_at: datetime

class UserCreate(User):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    username: Optional[str] = None

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(session, username: str):
    rows = session.execute(
        "SELECT * FROM users WHERE username = %s ALLOW FILTERING",
        [username]
    )
    user = rows.one()
    if user:
        return UserInDB(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            hashed_password=user.hashed_password,
            created_at=user.created_at
        )
    return None

def authenticate_user(session, username: str, password: str):
    user = get_user_by_username(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    session = get_cassandra_session()
    user = get_user_by_username(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.get("/")
async def root():
    return {"message": "Auth Service is running", "version": "1.0.0"}

@app.post("/register", response_model=User)
async def register(user: UserCreate):
    session = get_cassandra_session()
    
    # Check if user exists
    existing_user = get_user_by_username(session, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    user_id = uuid.uuid4()
    hashed_password = get_password_hash(user.password)
    
    session.execute(
        """
        INSERT INTO users (id, username, email, hashed_password, role, full_name, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, user.username, user.email, hashed_password, user.role, user.full_name, datetime.utcnow())
    )
    
    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    session = get_cassandra_session()
    user = authenticate_user(session, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user={
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    )

@app.get("/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return User(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role
    )

@app.post("/verify-token")
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"valid": True, "username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
