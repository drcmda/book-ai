#!/bin/bash
set -e

echo "======================================"
echo "Book AI - Intelligent Search System"
echo "======================================"
echo ""

# Check if Ollama is accessible
echo "Checking Ollama connection..."
until curl -s http://ollama:11434/api/tags >/dev/null 2>&1; do
    echo "Waiting for Ollama to be ready..."
    sleep 2
done
echo "✓ Ollama is ready"
echo ""

# Check if qwen3:8b model exists
echo "Checking for qwen3:8b model..."
if curl -s http://ollama:11434/api/tags | grep -q "qwen3:8b"; then
    echo "✓ qwen3:8b model found"
else
    echo "⚠ qwen3:8b model not found. Pulling model (this may take a while)..."
    curl -X POST http://ollama:11434/api/pull -d '{"name": "qwen3:8b"}' 2>&1 | \
        grep -o '"status":"[^"]*"' | sed 's/"status":"\([^"]*\)"/\1/' || true
    echo "✓ Model pulled successfully"
fi
echo ""

# Function to calculate checksum of books directory
calculate_books_checksum() {
    # Create a checksum based on filenames, sizes, and modification times
    find /app/books -type f \( -name "*.pdf" -o -name "*.docx" -o -name "*.txt" -o -name "*.html" \) \
        -exec stat -c '%n %s %Y' {} \; 2>/dev/null | sort | md5sum | cut -d' ' -f1
}

# Check if books exist
if [ -z "$(ls -A /app/books 2>/dev/null)" ]; then
    echo ""
    echo "ERROR: No books found in /app/books/"
    echo ""
    echo "Please mount your books directory:"
    echo "  docker-compose run --rm book-ai"
    echo ""
    echo "Or add books to the ./books folder and restart."
    exit 1
fi

echo "✓ Found books in /app/books"
echo ""

# Calculate current books checksum
CURRENT_CHECKSUM=$(calculate_books_checksum)
CHECKSUM_FILE="/app/books_index/.books_checksum"

# Determine if we need to index
NEED_INDEX=false

if [ -d "/app/books_index" ] && [ "$(ls -A /app/books_index)" ]; then
    echo "✓ Index found at /app/books_index"

    # Check if books have changed
    if [ -f "$CHECKSUM_FILE" ]; then
        STORED_CHECKSUM=$(cat "$CHECKSUM_FILE")
        if [ "$CURRENT_CHECKSUM" != "$STORED_CHECKSUM" ]; then
            echo "⚠ Books have changed since last indexing"
            NEED_INDEX=true
        else
            echo "✓ Books unchanged, using existing index"
        fi
    else
        echo "⚠ No checksum found, re-indexing to be safe"
        NEED_INDEX=true
    fi
else
    echo "⚠ No index found"
    NEED_INDEX=true
fi

# Index if needed
if [ "$NEED_INDEX" = true ]; then
    echo ""
    echo "Indexing books (this may take a few minutes)..."
    echo "======================================"
    echo ""

    python index_books.py

    # Save checksum after successful indexing
    echo "$CURRENT_CHECKSUM" > "$CHECKSUM_FILE"

    echo ""
    echo "======================================"
    echo "✓ Indexing complete!"
fi

echo ""
echo "Starting chat interface..."
echo "======================================"
echo ""

exec python chat_with_books.py
