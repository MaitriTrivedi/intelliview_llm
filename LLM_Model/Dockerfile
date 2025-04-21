FROM ubuntu:22.04

WORKDIR /app

# Set non-interactive installation mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and needed dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    wget \
    git \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY llm_service.py .
COPY start.sh .

# Make the startup script executable
RUN chmod +x start.sh

# Install Ollama and download the model during build time
RUN curl -fsSL https://ollama.com/install.sh | sh && \
    mkdir -p /root/.ollama && \
    (ollama serve > /var/log/ollama.log 2>&1 &) && \
    echo "Waiting for Ollama server to start..." && \
    for i in $(seq 1 30); do \
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then \
            echo "Ollama server is running, pulling model..." && \
            ollama pull mistral && \
            echo "Model pulled successfully" && \
            pkill -f "ollama serve" && \
            exit 0; \
        fi; \
        echo "Waiting... $i/30"; \
        sleep 3; \
    done && \
    echo "Failed to start Ollama server in time" && \
    cat /var/log/ollama.log && \
    exit 1

# Expose the port
EXPOSE 8000

# Use the start script as the entrypoint
ENTRYPOINT ["/app/start.sh"]