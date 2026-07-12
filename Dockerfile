FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data/memory

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "nebula_writer.main:app", "--host", "0.0.0.0", "--port", "8000"]
