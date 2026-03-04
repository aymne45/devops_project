#!/bin/bash

# Script pour créer un utilisateur admin par défaut

echo "Waiting for auth service to be ready..."

# Wait for auth service to be ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8001/ > /dev/null 2>&1; then
        echo "Auth service is ready!"
        break
    fi
    echo "Waiting for auth service... (attempt $((attempt+1))/$max_attempts)"
    sleep 2
    attempt=$((attempt+1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "Error: Auth service did not become ready in time"
    exit 1
fi

echo ""
echo "Creating default admin user..."

# Create admin user via API
curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@ent.com",
    "password": "admin123",
    "full_name": "Administrateur",
    "role": "admin"
  }'

echo ""
echo "Default admin user created!"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "Creating default teacher user..."

curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teacher",
    "email": "teacher@ent.com",
    "password": "teacher123",
    "full_name": "Enseignant ENT",
    "role": "teacher"
  }'

echo ""
echo "Default teacher user created!"
echo "Username: teacher"
echo "Password: teacher123"
echo ""
echo "Creating default student user..."

curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student",
    "email": "student@ent.com",
    "password": "student123",
    "full_name": "Étudiant ENT",
    "role": "student"
  }'

echo ""
echo "Default student user created!"
echo "Username: student"
echo "Password: student123"
