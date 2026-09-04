FROM python:3.11-slim

# Prevent Python from writing pyc files to disc & buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install curl for healthcheck if needed
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY config/ ./config/
COPY data/ ./data/
COPY dashboard/ ./dashboard/
COPY src/ ./src/
COPY Docs/ ./Docs/
COPY entrypoint.sh .
COPY server.py .
COPY README.md .
RUN chmod +x entrypoint.sh

# Expose default port
EXPOSE 8000

# Start production server
ENTRYPOINT ["python", "server.py"]
