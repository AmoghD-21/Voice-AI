import os
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# 1. Initialize Local Hugging Face Embeddings
print("⏳ Loading local Hugging Face Sentence-Transformer model...")
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}  # Swaps automatically to 'cuda' if running on a GPU machine
)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Reads a PDF file and extracts all raw text."""
    print(f"📄 Extracting text from {pdf_path}...")
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text

def chunk_text(text: str, chunk_size: int = 100, chunk_overlap: int = 20) -> list:
    """Splits text into smaller chunks for precise semantic mapping."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def ingest_to_local_faiss(file_path: str):
    """Processes file, generates vectors locally via Hugging Face, and saves FAISS index."""
    if file_path.endswith('.pdf'):
        raw_text = extract_text_from_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

    chunks = chunk_text(raw_text)
    print(f"✂️ Split document into {len(chunks)} text chunks.")

    # Wrap raw text into LangChain Document objects
    documents = [
        Document(page_content=chunk, metadata={"source": os.path.basename(file_path)}) 
        for chunk in chunks
    ]
    
    print("🧠 Generating local embeddings & creating FAISS index...")
    # FAISS triggers the local model for calculation automatically
    db = FAISS.from_documents(documents, embeddings_model)
    
    # Save the vector database locally on disk
    print("💾 Saving FAISS index locally to folder 'faiss_index'...")
    db.save_local("faiss_index")
    print("✅ Ingestion successfully completed! Local DB is ready.")

if __name__ == "__main__":
    pdf_file = "Book.pdf"
    
    # # Create a quick sample text file if it doesn't exist
    # if not os.path.exists(sample_file):
    #     with open(sample_file, "w", encoding="utf-8") as f:
    #         f.write("The secret passkey for the real-time voice agent validation is 'SkyBlue-2026'. "
    #                 "The deployment utilizes Pipecat for streaming orchestration, FastAPI for web sockets, "
    #                 "and local Hugging Face + FAISS for vector retrieval. It runs entirely on free tiers.")
    #     print(f"Created a sample file: {sample_file}")

    ingest_to_local_faiss(pdf_file)