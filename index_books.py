from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter, HierarchicalNodeParser
from llama_index.readers.file import UnstructuredReader, PyMuPDFReader
from tqdm import tqdm  # For progress bars
import os

# Set up local embeddings
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

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
    def embed_documents(self, texts):
        with tqdm(total=len(texts), desc="Embedding chunks", unit="chunk") as pbar:
            embeddings = []
            for text in texts:
                emb = super().embed_documents([text])[0]
                embeddings.append(emb)
                pbar.update(1)
            return embeddings

Settings.embed_model = ProgressEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

index = VectorStoreIndex.from_documents(documents)

# Save the index to disk
index.storage_context.persist(persist_dir="./books_index")
print("Index created and saved with OCR support!")