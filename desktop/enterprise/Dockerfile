FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -m -s /bin/bash mia-agi

# Set working directory
WORKDIR /opt/mia-enterprise-agi

# Copy application files
COPY . .

# Install Python dependencies
RUN python3 -m pip install -r requirements.txt

# Install Node.js dependencies
RUN npm install

# Set permissions
RUN chown -R mia-agi:mia-agi /opt/mia-enterprise-agi

# Switch to application user
USER mia-agi

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python3", "mia_enterprise_launcher.py", "--docker"]
