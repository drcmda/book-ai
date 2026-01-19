A high-performance book search and retrieval system using BAAI/bge-m3 embeddings to index books (PDFs, DOCX, HTMLs, TXTs) with hybrid search (semantic + keyword), reranking, and advanced chunking. Chat interface powered by Ollama's Qwen3 model.

## Features

- **Hybrid Search**: Combines semantic vector search (BAAI/bge-m3) with BM25 keyword matching
- **Cross-Encoder Reranking**: Refines top results for better precision using sentence-transformers
- **Hierarchical Chunking**: Multi-level document parsing for better context preservation
- **Optimized for Large Collections**: Handles hundreds of books efficiently with batch embedding
- **Performance Optimizations**: Batch embedding (32 chunks at a time), GPU/MPS support
- **Rich Terminal UI**: Spinner feedback, markdown rendering, formatted panels

## Requirements

- Python 3.9+ and Ollama pre-installed
- ~10GB disk space for models and dependencies
- **Platform**: Cross-platform (macOS, Linux, Windows)
- **System deps**: Tesseract (OCR) and Poppler (PDF rendering) - see installation below

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
sudo apt-get install tesseract-ocr poppler-utils

# Linux (Fedora/RHEL):
sudo dnf install tesseract poppler-utils

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

The system uses:

- **Hybrid retrieval**: Vector search (semantic) + BM25 (keyword matching)
- **Query fusion**: Combines results using reciprocal rank fusion
- **Cross-encoder reranking**: Top 20 results reranked to best 10
- **Qwen3 8B**: Optimized for fast, accurate extraction and search
- **Rich UI**: Real-time spinner feedback and formatted markdown responses

## Docker Deployment

Docker provides a self-contained, cross-platform environment with zero manual dependency installation. All models are pre-downloaded into the image for faster first-run experience.

**Requirements:**
- Docker Desktop with **at least 12 GB RAM** allocated (Settings → Resources → Memory)
- ~15 GB disk space for images and models

### Quick Start

```bash
# Clone the repository (includes books in ./books/ folder)
git clone https://github.com/yourusername/book-ai-grok.git
cd book-ai-grok

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

**Using the Chat Interface:**

Once you attach to the container, you can type your questions directly:

```
You: which metal is related to cancer
AI: Cancer is the house of the Moon. Its metal is silver...

You: what about remedies for stomach pain
AI: Yes, there is a remedy for stomach pain mentioned...
```

Type your questions and press Enter. Type `exit` or press Ctrl+C to quit.

**Note:** The repository includes books ready to use. You can add more books by copying them into `./books/` before starting Docker.

### How It Works

**Volume Mounts (Books Are NOT Copied):**

- Your `./books` folder is mounted read-only into the container
- Your `./books_index` folder is mounted for persistent storage
- Books stay on your host machine - they're linked, not copied
- Index is preserved between container restarts

**What's Included in the Docker Image:**

- Python 3.11 + all dependencies
- Tesseract OCR and Poppler utilities
- BAAI/bge-m3 embedding model (pre-downloaded)
- Cross-encoder reranking model (pre-downloaded)
- Application code (index_books.py, chat_with_books.py)

**What's NOT in the Image (Mounted at Runtime):**

- Your books (in `./books/`)
- Your generated index (in `./books_index/`)
- Ollama models (stored in Docker volume `ollama_data`)

### Distribution & Sharing

**Current Setup: Books Included**

This repository includes books in the `./books/` folder, so users can clone and run immediately:

```bash
# Users clone and start
git clone https://github.com/yourusername/book-ai-grok.git
cd book-ai-grok
docker-compose up  # Auto-indexes books on first run
```

**Optional: Add Pre-built Index**

To skip indexing time for users, commit the index after building it locally:

```bash
# After running docker-compose up locally (which creates the index)
git add books_index/
git commit -m "Add pre-built index for faster startup"
git push

# Users now get instant startup (no indexing wait)
git clone https://github.com/yourusername/book-ai-grok.git
cd book-ai-grok
docker-compose up  # Index already exists, skips to chat immediately
```

**Note on Book Licensing:**
- Only include books you have rights to distribute
- For large book collections, consider using Git LFS: `git lfs track "books/*.pdf"`
- Alternative: Use `.gitignore` to exclude books and let users add their own

### Common Docker Workflows

**Add New Books (Auto-Reindexing):**

```bash
# Add more books to ./books/
cp ~/newbooks/*.pdf books/

# Restart - automatically detects changes and reindexes
docker-compose restart book-ai

# Or stop and restart everything
docker-compose down
docker-compose up
```

The system automatically detects when books are added, removed, or modified and reindexes only when needed.

**Use Existing Local Python Workflow:**

Docker doesn't affect your local setup. You can still run:

```bash
# Local Python (if you have dependencies installed)
python3 index_books.py
python3 chat_with_books.py

# Or use Docker
docker-compose up
```

Both workflows use the same `books/` and `books_index/` folders.

**Stop and Clean Up:**

```bash
# Stop containers
docker-compose down

# Remove containers + volumes (deletes Ollama models)
docker-compose down -v

# Remove built images
docker rmi book-ai-grok-book-ai
```

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

### Troubleshooting

**Memory error: "model requires more system memory than is available":**

The qwen3:8b model requires **at least 12 GB of RAM** allocated to Docker. By default, Docker Desktop may only allocate 2-8 GB.

To fix this:

1. Open **Docker Desktop**
2. Go to **Settings → Resources → Memory**
3. Increase memory to **12 GB** or higher
4. Click **Apply & Restart**
5. Restart your containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

Alternative: Use a smaller model like `qwen2.5:3b` (~3 GB RAM) by editing [chat_with_books.py](chat_with_books.py:20):
```python
ENGINE = "qwen2.5:3b"  # Smaller model
```

Then pull the model and restart:
```bash
docker exec book-ai-ollama ollama pull qwen2.5:3b
docker-compose restart book-ai
```

**"No books found" error:**

- Check that `./books/` exists and contains PDF/DOCX/TXT files
- Verify volume mount: `docker-compose config` should show `./books:/app/books:ro`

**Slow indexing:**

- Pre-downloaded models are baked into the image, but first build takes ~5 minutes
- Subsequent runs are instant (models cached in image layers)

**Port conflict (11434 already in use):**

- You have Ollama running locally. Either stop it (`ollama stop`) or change the port in docker-compose.yml

## Technical Details

### Architecture

**Retrieval Pipeline:**

1. **Vector search**: Semantic similarity using BAAI/bge-m3 (1024-dim embeddings)
2. **BM25 search**: Keyword matching using term frequency + inverse document frequency
3. **Query fusion**: Reciprocal rank fusion combines both retrievers (top 20)
4. **Cross-encoder reranking**: Scores query-document pairs to select best 10
5. **LLM generation**: Qwen3 8B generates final answer from top chunks

**Key Components:**

- Hierarchical chunking: 2048/512/256 tokens with 50-token overlap
- Batch embedding: 32 chunks processed simultaneously
- In-memory storage: Simple key-value store for docstore/index
- MPS/GPU support: Automatic device detection for embeddings

### Performance Benchmarks

**Indexing (2 books, ~600 pages):**

- Loading: ~30 seconds
- Embedding: ~2 minutes (6249 chunks)
- Storage: <1 second
- **Total: ~2.5 minutes**

**Query Performance:**

- BM25 + Vector retrieval: ~0.5 seconds
- Reranking (20→10): ~0.3 seconds
- LLM generation: ~1-4 seconds (varies by response length)
- **Total: ~2-5 seconds per query**

**Scalability:**

- 10 books: ~10 minutes indexing, same query speed
- 100 books: ~90 minutes indexing, +0.5s query overhead
- 500 books: ~7 hours indexing, +1-2s query overhead
