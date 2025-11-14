FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install package
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 opsagent && chown -R opsagent:opsagent /app
USER opsagent

# Expose API port
EXPOSE 18080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:18080/health || exit 1

# Run the application
CMD ["python", "-m", "src.main", "--config", "config/config.yaml"]
