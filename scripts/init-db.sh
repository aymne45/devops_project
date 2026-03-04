#!/bin/bash

# Script d'initialisation de la base de données Cassandra

echo "Waiting for Cassandra to be ready..."

# Wait for Cassandra to be healthy
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec ent-cassandra cqlsh -e "DESCRIBE CLUSTER" > /dev/null 2>&1; then
        echo "Cassandra is ready!"
        break
    fi
    echo "Waiting for Cassandra... (attempt $((attempt+1))/$max_attempts)"
    sleep 2
    attempt=$((attempt+1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "Error: Cassandra did not become ready in time"
    exit 1
fi

echo "Creating keyspace and tables..."

# Copy schema file to container and execute
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
docker cp "$SCRIPT_DIR/schema.cql" ent-cassandra:/tmp/schema.cql
docker exec ent-cassandra cqlsh -f /tmp/schema.cql

echo "Database initialization complete!"
