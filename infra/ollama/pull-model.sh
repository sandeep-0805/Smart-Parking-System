#!/bin/bash
set -e

export OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
MODEL="${OLLAMA_MODEL:-llama3.2:3b}"

echo "=== SmartParking Ollama Init ==="
echo "Host : ${OLLAMA_HOST}"
echo "Model: ${MODEL}"

# Wait for Ollama to be ready
echo "Waiting for Ollama..."
until ollama list > /dev/null 2>&1; do
    echo "  ...not ready, retrying in 3s"
    sleep 3
done
echo "Ollama is ready."

# Check if model already exists
if ollama list | grep -q "${MODEL}"; then
    echo "Model '${MODEL}' already pulled. Done."
    exit 0
fi

# Pull the model
echo "Pulling model '${MODEL}'... (this may take several minutes)"
ollama pull "${MODEL}"
echo "Model '${MODEL}' pulled successfully."
