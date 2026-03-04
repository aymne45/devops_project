#!/bin/bash

# Script pour télécharger le modèle Llama 3 dans Ollama

echo "Pulling Llama 3 model in Ollama..."

docker exec -it ent-ollama ollama pull llama3

echo "Llama 3 model installed successfully!"
echo "You can now use the chatbot service."
