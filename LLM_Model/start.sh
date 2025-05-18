#!/bin/bash
set -e

echo "Checking for mounted model files..."
if [ -z "$(ls -A /root/.ollama 2>/dev/null)" ]; then
    echo "WARNING: No model files found in the mounted volume!"
    echo "Make sure you've correctly mounted the model directory to /root/.ollama"
else
    echo "Model files detected in mounted volume."
    ls -la /root/.ollama
fi

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

# Verify if the model is available through Ollama
echo "Checking for available models:"
ollama list

echo "Starting FastAPI application..."
exec uvicorn llm_service:app --host 0.0.0.0 --port 8000