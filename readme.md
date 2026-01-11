Uses all-MiniLM-L6-v2 to index a folder of books (PDFs, DOCX, HMTLs, TXTs) with improved chunking, and chat with them using Ollama's Qwen3 model.

Requires Python and Ollama pre-installed.

```bash
pip3 install --no-cache-dir llama-index-core llama-index-llms-ollama llama-index-embeddings-huggingface llama-index-readers-file python-docx beautifulsoup4 pypdf tqdm "unstructured[local-inference]" pytesseract pillow_heif
ollama pull qwen3:14b
brew install tesseract
brew install poppler
```

# First, generate the index

Do this once, or every time you add new books to the folder.

```bash
python3 index_books.py
```

# Then, chat with the indexed books

```bash
python3 chat_with_books.py
```
