CREATE KEYSPACE IF NOT EXISTS ent_db 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE ent_db;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    hashed_password TEXT,
    role TEXT,
    full_name TEXT,
    filiere TEXT,
    created_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS users_username_idx ON users (username);

CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY,
    title TEXT,
    description TEXT,
    teacher_username TEXT,
    file_name TEXT,
    file_url TEXT,
    file_size BIGINT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS courses_teacher_idx ON courses (teacher_username);

CREATE TABLE IF NOT EXISTS chat_history (
    id UUID PRIMARY KEY,
    username TEXT,
    question TEXT,
    answer TEXT,
    timestamp TIMESTAMP
);

CREATE INDEX IF NOT EXISTS chat_history_username_idx ON chat_history (username);
