A high-performance book search and retrieval system using BAAI/bge-m3 embeddings to index books (PDFs, DOCX, HTMLs, TXTs) with hybrid search (semantic + keyword), reranking, and advanced chunking. Chat interface powered by Ollama's Qwen3 model.

## Features

- **Hybrid Search**: Combines semantic vector search (BAAI/bge-m3) with BM25 keyword matching
- **Cross-Encoder Reranking**: Refines top results for better precision using sentence-transformers
- **Query fusion**: Combines results using reciprocal rank fusion
- **Qwen3 8B LLM generation\***: Optimized for fast, accurate extraction and search
- **Hierarchical Chunking**: Multi-level document parsing for better context preservation
- **Optimized for Large Collections**: Handles hundreds of books efficiently with batch embedding
- **Performance Optimizations**: Batch embedding (32 chunks at a time), GPU/MPS support
- **Rich Terminal UI**: Spinner feedback, markdown rendering, formatted panels

## Requirements

- Python 3.9+ and Ollama pre-installed OR Docker Desktop
- ~10GB disk space for models and dependencies and **at least 12 GB RAM**
- **Platform**: Cross-platform (macOS, Linux, Windows)
- **System deps**: Tesseract (OCR) and Poppler (PDF rendering) - see installation below

# Local installation

```bash
# Install Python dependencies (core packages)
# Note: sentence-transformers will install PyTorch (~2GB) automatically
pip3 install --no-cache-dir \
  llama-index-core \
  llama-index-llms-ollama \
  llama-index-embeddings-huggingface \
  llama-index-readers-file \
  llama-index-retrievers-bm25 \
  sentence-transformers \
  rich \
  tqdm

# Install document processing dependencies
pip3 install --no-cache-dir \
  "unstructured[local-inference]" \
  python-docx \
  beautifulsoup4 \
  pypdf \
  pytesseract \
  pillow_heif

# Install Ollama model
ollama pull qwen3:8b

# Install system dependencies for OCR and PDF processing
# macOS:
brew install tesseract poppler

# Linux (Ubuntu/Debian):
# sudo apt-get install tesseract-ocr poppler-utils

# Linux (Fedora/RHEL):
# sudo dnf install tesseract poppler-utils

# Windows:
# 1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
# 2. Install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/
# Add both to your PATH

# Note: Tesseract is only needed for OCR on scanned PDFs
# Poppler is only needed for better PDF rendering
# The system will work without them for text-based PDFs/documents
```

## Usage

### 1. Generate the Index

Run this once, or every time you add new books to the folder.

```bash
python3 index_books.py
```

This will:

- Load all books from the `books/` folder
- Process them with OCR support for scanned PDFs
- Create embeddings using BAAI/bge-m3 model (batch processing for speed)
- Save the index to `./books_index`

### 2. Chat with Your Books

```bash
python3 chat_with_books.py
```

# Docker deployment

Docker provides a self-contained, cross-platform environment with zero manual dependency installation. All models are pre-downloaded into the image for faster first-run experience.

**Requirements:**

- Docker Desktop with **at least 12 GB RAM** allocated (Settings → Resources → Memory)
- ~15 GB disk space for images and models

### Quick Start

```bash
# Clone the repository (includes books in ./books/ folder)
git clone https://github.com/drcmda/book-ai
cd book-ai

# Start everything with Docker Compose (builds and starts in background)
docker-compose up -d

# Wait for initialization to complete (first run downloads models)
docker logs -f book-ai-chat

# Once you see "Ready to chat! Type 'exit' to quit.", attach to the container
docker attach book-ai-chat
```

That's it! The system will:

1. Download and start Ollama with Qwen3:8b
2. Build the Book AI container (with pre-downloaded embedding models)
3. Auto-index the books in the `./books/` folder on first run
4. Launch the interactive chat interface

### GPU Support (NVIDIA Only)

Uncomment the GPU section in [docker-compose.yml](docker-compose.yml:18-25):

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

Note: macOS (Metal/MPS) and AMD GPUs are not supported via Docker GPU passthrough.
