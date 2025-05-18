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

# Install Ollama without downloading the model
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create ollama directory structure but don't download models
RUN mkdir -p /root/.ollama/models/blobs

# Expose the port
EXPOSE 8000

# Use the start script as the entrypoint
ENTRYPOINT ["/app/start.sh"]