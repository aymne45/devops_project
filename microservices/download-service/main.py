from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
from minio import Minio
from minio.error import S3Error
from cassandra.cluster import Cluster
import os
import uuid
import requests
import io

app = FastAPI(title="Download Service", version="1.0.0")

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

# Cassandra connection
def get_cassandra_session():
    cluster = Cluster(
        [os.getenv("CASSANDRA_HOST", "cassandra")],
        port=int(os.getenv("CASSANDRA_PORT", "9042"))
    )
    session = cluster.connect()
    session.set_keyspace("ent_db")
    return session

# Pydantic models
class Course(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    teacher_username: str
    file_name: str
    file_url: str
    file_size: int
    created_at: datetime
    updated_at: datetime

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
    return {"message": "Download Service is running", "version": "1.0.0"}

@app.get("/courses", response_model=List[Course])
async def list_available_courses(authorization: str = Depends(lambda x: x)):
    # Verify authentication (students can access)
    user = await get_current_user(authorization)
    
    session = get_cassandra_session()
    rows = session.execute("SELECT * FROM courses")
    
    courses = []
    for row in rows:
        courses.append(Course(
            id=row.id,
            title=row.title,
            description=row.description,
            teacher_username=row.teacher_username,
            file_name=row.file_name,
            file_url=row.file_url,
            file_size=row.file_size,
            created_at=row.created_at,
            updated_at=row.updated_at
        ))
    
    return courses

@app.get("/courses/{course_id}", response_model=Course)
async def get_course_details(course_id: uuid.UUID, authorization: str = Depends(lambda x: x)):
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
        file_name=row.file_name,
        file_url=row.file_url,
        file_size=row.file_size,
        created_at=row.created_at,
        updated_at=row.updated_at
    )

@app.get("/courses/{course_id}/download")
async def download_course_file(course_id: uuid.UUID, authorization: str = Depends(lambda x: x)):
    # Verify authentication
    user = await get_current_user(authorization)
    
    # Get course info from Cassandra
    session = get_cassandra_session()
    row = session.execute(
        "SELECT * FROM courses WHERE id = %s",
        [course_id]
    ).one()
    
    if not row:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Extract object name from file_url
    object_name = row.file_url.split("/")[-1]
    
    # Download file from MinIO
    try:
        response = minio_client.get_object(BUCKET_NAME, object_name)
        file_data = response.read()
        response.close()
        response.release_conn()
        
        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={row.file_name}"
            }
        )
        
    except S3Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}"
        )

@app.get("/search")
async def search_courses(
    query: str,
    authorization: str = Depends(lambda x: x)
):
    # Verify authentication
    user = await get_current_user(authorization)
    
    session = get_cassandra_session()
    rows = session.execute("SELECT * FROM courses")
    
    # Simple search by title or description
    results = []
    query_lower = query.lower()
    
    for row in rows:
        if (query_lower in row.title.lower() or 
            query_lower in row.description.lower()):
            results.append(Course(
                id=row.id,
                title=row.title,
                description=row.description,
                teacher_username=row.teacher_username,
                file_name=row.file_name,
                file_url=row.file_url,
                file_size=row.file_size,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
