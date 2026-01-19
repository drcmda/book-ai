import warnings
warnings.filterwarnings("ignore")
import time
import os

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding  # Added for local embeddings
from llama_index.llms.ollama import Ollama
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.postprocessor import SentenceTransformerRerank
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live

EMBED_MODEL = "BAAI/bge-m3"  # Good for semantic search/retrieval tasks
ENGINE = "qwen3:8b"  # Balanced model: fast enough for search, accurate for extraction
print(f"Initializing chat engine with model {ENGINE}. This may take a while ...")

console = Console()

# Set up local embeddings with device placement (must be before loading index to avoid OpenAI default)
# Note: On Mac M4, this will use CPU since sentence-transformers doesn't support MPS well
Settings.embed_model = HuggingFaceEmbedding(
    model_name=EMBED_MODEL,
    device="mps" if __import__("torch").backends.mps.is_available() else ("cuda" if __import__("torch").cuda.is_available() else "cpu")
)

# Load the saved index (simple in-memory storage)
print("Loading index from storage...")
storage_context = StorageContext.from_defaults(persist_dir="./books_index")
index = load_index_from_storage(storage_context)

# Set up Ollama as the LLM
Settings.llm = Ollama(
    model=ENGINE,
    request_timeout=300.0,
    temperature=0.1,
    context_window=32768,   # Qwen3 supports much larger contexts
    base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
)

# Create hybrid retriever with vector + BM25
print("Setting up hybrid retrieval (vector + BM25)...")

# Vector retriever
vector_retriever = index.as_retriever(
    similarity_top_k=15,
)

# BM25 retriever - pass nodes as a list
nodes = [node for node in index.docstore.docs.values()]
bm25_retriever = BM25Retriever.from_defaults(
    nodes=nodes,
    similarity_top_k=15,
)

# Combine both retrievers
retriever = QueryFusionRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    similarity_top_k=20,
    num_queries=1,
    mode="reciprocal_rerank",
    use_async=False,
)

# Add reranker
print("Setting up reranker...")
reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-2-v2",
    top_n=10,
)

# Create chat engine with persistent system prompt and conversation history
chat_engine = ContextChatEngine.from_defaults(
    retriever=retriever,
    node_postprocessors=[reranker],
    system_prompt=(
        "You are a precise search and retrieval assistant for a collection of indexed books. "
        "Your primary purpose is to help users find specific content, chapters, mentions, and references across the book collection.\n\n"

        "CORE PRINCIPLES:\n"
        "- Answer ONLY based on the retrieved text chunks - never invent or assume information\n"
        "- Be comprehensive: find ALL relevant matches, including direct mentions and semantically related content\n"
        "- Be precise: provide exact book titles, page/chapter references when available in the source\n"
        "- No disclaimers, warnings, or caveats unless explicitly in the source text\n\n"

        "RESPONSE FORMAT:\n"
        "1. For search queries ('where does it mention X'):\n"
        "   - List ALL books containing relevant information\n"
        "   - Provide exact book filenames (e.g., '33_1969-esoteric-course-of-kabbalah.pdf')\n"
        "   - Include chapter/section titles ONLY if clearly stated in the retrieved text\n"
        "   - Add short verbatim excerpts showing the relevant mention\n\n"

        "2. For content requests ('what does it say about X'):\n"
        "   - Provide complete, exact quotes from the source\n"
        "   - Include full paragraphs or chapters if relevant to the query\n"
        "   - Cite the specific book source for each piece of information\n\n"

        "3. For finding related topics:\n"
        "   - Consider semantic variations (e.g., China/Chinese/Sino)\n"
        "   - Prioritize direct matches, then semantically related content\n"
        "   - Clearly indicate the relationship between the query and retrieved content\n\n"

        "Remember: You are a search tool, not a conversationalist. Be exhaustive, accurate, and cite sources."
    )
)

# Simple chat loop with history
print(f"Ready to chat! Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break

    # Show spinner while processing with error handling
    try:
        with Live(Spinner("dots", text="Searching and retrieving..."), console=console, transient=True):
            response = chat_engine.chat(user_input)

        console.print(
            Panel(
                Markdown(response.response),
                title="Response",
                title_align="left",
                border_style="blue"
            )
        )
    except Exception as e:
        error_msg = str(e)
        console.print(f"[red]Error: {error_msg}[/red]")

        # Provide helpful hints based on error type
        if "system memory" in error_msg.lower():
            console.print("[yellow]→ Docker needs more memory allocated[/yellow]")
            console.print("[yellow]  Go to Docker Desktop → Settings → Resources → Memory[/yellow]")
            console.print("[yellow]  Increase to at least 12 GB and restart Docker[/yellow]")
        elif "connection" in error_msg.lower() or "connect" in error_msg.lower():
            console.print("[yellow]→ Cannot connect to Ollama[/yellow]")
            console.print("[yellow]  Check that Ollama container is running: docker ps[/yellow]")

        console.print("[yellow]Please try again or type 'exit' to quit.[/yellow]")