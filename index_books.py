from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter, HierarchicalNodeParser
from llama_index.readers.file import UnstructuredReader, PyMuPDFReader
from tqdm import tqdm  # For progress bars
import os

EMBED_MODEL = "BAAI/bge-m3"  # Good for semantic search/retrieval tasks
# Alternative for faster (but less accurate): "BAAI/bge-small-en-v1.5"

# Set up local embeddings with device placement
# Note: On Mac M4, this will use CPU since sentence-transformers doesn't support MPS well
Settings.embed_model = HuggingFaceEmbedding(
    model_name=EMBED_MODEL,
    device="mps" if __import__("torch").backends.mps.is_available() else ("cuda" if __import__("torch").cuda.is_available() else "cpu")
)

# Set up node parser
#Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=128)
Settings.node_parser = HierarchicalNodeParser.from_defaults(
    chunk_sizes=[2048, 512, 256],     # must stay decreasing
    chunk_overlap=50,                 # ← must be < 128 (50 is safe & reasonable)
)

# Custom file extractors: Use Unstructured for PDFs (with OCR), default for others
file_extractor = {
    ".pdf": UnstructuredReader(),  # Handles OCR for image-based PDFs
    ".html": PyMuPDFReader(),      # Fast for HTML (fallback if needed)
    # TXT and DOC use built-in defaults
}

# Path to your books folder
books_dir = "books"  # Replace with your actual path

# Get list of files to process (for progress bar)
all_files = []
for root, _, files in os.walk(books_dir):
    for file in files:
        if file.lower().endswith((".txt", ".html", ".pdf", ".doc", ".docx")):
            all_files.append(os.path.join(root, file))

print(f"Starting document loading... Found {len(all_files)} files to process.")

# Load documents with progress bar
documents = []
with tqdm(total=len(all_files), desc="Loading files", unit="file") as pbar:
    for file_path in all_files:
        # Use SimpleDirectoryReader for individual files to track progress
        reader = SimpleDirectoryReader(input_files=[file_path], file_extractor=file_extractor)
        docs = reader.load_data()
        documents.extend(docs)
        pbar.update(1)
        pbar.set_postfix(file=os.path.basename(file_path))  # Show current file

print(f"Loaded {len(documents)} documents. Starting indexing...")

# Create the index with embedding progress
# To track embedding, we override the embedder with a callback
class ProgressEmbedding(HuggingFaceEmbedding):
    def _get_query_embedding(self, query):
        return super()._get_query_embedding(query)

    def _get_text_embedding(self, text):
        return super()._get_text_embedding(text)

    def _get_text_embeddings(self, texts):
        # Process in batches with progress tracking
        batch_size = 32
        all_embeddings = []
        with tqdm(total=len(texts), desc="Embedding chunks", unit="chunk") as pbar:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = super()._get_text_embeddings(batch)
                all_embeddings.extend(batch_embeddings)
                pbar.update(len(batch))
        return all_embeddings

Settings.embed_model = ProgressEmbedding(
    model_name=EMBED_MODEL,
    device="mps" if __import__("torch").backends.mps.is_available() else ("cuda" if __import__("torch").cuda.is_available() else "cpu")
)

# Create index with simple in-memory storage
print("Creating index...")
index = VectorStoreIndex.from_documents(
    documents,
    show_progress=True
)

# Save the index to disk
index.storage_context.persist(persist_dir="./books_index")
print("Index created and saved!")