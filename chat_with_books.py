import warnings
warnings.filterwarnings("ignore")

from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding  # Added for local embeddings
from llama_index.llms.ollama import Ollama
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.postprocessor.colbert_rerank import ColbertRerank

# Set up local embeddings (must be before loading index to avoid OpenAI default)
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load the saved index
storage_context = StorageContext.from_defaults(persist_dir="./books_index")
index = load_index_from_storage(storage_context)

# Set up Ollama as the LLM
Settings.llm = Ollama(model="qwen3:14b", request_timeout=300.0)

# Create retriever with more context for cross-referencing
retriever = index.as_retriever(
    similarity_top_k=15,           # more chunks → better chance of getting real titles
    vector_store_query_mode="default"  # or try "hybrid" if you install llama-index-postprocessor-colbert
)

reranker = ColbertRerank(top_n=8)  # keeps top 8 after reranking

# Create chat engine with persistent system prompt and conversation history
chat_engine = ContextChatEngine.from_defaults(
    retriever=retriever,
    node_postprocessors=[reranker],
    system_prompt= "You are an accurate Gnostic text expert. "        
        "Do NOT fabricate, summarize, or translate titles. Only use information directly from retrieved chunks. "
        "If multiple references exist, list them separately. Be exhaustive but precise."
)

# Simple chat loop with history
print("Chat with your books! (Conversation has memory.) Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break
    response = chat_engine.chat(user_input)
    print("AI:", response.response)