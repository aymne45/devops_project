from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from minio import Minio
from minio.error import S3Error
from cassandra.cluster import Cluster
import os
import uuid
import requests

app = FastAPI(title="File Management Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = "ent-courses"

# Auth service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Ensure bucket exists
def ensure_bucket():
    try:
        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
    except S3Error as e:
        print(f"Error creating bucket: {e}")

# Cassandra connection
def get_cassandra_session():
    cluster = Cluster(
        [os.getenv("CASSANDRA_HOST", "cassandra")],
        port=int(os.getenv("CASSANDRA_PORT", "9042"))
    )
    session = cluster.connect()
    session.set_keyspace("ent_db")
    
    # Create courses table
    session.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id UUID PRIMARY KEY,
            title TEXT,
            description TEXT,
            teacher_username TEXT,
            filiere TEXT,
            file_name TEXT,
            file_url TEXT,
            file_size BIGINT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    
    # Create index on teacher
    session.execute("""
        CREATE INDEX IF NOT EXISTS ON courses (teacher_username)
    """)
    
    return session

# Pydantic models
class Course(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    teacher_username: str
    filiere: str
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

class CourseCreate(BaseModel):
    title: str
    description: str

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

# Routes
@app.get("/")
async def root():
    return {"message": "File Management Service is running", "version": "1.0.0"}

@app.post("/courses", response_model=Course)
async def create_course(
    title: str = Form(...),
    description: str = Form(...),
    filiere: str = Form(...),
    teacher_username: str = Form(...),
    file: Optional[UploadFile] = File(None),
    authorization: str = Header(None)
):
    # Verify user is a teacher
    user = await get_current_user(authorization)
    if user["role"] != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create courses"
        )
    
    file_url = None
    file_name = None
    file_size = 0
    
    # Upload file to MinIO only if provided
    if file:
        # Ensure bucket exists
        ensure_bucket()
        
        # Generate unique file name
        file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        
        try:
            file_content = await file.read()
            file_size = len(file_content)
            
            minio_client.put_object(
                BUCKET_NAME,
                unique_filename,
                data=file_content,
                length=file_size,
                content_type=file.content_type or "application/octet-stream"
            )
            
            file_url = f"/api/download/courses/{unique_filename}"
            file_name = file.filename
            
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading file: {str(e)}"
            )
    
    # Save metadata to Cassandra
    session = get_cassandra_session()
    course_id = uuid.uuid4()
    created_at = datetime.utcnow()
    
    session.execute(
        """
        INSERT INTO courses (id, title, description, teacher_username, filiere, file_name, 
                           file_url, file_size, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (course_id, title, description, teacher_username, filiere, file_name,
         file_url, file_size, created_at, created_at)
    )
    
    return Course(
        id=course_id,
        title=title,
        description=description,
        teacher_username=teacher_username,
        filiere=filiere,
        file_name=file_name,
        file_url=file_url,
        file_size=file_size,
        created_at=created_at,
        updated_at=created_at
    )

@app.get("/courses", response_model=List[Course])
async def list_courses(authorization: str = Header(None)):
    # Verify authentication
    user = await get_current_user(authorization)
    
    session = get_cassandra_session()
    
    # If teacher, show only their courses
    if user["role"] == "teacher":
        rows = session.execute(
            "SELECT * FROM courses WHERE teacher_username = %s ALLOW FILTERING",
            [user["username"]]
        )
    else:
        # Students and admins see all courses
        rows = session.execute("SELECT * FROM courses")
    
    courses = []
    for row in rows:
        courses.append(Course(
            id=row.id,
            title=row.title,
            description=row.description,
            teacher_username=row.teacher_username,
            filiere=row.filiere,
            file_name=row.file_name,
            file_url=row.file_url,
            file_size=row.file_size,
            created_at=row.created_at,
            updated_at=row.updated_at
        ))
    
    return courses

@app.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: uuid.UUID, authorization: str = Header(None)):
    # Verify authentication
    user = await get_current_user(authorization)
    
    session = get_cassandra_session()
    row = session.execute(
        "SELECT * FROM courses WHERE id = %s",
        [course_id]
    ).one()
    
    if not row:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return Course(
        id=row.id,
        title=row.title,
        description=row.description,
        teacher_username=row.teacher_username,
        filiere=row.filiere,
        file_name=row.file_name,
        file_url=row.file_url,
        file_size=row.file_size,
        created_at=row.created_at,
        updated_at=row.updated_at
    )

@app.delete("/courses/{course_id}")
async def delete_course(course_id: uuid.UUID, authorization: str = Header(None)):
    # Verify user is a teacher or admin
    user = await get_current_user(authorization)
    if user["role"] not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can delete courses"
        )
    
    session = get_cassandra_session()
    
    # Get course info
    row = session.execute(
        "SELECT * FROM courses WHERE id = %s",
        [course_id]
    ).one()
    
    if not row:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if teacher owns the course
    if user["role"] == "teacher" and row.teacher_username != user["username"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own courses"
        )
    
    # Delete from MinIO
    try:
        object_name = row.file_url.split("/")[-1]
        minio_client.remove_object(BUCKET_NAME, object_name)
    except S3Error as e:
        print(f"Error deleting file from MinIO: {e}")
    
    # Delete from Cassandra
    session.execute("DELETE FROM courses WHERE id = %s", [course_id])
    
    return {"message": "Course deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
