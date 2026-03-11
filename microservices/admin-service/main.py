from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext
from cassandra.cluster import Cluster
import os
import uuid
import requests

app = FastAPI(title="Admin Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cassandra connection
def get_cassandra_session():
    cluster = Cluster(
        [os.getenv("CASSANDRA_HOST", "cassandra")],
        port=int(os.getenv("CASSANDRA_PORT", "9042"))
    )
    session = cluster.connect()
    session.set_keyspace("ent_db")
    
    # Create events table if not exists
    session.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id UUID PRIMARY KEY,
            title TEXT,
            description TEXT,
            event_type TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            teacher_username TEXT,
            created_at TIMESTAMP
        )
    """)
    
    session.execute("""
        CREATE INDEX IF NOT EXISTS ON events (teacher_username)
    """)
    
    # Create assignments table if not exists
    session.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id UUID PRIMARY KEY,
            title TEXT,
            description TEXT,
            deadline TIMESTAMP,
            filiere TEXT,
            teacher_username TEXT,
            status TEXT,
            created_at TIMESTAMP
        )
    """)
    
    session.execute("""
        CREATE INDEX IF NOT EXISTS ON assignments (teacher_username)
    """)
    
    return session

# Pydantic models
class User(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    full_name: str
    role: str
    created_at: datetime

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None

class Stats(BaseModel):
    total_users: int
    total_students: int
    total_teachers: int
    total_admins: int
    total_courses: int

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
    user = await verify_token(token)
    
    # Check if user is admin
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

def get_password_hash(password):
    return pwd_context.hash(password)

# Routes
@app.get("/")
async def root():
    return {"message": "Admin Service is running", "version": "1.0.0"}

@app.get("/stats", response_model=Stats)
async def get_stats(authorization: str = Header(None)):
    # Verify admin
    await get_current_user(authorization)
    
    session = get_cassandra_session()
    
    # Count users by role
    users = session.execute("SELECT role FROM users")
    total_users = 0
    total_students = 0
    total_teachers = 0
    total_admins = 0
    
    for user in users:
        total_users += 1
        if user.role == "student":
            total_students += 1
        elif user.role == "teacher":
            total_teachers += 1
        elif user.role == "admin":
            total_admins += 1
    
    # Count courses
    courses = session.execute("SELECT COUNT(*) FROM courses")
    total_courses = list(courses)[0].count if courses else 0
    
    return Stats(
        total_users=total_users,
        total_students=total_students,
        total_teachers=total_teachers,
        total_admins=total_admins,
        total_courses=total_courses
    )

@app.get("/users", response_model=List[User])
async def list_users(
    role: Optional[str] = None,
    authorization: str = Header(None)
):
    # Verify admin
    await get_current_user(authorization)
    
    session = get_cassandra_session()
    
    if role:
        rows = session.execute(
            "SELECT * FROM users WHERE role = %s ALLOW FILTERING",
            [role]
        )
    else:
        rows = session.execute("SELECT * FROM users")
    
    users = []
    for row in rows:
        users.append(User(
            id=row.id,
            username=row.username,
            email=row.email,
            full_name=row.full_name,
            role=row.role,
            created_at=row.created_at
        ))
    
    return users

@app.post("/users", response_model=User)
async def create_user(
    user: UserCreate,
    authorization: str = Header(None)
):
    # Verify admin
    await get_current_user(authorization)
    
    session = get_cassandra_session()
    
    # Check if username exists
    existing = session.execute(
        "SELECT username FROM users WHERE username = %s ALLOW FILTERING",
        [user.username]
    ).one()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create user
    user_id = uuid.uuid4()
    hashed_password = get_password_hash(user.password)
    created_at = datetime.utcnow()
    
    session.execute(
        """
        INSERT INTO users (id, username, email, hashed_password, role, full_name, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, user.username, user.email, hashed_password, user.role, user.full_name, created_at)
    )
    
    return User(
        id=user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        created_at=created_at
    )

@app.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: uuid.UUID,
    authorization: str = Header(None)
):
    # Verify admin
    await get_current_user(authorization)
    
    session = get_cassandra_session()
    row = session.execute(
        "SELECT * FROM users WHERE id = %s",
        [user_id]
    ).one()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        id=row.id,
        username=row.username,
        email=row.email,
        full_name=row.full_name,
        role=row.role,
        created_at=row.created_at
    )

@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    authorization: str = Header(None)
):
    # Verify admin
    await get_current_user(authorization)
    
    session = get_cassandra_session()
    
    # Check if user exists
    existing = session.execute(
        "SELECT * FROM users WHERE id = %s",
        [user_id]
    ).one()
    
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    updates = []
    params = []
    
    if user_update.email:
        updates.append("email = %s")
        params.append(user_update.email)
    
    if user_update.full_name:
        updates.append("full_name = %s")
        params.append(user_update.full_name)
    
    if user_update.role:
        updates.append("role = %s")
        params.append(user_update.role)
    
    if user_update.password:
        updates.append("hashed_password = %s")
        params.append(get_password_hash(user_update.password))
    
    if updates:
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        session.execute(query, params)
    
    # Get updated user
    row = session.execute(
        "SELECT * FROM users WHERE id = %s",
        [user_id]
    ).one()
    
    return User(
        id=row.id,
        username=row.username,
        email=row.email,
        full_name=row.full_name,
        role=row.role,
        created_at=row.created_at
    )

# Event models
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: str  # cours, examen, tp, td
    start_date: datetime
    end_date: datetime

class Event(BaseModel):
    id: str
    title: str
    description: Optional[str]
    event_type: str
    start_date: datetime
    end_date: datetime
    teacher_username: str
    created_at: datetime

# Event endpoints
@app.post("/events", response_model=Event)
async def create_event(event: EventCreate, username: str):
    """Create a new calendar event"""
    session = get_cassandra_session()
    
    event_id = uuid.uuid4()
    now = datetime.utcnow()
    
    session.execute("""
        INSERT INTO events (id, title, description, event_type, start_date, end_date, teacher_username, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (event_id, event.title, event.description, event.event_type, event.start_date, event.end_date, username, now))
    
    return Event(
        id=str(event_id),
        title=event.title,
        description=event.description,
        event_type=event.event_type,
        start_date=event.start_date,
        end_date=event.end_date,
        teacher_username=username,
        created_at=now
    )

@app.get("/events/{username}", response_model=List[Event])
async def get_teacher_events(username: str):
    """Get all events for a teacher"""
    session = get_cassandra_session()
    
    rows = session.execute(
        "SELECT * FROM events WHERE teacher_username = %s ALLOW FILTERING",
        [username]
    )
    
    events = []
    for row in rows:
        events.append(Event(
            id=str(row.id),
            title=row.title,
            description=row.description,
            event_type=row.event_type,
            start_date=row.start_date,
            end_date=row.end_date,
            teacher_username=row.teacher_username,
            created_at=row.created_at
        ))
    
    return events

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """Delete an event"""
    session = get_cassandra_session()
    
    session.execute(
        "DELETE FROM events WHERE id = %s",
        [uuid.UUID(event_id)]
    )
    
    return {"message": "Event deleted successfully"}

# Assignment models
class AssignmentCreate(BaseModel):
    title: str
    description: str
    deadline: datetime
    filiere: str
    status: str = "active"

class Assignment(BaseModel):
    id: str
    title: str
    description: str
    deadline: datetime
    filiere: str
    teacher_username: str
    status: str
    created_at: datetime

@app.post("/assignments", response_model=Assignment)
async def create_assignment(assignment: AssignmentCreate, username: str):
    """Create a new assignment"""
    session = get_cassandra_session()
    
    assignment_id = uuid.uuid4()
    now = datetime.utcnow()
    
    session.execute(
        """
        INSERT INTO assignments (id, title, description, deadline, filiere, teacher_username, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (assignment_id, assignment.title, assignment.description, assignment.deadline,
         assignment.filiere, username, assignment.status, now)
    )
    
    return Assignment(
        id=str(assignment_id),
        title=assignment.title,
        description=assignment.description,
        deadline=assignment.deadline,
        filiere=assignment.filiere,
        teacher_username=username,
        status=assignment.status,
        created_at=now
    )

@app.get("/assignments/{username}", response_model=List[Assignment])
async def get_teacher_assignments(username: str):
    """Get all assignments for a teacher"""
    session = get_cassandra_session()
    
    rows = session.execute(
        "SELECT * FROM assignments WHERE teacher_username = %s ALLOW FILTERING",
        [username]
    )
    
    assignments = []
    for row in rows:
        assignments.append(Assignment(
            id=str(row.id),
            title=row.title,
            description=row.description,
            deadline=row.deadline,
            filiere=row.filiere,
            teacher_username=row.teacher_username,
            status=row.status,
            created_at=row.created_at
        ))
    
    return assignments

@app.delete("/assignments/{assignment_id}")
async def delete_assignment(assignment_id: str):
    """Delete an assignment"""
    session = get_cassandra_session()
    
    session.execute(
        "DELETE FROM assignments WHERE id = %s",
        [uuid.UUID(assignment_id)]
    )
    
    return {"message": "Assignment deleted successfully"}

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    authorization: str = Header(None)
):
    # Verify admin
    admin = await get_current_user(authorization)
    
    session = get_cassandra_session()
    
    # Check if user exists
    existing = session.execute(
        "SELECT * FROM users WHERE id = %s",
        [user_id]
    ).one()
    
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-deletion
    if existing.username == admin["username"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Delete user
    session.execute("DELETE FROM users WHERE id = %s", [user_id])
    
    return {"message": "User deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
