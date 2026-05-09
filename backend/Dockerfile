# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pypdf sentence-transformers

# Copy the rest of the backend code
COPY backend ./backend
COPY scripts ./scripts
COPY data ./data
COPY run_backend.py .

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "run_backend.py"]
