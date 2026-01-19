FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including build tools for Python packages
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    gcc \
    g++ \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding models to bake them into the image
# This saves time on first run
RUN python -c "from sentence_transformers import SentenceTransformer; \
    print('Downloading BAAI/bge-m3...'); \
    SentenceTransformer('BAAI/bge-m3'); \
    print('Downloading cross-encoder...'); \
    SentenceTransformer('cross-encoder/ms-marco-MiniLM-L-2-v2'); \
    print('Models downloaded!')"

# Copy application code
COPY index_books.py .
COPY chat_with_books.py .
COPY entrypoint.sh .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Create directories for books and index
RUN mkdir -p /app/books /app/books_index

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://ollama:11434

# Expose port for potential future web interface
EXPOSE 8080

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
