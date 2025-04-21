#!/bin/bash
set -e

echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

echo "Waiting for Ollama to be ready..."
for i in {1..30}; do
  echo "Checking Ollama availability... ($i/30)"
  if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama is ready!"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "Timeout waiting for Ollama to start"
    exit 1
  fi
  sleep 2
done

echo "Starting FastAPI application..."
exec uvicorn llm_service:app --host 0.0.0.0 --port 8000